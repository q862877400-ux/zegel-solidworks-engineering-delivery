"""★ 解压 DSH 会话日志（zstd）并数出**实际用的模型路由**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   DSH 会话日志（不是 SW 仓库）
# 文件:   C:\Users\Zegel\.dsh\sessions\--D-AI-SW--\<会话id>\session.v4.jsonl.zstd
# 定位:   ★★★ **一个必须查清的事实**：业主两次因「派出去的是 DeepSeek 而不是 bunny」发火
# 。
#           `list_agents` 现在显示**已结束**的 bunny-vf4/vf5/vf6 是 `deepseek-flash`，
#           而它们 spawn 时返回的是 `"model":"space-bunny-free"` ⇒ ★ **两者矛盾，我不能猜** ✓
#         ★★ 本脚本是**唯一能定案的证据源**：会话日志记的是**实际用的路由**，不是"应该用的" ✓
#           （遥测目录是空的；日志是 `.jsonl.zstd` ⇒ 纯文本 grep 命中 0，**必须先解压**）✓
# 官方依据: 不适用（本机事实核查）
# 许可:   本机数据，无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★ 会话 id → 名字（取自 `list_agents` / 完成通知）
SESSIONS = {
    "2d099855-3f17-4e72-ad5f-a4a79bfcec92": "bunny-vf4",
    "20b40369-32a3-412d-aa42-885d50d579e8": "bunny-vf6",
    "8009e438-da57-4870-81bf-111e348b0577": "bunny-vf5",
}
ROOT = Path(r"C:\Users\Zegel\.dsh\sessions\--D-AI-SW--")
MARKS = ("space-bunny-free", "deepseek-flash", "opencode-zen", "deepseek-official",
         "gemini-3.8-flash", "opencode", "zen")


def decompress(p: Path) -> bytes:
    """★ 三级降级：stdlib `compression.zstd` → `zstandard` 包 → `zstd` CLI。"""
    try:
        from compression import zstd                              #: ★ Python 3.14 自带
        return zstd.decompress(p.read_bytes())
    except Exception:                                             # noqa: BLE001
        pass
    try:
        import zstandard                                          # type: ignore
        return zstandard.ZstdDecompressor().decompress(p.read_bytes())
    except Exception:                                             # noqa: BLE001
        pass
    import subprocess
    r = subprocess.run(["zstd", "-d", "-c", str(p)], capture_output=True)
    if r.returncode == 0:
        return r.stdout
    raise RuntimeError("三种解压方式都失败")


def main() -> int:
    for sid, who in SESSIONS.items():
        log = ROOT / sid / "session.v4.jsonl.zstd"
        if not log.is_file():
            print("★ %-10s 找不到日志：%s" % (who, log))
            continue
        try:
            data = decompress(log)
        except Exception as exc:                                  # noqa: BLE001
            print("★ %-10s 解压失败：%s" % (who, exc))
            continue
        text = data.decode("utf-8", errors="replace")
        counts = {m: text.count(m) for m in MARKS}
        hits = {k: v for k, v in counts.items() if v}
        print("★ %-10s 日志 %d 字符；命中：%s" % (who, len(text), hits or "**一个标识都没有**"))
        #: ★ 再捞一眼 model 字段（可能落在 `"model":"..."` 里）
        models = set(re.findall(r'"model"\s*:\s*"([^"]{1,40})"', text))
        print("             出现过的 \"model\" 取值：%s" % (sorted(models) or "（无）"))
        #: ★ provider 字段
        provs = set(re.findall(r'"provider"\s*:\s*"([^"]{1,40})"', text))
        print("             出现过的 \"provider\" 取值：%s" % (sorted(provs) or "（无）"))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
