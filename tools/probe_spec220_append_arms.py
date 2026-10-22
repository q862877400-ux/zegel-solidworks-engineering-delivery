"""★ 探针：只读判别"两选面"的 Append 语义（SelectByID2 臂 与 Select4 臂）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/probe_spec220_append_arms.py
# 定位:   ★ 规格 220 T-220-01 第 9 轮 —— ★ 上一轮读数卡在"第二次选面不累加"（第 1 次=1
#            第 2 次=1）
#         ⇒ ★ 本探针**一次测两条路**，★ 每步只变一个量并打印回读计数 ✓
# 官方依据: ★ 事实 32（本仓）：实体没有可用名字 ⇒ ① 按面上的点 `SelectByID2` ·★ ② 或按对
#           象 `IEntity.Select4(Append, Callout)` ✓（后者**有** Append 形参 ✓）
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

import sw_connect  # noqa: E402
import tool_caller  # noqa: E402

RECT = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 100.0, "y2_mm": 60.0}


def _centres(model):
    import sw_part as _sp
    import sw_selection_spec as _ss

    faces = list(_ss.entities_on_body(model, "FACE", body_index=0) or [])
    out = []
    for i, f in enumerate(faces):
        b = list(_sp.get_com_member(f, "GetBox") or [])
        if len(b) >= 6:
            out.append(
                {
                    "i": i,
                    "face": f,
                    "c": (
                        (b[0] + b[3]) / 2.0,
                        (b[1] + b[4]) / 2.0,
                        (b[2] + b[5]) / 2.0,
                    ),
                }
            )
    return out


def main() -> int:
    import sw_part as _sp

    out = {}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    inj = {"model": model, "sw": sw}
    for step, params in (
        ("solidworks_sketch_start", {}),
        ("solidworks_sketch_add_rectangle", RECT),
        ("solidworks_extrude_boss", {"sketch_name": "Sketch1", "depth_mm": 20.0}),
    ):
        ok, note = tool_caller.call(step, inject_objects=inj, **params)
        if not ok:
            print("★ 建板没成：%s" % step)
            return 1

    f = _centres(model)
    a, b_ = f[0], f[1]
    print("★ 面心：a(0)=%r · b_(1)=%r" % (a["c"], b_["c"]))
    ext = model.Extension
    sm = model.SelectionManager
    res = {}

    def cnt():
        return int(sm.GetSelectedObjectCount2(-1))

    #: ── a 臂：SelectByID2 的两步（先 False 再 True）───────────────────────
    model.ClearSelection2(True)
    ext.SelectByID2(
        "", "FACE", a["c"][0], a["c"][1], a["c"][2], False, 0, _sp._empty_callout(), 0
    )
    res["A1_select_A_AppendFalse"] = cnt()
    ext.SelectByID2(
        "", "FACE", b_["c"][0], b_["c"][1], b_["c"][2], True, 0, _sp._empty_callout(), 0
    )
    res["A2_then_B_AppendTrue"] = cnt()

    #: ── a' 臂：两步都用 Append=True ───────────────────────────────────────
    model.ClearSelection2(True)
    ext.SelectByID2(
        "", "FACE", a["c"][0], a["c"][1], a["c"][2], True, 0, _sp._empty_callout(), 0
    )
    res["A3_A_AppendTrue"] = cnt()
    ext.SelectByID2(
        "", "FACE", b_["c"][0], b_["c"][1], b_["c"][2], True, 0, _sp._empty_callout(), 0
    )
    res["A4_B_AppendTrue"] = cnt()

    #: ── b_ 臂：走实体对象 IEntity.Select4(Append, Callout) ────────────────
    try:
        model.ClearSelection2(True)
        r1 = a["face"].Select4(False, _sp._empty_callout())
        res["B1_Select4_A_AppendFalse"] = [bool(r1), cnt()]
        r2 = b_["face"].Select4(True, _sp._empty_callout())
        res["B2_Select4_B_AppendTrue"] = [bool(r2), cnt()]
    except Exception as exc:  # noqa: BLE001
        res["B_arm_error"] = str(exc)[:160]

    for k, v in res.items():
        print("★ %-32s %r" % (k, v))
    out["steps"] = res
    out["centres"] = [a["c"], b_["c"]]
    p = ROOT / "output" / "spec220-append-arms.json"
    p.write_text(
        json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("★ 证据：%s" % p)
    try:
        sw.CloseAllDocuments(True)
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
