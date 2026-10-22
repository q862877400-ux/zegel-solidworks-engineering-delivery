"""★ 真机：工程图标注第二枪 —— **先选中视图**再 `InsertDatumTag2()`（★ 穷举"调用前提"）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_drawing_datum_tag2.py
# 定位:   ★ 2026-10-03（轮 411）承 `probe_drawing_datum_tag.py`：★ 那一版
#   **`InsertDatumTag2()` 回了 `None`、`GetDatumTagCount` 0→0** ⇒ ★ 它**也要先选中东西**
#   （★ 与 `AddDimension2` / `FeatureLinearPattern3` **同族前置** —— 见事实 320 / 321）。
#   ★ 本版把"**选中什么**"当成变量（★ 轮 408 新立的纪律：判"未建成"前先穷举"调用前提"）：
#     ① ★ **按名选中视图**（`SelectByID2(视图名, "DRAWINGVIEW", …)`）；
#     ② ★ 若①不成，★ **选中视图里的一个实体**（★ 走 `SelectByID2` 按点）。
#   ⚠ 只打开并加注、**不保存**（★ 硬约束⑦）。
# 官方依据: `IModelDoc2.InsertDatumTag2()`（零参）· `IView.GetDatumTagCount()` ·
#   `IModelDocExtension.SelectByID2`（**9 参**，第 7 个是 `Mark`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ `GetDatumTagCount()` 真的 +1。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "drawing-datum-tag2-evidence.json"
)
FIXTURE = Path(
    r"C:\Users\Public\Documents\SOLIDWORKS\SOLIDWORKS 2026\samples\introsw\box.slddrw"
)


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member

    from scripts.sw_drawing_view import get_first_view

    ev: dict = {"trials": [], "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.open_document(sw, str(FIXTURE), read_only=True)
        view = get_first_view(doc)
        #: ★ 视图名怎么取：`GetName` 不存在 ⇒ 试几个官方候选（★ 不猜，只试名字）
        vname = None
        for attr in ("Name", "GetName2", "GetName"):
            try:
                v = safe_get_com_member(view, attr)
                if v:
                    vname = str(v)
                    ev["view_name_via"] = attr
                    break
            except Exception:  # noqa: BLE001
                continue
        ev["view_name"] = vname
        ext = get_com_member(doc, "Extension")
        empty = sw_connect.create_empty_dispatch_variant()

        def sel(name, kind, mark=0):
            return get_com_member(
                ext,
                "SelectByID2",
                str(name),
                str(kind),
                0.0,
                0.0,
                0.0,
                False,
                int(mark),
                empty,
                0,
            )

        def count():
            return safe_get_com_member(view, "GetDatumTagCount")

        trials = []
        if vname:
            trials.append(("select_view_by_name", lambda: sel(vname, "DRAWINGVIEW", 0)))
        #: ★★★ ★ 2026-10-03（轮 411）**这里原本有一条**
        #: `trials.append(("view_select_method", lambda: bool(get_com_member(view, "Sele
        #: ct"))))`
        #:   —— ★ 而它是我**"试名字"性质**的调用（非官方入口）。
        #:   ★★ 真机后果：引出一个**模态进度窗**
        #:   （`#32770` · 静态文本「打开 零部件」「更新 工程图」「**正在加载零部件：**」）
        #:   ⇒ 护栏按纪律归为 `needs_llm` 并**中止调用**。
        #:   ★★ 教训：**"试名字"式的调用会引出弹窗** —— ★ 而官方入口要**先查**（铁律 5）。
        for label, act in trials:
            cell: dict = {"trial": label}
            try:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                before = count()
                r = act()
                tag = get_com_member(doc, "InsertDatumTag2")
                after = count()
                cell.update(
                    {
                        "act_returned": bool(r),
                        "tag_is_none": tag is None,
                        "count": [before, after],
                        "ok": after == before + 1,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                cell.update(
                    {
                        "ok": False,
                        "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                    }
                )
            ev["trials"].append(cell)
        wins = [c for c in ev["trials"] if c.get("ok")]
        ev["verdict"] = "pass" if wins else "partial"
        ev["note"] = (
            "★ 把「**选中什么**」当变量（★ 轮 408 的纪律）：① 按名选中视图；② 视图对象自选。"
            "★ 判据仍是 `GetDatumTagCount()` 真的 +1。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1400])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
