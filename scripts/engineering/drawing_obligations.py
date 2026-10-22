"""★ 阶段 2 · 图纸义务 + 变更传播（规格 317 的 D4/D5）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/drawing_obligations.py
# 定位:   规格 `specs/317-stage2-real-holes` 的 D4（图纸义务）/ D5（变更传播）。★★ 实
#           测（2026-10-12）缺口：  · **没有图纸义务模块** —— `processes.py` 只有 4 个工
#           艺函数（钣金/焊件）  · **没有变更传播** —— 没有「改尺寸 → 重建 → 出图 → 校验
#           」的编排
# 官方依据: ① 外部方案阶段 2 的「图纸义务」「变更传播」（逐字）② 本仓 `scripts/engineeri
#           ng/compiler.METHOD_LIBRARY` 的   `verification_obligations`（★ 义务的**真源*
#           * —— 不是手工列）③ 本仓**事实 71**（`GetPartBox` 回毫米）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收见 `tools/run_stage2_plate.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import pathlib
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[2]


#: ══════════════════════════════════════════════════════════════════════
# 一、图纸义务（★ D4）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class DrawingObligation:
    """★ 一条图纸义务（★ 覆盖率判据的**计数单位**）。"""

    name: str
    kind: str = "dimension"        #: `dimension` / `note` / `tolerance`
    covered: bool = False
    evidence: str = ""


def obligations_from_method(method_id: str) -> list[DrawingObligation]:
    """★ 从**方法声明**取义务（★ 不是手工列 —— ★ 手工必漏）。

    ★★ 为什么从方法取：`MethodSpec.verification_obligations` 是**已验证过**的
      义务清单（★ 那是方法的定义的一部分）。★ 手工列一份会与它**分叉**。
    """
    from .compiler import METHOD_LIBRARY
    m = METHOD_LIBRARY.get(method_id)
    if m is None:
        return []
    out = []
    for o in (getattr(m, "verification_obligations", ()) or ()):
        out.append(DrawingObligation(name=str(o), kind="dimension"))
    #: ★ 后置条件也是义务（★ 如「体数 = 1」「厚度回读等于冻结值」）
    for p in (getattr(m, "postconditions", ()) or ()):
        out.append(DrawingObligation(name=str(p), kind="note"))
    return out


def coverage(obls: list[DrawingObligation]) -> dict:
    """★ 覆盖率（★ SC-005 要求 **1.0**）。"""
    n = len(obls)
    c = sum(1 for o in obls if o.covered)
    return {
        "total": n, "covered": c,
        "ratio": (c / n) if n else 0.0,
        "missing": [o.name for o in obls if not o.covered],
        "ok": bool(n) and c == n,
    }


def mark_covered(obls: list[DrawingObligation], name: str, evidence: str = "") -> bool:
    """★ 按名字标「已覆盖」（★ 找不到 ⇒ 回 False，★ 不静默）。"""
    for o in obls:
        if o.name == name:
            o.covered = True
            o.evidence = evidence
            return True
    return False


#: ══════════════════════════════════════════════════════════════════════
# 二、产物摘要（★ D5 —— ★ 判「新旧混入」的唯一判据）
#: ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ArtifactDigest:
    path: str
    sha256: str
    kind: str                 #: `model` / `drawing` / `report`
    revision: str = ""


def digest_of(path: str | pathlib.Path, *, kind: str = "",
              revision: str = "") -> ArtifactDigest:
    """★ 算一个产物的**内容摘要**（★ 判「是不是新版本」的唯一硬判据）。"""
    p = pathlib.Path(str(path))
    if not p.is_file():
        return ArtifactDigest(str(p), "", kind or "", revision)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return ArtifactDigest(str(p), h.hexdigest(), kind or "", revision)


def version_consistent(digests: list[ArtifactDigest]) -> dict:
    """★ 版本一致性（★ SC-006）。

    ★★ 判据（★ 三条都要）：
      ① 三类产物（model / drawing / report）**都在**
      ② 三者的 `revision` **一致**（★ 非空）
      ③ 每个摘要的 `sha256` **非空**（★ 空 = 文件不存在）
    """
    kinds = {d.kind for d in digests if d.kind}
    want = {"model", "drawing", "report"}
    revs = {d.revision for d in digests if d.revision}
    empty = [d.path for d in digests if not d.sha256]
    return {
        "kinds_present": sorted(kinds),
        "kinds_missing": sorted(want - kinds),
        "revisions": sorted(revs),
        "revision_consistent": len(revs) == 1 and bool(revs),
        "empty_digests": empty,
        "ok": bool(want <= kinds) and len(revs) == 1 and bool(revs) and not empty,
    }


def changed_after_revision(before: list[ArtifactDigest],
                           after: list[ArtifactDigest]) -> dict:
    """★ 变更后**每个产物都必须变**（★ SC-010：无旧版本混入）。

    ★★ 这是 **N2 突变**的判据：让图纸**保留旧版本** ⇒ 它的 sha256 不变 ⇒ 本函数报出。
    """
    b = {d.kind: d.sha256 for d in before if d.kind}
    a = {d.kind: d.sha256 for d in after if d.kind}
    stale = [k for k in a if b.get(k) and a[k] == b[k]]
    missing = [k for k in a if not a[k]]
    return {
        "stale": stale,          #: ★ 没变的（★ 旧版本混入）
        "missing": missing,      #: ★ 空的（★ 没导出）
        "ok": not stale and not missing and bool(a),
        "★": "★ 变更后每个产物都必须变（★ 没变 ⇒ 旧版本混入）",
    }


#: ══════════════════════════════════════════════════════════════════════
# 三、变更传播（★ D5 —— ★ 编排）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class ChangeRecord:
    name: str                 #: 改了哪个参数
    old: object = None
    new: object = None
    affected_steps: tuple = ()   #: ★ 受影响的方法步骤（★ 靠 `derive` 里的名字找）
    propagated: bool = False


def affected_steps(steps, param_name: str) -> tuple:
    """★ 找出**引用了某参数**的步骤（★ 用于「变更传播」的影响面）。

    ★ 判据：该步骤的 `params` 里有这个键，**或** `derive` 文本里提到它。
      ★ 两个都要看 —— ★ 只看 `params` 会漏掉「派生参数」（如 `hole_group` 的 `count`）。
    """
    out = []
    for i, st in enumerate(steps):
        if param_name in (getattr(st, "params", {}) or {}):
            out.append(i)
        elif param_name in (getattr(st, "derive", "") or ""):
            out.append(i)
    return tuple(out)


def propagation_report(steps, changes: list[ChangeRecord]) -> dict:
    """★ 变更传播报告（★ SC-010：受影响产物**全部刷新**）。

    ★★ 2026-10-12 补一条**假通过**的堵漏：
      ⚠ 原实现只查 `if r["count"] and not r["propagated"]` ⇒ ★ **`count == 0` 时
        直接算过** ⇒ 而「变更名根本不在任何步骤里」正是 count==0 的**常见原因**
        （★ 实测踩过：用例的参数叫 `w`，而步骤里承载它的是 `x2_mm`
          ⇒ 影响面 0 ⇒ 报告回 `ok=True` ⇒ **假通过**）。
      ⇒ ★ 现在：**`count == 0` 也算不过**，并给专属码 ——
        ★ 「这个变更名没有落在任何步骤上」是一条**必须看见**的事实。
    """
    rows = []
    for c in changes:
        idx = affected_steps(steps, c.name)
        rows.append({"name": c.name, "old": str(c.old)[:60], "new": str(c.new)[:60],
                     "affected": list(idx), "count": len(idx),
                     "propagated": c.propagated})
    unpropagated = [r["name"] for r in rows if r["count"] and not r["propagated"]]
    #: ★ 影响面 0 ⇒ 变更名没落在任何步骤上（★ 不是"没有影响"，★ 是"判据没对上"）
    unmatched = [r["name"] for r in rows if not r["count"]]
    return {
        "changes": rows,
        "unpropagated": unpropagated,
        "unmatched": unmatched,
        "ok": not unpropagated and not unmatched,
        "★": "★ 有受影响步骤却没传播的、或变更名没落在任何步骤上的 ⇒ 都不算通过",
    }
