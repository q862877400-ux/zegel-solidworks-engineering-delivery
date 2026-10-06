"""★ 真机：规格 209 · B2-4（idx 175 blank_sketch）—— ★ 判据 = `IFeature::Visible` 的前后读数。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_b2_blank_sketch.py
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-4**：外部项目 idx **175 `hide_all_sketches`**。
#   ★★ 裁决书点名的**真风险**：「怎么回读「隐藏了没有」」—— 官方 `BlankSketch` 回 `void`、
#     且那页**既无 Returns 也无 Remarks**；★ 官方示例的判据是**肉眼**
#     （「Examine the graphics area」）⇒ ★ 本探针就是去**定出那个回读入口** ✓
#   ★★ 判据（规则 6，全回读）：
#     ```
#     ① 选区计数           ★ 事实 8：不许信返回值
#     ② IFeature::Visible  ★ swVisibilityState_e 的**前后读数**（Hide=1 · Shown=2 · Unknown=3）
#     ③ 正反向              ★ blank=True 要变 hide · blank=False 要变 shown（★ 两个方向都验）
#     ④ 负例                ★ 名字不存在 ⇒ 选区计数 0 ⇒ **必须大声报**（不静默当成功）
#     ```
# 官方依据: `C:\\swapi\\types\\IModelDoc2\\{BlankSketch,UnblankSketch}.md` ·
#   `C:\\swapi\\types\\IFeature\\Visible.md` · `C:\\swapi\\enums\\swVisibilityState_e.md` ·
#   `C:\\swapi\\examples\\Hide_and_Show_Sketches_Example_VB.md`（★ 调用序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "spec209-blank-sketch.json"


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import sw_part as P
    import sw_sketch as SK

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "规格 209 · B2-4 blank_sketch（★ 判据 = IFeature::Visible 的前后读数）",
          "judge": "选区计数 + swVisibilityState_e 前后读数（两个方向都验）", "steps": {},
          "negative": {}}
    opened = []

    def _close(doc):
        try:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass

    try:
        doc = sw_connect.new_document(sw, "part")
        opened.append(doc)
        #: ★ 造两张草图（★ 官方前置："Create multiple sketches"）
        for name, (x0, y0, x1, y1) in (("A", (-20.0, -10.0, 20.0, 10.0)),
                                       ("B", (-5.0, -5.0, 5.0, 5.0))):
            with P.sketch(doc, "Front Plane") as sk:
                P.sketch_corner_rectangle(doc, x0, y0, x1, y1)
        names = [str(safe_get_com_member(f, "Name") or "") for f in SK._selected_feature_objects(doc)]
        ev["tree_names"] = [str(safe_get_com_member(f, "Name") or "")
                            for f in _iter(doc)]
        sketches = [n for n in ev["tree_names"] if n.startswith(("Sketch", "草图"))]
        ev["sketch_names"] = sketches
        ev["sanity_selected_before"] = names
        first = sketches[0] if sketches else ""
        ev["using_sketch"] = first
        print("  特征树里的草图：%r" % (sketches,))

        #: ① 隐藏
        r1 = SK.set_sketch_blanked(doc, first, blank=True)
        ev["steps"]["blank"] = {k: r1.get(k) for k in
                                ("ok", "entry_used", "selection_count", "before", "after",
                                 "changed", "error")}
        print("  blank  ok=%s before=%s after=%s" % (
            r1.get("ok"), [(b.get("state"), b.get("raw")) for b in (r1.get("before") or [])],
            [(a.get("state"), a.get("raw")) for a in (r1.get("after") or [])]))

        #: ② 显示（★ 反方向）
        r2 = SK.set_sketch_blanked(doc, first, blank=False)
        ev["steps"]["unblank"] = {k: r2.get(k) for k in
                                  ("ok", "entry_used", "selection_count", "before", "after",
                                   "changed", "error")}
        print("  unblank ok=%s before=%s after=%s" % (
            r2.get("ok"), [(b.get("state"), b.get("raw")) for b in (r2.get("before") or [])],
            [(a.get("state"), a.get("raw")) for a in (r2.get("after") or [])]))

        #: ③ 负例：名字不存在 ⇒ 选区计数 0 ⇒ 大声报
        r3 = SK.set_sketch_blanked(doc, "不存在的草图名", blank=True)
        ev["negative"]["missing_name"] = {"ok": r3.get("ok"),
                                          "selection_count": r3.get("selection_count"),
                                          "error": r3.get("error")}
        print("  负例 missing_name ok=%s count=%s" % (r3.get("ok"), r3.get("selection_count")))

        #: ④ 判定（★ 两个方向都要真的变）
        ch1 = (r1.get("changed") or [])
        ch2 = (r2.get("changed") or [])
        ev["verdict"] = {
            "blank_moved_to_hide": any(c["state"][1] == "hide" for c in ch1),
            "unblank_moved_to_shown": any(c["state"][1] == "shown" for c in ch2),
            "negative_loud": (r3.get("ok") is False and r3.get("selection_count") == 0
                              and bool(r3.get("error"))),
        }
        ev["verdict"]["all_ok"] = all(ev["verdict"].values())
        print("  verdict =", json.dumps(ev["verdict"], ensure_ascii=False))
        _close(doc)
    except Exception as exc:                                   # noqa: BLE001
        ev["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        print("  FATAL %s" % str(exc)[:140])

    for d in opened:
        _close(d)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
                   encoding="utf-8")
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:                                          # noqa: BLE001
        pass
    return 0


def _iter(doc):
    """★ 顺序遍历特征树（★ 与 `sw_sheet_metal.iter_features` 同一写法）。"""
    from sw_connect import get_com_member
    f = get_com_member(doc, "FirstFeature")
    n = 0
    while f is not None and n < 4096:
        yield f
        f = get_com_member(f, "GetNextFeature")
        n += 1


if __name__ == "__main__":
    raise SystemExit(main())
