"""★ 阶段 4 · 需求协议 + 方法检索 + 问答契约 + 出站许可（规格 319 的 G1~G4）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/design_ir.py
# 定位:   规格 `specs/319-stage4-constrained-planning` 的 G1（需求与布局协议）/G2（方
#           法检索）/ G3（问题回答契约）/ G4（受控客户端与出站许可）。★★ 实测（2026-10-1
#           2）起点：`evaluation.py` 已有 `EvalCase`/`EvalSet`/`AdmissionGate`，`enginee
#           ring_contract.py` 已有 `EngineeringContract`，`corpus/l3-semantic.yaml` **就
#           是** S4-A 要的 60 条（分布完全对得上）；★ 而**没有规划器、没有方法检索、没有
#            DesignIR、没有候选预算/出站许可**。
# 官方依据: ① 外部方案阶段 4 的验收 S4-A / S4-B（逐字）② `corpus/l3-semantic.yaml`（★ 60
#            条 · 24/12/12/12 · 20/40）③ `scripts/engineering/compiler.py` 的 `METHOD_LI
#           BRARY` 与 `RejectCode`④ 本仓 `scripts/check_corpus.py` 的既有语料判据
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收入口 `tools/run_stage4_corpus.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
from dataclasses import dataclass, field

#: ══════════════════════════════════════════════════════════════════════
# 一、封闭码（★ 新增码必须同时加进 `IR_CODES`）
#: ══════════════════════════════════════════════════════════════════════

READY_FOR_REVIEW = "READY_FOR_REVIEW"
WAITING_INPUT = "WAITING_INPUT"
REJECTED_OUT_OF_SCOPE = "REJECTED_OUT_OF_SCOPE"
REJECTED_UNSUPPORTED = "REJECTED_UNSUPPORTED"
REJECTED_AMBIGUOUS = "REJECTED_AMBIGUOUS"

IR_CODES = (READY_FOR_REVIEW, WAITING_INPUT, REJECTED_OUT_OF_SCOPE,
            REJECTED_UNSUPPORTED, REJECTED_AMBIGUOUS)

#: ★★ **只有这一个能进执行**（★ S4-A：「应等待或拒绝却进入执行的次数为 0」）
EXECUTABLE = (READY_FOR_REVIEW,)

#: ══ 出站许可的封闭码
DATA_NOT_PERMITTED = "DATA_NOT_PERMITTED"
BUDGET_NOT_PERMITTED = "BUDGET_NOT_PERMITTED"
COST_UNKNOWN = "COST_UNKNOWN"
PERMIT_CODES = (DATA_NOT_PERMITTED, BUDGET_NOT_PERMITTED, COST_UNKNOWN)

#: ★★ **候选预算**（★ S4-B 逐字：每次候选不超 4096 token）
CANDIDATE_TOKEN_BUDGET = 4096
#: ★★ **最多两批**主动问题（★ S4-B 逐字）
MAX_ELICIT_BATCHES = 2


class DesignIRError(Exception):
    """★ 需求解析失败（★ 带封闭码）。"""

    CODES = ("empty-requirement", "bad-code", "batch-exceeded", "budget-exceeded")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法 DesignIR 拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 二、DesignIR（★ G1 —— ★ 需求与布局协议）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class DesignIR:
    """★ **需求 → 设计意图**的中间表示（★ 人工不写工具序列的**起点**）。"""

    requirement: str = ""
    function: str = ""            #: ★ 功能（如「承载」）
    interface: str = ""           #: ★ 接口（如「四角孔位」）
    constraints: dict = field(default_factory=dict)
    open_questions: list = field(default_factory=list)
    state: str = WAITING_INPUT
    notes: str = ""

    def __post_init__(self) -> None:
        assert self.state in IR_CODES, "★ 非法状态：%r" % self.state

    @property
    def executable(self) -> bool:
        """★★ **能不能进执行**（★ 只有 `READY_FOR_REVIEW` 能）。"""
        return self.state in EXECUTABLE

    @property
    def blocks_cad(self) -> bool:
        """★★ **要不要挡住 CAD 写入**（★ FR-002）。

        ★ 判据：**只要不是 `READY_FOR_REVIEW`** ⇒ 挡（★ `WAITING_INPUT` 与三种拒绝都挡）。
        """
        return not self.executable


#: ★ 关键输入（★ 缺了 ⇒ `WAITING_INPUT`）。
#: ★★ **判据是「能不能算出来」，不是「有没有那个词」** ——
#:   ⚠ 实测（2026-10-12）第一版要求**字面命中**关键词，而
#:     「在一块 100×60×20 的板上四角各打一个 M6 通孔，孔心距边 10mm」
#:     里**没有「尺寸」「材料」这两个词** ⇒ 被判 `WAITING_INPUT`
#:     ⇒ ★★ **而那条是 L3 语料里标为 `solvable` 的第一条** ✗
#:   ⇒ ★ 改判据：**能从文本算出来**就算有（★ 与 `planner.extract_geometry` 同口径）。
#:   ★ 这是「**判据不匹配组织单元**」的又一实例（本仓事实 51 同族）——
#:     判据要落在**真正决定可做性的那件事**上（★ 数字齐不齐），不是**词在不在**。
CRITICAL_HINTS = (
    #: ★ 尺寸：**有数字**就算有（★ 具体三围由 `extract_geometry` 抽）
    ("尺寸", ("尺寸", "多大", "长", "宽", "高", "厚", "直径", "φ", "Φ")),
    #: ★ 材料：本仓方法**不依赖材料**（★ 材料是**后置**的工程义务，不是建模前置）
    #:   ⇒ ★ **不作为关键输入**
    ("孔位", ("孔位", "孔心", "间距", "距边", "中心距", "四角")),
    #: ★ 载荷：同上 —— ★ 建模**不需要**载荷（★ 载荷是阶段 5 的计算义务）
)

#: ★ 能力边界（★ 本仓已验证的方法覆盖的域）。
#: ★★ 2026-10-12 扩表（★ 实测：第一版只有建模词 ⇒ L3-014/019/022/023/024 被误挡）：
#:   ★ 语料里 `solvable` 的**不止建模** —— 还有**属性 / 工程图 / 干涉 / 缩放 /
#:     方程 / 阶梯轴 / 键槽**。★ 那些本仓**都有工具**（★ 已注册、已准入）
#:   ⇒ ★ 域表必须覆盖**工具面真的支持的**那些，否则就是**误挡可解需求**（MISBLOCK）。
SUPPORTED_DOMAINS = (
    #: ══ 建模 ══
    "板", "轴", "孔", "支架", "法兰", "套", "块", "夹具",
    "定位", "导向", "箱体", "连杆", "钳",
    #: ══ 几何操作 ══
    "阶梯轴", "键槽", "倒角", "圆角", "抽壳", "圆顶", "筋",
    #: ══ 文档 / 元数据 ══
    "自定义属性", "属性", "编号", "工程图", "视图", "标注",
    #: ══ 检查 / 计算 ══
    "干涉", "质量", "体积", "质量属性", "测量",
    #: ══ 参数化 ══
    "方程", "全局变量", "参数", "配置", "缩放",
)
#: ★ 明确不支持（★ 能力边界 ⇒ `REJECTED_UNSUPPORTED`）
UNSUPPORTED_HINTS = ("曲面", "自由曲面", "钣金展开", "焊接变形", "注塑模流",
                     "多物理场", "疲劳寿命", "齿轮箱整体", "整机", "减速器")
#: ★★ **量级荒谬**（★ 对抗语义 ⇒ `REJECTED_AMBIGUOUS`）。
#:   ★ 依据：本仓是**机械零件**工具，而「直径 1000 米」不是机械零件；
#:   ★ 且「1000 米 + 0.001mm 精度」相对误差 1e-9 ⇒ ★ **物理上不可实现**。
#:   ★ 判据：**长度超过 100 米** 或 **精度比 1e-6 相对更严**。
ABSURD_LENGTH_M = 100.0
ABSURD_PRECISION_MM = 0.001


def parse_requirement(text: str) -> DesignIR:
    """★★ **一句需求 → `DesignIR`**（★ G1）。

    ★★ 判据顺序（★ **最严的在前** —— ★ 与阶段 2 七档、阶段 3 恢复判定同族）：
      ```
      ① 空需求            ⇒ REJECTED_AMBIGUOUS
      ② 超能力边界        ⇒ REJECTED_OUT_OF_SCOPE / REJECTED_UNSUPPORTED
      ③ 域内但缺关键输入  ⇒ WAITING_INPUT（★ 且列出具名问题）
      ④ 域内且输入齐      ⇒ READY_FOR_REVIEW
      ```
    ★★ **为什么 ① 在最前**：空需求连「问什么」都定不出来 ⇒ 归「模糊」而不是「缺输入」。
    """
    t = (text or "").strip()
    if not t:
        return DesignIR(requirement="", state=REJECTED_AMBIGUOUS,
                        notes="★ 需求为空 ⇒ 无法定出要问什么")
    ir = DesignIR(requirement=t)

    #: ② 能力边界
    for bad in UNSUPPORTED_HINTS:
        if bad in t:
            ir.state = REJECTED_UNSUPPORTED if bad in ("曲面", "自由曲面", "多物理场",
                                                       "疲劳寿命") \
                else REJECTED_OUT_OF_SCOPE
            ir.notes = "★ 超出已验证能力：%r" % bad
            return ir
    #: ★★ **量级荒谬 / 精度荒谬**（★ 对抗语义 —— ★ L3-055 正是这一类）
    #:   ★ 判据：长度 > 100 米，或「大长度 + 极小精度」同时出现。
    big = re.search(r"(\d+(?:\.\d+)?)\s*(米|m)\b", t)
    tiny = re.search(r"精度\s*[:：]?\s*(\d+(?:\.\d+)?)\s*mm", t)
    if big and float(big.group(1)) >= ABSURD_LENGTH_M:
        if tiny and float(tiny.group(1)) <= ABSURD_PRECISION_MM:
            ir.state = REJECTED_AMBIGUOUS
            ir.notes = ("★ 量级荒谬：%s 米 + 精度 %s mm ⇒ 相对误差 1e-9，"
                        "★ 不是机械零件" % (big.group(1), tiny.group(1)))
            return ir
        ir.state = REJECTED_OUT_OF_SCOPE
        ir.notes = "★ 尺寸 %s 米超出机械零件量级" % big.group(1)
        return ir
    #: ★ 「整机 / 减速器」这一类 ⇒ 域外（★ Q1 突变正是这一类）
    if re.search(r"整机|整台|全套|减速器|变速箱", t):
        ir.state = REJECTED_OUT_OF_SCOPE
        ir.notes = "★ 需求是**整机级**，而本仓只有单零件方法 ⇒ 域外"
        return ir

    #: ★ 域判定
    domain = next((d for d in SUPPORTED_DOMAINS if d in t), "")
    if not domain:
        ir.state = REJECTED_UNSUPPORTED
        ir.notes = "★ 需求里找不到已验证的域（板/轴/孔/支架/夹具/箱体/连杆）"
        return ir
    ir.constraints["domain"] = domain

    #: ③ 关键输入（★ 判据：**能不能算出来**，不是「词在不在」）
    #: ★★ **2026-10-12 补一条大前提**：**非建模意图不要求几何** ——
    #:   ⚠ 实测：L3-014（加自定义属性）/019（出工程图）/022（干涉检查）/
    #:     023（放大读体积）/024（加方程）**都被判 `WAITING_INPUT`** ✗ ——
    #:     ★ 而那些需求**本来就不需要几何**（★ 属性是键值、出图靠已有模型、
    #:     干涉靠已有装配、方程是公式）。
    #:   ⇒ ★ 判据：**意图决定要不要几何**（★ 与 `planner.detect_intent` 同口径）。
    from .planner import detect_intent as _di
    _intent = _di(t)
    _needs_geo = _intent in ("plate", "hole_group", "keyway", "stepped_shaft",
                             "revolve", "shell", "pin")

    missing = []
    for name, words in CRITICAL_HINTS:
        if any(w in t for w in words):
            continue
        if name == "尺寸":
            #: ★ 非建模意图**不要求尺寸**
            if not _needs_geo:
                continue
            if _has_extractable_size(t):
                continue
        if name == "孔位":
            #: ★★ **只有需求里真的有孔时才要求孔位** ——
            #:   ⚠ 实测（2026-10-12）：第一版无条件要求孔位 ⇒
            #:     「φ20×100 的圆柱轴」被判缺孔位 ⇒ ★ **那条也是 `solvable`** ✗
            if not re.search(r"孔|螺|螺纹", t):
                continue
            if re.search(r"四角|均布|中心|阵列", t):
                continue
        missing.append(name)
    if missing:
        ir.state = WAITING_INPUT
        ir.open_questions = ["请给出%s" % m for m in missing]
        ir.notes = "★ 缺关键输入：%s" % missing
        return ir

    ir.state = READY_FOR_REVIEW
    ir.function = _guess_function(t)
    ir.interface = _guess_interface(t)
    ir.notes = "★ 输入齐、域内 ⇒ 可进规划"
    return ir


def _has_extractable_size(t: str) -> bool:
    """★★ **能不能真抽出可建模的尺寸**（★ 与 `planner.extract_geometry` 同口径）。

    ★ 判据（★ 三条之一即可）：
      · `100×60` 这种三围写法
      · `φ20` / `M6` 这种直径写法
      · 单独的「长 100」这种
    ★★ 为什么不能只看「有没有数字」：`打个 4 个孔` 有数字，但**没有尺寸**。
    """
    if re.search(r"\d+(?:\.\d+)?\s*[×xX*]\s*\d+(?:\.\d+)?", t):
        return True
    if re.search(r"(?:φ|Φ|直径)\s*\d+(?:\.\d+)?", t):
        return True
    if re.search(r"\bM\d+(?:\.\d+)?\b", t):
        return True
    return bool(re.search(r"(?:长|宽|高|厚|半径|直径)\s*[:：]?\s*\d+", t))


def _guess_function(t: str) -> str:
    for k, v in (("承载", "承载"), ("定位", "定位"), ("夹紧", "夹紧"),
                 ("传动", "传动"), ("导向", "导向"), ("支撑", "支撑")):
        if k in t:
            return v
    return "未指定"


def _guess_interface(t: str) -> str:
    for k, v in (("孔", "孔系"), ("轴", "轴颈"), ("面", "配合面"),
                 ("槽", "槽口"), ("螺纹", "螺纹副")):
        if k in t:
            return v
    return "未指定"


#: ══════════════════════════════════════════════════════════════════════
# 三、方法检索（★ G2 —— ★ 候选预算 4096 token）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class MethodCandidate:
    method_id: str
    score: float = 0.0
    tokens: int = 0
    applicable: bool = True


def _est_tokens(method) -> int:
    """★ 估一个方法的**候选描述**要多少 token（★ 粗估：字数 / 1.6）。"""
    blob = "%s %s %s" % (method.id, method.goal,
                         " ".join(getattr(method, "steps", ()) or ()))
    return max(1, int(len(blob) / 1.6))


def retrieve_methods(ir: DesignIR, *,
                     budget: int = CANDIDATE_TOKEN_BUDGET) -> dict:
    """★★ **按 `DesignIR` 找候选方法**（★ G2 —— ★ 每次候选 ≤4096 token）。

    ★★ 判据（★ FR-004）：
      · 逐个累加候选的 token，**超预算就停**（★ 不是「超了就报错」——
        ★ 而是**截断**，并**如实报出**截断了多少）
      · `WAITING_INPUT` / 拒绝态 ⇒ **不检索**（★ 没有可规划的输入）
    """
    from .compiler import METHOD_LIBRARY

    if not ir.executable:
        return {"candidates": [], "tokens": 0, "truncated": 0,
                "reason": "★ 状态是 %s ⇒ 不检索（★ 没有可规划的输入）" % ir.state,
                "budget": budget}

    dom = str(ir.constraints.get("domain") or "")
    scored = []
    for mid, m in METHOD_LIBRARY.items():
        s = 0.0
        blob = "%s %s" % (m.goal, " ".join(getattr(m, "steps", ()) or ()))
        if dom and dom in blob:
            s += 2.0
        if ir.function and ir.function in blob:
            s += 1.0
        if ir.interface and ir.interface in blob:
            s += 0.5
        if any(d in blob for d in getattr(m, "applicable_devices", ()) or ()):
            s += 0.5
        scored.append((s, mid, m))
    scored.sort(key=lambda x: (-x[0], x[1]))

    out: list[MethodCandidate] = []
    used = 0
    truncated = 0
    for s, mid, m in scored:
        tk = _est_tokens(m)
        if used + tk > budget:
            truncated += 1
            continue
        used += tk
        out.append(MethodCandidate(method_id=mid, score=s, tokens=tk,
                                   applicable=s > 0))
    return {"candidates": out, "tokens": used, "truncated": truncated,
            "budget": budget, "reason": ""}


#: ══════════════════════════════════════════════════════════════════════
# 四、问答契约（★ G3 —— ★ 最多两批 · 缺项不写 CAD）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class ElicitBatch:
    batch_index: int = 0
    questions: list = field(default_factory=list)
    answers: dict = field(default_factory=dict)


@dataclass
class Elicitation:
    batches: list = field(default_factory=list)

    def ask(self, questions: list) -> ElicitBatch:
        """★★ **发起一批主动问题**（★ FR-003：**最多两批**）。"""
        if len(self.batches) >= MAX_ELICIT_BATCHES:
            raise DesignIRError(
                "batch-exceeded",
                "★ 已经问了 %d 批（★ 上限 %d）⇒ 不许再问"
                % (len(self.batches), MAX_ELICIT_BATCHES))
        b = ElicitBatch(batch_index=len(self.batches) + 1,
                        questions=list(questions))
        self.batches.append(b)
        return b

    def answer(self, batch_index: int, answers: dict) -> None:
        for b in self.batches:
            if b.batch_index == batch_index:
                b.answers.update(answers or {})
                return

    @property
    def unanswered(self) -> list:
        out = []
        for b in self.batches:
            out.extend(q for q in b.questions if q not in b.answers)
        return out

    @property
    def may_write_cad(self) -> bool:
        """★★ **能不能写 CAD**（★ FR-002）。

        ★ 判据：**所有批次的每个问题都答了** ⇒ 才能写。
        """
        return not self.unanswered


#: ══════════════════════════════════════════════════════════════════════
# 五、出站许可（★ G4 —— ★ 受控客户端）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class OutboundPermit:
    allowed: bool = False
    code: str = ""
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.allowed:
            assert self.code in PERMIT_CODES, "★ 非法许可码：%r" % self.code


@dataclass
class BudgetHold:
    """★ **预算预占**（★ FR-006：未知费用**不释放**预占）。"""

    amount: float = 0.0
    held: bool = False
    released: bool = False

    def hold(self, amount: float) -> None:
        self.amount = float(amount)
        self.held = True
        self.released = False

    def release(self, *, cost_known: bool) -> bool:
        """★★ **只有费用已知**才释放预占（★ FR-006）。

        ★ 未知费用 ⇒ **不释放**（★ 否则下一轮会**超额**）。
        """
        if not cost_known:
            return False
        self.released = True
        self.held = False
        return True


def outbound_permit(*, data_permitted: bool, budget_permitted: bool,
                    cost_known: bool = True) -> OutboundPermit:
    """★★ **能不能发云请求**（★ G4 —— ★ FR-005/006）。

    ★★ 判据顺序（★ 最严的在前）：
      ```
      ① 数据未获准      ⇒ DATA_NOT_PERMITTED
      ② 余额未获准      ⇒ BUDGET_NOT_PERMITTED
      ③ 费用未知        ⇒ COST_UNKNOWN
      ④ 都过            ⇒ allowed
      ```
    ★★ **为什么数据排第一**：数据外发是**不可撤**的（★ 余额不足只是没跑成）。
    """
    if not data_permitted:
        return OutboundPermit(False, DATA_NOT_PERMITTED,
                              "★ 数据未获准外发 ⇒ **出站请求数 = 0**")
    if not budget_permitted:
        return OutboundPermit(False, BUDGET_NOT_PERMITTED,
                              "★ 余额未获准 ⇒ **出站请求数 = 0**")
    if not cost_known:
        return OutboundPermit(False, COST_UNKNOWN,
                              "★ 费用未知 ⇒ 不放行、**也不释放预算预占**")
    return OutboundPermit(True, detail="★ 数据与余额都获准、费用已知 ⇒ 放行")
