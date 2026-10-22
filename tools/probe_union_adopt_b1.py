"""★ 真机：规格 209 · B1 批的 4 件活逐个试（★ 判据按能力分：回读状态 / 回读属性 / 回读清单）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_union_adopt_b1.py
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B1 批**真机探针（候选来自规格 207 的
# `docs/recon-207/adjudication.md`）。★★ **本探针是那 4 件活拿到 `verified` 的唯一依据**
#  ——
# 裁决书 §四 逐字写着「**一条真机都没验** —— ★ 全程离线静态（D-3：几十个 bunny 并发抢单
# 实例
#   COM 会死锁）。所有『后端可达』都是**静态推断**，必须在真机复验后才能标 `verified`」✓
# 官方依据: 见各能力函数的来源块（`scripts/sw_session.py` / `sw_sketch_edit_ops.py` /
#   `sw_render_material.py` / `sw_document_data.py` 的本批追加段）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
#
# ★★ **判据按能力分（★ 一个判据套不住四件事 —— 这是本探针的关键）**：
#   ```
#   T1 重建      ★ 回读 `NeedsRebuild2` + 特征树计数 + 包围盒（**不是返回值**）
#                + ★ 顺手取证「EditRebuild3 当属性读会拿到 bound method」那个陷阱
#   T2 构造几何  ★ 回读 `ISketchSegment.ConstructionGeometry`（逐段）
#                + ★★ **回答裁决书要求先定的那个问题**：连调两次是**切换**还是**置位**
#   T3 显示状态  ★ 两个官方入口（`GetDisplayStates` vs `GetDisplayStatesCount`）读数一致
#                + 激活后回读「第一个名字」；★ 装配上须给 `ambiguous`
#   T4 引用文档  ★ 官方 `## Returns` 的**步长**能整除 + 名字/路径成对
#   ```
# ⚠ ★ **不判"能/不能"之外的废话**：每格都落 `output/union-adopt-b1-evidence.json`。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "union-adopt-b1-evidence.json"


def main() -> int:
    import sw_connect
    import sw_document_data as DD
    import sw_part as P
    import sw_render_material as RM
    import sw_session as S
    import sw_sketch as SK
    import sw_sketch_edit_ops as E
    from sw_connect import get_com_member, get_com_member_raw, safe_get_com_member  # noqa: F401

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "规格 209 · B1 批（idx 235+236 / 79 / 97 / 244）真机",
        "judge": "回读状态 / 回读属性 / 回读清单（★ 按能力分）",
        "T1_rebuild": [],
        "T1_trap": None,
        "T2_construction": [],
        "T2_toggle_probe": None,
        "T3_display_states": {},
        "T4_dependencies": {},
        "T5_move_body": {},
        "T5b_rotation_units": {},
    }
    opened = []

    def _close(doc):
        try:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass

    def _make_box(tag=""):
        d = sw_connect.new_document(sw, "part")
        opened.append(d)
        P.start_sketch(d, plane_name="Front Plane")
        P.sketch_corner_rectangle(d, -30.0, -20.0, 30.0, 20.0)
        sk = P.current_sketch_name(d, "")
        P.end_sketch(d)
        P.extrude_boss(d, sk, 20.0)
        return d

    #: ── T1 · 重建（idx 235 + 236，三档 mode 一条工具）────────────────────────────────
    try:
        doc = _make_box()
        for mode in ("edit", "force", "all"):
            r = S.rebuild_report(doc, mode)
            ev["T1_rebuild"].append(
                {
                    "mode": mode,
                    "ok": r.get("ok"),
                    "returned": str(r.get("returned")),
                    "needs_before": r.get("needs_rebuild_before"),
                    "needs_after": r.get("needs_rebuild_after"),
                    "state_before": r.get("state_before"),
                    "state_after": r.get("state_after"),
                    "tree": [r.get("tree_before"), r.get("tree_after")],
                    "bbox_changed": r.get("bbox_changed"),
                    "bbox_comparable": r.get("bbox_comparable"),
                    "bbox_before": r.get("bbox_before"),
                    "bbox_after": r.get("bbox_after"),
                    "entry_used": r.get("entry_used"),
                    "error": r.get("error"),
                }
            )
            print(
                "  T1 %-6s ok=%-5s needs %s→%s tree %s→%s bbox_changed=%s"
                % (
                    mode,
                    r.get("ok"),
                    r.get("needs_rebuild_before"),
                    r.get("needs_rebuild_after"),
                    r.get("tree_before"),
                    r.get("tree_after"),
                    r.get("bbox_changed"),
                )
            )
        #: ★ 负例：非法 mode 必须在**入口**被拒（不碰 COM）
        bad = S.rebuild_report(doc, "nonsense")
        ev["T1_rebuild"].append(
            {
                "mode": "nonsense",
                "ok": bad.get("ok"),
                "error": bad.get("error"),
                "judge": "负例：非法 mode 应被拒",
            }
        )
        #: ★★ 陷阱取证：**不调**直接取成员 ⇒ ★ 见下面的实测读数（★ 我原先按裁决书写的是
        #:   「拿到 bound method」—— ★★ **实测不是那个形态** ⇒ 按读数如实记，改口径）
        raw = get_com_member_raw(doc, "EditRebuild3")
        ev["T1_trap"] = {
            "type": type(raw).__name__,
            "callable": callable(raw),
            "truthy": bool(raw),
            "★ verdict": (
                "pywin32 迟到绑定下 `getattr` **本身就会把它调掉** ⇒ "
                "读到的**已经是返回值**（`bool`）、**恒为真** ⇒ 拿它当判据会**永远为真**"
                if not callable(raw)
                else "取到的是 bound method（恒真）"
            ),
            "★": "三家外部项目都这样读它（`_get(doc,'EditRebuild3')`）⇒ ★★ 本仓实测："
            "pywin32 下「读」**就等于「调」**，读到的是 `bool`（恒真）⇒ "
            "拿它当判据会**永远为真**；正解是**真的调用**它（本仓 `rebuild_report` 就是调的）",
        }
        _close(doc)
    except Exception as exc:  # noqa: BLE001
        ev["T1_rebuild"].append(
            {"fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
        )
        print("  T1 FATAL %s" % str(exc)[:120])

    #: ── T2 · 构造几何（idx 79）★ 并回答「连调两次是切换还是置位」─────────────────────
    #: ───
    def _flags(d):
        sk = get_com_member(get_com_member(d, "SketchManager"), "ActiveSketch")
        out = []
        for s in SK.get_sketch_segments(sk) or []:
            try:
                out.append(bool(get_com_member(s, "ConstructionGeometry")))
            except Exception:  # noqa: BLE001
                out.append(None)
        return out

    try:
        doc = sw_connect.new_document(sw, "part")
        opened.append(doc)
        P.start_sketch(doc, plane_name="Front Plane")
        P.sketch_line(doc, -20.0, 0.0, 0.0, 0.0)
        P.sketch_line(doc, 0.0, 0.0, 0.0, 20.0)
        ev["T2_construction"].append({"step": "before", "flags": _flags(doc)})
        r1 = E.sketch_set_construction_geometry(doc, "index:0", construction=True)
        ev["T2_construction"].append(
            {
                "step": "set index:0 → True",
                "ok": r1.get("ok"),
                "target_before": r1.get("target_before"),
                "target_after": r1.get("target_after"),
                "entry_used": r1.get("entry_used"),
                "error": r1.get("error"),
                "flags": _flags(doc),
            }
        )
        #: ★★ 裁决书要求先定的那一件事：**同一段上再调一次官方零参入口** ⇒ 切换 还是 置
        #: 位？
        before2 = _flags(doc)
        get_com_member(
            get_com_member(doc, "SketchManager"), "CreateConstructionGeometry"
        )
        after2 = _flags(doc)
        ev["T2_toggle_probe"] = {
            "before": before2,
            "after": after2,
            "★ verdict": ("置位（幂等）" if before2 == after2 else "★ 切换（toggle）"),
            "_": "官方摘要逐字是「**Sets** … **instead of**」⇒ 预期置位；本格是**实测**，不是推断",
        }
        #: 复位方向：官方唯一的回程 = 属性 setter
        r3 = E.sketch_set_construction_geometry(doc, "index:0", construction=False)
        ev["T2_construction"].append(
            {
                "step": "set index:0 → False",
                "ok": r3.get("ok"),
                "target_before": r3.get("target_before"),
                "target_after": r3.get("target_after"),
                "entry_used": r3.get("entry_used"),
                "error": r3.get("error"),
                "flags": _flags(doc),
            }
        )
        #: 负例：越界下标必须被拒（★ 本函数**回字典**、不抛 —— 判据看 `ok`/`error`，不是
        #: "有没有抛"）
        neg = E.sketch_set_construction_geometry(doc, "index:99", construction=True)
        ev["T2_construction"].append(
            {
                "step": "负例 index:99",
                "ok": neg.get("ok"),
                "error": neg.get("error"),
                "_": "★ 本函数**回字典不抛** ⇒ 负例判据是 `ok=False` + error 写明越界",
            }
        )
        _close(doc)
        print(
            "  T2 toggle_probe %s→%s ⇒ %s"
            % (before2, after2, ev["T2_toggle_probe"]["★ verdict"])
        )
    except Exception as exc:  # noqa: BLE001
        ev["T2_construction"].append(
            {"fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
        )
        print("  T2 FATAL %s" % str(exc)[:120])

    #: ── T3 · 显示状态（idx 97）───────────────────────────────────────────────────────
    #: ─
    try:
        doc = _make_box()
        l0 = RM.list_display_states(doc)
        cfg = get_com_member(
            get_com_member(doc, "ConfigurationManager"), "ActiveConfiguration"
        )
        created = get_com_member(cfg, "CreateDisplayState", "MCP_DS_PROBE")
        l1 = RM.list_display_states(doc)
        #: ★ 激活**另一个**（不是当前活动的那个）—— ★ 这样 `changed` 才真的被判到
        #:   （★ 新建的显示状态会立刻成为第一个 = 活动 ⇒ 再用它自己验等于没验）
        target = next(
            (x for x in (l1.get("display_states") or []) if x != l1.get("active")), None
        )
        a1 = (
            RM.apply_display_state(doc, target)
            if target
            else {"ok": None, "error": "只有一条显示状态"}
        )
        a2 = RM.apply_display_state(doc, "no_such_state")
        ev["T3_display_states"] = {
            "list_before": l0,
            "create_second": str(created),
            "list_after": l1,
            "apply_target": target,
            "apply_second": a1,
            "apply_missing": a2,
            "judge": "① 两个官方入口读数一致 ② 激活后回读「第一个名字」== 请求名（且 changed=True）"
            " ③ 不存在→报错不猜",
        }
        _close(doc)
        print(
            "  T3 list %r → %r · apply ok=%s · missing ok=%s"
            % (
                l0.get("display_states"),
                l1.get("display_states"),
                a1.get("ok"),
                a2.get("ok"),
            )
        )
    except Exception as exc:  # noqa: BLE001
        ev["T3_display_states"] = {
            "fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])
        }
        print("  T3 FATAL %s" % str(exc)[:120])

    #: ── T4 · 引用文档（idx 244）★ 自建 零件 + 装配 ⇒ 依赖清单非空才叫有判据 ──────────
    #: ──────
    try:
        import sw_assembly as A

        outdir = R / "output" / "probe209"
        outdir.mkdir(parents=True, exist_ok=True)
        part = _make_box()
        part_path = str(outdir / "probe209_part.sldprt")
        save_part = sw_connect.save_document(part, part_path)
        asm = sw_connect.new_document(sw, "assembly")
        opened.append(asm)
        comp = A.add_component(asm, part_path, 0.0, 0.0, 0.0, sw=sw)
        asm_path = str(outdir / "probe209_asm.sldasm")
        save_asm = sw_connect.save_document(asm, asm_path)
        dep = DD.document_dependencies(
            sw, asm_path, traverse=True, search=False, add_read_only_info=False
        )
        dep_ro = DD.document_dependencies(
            sw, asm_path, traverse=False, search=False, add_read_only_info=True
        )
        dep_missing = DD.document_dependencies(sw, str(outdir / "no_such_file.sldprt"))
        #: ★★ 官方例子说非只读跟的是**空串**，★ 而本仓实测回的是 `"FALSE"` ⇒ ★ 取证原始*
        #: *类型与 repr**
        #: （★ 不靠 `str()` 之后的样子下结论 —— 那会把「真的是这个串」与「被我们转出来的
        #: 」混起来）
        raw_vals = get_com_member(
            sw, "GetDocumentDependencies2", asm_path, False, False, True
        )
        ev["T4_dependencies"] = {
            "part_saved": bool(save_part),
            "asm_saved": bool(save_asm),
            "component": comp is not None,
            "part_path": part_path,
            "asm_path": asm_path,
            "raw_types": [type(x).__name__ for x in (raw_vals or [])],
            "raw_repr": [repr(x)[:60] for x in (raw_vals or [])],
            "traverse_true": {
                k: dep.get(k) for k in ("ok", "count", "raw_len", "entries", "error")
            },
            "add_read_only_info": {
                k: dep_ro.get(k) for k in ("ok", "count", "raw_len", "entries", "error")
            },
            "missing_doc": {
                k: dep_missing.get(k)
                for k in ("ok", "count", "raw_len", "error", "note")
            },
            "limitations": dep.get("limitations"),
            "judge": "官方 Returns 的步长能整除 + 名字/路径成对 + 盲区随返回值带出",
        }
        _close(asm)
        _close(part)
        print(
            "  T4 deps count=%s raw_len=%s ok=%s"
            % (dep.get("count"), dep.get("raw_len"), dep.get("ok"))
        )
    except Exception as exc:  # noqa: BLE001
        ev["T4_dependencies"] = {
            "fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])
        }
        print("  T4 FATAL %s" % str(exc)[:120])

    #: ── T5 · 移动 / 复制实体（idx 209）★ 判据 = 包围盒变（移动）/ 实体个数增（复制）──
    #: ──────────
    try:
        import sw_body_ops as BO

        doc = _make_box()
        r_move = BO.move_copy_body(doc, "all", translate_x_mm=25.0)
        r_copy = BO.move_copy_body(
            doc, "all", translate_x_mm=40.0, copy=True, num_copies=1
        )
        #: ★★ 官方 Remarks 的坑：平移与旋转**同时给** ⇒ 官方只应用旋转 ⇒ 本工具必须**说
        #: 出来**
        r_both = BO.move_copy_body(
            doc, "all", translate_x_mm=5.0, rotate_angle_z_deg=30.0
        )
        r_neg = BO.move_copy_body(doc, "index:99", translate_x_mm=1.0)
        #: ★★ T5b · **用"旋转后的包围盒"定死角度单位与"哪根轴"**（★ 不是靠"没报错"当判据
        #: ）：
        #:   60×40×20（x ±30 / y ±20 / z ∈[-20,0]）分别只给 **X / Y / Z 一个角**，
        #:   再看**哪个平面被转了** —— 判据是**跨度的变化**，不是返回值：
        #:   ```
        #:   绕 X 转 ⇒ x 跨度不变、y/z 跨度变
        #:   绕 Y 转 ⇒ y 跨度不变、x/z 跨度变
        #:   绕 Z 转 ⇒ z 跨度不变、x/y 跨度变
        #:   ```
        import math as _m

        def _spans(doc_):
            st = BO.body_state(doc_)
            bb = st.get("bbox_mm") or {}
            if not bb.get("min"):
                return None
            return tuple(round(bb["max"][i] - bb["min"][i], 4) for i in range(3))

        def _plane_moved(s0, s1):
            """★ 判据 = **哪一轴的跨度不动**（绕某轴转 ⇒ 该轴坐标逐点不变 ⇒ 它的跨度是唯一不动的）✓"""
            if not (s0 and s1):
                return "读不到跨度"
            unchanged = [i for i in range(3) if abs(s0[i] - s1[i]) <= 1e-3]
            name = {0: "X", 1: "Y", 2: "Z"}
            if len(unchanged) == 1:
                return "实际绕 %s 轴（该轴跨度不变）" % name[unchanged[0]]
            return "★ 判据分不出来（跨度不变的轴 = %r）" % (
                [name[i] for i in unchanged],
            )

        axes = {}
        for label, kw in (
            ("x", {"rotate_angle_x_deg": 30.0}),
            ("y", {"rotate_angle_y_deg": 30.0}),
            ("z", {"rotate_angle_z_deg": 30.0}),
        ):
            d_ax = _make_box()
            s0 = _spans(d_ax)
            r_ax = BO.move_copy_body(d_ax, "all", **kw)
            s1 = _spans(d_ax)
            axes[label] = {
                "ok": r_ax.get("ok"),
                "moved": r_ax.get("moved"),
                "spans_before": s0,
                "spans_after": s1,
                "verdict": _plane_moved(s0, s1) if (s0 and s1) else "读不到跨度",
            }
            _close(d_ax)
            print("  T5b 只给 %s 角 ⇒ %s" % (label, axes[label]["verdict"]))
        #: ★ 幅度判据：0.5236 rad = 30° ⇒ 绕 X 转 30° 后 y 跨度应为
        #: `20cos30+20sin30 = 27.3205`、z 跨度 `20cos30+20sin30 = 27.3205`（★ 与"按弧度
        #: 解释"对不上）
        ev["T5b_rotation_units"] = {
            "axes": axes,
            "expected_span_if_30deg": round(
                20.0 * _m.cos(_m.radians(30.0)) + 20.0 * _m.sin(_m.radians(30.0)), 4
            ),
            "★ verdict": "见 axes[*].verdict（★ 三格互相对照 ⇒ 能区分'轴错位'与'单位错'）",
            "_": "官方页**没写** RotAngle 的单位、也没说哪根轴；本格是**实测**，用跨度判，不用返回值判",
        }
        ev["T5_move_body"] = {
            "move": {
                k: r_move.get(k)
                for k in (
                    "ok",
                    "selection_count",
                    "moved",
                    "copied",
                    "before",
                    "after",
                    "returned",
                    "error",
                )
            },
            "copy": {
                k: r_copy.get(k) for k in ("ok", "before", "after", "copied", "error")
            },
            "both_translation_and_rotation": {
                k: r_both.get(k) for k in ("ok", "both_given", "note", "error")
            },
            "negative_index": {k: r_neg.get(k) for k in ("ok", "error")},
            "judge": "移动 ⇒ 包围盒必变；复制 ⇒ 实体个数必增（★ 都回读，不用 IFeature 指针）",
        }
        _close(doc)
        print(
            "  T5 move ok=%s moved=%s | copy ok=%s copied=%s | both_given=%s | neg ok=%s"
            % (
                r_move.get("ok"),
                r_move.get("moved"),
                r_copy.get("ok"),
                r_copy.get("copied"),
                r_both.get("both_given"),
                r_neg.get("ok"),
            )
        )
    except Exception as exc:  # noqa: BLE001
        ev["T5_move_body"] = {"fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
        print("  T5 FATAL %s" % str(exc)[:120])

    for d in opened:
        _close(d)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
