"""★ 真机：`sw_weldment.ensure_cut_list`（★ 它早已实现 dispid 兜底，★ 而没被接进工具层）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_weldment_cut_list.py
# 定位:   ★ 2026-10-03（轮 497）★ 给 `scripts/sw_weldment.ensure_cut_list` 留**当前**
#           的真机证据。
#
#   ★★ **为什么要重做**（★ 本轮的发现链）：
#     · `output/weldment-evidence.json` 里 `create_cut_list` 是 **`ok:false`**，
#       错误逐字「`IFeatureManager.InsertWeldmentCutList2` 在当前后端（**pywin32 迟到绑定**）
#       上**取不到**」⇒ ★ 而**那份证据没有产出者**（★ 全仓 grep 无命中）⇒ ★ **是旧证据** ⚠
#     · 而 `scripts/sw_weldment.py` **L260-275** 里**早就有 dispid 兜底**，注释逐字：
#       「★ SW2026 IDispatch 将 **DISPID 174** 的方法**同时暴露成值为 `None` 的伪属性**，
#        直接按官方类型库 **DISPATCH_METHOD** 语义调用，★ **避免把 None 当函数**」✓
#     · 轮 496 的探针也证实：`GetIDsOfNames("InsertWeldmentCutList2")` ⇒ **dispid = 174**，
#       `Invoke(174, …, VARIANT(VT_ARRAY|VT_DISPATCH, bodies))` ⇒ **树新增 `切割清单项目1`** ✓
#     ⇒ ★★ 故那份旧证据**不代表现状**，本探针重做一遍 ✓
#
#   ★★★ 另外 `tools/census_orphan_callability.py` 把 `("sw_weldment", "create_cut_list")`
#     列在 **孤儿候选**里（★ 实现了、而**没被工具层调用**）—— ★ 那也正是本轮要消掉的。
#
#   ⚠ 全程走 `tools/sw_guard.py`（★ 超时 + 弹窗处置 + `sw_alive` 复查）。
# 官方依据: `C:\swapi\types\IFeatureManager\InsertWeldmentCutList2.md`
#   （`Feature InsertWeldmentCutList2( System.object Bodies )` · `kind: method`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **特征树里出现 `CutListFolder` 类型的特征**（★ 用 `GetTypeName2`，
#   ★ 而不是拿名字猜 —— 事实 242：挑只依赖被测对象的那个）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_sketch as SK  # noqa: E402                                   # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_weldment as W  # noqa: E402


def _cut_list_folders(model):
    """★ 按**类型名**数切割清单文件夹（★ 事实 242）。"""
    out = []
    try:
        for feat in W.iter_features_recursive(model):
            if str(C.get_com_member(feat, "GetTypeName2") or "") == "CutListFolder":
                out.append(str(C.get_com_member(feat, "Name") or ""))
    except Exception as exc:  # noqa: BLE001
        return {"err": "%s: %s" % (type(exc).__name__, str(exc)[:90])}
    return out


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u771f\u673a\uff1asw_weldment.ensure_cut_list\uff08\u2605 \u5b83\u65e9\u5df2\u5b9e\u73b0 dispid \u515c\u5e95\uff09",
        "judge": "\u7279\u5f81\u6811\u91cc\u51fa\u73b0 **CutListFolder** \u7c7b\u578b\u7684\u7279\u5f81\uff08GetTypeName2\uff09",
        "steps": [],
    }
    doc = None
    try:
        doc = C.new_document(sw, "part")
        #: \u2605 \u2460 \u5148\u5efa\u4e00\u4e2a**\u710a\u4ef6**\uff08\u2605 \u7ed3\u67
        #: 84\u6784\u4ef6\uff09
        #: \u2605\u2605 2026-10-03\uff08\u8f6e 497\uff09**\u7b2c\u4e00\u7248\u7b7e\u540d
        #: \u8c03\u9519\u4e86** \u2014\u2014
        #: \u26a0 \u6211\u4f20\u7684\u662f `(doc, "\u8349\u56fe1", profile)`\uff0c\u2605
        #:  \u800c\u771f\u7b7e\u540d\u662f
        #:     `create_structural_member(model, **profile_path**, **segment_groups**, ...)`
        #: \u21d2 \u2605 **\u6211\u628a\u300c\u8349\u56fe\u540d\u300d\u5f53\u6210\u4e86\
        #: u300c\u578b\u6750\u8def\u5f84\u300d** \u26a0
        #: \u771f\u673a\u62a5 `FileNotFoundError: \u710a\u4ef6\u578b\u6750\u4e0d\u5b58\u
        #: 5728\u6216\u683c\u5f0f\u9519\u8bef: D:\AI\SW\\u8349\u56fe1` \u2713
        #: \u21d2 \u2605 \u6b63\u662f AGENTS.md \u90a3\u6761\u7eaa\u5f8b\uff1a**\u6309\u
        #: 5951\u7ea6\u8c03\uff0c\u522b\u624b\u8c03\u5185\u90e8\u5b9e\u73b0** \u2713
        #: \u2605\u2605 \u800c `segment_groups` \u8981\u7684\u662f**\u8349\u56fe\u6bb5\u
        #: 5bf9\u8c61**\uff08\u2605 `sw_weldment.py` L182-195\uff1a
        #: \u6bcf\u7ec4\u4e00\u4e2a `CreateStructuralMemberGroup`\uff09\u21d2 \u2605 \u6
        #: 545\u8fd9\u91cc**\u5728\u8349\u56fe\u5f00\u7740\u65f6**\u53d6\u6bb5\u3002
        P.start_sketch(doc, plane_name="Front Plane")
        C.get_com_member(
            C.get_com_member(doc, "SketchManager"),
            "CreateLine",
            0.0,
            0.0,
            0.0,
            120.0 / 1000.0,
            0.0,
            0.0,
        )
        #: \u2605 \u2605\u2605 **\u8d81\u8349\u56fe\u8fd8\u5f00\u7740\u53d6\u6bb5**\uff0
        #: 8\u2605 `_capture_sketch_ref` \u7684\u6559\u8bad\uff1a
        #: \u5b83\u7b2c\u4e00\u884c\u8bfb `SketchManager.ActiveSketch`\uff0c\u2605 \u517
        #: 3\u4e86\u5c31\u53d6\u4e0d\u5230\uff09
        segments = []
        try:
            sk = C.get_com_member(
                C.get_com_member(doc, "SketchManager"), "ActiveSketch"
            )
            segments = list(SK.get_sketch_segments(sk) or [])
        except Exception as exc:  # noqa: BLE001
            ev["steps"].append(
                {
                    "step": "get_segments",
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                }
            )
        P.end_sketch(doc)
        profile = (
            r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles"
            r"\GB\square-rods.sldlfp"
        )
        ev["steps"].append({"step": "segments", "n": len(segments)})
        sm = None
        if segments:
            try:
                sm = W.create_structural_member(
                    doc, profile_path=profile, segment_groups=[[s] for s in segments]
                )
            except Exception as exc:  # noqa: BLE001
                ev["steps"].append(
                    {
                        "step": "structural_member",
                        "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
                    }
                )
        ev["steps"].append({"step": "structural_member_ok", "ok": sm is not None})
        ev["tree_before"] = list(P.feature_names(doc) or [])
        ev["cutlist_before"] = _cut_list_folders(doc)

        #: \u2605 \u2461 \u771f\u673a\u8c03\u5b83
        try:
            folders = W.ensure_cut_list(doc)
            #: ⚠ 2026-10-03（轮 497）**这里也踩了一下**：我原来写
            #:   `C.get_com_member(f, "Name")` —— ★ 而真机报
            #:   `AttributeError: 'PyIDispatch' object has no attribute 'Name'` ⚠
            #:   ⇒ ★ 那些 `CutListFolder` 的 `f` **直接读 `.Name` 不行**
            #:   ⇒ ★ 故**只记个数**；★ 而名字交给下面的 `_cut_list_folders()`
            #: （★ 它走 `iter_features_recursive` 拿到的是**特征对象**、那条路能读到 `Na
            #: me`）✓
            ev["ensure"] = {"ok": True, "n": len(folders or [])}
        except Exception as exc:  # noqa: BLE001
            ev["ensure"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
            }
        ev["tree_after"] = list(P.feature_names(doc) or [])
        ev["cutlist_after"] = _cut_list_folders(doc)
        ev["verdict"] = "pass" if ev["cutlist_after"] else "fail"
    except Exception as exc:  # noqa: BLE001
        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        ev["verdict"] = "fail"
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass

    p = R / "output" / "weldment-cut-list-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u636e\uff1a**%s**" % ev.get("verdict"))
    print(
        "  \u7ed3\u6784\u6784\u4ef6\uff1a%s"
        % [s for s in ev["steps"] if s.get("step") == "structural_member_ok"]
    )
    print("  ensure\uff1a%s" % json.dumps(ev.get("ensure"), ensure_ascii=False)[:200])
    print(
        "  \u6e05\u5355 \u524d=%s \u540e=%s"
        % (ev.get("cutlist_before"), ev.get("cutlist_after"))
    )
    print(
        "  \u6811 \u524d=%d \u540e=%d"
        % (len(ev.get("tree_before") or []), len(ev.get("tree_after") or []))
    )
    for s in ev["steps"]:
        if s.get("err"):
            print("  step_err=%s" % str(s["err"])[:140])
    if ev.get("err"):
        print("  err=%s" % ev["err"][:170])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
