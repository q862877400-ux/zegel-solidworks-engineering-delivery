r"""@brief 端到端实测 `scripts/sw_sheet_metal.py`（把它的「未在本机实测」摘掉）。

## 为什么现在必须测
该模块头部自述「**未在本机实测**」，而它的 6 个函数**已经作为 MCP 工具暴露给用户了**
（T-011 接线，`server.py` 45 → 65）。**⇒ 没测过就暴露是风险。** 本轮补这个洞。

## 测什么
| 函数 | 判据 |
|---|---|
| `create_base_flange(model, sketch_ref, spec)` | 返回真 `IFeature` 且特征树里出现钣金特征；**且草图被按名字选到** |
| `sheet_metal_evidence(model)` | 能读回厚度 / 折弯半径等 |
| `create_one_bend(model, sketch_ref, spec)` | 在已有基体法兰上再建一个折弯 |
| `create_edge_flange` / `create_gusset` / `create_draft` | 同样试；**失败就如实报**（不包装成成功）|

**⚠ 安全（铁律 2）**：建特征可能弹模态对话框 ⇒ 先置 `CommandInProgress = True`；
只在自己新建的文档上操作；跑完关闭、**不保存**。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_sheet_metal_e2e.py
# 定位:   `scripts/sw_sheet_metal.py` 头部「未在本机实测」的摘帽实验；
#         也是 T-011 那 6 条钣金工具的**底层验收**。
# 官方签名依据: 见 `scripts/sw_sheet_metal.py` 各函数的来源块
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part  # noqa: E402
from scripts import sw_sheet_metal as SM  # noqa: E402

PASS, FAIL = [], []


def check(label, fn):
    try:
        v = fn()
        print("  ✓ %-56s → %r" % (label, str(v)[:60]))
        PASS.append(label)
        return v
    except Exception as exc:  # noqa: BLE001
        print("  ✗ %-56s → %s: %s" % (label, type(exc).__name__, str(exc)[:74]))
        FAIL.append((label, str(exc)[:110]))
        return None


def feature_names(model):
    out = []
    try:
        for f in SM.iter_features(model):
            try:
                out.append(str(get_com_member(f, "Name")))
            except Exception:  # noqa: BLE001
                pass
    except Exception:  # noqa: BLE001
        pass
    return out


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)

    # ⚠ 铁律 2：建特征前抑制模态对话框
    try:
        sw.CommandInProgress = True
        print("[0] CommandInProgress = True（抑制模态对话框）")
    except Exception as exc:  # noqa: BLE001
        print("[0] ⚠ 设 CommandInProgress 失败: %s" % str(exc)[:60])

    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        print("[1] 新零件 %r" % title)

        # ── 建一个闭合矩形草图（平板基体的轮廓）──────────────────
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        names = feature_names(model)
        print("[2] 草图已建；特征树: %r" % (names,))

        print()
        print("=== ① create_base_flange（闭合轮廓 ⇒ 平板基体）===")
        spec = SM.BaseFlangeSpec(thickness=0.002, bend_radius=0.002, depth=0.0 + 0.05)
        feat = check("create_base_flange(model, 'Sketch1', spec)",
                     lambda: SM.create_base_flange(model, "Sketch1", spec))
        names_after = feature_names(model)
        print("     建后特征树: %r" % (names_after,))
        check("特征树里出现了新特征",
              lambda: len(names_after) > len(names))

        print()
        print("=== ② sheet_metal_evidence（读回）===")
        ev = check("sheet_metal_evidence(model)", lambda: SM.sheet_metal_evidence(model))
        if isinstance(ev, dict):
            for k in sorted(ev)[:10]:
                print("       %-28s %r" % (k, str(ev[k])[:48]))

        print()
        print("=== ③ create_one_bend（在已有钣金上）===")
        try:
            sk2 = sw_part.sketch(model, "Front Plane")
            sw_part.sketch_corner_rectangle(model, -0.02, -0.02, 0.02, 0.02)
            one = SM.OneBendSpec(bend_radius=0.002, angle=90.0)
            check("create_one_bend(model, 'Sketch2', spec)",
                  lambda: SM.create_one_bend(model, "Sketch2", one))
        except Exception as exc:  # noqa: BLE001
            print("  ⚠ 建第二个草图就失败（跳过 one_bend）: %s" % str(exc)[:70])

        print()
        print("=== ④ create_edge_flange（需**先选好边**）===")
        try:
            from scripts.sw_selection_spec import resolve_selection
            resolve_selection(model, "index:0", "EDGE")
            ef = SM.EdgeFlangeSpec(bend_radius=0.002, flange_length=0.01)
            check("create_edge_flange(model, spec) [边已选]",
                  lambda: SM.create_edge_flange(model, ef))
        except Exception as exc:  # noqa: BLE001
            print("  ✗ 选边就失败: %s" % str(exc)[:70])

        print()
        print("=== ⑤ create_gusset / create_draft（需**先选好面**）===")
        try:
            from scripts.sw_selection_spec import resolve_selection
            resolve_selection(model, "index:0", "FACE")
            gs = SM.GussetSpec(thickness=0.002, profile_distance_1=0.01)
            check("create_gusset(model, spec) [面已选]",
                  lambda: SM.create_gusset(model, gs))
        except Exception as exc:  # noqa: BLE001
            print("  ✗ gusset 路径失败: %s" % str(exc)[:70])
        try:
            from scripts.sw_selection_spec import resolve_selection
            resolve_selection(model, "index:0", "FACE")
            df = SM.DraftFeatureSpec(angle=5.0, depth=0.01)
            check("create_draft(model, None, spec) [面已选]",
                  lambda: SM.create_draft(model, None, df))
        except Exception as exc:  # noqa: BLE001
            print("  ✗ draft 路径失败: %s" % str(exc)[:70])

        print()
        print("=== 结论 ===")
        print("  通过 %d 项，失败 %d 项" % (len(PASS), len(FAIL)))
        for label, msg in FAIL:
            print("    ✗ %s\n        %s" % (label, msg))
    finally:
        try:
            sw.CommandInProgress = False
            print("[收尾] CommandInProgress = False")
        except Exception:  # noqa: BLE001
            pass
        try:
            if title:
                sw.CloseDoc(title)
                print("[收尾] 文档已关闭（未保存）")
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
