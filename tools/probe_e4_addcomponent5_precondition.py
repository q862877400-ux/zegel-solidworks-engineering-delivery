"""★ 单测 A：`AddComponent5`（8 参）+ 官方前置「零件必须在内存里」。

## 为什么只测一条

第 43 轮第一个探针同时试了 A（`AddComponent5`）与 B（`AddComponents3`），
**SolidWorks 崩了**（多个 `SLDEXITAPP.exe` 错误报告），进程被终止，
**一份证据都没落盘** ⇒ 分不清是谁崩的。

⇒ 本轮两次教训：
  ① **一次只测一条**（同第 13/14 轮 `AddHorizontalDimension2` 六次崩溃的教训）；
  ② ★ **证据要边跑边写**，不能只在 `finally` 里写 —— 进程被杀时 `finally` 不会执行。

## 官方前置逐字（`C:\\swapi\\types\\IAssemblyDoc\\AddComponent5.md`）

> **The specified file must be loaded in memory.** A file is loaded into memory
> when you load the file in your SOLIDWORKS Design session (`ISldWorks::OpenDoc6`)
> or open an assembly that already contains the file.

第 22 / 42 轮都是「新建装配 → 直接传路径」，零件从没进内存 ⇒ 前置不成立。
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

from scripts import sw_connect as c_  # noqa: E402
from scripts.sw_connect import get_com_member, open_doc_count  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 单条重试）
# 文件:   tools/probe_e4_addcomponent5_precondition.py
# 定位:   上一版同时试 AddComponent5 与 AddComponents3 导致 SolidWorks 崩溃且无证据。
#          本版**只测 AddComponent5**，且**每步立刻落盘**（进程被杀也留得下读数）。
#          核心假设：官方 Remarks 要求「文件必须已在内存中」，第 22/42 轮缺的就是这一步。
# 官方依据: C:\swapi\types\IAssemblyDoc\AddComponent5.md（8 参 + 该 Remarks）·
#          ISldWorks::OpenDoc6 · IAssemblyDoc::GetComponents
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "e4-addcomponent5-precondition.json"
EV: dict = {"probe": "e4-addcomponent5-precondition", "part": str(PART), "steps": []}


def _flush() -> None:
    """★ 每步立刻落盘 —— 进程被弹窗冻住/杀掉时也能留下读数。"""
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(EV, ensure_ascii=False, indent=2), encoding="utf-8")


def _mark(step: str, **kw) -> None:
    EV["steps"].append(dict(step=step, at=time.strftime("%H:%M:%S"), **kw))
    _flush()
    print("· %s %s" % (step, kw))


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

        ok_p, part_doc = _try(c_.open_document, sw, str(PART))
        loaded = str(_member(part_doc, "GetPathName") or "") if ok_p else ""
        _mark("open_part", ok=ok_p, loaded_path=loaded)

        ok_n, asm_doc = _try(c_.new_document, sw, "assembly")
        _mark("new_assembly", ok=ok_n, title=_title(asm_doc) if ok_n else "")

        ok_a, _ = _try(sw.ActivateDoc3, _title(asm_doc), 0, False)
        active = _member(sw, "ActiveDoc")
        _mark(
            "activate",
            ret=ok_a,
            active_is_asm=(_title(active) == _title(asm_doc)),
        )

        before = _count(asm_doc)
        _mark("count_before", n=before)

        #: ★ 唯一一次 AddComponent5（8 参，官方签名）
        ok5, ret5 = _try(
            lambda: get_com_member(
                asm_doc, "AddComponent5", loaded, 0, "", False, "",
                0.0, 0.0, 0.0,
            )
        )
        after = _count(asm_doc)
        _mark(
            "addcomponent5",
            call_ok=ok5,
            ret_none=(ret5 is None) if ok5 else None,
            err="" if ok5 else str(ret5)[:160],
            after=after,
            added=after - before,
        )

        EV["ok"] = bool(after - before > 0)
        EV["conclusion"] = (
            "★ 前置到位后**加得进去**（%s → %s）⇒ 第 22/42 轮的阻塞不成立"
            % (before, after)
            if EV["ok"]
            else "★ 前置到位仍加不进去（%s → %s）⇒ 阻塞成立，且已排除前置这一层"
            % (before, after)
        )
        _mark("conclusion", text=EV["conclusion"])
        return 0 if EV["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        EV["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        EV["traceback"] = traceback.format_exc()[-1000:]
        _mark("exception", err=EV["err"])
        return 1
    finally:
        if sw is not None:
            try:
                open_doc_count(sw)
            except Exception:  # noqa: BLE001
                pass
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        _flush()
        print("   证据已写：output/e4-addcomponent5-precondition.json")


if __name__ == "__main__":
    raise SystemExit(main())
