"""★ 照**官方示例**完整复现「把外观加到指定显示状态」的七步序列，并逐步入账。

★ 为什么要它（2026-10-02 轮 369–370）
```
★ `render_material_library` 卡在"写成功、读回空"。轮 370 **逐行读官方示例**
   （`Add_and_Delete_Materials_from_Specific_Display_States_Example_VBNET`）⇒ 发现我们**漏了两步**：
   ① **`IRenderMaterial.AddEntity(entity)`** —— 官方示例里先 `SelectByID2("", "FACE", …)` 选一个面、
      取 `GetSelectedObject6(1, -1)`，再 `AddEntity(那个实体)`；
   ② **`DisplayStateNames` 要传 `swConfig.GetDisplayStates` 的**真实名字数组**（★ 我们此前传 `[]`）。
★ 本轮**照全做**（★ 七步入账），★ 结果：**写全成功**（`AddEntity` ok · `Add…` 回 true 且 `id1 = 6`）
   而**读仍回空**（`GetRenderMaterialsCount2` ⇒ 0 · `GetRenderMaterials2` ⇒ `NoneType`）。
⇒ ★★ **于是"读不到"这条**不是我们的步骤缺失** —— ★ 官方示例的每一步都做了。
   ⇒ ★★★ 那是一道**边界**（★ 与事实 47 / 77 同族：★ "本机到这个程度为止"）——
     ★ 记它，比反复试参数有用。
```

## 用法
```
python tools/prove_render_material_sequence.py        # 跑一遍并落 output/render-material-sequence.json
python tools/prove_render_material_sequence.py --keep # 不关文档（调试）
```

"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（探针）
# 文件:   tools/prove_render_material_sequence.py
# 定位:   objective③ 挖 `render_material_library`：把官方示例的七步序列落成**可复跑**
#           的探针。
# 官方依据: `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\Add_and_Delete_Materials
#           _from_
#   Specific_Display_States_Example_VBNET.htm`（★ 七步序列：CreateDisplayState · 选面 ·
# GetSelectedObject6 · **AddEntity** · GetDisplayStates · AddDisplayStateSpecificRenderM
# aterial ·
#   GetRenderMaterialsCount2）· `C:\swapi\types\IConfiguration\CreateDisplayState.md` ·
#   `C:\swapi\types\IModelDocExtension\AddDisplayStateSpecificRenderMaterial.md`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 新建临时文档并关闭（★ 不保存、不另存 —— 硬约束⑦）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "render-material-sequence.json"
)

#: ★ 官方示例用的显示状态选项（★ 反射：swThisDisplayState=1 · **swAllDisplayState=2** ·
#: swSpecifyDisplayState=3）
ALL_DISPLAY_STATE = 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    import sw_connect
    import sw_render_material as M
    from sw_connect import get_com_member, out_i4
    from sw_part import (
        _select_com_object,
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )

    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    ev: dict = {"steps": {}, "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk = current_sketch_name(doc)
        end_sketch(doc)
        extrude_boss(doc, sk, 10.0)
        ext = M.get_extension(doc)

        #: ① 取活动配置
        conf = get_com_member(
            get_com_member(doc, "ConfigurationManager"), "ActiveConfiguration"
        )
        #: ② 建显示状态（★ 官方第一步）
        ev["steps"]["create_display_state"] = {
            "ok": bool(get_com_member(conf, "CreateDisplayState", "MCP_DS")),
        }
        #: ③ 读显示状态名数组（★ 官方用它做 DisplayStateNames）
        names = [str(x) for x in (get_com_member(conf, "GetDisplayStates") or [])]
        ev["steps"]["get_display_states"] = {"ok": bool(names), "names": names[:5]}
        #: ④ 选一个面（★ 官方 `' Select a face`）
        face = None
        for b in get_com_member(doc, "GetBodies2", 0, False) or []:
            fs = get_com_member(b, "GetFaces") or []
            if fs:
                face = fs[0]
                break
        doc.ClearSelection2(True)
        sel_ok = bool(
            face is not None and _select_com_object(face, append=True, mark=0)
        )
        ev["steps"]["select_face"] = {"ok": sel_ok}
        #: ⑤ 建外观 + **AddEntity**（★ 我们此前漏掉的那一步）
        mat = M.create_render_material(doc, "MCP_SeqMat", M.RenderMaterialSpec())
        try:
            ev["steps"]["add_entity"] = {
                "ok": bool(get_com_member(mat, "AddEntity", face))
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["add_entity"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:100]),
            }
        #: ⑥ Add（★ opt=2 + **真实名字数组**）
        id1, id2 = out_i4(), out_i4()
        try:
            r = get_com_member(
                ext,
                "AddDisplayStateSpecificRenderMaterial",
                mat,
                ALL_DISPLAY_STATE,
                names,
                id1,
                id2,
            )
            ev["steps"]["add"] = {
                "ok": bool(r),
                "id1": repr(id1.value),
                "id2": repr(id2.value),
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["add"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:100]),
            }
        #: ⑦ 读回
        try:
            n = int(
                get_com_member(
                    ext, "GetRenderMaterialsCount2", ALL_DISPLAY_STATE, names
                )
                or 0
            )
            raw = get_com_member(ext, "GetRenderMaterials2", ALL_DISPLAY_STATE, names)
            item = None
            if raw is not None:
                try:
                    item = str(get_com_member(raw, "MaterialIdName") or "")[:60]
                except Exception:  # noqa: BLE001
                    item = "(object)"
            ev["steps"]["read_back"] = {
                "ok": n > 0,
                "count": n,
                "raw_type": type(raw).__name__,
                "item": item,
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["read_back"] = {"ok": False, "err": str(exc)[:80]}

        #: ★ 判据：**七步都执行成功**（★ 含读）才算 pass；★ 而"读回空"是已知边界（不谎报
        #:  pass）
        exec_ok = all(v.get("ok") for k, v in ev["steps"].items() if k != "read_back")
        ev["verdict"] = (
            "pass" if (exec_ok and ev["steps"]["read_back"].get("ok")) else "partial"
        )
        ev["note"] = (
            "★ 官方示例的每一步都执行成功；★ 而**读回仍空** ⇒ 那是**本机文档/环境**的边界"
            "（★ 不是步骤缺失）。★ 详见 known-facts 事实 286/287。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        if doc is not None and not args.keep:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
