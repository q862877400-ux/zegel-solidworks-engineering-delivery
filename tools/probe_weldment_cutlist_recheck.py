"""★ 真机：核「结构系统（焊件）」那一族 —— `InsertWeldmentCutList2` 的**真实形态**是什么。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_weldment_cutlist_recheck.py
# 定位:   ★ 2026-10-03（轮 548）★ 把**目标点名第三族**（结构系统 / 焊件）**核到与前两
#           族同一标准**。
#
#   ★★ **为什么还要核**：`docs/toolbar-gaps-backend-limits.md` §四 判它「成立」，
#     ★ 而**理由是**「`InsertWeldmentCutList2` **取不到**」—— ★ 而**"取不到"是个含糊的词** ⚠
#     ★ 按轮 545-547 的教训（边界要精确到**接口级**），★ 得问清：
#     **它是回 `None`、报错、还是接口不在类型库里？**
#
#   ★ 静态已查（本轮）：
# · ★ **两源都有它**：`C:\\swapi\\types\\IFeatureManager\\InsertWeldmentCutList2.md` + C
# HM ✓
#       ⇒ ★ **故"取不到"不是"官方没有它"**；
#     · ★ 类型库：`InsertWeldmentCutList2` **arity=2（1 in `Bodies` + out）**；
#       旧版 `InsertWeldmentCutList` **arity=1（0 in + out）**；
#       ★ 而 **`IWeldmentCutListFolder` 在类型库里查不到** ⚠
#
#   ★ 真机试三条：
#     ⓐ `InsertWeldmentCutList2([])`（★ 空数组 —— 1 in）
#     ⓑ `InsertWeldmentCutList()`（★ 旧版 · 0 in）
#     ⓒ `InsertWeldmentFeature()`（★ 另一条 —— ★ 建"焊件"这个特征本身）
#   ★ 并**同时记**：★ 返回值（种类 + `Name` + `GetTypeName2`）· ★ 树增量 · ★ 错误串。
#     ⇒ ★ 与**事实 420 的分类判据**（回对象 / 回 None / 报错）**逐格对齐**。
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **本探针不求建成** —— ★ 它要的是**那一族的形态**这一个事实。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_feature_readback as fr  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402


def _mk_multi_body(doc):
    """★ 一个**多体**实体件（★ 焊件/切割清单要有体）。"""
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.03,
        -0.03,
        0.0,
        0.03,
        0.03,
        0.0,
    )
    P.end_sketch(doc)
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    ok = False
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            ok = True
            break
        except Exception:  # noqa: BLE001
            continue
    #: \u2605 \u7b2c\u4e8c\u4e2a\u4e0d\u76f8\u4ea4\u7684\u4f53\uff08\u2605 \u591a\u4f53\
    #: uff09
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        0.05,
        0.05,
        0.0,
        0.07,
        0.07,
        0.0,
    )
    P.end_sketch(doc)
    names2 = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in (names2[-1] if names2 else "\u8349\u56fe2", "\u8349\u56fe2"):
        try:
            P.extrude_boss(doc, cand, 0.02, merge=False)
            break
        except Exception:  # noqa: BLE001
            try:
                P.extrude_boss(doc, cand, 0.02)
                break
            except Exception:  # noqa: BLE001
                pass
    return ok


def _bodies(doc):
    return list(C.get_com_member(doc, "GetBodies2", 0, True) or [])


def _one(sw, tag, kind):
    row = {"tag": tag, "kind": kind}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["solid"] = _mk_multi_body(doc)
        row["n_bodies"] = len(_bodies(doc))
        before = list(fr.feature_names(doc) or [])
        fm = C.get_com_member(doc, "FeatureManager")
        ret = None
        try:
            if kind == "cutlist2":
                ret = C.get_com_member(fm, "InsertWeldmentCutList2", [])
            elif kind == "cutlist_old":
                ret = C.get_com_member(fm, "InsertWeldmentCutList")
            else:
                ret = C.get_com_member(fm, "InsertWeldmentFeature")
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(C.get_com_member(ret, m))
                    except Exception:  # noqa: BLE001
                        pass
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
            s = str(exc)
            for tok in ("0x80010105", "0x80028CA0", "0x80004005"):
                if tok in s:
                    row["error_code"] = tok
                    break
        after = list(fr.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        #: \u2605\u2605 \u4e8b\u5b9e 420 \u7684\u5206\u7c7b\u5224\u636e
        if row.get("err"):
            row["class"] = "raised"
        elif ret is not None:
            row["class"] = "returned_object"
        else:
            row["class"] = "silent_none"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
        row["class"] = "raised"
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u7ed3\u6784\u7cfb\u7edf\uff08\u710a\u4ef6\uff09\u90a3\u4e00\u65cf\uff1a`InsertWeldmentCutList2` \u7684**\u771f\u5b9e\u5f62\u6001**",
        "static": "\u4e24\u6e90\u90fd\u6709\u5b83\uff08swapi md + CHM\uff09\uff1b\u7c7b\u578b\u5e93\uff1aCutList2 arity=2\uff081 in `Bodies`\uff09\u00b7 CutList arity=1\uff080 in\uff09\uff1b"
        "`IWeldmentCutListFolder` \u7c7b\u578b\u5e93\u91cc\u67e5\u4e0d\u5230",
        "cases": [],
    }
    for tag, kind in (
        ("\u2460 InsertWeldmentCutList2([])", "cutlist2"),
        (
            "\u2461 InsertWeldmentCutList()\uff08\u2605 \u65e7\u7248\uff09",
            "cutlist_old",
        ),
        ("\u2462 InsertWeldmentFeature()", "feature"),
    ):
        ev["cases"].append(_one(sw, tag, kind))
    ev["classes"] = sorted({c.get("class") for c in ev["cases"] if c.get("class")})
    ev["total"] = len(ev["cases"])
    ev["verdict"] = (
        "all_raised"
        if ev["classes"] == ["raised"]
        else (
            "all_silent_none"
            if ev["classes"] == ["silent_none"]
            else "mixed:" + ",".join(ev["classes"])
        )
    )
    p = R / "output" / "weldment-cutlist-recheck-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5f62\u6001\uff1a**%s**\uff08%s\uff09" % (ev["verdict"], ev["classes"]))
    for c in ev["cases"]:
        print(
            "  %-36s \u4f53=%s \u56de=%-9s \u540d=%s \u578b=%s"
            % (
                c.get("tag"),
                c.get("n_bodies"),
                c.get("returned"),
                c.get("ret_name"),
                c.get("ret_type"),
            )
        )
        print(
            "        \u5206\u7c7b=**%s** new=%s \u9519\u7801=%s"
            % (c.get("class"), c.get("new"), c.get("error_code"))
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
