# 阶段一接口约定：my_gpt.py

本地裁判 `judge/grad_judge.py`（v1.1）只通过 `my_gpt.py` 认识你的模型。把 `grad_judge.py`、`my_gpt.py`、`train_log.json`（以及 `my_gpt.py` 要读取的权重文件）放在**同一个文件夹**里运行裁判。

## my_gpt.py 必须提供

```python
def load():
    """返回 (model, meta)"""
    return model, {"vocab_size": int, "block_size": int}
```

- `model` 是 `torch.nn.Module`。
- `model(idx)`：`idx` 是 `[B, T]` 的整数张量，返回 logits，形状 `[B, T, vocab_size]`。也可以返回 `(logits, …)` 元组，裁判取第一个元素。
- `model.generate(idx, max_new_tokens, use_cache)`：**贪心**生成（每步取概率最大的 token），返回 `[B, T + max_new_tokens]`。`use_cache=True` 时用 KV Cache，`False` 时每步重新计算整段序列。

## train_log.json

训练时写出，裁判读取其中两个字段：

```json
{"val_bpc": 6.41, "train_minutes": 95.3}
```

- `val_bpc`：最新一次验证集**每字比特数** = 验证集总负对数似然（自然对数）÷ 验证集字符数 ÷ ln 2。
- `train_minutes`：训练总耗时（分钟），用 `time.time()` 实测。

## 裁判检查什么

| 指标 | 要求 | 怎么测 |
|---|---|---|
| 参数量 | 500 万 – 5000 万 | `sum(p.numel() for p in model.parameters())` |
| 形状 | `(2, T, vocab_size)` | 随机输入，`T = min(16, block_size)` |
| 因果性 | 最大变化 < 1e-5 | 只改第 t 个位置之后的输入，比较前 t+1 个位置的输出 |
| KV Cache 一致 | 完全一致 | 同一个 4-token 开头，带 / 不带 cache 各生成 24 个 |
| 验证 bpc | ≤ 7.0（暂定） | 读 `train_log.json` |
| 训练耗时 | T4 ≤ 120 分钟，Mac ≤ 240 分钟（暂定） | 读 `train_log.json`，网页按你选的算力判定 |

另外：
- 随机测试输入的种子由**挑战码**决定，没法提前准备。
- 成绩单里的 `device` 来自 `torch`：Colab T4 是 `cuda:Tesla T4`，Mac 是 `mps:…`。网页会核对它和你选的算力是否一致。
- `code_hash` 是 `my_gpt.py` 和 `train_log.json` 的 SHA-256 前 16 位，会写进作品集，别人克隆你的仓库后可以核对。

## 规则

不准使用 `transformers` 或任何现成的注意力 / Transformer 模块（如 `nn.MultiheadAttention`、`nn.TransformerEncoder`、`F.scaled_dot_product_attention`）。可以用基础层（`nn.Linear`、`nn.Embedding`、`nn.LayerNorm` 等）和张量运算。
