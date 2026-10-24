"""★ S3 T011：在**已交付件的副本**上改板宽 100→120，验证下游联动、保存重开。

## 为什么这条是 E2 的核心

`docs/ENGINEERING-PATH.md` 第六节 S3 第 4 条逐字：

> 在同一个**交付件副本**上改已有主参数，检查下游联动、特征错误和引用；
> 保存重开、配置切换后复查。

而 `tools/run_stage2_plate.py` 的 `run_change()` 现在是 `new_document()` 后按新参数
**重新生成**（`R-engineering-path.md` R-10 已记为「替代品」）。那不叫改已交付件。

## 本探针做什么

① 把 `output/stage2/板1_rev-1.SLDPRT` **复制**一份（**不动交付件本身**）
② 打开副本
③ 数草图驱动尺寸（`count_sketch_dimensions`）
④ 找值 ≈ 100 mm 的那个（板宽），改成 120 mm（`update_dimension_mm`）
⑤ 回读**包围盒 X 跨度** ⇒ 期望 120 mm（几何真的变了，不是只有数值变了）
⑥ 保存 → 关闭 → **重开** → 再读尺寸与包围盒 ⇒ 期望仍是 120（参数化关系落进文件）
⑦ 报告特征错误数（`whats_wrong`）—— 改完不该有错误

## 只读纪律

- **只改副本**：交付件 `板1_rev-1.SLDPRT` 不动
- 副本写到 `output/t011-copy/`
- 收尾关掉**自己开的**文档
- `CommandInProgress` 抑制弹窗（铁律 2）
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
from scripts.sw_feature_readback import feature_names, whats_wrong  # noqa: E402
from scripts.sw_sketch_dimensions import count_sketch_dimensions  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_t011_edit_delivered_plate.py
# 定位:   specs/350-first-part-delivery T011 —— 在**已交付件副本**上改主参数，
#          验下游联动 / 无特征错误 / 保存重开仍成立。区别于 run_change 的
#          「新建文档重新生成」（R-engineering-path.md R-10 记为替代品）。
# 官方依据: IDimension.SetSystemValue3（米，经 update_dimension_mm）·
#           IPartDoc.GetBodies2(0, True) → IBody2.GetBodyBox() ·
#           IModelDoc2.OpenDoc6 / Save3（经 sw_connect.open_document / save_document）·
#           IFeature.GetFirstDisplayDimension + IDisplayDimension.GetNext2（数尺寸）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
COPY_DIR = R / "output" / "t011-copy"
SW_SOLID_BODY = 0


def _bbox_mm(doc) -> dict:
    """★ 包围盒（`GetBodies2(0, True)` → `GetBodyBox()`，6 个 double 单位米）。"""
    out: dict = {"ok": False}
    ok, body = _try(get_com_member, doc, "GetBodies2", SW_SOLID_BODY, True)
    if not ok or not body:
        out["error"] = "GetBodies2: %s" % str(body)[:90]
        return out
    try:
        b = body[0] if isinstance(body, (list, tuple)) else list(body)[0]
    except (IndexError, TypeError):
        out["error"] = "GetBodies2 回空"
        return out
    ok2, box = _try(get_com_member, b, "GetBodyBox")
    if not ok2 or not box:
        out["error"] = "GetBodyBox: %s" % str(box)[:90]
        return out
    n = [float(v) for v in list(box)]
    if len(n) < 6:
        out["error"] = "GetBodyBox 只回 %d 个数" % len(n)
        return out
    out.update(
        {
            "ok": True,
            "x_mm": round((n[3] - n[0]) * 1000.0, 6),
            "y_mm": round((n[4] - n[1]) * 1000.0, 6),
            "z_mm": round((n[5] - n[2]) * 1000.0, 6),
            "raw": n,
        }
    )
    return out


def _dims(doc) -> list:
    """★ 草图驱动尺寸清单。"""
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
        g = 0
        while dd is not None and g < 200:
            g += 1
            ok_dim, dim = _try(get_com_member, dd, "GetDimension")
            if ok_dim and dim is not None:
                ok_n, full = _try(lambda: str(dim.FullName))
                ok_v, sv = _try(lambda: float(dim.SystemValue))
                out.append(
                    {
                        "sketch": nm,
                        "full_name": full if ok_n else "",
                        "value_mm": round(sv * 1000.0, 6) if ok_v else None,
                    }
                )
            ok_nx, nx = _try(get_com_member, dd, "GetNext2")
            dd = nx if ok_nx else None
    return out



def _dirty_flag(doc) -> dict:
    """★ `IModelDoc2.GetSaveFlag()` —— 文档是否有未保存改动。

    ★ 为什么要看它：`Save` 在**文档不脏**时是**空操作但返回 True**
      ⇒ 「保存成功」与「真的落盘」是两件事。
    """
    ok, v = _try(get_com_member, doc, "GetSaveFlag")
    return {"ok": ok, "unsaved": bool(v) if ok else str(v)[:80]}


def _mtime(path) -> float:
    try:
        return round(Path(path).stat().st_mtime, 3)
    except OSError:
        return -1.0



def _fingerprint(path) -> dict:
    """★ 文件指纹：大小 + sha256 前 16 位 + mtime。"""
    import hashlib

    try:
        p = Path(path)
        b = p.read_bytes()
        return {
            "size": len(b),
            "sha16": hashlib.sha256(b).hexdigest()[:16],
            "mtime": round(p.stat().st_mtime, 3),
        }
    except OSError as exc:
        return {"error": str(exc)[:80]}


def _doc_path(doc) -> str:
    """★ 文档**实际**的磁盘路径（`IModelDoc2.GetPathName`）。"""
    ok, v = _try(get_com_member, doc, "GetPathName")
    return str(v) if ok and v else "(取不到)"

def _errors(doc) -> dict:
    ok, w = _try(whats_wrong, doc)
    return w if ok else {"error": str(w)[:120]}


def main() -> int:
    ev: dict = {"probe": "t011-edit-delivered-plate", "steps": []}
    sw = doc = None
    try:
        if not SRC.is_file():
            print("★ 找不到交付件：%s" % SRC)
            return 2
        COPY_DIR.mkdir(parents=True, exist_ok=True)
        dst = COPY_DIR / "板1_rev-1_copy.SLDPRT"
        shutil.copy2(SRC, dst)
        ev["src"] = str(SRC)
        ev["copy"] = str(dst)
        print("① 已复制交付件副本 → %s" % dst.name)

        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        ok_o, doc = _try(c_.open_document, sw, str(dst))
        ev["open"] = {"ok": ok_o, "detail": str(doc)[:100]}
        if not ok_o or doc is None:
            print("★ 打不开副本：%s" % str(doc)[:120])
            return 2
        print("② 已打开副本")
        ev["doc_pathname"] = _doc_path(doc)
        ev["fingerprint_after_open"] = _fingerprint(ev["doc_pathname"])
        print("   文档实际路径：%s" % ev["doc_pathname"])

        before = {
            "dims": _dims(doc),
            "dim_count": count_sketch_dimensions(doc),
            "bbox": _bbox_mm(doc),
            "errors": _errors(doc),
        }
        ev["before"] = before
        print(
            "③ 打开时：尺寸 %d 个 · 包围盒 %s · 错误 %s"
            % (
                before["dim_count"],
                before["bbox"].get("x_mm"),
                before["errors"].get("count", before["errors"]),
            )
        )

        #: ④ 找值 ≈100mm 的宽度尺寸 → 改 120
        target = next(
            (
                d
                for d in before["dims"]
                if d.get("value_mm") is not None
                and abs(d["value_mm"] - 100.0) < 1.0
            ),
            None,
        )
        ev["target"] = target
        if target is None:
            ev["conclusion"] = "★ 找不到值≈100mm 的尺寸 ⇒ 交付件不是尺寸驱动，改不了"
            print(ev["conclusion"])
            return 1

        ok_u, upd = _try(update_dimension_mm, doc, target["full_name"], 120.0)
        ev["update"] = {"ok": ok_u, "detail": str(upd)[:300]}
        print("④ 改宽度 → 120mm：%s" % ("ok" if ok_u else str(upd)[:80]))

        after = {
            "dims": _dims(doc),
            "bbox": _bbox_mm(doc),
            "errors": _errors(doc),
        }
        ev["after_change"] = after
        print(
            "⑤ 改后：包围盒 X = %s mm · 错误 %s"
            % (after["bbox"].get("x_mm"), after["errors"].get("count", after["errors"]))
        )

        #: ⑥ 保存 → 关闭 → 重开
        ev["dirty_before_save"] = _dirty_flag(doc)
        ev["mtime_before_save"] = _mtime(dst)
        ok_s, sv = _try(c_.save_document, doc)
        ev["mtime_after_save"] = _mtime(dst)
        ev["dirty_after_save"] = _dirty_flag(doc)
        #: ★ 比的是**文档实际路径**的 mtime（沙盒下 dst 不是同一文件）
        ev["file_changed_by_save"] = (
            (ev.get("fingerprint_after_save") or {}).get("mtime")
            != (ev.get("fingerprint_after_open") or {}).get("mtime")
        )
        #: ★ 保存后**先原地再读一次** —— 区分「存盘失败」与「重开忽略」
        ev["bbox_right_after_save"] = _bbox_mm(doc)
        ev["fingerprint_after_save"] = _fingerprint(ev["doc_pathname"])
        ev["doc_pathname_after_save"] = _doc_path(doc)
        print(
            "   保存：ok=%s · 脏标记 %s→%s · mtime %s→%s · 保存后 bbox X=%s"
            % (
                ok_s,
                ev["dirty_before_save"].get("unsaved"),
                ev["dirty_after_save"].get("unsaved"),
                ev["mtime_before_save"],
                ev["mtime_after_save"],
                ev["bbox_right_after_save"].get("x_mm"),
            )
        )
        ev["save"] = {"ok": ok_s, "detail": str(sv)[:120]}
        #: ★ COM 里 GetTitle 是**属性**（直接取就是 str），不能当方法调
        ok_t, title = _try(get_com_member, doc, "GetTitle")
        title = title if ok_t and title else ""
        _try(sw.CloseDoc, title)
        doc = None
        #: ★★ 必须重开**文档实际所在的路径**（沙盒里会被改写成
        #:   output/sandbox/inputs/xxx__N.SLDPRT），而不是我传进去的 dst。
        #:   ⚠ 第一次跑时重开了 dst ⇒ 又拿到一份原始副本 ⇒
        #:     误判「保存没落盘」。这是**测量假象**，不是 Save 的缺陷。
        reopen_path = ev.get("doc_pathname") or str(dst)
        if reopen_path == "(取不到)":
            reopen_path = str(dst)
        ok_r, doc2 = _try(c_.open_document, sw, reopen_path)
        ev["reopen_path"] = reopen_path
        ev["reopen"] = {"ok": ok_r, "detail": str(doc2)[:100]}
        if ok_r and doc2 is not None:
            doc = doc2
            reopened = {
                "dims": _dims(doc),
                "bbox": _bbox_mm(doc),
                "errors": _errors(doc),
            }
            ev["after_reopen"] = reopened
            print(
                "⑥ 保存重开后：包围盒 X = %s mm" % reopened["bbox"].get("x_mm")
            )

        #: ⑦ 判读
        x0 = before["bbox"].get("x_mm")
        x1 = after["bbox"].get("x_mm")
        x2 = (ev.get("after_reopen") or {}).get("bbox", {}).get("x_mm")
        grew = x0 is not None and x1 is not None and x1 > x0 + 1.0
        persisted = x2 is not None and abs(x2 - 120.0) < 1.0
        no_err = (after["errors"].get("count") or 0) == 0
        ev["verdict"] = {
            "had_driving_dimension": (before["dim_count"] or 0) >= 1,
            "save_wrote_file": bool(ev.get("file_changed_by_save")),
            "sha_changed": (
                (ev.get("fingerprint_after_open") or {}).get("sha16")
                != (ev.get("fingerprint_after_save") or {}).get("sha16")
            ),
            "size_changed": (
                (ev.get("fingerprint_after_open") or {}).get("size")
                != (ev.get("fingerprint_after_save") or {}).get("size")
            ),
            "doc_was_dirty_before_save": (ev.get("dirty_before_save") or {}).get(
                "unsaved"
            ),
            "changed_on_copy": bool(grew),
            "bbox_x": "%s → %s → %s" % (x0, x1, x2),
            "persisted_after_reopen": bool(persisted),
            "no_feature_errors": bool(no_err),
        }
        ev["ok"] = bool(grew and persisted)
        ev["conclusion"] = (
            "★ 在交付件副本上改板宽成功：包围盒 X %s → %s → %s mm，"
            "保存重开仍成立 ⇒ E2 的「改已交付件」这条成立"
            % (x0, x1, x2)
            if ev["ok"]
            else "★ 未达预期，详见 verdict"
        )
        print(ev["conclusion"])
        for k, v in ev["verdict"].items():
            print("  %-28s %s" % (k, v))
        return 0 if ev["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1600:]
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
        dest = R / "output" / "t011-edit-delivered-plate.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
