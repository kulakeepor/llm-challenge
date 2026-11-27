# 版本、更新与回滚

这个仓库是「挑战大模型工程师」的唯一源头：网页源码、任务包、本地裁判都在这里。线上网页是一个 Claude Artifact，地址固定为 <https://claude.ai/artifact/Gqn9v7mWLPYjJ8SbzNmus7>。

## 版本号

用语义化版本 `vMAJOR.MINOR.PATCH`：

| 改动 | 版本位 | 例子 |
|---|---|---|
| 存档格式变了，或旧的成绩单 / 备份不再兼容 | MAJOR | v3 → v4 |
| 新功能、新阶段的任务包或裁判 | MINOR | v3.0 → v3.1 |
| 修 bug、改文案、调阈值 | PATCH | v3.1.0 → v3.1.1 |

页面存档格式的版本（localStorage 里的 `v`）和 MAJOR 保持一致，目前是 3。

裁判 `judge/grad_judge.py` 有自己的 `VERSION`（目前 1.1），会写进每份成绩单。改裁判时同时改它，并在 CHANGELOG 里写明。

## 更新流程

1. 从 `main` 拉分支：`feat/…`、`fix/…`、`docs/…`。
2. 改动、自测（网页改动要跑一遍阶段一全流程，见 CHANGELOG 里每版的测试记录）。
3. 开 PR，写清楚改了什么、怎么测的、是否影响存档兼容。
4. 合并进 `main`。
5. 在 `main` 上打 tag 并建 GitHub Release：`git tag vX.Y.Z && git push origin vX.Y.Z`。
6. 网页有改动时：把这个 tag 的 `web/index.html` 发布到同一个 Artifact 地址，然后把 Artifact 返回的版本号写进这个 Release 的说明里。

`main` 上任何时候都应该是线上正在用的版本或即将发布的版本。

## 回滚

**网页**：找到要回到的 tag，取出那一版的 `web/index.html`，重新发布到同一个 Artifact 地址。

```bash
git show v3.0.0:web/index.html > /tmp/index.html   # 再把这个文件发布到 Artifact
```

Artifact 自身也保留历史版本，每个 Release 的说明里都记着对应的 Artifact 版本号，可以对照。

**仓库**：不改写历史。用 `git revert <合并提交>` 开一个回滚 PR，合并后打一个新的 PATCH tag。

**学员数据**：进度存在学员自己的浏览器里，回滚网页不会删数据。但如果回滚跨过了存档格式升级（MAJOR），旧页面可能读不懂新存档，所以 MAJOR 升级前要确认迁移函数可逆，或者提醒学员先导出备份。
