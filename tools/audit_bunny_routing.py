"""★ 机械检查：某批派活**实际**跑的是哪个模型（解压会话日志，不认 list_agents）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（针对 DSH 会话日志）
# 文件:   tools/audit_bunny_routing.py
# 定位:   ★ 目标 ③ 的硬纪律落地：**解压会话日志实证实际模型** ✓
#         ★★ **为什么不能看 `list_agents`**：它对 **inactive** 成员会误报 ——
#           实测：跑的是 bunny 的 vf4/vf5/vf6/dp1 被显示成 `deepseek-flash`，
#           而会话日志里 `deepseek-flash` **命中 0**、只有 `space-bunny-free` ✓✗
#           ⇒ ★ **能定案的是会话日志**，而且它是 `.jsonl.zstd` **压缩**的
#             （纯文本 grep 命中 0，**必须先解压**）✓
#         ★★★ 判据：在某批的会话里，`space-bunny-free` 必须命中、`deepseek-flash` 必须 0 命中 ✓
# 官方依据: 不适用（本机事实核查）
# 许可:   本机数据，无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SESSIONS = Path(r"C:\Users\Zegel\.dsh\sessions\--D-AI-SW--")
MARKS = ("space-bunny-free", "deepseek-flash", "opencode-zen", "gemini-3.8-flash")


def decompress(p: Path) -> bytes:
    """★ 三级降级：stdlib `compression.zstd` → `zstandard` 包 → `zstd` CLI。"""
    try:
        from compression import zstd                              #: Python 3.14 自带
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--marker", default="bunny-records-deep",
                    help="会话日志里必须出现的字符串（用来认出这一批的会话）")
    ap.add_argument("--limit", type=int, default=40, help="最多扫几个（按修改时间倒序）")
    ap.add_argument("--orchestrator", default="",
                    help="编排者会话 id 前缀（★ 它跑会话模型是应然的，予以豁免）")
    a = ap.parse_args()

    logs = sorted(SESSIONS.glob("*/session.v4.jsonl.zstd"),
                  key=lambda p: p.stat().st_mtime, reverse=True)[: a.limit]
    print("★ 扫最近 %d 个会话，找含 %r 的：" % (len(logs), a.marker))

    hit = bad = orch = 0
    #: ★ 先把匹配到的会话收齐，才能定出「谁是编排者」（日志最大者）
    matched: list[Path] = []
    texts: dict[Path, str] = {}
    for log in logs:
        try:
            text = decompress(log).decode("utf-8", errors="replace")
        except Exception as exc:                                  # noqa: BLE001
            print("  %s 解压失败：%s" % (log.parent.name[:12], exc))
            continue
        if a.marker not in text:
            continue
        matched.append(log)
        texts[log] = text

    biggest = max(matched, key=lambda p: p.stat().st_size) if matched else None
    if biggest is not None:
        print("  ★ 假定编排者 = %s（日志最大 %.1f MB）—— 若非如此请用 --orchestrator 指定"
              % (biggest.parent.name[:12], biggest.stat().st_size / 1048576))

    for log in matched:
        text = texts[log]
        counts = {m: text.count(m) for m in MARKS}
        models = sorted(set(re.findall(r'"model"\s*:\s*"([^"]{1,40})"', text)))
        #: ★★ 先判**是不是编排者**再判合规 —— 否则本检查会把 Lead 自己的会话报成违规
        #: （实测：我一个会话因读写 `bunny-records-deep` 路径而被匹配到，deepseek 命中 2
        #: 193）
        #:   ⇒ ★ 编排者**本来就该是会话模型**；只有**工作者**必须全 bunny ✓
        #:   ★ 判据：编排者会话里会出现 `spawn_teammate`，工作者不会 ✓
        #: ★ 编排者（Lead）本来就该跑会话模型 ⇒ **豁免**；只有**工作者**必须全 bunny
        is_orchestrator = biggest is not None and log == biggest
        bunny = counts["space-bunny-free"] > 0
        deep = counts["deepseek-flash"] > 0
        if is_orchestrator:
            orch += 1
            flag = "· 编排者（豁免）"
        elif bunny and not deep:
            hit += 1
            flag = "✓ bunny"
        else:
            bad += 1
            flag = "★ 混用/异常" if deep else "★ 无模型标记"
        print("  %-14s %-16s bunny=%-4d deepseek=%-4d model 取值=%s"
              % (log.parent.name[:12], flag, counts["space-bunny-free"],
                 counts["deepseek-flash"], models))

    print("\n★ 结论：合规 %d 个 · 异常 %d 个" % (hit, bad))
    if bad:
        print("  ★★ 有异常 ⇒ **停下核查这一批的派活方式**，不要继续")
        return 1
    if hit == 0:
        print("  ★ 一个都没匹配到 ⇒ marker 选错了，不是「检查通过」")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
