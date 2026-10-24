"""★ S3 真机采集：E3 特征树可编辑 —— 回读类型/错误/父子 + 实际编辑前序并验证后续。

## 为什么做这条

E3 的判据（`docs/ENGINEERING-PATH.md` 第四节）：

> 回读特征类型、错误/警告、引用与父子依赖；**实际编辑前序草图或参数并验证后续**
> 负例：导入死实体冒充原生特征、悬空引用、错误配置、目标对象漂移
> 替代品：特征数大于零、STEP 可打开

`scripts/engineering/acceptance/e2_e3_solid.py` 的判定器已写好，缺的是**真机采集**。

## ★ 一个关键区分（第 14 轮查明）

| 动作 | 状态 |
|---|---|
| **新建**尺寸（`AddDimension2` / `AddHorizontalDimension2`） | ❌ 本机把进程弄崩（事实 560） |
| **改已有**尺寸（`update_dimension_mm` → `SetSystemValue3`） | ✅ 通（第 11/12 轮 T011 验过） |

⇒ E3 的「实际编辑前序」用**改已有尺寸**，不受那条退化影响。

## 本探针做两件事

**① 先量准类型名**（不猜：铁律 5）
  把特征树里每个特征的 `GetTypeName2` 原样打出来 —— 用它确定「什么是原生特征」
  的判据词表，而不是凭印象写 `"Import"` / `"Extrude"`。

**② 再做编辑并验后续**
  把 `D1@草图1`（板宽）从 100 改成 120，然后核四件事：
  - 改动后 `whats_wrong` 的错误数仍为 0
  - 特征数不变（没有东西被吃掉）
  - 孔的切除特征仍在（`GetChildren` 里能找到）
  - 包围盒 X 跟着变（下游真的跟了）

## 只读纪律

- 只操作**副本**（`output/t011-copy/`），交付件不动
- `CommandInProgress`（铁律 2）
- 收尾只关**自己开的**文档
"""

from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c_  # noqa: E402
from scripts.sw_connect import get_com_member  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_document_data import update_dimension_mm  # noqa: E402
from scripts.sw_feature_readback import feature_info, feature_names, whats_wrong  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_s3_e3_feature_tree.py
# 定位:   specs/350-first-part-delivery T012 / E3 —— 真机采集「特征树可编辑」：
#           回读类型/错误/父子依赖，并**实际编辑前序参数**验证下游。
#           ★ 只改**已有**尺寸（通），不新建尺寸（本机崩，事实 560）。
# 官方依据: IFeature.GetTypeName2 / GetChildren / GetParents / GetEditStatus / GetFaceCount
#           IModelDocExtension.GetWhatsWrongCount（经 sw_feature_readback.whats_wrong）
#           IDimension.SetSystemValue3（经 sw_document_data.update_dimension_mm，单位米）
#           IPartDoc.GetBodies2(0,True) → IBody2.GetBodyBox()（读几何变化）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
COPY_DIR = R / "output" / "e3-copy"
SW_SOLID_BODY = 0


def _member(obj, name):
    ok, v = _try(get_com_member, obj, name)
    return v if ok and v is not None else None


def _bbox_x_mm(doc) -> float | None:
    ok, body = _try(get_com_member, doc, "GetBodies2", SW_SOLID_BODY, True)
    if not ok or not body:
        return None
    try:
        b = body[0] if isinstance(body, (list, tuple)) else list(body)[0]
    except (IndexError, TypeError):
        return None
    ok2, box = _try(get_com_member, b, "GetBodyBox")
    if not ok2 or not box:
        return None
    n = [float(v) for v in list(box)]
    return round((n[3] - n[0]) * 1000.0, 4) if len(n) >= 6 else None


def _tree(doc) -> list:
    """★ 逐特征读数：类型 / 面数 / 父子计数 / 编辑状态。"""
    rows = []
    for nm in feature_names(doc) or []:
        info = feature_info(doc, nm) or {}
        rows.append(
            {
                "name": nm,
                "type": info.get("GetTypeName2"),
                "faces": info.get("GetFaceCount"),
                "parents": info.get("GetParents"),
                "children": info.get("GetChildren"),
                "edit_status": info.get("GetEditStatus"),
                "error": info.get("error"),
            }
        )
    return rows


def main() -> int:
    ev: dict = {"probe": "s3-e3-feature-tree"}
    sw = doc = None
    try:
        if not SRC.is_file():
            print("★ 找不到交付件：%s" % SRC)
            return 2
        COPY_DIR.mkdir(parents=True, exist_ok=True)
        dst = COPY_DIR / "板1_rev-1_e3.SLDPRT"
        shutil.copy2(SRC, dst)

        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        ok_o, doc = _try(c_.open_document, sw, str(dst))
        if not ok_o or doc is None:
            print("★ 打不开副本：%s" % str(doc)[:120])
            return 2

        #: ① 类型词表（**量出来的**，不是猜的）
        before = _tree(doc)
        ev["tree_before"] = before
        ev["type_vocabulary"] = sorted({r.get("type") for r in before if r.get("type")})
        ww0 = whats_wrong(doc)
        ev["whats_wrong_before"] = ww0
        ev["feature_count_before"] = len(before)
        print("① 特征 %d 个 · 类型词表 %s" % (len(before), ev["type_vocabulary"]))
        for r in before:
            print("   %-14s type=%-18s faces=%s 父=%s 子=%s" % (
                str(r["name"])[:14], str(r["type"])[:18],
                r["faces"], r["parents"], r["children"],
            ))
        print("   错误/警告：%s" % json.dumps(ww0, ensure_ascii=False)[:120])

        #: ② 找板宽尺寸并改成 120（改**已有**尺寸，不新建）
        dims = []
        for nm in feature_names(doc) or []:
            if not (nm.startswith("草图") or nm.lower().startswith("sketch")):
                continue
            ok_f, feat = _try(get_com_member, doc, "FeatureByName", nm)
            if not ok_f or feat is None:
                continue
            dd = _member(feat, "GetFirstDisplayDimension")
            g = 0
            while dd is not None and g < 100:
                g += 1
                dim = _member(dd, "GetDimension")
                if dim is not None:
                    full = _member(dim, "FullName")
                    sv = _member(dim, "SystemValue")
                    dims.append(
                        {
                            "full_name": str(full) if full else "",
                            "value_mm": round(float(sv) * 1000.0, 4)
                            if sv is not None
                            else None,
                        }
                    )
                dd = _member(dd, "GetNext2")
        ev["dims"] = dims
        target = next(
            (
                d
                for d in dims
                if d.get("value_mm") is not None and abs(d["value_mm"] - 100.0) < 1.0
            ),
            None,
        )
        ev["target_dim"] = target
        print("② 尺寸 %s · 目标 %s" % (dims, target))
        if target is None:
            ev["conclusion"] = "★ 没有值≈100 的尺寸 ⇒ 改不了前序"
            print(ev["conclusion"])
            return 1

        bbox0 = _bbox_x_mm(doc)
        ok_u, upd = _try(update_dimension_mm, doc, target["full_name"], 120.0)
        ev["update"] = {"ok": ok_u, "detail": str(upd)[:200]}

        #: ③ 验后续
        after = _tree(doc)
        ww1 = whats_wrong(doc)
        bbox1 = _bbox_x_mm(doc)
        ev["tree_after"] = after
        ev["whats_wrong_after"] = ww1
        ev["feature_count_after"] = len(after)
        ev["bbox"] = {"before_mm": bbox0, "after_mm": bbox1}

        hole_features_before = [
            r["name"] for r in before if "切除" in str(r["name"]) or "Cut" in str(r["name"])
        ]
        hole_features_after = [
            r["name"] for r in after if "切除" in str(r["name"]) or "Cut" in str(r["name"])
        ]
        ev["hole_features"] = {
            "before": hole_features_before,
            "after": hole_features_after,
        }

        err_ok = (ww1.get("count") or 0) == 0
        count_ok = len(after) == len(before)
        holes_ok = len(hole_features_after) == len(hole_features_before)
        geom_ok = bool(bbox0 and bbox1 and bbox1 > bbox0 + 1.0)
        ev["downstream"] = {
            "no_errors_after": err_ok,
            "feature_count_unchanged": count_ok,
            "hole_features_intact": holes_ok,
            "geometry_followed": geom_ok,
            "bbox_x": "%s → %s" % (bbox0, bbox1),
        }
        ok = bool(ok_u and err_ok and count_ok and holes_ok and geom_ok)
        ev["editable_prefix_verified"] = ok
        ev["ok"] = ok
        ev["conclusion"] = (
            "★ 前序可编辑且下游跟随：改板宽 100→120 后 错误 0 · 特征数 %d 不变 · "
            "孔特征 %d 个仍在 · 包围盒 X %s → %s mm"
            % (len(after), len(hole_features_after), bbox0, bbox1)
            if ok
            else "★ 未达预期，见 downstream"
        )
        print("③ %s" % ev["conclusion"])
        for k, v in ev["downstream"].items():
            print("   %-26s %s" % (k, v))
        return 0 if ok else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1200:]
        print("★ 失败：", ev["err"])
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
        dest = R / "output" / "s3-e3-feature-tree.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
