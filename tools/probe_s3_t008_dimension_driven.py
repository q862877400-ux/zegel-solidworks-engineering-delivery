"""★ S3 T008：把板件做成尺寸驱动 —— 用**可行的**那两个入口。

## ★★ 为什么不用 `AddDimension2` / `AddHorizontalDimension2`

`docs/dead-ends.md` 已把它们记为**走死的路**（轮 400 / 153 / 154 / 155）：

> 两条真缺口试过而未攻下：① `add_dimension` —— 单位已查清（官方叫米）、
> 前置已做（先选中实体），而选中 **2 条边**后 `AddDimension2` **仍回 None**

> 累计 **6 种选法全部失败** …… 卡点查明：`IEntity.Select4` **没有 mark 参数**
> （选完 mark 仍是 0），而 `SelectByID2` 需要**名字**、**边与草图段都没有名字**。

★★ 本轮我**先没扫 dead-ends 就去试 `AddHorizontalDimension2`**，实测它在本机
   **直接把 SolidWorks 崩掉**（`RPC 服务器不可用`）—— 比记载的更糟。这是流程错误，
   已记入报告。**结论不变：这条路不走。**

## 本探针走哪两条

| # | 入口 | 依据 |
|---|---|---|
① 首选：`ISketchManager.FullyDefineSketch(...)`
② 退回：`ISketch.AutoDimension2(1, 1, -1, 1, -1)`

`FullyDefineSketch` 签名（官方逐字，10 参）：

```
int FullyDefineSketch(bool EntitiesToFullyDefine, bool UseRelations,
                      int RelationsToApply, bool UseDimensions,
                      int HorizontalDimScheme, object HorizontalDatumDisp,
                      int VerticalDimScheme, object VerticalDatumDisp,
                      int HorizontalDimPlacement, int VerticalDimPlacement)
```

⚠ 既有证据记的是「`FullyDefineSketch(11 参)` → 无效的参数数目」——
  说明那次数错了参数；官方是 **10 个**。

## 验证什么

① 矩形建好后 `GetConstrainedStatus()` 期望 **2**（欠约束）
② 加尺寸后期望 **3**（完全定义）且**尺寸数 ≥ 2**
③ 用 `update_dimension_mm` 把宽度改成 120 ⇒ 回读包围盒 X 跨度**变大**

## 只读

建临时文档；收尾关掉**自己开的**文档。`CommandInProgress` 抑制弹窗（铁律 2）。
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
from scripts.sw_feature_readback import feature_names  # noqa: E402
from scripts.sw_sketch import active_sketch as _active_sketch  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_s3_t008_dimension_driven.py
# 定位:   specs/350-first-part-delivery T008 —— 板件做成尺寸驱动并验证
#          「改尺寸 → 几何变」。★ 明确**不走** AddDimension2 那条死路
#          （docs/dead-ends.md 轮 400/153/154/155）。
# 官方依据: ISketchManager.FullyDefineSketch（10 参，官方指向它）；
#           ISketch.AutoDimension2（Obsolete，但既有真机证据证其可用）；
#           IDisplayDimension.GetNext2（遍历显示尺寸的正确入口）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

#: ★ `swAutodimEntities_e.swAutodimEntitiesAll` —— 给草图上全部受支持实体加尺寸
ENTITIES_ALL = 1
#: ★ `swAutodimScheme_e.swAutodimSchemeBaseline`
SCHEME_BASELINE = 1
#: ★ 放置值 -1（既有证据用的就是它，实测能成）
PLACEMENT_DEFAULT = -1

#: ★ 包围盒读不到时的错误详情（供证据 JSON 用）
_bbox_error = ""


def _try(fn, *a):
    try:
        return True, fn(*a)
    except Exception as exc:  # noqa: BLE001
        return False, "%s: %s" % (type(exc).__name__, str(exc)[:140])


def _status(doc):
    ok, sk = _try(_active_sketch, doc)
    if not ok or sk is None:
        return None
    ok2, val = _try(lambda: int(sk.GetConstrainedStatus))
    return val if ok2 else None


def _dimensions(doc) -> list:
    """★ 遍历草图特征上的显示尺寸。迭代用 `IDisplayDimension.GetNext2`。"""
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
        while dd is not None and guard < 100:
            guard += 1
            ok_dim, dim = _try(get_com_member, dd, "GetDimension")
            if ok_dim and dim is not None:
                ok_n, full = _try(lambda: str(dim.FullName))
                ok_v, sysval = _try(lambda: float(dim.SystemValue))
                out.append(
                    {
                        "sketch": nm,
                        "full_name": full if ok_n else "",
                        "value_mm": round(sysval * 1000.0, 6) if ok_v else None,
                    }
                )
            ok_next, nxt = _try(get_com_member, dd, "GetNext2")
            dd = nxt if ok_next else None
    return out


def _bbox_x_mm(doc):
    """★ 回读包围盒 X 跨度（毫米）。

    ★ 两条路都试，**都失败才回 None**（并把错误留在 `_bbox_error` 里）：
      ① `IPartDoc.GetBodies2(True)` → `IBody2.GetBodyBox()`  ← 首选
      ② `IModelDocExtension.GetBox()`
    ⚠ 上一版只用 ②，实测回 None ⇒ 判据把「读不到」误报成「几何没动」。
    """
    global _bbox_error
    errs = []

    ok, body = _try(get_com_member, doc, "GetBodies2", True)
    if ok and body:
        try:
            b = body[0] if isinstance(body, (list, tuple)) else list(body)[0]
        except (IndexError, TypeError):
            b = None
        if b is not None:
            ok2, box = _try(get_com_member, b, "GetBodyBox")
            if ok2 and box:
                nums = [float(v) for v in list(box)]
                if len(nums) >= 6:
                    return round((nums[3] - nums[0]) * 1000.0, 6)
                errs.append("GetBodyBox 只回 %d 个数" % len(nums))
            else:
                errs.append("IBody2.GetBodyBox: %s" % str(box)[:80])
        else:
            errs.append("GetBodies2 回空数组")
    else:
        errs.append("IPartDoc.GetBodies2: %s" % str(body)[:80])

    ok3, ext = _try(get_com_member, doc, "Extension")
    if ok3 and ext is not None:
        ok4, box2 = _try(get_com_member, ext, "GetBox")
        if ok4 and box2:
            nums = [float(v) for v in list(box2)]
            if len(nums) >= 6:
                return round((nums[3] - nums[0]) * 1000.0, 6)
            errs.append("Extension.GetBox 只回 %d 个数" % len(nums))
        else:
            errs.append("IModelDocExtension.GetBox: %s" % str(box2)[:80])
    else:
        errs.append("取 Extension 失败: %s" % str(ext)[:80])

    _bbox_error = " | ".join(errs)
    return None


def _add_dims(doc, sk) -> dict:
    """★ 先试后继 `FullyDefineSketch(10 参)`，失败再退 `AutoDimension2`。"""
    res: dict = {}

    #: ① 后继：FullyDefineSketch —— UseDimensions=True 才算「尺寸驱动」
    ok, ret = _try(
        lambda: get_com_member(
            doc.SketchManager,
            "FullyDefineSketch",
            True,               # EntitiesToFullyDefine
            True,               # UseRelations
            -1,                 # RelationsToApply
            True,               # UseDimensions  ← 关键：要尺寸
            SCHEME_BASELINE,    # HorizontalDimScheme
            None,               # HorizontalDatumDisp
            SCHEME_BASELINE,    # VerticalDimScheme
            None,               # VerticalDatumDisp
            PLACEMENT_DEFAULT,  # HorizontalDimPlacement
            PLACEMENT_DEFAULT,  # VerticalDimPlacement
        )
    )
    res["fully_define_sketch"] = {"ok": ok, "ret": str(ret)[:120]}
    res["dims_after_fds"] = len(_dimensions(doc))
    if ok and res["dims_after_fds"] >= 1:
        res["used"] = "FullyDefineSketch"
        return res

    #: ② 退回：AutoDimension2（Obsolete 但有既有真机证据）
    ok2, ret2 = _try(
        lambda: get_com_member(
            sk,
            "AutoDimension2",
            ENTITIES_ALL,
            SCHEME_BASELINE,
            PLACEMENT_DEFAULT,
            SCHEME_BASELINE,
            PLACEMENT_DEFAULT,
        )
    )
    res["auto_dimension2"] = {"ok": ok2, "ret": str(ret2)[:120]}
    res["dims_after_autodim"] = len(_dimensions(doc))
    res["used"] = "AutoDimension2" if ok2 else "(都失败)"
    return res



def _unit_probe(doc) -> dict:
    """★ 量准单位：文档长度单位 + 同一条尺寸的三种读法。

    ★ 为什么要这个：上一轮三处读数互相不一致 ——
      `IDimension.SystemValue × 1000` 给 120000、`update_dimension_mm` 的
      `after_mm` 给 120.0、而需求是 120。⇒ 不猜，**把三种读法同时记下来**。

    只读，不改模型。
    """
    out: dict = {}
    #: ① 文档长度单位（`IModelDoc2.GetUnits` → `System.int`，含小数位与单位枚举）
    ok_u, units = _try(get_com_member, doc, "GetUnits")
    if ok_u and units:
        out["GetUnits_raw"] = [int(v) for v in list(units)][:8]
    else:
        out["GetUnits_raw"] = "取不到: %s" % str(units)[:80]

    #: ② 每个尺寸：`SystemValue` / `GetSystemValue3` / `FullName`
    rows = []
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
                #: ★ 这正是 `update_dimension_mm` 用的读法（文档单位）
                ok_g3, g3 = _try(get_com_member, dim, "GetSystemValue3", 0, None)
                row["GetSystemValue3"] = g3 if ok_g3 else str(g3)[:80]
                rows.append(row)
            ok_next, nxt = _try(get_com_member, dd, "GetNext2")
            dd = nxt if ok_next else None
    out["dimension_readings"] = rows
    return out


def main() -> int:
    ev: dict = {"probe": "s3-t008-dimension-driven", "steps": []}
    sw = doc = None
    code = 1
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        #: ★ 铁律 2：抑制模态框
        try:
            sw.CommandInProgress = True
            ev["command_in_progress"] = True
        except Exception as exc:  # noqa: BLE001
            ev["command_in_progress"] = str(exc)[:80]
        doc = c_.new_document(sw, "part")

        #: ① 建 100×60 矩形
        p_.start_sketch(doc, plane_name="Front Plane")
        p_.sketch_corner_rectangle(doc, 0.0, 0.0, 100.0, 60.0)
        sk = _active_sketch(doc)
        ev["status_after_rectangle"] = _status(doc)
        ev["dims_after_rectangle"] = len(_dimensions(doc))
        ev["steps"].append(
            {
                "step": "rectangle",
                "status": ev["status_after_rectangle"],
                "dims": ev["dims_after_rectangle"],
            }
        )

        #: ② 加尺寸（挑可行入口）
        ev["add_dims"] = _add_dims(doc, sk)
        ev["status_after_dims"] = _status(doc)
        dims = _dimensions(doc)
        ev["dimensions"] = dims
        ev["dimension_count"] = len(dims)
        ev["steps"].append(
            {
                "step": "add_dims",
                "used": ev["add_dims"].get("used"),
                "status": ev["status_after_dims"],
                "dims": len(dims),
            }
        )

        #: ③ 改宽度 100 → 120，回读几何
        ev["units_before_update"] = _unit_probe(doc)
        ev["bbox_x_before_mm"] = _bbox_x_mm(doc)
        width_dim = next(
            (x for x in dims if abs((x["value_mm"] or 0.0) - 100.0) < 0.5), None
        )
        ev["width_dimension"] = width_dim
        if width_dim and width_dim["full_name"]:
            from scripts.sw_document_data import update_dimension_mm

            ok_u, upd = _try(update_dimension_mm, doc, width_dim["full_name"], 120.0)
            ev["update_width"] = {"ok": ok_u, "detail": str(upd)[:200]}
            #: ★ 交叉验证 ①：尺寸值回读（不依赖包围盒）
            dims_after = _dimensions(doc)
            ev["dimensions_after_update"] = dims_after
            same = next(
                (x for x in dims_after if x["full_name"] == width_dim["full_name"]),
                None,
            )
            ev["width_after_mm"] = same["value_mm"] if same else None
            #: ★ 交叉验证 ②：包围盒
            ev["bbox_x_after_mm"] = _bbox_x_mm(doc)
            ev["bbox_error"] = _bbox_error
            #: ★ 改完再量一次单位与三种读法 —— 这是判「到底是单位错还是几何没动」的关键
            ev["units_after_update"] = _unit_probe(doc)
            ev["steps"].append(
                {
                    "step": "update_width",
                    "ok": ok_u,
                    "bbox_after": ev["bbox_x_after_mm"],
                }
            )
        else:
            ev["update_width"] = {
                "ok": False,
                "detail": "没有值≈100mm 的尺寸 ⇒ 无法验证改宽度",
            }

        #: ④ 总判
        bbox_grew = (
            ev.get("bbox_x_before_mm") is not None
            and ev.get("bbox_x_after_mm") is not None
            and ev["bbox_x_after_mm"] > ev["bbox_x_before_mm"] + 1.0
        )
        #: ★ 尺寸值确实变了 ⇒ 改「生效」了（即使包围盒读不到）
        #:   ⚠ 不用 `IDimension.SystemValue` 当依据 —— 实测它 `SetSystemValue3` 之后
        #:     回的数值与文档单位不一致（三种读法互不相同）。用它做判据会误判。
        #: ★★ 判「改尺寸生效了吗」只能用**独立读数**，不能信可疑组件的自我报告。
        #:   实测到的问题：`update_dimension_mm` 自报 success，而 `IDimension.SystemValue`
        #:   从 0.1（=100mm，米制正确）跳到 120.0（应为 0.12）——**放大了 1000 倍**。
        #:   ⇒ 它自己的 `after` 与请求一致，恰恰是可疑之处，不能当证据。
        before_sv = next(
            (
                r.get("SystemValue")
                for r in ((ev.get("units_before_update") or {}).get("dimension_readings") or [])
                if r.get("full_name")
            ),
            None,
        )
        after_sv = next(
            (
                r.get("SystemValue")
                for r in ((ev.get("units_after_update") or {}).get("dimension_readings") or [])
                if r.get("full_name")
            ),
            None,
        )
        #: 期望：100mm → 120mm ⇒ SystemValue（米制）应 0.1 → **0.12**（×1.2）
        expected_sv = None
        if isinstance(before_sv, (int, float)) and before_sv:
            expected_sv = float(before_sv) * 1.2
        ratio = None
        if (
            isinstance(before_sv, (int, float))
            and before_sv
            and isinstance(after_sv, (int, float))
        ):
            ratio = round(float(after_sv) / float(before_sv), 6)

        #: ★ 判据：只有 SystemValue 落在「×1.2 附近」才算改对了
        dim_changed = bool(
            expected_sv is not None
            and isinstance(after_sv, (int, float))
            and abs(float(after_sv) - expected_sv) < abs(expected_sv) * 0.05
        )
        #: ★ 疑似单位缺陷：比例接近 1200 倍（0.1→120 是 ×1200，即内容上 ×1.2 再 ×1000）
        unit_defect = bool(ratio is not None and ratio > 500)
        ev["dim_changed_evidence"] = {
            "SystemValue_before": before_sv,
            "SystemValue_after": after_sv,
            "expected_after": expected_sv,
            "ratio_after_over_before": ratio,
            "independent_read_available": expected_sv is not None,
            "GetSystemValue3": next(
                (
                    r.get("GetSystemValue3")
                    for r in ((ev.get("units_after_update") or {}).get("dimension_readings") or [])
                    if r.get("full_name")
                ),
                None,
            ),
            "unit_defect_suspected": unit_defect,
        }
        if unit_defect:
            ev["unit_defect_note"] = (
                "★ SystemValue 从 %r 变成 %r，比例 %r —— 请求是 ×1.2。"
                "⇒ `update_dimension_mm` 报 success 但写入了放大约 1000 倍的值。"
                "★ 这是**新发现的缺陷**，不是本探针的问题；"
                "它的 `after` 自我报告不能当证据。"
                % (before_sv, after_sv, ratio)
            )
            dim_changed = False
        grew = bool(bbox_grew or dim_changed)
        ev["grew_by"] = (
            "bbox" if bbox_grew else ("dimension_value" if dim_changed else "none")
        )
        ev["verdict"] = {
            "rectangle_was_under_constrained": ev.get("status_after_rectangle") == 2,
            "dims_added": ev.get("dimension_count", 0) >= 1,
            "became_fully_constrained": ev.get("status_after_dims") == 3,
            "width_change_moved_geometry": bool(grew),
        }
        #: ★ 两条硬判据：有尺寸 + 改尺寸几何真的变
        ev["verdict"]["width_change_independently_verified"] = bool(dim_changed)
        #: ★★ ok 只认「加尺寸成功」+「改动被独立证实」
        ev["ok"] = bool(ev["verdict"]["dims_added"]) and bool(dim_changed)
        ev["conclusion"] = (
            "★ 板件可做成尺寸驱动：用 %s 加了 %d 个尺寸，约束状态 %s；"
            "改宽度后 X 跨度 %s → %s mm"
            % (
                ev["add_dims"].get("used"),
                ev.get("dimension_count", 0),
                ev.get("status_after_dims"),
                ev.get("bbox_x_before_mm"),
                ev.get("bbox_x_after_mm"),
            )
            if ev["ok"]
            else "★ 未达预期，详见 verdict 与 add_dims"
        )
        print(ev["conclusion"])
        for k, v in ev["verdict"].items():
            print("  %-34s %s" % (k, v))
        print("  入口：%s" % ev["add_dims"].get("used"))
        code = 0 if ev["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1800:]
        print("★ 失败：", ev["err"])
        print(ev["traceback"])
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
        dest = R / "output" / "s3-t008-dimension-driven.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
