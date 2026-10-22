"""★ 任意草图的**几何关系生成器** —— 从轮廓**测**出关系，不查形状表。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/sketch_relations_gen.py
# 定位:   规格 `specs/330-sketch-relation-generator` —— **通用几何关系生成器**。★★ 触
#           发它的是 2026-10-12 业主批注 3（原话）：「像你这个形状关系，你这里是**写死的
#           **……你现在换一个 L 型是这样的  一个逻辑，那改天换一个比较奇怪的形状呢？你比
#           如说换一个 **U 型**呢，  换一个 **H 型**呢？**你不能每一次都凭大语言模型本身
#           去分析**，  你应该有一个**几何关系的生成器**，或者是一个库，或者是什么其他的
#           方案。  ……就给你一个**任意的草图**，就哪怕比如说一个 **X 形状**的横截面，  
#           这个 X 形状它就比较复杂了，它**没有任何一条线是水平的或者是竖直的**，  但是
#           它也互相是有各种关系的，比如说 X 的**长边和短边是垂直的**，  X **两边的线应
#           该是共线的**……  ★ 像这种**硬编码**的形式去生成形状关系是一种很蠢、  而且很容
#           易就覆盖不了一些特殊情况的做法。」
#
#           ★★ 判据（本模块的设计公理）：
#             **关系是从「轮廓的几何量测」推出来的，不是从「形状名字」查出来的。**
#             ★ 输入 = 顶点坐标 + 段类型（线/弧）；★ 输出 = 关系清单 + 尺寸需求 + 自由度账。
#             ★ 所以 U/H/X/星形/任意多边形**走同一条代码路径**。
#
# 官方依据: ① SolidWorks 官方  [草图状态](https://help.solidworks.com/2026/Chinese-simpl
#           ified/SolidWorks/acadhelp/c_moving2d3d_sketch_states.htm)  逐字：「**尺寸和
#           几何关系为两种类型的约束**」⇒ ★ 两者**都要生成**。② `scripts/sw_sketch_relat
#           ions.py` 的 `RELATION_TYPES`  —— 官方 `swConstraintType_e` 逐项照录（★ 本模
#           块只**产出名字**，  派发由那个模块做 —— ★ 单一职责）。③ `specs/315-eval-corp
#           us/sketch-definition-protocol.md`（★ 本仓协议）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `verified`：★ 纯计算，无 COM；★ 自带**跨形状回归**
#   （`tests/test_sketch_relation_generator.py` 覆盖 L/U/H/X/T/矩形/带弧槽口）。
# -----------------------------------------------------------------------------
from __future__ import annotations

import math
from dataclasses import dataclass, field

#: ★ 角度容差（度）—— ★ 判定「平行/垂直/水平/竖直」的阈值
#:   ★ 为什么不是 0：★ 用户手画/程序生成的坐标**总有小误差**。
#:   ★ 1e-6 度太严（浮点噪声会漏判）；1 度太松（会把 89° 当垂直）。
#:   ★ 取 0.5° —— ★ 而**判不出来就如实说判不出**（★ 不硬凑）。
ANGLE_TOL_DEG = 0.5
#: ★ 长度容差（毫米）—— ★ 判定「等长/共线」的阈值
LEN_TOL_MM = 1e-6

#: ★★ **段类型**
LINE = "line"
ARC = "arc"


class SketchGenError(Exception):
    """★ 生成器失败（★ 带封闭码）。"""

    CODES = ("too-few-vertices", "not-closed", "bad-segment",
             "unknown-relation", "ambiguous")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法生成器拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 一、轮廓输入（★ 与形状名字无关）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class Segment:
    """★ 一段轮廓。

    ★ 判据：**只用几何量描述** —— `(x1,y1) → (x2,y2)` + 类型；
      ★ **没有**「这是 L 形的第 3 条边」这种名字。
    """

    x1: float
    y1: float
    x2: float
    y2: float
    kind: str = LINE
    #: ★ 圆弧：圆心 + 半径 + 是否逆时针（★ 直线时为 None）
    cx: float = 0.0
    cy: float = 0.0
    r: float = 0.0
    ccw: bool = True

    @property
    def dx(self) -> float:
        return self.x2 - self.x1

    @property
    def dy(self) -> float:
        return self.y2 - self.y1

    @property
    def length(self) -> float:
        if self.kind == ARC:
            #: ★ 弧长 = r × 圆心角
            a1 = math.atan2(self.y1 - self.cy, self.x1 - self.cx)
            a2 = math.atan2(self.y2 - self.cy, self.x2 - self.cx)
            d = a2 - a1
            if self.ccw:
                while d <= 0:
                    d += 2 * math.pi
            else:
                while d >= 0:
                    d -= 2 * math.pi
                d = -d
            return abs(self.r * d)
        return math.hypot(self.dx, self.dy)

    @property
    def angle_deg(self) -> float:
        """★ 方向角（0~180，★ 线段的「朝向」与正反向无关）。"""
        if self.kind == ARC:
            return float("nan")
        a = math.degrees(math.atan2(self.dy, self.dx)) % 180.0
        return a


def _ang_close(a: float, b: float, tol: float = ANGLE_TOL_DEG) -> bool:
    """★ 两个方向角是否相同（★ 模 180 ⇒ 线段正反向等价）。"""
    d = abs((a - b) % 180.0)
    return min(d, 180.0 - d) <= tol


#: ══════════════════════════════════════════════════════════════════════
# 二、关系清单（★ 输出 = 名字 + 段序号）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class Relation:
    """★ 一条几何关系。"""

    kind: str                       #: HORIZONTAL / VERTICAL / PARALLEL / …
    segs: tuple = ()                #: ★ 段序号（0 基）
    why: str = ""                   #: ★ **依据**（★ 量到了什么 ⇒ 判成这个）

    def key(self) -> str:
        return "%s:%s" % (self.kind, ",".join(str(s) for s in self.segs))

    def to_dict(self) -> dict:
        return {"kind": self.kind, "segs": list(self.segs), "why": self.why}


@dataclass
class SketchPlan:
    """★ 生成结果（★ 关系 + 尺寸需求 + 自由度账）。"""

    relations: list = field(default_factory=list)
    dimensions: list = field(default_factory=list)
    dof_before: int = 0
    dof_after: int = 0
    notes: list = field(default_factory=list)

    @property
    def fully_defined(self) -> bool:
        return self.dof_after == 0

    def to_dict(self) -> dict:
        return {
            "relations": [r.to_dict() for r in self.relations],
            "dimensions": list(self.dimensions),
            "dof_before": self.dof_before,
            "dof_after": self.dof_after,
            "fully_defined": self.fully_defined,
            "notes": list(self.notes),
        }

    def relation_string(self) -> str:
        """★ 转成 `solidworks_sketch_apply_relations` 吃的格式。"""
        return ";".join(
            "%s:%s" % (r.kind.lower(), ",".join(str(s) for s in r.segs))
            for r in self.relations)


#: ══════════════════════════════════════════════════════════════════════
# 三、★★ 核心：从几何量测推关系
#: ══════════════════════════════════════════════════════════════════════

def detect_relations(segs: list) -> list:
    """★★ **从轮廓量测出关系**（★ 不查形状表）。

    ★★ 算法（★ 五类，★ 全部基于**量测**）：
      ```
      ① 单段方向     dy≈0 ⇒ HORIZONTAL · dx≈0 ⇒ VERTICAL
      ② 相邻段      端点重合 ⇒ COINCIDENT（★ 链式绘制自带；★ 分开画的要加）
      ③ 任两段方向   夹角≈0/180 ⇒ PARALLEL · 夹角≈90 ⇒ PERPENDICULAR
      ④ 平行且共线   平行 + 端点在对方延长线上 ⇒ COLLINEAR
      ⑤ 圆弧         同半径 ⇒ EQUAL · 与相邻直线相切 ⇒ TANGENT
      ```
    ★★ 判据：**输入只有坐标** ⇒ ★ U/H/X/星形**走同一条路径**。
    """
    out: list = []
    n = len(segs)

    #: ① 单段方向
    for i, s in enumerate(segs):
        if s.kind == ARC:
            continue
        if abs(s.dy) <= LEN_TOL_MM:
            out.append(Relation("HORIZONTAL", (i,),
                                "dy=%.3g ≈ 0 ⇒ 水平" % s.dy))
        elif abs(s.dx) <= LEN_TOL_MM:
            out.append(Relation("VERTICAL", (i,),
                                "dx=%.3g ≈ 0 ⇒ 竖直" % s.dx))

    #: ② 相邻段端点重合
    for i in range(n):
        a, b = segs[i], segs[(i + 1) % n]
        if (abs(a.x2 - b.x1) <= LEN_TOL_MM
                and abs(a.y2 - b.y1) <= LEN_TOL_MM):
            out.append(Relation("COINCIDENT", (i, (i + 1) % n),
                                "第 %d 段终点 == 第 %d 段起点" % (i, (i + 1) % n)))
        else:
            out.append(Relation("COINCIDENT", (i, (i + 1) % n),
                                "★ 两端**不重合**（差 %.4g mm）⇒ 必须补这条关系"
                                % math.hypot(a.x2 - b.x1, a.y2 - b.y1)))

    #: ③ 平行 / 垂直
    for i in range(n):
        for j in range(i + 1, n):
            a, b = segs[i], segs[j]
            if a.kind == ARC or b.kind == ARC:
                continue
            aa, ab = a.angle_deg, b.angle_deg
            if _ang_close(aa, ab):
                out.append(Relation("PARALLEL", (i, j),
                                    "方向 %.2f° vs %.2f° ⇒ 平行" % (aa, ab)))
            elif _ang_close(abs(aa - ab), 90.0):
                out.append(Relation("PERPENDICULAR", (i, j),
                                    "方向 %.2f° vs %.2f° ⇒ 垂直" % (aa, ab)))

    #: ④ 共线（★ 平行 + 端点落在对方所在直线上）
    for i in range(n):
        for j in range(i + 1, n):
            a, b = segs[i], segs[j]
            if a.kind == ARC or b.kind == ARC:
                continue
            if not _ang_close(a.angle_deg, b.angle_deg):
                continue
            #: ★ 点 b 的起点到 a 所在直线的距离
            L = a.length
            if L <= LEN_TOL_MM:
                continue
            ux, uy = a.dx / L, a.dy / L
            vx, vy = b.x1 - a.x1, b.y1 - a.y1
            perp = abs(ux * vy - uy * vx)
            if perp <= LEN_TOL_MM:
                out.append(Relation("COLLINEAR", (i, j),
                                    "平行且起点到第 %d 段所在直线距离 %.3g ≈ 0 ⇒ 共线"
                                    % (i, perp)))

    #: ⑤ 圆弧：等半径 / 相切
    for i, s in enumerate(segs):
        if s.kind != ARC:
            continue
        for j in range(i + 1, n):
            t = segs[j]
            if t.kind == ARC and abs(s.r - t.r) <= LEN_TOL_MM:
                out.append(Relation("SAMELENGTH", (i, j),
                                    "两弧半径都是 %.4g ⇒ 相等" % s.r))
        for j in ((i - 1) % n, (i + 1) % n):
            t = segs[j]
            if t.kind == ARC:
                continue
            #: ★ 相切：弧的端点到直线的距离 ≈ 0 **且** 直线方向 ⊥ 半径方向
            ex, ey = (s.x1, s.y1) if j == (i - 1) % n else (s.x2, s.y2)
            L = t.length
            if L <= LEN_TOL_MM:
                continue
            ux, uy = t.dx / L, t.dy / L
            vx, vy = ex - t.x1, ey - t.y1
            if abs(ux * vy - uy * vx) <= LEN_TOL_MM:
                #: ★ 半径方向与直线方向垂直 ⇒ 相切
                rx, ry = ex - s.cx, ey - s.cy
                dot = ux * rx + uy * ry
                if abs(dot) / max(1e-12, math.hypot(rx, ry)) <= 1e-3:
                    out.append(Relation("TANGENT", (j, i),
                                        "第 %d 段与第 %d 弧在端点相切" % (j, i)))
    return out


def detect_symmetry(segs: list) -> list:
    """★ **对称检测**（★ 关于 x=0 / y=0 / 两条轴都对称）。

    ★★ 判据：**顶点集合**在镜像下**闭合** ⇒ 对称。
      ★ 这是「**任意形状**」能用的判据 —— ★ 不看形状名字，★ 只看点集。
    """
    pts = [(s.x1, s.y1) for s in segs]
    if not pts:
        return []
    out = []

    def _mirror_closed(axis: str, tol: float = 1e-6) -> bool:
        for (x, y) in pts:
            mx, my = (-x, y) if axis == "y" else (x, -y)
            if not any(abs(mx - px) <= tol and abs(my - py) <= tol
                       for (px, py) in pts):
                return False
        return True

    if _mirror_closed("y"):
        out.append(Relation("SYMMETRIC", (), "顶点集关于 **Y 轴**（x=0）镜像闭合"))
    if _mirror_closed("x"):
        out.append(Relation("SYMMETRIC", (), "顶点集关于 **X 轴**（y=0）镜像闭合"))
    return out


#: ★★ **锚定原点**扣 2（★ 官方逐字：「矩形本身**固定到原点**」）
ANCHOR_COST = 2

#: ★ 数值微分的步长（毫米）—— ★ 与 LEN_TOL_MM 同量级
#:   ⚠ 实测：整段替换时**漏了这个常量** ⇒ NameError ✗
#:     （★ 而「少一个常量」看起来像「函数写错了」）。
_FD_EPS = 1e-6


def _variables(segs: list) -> list:
    """★★ **变量向量**：★ 每段 **4 个**（起点 x,y + 终点 x,y）。

    ★★ 判据（★ 这条决定了「任意形状都能算」）：
      ★ **不假定端点已共享** —— ★ 共享是 `COINCIDENT` 关系**做出来的**，
      ★ 不是几何的先天性质（★ 分开画的 4 条线各有 2 个端点）。
    """
    out = []
    for s in segs:
        out.extend([s.x1, s.y1, s.x2, s.y2])
    return out


def _residuals(r: Relation, v: list) -> list:
    """★ 一条关系对应的**标量方程组**（★ 全 0 = 满足）。

    ★★ 判据：每个关系写成**显式方程** —— ★ 这样才能数值求导、算秩。
      ★ 「每类关系扣几分」那种说法**算不了秩**
      （★ 那正是我在这一处栽了两次的地方）。
    """
    def ep(i: int) -> tuple:
        return (v[4 * i], v[4 * i + 1]), (v[4 * i + 2], v[4 * i + 3])

    if not r.segs:
        return []
    if r.kind == "HORIZONTAL":
        (_, a), (_, b) = ep(r.segs[0])
        return [a - b]
    if r.kind == "VERTICAL":
        (a, _), (b, _) = ep(r.segs[0])
        return [a - b]
    if r.kind == "COINCIDENT":
        (_, a2), (b1, _) = ep(r.segs[0]), ep(r.segs[1])
        return [a2[0] - b1[0], a2[1] - b1[1]]
    if r.kind in ("PARALLEL", "COLLINEAR", "PERPENDICULAR"):
        (a1, a2), (b1, b2) = ep(r.segs[0]), ep(r.segs[1])
        ux, uy = a2[0] - a1[0], a2[1] - a1[1]
        vx, vy = b2[0] - b1[0], b2[1] - b1[1]
        if r.kind == "PERPENDICULAR":
            return [ux * vx + uy * vy]
        cross = ux * vy - uy * vx
        if r.kind == "PARALLEL":
            return [cross]
        wx, wy = b1[0] - a1[0], b1[1] - a1[1]
        return [cross, ux * wy - uy * wx]
    if r.kind == "SAMELENGTH":
        (a1, a2), (b1, b2) = ep(r.segs[0]), ep(r.segs[1])
        return [math.hypot(a2[0] - a1[0], a2[1] - a1[1])
                - math.hypot(b2[0] - b1[0], b2[1] - b1[1])]
    return []


def _independent(relations: list) -> list:
    """★ **去掉完全重复的关系**（★ 同 `(kind, segs)` 只留一条）。

    ★ 判据：★ 这只做**最粗的去重**；★ **真正的冗余判定交给秩**
      （★ 见 `dof_account`）—— ★ 因为手写规则追不上任意形状。
    """
    seen, out = set(), []
    for r in relations:
        if r.key() in seen:
            continue
        seen.add(r.key())
        out.append(r)
    return out


def _jacobian_rank(relations: list, v: list) -> int:
    """★★ **约束雅可比的秩** = **独立约束数**（★ 数值求秩）。

    ★★ 算法：★ 对**每个标量方程**做中心差分 ⇒ 一行 ⇒
      ★ 带容差高斯消元 ⇒ ★ 秩 = 主元数。
    ★★ 判据：★ **与形状无关、与关系种类无关** ——
      ★ 这是本模块「**不是硬编码**」的技术保证（★ 业主批注 3）。
    """
    rows: list = []
    for r in relations:
        for k in range(len(_residuals(r, v))):
            row = []
            for j in range(len(v)):
                hi, lo = list(v), list(v)
                hi[j] += _FD_EPS
                lo[j] -= _FD_EPS
                f_hi = _residuals(r, hi)[k]
                f_lo = _residuals(r, lo)[k]
                row.append((f_hi - f_lo) / (2 * _FD_EPS))
            rows.append(row)

    rank = 0
    n_row = len(rows)
    used = [False] * n_row
    for col in range(len(v)):
        piv, best = -1, 1e-6
        for i in range(n_row):
            if not used[i] and abs(rows[i][col]) > best:
                piv, best = i, abs(rows[i][col])
        if piv < 0:
            continue
        used[piv] = True
        rank += 1
        pv = rows[piv][col]
        for i in range(n_row):
            if i != piv and abs(rows[i][col]) > 1e-12:
                f = rows[i][col] / pv
                for j in range(col, len(v)):
                    rows[i][j] -= f * rows[piv][j]
    return rank


def dof_account(segs: list, relations: list, *,
                anchored: bool = True) -> dict:
    """★★ **自由度账**（★ 判「完全定义够不够」）。

    ★★ 公式（★ 判据 —— ★ **秩由数值算，不是查表**）：
      ```
      DOF = 4 × 段数                     ← ★ 每段 2 端点 × (x, y)
            − rank(J)                    ← ★ 独立约束数（★ 数值求秩）
            − 2（★ 锚定原点，若 anchored）
            − 尺寸数
      ```
    ★★ `DOF == 0` ⇒ **完全定义**；★ `> 0` ⇒ **欠定义，要补尺寸**；
      ★ `< 0` ⇒ **过定义**（★ 官方：红色）。

    ★★ 为什么必须用秩（★ 我在这一处栽了**两次**，★ 逐条记下来）：
      ```
      ① 第一版：DOF = 2×段数 − Σ「每类关系扣几分」的硬编码表
         ⇒ ★ 矩形算出「还需 0 个尺寸」✗（★ 矩形要 2 个）
      ② 第二版：改成 4×段数 + 手写冗余规则
         ⇒ ★ 矩形对了（2）· L 对了（4）
         ⇒ ★★ 但 **X 形算出 0** ✗ —— ★ 因为两两配对有 O(N²) 条关系，
            ★ 其中绝大多数**是链条推出来的、不独立**，
            ★ 手写规则**永远追不上任意形状**。
      ③ 正解：★ **数值求秩** —— ★ 与形状无关、与关系种类无关。
      ```
    ★★ 这三次尝试本身就是业主批注 3 的**实证**：
      ★ 「硬编码…很蠢，而且很容易就覆盖不了一些特殊情况」——
      ★ ①② 正是硬编码，★ ③ 才是生成器。
    """
    v = _variables(segs)
    ind = _independent(relations)
    rank = _jacobian_rank(ind, v)
    dof0 = 4 * len(segs)
    anchor = ANCHOR_COST if anchored else 0
    return {"segments": len(segs), "dof_initial": dof0,
            "relations": len(relations), "independent": len(ind),
            "redundant": len(relations) - len(ind),
            "rank": rank, "anchor_cost": anchor,
            "dof_before_dims": dof0 - rank - anchor,
            "dims_needed": max(0, dof0 - rank - anchor)}


def generate(segs: list, *, anchored: bool = True,
             dims: list | None = None) -> SketchPlan:
    """★★ **主入口**：给任意轮廓 ⇒ 出关系清单 + 尺寸需求 + 自由度账。

    ★★ 判据：**同一条代码路径**服务所有形状 —— ★ 输入只有**顶点坐标**。
    """
    if len(segs) < 3:
        raise SketchGenError("too-few-vertices",
                             "★ 闭合轮廓至少 3 段，实得 %d" % len(segs))
    rels = detect_relations(segs)
    rels += detect_symmetry(segs)
    acct = dof_account(segs, rels, anchored=anchored)
    need = acct["dims_needed"]
    given = list(dims or [])
    return SketchPlan(
        relations=_independent(rels),
        dimensions=given if given else ["★ 需要 %d 个尺寸" % need],
        dof_before=acct["dof_initial"],
        dof_after=need - len(given),
        notes=[
            "★ 段 %d · 初始自由度 %d" % (acct["segments"], acct["dof_initial"]),
            "★ 关系 %d 条 ⇒ 独立约束 **rank = %d**（★ 数值求秩）"
            % (acct["relations"], acct["rank"]),
            "★ 锚定原点 ⇒ 扣 %d" % acct["anchor_cost"],
            "★ 还需 **%d 个尺寸**" % need,
        ])


#: ══════════════════════════════════════════════════════════════════════
# 五、从**顶点序列**建轮廓（★ 便于把形状写成数据）
#: ══════════════════════════════════════════════════════════════════════

def polygon(points: list) -> list:
    """★ 由**顶点序列**（闭合）建 `Segment` 列表。

    ★ 判据：★ 输入是**纯坐标** ⇒ ★ 加一个形状就是**加一行数据**，
      ★ 不是加一段代码（★ 这正是业主批注 3 要的）。
    """
    out = []
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        out.append(Segment(x1, y1, x2, y2))
    return out


#: ══ 便于测试/复用的**形状数据**（★ 只加数据，不加代码）════════════════

SHAPES: dict[str, list] = {
    #: ★ 矩形 100×60（★ 从原点起）
    "rectangle": [(0, 0), (100, 0), (100, 60), (0, 60)],
    #: ★ L 形（★ 外框 100×100，右上角挖掉 60×60 的缺口）
    "L": [(0, 0), (100, 0), (100, 100), (40, 100), (40, 40), (0, 40)],
    #: ★ U 形（★ 100×80 的框，上方挖一个 60×50 的槽）
    "U": [(0, 0), (100, 0), (100, 80), (70, 80), (70, 50),
          (30, 50), (30, 80), (0, 80)],
    #: ★ H 形（★ 两条竖梁 + 中间横梁）
    "H": [(0, 0), (30, 0), (30, 40), (70, 40), (70, 0), (100, 0),
          (100, 100), (70, 100), (70, 60), (30, 60), (30, 100), (0, 100)],
    #: ★ T 形
    "T": [(0, 0), (100, 0), (100, 30), (65, 30), (65, 100),
          (35, 100), (35, 30), (0, 30)],
    #: ★★ X 形（★ 业主举的例子 —— **没有一条线水平或竖直**）
    #:   ★ 由两条交叉的斜带构成：长边与短边**垂直**，两侧线**共线**
    "X": [(0, 0), (20, 0), (60, 40), (100, 0), (120, 0), (70, 50),
          (120, 100), (100, 100), (60, 60), (20, 100), (0, 100), (50, 50)],
}
