"""★ 阶段 2 · 真机变更传播（规格 317 的 D5 真机链）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/change_run.py
# 定位:   规格 `specs/317-stage2-real-holes` 的 D5（变更传播）的**真机链**。★★ 上一轮
#           （第 1/2 轮）D5 只做了机制与测试，**没跑真机链**⇒ 本模块补「改尺寸 → 重建 → 
#           出图 → 校验」那一段。
# 官方依据: ① 本仓 `scripts/engineering/drawing_obligations.py` 的   `ArtifactDigest` / 
#           `changed_after_revision` / `propagation_report`② 本仓 `scripts/config_update
#           _dimension.py` 与   `solidworks_config_update_dimension`（改具名尺寸的入口）
#           ③ 本仓**事实 71**（`GetPartBox` 回毫米）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收见 `tools/run_stage2_plate.py --change`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]


def find_dimension_names(doc) -> dict:
    """★ 找出文档里**可改的具名尺寸**（★ 判据 = 真机回读，不是猜名字）。

    ★★ 为什么必须回读：`D1@草图1` 这类名字**随语言与草图序号变**（本仓已知事实 9）。
      ★ 猜名字 ⇒ 改不动 ⇒ 而「改不动」与「改了没生效」长得一样。
    """
    import sys
    for p in (str(ROOT / "scripts"), str(ROOT / "tools"), str(ROOT)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import sw_connect

    out: dict = {"dimensions": [], "error": ""}
    try:
        #: ★ 遍历特征树，取每个特征的 `DisplayDimension` / `GetFirstDisplayDimension`
        feat = sw_connect.safe_get_com_member(doc, "FirstFeature")
        feat = feat() if callable(feat) else feat
        seen = 0
        while feat is not None and seen < 200:
            seen += 1
            try:
                dd = sw_connect.safe_get_com_member(feat, "GetFirstDisplayDimension")
                dd = dd() if callable(dd) else dd
                n = 0
                while dd is not None and n < 50:
                    n += 1
                    try:
                        dim = sw_connect.safe_get_com_member(dd, "GetDimension")
                        dim = dim() if callable(dim) else dim
                        nm = sw_connect.safe_get_com_member(dim, "FullName")
                        nm = nm() if callable(nm) else nm
                        val = sw_connect.safe_get_com_member(
                            dim, "GetSystemValue2", "")
                        val = val() if callable(val) else val
                        if nm:
                            out["dimensions"].append(
                                {"name": str(nm), "value_m": float(val or 0)})
                    except Exception:                                      # noqa: BLE001
                        pass
                    try:
                        dd = sw_connect.safe_get_com_member(dd, "GetNext3")
                        dd = dd() if callable(dd) else dd
                    except Exception:                                      # noqa: BLE001
                        break
            except Exception:                                              # noqa: BLE001
                pass
            try:
                feat = sw_connect.safe_get_com_member(feat, "GetNextFeature")
                feat = feat() if callable(feat) else feat
            except Exception:                                              # noqa: BLE001
                break
    except Exception as exc:                                               # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    return out


def change_plan(old: dict, new: dict) -> list:
    """★ 由「旧参数 → 新参数」算出**变更清单**（★ 每条带影响面）。

    ★ 判据：只列**真的变了**的（★ 没变的不算变更 —— 否则传播报告会假阳性）。
    """
    from .drawing_obligations import ChangeRecord
    rows = []
    for k in sorted(set(old) | set(new)):
        a, b = old.get(k), new.get(k)
        if a != b:
            rows.append(ChangeRecord(name=k, old=a, new=b))
    return rows


def verify_propagation(before_digests: list, after_digests: list,
                       changes: list, steps) -> dict:
    """★ 变更传播的总判据（★ SC-010：无旧模型/旧尺寸/旧证据混入）。

    ★★ 三条都要：
      ① 每个受影响产物**都变了**（sha256 不同）—— `changed_after_revision`
      ② 版本**一致**（model/drawing/report 同一 revision）—— `version_consistent`
      ③ 有受影响步骤就**必须传播** —— `propagation_report`
    """
    from . import drawing_obligations as DO

    changed = DO.changed_after_revision(before_digests, after_digests)
    version = DO.version_consistent(after_digests)
    prop = DO.propagation_report(steps, changes)
    return {
        "changed": changed,
        "version": version,
        "propagation": prop,
        "ok": bool(changed.get("ok") and version.get("ok") and prop.get("ok")),
        "★": "★ 三条都要过：产物都变 + 版本一致 + 有受影响就传播",
    }


def digest_set(model: pathlib.Path, drawing: pathlib.Path,
               report: pathlib.Path, *, revision: str) -> list:
    """★ 造三类产物的摘要集（★ 判「新旧混入」的输入）。"""
    from . import drawing_obligations as DO
    return [DO.digest_of(model, kind="model", revision=revision),
            DO.digest_of(drawing, kind="drawing", revision=revision),
            DO.digest_of(report, kind="report", revision=revision)]
