"""★ 官方页「废弃」判定的**精确判据**（★ 只报不动 · ★ 阶段 3 · 判据修正）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `tools/check_obsolete_heuristic.py`
# 定位:   ★ **为什么要它**：★ 我在 `output/_read_*_members.py` 里用的判据是
#     `"Obsolete" in t` ⇒ ★★ **而在 `IFeature/GetTypeName2.md` 那页它是**假阳性**** ——
#     ★★★ 那一页里 `Obsolete` 出现 4 次、**全是那张"类型 → 接口"表的**单元格内容****
#     （★ 「Shape | Obsolete」·「BlockFolder | Obsolete」·「BlockDef | Obsolete」·
#      「ViewBodyFeature | Obsolete」）⇒ ★★★★ **那是表格数据、★ 不是"本成员废弃"** ✓
#   ★★★★★ **精确判据（★ 本工具写死、★ 只报）**：
#     ★ 真正的废弃声明**成句**、★ 且出现在 **front-matter 之后、`**Signature**` 之前**：
#       · ★ `Obsolete. …`（★ 或 `Obsolete. Superseded by …`）
#       · ★ `Not supported in SOLIDWORKS …` ✓
#     ★★ 而表格里的 `Obsolete` 是**单元格内容**（★ 用"在 Signature 之前 + 成句"两条一起滤）✓
#   ★★★★★★ **影响面复核**（★ 本会话实测 · `output/_reaudit_obsolete_heuristic.py`）：
#     ★ 对**前几轮读过的 16 个成员**逐条比两种判据 ⇒ ★★ **只有 `GetTypeName2` 被判错**、
#       ★★★ **而它恰好是**本轮才读的**** ⇒ ★ **前几轮的结论**没受影响**** ✓
#     ★★ **而全库扫的读数**（★ 本工具跑出来的）：★ 扫 **12123 页** ⇒
#       ★★★ **两种判据不一致的有 **33 页****，★ 而**两类都有**：
#         · ★ **假阳性**：★ `IFeature.GetTypeName{,2}` · ★ `IModelView.*StereoSeparation` ·
#           ★★ **`INote.*` 一大批** · ★ `ICurve.GetBCurveParams5` ⇒ ★ 表格内容 ✓
#         · ★★ **假阴性**（★ **更危险**）：★ **`IModelDocExtension.DeleteRenderMaterial`** ·
#           ★ `AddRenderMaterial` · ★ `AddDefaultRenderMaterial` ⇒
#           ★★★ **它们写的是「Not supported in SOLIDWORKS 2011 and later」** ✓
#     ⇒ ★★★★ **而 `DeleteRenderMaterial` 正是本会话 T1 处理过的那条** ——
#       ★ 我当时的读数「官方页**没有** `Obsolete` 行、★ 而名单 `obsolete=True`、★ 措辞是
#         `Not supported in SOLIDWORKS 2011 and later`」⇒ ★★ **完全正确**（★ 新判据也认它）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import re
import sys
from pathlib import Path

SWAPI = Path(r"C:\swapi\types")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def obsolete_naive(text: str) -> bool:
    """★ 我前几轮用的判据 —— ★★ **有假阳性**（★ 表格单元格里也会出现这个词）✓"""
    return "Obsolete" in text


def obsolete_precise(text: str) -> bool:
    """★ 修正后的判据：★ 只认 **front-matter 之后、`**Signature**` 之前**、且**成句**的声明 ✓"""
    head = text.split("**Signature**")[0]
    parts = head.split("---")
    body = "---".join(parts[2:]) if len(parts) >= 3 else head
    return bool(re.search(r"(?m)^\s*(Obsolete\.|Not supported in SOLIDWORKS)", body))


def main() -> int:
    if not SWAPI.is_dir():
        print("★ 官方源不在本机 ⇒ 无可复核")
        return 0
    diff = []
    total = 0
    for p in SWAPI.rglob("*.md"):
        if p.parent.name in ("examples", "enums", "docs"):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        total += 1
        a, b = obsolete_naive(t), obsolete_precise(t)
        if a != b:
            diff.append((str(p.relative_to(SWAPI)), a, b))
    print("★ 扫了 %d 页 ⇒ ★ **两种判据不一致的有 %d 页**" % (total, len(diff)))
    for rel, a, b in diff[:20]:
        print("   %-58s 原=%-6s 修正后=%-6s" % (rel[-56:], a, b))
    if len(diff) > 20:
        print("   …（★ 共 %d 页）" % len(diff))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
