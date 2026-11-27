"""
大模型工程师毕业考核 · 本地裁判
用法：  python3 grad_judge.py s1 --challenge 挑战码   （挑战码在毕业考核网页上领取）
生成：  report_s1.json  → 上传到毕业考核网页

阶段一要求你在同一目录放一个 my_gpt.py，提供：
    load() -> (model, meta)
        model: torch.nn.Module，调用 model(idx) 返回 logits，形状 [B, T, vocab_size]
               并提供 model.generate(idx, max_new_tokens, use_cache) 贪心生成，返回 [B, T+max_new_tokens]
        meta : {"vocab_size": int, "block_size": int}
以及训练时写出的 train_log.json：{"val_bpc": 最新一次验证集每字比特数, "train_minutes": 训练总分钟数}
"""
import hashlib, json, sys, datetime, pathlib

HERE = pathlib.Path(__file__).resolve().parent
VERSION = "1.1"
CHALLENGE = ""


def code_hash(*names):
    h = hashlib.sha256()
    for n in names:
        p = HERE / n
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


def device_name():
    import torch
    if torch.cuda.is_available():
        return "cuda:" + torch.cuda.get_device_name(0)
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        import platform
        return "mps:Apple " + (platform.processor() or "Silicon")
    return "cpu"


def seed_from(code):
    return int(hashlib.sha256(code.encode()).hexdigest()[:8], 16)


def stage1():
    import torch
    sys.path.insert(0, str(HERE))
    import my_gpt
    torch.manual_seed(seed_from(CHALLENGE))  # 测试输入由挑战码决定，无法提前准备
    model, meta = my_gpt.load()
    model.eval()
    V, block = int(meta["vocab_size"]), int(meta["block_size"])
    m, notes = {}, []

    m["params"] = sum(p.numel() for p in model.parameters())

    # 形状测试
    T = min(16, block)
    idx = torch.randint(0, V, (2, T))
    with torch.no_grad():
        out = model(idx)
    logits = out[0] if isinstance(out, (tuple, list)) else out
    m["shape_ok"] = tuple(logits.shape) == (2, T, V)
    if not m["shape_ok"]:
        notes.append(f"形状应为 (2, {T}, {V})，实际是 {tuple(logits.shape)}")

    # 因果性测试：只改 t 之后的字，位置 0..t 的输出不能变
    worst = 0.0
    with torch.no_grad():
        for t in range(T - 1):
            x2 = idx.clone()
            x2[:, t + 1:] = torch.randint(0, V, (2, T - t - 1))
            a = model(idx); a = a[0] if isinstance(a, (tuple, list)) else a
            b = model(x2); b = b[0] if isinstance(b, (tuple, list)) else b
            worst = max(worst, (a[:, : t + 1] - b[:, : t + 1]).abs().max().item())
    m["causal_max_diff"] = worst
    if worst >= 1e-5:
        notes.append("改动未来的字影响了当前输出：检查注意力遮罩")

    # KV Cache 一致性
    start = torch.randint(0, V, (1, 4))
    with torch.no_grad():
        g1 = model.generate(start.clone(), 24, use_cache=False)
        g2 = model.generate(start.clone(), 24, use_cache=True)
    m["kv_cache_match"] = bool(torch.equal(g1, g2))
    if not m["kv_cache_match"]:
        n = int((g1 != g2).nonzero()[0, 1]) if g1.shape == g2.shape else -1
        notes.append(f"带 / 不带 KV Cache 的生成从第 {n} 个位置开始不同")

    # 验证集 bpc
    log = HERE / "train_log.json"
    if log.exists():
        lg = json.loads(log.read_text())
        m["val_bpc"] = float(lg["val_bpc"])
        if "train_minutes" in lg:
            m["train_minutes"] = float(lg["train_minutes"])
        else:
            notes.append("train_log.json 里没有 train_minutes")
    else:
        notes.append("没找到 train_log.json")
    return m, notes, code_hash("my_gpt.py", "train_log.json")


STAGES = {"s1": stage1}


def main():
    global CHALLENGE
    args = sys.argv[1:]
    s = args[0] if args else ""
    if "--challenge" in args and args.index("--challenge") + 1 < len(args):
        CHALLENGE = args[args.index("--challenge") + 1].strip().upper()
    if s in STAGES and not CHALLENGE:
        print("缺少挑战码：先在毕业考核网页上领取，然后运行  python3 grad_judge.py " + s + " --challenge 挑战码")
        sys.exit(1)
    if s not in STAGES:
        print("用法：python3 grad_judge.py s1 --challenge 挑战码")
        print("目前开放：", ", ".join(STAGES), "（其余阶段的裁判在解锁时发布）")
        sys.exit(1)
    metrics, notes, h = STAGES[s]()
    rep = {"kind": "llm-grad-report", "stage": s, "judge_version": VERSION,
           "challenge": CHALLENGE, "device": device_name(),
           "created": datetime.datetime.now().isoformat(timespec="seconds"),
           "code_hash": h, "metrics": metrics, "notes": notes}
    out = HERE / f"report_{s}.json"
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=2))
    for k, v in metrics.items():
        print(f"  {k:18s} {v}")
    for n in notes:
        print("  ⚠️", n)
    print(f"\n成绩单已生成：{out}\n把它上传到毕业考核网页。")


if __name__ == "__main__":
    main()
