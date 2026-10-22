"""★ 阶段 6 · 可调连杆：闭环求解 + 分支 + 奇异 + 连续性（规格 321 的 L1~L4）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/linkage.py
# 定位:   规格 `specs/321-stage6-adjustable-linkage` 的 L1（闭环求解）/L2（分支标识）/
#            L3（奇异区间）/ L4（采样证据判定）。★★ 实测（2026-10-12）起点：`part_loop.D
#           ofPlan` 已有`is_acceptable()`（★ 逐字「**有意保留自由度必须标注**，**不机械
#           要求全锁死**」）与 `add_intentional_dof`（★ 理由必填）；`assembly.Constraint
#           Graph.verdict()` 已有五档；`assembly.InterferenceScan.verdict()` 已有三结论
#           。★ 而**没有平面四杆闭环求解器、没有分支标识、没有奇异检测、  没有「采样证据
#            ⇒ INDETERMINATE」**。
# 官方依据: ① 外部方案阶段 6 的验收 S6（逐字）② 外部方案 §5 R6 ④ 逐字：「**将一切图中有
#           环都拒绝，正确闭链正例   必须失败**，以防『**保守到失去能力**』」⇒ ★ 本模块
#           的核心判据是   **正例必须能过**，★ 不是「把所有环都拒掉」③ `scripts/engineer
#           ing/part_loop.py` 的 `DofPlan.is_acceptable()`④ `scripts/engineering/rule_ve
#           rdicts.py` 的 `INDETERMINATE` / `BLOCKED_VERIFICATION`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（★ 本模块是**纯数学**，无真机依赖）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math
from dataclasses import dataclass, field

#: ══════════════════════════════════════════════════════════════════════
# 一、封闭码
#: ══════════════════════════════════════════════════════════════════════

PASS = "pass"
FAIL = "fail"
INDETERMINATE = "INDETERMINATE"
BLOCKED_VERIFICATION = "BLOCKED_VERIFICATION"
LINKAGE_CODES = (PASS, FAIL, INDETERMINATE, BLOCKED_VERIFICATION)

#: ★★ **两个装配分支**（★ L2 —— ★ 同一个闭环有两个解）
BRANCH_OPEN = "open"          #: ★ 开口式：`θ4 ∈ (0, π)`
BRANCH_CROSSED = "crossed"    #: ★ 交叉式：`θ4 ∈ (π, 2π)`
BRANCHES = (BRANCH_OPEN, BRANCH_CROSSED)

#: ★ 默认残差容差（mm）—— ★ 冻结值
DEFAULT_TOL_MM = 1e-6


try:
    from ._coded_error import CodedError
except ImportError:
    from _coded_error import CodedError


class LinkageError(CodedError):
    """★ 连杆求解失败（★ 带封闭码）。"""

    CODES = ("not-closed", "no-solution", "bad-branch", "bad-lengths")
    ASSERT_LABEL = "★ 非法连杆拒绝码"


#: ══════════════════════════════════════════════════════════════════════
# 二、平面四杆闭环求解（★ L1 —— ★ 独立算，不靠 CAD）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class FourBar:
    """★ 平面四杆：曲柄 `a` · 连杆 `b` · 摇杆 `c` · 机架 `d`。"""

    a: float = 40.0       #: ★ 曲柄（★ 主动件）
    b: float = 120.0      #: ★ 连杆
    c: float = 80.0       #: ★ 摇杆
    d: float = 150.0      #: ★ 机架

    def __post_init__(self) -> None:
        for nm in ("a", "b", "c", "d"):
            if getattr(self, nm) <= 0:
                raise LinkageError("bad-lengths", "★ %s 必须 > 0" % nm)

    @property
    def grashof(self) -> bool:
        """★ **Grashof 条件**：最短 + 最长 ≤ 其余两之和。

        ★ 判据（★ 决定**曲柄能不能整周回转**）：
          · 满足 ⇒ 有整转副（★ 曲柄摇杆 / 双曲柄 / 双摇杆）
          · 不满足 ⇒ **只能摆动**（★ 没有整转副）
        """
        ls = sorted([self.a, self.b, self.c, self.d])
        return (ls[0] + ls[3]) <= (ls[1] + ls[2])

    def coupler_point(self, theta2: float, branch: str = BRANCH_OPEN) -> tuple:
        """★ 由**曲柄角**算**连杆上某点**（★ 本函数只回 `B` 点：曲柄端点）。

        ★ 判据：`B = A + a·(cosθ2, sinθ2)`（★ 固定铰 `A` 在原点）。
        """
        return (self.a * math.cos(theta2), self.a * math.sin(theta2))


@dataclass
class FourBarSolution:
    theta2: float = 0.0
    theta3: float = 0.0          #: ★ 连杆角
    theta4: float = 0.0          #: ★ 摇杆角
    branch: str = BRANCH_OPEN
    residual: float = 0.0
    ok: bool = False

    def to_dict(self) -> dict:
        return {"theta2_deg": round(math.degrees(self.theta2), 6),
                "theta3_deg": round(math.degrees(self.theta3), 6),
                "theta4_deg": round(math.degrees(self.theta4), 6),
                "branch": self.branch,
                "residual_mm": self.residual,
                "ok": self.ok}


def solve_four_bar(fb: FourBar, theta2: float, *,
                   branch: str = BRANCH_OPEN,
                   tol_mm: float = DEFAULT_TOL_MM) -> FourBarSolution:
    """★★ **闭环求解**（★ L1 —— ★ 用**解析法**，★ 不靠 CAD）。

    ★★ 原理（★ 标准四杆闭环解析解）：
      ```
      B = (a·cosθ2, a·sinθ2)                 ← 曲柄端点
      从 B 到 D=(d, 0) 的连杆 + 摇杆闭合成三角形：
        b² = ...  ⇒  K1 = d/a, K2 = d/c, K3 = (a²−b²+c²+d²)/(2ac)
        A = cosθ2 − K1 − K2·cosθ2 + K3
        B_ = −2·sinθ2
        C_ = K1 − (K2+1)·cosθ2 + K3
        θ4 = 2·atan2(−B_ ∓ √(B_²−4A·C_), 2A)   ← ★★ **± 就是两个分支**
      ```
    ★★ **两个分支的判据**（★ L2）：判别式的 **±** 号 ——
      ★ `+` ⇒ `open` · `−` ⇒ `crossed`（★ 反之亦然，★ 由 `θ4` 落在哪个半区定）。
    ★★ **残差**：把解代回闭环方程算**实际闭合误差**（★ 不是「解出来了就算对」）。
    """
    if branch not in BRANCHES:
        raise LinkageError("bad-branch", "★ 未知分支：%r" % branch)

    a, b, c, d = fb.a, fb.b, fb.c, fb.d
    K1 = d / a
    K2 = d / c
    K3 = (a * a - b * b + c * c + d * d) / (2.0 * a * c)

    A_ = math.cos(theta2) - K1 - K2 * math.cos(theta2) + K3
    B_ = -2.0 * math.sin(theta2)
    C_ = K1 - (K2 + 1.0) * math.cos(theta2) + K3

    disc = B_ * B_ - 4.0 * A_ * C_
    if disc < 0:
        #: ★ 判别式 < 0 ⇒ **这个曲柄角下装不起来**（★ 不是"解错了"）
        raise LinkageError(
            "no-solution",
            "★ θ2=%g° 下闭环无解（判别式 %.6f < 0）" % (math.degrees(theta2), disc))

    root = math.sqrt(disc)
    #: ★★ **两个分支**：判别式的 ± 号。
    #:   ⚠ 实测（2026-10-12）：`±` 与「θ4 落在哪个半区」的对应**不是固定**的 ——
    #:     它随连杆尺寸变。⇒ ★ 不能把 `sign` 与分支**硬绑**，
    #:     ★ 而要**两个都算、再按 `branch_of` 挑**（★ 那才是分支的**定义**）。
    cands = []
    for sg in (1.0, -1.0):
        t4 = 2.0 * math.atan2(-B_ + sg * root, 2.0 * A_)
        bx = a * math.cos(theta2)
        by = a * math.sin(theta2)
        cx = d + c * math.cos(t4)
        cy = c * math.sin(t4)
        dx = cx - bx
        dy = cy - by
        t3 = math.atan2(dy, dx)
        res = abs(math.hypot(dx, dy) - b)
        cands.append((t3, t4, res, branch_of(fb, theta2, t4)))

    #: ★ 按**分支的定义**挑（★ 不是按 ± 号）
    picked = next((c for c in cands if c[3] == branch), None)
    if picked is None:
        raise LinkageError(
            "no-solution",
            "★ θ2=%g° 下没有 %s 分支的解（只有 %s）"
            % (math.degrees(theta2), branch,
               [c[3] for c in cands]))
    theta3, theta4, residual, _got_branch = picked

    return FourBarSolution(theta2=theta2, theta3=theta3, theta4=theta4,
                           branch=branch, residual=residual,
                           ok=residual <= tol_mm)


def branch_of(fb: FourBar, theta2: float, theta4: float) -> str:
    """★★ **由 `θ4` 判分支**（★ L2 —— ★ 判据：`θ4` 落在哪个半区）。

    ★★ 依据：两个装配分支的**几何区别**就是摇杆朝向 ——
      · `θ4 ∈ (0, π)`   ⇒ **开口式**（`open`）
      · `θ4 ∈ (π, 2π)`  ⇒ **交叉式**（`crossed`）
    """
    t = theta4 % (2.0 * math.pi)
    return BRANCH_OPEN if 0.0 < t < math.pi else BRANCH_CROSSED


#: ══════════════════════════════════════════════════════════════════════
# 三、奇异区间（★ L3）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class SingularPoint:
    theta2_deg: float = 0.0
    kind: str = "toggle"          #: `toggle` / `fold`
    margin: float = 0.0           #: ★ 判别式（★ 越小越接近奇异）


@dataclass
class SingularScan:
    points: list = field(default_factory=list)
    scanned: int = 0

    @property
    def has_singular(self) -> bool:
        return bool(self.points)


def _disc(fb: FourBar, theta2: float) -> float:
    a, b, c, d = fb.a, fb.b, fb.c, fb.d
    K1 = d / a
    K2 = d / c
    K3 = (a * a - b * b + c * c + d * d) / (2.0 * a * c)
    A_ = math.cos(theta2) - K1 - K2 * math.cos(theta2) + K3
    B_ = -2.0 * math.sin(theta2)
    C_ = K1 - (K2 + 1.0) * math.cos(theta2) + K3
    return B_ * B_ - 4.0 * A_ * C_


def singular_scan(fb: FourBar, *, samples: int = 360,
                  margin: float = 1e-3) -> SingularScan:
    """★★ **奇异区间扫描**（★ L3 —— ★ FR-005）。

    ★★ 判据：**判别式趋近 0** ⇒ 闭环接近**奇异**（★ 两分支在此**合并**）。
      · `disc ≈ 0` ⇒ **死点**（toggle，★ 传动角为 0）
      · `disc < 0` ⇒ **装不起来**（fold，★ 超出可达域）
    ★★ **必须在端点与已知危险位置检查**（★ FR-005 逐字）——
      ⇒ 本函数**额外把 `θ2=0°` 与 `180°` 两个端点也扫进去**。
    """
    pts: list[SingularPoint] = []
    angles = [2.0 * math.pi * i / samples for i in range(samples)]
    #: ★ FR-005：**端点**必须查
    for extra in (0.0, math.pi):
        if extra not in angles:
            angles.append(extra)
    for t in angles:
        dv = _disc(fb, t)
        if dv < 0:
            pts.append(SingularPoint(math.degrees(t), "fold", dv))
        elif dv <= margin:
            pts.append(SingularPoint(math.degrees(t), "toggle", dv))
    return SingularScan(points=pts, scanned=len(angles))


#: ══════════════════════════════════════════════════════════════════════
# 四、连续性判定（★ L4 —— ★ FR-007/009）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class ContinuityVerdict:
    verdict: str = PASS
    run_state: str = ""
    coverage: float = 0.0
    is_full_domain_proof: bool = False
    releasing: bool = False
    reason: str = ""

    def __post_init__(self) -> None:
        assert self.verdict in LINKAGE_CODES, "★ 非法判定：%r" % self.verdict


def continuity_verdict(*, order_requires_continuous: bool,
                       is_full_domain_proof: bool,
                       sampled: int = 0,
                       uncovered: int = 0,
                       interferences: list | None = None) -> ContinuityVerdict:
    """★★ **连续性判定**（★ L4 —— ★ FR-007/009）。

    ★★ 判据顺序（★ **最严的在前**）：
      ```
      ① 检出干涉                      ⇒ FAIL（★ 必须解释）
      ② 订单要求连续 且 只有采样证据  ⇒ INDETERMINATE + BLOCKED_VERIFICATION
                                        （★ **不能自动交付**）
      ③ 有未覆盖区间                  ⇒ INDETERMINATE + BLOCKED_VERIFICATION
      ④ 有全域证明                    ⇒ PASS
      ⑤ 其余（没要求连续、也没覆盖缺口）⇒ PASS
      ```
    ★★ **② 是本模块的核心**：★ 外部方案逐字「若订单要求连续无干涉但只有采样证据，
      验证结果必须为 `INDETERMINATE`，运行状态为 `BLOCKED_VERIFICATION`，
      **不能自动交付**」。
    ★★ **为什么 ③ 与 ② 一样严**：★ 有未覆盖区间 ⇒ 那是**已知的洞**，
      ★ 比"只有采样"更明确 —— ★ 更要挡住。
    """
    if interferences:
        return ContinuityVerdict(
            FAIL, "", 0.0, False, False,
            "★ 检出干涉 %d 处 ⇒ 必须解释（★ 不能当无干涉）" % len(interferences))

    total = sampled + uncovered
    cov = (sampled / total) if total > 0 else 0.0

    if order_requires_continuous and not is_full_domain_proof:
        return ContinuityVerdict(
            INDETERMINATE, BLOCKED_VERIFICATION, cov, False, False,
            "★★ 订单要求**连续无干涉**，而只有**采样证据** ⇒ "
            "`INDETERMINATE` + `BLOCKED_VERIFICATION`（★ **不能自动交付**）")

    if uncovered:
        return ContinuityVerdict(
            INDETERMINATE, BLOCKED_VERIFICATION, cov, False, False,
            "★ 有 %d 个**未覆盖区间** ⇒ 不能自动交付" % uncovered)

    return ContinuityVerdict(
        PASS, "", cov, is_full_domain_proof, True,
        "★ 无干涉、无未覆盖区间 ⇒ 放行")


#: ══════════════════════════════════════════════════════════════════════
# 五、整体验收（★ S6）
#: ══════════════════════════════════════════════════════════════════════

def evaluate_linkage(fb: FourBar, theta2: float, *,
                     branch: str = BRANCH_OPEN,
                     target_dof: int = 1,
                     actual_dof: int = 1,
                     intentional_dof: list | None = None,
                     order_requires_continuous: bool = False,
                     is_full_domain_proof: bool = False,
                     sampled: int = 360, uncovered: int = 0,
                     interferences: list | None = None,
                     tol_mm: float = DEFAULT_TOL_MM) -> dict:
    """★★ **连杆机构的整体判定**（★ S6）。

    ★★ 判据（★ 五项都要）：
      ① 闭环**有解**且**残差在容差内**
      ② **分支**与请求的一致
      ③ **目标自由度 == 实际自由度**
      ④ 有自由度时**逐条标注了理由**（★ 复用 `DofPlan` 的纪律）
      ⑤ 连续性判定（★ FR-007：采样 ⇒ `INDETERMINATE`）
    """
    out: dict = {}

    #: ① 闭环
    try:
        sol = solve_four_bar(fb, theta2, branch=branch, tol_mm=tol_mm)
        out["solution"] = sol.to_dict()
        out["residual_ok"] = sol.ok
    except LinkageError as e:
        out["solution"] = None
        out["residual_ok"] = False
        out["solve_error"] = "%s: %s" % (e.code, e.detail)

    #: ② 分支
    if out.get("solution"):
        got_branch = branch_of(fb, theta2, math.radians(out["solution"]["theta4_deg"]))
        out["branch"] = got_branch
        out["branch_ok"] = (got_branch == branch)
    else:
        out["branch"] = ""
        out["branch_ok"] = False

    #: ③ 自由度
    out["target_dof"] = int(target_dof)
    out["actual_dof"] = int(actual_dof)
    out["dof_ok"] = int(target_dof) == int(actual_dof)

    #: ④ 有意保留自由度必须标注理由（★ 复用 `DofPlan` 的纪律）
    motions = list(intentional_dof or ())
    if actual_dof > 0:
        out["dof_annotated"] = bool(motions) and all(
            str(m.get("why", "")).strip() for m in motions)
    else:
        out["dof_annotated"] = True

    #: ⑤ 连续性
    cv = continuity_verdict(order_requires_continuous=order_requires_continuous,
                            is_full_domain_proof=is_full_domain_proof,
                            sampled=sampled, uncovered=uncovered,
                            interferences=interferences)
    out["continuity"] = {"verdict": cv.verdict, "run_state": cv.run_state,
                         "coverage": round(cv.coverage, 6),
                         "releasing": cv.releasing, "reason": cv.reason}

    #: ★ 奇异（★ 报告用 —— ★ 不直接判失败，★ 由"指定区间义务"决定）
    ss = singular_scan(fb, samples=min(360, max(36, sampled)))
    out["singular"] = {"count": len(ss.points), "scanned": ss.scanned,
                       "kinds": sorted({p.kind for p in ss.points})}

    out["ok"] = bool(out.get("residual_ok") and out.get("branch_ok")
                     and out.get("dof_ok") and out.get("dof_annotated")
                     and cv.releasing)
    out["★"] = ("★ 五项：闭环残差 + 分支对 + 自由度对 + 自由度已标注 + 连续性放行"
                "（★ **正确闭链正例必须能过** —— ★ 不许「保守到失去能力」）")
    return out
