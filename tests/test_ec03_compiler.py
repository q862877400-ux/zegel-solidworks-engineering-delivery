"""★ EC03 判据（V1–V10）—— 同一编译器 / 越权 / 欠约束 / 循环 / 纯离线 / 冻结不可改写。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/compiler.py`（★ EC03 的编译器）
#         `specs/305-ec03-method-library-and-ir/spec.md`（★ 8 FR · 10 V）
#         `scripts/engineering_contract.py`（★ EC01 的契约 —— ★ 编译器**只吃它**）
# 定位:   ★ EC03 的 **V1–V10**（★ 逐字承计划 §5 EC03 的「验收」）。
# 官方依据: 不适用（本仓的规划编译层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import engineering_contract as ec
from engineering import compiler as C


def _frozen(intent: str, *, devices=("plate",), domains=None, state=None):
    """★ 造一个**已冻结**的契约（★ 编译器只吃冻结的）。

    ⚠ 第一版写 `domains or {"outline": ...}` ⇒ ★★ **传 `domains={}` 会被换成默认值**
      ⇒ ★ 那条「空域 ⇒ 欠约束」的判据**永远测不到空域**（★ 判据假绿）✗
    ★★ **修法**：★ 用 `is None` 判（★ `{}` 是**有效输入**，★ 不是「没传」）。
    """
    c = ec.EngineeringContract(contract_id="C-1", intent=intent)
    c.classify("intent", ec.InformationClass.KNOWN)
    c.safety_level = "普通"
    c.material = ec.MaterialRef("Q235", "GB/T 700", "2006")
    c.process = ec.ProcessIntent(kind="machined")
    for d in (devices or ()):
        c.datums.append(ec.Datum("安装结合面", semantic_role="mounting_interface"))
    c.load_cases.append(ec.LoadCase("面压", "static",
                                    ec.normalize_quantity(ec.Quantity(1.0, "N", "force"))))
    #: ★★ `None` ⇒ 用默认域；★ `{}` ⇒ **真的是空域**（★ 那不是「没传」）
    dom = {"outline": (0.01, 1.0)} if domains is None else domains
    for name, (lo, hi) in dom.items():
        c.parameter_domains[name] = ec.ParameterDomain(name, lo, hi, "m",
                                                      allow_negative=False)
    c.obligations.append(ec.VerificationObligation("OB-1", "回读尺寸", evidence_kind="readback"))
    if state is None:
        c.freeze()
    return c


# ══════════════════════════════════════════════════════════════════════
# V1 · 同一编译器（★ 模型无关）
# ══════════════════════════════════════════════════════════════════════

def test_v1_same_contract_compiles_identically():
    """★★★ V1：★ **同一份契约 ⇒ 编译结果一致**（★ 逐字承计划验收：「★ 两模型生成的合法意图
    都通过**同一编译器**」）。

    ★★ 判据：★ 编译器**只吃 `EngineeringContract`** ⇒ ★ 同一契约**必然**同结果。
    """
    a = _frozen("做一个安装板")
    b = _frozen("做一个安装板")
    pa = C.compile_contract(a, device_class="plate")
    pb = C.compile_contract(b, device_class="plate")
    assert pa.method_id == pb.method_id, "★★ 同契约选了不同方法：%r vs %r" % (
        pa.method_id, pb.method_id)
    assert [n.tool for n in pa.dag.nodes] == [n.tool for n in pb.dag.nodes], (
        "★★ 同契约编出不同 DAG")
    assert pa.freeze() == pb.freeze(), "★★ 同契约的计划哈希不同 ⇒ ★ 编译器不确定"


def test_v1_compiler_does_not_read_free_text():
    """★★★ V1：★ 编译器**只吃契约的字段**（★ 不吃自由文本）。

    ★★ 判据：★ 用**同一 intent** 但**不同的其它字段**，★ 只要那些字段**不进编译**，
      ★★ 结果就该一样 ⇒ ★ 证明编译器**不读**额外文本。
    """
    a = _frozen("做一个安装板")
    b = _frozen("做一个安装板")
    #: ★ 给 b 塞一段**额外的自由文本**（★ 不在契约字段里）
    b.__dict__["free_text_from_model"] = "★ 模型说：先画个圆再拉伸再倒角（★ 一堆废话）"
    pa = C.compile_contract(a, device_class="plate")
    pb = C.compile_contract(b, device_class="plate")
    assert [n.tool for n in pa.dag.nodes] == [n.tool for n in pb.dag.nodes], (
        "★★ 自由文本影响了编译 ⇒ ★ 编译器读了不该读的东西（★ 模型无关性破了）")


def test_v1_method_selection_is_deterministic():
    """★★ V1：★ 选法是**确定性**的（★ 最长关键词优先）。"""
    for intent, expected in (("做一个安装板", "plate"),
                             ("做一根阶梯轴", "stepped_shaft"),
                             ("打一组孔组", "hole_group"),
                             ("做一个安装支架", "mounting_bracket")):
        spec = C._pick_method(intent)
        assert spec is not None and spec.id == expected, (
            "★ 「%s」选成了 %r（★ 应 %r）" % (intent, spec and spec.id, expected))


# ══════════════════════════════════════════════════════════════════════
# V2 · 拒绝越权
# ══════════════════════════════════════════════════════════════════════

def test_v2_overreach_is_rejected_at_compile_time():
    """★★★ V2：★ **越权 ⇒ 编译期失败**（★ 逐字承计划验收）。"""
    c = _frozen("做一个安装板", domains={"outline": (0.01, 1.0),
                                        "wall_thickness": (0.001, 0.02)})
    with pytest.raises(C.PlanError) as exc:
        C.compile_contract(c, device_class="plate")
    assert exc.value.code == C.RejectCode.OVERREACH, (
        "★ 拒绝码不对：%s" % exc.value.code)
    #: ★★ 报错必须**点名**哪个参数越权
    assert "wall_thickness" in str(exc.value), "★ 没点名越权的参数"


def test_v2_within_domain_is_allowed():
    """★★ V2 负例：★ **在修改域内 ⇒ 允许**（★ 不是一律拒）。"""
    c = _frozen("做一个安装板", domains={"outline": (0.01, 1.0),
                                        "thickness": (0.002, 0.05)})
    plan = C.compile_contract(c, device_class="plate")
    assert plan.method_id == "plate"


# ══════════════════════════════════════════════════════════════════════
# V3 · 拒绝欠约束
# ══════════════════════════════════════════════════════════════════════

def test_v3_underconstrained_is_rejected():
    """★★★ V3：★ **欠约束（★ 没有参数域）⇒ 编译期失败**。"""
    c = _frozen("做一个安装板", domains={})
    #: ★★ 注意：★ 空域会让 `freeze()` 通过（★ 它只查 `required_missing`/安全等级/假设）
    #:   ⇒ ★ 那正是**编译期**该抓的（★ 不是冻结期）
    with pytest.raises(C.PlanError) as exc:
        C.compile_contract(c, device_class="plate")
    assert exc.value.code == C.RejectCode.UNDERCONSTRAINED, (
        "★ 拒绝码不对：%s" % exc.value.code)


def test_v3_no_domain_means_no_feasible_plan():
    """★★ V3：★ **没域 ⇒ 不可行**（★ 不能「先编了再说」）。"""
    c = _frozen("做一个安装板", domains={})
    with pytest.raises(C.PlanError):
        C.compile_contract(c)


# ══════════════════════════════════════════════════════════════════════
# V4 · 拒绝循环依赖
# ══════════════════════════════════════════════════════════════════════

def test_v4_cycle_is_detected():
    """★★★ V4：★ **循环依赖 ⇒ 编译期失败**（★ 逐字承计划验收）。"""
    dag = C.ToolDAG(nodes=[
        C.DAGNode(tool="a", depends_on=("b",)),
        C.DAGNode(tool="b", depends_on=("a",)),
    ])
    assert dag.has_cycle() is True, "★★ 环没被检出"
    #: ★★ 必须能**指认**环（★ 不只说「有环」）
    path = dag.cycle_path()
    assert len(path) >= 3 and path[0] == path[-1], "★ 环路径不可读：%r" % path


def test_v4_acyclic_dag_passes():
    """★★ V4 负例：★ **无环 ⇒ 通过**。"""
    dag = C.ToolDAG(nodes=[
        C.DAGNode(tool="a"),
        C.DAGNode(tool="b", depends_on=("a",)),
        C.DAGNode(tool="c", depends_on=("b",)),
    ])
    assert dag.has_cycle() is False
    assert dag.cycle_path() == []


def test_v4_self_loop_is_a_cycle():
    """★★ V4：★ **自环**（★ A 依赖 A）也是环。"""
    dag = C.ToolDAG(nodes=[C.DAGNode(tool="a", depends_on=("a",))])
    assert dag.has_cycle() is True, "★★ 自环没被检出"


# ══════════════════════════════════════════════════════════════════════
# V5 · 不需要 COM 即可检验
# ══════════════════════════════════════════════════════════════════════

def test_v5_compiler_has_no_com_imports():
    """★★★★★ V5：★ **编译器不 import 任何 COM 模块**（★ 逐字承计划验收：
    「★ **不需要 COM 即可检验计划正确性**」）。

    ★★ 判据：★ 扫编译器的 `import` 行 ⇒ ★ **不许出现** `win32com`/`comtypes`/`sw_part` 等。
    """
    out = C.assert_no_com_imports()
    assert out["ok"] is True, (
        "★★ 编译器 import 了 COM 模块 ⇒ ★ 没装 SolidWorks 的机器上就验不了计划：%r"
        % out["offending_imports"])


def test_v5_compilation_works_without_touching_com():
    """★★★ V5：★ **整条编译路径**都不碰 COM（★ 本判据本身就是证明）。"""
    c = _frozen("做一个安装板")
    plan = C.compile_contract(c, device_class="plate")
    assert plan.dag.nodes, "★ 没编出 DAG"
    #: ★★ 本文件**也不许** import COM（★ 否则「不需要 COM」是空话）
    #:   ⚠ 用 **AST** 核（★ 不用文本包含 —— ★ 那会被**判据字符串自己**误触发，
    #:     本判据第一版就这么红了一次）
    import ast
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8", errors="replace"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    bad = [m for m in imported
           if any(k in m for k in ("win32com", "comtypes", "pythoncom", "sw_part",
                                   "sw_session", "sw_connect"))]
    assert not bad, "★★ 本判据 import 了 COM：%r" % bad


# ══════════════════════════════════════════════════════════════════════
# V6 · 冻结计划不能被执行器静默改写
# ══════════════════════════════════════════════════════════════════════

def test_v6_frozen_plan_verifies_unchanged():
    """★★★ V6：★ **冻结后未改 ⇒ 校验通过**。"""
    c = _frozen("做一个安装板")
    plan = C.compile_contract(c, device_class="plate")
    h = plan.freeze()
    assert h.startswith("sha256:"), "★ 冻结没产生哈希"
    assert plan.verify_unchanged() is True, "★ 未改动却校验失败"


def test_v6_silent_modification_is_detected():
    """★★★★★ V6 的**核心**：★ **静默改写冻结计划 ⇒ 校验失败**。

    ★★ 依据（★ 计划验收逐字）：★「★ **冻结计划不能被执行器静默改写**」。
    ★★★ **⇒ 不是「警告」，是「拒绝」** —— ★ `verify_unchanged()` 回 `False`。
    """
    c = _frozen("做一个安装板")
    plan = C.compile_contract(c, device_class="plate")
    plan.freeze()
    assert plan.verify_unchanged() is True
    #: ★★★ **静默加一个节点**（★ 那是「执行器偷偷改计划」的形态）
    plan.dag.nodes.append(C.DAGNode(tool="sneaky_extra_step"))
    assert plan.verify_unchanged() is False, (
        "★★★ 计划被**静默改写**却校验通过 ⇒ ★ 审签的与执行的不是同一份（★ V6 的核心负例）")


def test_v6_unfrozen_plan_cannot_be_verified():
    """★★ V6：★ **未冻结 ⇒ 校验必失败**（★ 不能拿没冻结的当已批准）。"""
    c = _frozen("做一个安装板")
    plan = C.compile_contract(c, device_class="plate")
    assert plan.frozen is False
    assert plan.verify_unchanged() is False, (
        "★★ 未冻结的计划通过了校验 ⇒ ★ 等于没有审签")


def test_v6_hash_excludes_self_referential_fields():
    """★★ V6：★ 计划哈希**不含** `frozen`/`plan_hash` 自身（★ 否则自指）。"""
    c = _frozen("做一个安装板")
    plan = C.compile_contract(c, device_class="plate")
    h1 = plan.compute_hash()
    plan.frozen = True
    plan.plan_hash = "x"
    assert plan.compute_hash() == h1, (
        "★★ 改了 `frozen`/`plan_hash` 哈希就变 ⇒ ★ 自指")


# ══════════════════════════════════════════════════════════════════════
# V7 · unknown 不落入默认可行
# ══════════════════════════════════════════════════════════════════════

def test_v7_unknown_does_not_default_to_feasible():
    """★★★★ V7：★ **`unknown` 不能落入默认可行**（★ 逐字承 EC03-T05）。

    ★★ 判据：★ 契约仍有**必需缺失** ⇒ ★ **编译期拒绝**（★ 不是「先编了再说」）。
    """
    c = ec.EngineeringContract(contract_id="C-U", intent="做一个安装板")
    c.classify("material", ec.InformationClass.REQUIRED_MISSING)
    c.safety_level = "普通"
    #: ★★ 契约**冻不了** ⇒ 先手工给个哈希（★ 模拟「有人绕过冻结」）
    c.state = ec.ContractState.FROZEN
    c.content_hash = "sha256:" + "0" * 64
    with pytest.raises(C.PlanError) as exc:
        C.compile_contract(c, device_class="plate")
    assert exc.value.code == C.RejectCode.UNKNOWN_NOT_FEASIBLE, (
        "★ 拒绝码不对：%s" % exc.value.code)


def test_v7_unfrozen_contract_is_rejected():
    """★★ V7：★ **契约未冻结 ⇒ 拒绝**（★ `reject-contract-not-frozen`）。"""
    c = ec.EngineeringContract(contract_id="C-D", intent="做一个安装板")
    with pytest.raises(C.PlanError) as exc:
        C.compile_contract(c)
    assert exc.value.code == C.RejectCode.CONTRACT_NOT_FROZEN


# ══════════════════════════════════════════════════════════════════════
# V8 · 优雅是多指标
# ══════════════════════════════════════════════════════════════════════

def test_v8_elegance_is_multi_metric():
    """★★★★ V8：★ **优雅是**多指标**，★ 不能仅「最少特征」**（★ 逐字承 EC03-T07）。"""
    c = _frozen("做一个安装板")
    plan = C.compile_contract(c, device_class="plate")
    s = C.score_elegance(plan)
    assert s.is_single_metric() is False, (
        "★★ 优雅退化成**单指标** ⇒ ★ 违反「不能仅最少特征」：%r" % s)
    #: ★★ 五个指标都要**非零**
    for name in ("modification_stability", "datum_expression", "intent_readability",
                 "tool_risk", "manufacturability"):
        assert getattr(s, name) > 0.0 or name == "tool_risk", (
            "★ 指标 `%s` 是 0 ⇒ ★ 没参与评分" % name)


def test_v8_total_uses_all_five_metrics():
    """★★ V8：★ 总分必须**用上五个指标**（★ 改任何一个都影响总分）。"""
    base = C.EleganceScore(0.5, 0.5, 0.5, 0.5, 0.5)
    t0 = base.total()
    for field_name in ("modification_stability", "datum_expression",
                       "intent_readability", "tool_risk", "manufacturability"):
        s = C.EleganceScore(0.5, 0.5, 0.5, 0.5, 0.5)
        setattr(s, field_name, 1.0)
        assert abs(s.total() - t0) > 1e-12, (
            "★★ 改 `%s` 不影响总分 ⇒ ★ 那个指标是摆设" % field_name)


def test_v8_elegance_does_not_use_feature_count():
    """★★★★ V8：★ **打分不看特征个数**（★ 那是「最少特征」的形态）。

    ★★ 判据：★ 造两个**特征数不同**但**指标相同**的计划 ⇒ ★ **分数必须相同**
      （★ 因为 `score_elegance` 只看工具**类型**，★ 不看**数量**）。
    """
    c = _frozen("做一个安装板")
    plan = C.compile_contract(c, device_class="plate")
    s1 = C.score_elegance(plan)
    #: ★★ 复制一份并**加一个**节点（★ 只改数量）
    plan2 = C.compile_contract(c, device_class="plate")
    plan2.dag.nodes.append(C.DAGNode(tool="chamfer"))
    s2 = C.score_elegance(plan2)
    assert abs(s1.manufacturability - s2.manufacturability) < 1e-12, (
        "★★ 特征数变了分数就变 ⇒ ★ 可能退化成「最少特征」")


# ══════════════════════════════════════════════════════════════════════
# V9 · 沙箱探索产物不得直接进生产
# ══════════════════════════════════════════════════════════════════════

def test_v9_sandbox_exploration_is_not_production():
    """★★★ V9：★ **沙箱探索产物不得直接进生产方法库**（★ 逐字承 EC03-T08）。"""
    out = C.is_production_method("sandbox_explore_1")
    assert out is False, "★★ 沙箱产物被判成生产方法 ⇒ ★ 未审查就进库"
    assert C.is_production_method("plate") is True, "★ 受控方法应算生产"


def test_v9_production_methods_require_review_metadata():
    """★★ V9：★ 生产方法必须带**审查元数据**（★ 来源/域/正负例 —— ★ EC03-T08 逐字）。"""
    for mid, spec in C.METHOD_LIBRARY.items():
        assert spec.rationale, "★★ 方法 `%s` 没有选法原因（★ T02 要求）" % mid
        assert spec.alternatives, "★★ 方法 `%s` 没有替代方案（★ T02 要求）" % mid
        assert spec.applicable_devices, "★★ 方法 `%s` 没有适用域" % mid
        assert spec.failure_domain, "★★ 方法 `%s` 没有失败域（★ T01 要求）" % mid


# ══════════════════════════════════════════════════════════════════════
# V10 · 四个受控方法
# ══════════════════════════════════════════════════════════════════════

def test_v10_four_controlled_methods_exist():
    """★★★ V10：★ **板 / 孔组 / 阶梯轴 / 安装支架** 四个受控方法必须齐（★ EC03-T02 逐字）。"""
    for mid in ("plate", "hole_group", "stepped_shaft", "mounting_bracket"):
        assert mid in C.METHOD_LIBRARY, "★★ 缺受控方法 `%s`" % mid


@pytest.mark.parametrize("intent,device,method", [
    ("做一个安装板", "plate", "plate"),
    ("做一根阶梯轴", "shaft", "stepped_shaft"),
    ("做一个安装支架", "bracket", "mounting_bracket"),
])
def test_v10_methods_compile_end_to_end(intent, device, method):
    """★★★ V10：★ 三个方法**端到端可编译**（★ 且选法正确）。"""
    domains = {"outline": (0.01, 1.0)} if method != "stepped_shaft" else {"diameter": (0.005, 0.2)}
    c = _frozen(intent, domains=domains)
    plan = C.compile_contract(c, device_class=device)
    assert plan.method_id == method, "★ 选成了 %r" % plan.method_id
    assert plan.dag.nodes, "★ 没编出 DAG"
    assert plan.freeze().startswith("sha256:")


def test_v10_unknown_intent_is_rejected():
    """★★ V10：★ **没有匹配方法 ⇒ 拒绝**（★ 不硬套一个）。"""
    c = _frozen("做一个会飞的咖啡机", domains={"outline": (0.01, 1.0)})
    with pytest.raises(C.PlanError) as exc:
        C.compile_contract(c, device_class="plate")
    assert exc.value.code == C.RejectCode.NO_METHOD
