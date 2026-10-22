"""★ Q14 · 落点与持久化：runs 目录 + 原子提交清单 + 四类持久化（规格 327 的 T10~T15）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/runs.py
# 定位:   规格 `specs/327-release-manifest-rules-and-runs` 的 T10（`runs` 结构）/T11（
#           同卷原子重命名）/ T12（旧版本不覆盖不删除）/ T13（孤立暂存不算完成）/T14（四
#           类持久化）/ T15（B 侧薄编排入口）。★★ 实测（2026-10-12）起点：`output/runs/`
#            **存在**（460 项，★ 是阶段 326 的 `questions/`）；「旧版本不覆盖、不删除」
#           与「单写者」**已有**；★ 而**没有 `attempts/` / `checkpoints/` / `commits/`、
#           没有同卷原子重命名、没有四类持久化、没有 B 侧入口**。
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q14（L261-297）逐字：L269「一
#           期单机单写者，采用**不可变版本文件与提交清单**，  **不引入数据库**」L271-281
#            逐字给的目录图：  ```  output/runs/<run_id>/    plans/<revision>.json    in
#           terfaces/<revision>.json    questions/<revision>.json    events/<sequence>.j
#           son    attempts/<attempt_id>/...    checkpoints/<checkpoint_id>/CAD/...    c
#           heckpoints/<checkpoint_id>/evidence/...    commits/<sequence>.json  ```L283
#           「唯一权威是**完整的提交链及其引用内容**；Markdown 和状态摘要  都是**派生视
#           图**。新版本写入、校验、刷盘后，**以同卷原子重命名  发布新的提交清单**。**旧
#           版本不覆盖、不删除**。**孤立的暂存文件保留，  但没有提交记录就不能自动视作完
#           成**」L297「**任务树、接口、证据、未决问题四类均持久化**；可重建的是  派生展
#           示、调度就绪队列和 COM 对象，不是用户已批准的工程决定」L265「后续 A 只能做**
#           同一核心的另一个适配器**」
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[2]
#: ★★ **运行目录的根**（★ 默认 `output/runs`）。
#: ⚠ 实测（2026-10-12，全量 pytest）：测试**共用** `output/runs/_test-*` 这种
#:   固定名 ⇒ ★ **同一进程里跑第二遍就撞**（`overwrite`）✗ ——
#:   ★ 而单独跑那一份**全绿** ⇒ ★ 「顺序/状态泄漏」看起来像「偶发」。
#: ⇒ ★ 判据：**根可注入**（★ `set_runs_root()`），★ 测试用 `tmp_path` 隔离。
RUNS = ROOT / "output" / "runs"


def set_runs_root(path: pathlib.Path | str) -> None:
    """★★ **换运行目录的根**（★ 测试隔离用 —— ★ 见 `RUNS` 的实测记录）。"""
    global RUNS                                                         # noqa: PLW0603
    RUNS = pathlib.Path(path)


def reset_runs_root() -> None:
    """★ 恢复默认根。"""
    global RUNS                                                         # noqa: PLW0603
    RUNS = ROOT / "output" / "runs"

#: ★★ Q14 L271-281 逐字给的**七个子目录**
RUN_SUBDIRS = ("plans", "interfaces", "questions", "events", "attempts",
               "checkpoints", "commits")

#: ★★ Q14 L297 逐字要持久化的**四类**
PERSISTED_KINDS = ("task_tree", "interfaces", "evidence", "open_questions")

#: ★ 可重建的（★ Q14 L297 逐字：「可重建的是派生展示、调度就绪队列和
#:   COM 对象」）—— ★ **不持久化**
REBUILDABLE = ("derived_views", "scheduler_ready_queue", "com_objects")


class RunError(Exception):
    """★ 运行目录失败（★ 带封闭码）。"""

    CODES = ("missing-subdir", "no-commit", "overwrite", "missing-kind",
             "bad-sequence")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法运行拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


def run_dir(run_id: str) -> pathlib.Path:
    return RUNS / run_id


def init_run(run_id: str) -> dict:
    """★ **建一个运行目录**（★ T10 —— ★ Q14 L271-281 的图）。"""
    d = run_dir(run_id)
    made = []
    for sub in RUN_SUBDIRS:
        p = d / sub
        p.mkdir(parents=True, exist_ok=True)
        made.append(sub)
    return {"run_id": run_id, "path": str(d), "subdirs": made,
            "n": len(made)}


def check_structure(run_id: str) -> dict:
    """★ **目录结构检查**（★ T10）。"""
    d = run_dir(run_id)
    have = {s: (d / s).is_dir() for s in RUN_SUBDIRS}
    miss = [s for s, ok in have.items() if not ok]
    return {"ok": not miss, "missing": miss, "have": have,
            "n": len(RUN_SUBDIRS)}


#: ══════════════════════════════════════════════════════════════════════
# 一、原子写（★ T11/T12 —— ★ Q14 L283）
#: ══════════════════════════════════════════════════════════════════════

def atomic_write(path: pathlib.Path, payload) -> dict:
    """★★ **同卷原子重命名发布**（★ T11 —— ★ Q14 L283 逐字）。

    ★★ Q14 L283 逐字：「新版本写入、校验、刷盘后，**以同卷原子重命名发布
      新的提交清单**」。

    ★★ 判据（★ 三条）：
      ```
      ① 先写**临时名**（★ 同目录 ⇒ 同卷）
      ② 再 `Path.replace`（★ 同卷原子重命名）
      ③ ★★ **旧版本不覆盖** —— ★ 目标已存在 ⇒ **拒**（★ Q14 L283）
      ```
    """
    if path.exists():
        raise RunError("overwrite",
                       "★★ %s 已存在 ⇒ **旧版本不覆盖**（★ Q14 L283 逐字）"
                       % path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / (".tmp-" + path.name)
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    tmp.replace(path)          #: ★ 同卷原子重命名
    return {"path": str(path), "atomic": True, "overwrote": False}


def write_revision(run_id: str, kind: str, revision: str, payload) -> dict:
    """★ 写一个**不可变版本文件**（★ T12 —— ★ Q14 L283 逐字）。"""
    if kind not in RUN_SUBDIRS:
        raise RunError("missing-subdir", "★ 未知子目录：%r" % kind)
    return atomic_write(run_dir(run_id) / kind / ("%s.json" % revision),
                        payload)


def write_event(run_id: str, sequence: int, payload) -> dict:
    """★ 写一个事件（★ Q14 L271-281 的 `events/<sequence>.json`）。"""
    if sequence < 0:
        raise RunError("bad-sequence", "★ 序号必须 ≥0")
    return atomic_write(run_dir(run_id) / "events" / ("%06d.json" % sequence),
                        payload)


#: ══════════════════════════════════════════════════════════════════════
# 二、提交清单（★ T13 —— ★ Q14 L283）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class Commit:
    """★ **一条提交记录**（★ Q14 L283 逐字：「唯一权威是**完整的提交链及其
    引用内容**」）。"""

    sequence: int = 0
    references: list = field(default_factory=list)   #: ★ 引用的文件（相对路径）
    note: str = ""

    def to_dict(self) -> dict:
        return {"sequence": self.sequence,
                "references": list(self.references), "note": self.note}


def commit(run_id: str, sequence: int, references: list,
           note: str = "") -> dict:
    """★★ **发布一条提交清单**（★ Q14 L283 逐字）。"""
    c = Commit(sequence=sequence, references=list(references), note=note)
    p = run_dir(run_id) / "commits" / ("%06d.json" % sequence)
    atomic_write(p, c.to_dict())
    return {"ok": True, "commit": c.to_dict(), "path": str(p)}


def load_commits(run_id: str) -> list:
    """★ 读**完整提交链**（★ Q14 L283：「唯一权威是完整的提交链」）。"""
    d = run_dir(run_id) / "commits"
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.glob("*.json")):
        out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def is_complete(run_id: str, artifact: str) -> dict:
    """★★ **孤立暂存不算完成**（★ T13 —— ★ Q14 L283 逐字）。

    ★★ Q14 L283 逐字：「**孤立的暂存文件保留，但没有提交记录就不能自动
      视作完成**」。

    ★★ 判据：**文件在盘上** ≠ **有提交记录引用它** —— ★ 两者都要。
    """
    p = run_dir(run_id) / artifact
    on_disk = p.is_file()
    referenced = any(artifact in (c.get("references") or [])
                     for c in load_commits(run_id))
    return {"artifact": artifact, "on_disk": on_disk,
            "referenced": referenced,
            "complete": on_disk and referenced,
            "★": ("★★ **孤立暂存不算完成**（★ Q14 L283）："
                  "在盘上=%s · 被提交引用=%s" % (on_disk, referenced))}


#: ══════════════════════════════════════════════════════════════════════
# 三、四类持久化（★ T14 —— ★ Q14 L297）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **四类 → 落在哪个子目录**（★ Q14 L297 逐字）
KIND_TO_SUBDIR = {
    "task_tree": "plans",
    "interfaces": "interfaces",
    "evidence": "checkpoints",
    "open_questions": "questions",
}


def persist(run_id: str, kind: str, revision: str, payload) -> dict:
    """★★ **四类持久化**（★ T14 —— ★ Q14 L297 逐字）。

    ★★ Q14 L297 逐字：「**任务树、接口、证据、未决问题四类均持久化**；
      可重建的是派生展示、调度就绪队列和 COM 对象，
      **不是用户已批准的工程决定**」。

    ★★ 判据：**四类各落一个子目录**；★ 且**可重建的三类不许走这条路**。
    """
    if kind in REBUILDABLE:
        raise RunError(
            "missing-kind",
            "★ %r 是**可重建**的（★ Q14 L297）⇒ **不持久化**" % kind)
    if kind not in PERSISTED_KINDS:
        raise RunError("missing-kind", "★ 未知持久化类别：%r" % kind)
    sub = KIND_TO_SUBDIR[kind]
    return write_revision(run_id, sub, revision, payload)


def check_persistence(run_id: str) -> dict:
    """★ **四类是否都持久化过**（★ T14）。"""
    d = run_dir(run_id)
    have = {}
    for kind, sub in KIND_TO_SUBDIR.items():
        sd = d / sub
        have[kind] = bool(sd.is_dir() and list(sd.glob("*.json")))
    return {"ok": all(have.values()), "have": have,
            "missing": [k for k, v in have.items() if not v],
            "★": "★ Q14 L297：四类均持久化（★ 可重建的三类不走这条路）"}


#: ══════════════════════════════════════════════════════════════════════
# 四、B 侧薄编排入口（★ T15 —— ★ Q14 L265）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **B 侧入口复用的是同一个核心**（★ Q14 L265 逐字：「后续 A 只能做
#:   **同一核心的另一个适配器**」）
SHARED_CORE = ("engineering.registry", "engineering.protocols",
               "engineering.decisions", "engineering.rule_service",
               "engineering.recovery", "engineering.catalog",
               "engineering.authorization", "engineering.executor")

#: ★★ **它不许另建的**（★ Q14 L265 逐字：「**不先启用其 UI 和另一套规划循环**」）
NOT_ALLOWED_TO_BUILD = ("ui", "second_planning_loop", "second_state_system",
                        "second_rule_system")


def thin_orchestrator(*, reuses_core: list,
                      builds: list) -> dict:
    """★★ **B 侧薄编排入口的判据**（★ T15 —— ★ Q14 L265 逐字）。

    ★★ 判据（★ 两条）：
      ```
      ① **必须复用同一核心**（★ 至少复用 3 个核心模块）
      ② ★★ **不许另建** UI / 第二套规划循环 / 第二套状态或规则体系
      ```
    """
    bad = [b for b in builds if b in NOT_ALLOWED_TO_BUILD]
    reused = [m for m in reuses_core if m in SHARED_CORE]
    return {
        "ok": not bad and len(reused) >= 3,
        "reused": reused, "reused_n": len(reused),
        "forbidden_built": bad,
        "reason": ("★★ 不许另建 %s（★ Q14 L265：「不先启用其 UI 和另一套规划循环」）"
                   % bad if bad else
                   ("" if len(reused) >= 3 else
                    "★ 只复用了 %d 个核心模块（★ 要 ≥3）" % len(reused))),
        "★": "★ 复用同一规划核心（★ Q14 L265：「同一核心的另一个适配器」）",
    }


def core_status() -> dict:
    """★ 检查**共享核心**是否都在。"""
    import importlib                                                    # noqa: PLC0415
    have = {}
    for m in SHARED_CORE:
        try:
            importlib.import_module(m)
            have[m] = True
        except Exception:                                               # noqa: BLE001
            have[m] = False
    return {"ok": all(have.values()), "have": have,
            "n": len(SHARED_CORE),
            "missing": [k for k, v in have.items() if not v]}
