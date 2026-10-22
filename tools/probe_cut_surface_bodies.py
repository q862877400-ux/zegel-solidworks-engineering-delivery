"""★ 真机：`InsertCutSurface` 的 **`Bodies` 形态矩阵**（★ 上轮错码链的推论）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_cut_surface_bodies.py
# 定位:   ★ 2026-10-03（轮 522）★ 执行**上一轮留在事实 402 里的推论**：
#
#   > ★★ 剩下最可能：**`Bodies` 那个位置该是 `VARIANT`**（★ 而我传的是 Python `list`），
#   >   或 out 也算进某种计数。
#
#   ★ 上轮那条**错码链**（★ 每一步各指一处）：
#   ```
#   5 参                      ⇒ 非选择性的参数    （= "某个参数没给"）
#   7 参（两个 out_dispatch）   ⇒ 类型不匹配（位置 **6**）（= 第 7 个参数类型错）
#   7 参（out_i4 + out_dispatch）⇒ 无效的参数数目  （= 类型对了、而**个数**仍不对）
#   ```
#   ★ 故本轮**只动第 5 个参数**（`Bodies`）的类型，★ 其余保持上一轮已证对的那套
#     （`out_i4()` + `out_dispatch()`）。
#
#   ★ 试的形态（★ 从"最像官方说的空数组"到"各种 VARIANT 包装"）：
#     ⓐ Python `list`（★ 上轮已试 ⇒ 无效的参数数目）
#     ⓑ `VARIANT(VT_ARRAY|VT_DISPATCH, [])`
#     ⓒ 空 `VARIANT()`（★ 即"没给"）
#     ⓓ `VARIANT(VT_ARRAY|VT_VARIANT, [])`
#     ⓔ `None`
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6）：**特征树多了新特征**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import sys  # noqa: E402

sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

#: ⚠ **修**：`VARIANT` **不在 `pythoncom` 里** —— 本仓用的是 **`win32com.client.VARIANT`
#: **
#:   （★ 轮 522 第一版我 `import pythoncom` 就取 `pythoncom.VARIANT` ⇒ 三组白跑、
#:    ★ 报 `module 'pythoncom' has no attribute 'VARIANT'` —— ★ **那是探针的毛病**）
import pythoncom  # noqa: E402
from win32com.client import VARIANT as _V  # noqa: E402

from scripts import sw_connect as c_  # noqa: E402
from scripts import sw_part as p_  # noqa: E402


def _mk_solid(doc):
    p_.start_sketch(doc, plane_name="Top Plane")
    c_.get_com_member(
        c_.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.03,
        -0.03,
        0.0,
        0.03,
        0.03,
        0.0,
    )
    p_.end_sketch(doc)
    names = [
        n
        for n in (p_.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            p_.extrude_boss(doc, cand, 0.02)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _bodies_variants():
    """★ 返回 [(标签, 值工厂)] —— ★ 工厂每次调都要给**新对象**（★ VARIANT 会复用）。"""
    out = [("list\uff08\u4e0a\u8f6e\u5df2\u8bd5\uff09", lambda: [])]
    try:
        out.append(
            (
                "VARIANT(VT_ARRAY|VT_DISPATCH, [])",
                lambda: _V(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, []),
            )
        )
    except Exception as exc:  # noqa: BLE001
        #: 2026-10-22: `except ... as exc` deletes `exc` at block end, so a lambda
        #: capturing it would raise NameError when called later; bind a local first.
        _bind_err = str(exc)[:60]
        out.append(
            ("VT_ARRAY|VT_DISPATCH 构不出", lambda: ("ERR", _bind_err))
        )
    out.append(("VARIANT()\uff08\u7a7a\uff09", lambda: _V()))
    try:
        out.append(
            (
                "VARIANT(VT_ARRAY|VT_VARIANT, [])",
                lambda: _V(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, []),
            )
        )
    except Exception as exc:  # noqa: BLE001
        #: 2026-10-22: same as above -- bind the message before the except scope ends.
        _bind_var = str(exc)[:60]
        out.append(
            ("VT_ARRAY|VT_VARIANT 构不出", lambda: ("ERR", _bind_var))
        )
    out.append(("None", lambda: None))
    return out


def _one(sw, tag, factory):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = c_.new_document(sw, "part")
        _mk_solid(doc)
        #: \u2605 \u9009\u4e00\u4e2a\u57fa\u51c6\u9762\u4f5c\u5207\u9762\uff08\u2605 \u5
        #: b98\u65b9\uff1apreselected surface or plane\uff09
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        ext = c_.get_com_member(doc, "Extension")
        for plane in ("\u524d\u89c6\u57fa\u51c6\u9762", "Front Plane"):
            try:
                if c_.get_com_member(
                    ext,
                    "SelectByID2",
                    plane,
                    "PLANE",
                    False,
                    0,
                    0.0,
                    0.0,
                    0.0,
                    False,
                    0,
                    None,
                    0,
                ):
                    row["plane"] = plane
                    break
            except Exception:  # noqa: BLE001
                continue
        from sw_connect import out_dispatch as _od
        from sw_connect import out_i4 as _oi4

        fm = c_.get_com_member(doc, "FeatureManager")
        before = list(p_.feature_names(doc) or [])
        try:
            bodies = factory()
            if isinstance(bodies, tuple) and bodies and bodies[0] == "ERR":
                row["err"] = "\u6784\u9020\u5931\u8d25\uff1a%s" % bodies[1]
                return row
            ret = c_.get_com_member(
                fm, "InsertCutSurface", False, 0, False, True, bodies, _oi4(), _od()
            )
            row["returned"] = type(ret).__name__ if ret is not None else "None"
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
            row["code"] = getattr(exc, "args", (None,))[0]
        after = list(p_.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new"])
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(c_.get_com_member(doc, "GetTitle") or "")
                if t:
                    c_.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = c_.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "InsertCutSurface \u7684 **Bodies \u5f62\u6001\u77e9\u9635**\uff08\u2605 \u4e0a\u8f6e\u9519\u7801\u94fe\u7684\u63a8\u8bba\uff09",
        "why": "\u4e0a\u8f6e\uff1a5 \u53c2\u21d2\u975e\u9009\u62e9\u6027 \u00b7 7 \u53c2(2 dispatch)\u21d2\u7c7b\u578b\u4e0d\u5339\u914d\u4f4d\u7f6e6 \u00b7 "
        "7 \u53c2(i4+dispatch)\u21d2\u65e0\u6548\u7684\u53c2\u6570\u6570\u76ee "
        "\u21d2 \u2605 \u53ea\u52a8\u7b2c 5 \u4e2a\u53c2\u6570\uff08Bodies\uff09\u7684\u7c7b\u578b",
        "cases": [],
    }
    for tag, factory in _bodies_variants():
        ev["cases"].append(_one(sw, tag, factory))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = (
        "bodies_variant_works" if ev["passed"] else "all_bodies_variants_fail"
    )
    p = R / "output" / "cut-surface-bodies-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09"
        % (ev["verdict"], ev["passed"], ev["total"])
    )
    for c in ev["cases"]:
        print(
            "  %-36s ok=%-6s \u56de=%-8s new=%s"
            % (c.get("tag"), c.get("ok"), c.get("returned"), c.get("new"))
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
