# 挑战大模型工程师

一场开放给所有人的毕业考核：五个阶段加一场答辩。全部通过，就具备入门级大模型工程师的能力：懂原理、能训练、能调试、能评测、能微调、能交付。

**考场（网页）**：<https://claude.ai/artifact/Gqn9v7mWLPYjJ8SbzNmus7>

| 阶段 | 内容 | 任务包 |
|---|---|---|
| 一 · 造 | 从零手写 mini-GPT | ✅ [Colab 模板](https://colab.research.google.com/github/kulakeepor/llm-challenge/blob/main/notebooks/s1_mini_gpt.ipynb) · [接口约定](docs/my_gpt_interface.md) |
| 二 · 调 | 拆弹：修好下了毒的训练代码 | 随课程发布 |
| 三 · 练 | 扩展定律与消融实验 | 随课程发布 |
| 四 · 对齐 | SFT + DPO，把续写机变成助手 | 随课程发布 |
| 五 · 交付 | 量化、API、模型卡 | 随课程发布 |
| 答辩 | AI 考官从你的材料里出 4 题 | 网页内完成 |

## 怎么考

1. 在网页上选算力（Colab 免费 T4 或自己的 Apple Silicon Mac），进入阶段页面**领取挑战码**。
2. 完成任务，用本地裁判生成成绩单：
   ```bash
   python3 grad_judge.py s1 --challenge 你的挑战码
   ```
3. 在网页上交三样证据：**成绩单**（`report_s1.json`）、**公开仓库**、**书面材料**（AI 考官批改）。三样都过，盖章通关，自动进入你的作品集。

进度只保存在你的浏览器里，可以导出备份。作品集可以导出成独立网页。

## 仓库结构

```
judge/grad_judge.py          本地裁判（目前开放阶段一）
notebooks/s1_mini_gpt.ipynb  阶段一 Colab 模板（Mac 上用 Jupyter 打开也能跑）
docs/my_gpt_interface.md     阶段一接口约定
docs/RELEASE.md              版本、更新与回滚规则
web/index.html               考场网页源码（线上 Artifact 由它发布）
CHANGELOG.md                 更新记录
```

## 防造假的边界

训练发生在你自己的设备上，没有任何网页能彻底防止伪造。这份考核的可信度来自公开、可复现的证据：挑战码、代码指纹、公开仓库和答辩。别人随时可以克隆你的仓库重跑一遍。

标“暂定”的阈值和算力预算，会在参考解法分别于 Colab T4 和 Apple Silicon Mac 上实测后校准。
