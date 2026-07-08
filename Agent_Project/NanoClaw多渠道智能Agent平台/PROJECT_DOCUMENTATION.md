# NanoClaw 项目文档

> 文档校准日期：2026-06-08。本文档基于当前工作区源码整理，重点用于项目学习、交接、二次开发和问题排查。文档示例中的密钥均使用占位符，不复制当前本地配置中的真实凭据。

## 1. 项目概览

NanoClaw 是一个面向编程与自动化任务的 AI Agent 项目。它以 OpenAI-compatible Chat Completions API 为模型入口，通过统一的工具系统、会话管理、多渠道消息网关和 MCP(Model Context Protocol) 扩展机制，让用户可以在 CLI、Web、飞书、QQ 等渠道中与同一个 Agent 能力交互。

项目的核心能力包括：

- 调用兼容 OpenAI API 的大模型服务。
- 支持 function calling 风格的本地工具调用。
- 支持文件读写、目录查看、Shell 命令执行、网页搜索、网页抓取和子 Agent。
- 支持通过 MCP Server 动态扩展外部工具。
- 支持 CLI、WebSocket Web UI、飞书、QQ 多渠道接入。
- 按会话保存历史消息，并在上下文过长时进行历史压缩。
- 通过 `skills/` 目录加载技能说明，把可用技能注入 system prompt。

从代码结构看，NanoClaw 更像一个“可扩展 Agent 运行框架”，而不是单一聊天机器人。它的设计重点是把模型、工具、渠道、会话和外部 MCP 服务拆成相对独立的模块。

### 1.1 适合读者

本文档适合三类读者：

| 读者 | 重点阅读章节 |
| --- | --- |
| 只想运行项目的人 | 第 2、5、14、17 章 |
| 想理解架构的人 | 第 3、4、6、7、8、9 章 |
| 想二次开发的人 | 第 6、7、8、9、10、12、18 章 |

如果是第一次接触该项目，建议先阅读第 3 章整体架构，再回到第 2 章按步骤启动。这样更容易理解为什么项目启动时会同时出现 CLI、Web、MCP 和外部平台渠道相关日志。

### 1.2 项目边界

NanoClaw 当前主要解决的是“让大模型通过工具和多渠道执行任务”的运行框架问题。它不是一个完整的生产级平台，当前代码中还没有完整覆盖以下能力：

- 用户权限体系和鉴权。
- 多租户隔离。
- 完整审计日志。
- 严格的工具沙箱。
- 可配置的限流、熔断和监控。
- 完整自动化测试套件。

因此，如果把它部署给不可信用户使用，需要额外补齐安全隔离、权限控制和日志审计。

### 1.3 推荐阅读顺序

建议按下面顺序理解项目：

1. [main.py](main.py)：先看项目如何启动、如何装配 Provider、工具、渠道和 Gateway。
2. [gateway.py](gateway.py) 与 [bus/queue.py](bus/queue.py)：理解消息如何在渠道和 Agent 之间流动。
3. [agent/loop.py](agent/loop.py)：理解模型调用、工具调用和会话保存的主循环。
4. [agent/tools/](agent/tools/)：理解所有工具如何接入 function calling。
5. [channels/](channels/)：理解不同外部入口如何转换成统一消息格式。
6. [agent/tools/mcp_server.py](agent/tools/mcp_server.py) 与 [mcp_servers/poetry_server.py](mcp_servers/poetry_server.py)：理解 MCP 扩展。
7. [session/manager.py](session/manager.py) 与 [agent/memory.py](agent/memory.py)：理解历史持久化和压缩。

### 1.4 图解速览

如果先不看细节，可以只记住这一条主线：

```text
用户
  |
  v
渠道 Channel
  |  CLI / Web / 飞书 / QQ
  v
消息总线 MessageBus
  |  inbound_queue
  v
网关 Gateway
  |  找到或创建当前会话的 Agent
  v
AgentLoop
  |  组织上下文 -> 调模型 -> 必要时调工具
  v
模型 Provider + 工具 ToolRegistry
  |
  v
Agent 回复
  |
  v
消息总线 MessageBus
  |  outbound_queue
  v
原渠道 Channel.send()
  |
  v
用户看到回复
```

#### 1.4.1 启动流程图

运行 `python main.py` 后，项目大致按下面顺序装配：

```text
python main.py
  |
  v
main()
  |
  v
async_main()
  |
  +--> load_config()
  |      读取 config.json
  |      读取 NANOCLAW_API_KEY 覆盖 api_key
  |
  +--> MessageBus()
  |      创建 inbound_queue / outbound_queue
  |
  +--> MCPClientManager.connect_all()
  |      如果配置了 mcp_servers，就连接外部 MCP 工具
  |
  +--> 创建渠道
  |      CLIChannel       一定创建
  |      WebChannel       web.enabled=true 时创建
  |      FeishuChannel    配了飞书 app_id/app_secret 时创建
  |      QQChannel        配了 QQ app_id/app_secret 时创建
  |
  +--> Gateway(bus, channels, create_agent)
  |      把渠道和 Agent 工厂交给网关
  |
  +--> 预创建 cli:local Agent
  |      让 CLI 一启动就能看到工具列表
  |
  v
gateway.run()
  |
  +--> 启动所有 channel.start()
  +--> 启动 Gateway._process_inbound()
  +--> 启动 Gateway._dispatch_outbound()
```

#### 1.4.2 一次对话流程图

以 Web 页面发一句话为例：

```text
浏览器输入一句话
  |
  v
channels/web.py
  WebSocket /ws 收到文本
  |
  v
封装 InboundMessage
  channel   = "web"
  sender_id = client_id
  chat_id   = client_id
  content   = 用户文本
  |
  v
bus.publish_inbound()
  |
  v
MessageBus.inbound_queue
  |
  v
Gateway._process_inbound()
  |
  +--> session_key = "web:{client_id}"
  |
  +--> 如果没有这个 Agent:
  |       create_agent(session_key)
  |
  v
AgentLoop.run(content)
  |
  v
生成回复
  |
  v
封装 OutboundMessage
  channel = "web"
  chat_id = client_id
  content = Agent 回复
  |
  v
bus.publish_outbound()
  |
  v
Gateway._dispatch_outbound()
  |
  v
WebChannel.send()
  |
  v
websocket.send_text()
  |
  v
浏览器显示回复
```

#### 1.4.3 Agent 内部流程图

`AgentLoop.run()` 是最核心的循环，可以理解成：

```text
AgentLoop.run(user_message)
  |
  +--> ContextBuilder.build_messages()
  |      system prompt
  |      历史消息
  |      当前用户消息
  |
  +--> SessionManager.save_message(user)
  |
  v
循环，最多 max_iterations 次
  |
  +--> MemoryConsolidator.maybe_consolidate()
  |      如果上下文太长，压缩旧历史
  |
  +--> provider.chat(messages, tools)
  |
  +--> 模型返回普通文本？
  |       |
  |       +--> 是:
  |             保存 assistant 回复
  |             return 回复文本
  |
  +--> 模型返回 tool_calls？
          |
          +--> 保存 assistant tool_call 消息
          |
          +--> 对每个 tool_call:
                 |
                 +--> 检查是否重复调用过多
                 |
                 +--> ToolRegistry.execute(name, arguments)
                 |
                 +--> 工具结果作为 role="tool" 加回 messages
          |
          +--> 回到循环顶部，再问一次模型
```

#### 1.4.4 工具调用流程图

模型想读文件、执行命令、搜索网页或调用 MCP 工具时，都会走统一工具注册表：

```text
模型返回 tool_call
  |
  v
AgentLoop
  |
  v
ToolRegistry.execute(tool_name, arguments)
  |
  +--> 本地工具
  |      read_file / write_file / list_dir
  |      exec
  |      web_search / web_fetch
  |      spawn_subagent
  |
  +--> MCP 工具
         poetry__search_poetry
         poetry__random_poetry
         poetry__list_poets
         其他 server__tool
  |
  v
工具返回字符串
  |
  v
AgentLoop 把结果塞回 messages
  |
  v
模型基于工具结果继续回答
```

#### 1.4.5 文件和模块关系图

下面这张图可以帮助你把文件名和职责对应起来：

```text
main.py
  项目总入口，负责装配所有东西
  |
  +--> config.py
  |      读取 config.json 和 NANOCLAW_API_KEY
  |
  +--> gateway.py
  |      多渠道消息路由
  |
  +--> bus/queue.py
  |      inbound_queue / outbound_queue
  |
  +--> channels/
  |      cli.py      终端入口
  |      web.py      WebSocket 入口
  |      feishu.py   飞书入口
  |      qq.py       QQ 入口
  |
  +--> agent/
  |      loop.py     Agent 主循环
  |      context.py  system prompt 构造
  |      memory.py   历史压缩
  |      skills.py   技能扫描
  |
  +--> agent/tools/
  |      registry.py     工具注册表
  |      filesystem.py   文件读写
  |      shell.py        Shell 命令
  |      web_search.py   搜索
  |      web_fetch.py    网页抓取
  |      spawn.py        子 Agent
  |      mcp_server.py   MCP 工具包装
  |
  +--> providers/
  |      base.py          LLM 抽象接口
  |      openai_compat.py OpenAI-compatible 调用实现
  |
  +--> session/
  |      manager.py       会话 JSONL 持久化
```

#### 1.4.6 记忆和会话落盘图

```text
用户消息 / assistant 回复 / tool 结果
  |
  v
SessionManager.save_message()
  |
  v
workspace/sessions/{channel}_{sender_id}.jsonl


上下文太长
  |
  v
MemoryConsolidator.maybe_consolidate()
  |
  +--> 调模型总结旧消息
  |
  +--> 把总结插回当前 messages
  |
  v
workspace/memory/HISTORY.md
```

## 2. 快速开始

### 2.1 环境要求

建议使用 Python 3.11 或 Python 3.12。项目中使用了 `asyncio`、FastAPI、uvicorn、OpenAI SDK、MCP SDK、飞书 SDK、QQ Bot SDK 等依赖。

项目根目录：

```text
D:\pythonProjrct\2025\nanoclaw
```

安装依赖：

```powershell
pip install -r requirements.txt
```

注意：当前 `requirements.txt` 很宽，包含大量与 NanoClaw 主流程不一定直接相关的包。实际部署时可以按运行渠道精简依赖，但本文档按现有项目状态说明。

### 2.1.1 依赖分层说明

从源码实际 import 看，核心运行至少涉及：

| 功能 | 关键依赖 | 来源文件 |
| --- | --- | --- |
| OpenAI-compatible 模型调用 | `openai` | [providers/openai_compat.py](providers/openai_compat.py) |
| Web 服务 | `fastapi`、`uvicorn` | [channels/web.py](channels/web.py) |
| HTTP 抓取 | `httpx`、`html2text` | [agent/tools/web_fetch.py](agent/tools/web_fetch.py) |
| 网页搜索 | `ddgs` | [agent/tools/web_search.py](agent/tools/web_search.py) |
| MCP | `mcp` | [agent/tools/mcp_server.py](agent/tools/mcp_server.py)、[mcp_servers/poetry_server.py](mcp_servers/poetry_server.py) |
| 飞书渠道 | `lark-oapi` | [channels/feishu.py](channels/feishu.py) |
| QQ 渠道 | `qq-botpy` | [channels/qq.py](channels/qq.py) |
| 技能 frontmatter 解析 | `PyYAML` | [agent/skills.py](agent/skills.py) |

当前 [requirements.txt](requirements.txt) 中能看到 `openai`、`fastapi`、`uvicorn`、`httpx`、`mcp`、`lark-oapi`、`qq-botpy`、`PyYAML`，但没有列出 `ddgs` 和 `html2text`。这意味着项目可以启动，但当 Agent 真正调用 `web_search` 或 `web_fetch` 时，可能因为缺少这两个包而失败。建议后续把它们补入依赖文件，或在文档/安装脚本中单独说明：

```powershell
pip install ddgs html2text
```

### 2.2 配置文件

主配置文件是根目录下的 [config.json](config.json)，由 [config.py](config.py) 的 `load_config()` 读取。

推荐配置示例：

```json
{
  "api_key": "",
  "base_url": "https://api.siliconflow.cn/v1",
  "models": {
    "main": "Pro/zai-org/GLM-5",
    "subagent": "Qwen/Qwen3.5-35B-A3B",
    "cheap": "Qwen/Qwen3.5-4B"
  },
  "workspace": ".",
  "max_iterations": 32,
  "identity_file": "identity.md",
  "web": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 8080
  },
  "feishu": {
    "app_id": "cli_xxx",
    "app_secret": "your_feishu_app_secret"
  },
  "qq": {
    "app_id": "your_qq_app_id",
    "app_secret": "your_qq_app_secret"
  },
  "mcp_servers": {
    "poetry": {
      "command": "python",
      "args": ["mcp_servers/poetry_server.py"],
      "description": "古诗词查询服务"
    }
  }
}
```

更安全的做法是不要把 API Key 写入 `config.json`，而是使用环境变量：

```powershell
$env:NANOCLAW_API_KEY = "sk-your-api-key"
python main.py
```

`NANOCLAW_API_KEY` 的优先级高于配置文件里的 `api_key`。

### 2.3 启动项目

在项目根目录执行：

```powershell
python main.py
```

启动后主流程会：

1. 读取 [config.json](config.json)。
2. 创建 `MessageBus`。
3. 如配置了 MCP Server，则尝试连接并加载 MCP 工具。
4. 创建 CLI 渠道。
5. 按配置决定是否启用飞书、QQ、Web 渠道。
6. 创建 `Gateway`，并预先创建 CLI 会话 Agent。
7. 并发运行所有渠道和消息分发循环。

如果启用了 Web 渠道，默认访问：

```text
http://0.0.0.0:8080
```

在本机浏览器通常使用：

```text
http://127.0.0.1:8080
```

### 2.4 CLI 命令

CLI 渠道支持以下命令：

| 命令 | 作用 |
| --- | --- |
| `/exit` | 退出 CLI 对话 |
| `/clear` | 清空当前 CLI 会话历史 |
| `/tools` | 查看当前 Agent 注册的工具列表 |

### 2.5 启动模式

当前项目没有独立的“只启动 Web”或“只启动外部平台”命令，统一从 `python main.py` 进入。不同模式由配置决定：

| 模式 | 配置条件 | 结果 |
| --- | --- | --- |
| CLI 基础模式 | 默认总是创建 `CLIChannel` | 终端可直接对话 |
| Web 模式 | `web.enabled=true` | 启动 FastAPI + WebSocket，访问 Web UI |
| 飞书模式 | 同时配置 `feishu.app_id` 和 `feishu.app_secret` | 建立飞书 WebSocket 客户端 |
| QQ 模式 | 同时配置 `qq.app_id` 和 `qq.app_secret` | 启动 QQ Bot 客户端 |
| MCP 扩展模式 | `mcp_servers` 非空 | 启动并注册 MCP Server 工具 |

如果只是本地学习，建议先关闭飞书和 QQ，只保留 CLI、Web 和 poetry MCP。这样排错范围最小。

## 3. 整体架构

NanoClaw 的核心架构可以概括为：

```text
用户渠道
  |-- CLI
  |-- WebSocket Web UI
  |-- 飞书
  |-- QQ
        |
        v
MessageBus
  |-- inbound_queue
  |-- outbound_queue
        |
        v
Gateway
        |
        v
AgentLoop
  |-- ContextBuilder
  |-- SessionManager
  |-- OpenAICompatProvider
  |-- ToolRegistry
        |
        v
本地工具 / MCP 工具 / 子 Agent
```

关键职责：

- [main.py](main.py)：程序入口，负责读取配置、初始化 MCP、注册渠道、组装 Agent。
- [gateway.py](gateway.py)：多渠道网关，负责把入站消息路由到对应会话 Agent，并把回复发回原渠道。
- [bus/queue.py](bus/queue.py)：异步消息总线，用两个 `asyncio.Queue` 承载入站和出站消息。
- [agent/loop.py](agent/loop.py)：Agent 主循环，负责调用模型、处理工具调用、防止工具重复调用爆炸、保存对话历史。
- [providers/openai_compat.py](providers/openai_compat.py)：兼容 OpenAI API 格式的模型 Provider。
- [agent/tools/](agent/tools/)：工具系统，所有工具都实现统一 `Tool` 抽象。
- [channels/](channels/)：渠道适配器，负责把不同平台消息转换为统一消息结构。
- [session/manager.py](session/manager.py)：会话持久化，把每个会话保存为 JSONL。
- [agent/context.py](agent/context.py)：构造 system prompt，注入身份、时间、工作区、长期记忆和技能摘要。
- [agent/memory.py](agent/memory.py)：历史压缩器，在上下文过长时总结旧消息。
- [mcp_servers/](mcp_servers/)：本地 MCP Server 示例。

## 4. 运行数据流

### 4.1 入站消息

以 Web 渠道为例：

1. 浏览器连接 `WebChannel` 的 `/ws` WebSocket。
2. 用户发送文本。
3. [channels/web.py](channels/web.py) 把文本包装成 `InboundMessage`：

```python
InboundMessage(
    channel="web",
    sender_id=client_id,
    chat_id=client_id,
    content=data,
    raw={"client_id": client_id}
)
```

4. 消息进入 `MessageBus.inbound_queue`。
5. `Gateway._process_inbound()` 消费消息。
6. `Gateway` 用 `f"{channel}:{sender_id}"` 生成 `session_key`。
7. 如果该会话 Agent 不存在，则调用 `agent_factory(session_key)` 创建。
8. 调用 `AgentLoop.run(content)` 生成回复。

### 4.2 Agent 处理

`AgentLoop.run()` 的主要流程：

1. `ContextBuilder.build_messages()` 组装完整 messages：
   - system prompt
   - 历史消息
   - 当前用户消息
2. 保存用户消息到 `SessionManager`。
3. 循环调用 LLM：
   - 如果模型返回普通文本，保存 assistant 回复并返回。
   - 如果模型返回 tool calls，则执行工具并把工具结果追加到 messages。
4. 如果工具调用重复达到阈值，则触发防爆机制。
5. 如果超过 `max_iterations`，返回“达到最大迭代次数”的错误提示。

### 4.3 出站消息

1. `Gateway` 将 Agent 回复包装成 `OutboundMessage`。
2. 消息进入 `MessageBus.outbound_queue`。
3. `Gateway._dispatch_outbound()` 根据 `message.channel` 找到对应 Channel。
4. 调用 `channel.send(message)` 发回用户。

不同渠道的发送方式不同：

- CLI：打印到终端。
- Web：通过 WebSocket `send_text()` 发回指定连接。
- 飞书：调用飞书 IM API 发送文本消息。
- QQ：优先尝试 C2C 消息，失败后尝试群消息。

## 5. 配置项说明

`NanoClawConfig` 定义在 [config.py](config.py)。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `api_key` | string | 模型服务 API Key。可被 `NANOCLAW_API_KEY` 覆盖。 |
| `base_url` | string | OpenAI-compatible API 地址。默认是硅基流动地址。 |
| `model` | string | 默认模型名。 |
| `models` | object | 多模型配置，常见键为 `main`、`subagent`、`cheap`。 |
| `workspace` | string | 工作区路径，文件工具和 Shell 工具都受它限制。 |
| `max_iterations` | int | Agent 单轮最大模型/工具循环次数。 |
| `identity_file` | string | 身份提示词文件，默认 `identity.md`。 |
| `feishu.app_id` | string | 飞书应用 ID。存在 app_id 和 app_secret 时启用飞书渠道。 |
| `feishu.app_secret` | string | 飞书应用密钥。 |
| `qq.app_id` | string | QQ Bot App ID。存在 app_id 和 app_secret 时启用 QQ 渠道。 |
| `qq.app_secret` | string | QQ Bot App Secret。 |
| `web.enabled` | bool | 是否启用 Web 渠道。 |
| `web.host` | string | Web 服务监听地址。 |
| `web.port` | int | Web 服务监听端口。 |
| `mcp_servers` | object | MCP Server 配置，格式接近 Claude Desktop。 |

注意：当前项目中的 `config.json` 包含真实凭据。生产或提交代码前，应迁移到环境变量、私有配置文件或密钥管理服务，并避免把真实密钥写入公开仓库。

### 5.1 配置加载优先级

`load_config()` 的加载逻辑比较简单，优先级如下：

1. 先创建 `NanoClawConfig()` 默认值。
2. 如果 [config.json](config.json) 存在，则读取其中已声明字段并覆盖默认值。
3. 如果存在环境变量 `NANOCLAW_API_KEY`，最后用环境变量覆盖 `api_key`。

也就是说，`NANOCLAW_API_KEY` 是当前唯一显式支持的环境变量覆盖项。`base_url`、`model`、飞书、QQ、Web、MCP 等配置目前仍来自 JSON 文件或默认值。

### 5.2 多模型配置行为

`models` 字段用于支持不同用途的模型：

- `models.main`：主 Agent 默认模型。如果配置文件没有单独的 `model` 字段，`load_config()` 会把 `models.main` 作为 `config.model`。
- `models.subagent`：子 Agent 默认模型。`SpawnSubagentTool` 在未显式传入 model 时会优先使用它。
- `models.cheap`：当前源码中只是配置项，没有在主流程中直接使用。

如果同时配置了顶层 `model` 和 `models.main`，顶层 `model` 优先成为主 Agent 模型。

### 5.3 工作区配置的影响

`workspace` 不只是显示路径，它会影响多个模块：

| 模块 | 如何使用 `workspace` |
| --- | --- |
| 文件工具 | 限制 `read_file`、`write_file`、`list_dir` 只能访问工作区内路径 |
| Shell 工具 | 命令在工作区目录下执行 |
| `ContextBuilder` | 把工作区路径写入 system prompt |
| `SessionManager` | 当前在 `workspace/workspace/sessions` 下保存会话 |
| `MemoryConsolidator` | 当前在 `workspace/workspace/memory/HISTORY.md` 追加压缩历史 |
| `SkillsLoader` | 从 `workspace/skills` 扫描技能 |

在当前配置中 `workspace` 通常为 `"."`，因此这些路径都落在项目根目录下。

## 6. 核心模块说明

### 6.1 `main.py`

[main.py](main.py) 是项目入口，主要包含三个层次：

- `build_agent(config, session_key, mcp_manager)`：组装单个会话的 `AgentLoop`。
- `async_main()`：启动消息总线、MCP、渠道和网关。
- `main()`：同步入口，调用 `asyncio.run(async_main())`。

`build_agent()` 会创建：

- `OpenAICompatProvider`
- `ToolRegistry`
- 文件、Shell、Web、子 Agent 等本地工具
- MCP 工具
- `SkillsLoader`
- `SessionManager`
- `ContextBuilder`
- `MemoryConsolidator`
- `AgentLoop`

需要注意的是，函数签名接收了 `config` 参数，但内部又调用了一次 `load_config()`。这不会影响文档理解，但从工程整洁性看可以后续优化。

### 6.2 `gateway.py`

`Gateway` 是多渠道消息路由中心。

内部状态：

- `_agents: dict[str, AgentLoop]`：按 `session_key` 缓存 Agent。
- `_channel_map: dict[str, Channel]`：按渠道名缓存渠道适配器。

主要任务：

- 并发启动所有 Channel。
- 从 `MessageBus` 消费入站消息。
- 按会话找到或创建 Agent。
- 调用 Agent 处理消息。
- 将回复发布到出站队列。
- 从出站队列消费消息并分发给对应 Channel。

### 6.3 `bus/queue.py`

消息总线定义两个数据结构：

```python
InboundMessage(
    channel: str,
    sender_id: str,
    chat_id: str,
    content: str,
    raw: dict | None = None
)

OutboundMessage(
    channel: str,
    chat_id: str,
    content: str,
    reply_to: str | None = None
)
```

`MessageBus` 使用两个队列：

- `inbound_queue`：用户到 Agent。
- `outbound_queue`：Agent 到用户。

这让渠道适配器和 Agent 执行逻辑解耦。

### 6.4 `providers/`

[providers/base.py](providers/base.py) 定义标准接口：

- `ToolCallRequest`：模型返回的工具调用。
- `LLMResponse`：标准化模型响应。
- `LLMProvider`：抽象 Provider。

[providers/openai_compat.py](providers/openai_compat.py) 实现 OpenAI-compatible Provider：

- 使用 `AsyncOpenAI`。
- 根据 `tools` 是否存在决定是否传 `tool_choice="auto"`。
- 解析 tool calls 的 JSON arguments。
- 提取支持 reasoning 的模型返回内容。
- API 异常时返回 `finish_reason="error"`，而不是向上抛异常。

### 6.5 `agent/loop.py`

`AgentLoop` 是项目最核心的执行循环。

关键能力：

- 构造 messages。
- 调用模型。
- 执行工具。
- 保存用户、assistant、tool 消息。
- 维护内存态历史。
- 防止重复工具调用导致死循环。
- 支持最大迭代次数限制。

防爆参数：

| 常量 | 默认值 | 说明 |
| --- | --- | --- |
| `WARNING_THRESHOLD` | 10 | 同一工具签名重复到达该次数后提示警告。 |
| `FUSE_THRESHOLD` | 20 | 同一工具签名重复到达该次数后终止执行。 |
| `WINDOW_SIZE` | 30 | 统计重复工具调用的滑动窗口大小。 |

### 6.6 `agent/context.py`

[agent/context.py](agent/context.py) - `ContextBuilder` 负责生成 system prompt。它会合并：

- [identity.md](identity.md) 或默认身份说明。
- 当前时间。
- 工作区路径。
- [workspace/memory/MEMORY.md](workspace/memory/MEMORY.md) 长期记忆。
- [skills/](skills/) 目录加载出的技能摘要。
- 记忆管理提示。

最终输出 OpenAI messages 格式：

```python
[
    {"role": "system", "content": "..."},
    ...history,
    {"role": "user", "content": current_message}
]
```

### 6.7 `agent/memory.py`

[agent/memory.py](agent/memory.py) - `MemoryConsolidator` 用于历史压缩。

流程：

1. 粗略估算 messages token 数。
2. 未超过预算时直接返回。
3. 超过预算时保留 system prompt 和最后 6 条消息。
4. 中间旧消息交给 LLM 总结。
5. 将总结作为新的 system 消息插回上下文。
6. 把压缩记录追加到 `workspace/memory/HISTORY.md`。

### 6.8 `session/manager.py`

[session/manager.py](session/manager.py) - `SessionManager` 负责会话持久化。

存储路径：

```text
workspace/sessions/
```

每个会话一个 JSONL 文件。会话 key 中的 `:` 会被替换为 `_`：

```text
cli:local -> workspace/sessions/cli_local.jsonl
web:<client_id> -> workspace/sessions/web_<client_id>.jsonl
```

每条保存的消息都会附带 `timestamp`。读取历史时会移除 `timestamp`，避免传给模型 API。

### 6.9 模块依赖关系

从运行方向看，主要依赖关系如下：

```text
main.py
  -> config.py
  -> providers/openai_compat.py
  -> agent/tools/*
  -> agent/context.py
  -> agent/loop.py
  -> session/manager.py
  -> bus/queue.py
  -> channels/*
  -> gateway.py
```

从消息处理方向看，依赖关系更接近：

```text
Channel
  -> MessageBus
  -> Gateway
  -> AgentLoop
  -> LLMProvider
  -> ToolRegistry
  -> Tool.execute()
  -> SessionManager
```

开发时建议按消息处理方向排查问题。例如“Web 页面发了消息但没回复”，不要先看模型，而应依次确认：

1. WebSocket 是否连接成功。
2. [channels/web.py](channels/web.py) 是否发布了 `InboundMessage`。
3. [gateway.py](gateway.py) 中的 `_process_inbound()` 是否消费到消息。
4. 对应 `session_key` 的 Agent 是否创建。
5. Provider 是否成功返回。
6. 是否卡在工具调用、MCP 连接或外部平台发送。

## 7. 工具系统

所有工具都继承 [agent/tools/base.py](agent/tools/base.py) 中的 `Tool` 抽象类。

每个工具必须提供：

- `name`
- `description`
- `parameters`
- `execute(**kwargs)`

`Tool.to_function_definition()` 会把工具转换为 OpenAI function calling 需要的格式：

```python
{
    "type": "function",
    "function": {
        "name": self.name,
        "description": self.description,
        "parameters": self.parameters
    }
}
```

### 7.1 `ToolRegistry`

[agent/tools/registry.py](agent/tools/registry.py) - `ToolRegistry` 是工具注册和执行中心：

- `register(tool)`：按工具名注册工具。
- `get_definitions()`：生成传给模型的 tools schema。
- `execute(name, arguments)`：查找并执行工具。
- `list_tools()`：列出已注册工具名。

工具执行异常会被捕获并转换为错误字符串，避免单个工具异常打断整个 Agent 流程。

### 7.2 文件系统工具

定义在 [agent/tools/filesystem.py](agent/tools/filesystem.py)：

- `read_file`：读取工作区内文件，超过 16000 字符会截断。
- `write_file`：写入工作区内文件，会自动创建父目录。
- `list_dir`：列出工作区内目录内容。

三个工具都会把目标路径解析到 `workspace` 下，并检查是否越界，防止路径穿越。

### 7.3 Shell 工具

定义在 [agent/tools/shell.py](agent/tools/shell.py)，工具名为 `exec`。

主要保护：

- 阻止递归删除、格式化磁盘、关机重启、权限提升、危险权限修改、设备文件覆盖、下载后执行脚本、后门监听、磁盘镜像覆盖和 fork 炸弹等模式。
- 命令在配置的 `workspace` 下执行。
- 默认 60 秒超时。
- 输出最多 10000 字符。

这个工具只是基础防护，不等同于完整沙箱。生产环境应进一步隔离运行用户、文件系统和网络权限。

### 7.4 Web 搜索与抓取工具

[agent/tools/web_search.py](agent/tools/web_search.py)：

- 使用 DuckDuckGo 搜索。
- 参数包括 `query` 和 `max_results`。
- 输出最多 8000 字符。

[agent/tools/web_fetch.py](agent/tools/web_fetch.py)：

- 只允许 `http` 和 `https` URL。
- 使用 `httpx` 抓取网页。
- 使用 `html2text` 转为 Markdown 风格文本。
- 默认 15 秒超时。
- 输出最多 12000 字符。

### 7.5 子 Agent 工具

定义在 [agent/tools/spawn.py](agent/tools/spawn.py)，工具名为 `spawn_subagent`。

用途：

- 创建临时子 Agent 执行子任务。
- 子 Agent 不持久化历史。
- 可使用不同模型。
- 支持最大嵌套深度，默认 `max_depth=2`。
- 子 Agent 默认最多迭代 16 轮。

它适合独立、多步骤、可拆分的任务，但简单任务不应过度使用子 Agent。

### 7.6 当前工具清单

`build_agent()` 默认注册以下本地工具：

| 工具名 | 类 | 参数 | 主要用途 |
| --- | --- | --- | --- |
| `read_file` | `ReadFileTool` | `file_path` | 读取工作区内文件 |
| `write_file` | `WriteFileTool` | `file_path`、`content` | 写入工作区内文件 |
| `list_dir` | `ListDirTool` | `dir_path` | 列出工作区内目录 |
| `exec` | `ExecTool` | `command` | 在工作区执行 Shell 命令 |
| `web_search` | `WebSearchTool` | `query`、`max_results` | 搜索互联网信息 |
| `web_fetch` | `WebFetchTool` | `url` | 抓取具体网页内容 |
| `spawn_subagent` | `SpawnSubagentTool` | `task`、`model` | 创建临时子 Agent 执行子任务 |

如果配置了 MCP Server，还会注册 MCP 工具，命名为 `{server_name}__{tool_name}`。

### 7.7 工具接口契约

新增工具时，需要遵守以下契约：

- `name` 必须唯一，否则后注册的同名工具会覆盖旧工具。
- `description` 要让模型知道“什么时候该用这个工具”，不要只写技术实现。
- `parameters` 必须是 JSON Schema 风格对象，模型会根据它生成参数。
- `execute()` 必须是异步方法，接收 `**kwargs`，返回字符串。
- 工具内部可以抛异常，但 `ToolRegistry.execute()` 会捕获异常并返回错误字符串。
- 工具结果会作为 `role="tool"` 的消息追加给模型，因此结果应简洁、可读、包含下一步判断所需信息。

对高风险工具还应额外说明：

- 文件工具必须做路径边界检查。
- Shell 工具应尽量白名单化，而不是只靠危险模式黑名单。
- 网络工具应限制协议、超时、响应大小和内网访问。
- 写入类工具应返回写入路径、字符数和失败原因。

## 8. MCP 集成

MCP 集成定义在 [agent/tools/mcp_server.py](agent/tools/mcp_server.py)。

### 8.1 工作方式

`MCPClientManager` 负责：

1. 读取 `mcp_servers` 配置。
2. 为每个 Server 创建 `StdioServerParameters`。
3. 通过 `stdio_client()` 启动子进程。
4. 创建并初始化 `ClientSession`。
5. 调用 `list_tools()` 获取工具列表。
6. 把每个 MCP 工具包装为 `MCPTool`。
7. 退出时依次关闭 session 和 stdio context。

MCP 工具命名格式：

```text
{server_name}__{tool_name}
```

例如：

```text
poetry__search_poetry
poetry__random_poetry
poetry__list_poets
```

这样可以避免多个 MCP Server 提供同名工具时冲突。

### 8.2 示例 MCP Server

[mcp_servers/poetry_server.py](mcp_servers/poetry_server.py) 使用 FastMCP 提供古诗词工具：

- `search_poetry(keyword)`：按关键词搜索诗词。
- `random_poetry()`：随机返回一首诗词。
- `list_poets()`：返回诗人列表。

单独运行：

```powershell
python mcp_servers/poetry_server.py
```

通过 NanoClaw 加载时，在 [config.json](config.json) 中配置：

```json
{
  "mcp_servers": {
    "poetry": {
      "command": "python",
      "args": ["mcp_servers/poetry_server.py"],
      "description": "古诗词查询服务"
    }
  }
}
```

### 8.3 MCP 测试

项目提供 [test_mcp.py](test_mcp.py)，用于快速验证 MCP Server 连接和工具加载：

```powershell
python test_mcp.py
```

该脚本会：

1. 读取配置。
2. 连接所有 MCP Server。
3. 打印已加载工具。
4. 尝试调用第一个工具。
5. 关闭连接。

### 8.4 MCP 实现注意点

当前 MCP 客户端实现有几个关键细节：

- 只支持 stdio 传输，暂未实现 SSE、HTTP Stream 或 WebSocket 传输。
- `ClientSession` 必须手动 `__aenter__()` 后再 `initialize()`，否则内部消息循环不会启动。
- 单个 Server 连接失败或超时不会中止整个 NanoClaw 启动流程，而是打印警告并跳过该 Server。
- MCP 工具执行失败会返回错误字符串，不会直接抛出到 Agent 主循环。
- 关闭时先退出 `ClientSession`，再退出 `stdio_client` context。

### 8.5 MCP Server 开发约束

新增 MCP Server 时，应注意：

- Server 进程的 stdout 会被 MCP 协议占用，不应随意打印调试内容。
- 如果需要日志，应写 stderr 或文件日志。
- 工具参数 schema 要清晰，否则模型容易构造错误参数。
- 工具返回值尽量是文本，当前 `MCPClientManager.call_tool()` 会优先提取 content item 上的 `text`。
- Server 启动命令和参数应使用相对项目根目录可解析的路径，避免换机器后失效。

## 9. 渠道系统

所有渠道都继承 [channels/base.py](channels/base.py) 中的 `Channel` 抽象类。

每个渠道必须实现：

- `start()`：启动渠道，接收用户消息。
- `send(message)`：发送 Agent 回复。

可选实现：

- `stop()`：释放连接或后台资源。

### 9.1 CLI 渠道

文件：[channels/cli.py](channels/cli.py)

特点：

- 使用 `asyncio.to_thread(input, ...)` 包装阻塞输入。
- 将普通输入转换为 `InboundMessage(channel="cli")`。
- 使用 `asyncio.Event` 等待当前回复完成后再读取下一条输入。
- 支持 `/exit`、`/clear`、`/tools`。

### 9.2 Web 渠道

文件：[channels/web.py](channels/web.py)

特点：

- 使用 FastAPI 提供 HTTP 和 WebSocket。
- `GET /` 返回 [channels/web_ui/index.html](channels/web_ui/index.html)。
- `WebSocket /ws` 接收和发送文本消息。
- 每个浏览器连接生成一个 `client_id`。
- `client_id` 同时作为 `sender_id` 和 `chat_id`，用于把回复发回对应连接。

Web 前端 `channels/web_ui/index.html` 提供：

- 聊天界面。
- Markdown 渲染。
- 代码高亮。
- 代码复制按钮。
- WebSocket 自动连接。
- 断开后延迟重连。

### 9.3 飞书渠道

文件：[channels/feishu.py](channels/feishu.py)

启用条件：

```json
{
  "feishu": {
    "app_id": "cli_xxx",
    "app_secret": "your_feishu_app_secret"
  }
}
```

特点：

- 使用飞书 SDK 建立 WebSocket 客户端。
- 监听 P2 消息事件。
- 过滤 Bot 自己发送的消息。
- 只处理文本消息。
- 去掉群消息里的 @ 前缀。
- 通过飞书 IM API 发送文本回复。

### 9.4 QQ 渠道

文件：[channels/qq.py](channels/qq.py)

启用条件：

```json
{
  "qq": {
    "app_id": "your_qq_app_id",
    "app_secret": "your_qq_app_secret"
  }
}
```

特点：

- 使用 `qq-botpy` 官方 SDK。
- 处理群内 @ 机器人消息。
- 处理 C2C 单聊消息。
- 将 QQ 消息转换为统一 `InboundMessage`。
- 发送时优先尝试 C2C，失败后尝试群消息。

### 9.5 渠道统一契约

所有渠道最终都要把外部消息转换成统一的 `InboundMessage`：

```python
InboundMessage(
    channel="渠道名",
    sender_id="发送者 ID",
    chat_id="回复目标 ID",
    content="用户文本",
    raw={...}
)
```

字段含义：

| 字段 | 含义 | 为什么重要 |
| --- | --- | --- |
| `channel` | 消息来源渠道，如 `cli`、`web`、`feishu`、`qq` | Gateway 根据它把回复发回对应 Channel |
| `sender_id` | 用户或连接标识 | Gateway 用它构造 `session_key` |
| `chat_id` | 回复目标 | Channel 发送消息时用它定位目标 |
| `content` | 纯文本用户输入 | 传给 Agent 的实际任务内容 |
| `raw` | 原始平台数据 | 排查平台差异和扩展功能时使用 |

`Gateway` 的会话 key 规则是：

```python
session_key = f"{inbound_msg.channel}:{inbound_msg.sender_id}"
```

因此，同一个用户在不同渠道会得到不同会话；同一个 Web 页面刷新后如果生成了新的 `client_id`，也会得到新的会话。

### 9.6 渠道发送规则

出站消息统一使用 `OutboundMessage`：

```python
OutboundMessage(
    channel="渠道名",
    chat_id="目标会话或连接 ID",
    content="回复文本"
)
```

发送时的关键点：

- CLI 不需要 `chat_id` 定位具体窗口，直接打印。
- Web 使用 `chat_id` 找回对应 WebSocket 连接。
- 飞书使用 `chat_id` 作为消息接收目标。
- QQ 当前发送逻辑无法从 `OutboundMessage` 直接判断群聊或私聊，因此先尝试 C2C，失败后再尝试群消息。

## 10. 技能系统

技能加载器定义在 [agent/skills.py](agent/skills.py)。

目录结构：

```text
skills/
  code_review/
    SKILL.md
  translator/
    SKILL.md
  weather/
    SKILL.md
```

`SkillsLoader` 会：

1. 扫描 `skills/` 下的子目录。
2. 查找每个子目录中的 `SKILL.md`。
3. 解析可选 YAML frontmatter。
4. 生成技能摘要。
5. 把摘要注入 system prompt。

`SKILL.md` 示例：

```markdown
---
name: code-review
description: 代码审查技能，检查代码质量和潜在问题
---

# 使用指南

...
```

当 Agent 需要使用某个技能时，可以先通过文件工具读取对应 `SKILL.md` 的详细内容。

### 10.1 当前技能清单

当前 `skills/` 目录中有三个技能：

| 技能目录 | name | description |
| --- | --- | --- |
| `skills/weather/` | `weather` | 查询指定城市的实时天气和温度 |
| `skills/translator/` | `translator` | 翻译文本，支持中文、英文、日文、韩文互译 |
| `skills/code_review/` | `code_review` | 审查 Python 代码文件，找出 bug、安全隐患和改进建议 |

这些技能不会像 `Tool` 那样直接注册为 function calling 工具。它们的作用是通过 `SkillsLoader.build_skills_summary()` 注入 system prompt，让 Agent 知道“有这些能力说明可读”。当需要使用某个技能时，Agent 应先读取对应 `SKILL.md` 获取详细步骤，再按步骤执行。

### 10.2 技能与工具的区别

| 对比项 | 技能 Skill | 工具 Tool |
| --- | --- | --- |
| 存放位置 | `skills/*/SKILL.md` | `agent/tools/*.py` |
| 加载方式 | 扫描 Markdown，注入 prompt 摘要 | 注册到 `ToolRegistry` |
| 调用方式 | Agent 阅读说明后自行执行 | 模型发起 function calling |
| 返回结果 | 没有固定返回接口 | `execute()` 返回字符串 |
| 适用场景 | 流程说明、行为规范、任务方法 | 可程序化执行的具体动作 |

## 11. 工作区与数据文件

### 11.1 会话历史

路径：

```text
workspace/sessions/
```

文件格式：JSONL。

这些文件是运行数据，不是核心源码。

### 11.2 长期记忆

路径：

```text
workspace/memory/MEMORY.md
workspace/memory/HISTORY.md
```

用途：

- `MEMORY.md`：长期记忆，由 system prompt 指引 Agent 在有长期价值时更新。
- `HISTORY.md`：上下文压缩记录，由 `MemoryConsolidator` 追加写入。

### 11.3 日志与缓存

根目录下存在 `botpy.log*` 和多个 `__pycache__/` 目录。它们属于运行产物或缓存，不应作为项目核心文档内容维护。

## 12. 如何扩展项目

### 12.1 新增本地工具

步骤：

1. 在 [agent/tools/](agent/tools/) 下新增工具类。
2. 继承 `Tool`。
3. 实现 `name`、`description`、`parameters`、`execute()`。
4. 在 [main.py](main.py) 的 `build_agent()` 中注册：

```python
tools.register(MyNewTool(config.workspace))
```

建议：

- 参数 schema 保持简单明确。
- `execute()` 返回字符串。
- 捕获必要异常，避免工具内部异常直接影响 Agent。
- 涉及文件、命令、网络时要有边界检查。

### 12.2 新增渠道

步骤：

1. 在 [channels/](channels/) 下新增渠道类。
2. 继承 `Channel`。
3. 实现 `start()` 和 `send()`。
4. 把外部平台消息转换为 `InboundMessage`。
5. 在 [main.py](main.py) 中根据配置注册渠道。

关键约定：

- `channel` 字段必须与渠道名一致。
- `sender_id` 用于区分用户。
- `chat_id` 用于发送回复。
- 原始平台数据可放入 `raw`，便于调试。

### 12.3 新增 MCP Server

步骤：

1. 编写一个支持 stdio 的 MCP Server。
2. 在 [config.json](config.json) 的 `mcp_servers` 中新增配置。
3. 启动 NanoClaw 或运行 `python [test_mcp.py](test_mcp.py)` 验证。

配置示例：

```json
{
  "mcp_servers": {
    "my_server": {
      "command": "python",
      "args": ["mcp_servers/my_server.py"],
      "description": "我的 MCP 服务"
    }
  }
}
```

### 12.4 新增技能

步骤：

1. 在 [skills/](skills/) 下创建子目录。
2. 新增 `SKILL.md`。
3. 写入 frontmatter 和使用说明。
4. 重启项目，让 `SkillsLoader` 重新扫描。

## 13. 安全注意事项

### 13.1 凭据安全

当前项目配置文件中存在真实 API Key 和平台密钥。建议：

- 不把真实密钥提交到代码仓库。
- 使用环境变量覆盖 `api_key`。
- 将飞书、QQ 等平台密钥放入私有配置或密钥管理系统。
- 如果密钥已经暴露，应立即在对应平台轮换。

### 13.2 文件和 Shell 工具风险

虽然文件工具限制在 `workspace` 内，Shell 工具也有危险命令拦截，但这些只是基础防护。

生产环境建议：

- 使用独立低权限用户运行。
- 对工作区做最小权限控制。
- 对 Shell 工具加更严格的命令白名单。
- 在容器或沙箱中运行 Agent。
- 不向不可信用户开放写文件和执行命令能力。

### 13.3 Web 抓取风险

`web_fetch` 会访问用户指定 URL。生产环境中需要考虑：

- SSRF 防护。
- 内网地址拦截。
- 文件协议、特殊协议拦截。
- 响应大小限制。
- 超时和重定向策略。

当前实现只允许 `http/https`，但没有完整内网地址防护。

### 13.4 Web UI 风险

前端会渲染模型返回的 Markdown。虽然用户消息使用 `escapeHtml()`，但 Bot 消息由 `marked.parse()` 渲染。生产环境需要确认 Markdown 渲染器的安全配置，避免 XSS 风险。

## 14. 常见问题

### 14.1 终端中文显示乱码

当前部分源码注释和输出在 PowerShell 中可能显示为乱码。这通常与终端编码、文件编码或历史写入编码有关。

建议：

- 确认源码文件使用 UTF-8。
- PowerShell 中可尝试：

```powershell
chcp 65001
```

- 不要把终端显示出的乱码重新复制写入源码或文档。

### 14.2 启动时报 API Key 未配置

`build_agent()` 会检查 `config.api_key`。如果为空，会提示配置 API Key。

解决方式：

```powershell
$env:NANOCLAW_API_KEY = "sk-your-api-key"
python main.py
```

或者在 [config.json](config.json) 中配置 `api_key`，但不推荐长期这样做。

### 14.3 MCP Server 连接超时

`main.py` 中 MCP 连接默认超时 30 秒，`test_mcp.py` 中默认 10 秒。

排查：

- 确认 `command` 路径正确。
- 确认 `args` 路径相对项目根目录可访问。
- 确认 MCP Server 不向 stdout 打印协议外内容。
- 单独运行 MCP Server 或使用 MCP Inspector 检查。

### 14.4 Web 页面打不开

排查：

- `config.json` 中 `web.enabled` 是否为 `true`。
- 端口是否被占用。
- 启动日志中是否出现 WebChannel 启动信息。
- 本机访问使用 `http://127.0.0.1:8080`。

### 14.5 飞书或 QQ 渠道未启用

飞书需要同时配置 `feishu.app_id` 和 `feishu.app_secret`。

QQ 需要同时配置 `qq.app_id` 和 `qq.app_secret`。

如果缺少任意一个字段，`main.py` 会跳过对应渠道。

### 14.6 Agent 一直调用同一个工具

`AgentLoop` 有重复工具调用检测：

- 同一工具名和同一参数重复 10 次后警告。
- 重复 20 次后熔断终止。

如果频繁触发，通常说明：

- 模型没有理解工具结果。
- 工具返回内容不够清晰。
- system prompt 对任务终止条件描述不足。
- 用户任务本身缺少明确成功条件。

### 14.7 调用搜索或网页抓取时报缺包

`web_search` 在执行时才导入 `ddgs`，`web_fetch` 在执行时才导入 `html2text`。如果启动项目正常，但调用这两个工具时报 `No module named ...`，优先检查依赖是否安装：

```powershell
pip install ddgs html2text
```

后续建议把这两个包补入 [requirements.txt](requirements.txt)，否则新环境按依赖文件安装后仍可能缺少搜索和抓取能力。

### 14.8 会话历史过长或污染

会话历史保存在 `workspace/sessions/*.jsonl`。如果 Agent 表现异常、一直引用旧上下文，或测试时希望从干净状态开始，可以：

- CLI 中输入 `/clear` 清空当前 CLI 会话。
- 手动删除对应 `workspace/sessions/<session>.jsonl`。
- 临时换一个渠道或 sender_id，让 Gateway 创建新 session。

注意不要误删用户仍需要保留的历史记录。

### 14.9 修改 `identity.md` 后没有看到效果

`ContextBuilder` 每次构造 system prompt 时会读取 `identity.md`，但已经缓存到某个 Agent 实例里的历史仍会继续存在。修改身份文件后建议：

- 重启项目。
- 清空相关会话历史。
- 再发起新对话验证。

### 14.10 Web UI 显示在线但没有回复

排查顺序：

1. 浏览器 Network 面板确认 `/ws` 是否保持连接。
2. 终端日志确认 `WebChannel` 是否收到消息。
3. 检查模型 API Key 和 base_url 是否可用。
4. 检查是否卡在 MCP 连接、工具执行或外部网络请求。
5. 如果是模型调用失败，`OpenAICompatProvider` 会返回错误响应，Agent 可能输出通用错误提示。

## 15. 当前工程状态建议

基于当前代码状态，后续可以优先改进：

1. 凭据治理：移除 [config.json](config.json) 中真实密钥，改为本地私有配置或环境变量。
2. 依赖治理：把 [requirements.txt](requirements.txt) 精简为 NanoClaw 直接依赖。
3. 依赖补齐：把源码实际使用但当前依赖文件缺失的 `ddgs`、`html2text` 补入安装说明或依赖文件。
4. 编码治理：统一源码注释和 Markdown 文件为 UTF-8。
5. 安全增强：为 Shell、文件、Web 抓取工具增加更严格的沙箱和白名单。
6. 测试补齐：增加 ToolRegistry、文件工具路径边界、SessionManager、MCP 包装和 Gateway 路由的单元测试。
7. 文档拆分：如果后续内容继续增长，可把本文档拆成 `docs/architecture.md`、`docs/configuration.md`、`docs/channels.md` 和 `docs/mcp.md`。

## 16. 文件结构速览

```text
nanoclaw/
  main.py                  # 启动入口，组装 Agent、渠道、MCP 和 Gateway
  gateway.py               # 多渠道消息网关
  config.py                # 配置结构和加载逻辑
  config.json              # 本地配置文件
  identity.md              # Agent 身份和行为准则
  MCP_INTEGRATION.md       # MCP 集成说明
  test_mcp.py              # MCP 连接和工具加载测试
  requirements.txt         # Python 依赖

  providers/
    base.py                # LLM Provider 抽象和响应结构
    openai_compat.py       # OpenAI-compatible Provider

  agent/
    loop.py                # Agent 主循环
    context.py             # System prompt 构造
    memory.py              # 历史压缩
    skills.py              # 技能加载
    tools/
      base.py              # Tool 抽象
      registry.py          # 工具注册表
      filesystem.py        # 文件工具
      shell.py             # Shell 工具
      web_search.py        # 搜索工具
      web_fetch.py         # 网页抓取工具
      spawn.py             # 子 Agent 工具
      mcp_server.py        # MCP 工具包装和客户端管理

  channels/
    base.py                # Channel 抽象
    cli.py                 # CLI 渠道
    web.py                 # WebSocket Web 渠道
    feishu.py              # 飞书渠道
    qq.py                  # QQ 渠道
    web_ui/index.html      # Web 前端页面

  bus/
    queue.py               # 入站/出站消息总线

  session/
    manager.py             # 会话 JSONL 持久化

  skills/
    */SKILL.md             # 可加载技能说明

  mcp_servers/
    poetry_server.py       # 古诗词 MCP Server 示例

  workspace/
    sessions/              # 会话历史
    memory/                # 长期记忆和压缩历史
```

## 17. 本地验证清单

如果要验证项目是否能在新环境运行，建议按下面顺序执行。

### 17.1 静态检查

```powershell
python -m py_compile main.py gateway.py config.py
python -m py_compile agent\loop.py agent\context.py agent\memory.py agent\skills.py
python -m py_compile providers\base.py providers\openai_compat.py
python -m py_compile bus\queue.py session\manager.py
python -m py_compile channels\base.py channels\cli.py channels\web.py
python -m py_compile agent\tools\base.py agent\tools\registry.py agent\tools\filesystem.py
python -m py_compile agent\tools\shell.py agent\tools\web_search.py agent\tools\web_fetch.py
python -m py_compile agent\tools\spawn.py agent\tools\mcp_server.py
```

静态检查能发现语法错误和部分导入路径问题，但不能证明外部平台、模型 API 或 MCP 工具可用。

### 17.2 依赖检查

```powershell
python -c "import openai, fastapi, uvicorn, httpx, yaml, mcp"
python -c "import ddgs, html2text"
```

如果第二条失败，说明搜索或网页抓取工具的运行依赖不完整。

### 17.3 MCP 检查

```powershell
python test_mcp.py
```

预期结果：

- 能读取 `config.json` 中的 `mcp_servers`。
- 能连接至少一个 MCP Server。
- 能打印已加载 MCP 工具。
- 能调用一个测试工具。
- 最后正常 shutdown。

如果配置了社区 filesystem MCP，需要确认本机有 `npx` 且网络/缓存可用。

### 17.4 启动检查

```powershell
python main.py
```

预期结果：

- CLI 对话启动。
- 如果 `web.enabled=true`，Web 服务启动。
- `/tools` 能显示本地工具和可用 MCP 工具。
- 输入普通问题后能收到模型回复。
- 如果要求读文件或列目录，Agent 能调用对应工具。

### 17.5 Web 检查

访问：

```text
http://127.0.0.1:8080
```

预期结果：

- 页面能加载。
- 状态显示在线。
- 输入消息后 WebSocket 能发出请求。
- 回复能追加到页面。
- Markdown 和代码块能正常渲染。

## 18. 交接清单

交接项目时建议至少确认以下内容：

| 项目 | 需要确认的内容 |
| --- | --- |
| 凭据 | `config.json` 中是否仍有真实密钥，是否已轮换或迁移 |
| Python 环境 | 使用的 Python 版本、虚拟环境路径、依赖安装方式 |
| 模型服务 | `base_url`、主模型、子 Agent 模型是否可用 |
| 本地工具 | 文件、Shell、搜索、抓取、子 Agent 是否按预期可用 |
| MCP | 哪些 Server 启用、启动命令是否依赖本机绝对路径 |
| 渠道 | CLI、Web、飞书、QQ 哪些应启用，哪些只是开发残留配置 |
| 数据 | `workspace/sessions` 和 `workspace/memory` 是否需要保留 |
| 安全 | 是否允许不可信用户访问写文件、执行命令和网页抓取能力 |
| 测试 | 是否跑过第 17 章验证清单 |

## 19. 一句话总结

NanoClaw 的核心是一个可扩展的异步 Agent 框架：入口层负责启动和装配，Gateway 负责多渠道消息路由，AgentLoop 负责模型与工具循环，ToolRegistry 和 MCP 负责能力扩展，SessionManager 和 MemoryConsolidator 负责对话状态管理。
