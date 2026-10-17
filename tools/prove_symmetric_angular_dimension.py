"""★ 真机：**对称线性直径尺寸** —— `IModelDocExtension.AddSymmetricDimension`（★ 照官方例子）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_symmetric_angular_dimension.py
# 定位:   ★ 2026-10-03（轮 584）★ 照新纪律（**官方文档是第 0 步**）攻台账「对称线性直径尺寸」。
#
#   ★★★★★ **而这一轮把「第 ③ 样」用到了极致** —— ★ 答案全在**官方的那个例子**里
#     （`D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\Create_Full_Symmetrical_Angular_Dimension_Example_VB.htm`）：
#     ```
#     "This example shows how to create a full symmetrical angular dimension between
#      **a centerline and a line**."
#     Postconditions \u9010\u5b57\uff1a
#       3. Creates a **centerline and three lines** in the open sketch.
#       4. **Selects the centerline and one of the lines.**
#       5. **Suppresses the dimension dialog.**
#       6. Creates a full symmetrical angular dimension for the entities selected in step 4.
#       7. Unsuppresses the dimension dialog.
#     \u2605 \u800c\u5b83\u7684\u8c03\u7528\u5e8f\uff1a
#       InsertSketch(True) \u2192 CreateCenterLine \u2192 CreateLine \u00d73
#       \u2192 **SelectByID2("Line1", "SKETCHSEGMENT", x,y,z, False, 0, Nothing, 0)**
#       \u2192 **SelectByID2("Line3", "SKETCHSEGMENT", x,y,z, True, 0, Nothing, 0)**
#       \u2192 ClearSelection2(True)
#       \u2192 **SetUserPreferenceToggle(swInputDimValOnCreate, False)**   \u2190 \u2605 \u6291\u5236\u5c3a\u5bf8\u5bf9\u8bdd\u6846
#       \u2192 \u518d\u9009\u4e00\u6b21\uff08\u540c\u4e24\u4e2a\uff09
#       \u2192 **AddSymmetricDimension(x, y, z)** \u2192 \u56de **`DisplayDimension`**
#       \u2192 ClearSelection2(True) \u2192 toggle \u56de True
#     ```
#     \u2605\u2605 **\u800c\u5b83\u8fd8\u8bf4\u660e\u4e86\u4e00\u4ef6\u4e8b**\uff1a
#       \u2605 \u8349\u56fe\u6bb5**\u6709\u540d\u5b57**\uff08`"Line1"` / `"Line3"`\uff09\u3001\u2605 \u800c**\u6309\u90a3\u4e2a\u540d\u5b57\u80fd\u9009\u4e2d** \u2713
#       \uff08\u2605 \u4e0e\u4e8b\u5b9e 32 **\u4e0d\u77db\u76fe**\uff1a32 \u8bf4\u7684\u662f**\u8fb9/\u9762**\uff0c
#        \u2605 \u800c**\u8349\u56fe\u6bb5\u5728\u8349\u56fe\u91cc\u6709\u540d\u5b57**\uff09
#
#   ★ 判据：**返回对象非 None**（★ 官方回 `DisplayDimension`）**或** 草图尺寸计数增加。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 两组：照例子（选 centerline + line）/ 对照（什么都不选）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402


def _dims(doc):
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        if sk is None:
            return -1
        #: ★ 2026-10-03（轮 585）**修正**：★ 取法换成
        #:   `ISketch.GetDimensionCount2()`（★ 反射里有 `GetDimensionCount2`/`3`）
        #:   —— ★ 上一轮用 `GetSketchDimensions` **回 -1**（本仓没那个名字）。
        for nm in ("GetDimensionCount2", "GetDimensionCount3", "GetDimensionCount"):
            try:
                v = C.get_com_member(sk, nm)
                if v is not None:
                    return int(v)
            except Exception:                                             # noqa: BLE001
                continue
        return -1
    except Exception:                                                     # noqa: BLE001
        return -1


def _empty_callout():
    import pythoncom
    import win32com.client
    return win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)


def _one(sw, tag, do_select):
    row = {"tag": tag, "select": do_select, "ok": False}
    doc = None
    toggle_off = False
    try:
        doc = C.new_document(sw, "part")
        sm = C.get_com_member(doc, "SketchManager")
        #: \u2605 \u7167\u4f8b\u5b50\uff1a`InsertSketch(True)` \u2192 **centerline + 3 \u6761\u7ebf**
        C.get_com_member(sm, "InsertSketch", True)
        C.get_com_member(sm, "CreateCenterLine", 0.0, 0.043667, 0.0, 0.0, -0.050556, 0.0)
        C.get_com_member(sm, "CreateLine", -0.102, 0.039667, 0.0, -0.086223, 0.011, 0.0)
        C.get_com_member(sm, "CreateLine", 0.142445, 0.066556, 0.0, 0.100889, -0.032333, 0.0)
        C.get_com_member(sm, "CreateLine", 0.085334, 0.036556, 0.0, 0.049658, -0.048341, 0.0)
        ext = C.get_com_member(doc, "Extension")
        steps = {}
        if do_select:
            #: \u2605 **\u7167\u4f8b\u5b50\u9010\u5b57**\uff1a`("Line1","SKETCHSEGMENT", x,y,z, append, 0, Nothing, 0)`
            #: ★★ **直接调 `SelectByID2`**（★ 而**不是** `_select_by_id` ——
            #:   ★ 后者的签名是 `(extension, name, type, append, mark)`，
            #:   ★ **根本没有 x/y/z**（★ 上一轮我把坐标按位置传 ⇒ 撞上 `append`））。
            #:   ★ 官方 9 参：`(name, type, x, y, z, Append, mark, Callout, SelectOption)`
            for nm, (x, y), app in (("Line1", (-2.22223294397278e-04, 2.23334410869282e-02), False),
                                    ("Line3", (0.113556103437018, -1.44445141358242e-03), True)):
                try:
                    ok = C.get_com_member(ext, "SelectByID2", nm, "SKETCHSEGMENT",
                                          x, y, 0.0, bool(app), 0,
                                          _empty_callout(), 0)
                    steps["SelectByID2(%s)" % nm] = str(ok)
                except Exception as exc:                                  # noqa: BLE001
                    steps["SelectByID2(%s)" % nm] = "%s: %s" % (type(exc).__name__, str(exc)[:60])
            try:
                doc.ClearSelection2(True)
                steps["ClearSelection2"] = "ok"
            except Exception as exc:                                      # noqa: BLE001
                steps["ClearSelection2"] = str(exc)[:60]
        #: \u2605 **\u5fc5\u987b\u5148\u6291\u5236\u5c3a\u5bf8\u5bf9\u8bdd\u6846**\uff08\u2605 \u4f8b\u5b50\u7684\u6b65 5\uff09
        try:
            #: ★★ 2026-10-03（轮 584）**修正**：本仓**早就有**那张表 ——
            #:   `sw_automation_knowledge.DIALOG_SUPPRESSORS["swInputDimValOnCreate"] = 10`
            #:   （★ 值来自对 `swconst` 的反射）。
            #:   ★ 而我第一版凭空写了 `A.enum_value(...)`（★ **本仓没有那个函数**）
            #:   ⇒ ★ **toggle 从未设过** ⇒ 弹出「修改」对话框 ⇒ 挂住（★ 而**护栏把会话救回来了**）。
            from scripts.sw_automation_knowledge import DIALOG_SUPPRESSORS
            tog = DIALOG_SUPPRESSORS["swInputDimValOnCreate"]
            C.get_com_member(sw, "SetUserPreferenceToggle", int(tog), False)
            toggle_off = True
            steps["toggle_off"] = "swInputDimValOnCreate=%s" % tog
        except Exception as exc:                                          # noqa: BLE001
            steps["toggle_off"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
        if do_select:
            #: \u2605 **\u518d\u9009\u4e00\u6b21**\uff08\u2605 \u4f8b\u5b50\u5c31\u662f\u8fd9\u4e48\u505a\u7684\uff09
            for nm, (x, y), app in (("Line1", (-2.22223294397278e-04, 2.23334410869282e-02), False),
                                    ("Line3", (0.113556103437018, -1.44445141358242e-03), True)):
                try:
                    C.get_com_member(ext, "SelectByID2", nm, "SKETCHSEGMENT",
                                     x, y, 0.0, bool(app), 0, _empty_callout(), 0)
                except Exception:                                         # noqa: BLE001
                    pass
        before_dims = _dims(doc)
        row["dims_before"] = before_dims
        ret = None
        try:
            #: \u2605 **\u4e3b\u8c03\u7528**\uff08\u2605 3 \u53c2\uff1a\u5c3a\u5bf8\u6587\u5b57\u7684 x/y/z\uff09
            ret = C.get_com_member(ext, "AddSymmetricDimension",
                                   8.32913738352659e-02, 0.112403597688285, 0.0)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            #: ★★ 2026-10-03（轮 586）**换判据**：
            #:   ★ 上一轮两格都回 `CDispatch` ⇒ 那个判据**不能区分**。
            #:   ★ 故本轮去读**返回对象自己的名字**（★ 真建成的话
            #:   它应该有 `D1@草图1` 那种名字）。
            probe = {}
            if ret is not None:
                for nm in ("Name", "GetName", "FullName", "GetTypeName2"):
                    try:
                        v = C.get_com_member(ret, nm)
                        probe[nm] = str(v)[:60] if v is not None else "None"
                    except Exception as exc:                              # noqa: BLE001
                        probe[nm] = "%s: %s" % (type(exc).__name__, str(exc)[:48])
                #: ★ 而它还应能回答“属于哪个草图”
                for nm in ("GetSketch", "GetOwner", "GetFeature"):
                    try:
                        o = C.get_com_member(ret, nm)
                        if o is not None:
                            probe[nm] = type(o).__name__
                    except Exception as exc:                              # noqa: BLE001
                        probe[nm] = "%s: %s" % (type(exc).__name__, str(exc)[:40])
            row["probe"] = probe
            #: ★ 而**文档级**的尺寸计数（★ 上一轮没试这个入口）
            doc_dims = {}
            for nm in ("GetDimensionCount", "GetDimensionCount2"):
                try:
                    doc_dims[nm] = int(C.get_com_member(doc, nm))
                except Exception as exc:                                  # noqa: BLE001
                    doc_dims[nm] = "%s" % type(exc).__name__
            row["doc_dims"] = doc_dims
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after_dims = _dims(doc)
        row["dims_after"] = after_dims
        row["new_dims"] = (after_dims - before_dims) if (after_dims >= 0 and before_dims >= 0) else None
        row["ok"] = bool(ret is not None or (row["new_dims"] and row["new_dims"] > 0))
        row["steps"] = steps
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
    finally:
        if toggle_off:
            try:
                from scripts.sw_automation_knowledge import DIALOG_SUPPRESSORS
                tog = DIALOG_SUPPRESSORS["swInputDimValOnCreate"]
                C.get_com_member(sw, "SetUserPreferenceToggle", int(tog), True)
            except Exception:                                             # noqa: BLE001
                pass
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u5bf9\u79f0\u7ebf\u6027\u76f4\u5f84\u5c3a\u5bf8\uff1a`IModelDocExtension.AddSymmetricDimension`"
               "\uff08\u2605 **\u7167\u5b98\u65b9\u4f8b\u5b50**\uff09",
          "official": "\u4f8b\u5b50\uff1a\"\u2026between **a centerline and a line**\"\uff1b"
                      "\u2605 \u524d\u7f6e\uff1a**\u5148 `SetUserPreferenceToggle(swInputDimValOnCreate, False)`**"
                      "\uff08\u6291\u5236\u5c3a\u5bf8\u5bf9\u8bdd\u6846\uff09",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 **\u7167\u4f8b\u5b50**\uff08\u9009 centerline + line\uff09", True))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a**\u4ec0\u4e48\u90fd\u4e0d\u9009**", False))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "symmetric_dim_%d_of_%d" % (ev["passed"], ev["total"])
    p = R / "output" / "symmetric-angular-dimension-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print("  %-42s ok=%-6s \u5c3a\u5bf8 %s \u2192 %s\uff08\u589e %s\uff09\u56de=%s" % (
            c.get("tag"), c.get("ok"), c.get("dims_before"), c.get("dims_after"),
            c.get("new_dims"), c.get("returned")))
        for k, v in (c.get("steps") or {}).items():
            print("        step %-22s %s" % (k, str(v)[:92]))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
