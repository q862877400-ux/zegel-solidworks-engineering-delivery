"""★ 决定性测量：`HoleWizard5` 在 Depth 之后要 **13** 个 double 还是 **14** 个？

## 已知

- 官方 27 参：`… EndType, Diameter, Depth, Length, Value1..Value12, ThreadClass, RevDir, …`
  ⇒ Depth 之后是 `Length + Value1..Value12` = **13** 个 double。
- 既有实参表写了 **14** 个 `0.0` ⇒ 多一个 ⇒ `ThreadClass` 落到 `RevDir` 的 bool 位
  ⇒ 报 `com_error: (-2147352571, '类型不匹配。', None, 22)`。
- 但这段表在第 26 轮**曾跑成过**（`HoleWzd` 真建出来了）⇒ 必须实测确认，不能只按读文档下结论。

## 本探针

同一份板、同样的射线选面，分别用 13 个与 14 个 `0.0` 调 `HoleWizard5`（27/28 实参），
记录**哪一个建出了特征**。两次都记，不预设答案。

## 只读纪律

每次用新文档；`CommandInProgress`；收尾核文档数。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c_  # noqa: E402
from scripts import sw_hole_features as h_  # noqa: E402
from scripts import sw_part as p_  # noqa: E402
from scripts.sw_connect import get_com_member, open_doc_count  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402
from scripts.sw_feature_readback import feature_names  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 决定性测量）
# 文件:   tools/probe_holewizard_arity.py
# 定位:   按坐标版与选择器版都报「第 22 参类型不匹配」。官方 27 参要求 Depth 后 13 个
#          double，而既有实参表写了 14 个 ⇒ 实测 13 与 14 哪个真能建出特征。
#          第 26 轮那段表曾成功，故不能只按文档下结论，必须两边都真机跑。
# 官方依据: IFeatureManager.HoleWizard5（27 参）· IModelDocExtension.SelectByRay（12 参）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

TOP_Z = 0.020  #: 顶面 z（米）


def _plate(sw):
    doc = c_.new_document(sw, "part")
    p_.start_sketch(doc, plane_name="Front Plane")
    p_.sketch_corner_rectangle(doc, 0.0, 0.0, 100.0, 60.0)
    p_.end_sketch(doc)
    sk = [n for n in (feature_names(doc) or []) if n.startswith("草图")]
    _try(p_.extrude_boss, doc, sk[-1] if sk else "草图1", 20.0)
    return doc


def _ray(doc, x_m, y_m):
    """★ 从 (x,y,顶面) 上方朝 -z 打射线选面（12 参，Mark=0）。"""
    ext = get_com_member(doc, "Extension")
    doc.ClearSelection2(True)
    ok = get_com_member(
        ext, "SelectByRay",
        x_m, y_m, TOP_Z + 0.050,
        0.0, 0.0, -1.0,
        1e-4, int(h_.SW_SEL_FACES), False, 0, 0,
    )
    try:
        n = int(
            get_com_member(
                get_com_member(doc, "SelectionManager"), "GetSelectedObjectCount2", -1
            ) or 0
        )
    except Exception:  # noqa: BLE001
        n = -1
    return ok, n


def _try_variant(sw, zeros: int) -> dict:
    """★ 用 `zeros` 个 0.0 调 HoleWizard5。"""
    doc = _plate(sw)
    out: dict = {"zeros": zeros, "n_args": 7 + zeros + 1 + 6}
    try:
        ok_ray, sel = _ray(doc, 0.010, 0.010)
        out["ray"] = {"ok": ok_ray, "selected": sel}
        before = [str(n) for n in (feature_names(doc) or [])]
        args = (
            [int(h_.SW_WZD_HOLE), int(h_.SW_WZD_ANSI_METRIC), 40, "M8",
             int(h_.SW_END_THROUGH_ALL), 0.008, 0.020]
            + [0.0] * zeros
            + [""] + [False, True, False, False, False, False]
        )
        out["n_args"] = len(args)
        ok_h, ret_h = _try(
            lambda: get_com_member(
                get_com_member(doc, "FeatureManager"), "HoleWizard5", *args
            )
        )
        after = [str(n) for n in (feature_names(doc) or [])]
        out["call_ok"] = ok_h
        out["ret"] = str(ret_h)[:140]
        out["new_features"] = [n for n in after if n not in before]
        out["built"] = bool(out["new_features"])
        return out
    finally:
        _try(sw.CloseDoc, str(_member(doc, "GetTitle") or ""))


def main() -> int:
    ev: dict = {"probe": "holewizard-arity"}
    sw = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        for zeros in (13, 14):
            r = _try_variant(sw, zeros)
            ev["v13" if zeros == 13 else "v14"] = r
            print(
                "zeros=%d（共 %d 实参）⇒ built=%s new=%s %s"
                % (zeros, r["n_args"], r["built"], r["new_features"],
                   "" if r["built"] else r["ret"][:100])
            )
        a = ev.get("v13", {}).get("built")
        b = ev.get("v14", {}).get("built")
        ev["conclusion"] = (
            "★ 13 个能建、14 个不能 ⇒ 官方 27 参为准，既有实参表多了 1 个（应删一个 0.0）"
            if a and not b
            else "★ 14 个能建、13 个不能 ⇒ 本机按 28 参接受（与官方文档不符，按实测）"
            if b and not a
            else "两者都能建" if a and b else "两者都不能建（另找原因）"
        )
        print(ev["conclusion"])
        return 0
    finally:
        if sw is not None:
            ev["docs_left"] = open_doc_count(sw)
            print("收尾后剩余文档数：%s" % ev["docs_left"])
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        (R / "output" / "holewizard-arity.json").write_text(
            json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("证据已写：output/holewizard-arity.json")


if __name__ == "__main__":
    raise SystemExit(main())
