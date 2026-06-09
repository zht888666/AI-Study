# Intake And Running Depth

When the user only provides a JD, ask a short intake before recommending projects.

Ask for:

- 当前水平：语言基础、框架经验、是否做过完整项目。
- 技术栈偏好：必须贴合 JD，但允许候选人选择更熟悉的实现语言。
- 时间预算：总天数、每天可投入时间、是否有面试或投递 deadline。
- 资源条件：操作系统、本地内存、Docker、数据库、云服务器、GPU/AutoDL。
- 运行深度：`interview-only`、`smoke-test`、`local-full-run`、`remote-full-run`。

If the user does not answer, proceed with conservative defaults:

- 当前水平：低经验候选人。
- 技术栈偏好：优先使用 JD 明确要求且用户最可能掌握的主流栈。
- 时间预算：7-10 天。
- 资源条件：普通 Windows/Mac/Linux 本地环境，无付费云资源。
- 运行深度：`smoke-test`。

Depth rules:

- `interview-only`: prepare understanding and interview material only; do not claim the project has been run.
- `smoke-test`: verify one minimal startup command, health endpoint, CLI command, notebook cell, or core script.
- `local-full-run`: run the main local workflow end to end, including database or mock data when needed.
- `remote-full-run`: plan remote resources only when local execution is not enough.
