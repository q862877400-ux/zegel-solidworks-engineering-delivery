"""★ S3 测量探针：把三个「未查明」量准，不猜。

## 要量的三件事（上一轮 R-19 的「未确认」）

| # | 问题 | 怎么量 |
|---|---|---|
| 1 | `SetSystemValue3` 吃**米**还是**文档单位**？ | 直接写一个已知值（0.15），再看 `SystemValue` 与包围盒 |
| 2 | `GetSystemValue3` 的正确调用形状？ | 按官方 `(WhichConfigurations, Config_names)` 传 `(1, None)` |
| 3 | 可用的包围盒读法？ | `IPartDoc.GetBodies2(0, True)` → `IBody2.GetBodyBox()` |

## 官方依据（铁律 4，逐字）

- `types/IDimension/SetSystemValue3.md`：
  「Sets the value of this dimension in **system units (meters)** in the specified configuration.」
  `System.int SetSystemValue3(System.double NewValue, System.int WhichConfigurations, System.object Config_names)`
- `types/IDimension/GetSystemValue3.md`：
  「Gets the value of the current dimension in **system units** in the named configuration.」
  `System.object GetSystemValue3(System.int WhichConfigurations, System.object Config_names)`
  Returns「**Array of doubles** of the dimension values in system units」
- `types/IPartDoc/GetBodies2.md`：`System.object GetBodies2(System.int BodyType, System.bool BVisibleOnly)`
  ⚠ **两个参数都是必填** —— 只传一个会报「非选择性的参数」
- `types/IBody2/GetBodyBox.md`：`System.object GetBodyBox()`，Returns「Array of 6 doubles」
- `swBodyType_e.swSolidBody = 0`；`swInConfigurationOpts_e.swThisConfiguration = 1`

## ★ 本探针的判据（不靠自报）

先写 `0.15`（**米** = 150 mm），再回读**包围盒 X 跨度**：
- 若变成 ≈150 mm ⇒ `SetSystemValue3` **吃米**（官方说法成立）
- 若变成 ≈0.15 mm ⇒ 它吃文档单位（毫米），官方说法与本机不符

★ 两种结果都照样记录，**不预设答案**。

## 只读

建临时文档；`CommandInProgress` 抑制弹窗；收尾关掉**自己开的**文档。
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
from scripts import sw_part as p_  # noqa: E402
from scripts.sw_connect import get_com_member  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_feature_readback import feature_names  # noqa: E402
from scripts.sw_sketch import active_sketch as _active_sketch  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_s3_dimension_units.py
# 定位:   量准 R-19 的三项「未确认」：SetSystemValue3 的单位、GetSystemValue3 的
#          调用形状、可用的包围盒读法。★ 是**测量**，不是修 —— 不预设答案。
# 官方依据: IDimension.SetSystemValue3 / GetSystemValue3、
#           IPartDoc.GetBodies2（两参必填）、IBody2.GetBodyBox、
#           swBodyType_e.swSolidBody=0、swInConfigurationOpts_e.swThisConfiguration=1
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SW_SOLID_BODY = 0
SW_THIS_CONFIG = 1


def _dims(doc) -> list:
    """★ 遍历草图特征上的显示尺寸（迭代用 `IDisplayDimension.GetNext2`）。"""
    out: list = []
    for nm in feature_names(doc):
        if not (nm.startswith("草图") or nm.lower().startswith("sketch")):
            continue
        ok_f, feat = _try(get_com_member, doc, "FeatureByName", nm)
        if not ok_f or feat is None:
            continue
        ok_d, dd = _try(get_com_member, feat, "GetFirstDisplayDimension")
        if not ok_d or dd is None:
            continue
        guard = 0
        while dd is not None and guard < 50:
            guard += 1
            ok_dim, dim = _try(get_com_member, dd, "GetDimension")
            if ok_dim and dim is not None:
                row = {"sketch": nm}
                ok_n, full = _try(lambda: str(dim.FullName))
                row["full_name"] = full if ok_n else ""
                ok_sv, sv = _try(lambda: float(dim.SystemValue))
                row["SystemValue"] = sv if ok_sv else None
                #: ★ 官方形状：(WhichConfigurations=1, Config_names=空) ⇒ 回数组
                ok_g3, g3 = _try(get_com_member, dim, "GetSystemValue3", SW_THIS_CONFIG, None)
                if ok_g3:
                    try:
                        row["GetSystemValue3"] = [float(v) for v in list(g3)]
                    except (TypeError, ValueError):
                        row["GetSystemValue3"] = str(g3)[:60]
                else:
                    row["GetSystemValue3"] = "失败: %s" % str(g3)[:60]
                out.append(row)
            ok_next, nxt = _try(get_com_member, dd, "GetNext2")
            dd = nxt if ok_next else None
    return out


def _bbox(doc) -> dict:
    """★ 包围盒：`GetBodies2(0, True)` → `GetBodyBox()`（**两参必填**）。"""
    out: dict = {"ok": False}
    ok, body = _try(get_com_member, doc, "GetBodies2", SW_SOLID_BODY, True)
    if not ok or not body:
        out["error"] = "GetBodies2: %s" % str(body)[:100]
        return out
    try:
        b = body[0] if isinstance(body, (list, tuple)) else list(body)[0]
    except (IndexError, TypeError):
        out["error"] = "GetBodies2 回空"
        return out
    ok2, box = _try(get_com_member, b, "GetBodyBox")
    if not ok2 or not box:
        out["error"] = "GetBodyBox: %s" % str(box)[:100]
        return out
    nums = [float(v) for v in list(box)]
    if len(nums) < 6:
        out["error"] = "GetBodyBox 只回 %d 个数" % len(nums)
        return out
    out.update(
        {
            "ok": True,
            "x_mm": round((nums[3] - nums[0]) * 1000.0, 6),
            "y_mm": round((nums[4] - nums[1]) * 1000.0, 6),
            "z_mm": round((nums[5] - nums[2]) * 1000.0, 6),
            "raw": nums,
        }
    )
    return out


def main() -> int:
    ev: dict = {"probe": "s3-dimension-units", "steps": []}
    sw = doc = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = c_.new_document(sw, "part")

        #: 文档单位
        ok_u, units = _try(get_com_member, doc, "GetUnits")
        ev["GetUnits"] = [int(v) for v in list(units)][:8] if ok_u and units else str(units)[:80]

        #: 建 100×60 矩形 + AutoDimension2
        p_.start_sketch(doc, plane_name="Front Plane")
        p_.sketch_corner_rectangle(doc, 0.0, 0.0, 100.0, 60.0)
        sk = _active_sketch(doc)
        ok_ad, ret_ad = _try(
            lambda: get_com_member(sk, "AutoDimension2", 1, 1, -1, 1, -1)
        )
        ev["AutoDimension2"] = {"ok": ok_ad, "ret": str(ret_ad)[:60]}
        ev["status_after_dims"] = _try(lambda: int(sk.GetConstrainedStatus))[1]

        #: ★ 必须**退出草图并拉伸**才有实体 ——
        #:   `GetBodies2` 在只有草图时回 None（上一版就卡在这）。
        ok_end, ret_end = _try(p_.end_sketch, doc)
        ev["end_sketch"] = {"ok": ok_end, "ret": str(ret_end)[:60]}
        sk_names = [
            n for n in feature_names(doc)
            if n.startswith("草图") or n.lower().startswith("sketch")
        ]
        ok_ex, ret_ex = _try(p_.extrude_boss, doc, sk_names[-1] if sk_names else "草图1", 20.0)
        ev["extrude"] = {"ok": ok_ex, "ret": str(ret_ex)[:80]}

        #: ① 初始读数（三件一起）
        ev["before"] = {"dims": _dims(doc), "bbox": _bbox(doc)}
        ev["steps"].append({"step": "before", "bbox": ev["before"]["bbox"]})

        #: ② 找宽度尺寸，直接写 **0.15**（米 = 150 mm）
        dims = ev["before"]["dims"]
        target = next((d for d in dims if d.get("full_name")), None)
        ev["target"] = target
        if target:
            ok_lookup, dim = _try(get_com_member, doc, "Parameter", target["full_name"])
            ev["Parameter_lookup"] = {"ok": ok_lookup, "detail": str(dim)[:80]}
            if ok_lookup and dim is not None:
                ok_set, st = _try(
                    lambda: int(
                        get_com_member(dim, "SetSystemValue3", 0.15, SW_THIS_CONFIG, None)
                    )
                )
                ev["SetSystemValue3"] = {"ok": ok_set, "return": st if ok_set else str(st)[:100]}
                _try(get_com_member, doc, "EditRebuild3")

                #: ③ 写完再读三件
                ev["after"] = {"dims": _dims(doc), "bbox": _bbox(doc)}
                ev["steps"].append({"step": "after", "bbox": ev["after"]["bbox"]})

        #: ④ 判读：写 0.15 之后包围盒 X 是多少
        b0 = (ev.get("before") or {}).get("bbox") or {}
        b1 = (ev.get("after") or {}).get("bbox") or {}
        ev["bbox_before_x_mm"] = b0.get("x_mm")
        ev["bbox_after_x_mm"] = b1.get("x_mm")
        verdict = "未量到"
        if b0.get("ok") and b1.get("ok"):
            x0, x1 = b0["x_mm"], b1["x_mm"]
            if abs(x1 - 150.0) < 1.0:
                verdict = "★ SetSystemValue3 吃**米**（写 0.15 ⇒ 150 mm），与官方一致"
            elif abs(x1 - 0.15) < 0.01:
                verdict = "★★ SetSystemValue3 吃**文档单位(毫米)**（写 0.15 ⇒ 0.15 mm）"
            else:
                verdict = "★ 两者都不符：写 0.15 之后 X = %.6f mm（前 %.6f）" % (x1, x0)
        ev["verdict"] = verdict
        ev["ok"] = b0.get("ok") and b1.get("ok") is not None
        print("★ 单位判读：", verdict)
        print("  包围盒前:", json.dumps(b0, ensure_ascii=False)[:120])
        print("  包围盒后:", json.dumps(b1, ensure_ascii=False)[:120])
        print("  SetSystemValue3 返回:", json.dumps(ev.get("SetSystemValue3"), ensure_ascii=False))
        return 0
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1500:]
        print("★ 失败：", ev["err"])
        print(ev["traceback"])
        return 1
    finally:
        if sw is not None and doc is not None:
            try:
                sw.CloseDoc(doc.GetTitle())
            except Exception:  # noqa: BLE001
                pass
        if sw is not None:
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s3-dimension-units.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
