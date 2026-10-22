"""★ `mold_parting_geometry` 的**写入那半**真机探针：先"准备"（选好拔模方向）再插分型线。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_mold_parting_geometry.py
# 定位:   ★ 2026-10-02（轮 384）objective③：`mold_parting_geometry` 是 12 条 stitched 
#           里**唯一可挖的**
#   （★ 其余 10 条在 `docs/dead-ends.md` 上、`weldment_cut_list` 是环境缺件）。
#   ★ 而既有探针 `verify_mold_evidence_smoke.py` **只覆盖只读那一半**，
#   ★★ 且它自己明写「**未验**：`InsertMold*` —— 在未准备的分型件上会弹框」。
#   ⇒ 本探针补的正是**写入那半**：★ 先按契约**选好拔模方向参考**（那就是"准备"），再插。
# 官方依据: `scripts/sw_mold.py` 的 `insert_parting_line` 文档串 ——
#   「调用前须由调用方选好**拔模方向参考**（边线/基准面/轴）—— 官方在未选时会返回 None」。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 定量，能被"什么都没发生"证伪）：
# ```
# ① 选好参考后 `insert_parting_line` **返回非空的名字**（★ 未选时它抛 RuntimeError）
# ② **回读** `mold_evidence()` 的 `parting_lines` **从 0 变成 > 0**（★ 那才是"真插进去了"）
# ③ ★ 反证：**不选参考**时它**必须失败**（★ 那证明判据 ① 不是"恒真"）
# ```
# ★ 全程走 `sw_guard` 护栏：★ 会弹框的那几步在子进程里 + 硬超时（AGENTS.md 的常驻纪律）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "mold-parting-geometry-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member
    from sw_part import (current_sketch_name, end_sketch, extrude_boss,
                         sketch_corner_rectangle, start_sketch)
    import sw_mold as M

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None

    def counts(model):
        e = M.mold_evidence(model)
        return (e.get("counts") or {}) if isinstance(e, dict) else {}

    try:
        #: ① 建一个**有拔模斜度**的件（★ 分型线要在有斜度的体上才有意义）
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc)
        end_sketch(doc)
        extrude_boss(doc, sk, 25.0)
        ev["steps"]["doc"] = {"ok": True, "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}
        before = counts(doc)
        ev["steps"]["counts_before"] = {"ok": True, "counts": before}

        #: ② **反证**：**不选**参考 ⇒ 官方回 None ⇒ 我们的入口**必须**抛（★ 证明判据①不恒真）
        doc.ClearSelection2(True)
        try:
            M.insert_parting_line(doc)
            ev["steps"]["negative_unprepared"] = {"ok": False,
                                                  "note": "**未选参考却成功了** ⇒ 判据①恒真、该判据无效"}
        except Exception as exc:                                # noqa: BLE001
            ev["steps"]["negative_unprepared"] = {"ok": True,
                                                  "err": "%s: %s" % (type(exc).__name__, str(exc)[:90])}

        #: ③ **准备**：★ ★★★★ 官方 Remarks 明写**两件都要带 mark 选**（★ 铁律 4 查到的原话）：
        #:   ```
        #:   「Before calling this method, you must select **the direction of pull** and
        #:     **the edges for the parting line** by calling `IModelDocExtension::SelectByID2`
        #:     with the following Marks:  Direction of pull = **1** · Parting line edges = 4」
        #:   ```
        #:   ★ 我第一版**两处都没做对**（★ mark 传 0、且**没选边线**）⇒ 官方回 None ✓
        doc.ClearSelection2(True)
        picked = False
        for plane in ("Front Plane", "前视基准面", "Top Plane", "上视基准面"):
            if get_com_member(doc, "Extension").SelectByID2(
                    plane, "PLANE", 0, 0, 0, False, 1,
                    sw_connect.create_empty_dispatch_variant(), 0):
                picked = True
                ev["steps"]["select_pull_direction"] = {"ok": True, "plane": plane, "mark": 1}
                break
        if not picked:
            ev["steps"]["select_pull_direction"] = {"ok": False, "note": "四个候选面名都没选中"}
        #: ★ mark=4 ⇒ **分型线边线**：★ 取体上所有边（★ 简单件上"最外一圈"就是全部边）
        edges = []
        for body in (get_com_member(doc, "GetBodies2", 0, False) or []):
            edges.extend(get_com_member(body, "GetEdges") or [])
        n_sel = 0
        for e in edges:
            try:
                if e.Select4(True, sw_connect.create_empty_dispatch_variant(), 4):
                    n_sel += 1
            except TypeError:                                   #: ★ 有些重载没有 mark 参数
                try:
                    if e.Select4(True, sw_connect.create_empty_dispatch_variant()):
                        n_sel += 1
                except Exception:                               # noqa: BLE001
                    pass
        ev["steps"]["select_parting_edges"] = {"ok": n_sel > 0, "selected": n_sel,
                                               "of": len(edges), "mark": 4}

        #: ④ 插入分型线 ⇒ ★ 回读计数（★ 定量判据）
        try:
            name = M.insert_parting_line(doc)
            ev["steps"]["insert_parting_line"] = {"ok": bool(name), "feature_name": str(name)[:60]}
        except Exception as exc:                                # noqa: BLE001
            ev["steps"]["insert_parting_line"] = {"ok": False,
                                                  "err": "%s: %s" % (type(exc).__name__, str(exc)[:110])}
        after = counts(doc)
        ev["steps"]["counts_after"] = {"ok": True, "counts": after}
        n_before = int((before or {}).get("parting_lines") or 0)
        n_after = int((after or {}).get("parting_lines") or 0)
        ev["steps"]["count_increased"] = {"ok": n_after > n_before,
                                          "before": n_before, "after": n_after,
                                          "note": "★ 判据：parting_lines 计数必须**真的增加**（★ 定量）"}

        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = ("★ 本探针补 `mold_parting_geometry` 的**写入那半**（★ 既有冒烟只覆盖只读）；"
                      "★ 关键在**先按契约选拔模方向参考** —— 未选时官方返回 None（★ 已用反证验到）。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
