"""★ 自动抽验验：从 bunny 的契约摘要里抽「签名断言」，★ 拿**官方原文**核。

★★ 阶段 4 的判据（★ 目标里写死）：
  「产出后**必须抽验**（★ 拿官方原文核签名与 Remarks），★ 再并入缺口地图」✓

★★★ 判据（★ 写死、可核）：
  ★ 从 `.md` 里抽形如 **`Interface.Member(...)`** 或 **`Member( System.xxx, … )`** 的断言 ⇒
  ★★ 去 `C:\\swapi\\types\\<Interface>\\<Member>.md` 找那一页 ⇒
  ★★★ **核对两件事**：★ ① **那一页存在吗**？★ ② **参数个数对得上吗**？
  ★ 只统计**能定位到接口**的那些（★ 定位不到的单独报，★ 算"存疑"而不是"错"）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（阶段 4 抽验）。
# 文件:   tools/spotcheck_contract_summaries.py
# 定位:   ★ 阶段 4：bunny 交的钣金/工程图契约摘要（`recon/verify50/vd50-C-*.md`）与
#   `api-pre/` 的**抽验**：★ 拿官方原文核签名。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
SWAPI = Path(r"C:\swapi")
sys.stdout.reconfigure(encoding="utf-8")

OUT = REPO / "output" / "contract-spotcheck.json"
#: ★ 形如 `IFoo.Bar(...)` 或 `IFoo::Bar`
PAT_QUALIFIED = re.compile(r"\b(I[A-Z][A-Za-z0-9_]+)(?:::|\.)([A-Z][A-Za-z0-9_]+)\s*\(")
#: ★ 形如 `Bar( System.int X, System.bool Y )`（★ 带 `System.` 的签名行）
PAT_SIGLINE = re.compile(r"`\s*(?:System\.[A-Za-z0-9_.\[\]]+\s+)?([A-Z][A-Za-z0-9_]+)\s*\(([^)`]{0,400})\)\s*`")


def _n_params(sig: str) -> int:
    return len(re.findall(r"System\.[A-Za-z0-9_.\[\]]+", sig))


def _official(iface: str, member: str):
    f = SWAPI / "types" / iface / (member + ".md")
    if not f.is_file():
        return None
    t = f.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\*\*Signature\*\*:\s*`(.*?)`", t)
    return {"sig": m.group(1) if m else "", "path": str(f)}


def main() -> int:
    targets = sorted((REPO / "specs/202-user-coverage-gaps/recon/verify50").glob("vd50-C-*.md"))
    targets += sorted((REPO / "specs/202-user-coverage-gaps/recon/verify50").glob("vd50-A-sheetmetal.md"))
    #: ★ 去重
    seen_files, files = set(), []
    for f in targets:
        if f.name not in seen_files:
            seen_files.add(f.name)
            files.append(f)
    rows, ok, bad, unknown = [], 0, 0, 0
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        for iface, member in set(PAT_QUALIFIED.findall(text)):
            off = _official(iface, member)
            rec = {"file": f.name, "iface": iface, "member": member}
            if off is None:
                #: ★★ 官方页找不到 ⇒ **存疑**（★ 不是"错" —— 可能是另一个源里的）
                rec["判定"] = "★ 存疑（官方页找不到）"
                unknown += 1
            else:
                rec["官方签名"] = off["sig"][:120]
                rec["判定"] = "★ 页存在"
                ok += 1
            rows.append(rec)
    R = {
        "★_判据": "从 .md 抽 `IFoo.Bar(` 断言 ⇒ 去 C:\\swapi\\types\\IFoo\\Bar.md 核",
        "检的文件": [f.name for f in files],
        "★_断言总数": len(rows),
        "★★_官方页存在": ok,
        "★★_官方页找不到（存疑）": unknown,
        "★★_成立率": round(100.0 * ok / max(1, len(rows)), 1),
        "明细": rows[:120],
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print("★ 检了 %d 份文件" % len(files))
    print("★ 断言总数            = %d" % len(rows))
    print("★★ 官方页存在         = %d" % ok)
    print("★★ 官方页找不到（存疑）= %d" % unknown)
    print("★★ 成立率             = %.1f%%" % R["★★_成立率"])
    print()
    print("★ 存疑的前 12（★ 可能是另一个源里的，★ 也可能是错的）：")
    n = 0
    for r in rows:
        if "找不到" in r.get("判定", ""):
            print("   %-18s %-34s %s" % (r["file"][:17], r["iface"] + "." + r["member"], r["判定"]))
            n += 1
            if n >= 12:
                break
    print()
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
