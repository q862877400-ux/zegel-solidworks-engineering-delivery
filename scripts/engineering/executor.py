"""★ 阶段 1 · 执行器 + 执行意图记录 + COM 写调用计数器（规格 316 的 C6）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/executor.py
# 定位:   规格 `specs/316-stage1-parameter-plate` 的 C6（执行意图记录）。★★ 外部方案阶
#           段 1 逐字要求「每次写 COM 前记录意图；返回后记录结果」，且验收要求「负例的 *
#           *COM 写调用数全部为 0**」。★ 实测（2026-10-11）全仓**没有**这个计数器 ⇒ 本文
#           件补上。
# 官方依据: 不适用（本仓自研执行层）。★ 判据纪律依据：本仓**事实 8**（`SelectByID2`/`Sel
#           ect4` 的 bool 返回值不可信  ⇒ 判「写没写」只能**回读**或**在边界计数**）。
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收见 `tools/run_stage1_plate.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import pathlib
import time
from dataclasses import dataclass, field

from . import authorization as auth

ROOT = pathlib.Path(__file__).resolve().parents[2]


#: ══════════════════════════════════════════════════════════════════════
# 一、COM 写调用计数器（★ SC-009 的**唯一判据来源**）
#: ══════════════════════════════════════════════════════════════════════


class ComWriteCounter:
    """★ 在 COM 边界上数**写调用**（★ 事实 8：返回值不可信，只能计数/回读）。

    ★★ 怎么接（★ 两条路都要接）：
      · `scripts/sw_connect.set_com_member`      —— 属性写
      · `scripts/sw_connect.call_com_member`     —— 方法调（★ 只在效应为写时计数）
    ★ 只读路径**不计数**（★ 否则负例会因「读了一下」而误报）。
    """

    def __init__(self) -> None:
        self._n = 0
        self._armed = False
        self._log: list[str] = []

    def arm(self) -> None:
        """★ 开始计数（★ 执行前调）。"""
        self._armed = True

    def disarm(self) -> None:
        self._armed = False

    def bump(self, what: str = "") -> None:
        if self._armed:
            self._n += 1
            if len(self._log) < 200:
                self._log.append(what)

    def count(self) -> int:
        return self._n

    def reset(self) -> None:
        self._n = 0
        self._log.clear()

    def assert_zero(self, why: str) -> None:
        """★ 不为 0 就抛 —— ★ 负例**必须证明**「一次都没写」。"""
        if self._n != 0:
            raise AssertionError(
                "★ 负例「%s」本应 **0 次 COM 写调用**，实测 **%d 次**：%s"
                % (why, self._n, self._log[:5])
            )


#: ★ 全局单例（★ 与 `sw_connect` 的钩子共享）
COUNTER = ComWriteCounter()


#: ══════════════════════════════════════════════════════════════════════
# 二、执行意图记录（★ C6）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class ExecutionRecord:
    step: str
    tool: str
    params: dict = field(default_factory=dict)
    intent_at: str = ""  #: ★ 写 COM **之前**落盘
    result: str = ""
    com_write_count: int = 0  #: ★ 该步触达 COM 写调用的次数
    effect: str = ""  #: ★ 工具声明的效应（★ 计数的**权威**依据）
    member_writes: int = 0  #: ★ 成员级钩子看到的次数（★ 辅助证据）
    error: str = ""


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


#: ══════════════════════════════════════════════════════════════════════
# 三、执行（★ 走 `solidworks_*` 全名 —— ★ FR-012 禁绕内部函数）
#: ══════════════════════════════════════════════════════════════════════


def execute_plan(
    plan,
    reg: dict,
    *,
    host: dict | None = None,
    owned: auth.OwnedDocuments | None = None,
    doc=None,
    write_paths: tuple = (),
    log_dir: pathlib.Path | None = None,
    dry_run: bool = False,
) -> dict:
    """★ 执行一条**已编译**的计划。

    ★★ 纪律（★ 每条都有判据）：
      ① **先授权，再执行** —— 授权不过 ⇒ **一次 COM 都不碰**（★ SC-009）
      ② 每步写 COM **之前**落盘意图（★ I9）
      ③ 每步的 `com_write_count` 由 `COUNTER` 给（★ I10）
      ④ 只走 `solidworks_*` 全名（★ FR-012）—— 解析后的 `step.tool`
      ⑤ `dry_run=True` ⇒ **只授权不执行**（★ 负例测试用）

    :returns: `{ok, code, records, com_write_total, plan_method}`
    """
    #: ① 授权（★ 不过就**立刻返回**，不碰 COM）
    verdict = auth.authorize_plan(
        plan, reg, owned=owned, doc=doc, write_paths=write_paths
    )
    if not verdict.ok:
        return {
            "ok": False,
            "code": verdict.code,
            "detail": verdict.detail,
            "records": [],
            "com_write_total": COUNTER.count(),
            "plan_method": getattr(plan, "method_id", ""),
        }

    if dry_run:
        return {
            "ok": True,
            "code": "",
            "detail": "★ dry_run：只授权未执行",
            "records": [],
            "com_write_total": COUNTER.count(),
            "plan_method": getattr(plan, "method_id", ""),
        }

    #: ★ 执行器懒加载（★ 无真机时也能 import 本模块 —— 契约测试要）
    import sys

    for p in (str(ROOT / "tools"), str(ROOT / "scripts"), str(ROOT)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import tool_caller  # noqa: E402

    #: ★★ 把计数器接到 COM 边界上（★ `sw_connect` 是**唯一**的取/调入口）
    #:   ⇒ 之后所有写调用都会经 `COUNTER.bump`（★ 未 arm 时空操作）
    try:
        import sw_connect  # noqa: E402

        sw_connect.set_com_write_hook(COUNTER.bump)
    except Exception:  # noqa: BLE001
        pass

    records: list[ExecutionRecord] = []
    logdir = log_dir or (ROOT / "output" / "stage1-runs")
    logdir.mkdir(parents=True, exist_ok=True)
    intent_log = logdir / "intent.jsonl"

    for st in plan.steps:
        rec = ExecutionRecord(step=st.step, tool=st.tool, params=dict(st.params))
        #: ② 写 COM **之前**落盘意图
        rec.intent_at = _now()
        with intent_log.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "at": rec.intent_at,
                        "step": rec.step,
                        "tool": rec.tool,
                        "params": rec.params,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        #: ③ 计数
        #: ★★ 2026-10-12 **改判据**（★ 阶段 1 真机验收抓到的真缺陷）：
        #:   ★ 原实现只在 `sw_connect.get_com_member` 上挂钩子 ——
        #:   ★★ 而全仓 COM 调用有**三种写法**（实测计数）：
        #:      · `get_com_member(obj, "X", ...)`  **1141** 处 ✓ 钩子看得见
        #:      · `call_com_member(obj, "X", ...)`  **48** 处 ✓ 看得见
        #:      · **直接属性访问** `obj.FeatureManager.Yyy(...)`  **562** 处 ✗ **看不见**
        #:   ⇒ ★ 真机后果：`extrude_boss`（`model.FeatureManager.FeatureExtrusion3(...)`）
        #:     与 `chamfer`（`model.FeatureManager.InsertFeatureChamfer(...)`）
        #:     都走**第三种** ⇒ 计数恒 **0** ⇒ ★★ **SC-009 会假绿**
        #:     （★ 而它们**真的写了** —— 体积 120000 就是证据）。
        #:   ⇒ ★★ **改判据**：以**工具层的效应声明**为准（★ `reg[tool].effect`），
        #:     **而不是**靠成员名的动词去猜。★ 那才是「这个工具会不会写」的权威答案。
        #:   ★ 保留成员级钩子作**辅助证据**（`member_writes`）。
        before = COUNTER.count()
        COUNTER.arm()
        member_before = COUNTER.count()
        try:
            args = dict(st.params)
            #: ★★ 注入宿主走 `inject_objects=` 形参（★ **不是**普通实参）——
            #:   实测（2026-10-12）：第一版把 `model` 当普通参数传 ⇒
            #:   `tool_caller.call` 报「★ 声明注入 'model' 但没给对应对象」
            #:   （★ 它的签名是 `call(tool_name, *, inject_objects=None, **params)`）
            inject_objs = None
            d = reg.get(st.tool)
            if d is not None and d.inject and host:
                inject_objs = {d.inject: host.get(d.inject)}
            #: ④ 只走 `solidworks_*` 全名
            ok, out = tool_caller.call(st.tool, inject_objects=inject_objs, **args)
            rec.result = str(out)[:400]
            if not ok:
                rec.error = rec.result
        except Exception as exc:  # noqa: BLE001
            rec.error = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        finally:
            COUNTER.disarm()
        #: ★★ 判据 = **工具层效应**（★ 权威）+ 成员级钩子（★ 辅助证据）
        #:   · 工具声明 `write` ⇒ **计 1 次写**（★ 无论钩子看没看见）
        #:   · 工具声明 `read`  ⇒ 只信钩子（★ 真写了说明声明错了）
        member_writes = COUNTER.count() - member_before
        eff = reg.get(st.tool).effect if reg.get(st.tool) else "unknown"
        if eff == "write":
            rec.com_write_count = max(1, member_writes)
        else:
            rec.com_write_count = member_writes
        rec.effect = eff
        rec.member_writes = member_writes
        records.append(rec)
        if rec.error:
            break

    return {
        "ok": not any(r.error for r in records),
        "code": "",
        "detail": "",
        "records": records,
        "com_write_total": COUNTER.count(),
        "plan_method": getattr(plan, "method_id", ""),
    }


def records_to_dicts(records: list[ExecutionRecord]) -> list[dict]:
    return [
        {
            "step": r.step,
            "tool": r.tool,
            "params": r.params,
            "intent_at": r.intent_at,
            "result": r.result,
            "com_write_count": r.com_write_count,
            "effect": r.effect,
            "member_writes": r.member_writes,
            "error": r.error,
        }
        for r in records
    ]
