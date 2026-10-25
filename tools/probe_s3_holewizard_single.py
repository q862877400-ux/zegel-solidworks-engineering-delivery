"""★ 单点验证：异型孔向导建一个孔，`hole_params` 能否读到孔型。

## 为什么先单点

第 25 轮查明：E2 的 `孔型` 子项判 `unknown`，根因是**孔是切除-拉伸做的**
（E3 读到 `type=ICE`），而孔型只存在于**异型孔向导**特征的参数里。

要改成异型孔向导，得先回答一个问题：
**在这台机器上，异型孔向导建出来的孔，`hole_params` 到底能不能读到孔型？**

答不出就直接改生成路径 = 拿整条证据链赌一个没验过的前提。

## 本探针只做一件事

```
板 100×60×20  ──「+z」面选择器──> create_hole_wizard_at_selection_report(size='M8')
                                      ↓
                              hole_params 读回
```

## 判据（全部独立读数）

| 读数 | 手段 |
|---|---|
| 特征建出来没有 | `feature_names` 里有没有新特征、`GetTypeName2` 是什么 |
| 孔型读得到吗 | `sw_feature_readback.hole_params` 是否回出 `ThruHoleDiameter` 一类 |
| 孔径对不对 | 上面那个数的口径（米/毫米）要按已知事实 492 一类核对 |

★ 建成但读不到孔型 ⇒ 这条也**不通**（因为 E2 要的就是孔型可读）。
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
from scripts.sw_connect import open_doc_count  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402
from scripts.sw_feature_readback import feature_info, feature_names, hole_params  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 单点验证）
# 文件:   tools/probe_s3_holewizard_single.py
# 定位:   E2 的 `孔型` 子项当前判 unknown（孔是切除-拉伸做的，没有孔型信息）。
#          改成异型孔向导之前，先用**一个孔**验证「建得出 + 孔型读得回」。
#          不先验这个就改生成路径 = 拿整条证据链赌未验前提。
# 官方依据: IFeatureManager.HoleWizard5（27 参，见 sw_hole_features 的来源块）·
#          IModelDocExtension.SelectByRay（经 resolve_face_selector + 射线）·
#          IWizardHoleFeatureData2.ThruHoleDiameter / ThruHoleDepth
#          （经 sw_feature_readback.hole_params；★ 单位口径见该函数 docstring）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    ev: dict = {"probe": "s3-holewizard-single"}
    sw = doc = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = c_.new_document(sw, "part")
        p_.start_sketch(doc, plane_name="Front Plane")
        p_.sketch_corner_rectangle(doc, 0.0, 0.0, 100.0, 60.0)
        p_.end_sketch(doc)
        sk_names = [n for n in (feature_names(doc) or []) if n.startswith("草图")]
        _try(p_.extrude_boss, doc, sk_names[-1] if sk_names else "草图1", 20.0)
        before = [str(n) for n in (feature_names(doc) or [])]
        ev["features_before"] = before
        print("① 板已建：特征 %s" % before)

        #: ② 异型孔向导（面选择器 '+z'）
        ok_h, ret_h = _try(
            h_.create_hole_wizard_at_selection_report,
            doc, "+z", "M8",
        )
        ev["holewizard"] = {"ok": ok_h, "report": str(ret_h)[:400]}
        print("② 异型孔向导：ok=%s" % ok_h)
        if not ok_h:
            print("   report: %s" % str(ret_h)[:300])

        #: ③ 新特征与类型
        after = [str(n) for n in (feature_names(doc) or [])]
        ev["features_after"] = after
        new = [n for n in after if n not in before]
        ev["new_features"] = new
        types = {}
        for n in new:
            info = feature_info(doc, n) or {}
            types[n] = info.get("GetTypeName2")
        ev["new_feature_types"] = types
        print("③ 新特征 %s · 类型 %s" % (new, types))

        #: ④ 孔型能不能读回
        reads = {}
        for n in new:
            okp, prm = _try(hole_params, doc, n)
            reads[n] = prm if okp else "err: %s" % str(prm)[:120]
        ev["hole_params"] = reads
        for n, v in reads.items():
            print("④ %s 的 hole_params：%s" % (n, str(v)[:220]))

        #: 判读：建成 + 类型是 HoleWizard 类 + hole_params 能回出孔径
        is_wizard = any(
            t and any(k in str(t) for k in ("HoleWizard", "Wzd", "Hole"))
            for t in types.values()
        )
        got_dia = any(
            isinstance(v, dict)
            and any("ThruHole" in k or "HoleDiameter" in k for k in v)
            for v in reads.values()
        )
        ev["verdict"] = {
            "created": bool(new),
            "type_names": types,
            "looks_like_wizard": is_wizard,
            "hole_params_readable": got_dia,
        }
        ev["ok"] = bool(new and got_dia)
        ev["conclusion"] = (
            "★ 异型孔向导可用且孔型读得回（类型 %s）⇒ 改生成路径可行"
            % list(types.values())
            if ev["ok"]
            else "★ 未达：建成=%s · 孔型可读=%s ⇒ 见 verdict"
            % (bool(new), got_dia)
        )
        print(ev["conclusion"])
        return 0 if ev["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1200:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if sw is not None:
            if doc is not None:
                t = str(_member(doc, "GetTitle") or "")
                if t:
                    _try(sw.CloseDoc, t)
            ev["docs_left"] = open_doc_count(sw)
            print("   收尾后剩余文档数：%s" % ev["docs_left"])
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s3-holewizard-single.json"
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
