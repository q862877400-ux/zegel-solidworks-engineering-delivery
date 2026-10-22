"""★ 真机验证新增能力 `sw_part.feature_suppress` / `feature_unsuppress`（★ 阶段 5 补的缺口）。

★★ 判据（★ 跑之前写死）：★ **特征被抑制后，`IFeature.IsSuppressed2` 应为 True**
  —— ★ **而"特征树少了"不算判据**（★ 抑制的特征仍在树里，★ 只是带抑制标记）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_feature_suppress_e2e.py
# 定位:   ★ 阶段 5：验证新增的 `sw_part.feature_suppress` / `feature_unsuppress`。
#   官方依据: `C:\\swapi\\types\\IModelDoc2\\EditSuppress2.md` ·
#     `EditUnsuppress2.md` · `IFeature\\IsSuppressed2.md`
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402

OUT = REPO / "output" / "feature-suppress-e2e-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:90]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:180])}


def _is_suppressed(model, name: str):
    """★ 按名字取特征 ⇒ 读它的抑制状态（★ 官方 `IFeature.IsSuppressed2`）。"""
    feat = None
    try:
        feat = _g(model, "FirstFeature")
    except Exception:  # noqa: BLE001
        return None
    hops = 0
    while feat is not None and hops < 80:
        hops += 1
        try:
            if str(_g(feat, "Name") or "") == name:
                for nm in ("IsSuppressed2", "IsSuppressed"):
                    try:
                        return bool(_g(feat, nm))
                    except Exception:  # noqa: BLE001
                        continue
                return None
        except Exception:  # noqa: BLE001
            pass
        try:
            feat = _g(feat, "GetNextFeature")
        except Exception:  # noqa: BLE001
            feat = None
    return None


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        _g(
            _g(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.02,
            -0.015,
            0.0,
            0.02,
            0.015,
            0.0,
        )
        P.end_sketch(doc)
        nm = [n for n in (P.feature_names(doc) or []) if n.startswith("草图")]
        P.extrude_boss(doc, (nm[-1] if nm else "草图1"), 10.0)
        names = [str(x) for x in (P.feature_names(doc) or [])]
        R["特征"] = names[:10]
        target = next(
            (n for n in names if ("拉伸" in n or "Extrude" in n or "凸台" in n)), None
        )
        R["目标"] = target
        R["★_抑制前"] = _is_suppressed(doc, target) if target else None

        #: ★★ 新能力
        R["feature_suppress"] = _try(P.feature_suppress, doc, target)
        R["★_抑制后"] = _is_suppressed(doc, target) if target else None
        R["feature_unsuppress"] = _try(P.feature_unsuppress, doc, target)
        R["★_解除后"] = _is_suppressed(doc, target) if target else None

        #: ★ 负例（★ 事实 62：守卫要能被证伪）—— ★ 给一个**不存在的**特征名
        R["负例_不存在的特征"] = _try(P.feature_suppress, doc, "这个特征不存在_xyz")
    except Exception as exc:  # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
    a, b, c = R.get("★_抑制前"), R.get("★_抑制后"), R.get("★_解除后")
    R["★★_结论"] = (
        "★ PASS —— 抑制前 %s ⇒ 抑制后 %s ⇒ 解除后 %s" % (a, b, c)
        if (a is False and b is True and c is False)
        else "★★ 需人工看 —— 状态序列 %s ⇒ %s ⇒ %s 不是 False→True→False" % (a, b, c)
    )
    R["★_负例拒绝了吗"] = (
        "★★ 否（★ 守卫没生效）"
        if R.get("负例_不存在的特征", {}).get("ok")
        else "★ 是（★ 抛错）✓"
    )
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
