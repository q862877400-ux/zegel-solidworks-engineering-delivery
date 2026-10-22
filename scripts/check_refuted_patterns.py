"""★ C8 · 台账分叉门禁 —— ★ 已证伪清单的锚点必须**逐字**命中 `docs/known-facts.md`。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把 `GATE-FINAL` 的 C8 落地）。
# 文件:   scripts/check_refuted_patterns.py
# 定位:   ★ **C8 的判据逐字**（`specs/202-user-coverage-gaps/recon/gate-cand/GATE-FINA
#           L.md`）：「`docs/refuted-patterns.json` 里每条的 `anchor_quote` **必须逐字出
#           现在 `docs/known-facts.md` 中**。★ 有一个不命中 ⇒ 失败」
#         ★★ **它自称「唯一常驻硬门禁」** —— 而 2026-10-04（接手轮）的 A-3 查出：
#           ★ **它唯一依据的那个 JSON 当时在仓里不存在** ⇒ ★ 那条闸**没有可读对象、永远"通过"**
#           （★ 与**事实 40**「存在但没人用的守卫与没有守卫等价」同族）✓
#         ★★★ 本脚本 = **把那条闸真正接进 `release_check`** ⇒ ★ 从"有对象"到"在跑" ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ROOT / "docs" / "refuted-patterns.json"
FACTS = ROOT / "docs" / "known-facts.md"
REQUIRED_FIELDS = ("id", "claim", "refuted_by", "anchor_quote", "prevention")

#: ★★ 2026-10-04（接手轮）：★ **中文 Windows 上打印 `✓` 会 `UnicodeEncodeError: 'gbk' codec`** ——
#:   ★ 那是**事实 58** 那一族的又一例（★ 父进程用 `locale.getpreferredencoding()` = **GBK**）。
#:   ★★ 修法：★ **把 stdout 切成 utf-8**（★ `errors="replace"` ⇒ 再遇到别的编码也不至于整条崩）✓
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")            # type: ignore[attr-defined]
except Exception:                                                         # noqa: BLE001
    pass


def check() -> tuple[bool, str]:
    """★ 判据：① JSON 存在且可解析 · ② 每条齐必需字段 · ③ `anchor_quote` **逐字**命中事实表。"""
    if not PATTERNS.is_file():
        return False, ("★ `docs/refuted-patterns.json` **不存在** ⇒ 本条闸**没有可读对象**。"
                       "★ 那不是「通过」，★ 是**没在判**（★ 事实 40）。")
    try:
        data = json.loads(PATTERNS.read_text(encoding="utf-8"))
    except Exception as exc:                                              # noqa: BLE001
        return False, "★ `refuted-patterns.json` 解析失败：%s" % exc
    rows = data.get("patterns") or []
    if not rows:
        return False, "★ `patterns` 是空的 ⇒ 闸没有对象可判（★ 同「不存在」）。"
    facts = FACTS.read_text(encoding="utf-8", errors="replace")
    miss_field, miss_quote = [], []
    for r in rows:
        rid = r.get("id") or "<无 id>"
        for f in REQUIRED_FIELDS:
            if not (r.get(f) or "").strip():
                miss_field.append("%s.%s" % (rid, f))
        q = r.get("anchor_quote") or ""
        if q and q not in facts:
            miss_quote.append(rid)
    if miss_field or miss_quote:
        lines = []
        if miss_field:
            lines.append("★ 缺必需字段：%s" % ", ".join(miss_field))
        if miss_quote:
            lines.append("★★ `anchor_quote` **没有逐字命中** `docs/known-facts.md`：%s"
                         % ", ".join(miss_quote))
        return False, "\n".join(lines)
    return True, "★ %d 条 · `anchor_quote` **全部逐字命中** `docs/known-facts.md` ✓" % len(rows)


def main() -> int:
    ok, msg = check()
    print("★ C8 · 台账分叉门禁 —— %s" % ("PASS" if ok else "FAIL"))
    print("  " + msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
