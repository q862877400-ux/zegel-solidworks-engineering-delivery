"""★ 只读探针：列出会话里打开的文档，★ **不关、不改、不建任何东西**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B6 的**处置前置**）
# 文件:   tools/probe_list_open_docs.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 B6。★★ **它存在的理由是一个死结**：
# · ★ `sw_guard` 的预检在**探针运行之前**拒绝开始（★ 因为会话里有"非我方 + 未保存"的文档
#  ✓）
#   · ★★ 而**清理那个文档要连 COM** ⇒ ★ **要先过预检** ✗ ⇒ **死结** ✓
#   · ★★★ 出路：★ **用 `--skip-precheck` 跑**这一个**只读**动作** ✓ ——
#     ★ "信任这次运行"用在**只读**上是可接受的 ✓、★ **而不是**用它去关文档 ✗
#   ⇒ ★ 本探针**只读**：★ 列 `ISldWorks::GetDocuments()` 的每一项 + 它的
#     `GetPathName` / `GetTitle` / `Visible` / `GetSaveFlag` ✓
#     ★★ **一个 `CloseDoc` 都没有** ✓（★ 可 grep 自证 ✓）
# 官方依据（★ 三样）：
#   · `C:\swapi\types\ISldWorks\GetDocuments.md`：`System.object GetDocuments()`
#     ★ `## Returns`：Array of open documents in this SOLIDWORKS Design session ✓
#   · ★★ `C:\swapi\types\ISldWorks\EnumDocuments2.md` 的 `## Remarks` 逐字：
# 「… contain any open `IModelDoc2` pointer. ★ **This includes `IModelDoc2` objects that
#  may have
# been opened as file references**, for example, from an assembly or drawing. ★ You migh
# t want to
# use the `IModelDoc::Visible` property to determine if a particular document **has its 
# own window**
#      and is visible to the user.」✓✓
#   ⇒ ★★★ **所以"引用文档"会出现在列表里、★ 而没有自己的窗口** ✓
#     —— ★ 那正是"未保存"那一条的可能身份 ✓
# 判据:   ★★ 每条落 `path` / `title` / `visible` / `saved` 四个字段（★ 全是**回读** ✓）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def main() -> int:
    import sw_connect

    out: dict = {"kind": "READ-ONLY", "closes_anything": False,
                 "official": ["ISldWorks.GetDocuments", "ISldWorks.EnumDocuments2"]}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    try:
        docs = sw_connect.get_com_member(sw, "GetDocuments") or []
    except Exception as e:                                              # noqa: BLE001
        print("★ GetDocuments 失败：%s" % str(e)[:120])
        return 3

    rows = []
    ours = str(ROOT / "output").lower()
    for d in docs:
        if d is None:
            continue
        row = {}
        for label, member in (("path", "GetPathName"), ("title", "GetTitle")):
            try:
                row[label] = str(sw_connect.get_com_member(d, member) or "")
            except Exception:                                           # noqa: BLE001
                row[label] = None
        #: ★★ 官方 Remarks 给的判据：★ **有没有自己的窗口** ✓
        try:
            row["visible"] = bool(sw_connect.get_com_member(d, "Visible"))
        except Exception:                                               # noqa: BLE001
            row["visible"] = None
        #: ★ 已保存？
        try:
            row["saved"] = bool(sw_connect.get_com_member(d, "GetSaveFlag"))
        except Exception:                                               # noqa: BLE001
            try:
                row["saved"] = bool(sw_connect.get_com_member(d, "SaveFlag"))
            except Exception:                                           # noqa: BLE001
                row["saved"] = None
        row["is_ours_by_path"] = bool(row.get("path") and ours in str(row["path"]).lower())
        rows.append(row)
        print("★ path=%r · title=%r · visible=%r · saved=%r · ★ 路径属我方=%r"
              % (row.get("path"), row.get("title"), row.get("visible"), row.get("saved"),
                 row["is_ours_by_path"]))

    out["docs"] = rows
    out["count"] = len(rows)
    out["invisible"] = [r for r in rows if r.get("visible") is False]
    out["unsaved"] = [r for r in rows if r.get("saved") is False]
    out["ours"] = [r for r in rows if r["is_ours_by_path"]]
    print("★★ 合计 %d 个 · ★ 无窗口（引用文档）%d 个 · ★ 未保存 %d 个 · ★ 路径属我方 %d 个"
          % (len(rows), len(out["invisible"]), len(out["unsaved"]), len(out["ours"])))
    for r in out["unsaved"]:
        print("★★★ 未保存那一条 ⇒ path=%r · title=%r · visible=%r · 属我方=%r"
              % (r.get("path"), r.get("title"), r.get("visible"), r["is_ours_by_path"]))

    p = ROOT / "output" / "spec211-b6-open-docs.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
