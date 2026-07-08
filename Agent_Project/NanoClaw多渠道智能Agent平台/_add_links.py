import re

# Known file paths (longest first to avoid partial matches)
files = [
    "agent/tools/mcp_server.py",
    "agent/tools/filesystem.py",
    "agent/tools/web_search.py",
    "agent/tools/web_fetch.py",
    "agent/tools/base.py",
    "agent/tools/shell.py",
    "agent/tools/spawn.py",
    "mcp_servers/poetry_server.py",
    "providers/openai_compat.py",
    "providers/base.py",
    "channels/base.py",
    "channels/web.py",
    "channels/cli.py",
    "channels/feishu.py",
    "channels/qq.py",
    "session/manager.py",
    "agent/memory.py",
    "agent/context.py",
    "agent/skills.py",
    "agent/loop.py",
    "bus/queue.py",
    "gateway.py",
    "config.json",
    "config.py",
    "identity.md",
    "main.py",
    "test_mcp.py",
    "requirements.txt",
    "agent/tools/",
    "channels/",
    "mcp_servers/",
    "providers/",
    "session/",
    "bus/",
    "agent/",
    "skills/",
    "workspace/sessions/",
    "workspace/memory/",
]

# Sort by length (longest first)
files.sort(key=len, reverse=True)

with open('PROJECT_DOCUMENTATION.md', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
in_code_block = False
result_lines = []

for line in lines:
    if line.strip().startswith('```'):
        in_code_block = not in_code_block
        result_lines.append(line)
        continue
    
    if in_code_block:
        result_lines.append(line)
        continue
    
    # Process inline code in this line
    def replace_inline(match):
        text = match.group(1)
        for f in files:
            if text == f:
                return f'[`{text}`]({f})'
        return f'`{text}`'
    
    line = re.sub(r'`([^`]+)`', replace_inline, line)
    result_lines.append(line)

print('\n'.join(result_lines))
