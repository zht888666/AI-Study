"""Gateway 网关模块。"""

import asyncio
from typing import Callable

from agent.loop import AgentLoop
from bus.queue import InboundMessage, MessageBus, OutboundMessage
from channels.base import Channel


class Gateway:
    """管理渠道、消息路由和按会话隔离的 Agent 实例。"""

    def __init__(
        self,
        bus: MessageBus,
        channels: list[Channel],
        agent_factory: Callable[[str], AgentLoop],
        max_concurrent_agents: int = 5,
    ) -> None:
        """
        Args:
            bus: 消息总线实例。
            channels: 渠道适配器列表。
            agent_factory: 根据 session_key 创建 AgentLoop 的工厂函数。
            max_concurrent_agents: 同时执行 agent.run() 的最大会话数。
        """
        if max_concurrent_agents < 1:
            raise ValueError("max_concurrent_agents must be at least 1")

        self.bus = bus
        self.channels = channels
        self.agent_factory = agent_factory

        self._agents: dict[str, AgentLoop] = {}
        self._channel_map: dict[str, Channel] = {
            channel.name: channel for channel in channels
        }
        self._session_locks: dict[str, asyncio.Lock] = {}
        self._agent_semaphore = asyncio.Semaphore(max_concurrent_agents)
        self._inflight_tasks: set[asyncio.Task[None]] = set()

    async def run(self) -> None:
        """并发启动渠道、入站分发循环和出站分发循环。"""
        tasks: list[asyncio.Task[None]] = [
            asyncio.create_task(channel.start()) for channel in self.channels
        ]
        tasks.append(asyncio.create_task(self._process_inbound()))
        tasks.append(asyncio.create_task(self._dispatch_outbound()))

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            await self.shutdown()

    async def _process_inbound(self) -> None:
        """持续取入站消息，并将每条消息分发为独立处理任务。"""
        while True:
            try:
                inbound_msg = await self.bus.consume_inbound()
                task = asyncio.create_task(self._handle_inbound(inbound_msg))
                self._inflight_tasks.add(task)
                task.add_done_callback(self._inflight_tasks.discard)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                print(f"警告: 入站处理循环异常 - {exc}")

    async def _handle_inbound(self, inbound_msg: InboundMessage) -> None:
        """处理一条消息；同会话串行，不同会话可在全局上限内并发。"""
        session_key = f"{inbound_msg.channel}:{inbound_msg.sender_id}"
        lock = self._session_locks.get(session_key)
        if lock is None:
            lock = asyncio.Lock()
            self._session_locks[session_key] = lock

        async with lock:
            try:
                agent = self._agents.get(session_key)
                if agent is None:
                    agent = self.agent_factory(session_key)
                    self._agents[session_key] = agent

                # 先拿会话锁，再申请全局名额，避免同会话排队消息占用名额。
                async with self._agent_semaphore:
                    response = await agent.run(inbound_msg.content)

                outbound_msg = OutboundMessage(
                    channel=inbound_msg.channel,
                    chat_id=inbound_msg.chat_id,
                    content=response,
                )
                await self.bus.publish_outbound(outbound_msg)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                error_msg = OutboundMessage(
                    channel=inbound_msg.channel,
                    chat_id=inbound_msg.chat_id,
                    content="抱歉，处理消息时发生了错误。请稍后重试。",
                )
                await self.bus.publish_outbound(error_msg)
                print(f"警告: Agent 处理出错 - {exc}")

    async def _dispatch_outbound(self) -> None:
        """持续从出站队列取消息，并发送到对应渠道。"""
        while True:
            try:
                outbound_msg = await self.bus.consume_outbound()
                channel = self._channel_map.get(outbound_msg.channel)

                if channel is None:
                    print(f"警告: 渠道 '{outbound_msg.channel}' 不存在，无法发送消息")
                    continue

                try:
                    await channel.send(outbound_msg)
                except Exception as exc:
                    print(f"警告: 渠道 '{outbound_msg.channel}' 发送失败 - {exc}")
            except asyncio.CancelledError:
                break
            except Exception as exc:
                print(f"警告: 出站分发循环异常 - {exc}")

    async def shutdown(self) -> None:
        """停止渠道并取消仍在运行或等待的入站处理任务。"""
        for channel in self.channels:
            try:
                await channel.stop()
            except Exception as exc:
                print(f"警告: 渠道 '{channel.name}' 关闭失败 - {exc}")

        pending_tasks = list(self._inflight_tasks)
        for task in pending_tasks:
            task.cancel()
        if pending_tasks:
            await asyncio.gather(*pending_tasks, return_exceptions=True)

        self._inflight_tasks.clear()
        self._session_locks.clear()
        self._agents.clear()
