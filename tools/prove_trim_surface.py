"""★ 真机：**剪裁曲面**（`IFeatureManager.PreTrimSurface` + `PostTrimSurface` · 两段式）—— B6/T607。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_trim_surface.py
# 定位:   ★ 2026-10-03（轮 519）★ 给 `sw_surface_features.trim_surface_report` 留真机
#           证据。
#
#   ★★ **T607 的真名是上一轮（518）才找到的**：
#     · 轮 516/518 我按 `InsertTrimSurface` 查 ⇒ **swapi 里查不到**（★ 当时按铁律 5 记了）
#     · 轮 518 从**类型库 dump** 发现 `IModelDoc2` 上有 `PreTrimSurface` / `PostTrimSurface`
#     ⇒ ★★ **故真名是这一对**（**两段式**）✓
#     ⚠ **教训（★ 值得记）**：铁律 5 的「查不到」应当**限定在查过的名字**上 ——
#       我查的是**猜的名字**，★ 而**没有穷举** `TrimSurface` 那一族。
#
#   ★ 三源分工（★ 铁律 4 的典型实例）：
#     · swapi md ⇒ 只有签名，★ 四个参数**全是 `No description`** ⚠
# · **CHM** ⇒ ★★ 逐字给了四个参数的语义（mutual / splitSystem / splitLinear / removePick
# ed）
#       + PostTrimSurface 的 sew
# · **类型库** ⇒ arity 与方向：`IFeatureManager.PreTrimSurface` 有 **4 个 in** + `Retval
# `
#       （★ 而 `IModelDoc2` 那两个各**只有 1 个 in** ⇒ ★ 新版更全、本探针走新版）
#
#   ★ 前置：★ **两张相交曲面**（★ 一张被剪、一张作工具）。
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

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_surface_features as sf  # noqa: E402


def _mk_two_crossing_surfaces(doc):
    """★ 两张**相交**的曲面：★ 前视面拉一张（沿 Z 长）、★ 上视面拉一张（沿 Y 长）⇒ 它们在空间里交叉。"""
    made = 0
    for i, (plane, rect) in enumerate(
        (
            ("Front Plane", (-0.02, -0.02, 0.02, 0.02)),
            ("Top Plane", (-0.02, -0.01, 0.02, 0.01)),
        )
    ):
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        P.start_sketch(doc, plane_name=plane)
        C.get_com_member(
            C.get_com_member(doc, "SketchManager"),
            "CreateCornerRectangle",
            rect[0],
            rect[1],
            0.0,
            rect[2],
            rect[3],
            0.0,
        )
        P.end_sketch(doc)
        names = [
            n
            for n in (P.feature_names(doc) or [])
            if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
        ]
        for cand in ((names[-1],) + tuple(names) + ("\u8349\u56fe%d" % (i + 1),))[:4]:
            try:
                if sf.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get(
                    "ok"
                ):
                    made += 1
                    break
            except Exception:  # noqa: BLE001
                continue
    return made


def _run(sw, tag, fn):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["made"] = _mk_two_crossing_surfaces(doc)
        r = fn(doc)
        row["result"] = {k: v for k, v in (r or {}).items() if k != "\u2605"}
        row["ok"] = bool((r or {}).get("ok"))
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
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
        "_": "\u526a\u88c1\u66f2\u9762\uff1a`IFeatureManager.PreTrimSurface` + `PostTrimSurface`\uff08\u4e24\u6bb5\u5f0f\uff09",
        "why": "T607 \u7684**\u771f\u540d**\u662f\u4e0a\u4e00\u8f6e\u624d\u4ece\u7c7b\u578b\u5e93\u91cc\u627e\u5230\u7684"
        "\uff08`InsertTrimSurface` \u67e5\u4e0d\u5230\uff09",
        "cases": [],
    }
    ev["cases"].append(
        _run(
            sw,
            "\u2605 mutual=True\uff08\u4ea4\u9762\u4e92\u526a\uff09",
            lambda d: sf.trim_surface_report(d, mutual=True, split_system=True),
        )
    )
    ev["cases"].append(
        _run(
            sw,
            "\u2605 mutual=False\uff08standard\uff09",
            lambda d: sf.trim_surface_report(d, mutual=False, split_system=True),
        )
    )
    ev["cases"].append(
        _run(
            sw,
            "\u2605 mutual=True + sew=True",
            lambda d: sf.trim_surface_report(d, mutual=True, sew=True),
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "trim_surface_works" if ev["passed"] else "trim_surface_fails"
    p = R / "output" / "trim-surface-evidence.json"
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
        r = c.get("result") or {}
        print(
            "  %-30s ok=%-6s \u9762\u5efa\u4e86 %s"
            % (c.get("tag"), c.get("ok"), c.get("made"))
        )
        if r:
            print(
                "        new=%-22s sel=%-4s pre=%s post=%s"
                % (
                    r.get("new_features"),
                    r.get("faces_selected"),
                    r.get("pre_returned"),
                    r.get("post_returned"),
                )
            )
            if r.get("error"):
                print("        err=%s" % str(r["error"])[:120])
        if c.get("err"):
            print("        ERR=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
