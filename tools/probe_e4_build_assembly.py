"""★ E4 第一次真机装配：两个组件 + 试一次配合 + 干涉 + 判定器。

## 已确认的前置（第 43 轮，事实 564）

- `AddComponent5` 要求**文件已在内存**（官方 Remarks 逐字）
- 兜底必须用 `opened.GetPathName()`（沙箱会改名）

## 本轮要验什么

| 步骤 | 读数 | 判据 |
|---|---|---|
| 加两个组件 | `GetComponents` 条数 0 → 2 | 独立读数 |
| 组件清单 | `sw_assembly.list_components` | 只读、已验证 |
| 干涉检查 | `sw_assembly.check_interference` | 只读、已验证 |
| 试一次重合配合 | 配合数 | 已知：`AddMate5` 已废弃、且「没选中面」是历史根因 |
| E4 判定 | `judge_assembly_interference` | 要看 mates 是否 ≥1 |

## ★ 诚实处理的边界

若配合**建不出来**，那是**测试搭不起来**（不是产物不合格）。

⇒ 采集器要给 `complete=False`（`mates` 为空且**我们试过但失败**），
  让判定器报 `unknown`，而**不是**把「我方没搭出来」写成产物 `fail`。

★ 这是第 33 轮那条纪律的应用：**采集缺失不得说成不合格**。

## 证据边跑边写（第 43 轮崩溃教训）

进程被杀时 `finally` 不执行 ⇒ 每一步 `_flush()`。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_assembly as asm_  # noqa: E402
from scripts import sw_connect as c_  # noqa: E402
from scripts.sw_connect import get_com_member, open_doc_count  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · E4 首次真机装配）
# 文件:   tools/probe_e4_build_assembly.py
# 定位:   第 43 轮解除加组件阻塞后，第一次真的搭出两组件装配并跑 E4 判定器。
#          配合走仓库既有封装（add_mate_coincident → AddMate5，已知废弃且历史根因是没选中面）
#          ⇒ 若配合建不出来，采集器要标 complete=False（搭建失败 ≠ 产物不合格）。
# 官方依据: C:\swapi\types\IAssemblyDoc\AddComponent5.md（文件必须已在内存）·
#          IAssemblyDoc::GetComponents · IAssemblyDoc::CreateMate（AddMate5 的继任者）·
#          IAssemblyDoc::GetInterferenceDetectionManager（经 sw_assembly.check_interference）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "e4-build-assembly.json"
EV: dict = {"probe": "e4-build-assembly", "part": str(PART), "steps": []}


def _flush() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(EV, ensure_ascii=False, indent=2), encoding="utf-8")


def _mark(step: str, **kw) -> None:
    EV["steps"].append(dict(step=step, at=time.strftime("%H:%M:%S"), **kw))
    _flush()
    print("· %-22s %s" % (step, {k: v for k, v in kw.items() if k != "steps"}))


def _count(asm_doc) -> int:
    try:
        return len(list(get_com_member(asm_doc, "GetComponents", False) or []))
    except Exception:  # noqa: BLE001
        return -1


def _title(doc) -> str:
    return str(_member(doc, "GetTitle") or "")


def main() -> int:
    sw = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        if not PART.is_file():
            _mark("abort", err="零件不存在")
            return 1

        #: ① 零件进内存（官方前置）
        ok_p, part_doc = _try(c_.open_document, sw, str(PART))
        loaded = str(_member(part_doc, "GetPathName") or "") if ok_p else ""
        _mark("open_part", ok=ok_p, loaded=Path(loaded).name)

        #: ② 新装配 + 激活
        ok_n, asm_doc = _try(c_.new_document, sw, "assembly")
        _try(sw.ActivateDoc3, _title(asm_doc), 0, False)
        active = _member(sw, "ActiveDoc")
        _mark("new_assembly", ok=ok_n, active_is_asm=(_title(active) == _title(asm_doc)))

        before = _count(asm_doc)
        _mark("count_before", n=before)

        #: ③ 加两个组件（走封装，传 sw）
        added = []
        for i, dx in enumerate((0.0, 30.0), 1):
            ok_a, ret = _try(
                asm_.add_component, asm_doc, str(PART), dx, 0.0, 0.0, "", sw
            )
            n = _count(asm_doc)
            added.append({"i": i, "ok": ok_a, "count": n})
            if not ok_a:
                _mark("add_component_%d" % i, ok=False, err=str(ret)[:150], count=n)
        after = _count(asm_doc)
        _mark("count_after", n=after, added=after - before, detail=added)

        #: ④ 组件清单（只读、已验证）
        ok_l, comps = _try(asm_.get_components, asm_doc)
        _mark(
            "list_components",
            ok=ok_l,
            n=len(comps) if isinstance(comps, (list, tuple)) else "?",
        )

        #: ⑤ 试一次重合配合（走仓库封装；已知 AddMate5 废弃）
        ok_m, ret_m = _try(
            asm_.add_mate_coincident,
            asm_doc, "板1-1@装配", "FACE", "板1-2@装配", "FACE",
        )
        ok_ms, mate_list = _try(asm_.collect_mate_feature_summary, asm_doc)
        n_mates = -1
        try:
            if isinstance(mate_list, dict):
                #: ★ 只有 `None` 才回落 —— `count=0`（确实零配合）必须原样保留，
                #:   否则「明确读到 0」会被错报成「读不出 -1」（事实 61 同族）。
                _cnt = mate_list.get("count")
                n_mates = int(_cnt) if _cnt is not None else -1
            elif isinstance(mate_list, (list, tuple)):
                n_mates = len(mate_list)
        except Exception:  # noqa: BLE001
            n_mates = -1
        _mark(
            "try_mate",
            ok=ok_m,
            err="" if ok_m else str(ret_m)[:170],
            mates=n_mates,
        )

        #: ⑥ 干涉检查（只读、已验证）
        ok_i, interf = _try(asm_.get_interference_detection, asm_doc)
        _mark("interference", ok=ok_i, detail=str(interf)[:200])

        EV["component_count"] = after
        EV["mate_count"] = n_mates
        EV["interference"] = str(interf)[:400] if ok_i else "err"
        EV["ok"] = bool(after >= 2)
        EV["conclusion"] = (
            "★ 两组件装配**搭起来了**（组件数 %s → %s）；配合%s；干涉%s"
            % (
                before,
                after,
                "建成" if n_mates >= 1 else "**没建成**（历史根因：没选中面）",
                "已读" if ok_i else "读失败",
            )
        )
        _mark("conclusion", text=EV["conclusion"])
        return 0 if EV["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        EV["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        EV["traceback"] = traceback.format_exc()[-1200:]
        _mark("exception", err=EV["err"])
        return 1
    finally:
        if sw is not None:
            for d in list(sw.GetDocuments() or []):
                _try(sw.CloseDoc, str(_member(d, "GetTitle") or ""))
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
            EV["docs_left"] = open_doc_count(sw)
        _flush()
        print("   证据已写：output/e4-build-assembly.json")


if __name__ == "__main__":
    raise SystemExit(main())
