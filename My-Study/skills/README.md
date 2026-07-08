# JD 实习项目准备工具包

`internship-project-kit` 是一个 Codex Skill，用于把目标 JD 转成可投递、可面试、可讲清的计算机实习项目准备材料。

它适合后端、前端、全栈、移动端、测试开发、数据工程、云原生/DevOps、安全、系统、AI/算法等方向，尤其适合 0 经验或低经验候选人快速完成项目选题、开源项目理解、运行规划、面试化改造和简历表达。

## 能做什么

- 解析 JD 中的岗位职责、任职要求、技术栈、业务方向、地点、学历和毕业时间限制。
- 只给 JD 时，先补充候选人 intake：当前水平、技术栈偏好、时间预算、资源条件、运行深度。
- 联网抓取 GitHub/Gitee 候选项目元数据，并按岗位匹配度、上手速度、可讲亮点、运行成本和改造空间排序。
- 审计已 clone 的项目，生成 `audit.json`、`overview.md` 和 `overview.html`。
- 规划 baseline run，优先本地最小路径跑通，不足时再规划云服务器、数据库、对象存储、GPU/AutoDL 等远程资源。
- 生成面试包：STAR 简历项目、核心代码讲解、面试官拷问 Q&A、PPT 提示词和投递检查表。

## 安装

将 skill 目录复制到 Codex 的用户 skills 目录：

```powershell
Copy-Item -Recurse -Force "E:\homework\homework\My Studay\skills\internship-project-kit" "C:\Users\ASUS\.codex\skills\internship-project-kit"
```

如果你从 Gitee clone 本仓库，复制仓库中的 `My Studay/skills/internship-project-kit` 目录即可。

## 推荐用法

```text
使用 $internship-project-kit，根据下面这份 JD 帮我规划一个能投递、能面试、能讲清的计算机实习项目。

我的情况:
当前水平:
熟悉语言/框架:
时间预算:
本地/远程资源:
希望运行深度: interview-only / smoke-test / local-full-run / remote-full-run

JD:
```

如果暂时不知道怎么填，可以只给 JD，让 skill 先问 intake。

## 联网抓取器

抓取器只获取公开项目元数据，不自动 clone，不运行远程代码。

```powershell
E:\anaconda3\python.exe "E:\homework\homework\My Studay\skills\internship-project-kit\scripts\fetch_project_candidates.py" --query "fastapi project" --language Python --sources github --per-source 2 --output project-candidates.json
```

可选环境变量：

- `GITHUB_TOKEN`
- `GITEE_TOKEN`

没有 token 时使用匿名请求。脚本不会保存或打印 token。

## 校验

Windows 中文环境下建议用 Python UTF-8 模式校验 skill：

```powershell
E:\anaconda3\python.exe -X utf8 "C:\Users\ASUS\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "E:\homework\homework\My Studay\skills\internship-project-kit"
```

## 输出物

默认生成到 `project-prep/`：

```text
project-candidates.json
project-candidates.md
audit.json
overview.md
overview.html
baseline-run-plan.md
modification-plan.md
resume-star.md
core-code-walkthrough.md
interview-qa.md
ppt-prompts.md
submission-checklist.md
```

## 免责声明

本工具用于学习、项目准备和表达训练。开源项目推荐、运行方案和面试材料需要用户自行验证。不要伪造项目经历，不要把计划改造包装成已经完成的工作，不要隐瞒外部开源项目来源和自己的真实贡献。
