"""★ 真机：**复制实体** —— ★ 入口是 `ISketchManager.RotateOrCopy3DAboutXYZ`（`Copy=True`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_rotate_or_copy_3d.py
# 定位:   ★ 2026-10-03（轮 580）★ 照新纪律（**官方文档是第 0 步** + **铁律 5**）攻台账
#           「复制实体」。
#
#   ★★★★ **而本轮先把那条台账的归因**纠正了****：
# 台账写的是 `IModelDoc2.SketchModifyCopy` —— ★ **而按铁律 5 全接口查：那个名字不存在**
# ⚠
#     （★ `SketchModify` 全族**只有四个**：`Flip` / `Rotate` / `Scale` / `Translate`）
#
# ★★★★★ **而"复制"那半在别处**（★ 全 92 个 `ISketchManager` 成员里含 `Copy` 的只有两条）
# ：
#     ```
#     bool RotateOrCopy3DAboutXYZ(bool **Copy**, int NumCopies, bool KeepRelations,
#                                 double BaseX, double BaseY, double BaseZ,
#                                 double AngleAboutXDir, double AngleAboutYDir, \u2026)
#     bool RotateOrCopy3DAboutVector(bool **Copy**, int NumCopies, bool KeepRelations,
#                                    double BaseX, BaseY, BaseZ, double VectorXCoord, \u2026)
#     ```
# \u2605 \u800c\u5b98\u65b9\u5bf9 `Copy` \u7684\u9010\u5b57\uff1a**"True to copy 3D sket
# ch entities, false to not"** \u2713
#
#   ★ 前置：★ **一个 3D 草图**（★ `ISketchManager.Insert3DSketch`）+ ★ 里面一条线。
#   ★ 判据（★ 规则 6 + 事实 436）：**草图段数增加**（★ 复制一份 ⇒ 段数应变 2）。
# ⚠ 全程走 `tools/sw_guard.py`；★ 三格：`Copy=True` / `Copy=False`（对照：只转不复制）/
# 不选对照。
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

from scripts import sw_connect as C  # noqa: E402


def _seg_count(doc):
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        return len(list(C.get_com_member(sk, "GetSketchSegments") or [])) if sk else -1
    except Exception:  # noqa: BLE001
        return -1


def _one(sw, tag, do_copy):
    row = {"tag": tag, "copy": do_copy, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        sm = C.get_com_member(doc, "SketchManager")
        #: \u2605 **\u5f00\u4e00\u4e2a 3D \u8349\u56fe**
        try:
            C.get_com_member(sm, "Insert3DSketch", True)
            row["sketch3d"] = "Insert3DSketch"
        except Exception as exc:  # noqa: BLE001
            row["sketch3d"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
        #: \u2605 \u91cc\u9762\u753b\u4e00\u6761\u7ebf
        C.get_com_member(sm, "CreateLine", -0.02, 0.0, 0.0, 0.02, 0.0, 0.0)
        before = _seg_count(doc)
        row["seg_before"] = before
        ret = None
        try:
            #: \u2605 **9 \u53c2**\uff08\u2605 **\u53cd\u5c04\u4e0e swapi \u4e24\u6e90\u
            #: 4e00\u81f4**\uff1a`'RotateOrCopy3DAboutXYZ': 9`\uff09\uff1a
            #:   `Copy` \u00b7 `NumCopies` \u00b7 `KeepRelations` \u00b7 `BaseXYZ` \u00b7
            #: `AngleAboutXDir` \u00b7 `AngleAboutYDir` \u00b7 **`AngleAboutZDir`** \u21
            #: 90 \u2605 **\u6211\u7b2c\u4e00\u7248\u6f0f\u4e86\u8fd9\u4e2a**
            #: \u2605 \u800c\u6f0f\u53c2\u6570\u62a5\u7684\u662f `DISP_E_PARAMNOTOPTIONA
            #: L`\uff08`0x8002000F`\uff09
            #: \u2014\u2014 \u2605 **\u5b83\u770b\u4e0d\u51fa\u662f\u54ea\u4e2a\u53c2\u6
            #: 570\u6f0f\u4e86** \u26a0
            ret = C.get_com_member(
                sm,
                "RotateOrCopy3DAboutXYZ",
                bool(do_copy),
                1,
                True,
                0.0,
                0.0,
                0.0,
                0.7853981633974483,
                0.0,
                0.0,
            )
            row["returned"] = str(ret)
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = _seg_count(doc)
        row["seg_after"] = after
        row["new_segments"] = (after - before) if (after >= 0 and before >= 0) else None
        row["ok"] = bool(row["new_segments"] and row["new_segments"] > 0)
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
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
        "_": "\u590d\u5236\u5b9e\u4f53\uff1a`ISketchManager.RotateOrCopy3DAboutXYZ`\uff08\u2605 **\u7b2c\u4e00\u53c2 `Copy`**\uff09",
        "official": "\u53f0\u8d26\u5199\u7684 `SketchModifyCopy` **\u5168\u63a5\u53e3\u67e5\u4e0d\u5230**\uff08\u94c1\u5f8b 5\uff09\uff1b"
        "\u800c `ISketchManager` \u91cc\u542b `Copy` \u7684\u53ea\u6709 `RotateOrCopy3DAboutXYZ` / `AboutVector`\uff0c"
        '\u2605 \u5b98\u65b9\u5bf9 `Copy` \u7684\u9010\u5b57\uff1a"True to copy 3D sketch entities"',
        "cases": [],
    }
    ev["cases"].append(
        _one(sw, "\u2605 `Copy=True`\uff08\u2605 \u590d\u5236\uff09", True)
    )
    ev["cases"].append(
        _one(
            sw,
            "\u5bf9\u7167\uff1a`Copy=False`\uff08\u2605 \u53ea\u65cb\u8f6c\u3001\u4e0d\u590d\u5236\uff09",
            False,
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = (
        "rotate_or_copy_works" if ev["cases"][0].get("ok") else "rotate_or_copy_fails"
    )
    p = R / "output" / "rotate-or-copy-3d-evidence.json"
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
            "  %-40s ok=%-6s \u6bb5 %s \u2192 %s\uff08\u589e %s\uff09\u56de=%s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("seg_before"),
                c.get("seg_after"),
                c.get("new_segments"),
                c.get("returned"),
            )
        )
        if c.get("sketch3d"):
            print("        3D \u8349\u56fe\uff1a%s" % c.get("sketch3d"))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
