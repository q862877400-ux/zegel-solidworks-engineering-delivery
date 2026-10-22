"""★ 确认那个体是不是**焊件特征** —— 用 `IModelDoc2.FirstFeature`（属性）+ `GetTypeName2`。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机诊断）。规格 `specs/202-user-coverage-gaps` 的 **R3 收口**。
# 文件:   tools/diag_weldment_feature_kind.py
# 定位:   ★★ 上一轮逐面矩阵已证明「不是选面问题」（6 张面全回 None）。★ 下一个变量是
#   「**那个体到底是不是焊件特征**」—— 顶端盖只对焊件构件有意义。
#   ★ 我前两次都没读出来：第一次用了**不存在的成员** `GetFirstFeature`；
#     第二次想改它时**我的 shell 引号坏了、替换没生效**。
#   ★ 正确做法逐字来自 `scripts/sw_feature_readback.py` 的来源块：
#     「`IModelDoc2.FirstFeature` / `IFeature.GetNextFeature`（遍历特征树按名找）」
#     以及「用 `GetTypeName2` 判它有没有特征类型（**结构性判据**，与 UI 语言无关）」。
# 官方依据: `c:\swapi\types\IFeatureManager\InsertEndCapFeature3.md`（Remarks「end faces
# 」）
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

from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as p  # noqa: E402

OUT = REPO / "output" / "weldment-feature-kind-evidence.json"


def _g(o, n, *a):
    return c.get_com_member(o, n, *a)


def _walk(doc, limit=40):
    """★ 正确的特征树遍历 —— `FirstFeature` 是**属性**，不是 `GetFirstFeature`。"""
    out = []
    feat = _g(doc, "FirstFeature")
    while feat is not None and len(out) < limit:
        row = {}
        for k, m in (("name", "Name"), ("type", "GetTypeName2")):
            try:
                row[k] = str(_g(feat, m) or "")
            except Exception as exc:  # noqa: BLE001
                row[k] = "<%s>" % type(exc).__name__
        out.append(row)
        try:
            feat = _g(feat, "GetNextFeature")
        except Exception:  # noqa: BLE001
            break
    return out


def _profile():
    for root in (r"c:\ProgramData\SOLIDWORKS", r"c:\ProgramData\SolidWorks"):
        for h in sorted(Path(root).rglob("*.sldlfp")):
            if "weldment profiles" in str(h).lower():
                return str(h)
    return ""


def main() -> int:
    started = time.time()
    r_: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = c.new_document(sw, "part")
        p.start_sketch(doc, plane_name="Front Plane")
        _g(_g(doc, "SketchManager"), "CreateLine", -0.08, 0.0, 0.0, 0.08, 0.0, 0.0)
        p.end_sketch(doc)
        names = [
            n
            for n in (p.feature_names(doc) or [])
            if n.startswith("草图") or n.lower().startswith("sketch")
        ]
        r_["sketch"] = names[-1] if names else "草图1"
        r_["tree_before"] = _walk(doc)
        from scripts.sw_weldment import create_structural_member_from_sketch

        sm = create_structural_member_from_sketch(
            doc, sketch_name=r_["sketch"], profile_path=_profile()
        )
        r_["sm_ok"] = bool(isinstance(sm, dict) and sm.get("ok"))
        if isinstance(sm, dict):
            r_["sm_keys"] = sorted(sm)
        r_["tree_after"] = _walk(doc)
        r_["types_after"] = sorted(
            {t.get("type", "") for t in r_["tree_after"] if t.get("type")}
        )
        r_["is_weldment"] = any(
            "weld" in (t.get("type", "") or "").lower() for t in r_["tree_after"]
        )
        r_["bodies"] = len(list(_g(doc, "GetBodies2", 0, True) or []))
    except Exception as exc:  # noqa: BLE001
        r_["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
    r_["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(r_, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
