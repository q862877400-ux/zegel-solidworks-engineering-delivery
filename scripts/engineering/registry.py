"""★ 阶段 1 · 统一目录 + 名字解析 + 参数绑定（规格 316 的 C1/C3/C4）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/registry.py
# 定位:   规格 `specs/316-stage1-parameter-plate` 的 C1（统一目录）/ C3（名字解析）
#           / C4（参数绑定）。★ 这是阶段 1 的**核心缺口**：
#           实测（2026-10-11）`compiler.py` 的 `DAGNode.tool` 存的是**裸步名**
#           （`tool=step`），而全仓**没有**「裸步名 → `solidworks_*`」的解析器。
# 官方依据: 不适用（本仓自研编排层，不包装单一官方成员）。
#           注册真源：`register_capabilities.all_specs()`（476 个）
#                    + `mcp-server/server.py` 的 `@mcp.tool`（45 个）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收见 `tools/run_stage1_plate.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import pathlib
import re
import sys
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[2]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"), str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★ 规范工具名的前缀（唯一一条映射规则的依据）
PREFIX = "solidworks_"


class RegistryError(Exception):
    """★ 目录/解析失败（★ 带**封闭码** —— 与 `RejectCode` 同族）。"""

    CODES = (
        "unresolved-step-name",      #: ★ 解析不到
        "ambiguous-step-name",       #: ★ 映射到多个规范名
        "tool-not-admitted",         #: ★ 解析到但未准入
        "duplicate-canonical-name",  #: ★ 规范名重复
        "unknown-param",             #: ★ 参数不在声明形参里
        "missing-required-param",    #: ★ 缺必填参数
        "empty-registry",            #: ★ 目录为空（★ 防「静默通过」）
        "sub-method-not-expanded",   #: ★★ 步骤是**另一个方法 id** ⇒ 属阶段 2「子方法展开」
    )

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法目录拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 一、ToolDescriptor（★ C1 统一目录 —— ★ 规格 §3 FR-004）
#: ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ToolDescriptor:
    """★ 每个工具合成一个描述符（★ 供检索、编译、授权**共同使用**）。"""

    canonical_name: str
    step_name: str
    module: str
    function: str
    inject: str = ""
    params: tuple = ()
    required: tuple = ()          #: ★ 必填形参（无默认值的）
    effect: str = "unknown"       #: ★ `read` / `write` / `unknown`
    admitted: bool = False
    reject_reason: str = ""
    source: str = "all_specs"     #: ★ `all_specs` / `server_py`


#: ★ 只读效应词（来自工具声明的 `read_only=True`）
def _effect_of(spec) -> str:
    """★ 效应 = **保守合成**（`read_only` 声明 + 效应表 + **AST 解析**）。

    ★★ 为什么三个来源都要（★ 实测 2026-10-11）：
      · `read_only`：476 个里只有 **35 个** `True` / **1 个** `False` / **440 个** `None`
      · `docs/effect-declarations.json`：**278 个 `writes=null`**（58%）
      · ⇒ ★ 只靠前两个，**方法库要用的 11 个工具里 8 个会判「未知」⇒ 进不了执行集**
      · ⇒ ★ 第三个来源（AST 追 COM 成员动词）**把它们救回来**（见 `effects.resolve_effect`）
    """
    from . import effects as _fx

    declared = getattr(spec, "read_only", None)
    if declared is True:
        return "read"
    if declared is False:
        return "write"
    #: ★ 声明缺失 ⇒ 从实现里解析（★ 保守合成）
    got, _why = _fx.resolve_effect(getattr(spec, "module", "") or "",
                                   getattr(spec, "function", "") or "")
    return got


def _required_of(spec) -> tuple:
    """★ 必填形参 = 没有默认值的（`default is Ellipsis`）。"""
    out = []
    for p in (getattr(spec, "params", None) or ()):
        if getattr(p, "default", None) is Ellipsis:
            out.append(p.name)
    return tuple(out)


def build_registry(*, include_server_py: bool = True) -> dict[str, ToolDescriptor]:
    """★ 从**两个注册来源**合成统一目录（★ FR-010：两种来源均进入清单）。

    ★★ 不变式（★ 见 data-model §1）：
      I1 `canonical_name` 唯一
      I2 `admitted=False` ⇒ `reject_reason` 非空
      I3 `admitted=True` ⇒ `step_name` 非空
      I4 `admitted=True` ⇒ `module` 与 `function` 都非空
      I5 `effect == "unknown"` ⇒ `admitted=False`（★ 未知副作用不得自动执行）
    """
    import register_capabilities as rc

    reg: dict[str, ToolDescriptor] = {}

    for s in rc.all_specs():
        cn = s.name
        #: ★ I1：重复即拒绝加载
        if cn in reg:
            raise RegistryError("duplicate-canonical-name", cn)
        #: ★ 唯一一条映射规则：去掉前缀（★ 只对 `solidworks_*` 成立）
        step = cn[len(PREFIX):] if cn.startswith(PREFIX) else ""
        eff = _effect_of(s)
        #: ⚠ 实测（2026-10-12，规格 329）：原来要求 **`step` 非空**才准入
        #:   ⇒ ★ **`cadstudio_*` 那 45 个（★ 含目录检索的 4 个）永远进不了执行集** ✗
        #:     —— ★ 而"未准入"看起来像"它们有问题"，其实是**判据太窄**。
        #:   ★★ 判据修正：**准入看「有没有实现 + 效应已知」**，
        #:     ★ `step_name`（裸步名）只对**方法库**有意义（★ 空也不该挡准入）。
        #:   ★ 依据：`admitted` 的用途是**「能不能被编译器选中执行」**
        #:     （★ Q12 L221 逐字：「没有完成可执行适配的入口不得被编译器选中」），
        #:     ★ 而 `cadstudio_catalog_*` **有实现、效应是 `read`** ⇒ **该准入**。
        admitted = bool(getattr(s, "module", "")) \
            and bool(getattr(s, "function", None)) and eff != "unknown"
        reason = ""
        if not admitted:
            if not getattr(s, "function", None):
                reason = "没有实现函数地址"
            elif not getattr(s, "module", ""):
                reason = "没有实现模块"
            elif eff == "unknown":
                reason = "★ 效应未知（I5：未知副作用不得自动执行）"
            else:
                reason = "未满足准入不变式"
        reg[cn] = ToolDescriptor(
            canonical_name=cn, step_name=step,
            module=getattr(s, "module", "") or "",
            function=getattr(s, "function", None) or "",
            inject=getattr(s, "inject", "") or "",
            params=tuple(p.name for p in (getattr(s, "params", None) or ())),
            required=_required_of(s),
            effect=eff, admitted=admitted, reject_reason=reason,
            source="all_specs",
        )

    if include_server_py:
        #: ★ 第二个注册来源：`server.py` 的 `@mcp.tool(...)`（45 个）
        #: ★★ 实测（2026-10-11）真实写法是**带参数的装饰器**：
        #:   `@mcp.tool(\n    name="cadstudio_resolve_backend",\n
        #:     annotations={"readOnlyHint": True, ...})`
        #: ⇒ 第一版按 `@mcp.tool\n def xxx(` 抓 ⇒ **抓到 0 个**（★ 已修）
        #: ★ 而且**工具名在 `name=` 里**，不是函数名。
        srv = ROOT / "mcp-server" / "server.py"
        if srv.is_file():
            txt = srv.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(
                    r"@mcp\.tool\((.*?)\)\s*\n(?:async\s+)?def\s+(\w+)\(", txt, re.S):
                head, fn = m.group(1), m.group(2)
                nm = re.search(r'name\s*=\s*["\']([^"\']+)["\']', head)
                cn = nm.group(1) if nm else fn
                if cn in reg:
                    continue                      #: ★ 已由 all_specs 收录
                #: ★★ 读 `annotations` 里的 `readOnlyHint`（★ 那是**官方声明**的效应）
                ro = re.search(r'["\']readOnlyHint["\']\s*:\s*(True|False)', head)
                eff = "unknown"
                if ro:
                    eff = "read" if ro.group(1) == "True" else "write"
                step = cn[len(PREFIX):] if cn.startswith(PREFIX) else ""
                #: ★ 这两个前缀的工具不在 `solidworks_` 族里 ⇒ 没有裸步名 ⇒ 不进执行集
                admitted = bool(step) and eff != "unknown"
                reason = ""
                if not admitted:
                    if not step:
                        reason = "★ 工具名不带 `solidworks_` 前缀（%s）⇒ 没有裸步名" % cn
                    else:
                        reason = "★ 效应未知（I5：未知副作用不得自动执行）"
                reg[cn] = ToolDescriptor(
                    canonical_name=cn, step_name=step,
                    module="server", function=fn, inject="",
                    params=(), required=(), effect=eff,
                    admitted=admitted, reject_reason=reason,
                    source="server_py",
                )

    if not reg:
        raise RegistryError("empty-registry", "★ 目录为空 ⇒ 不许静默通过")
    return reg


def step_index(reg: dict[str, ToolDescriptor]) -> dict[str, list[str]]:
    """★ 裸步名 → 规范名**列表**（★ 用于检出**歧义**）。"""
    idx: dict[str, list[str]] = {}
    for cn, d in reg.items():
        if d.step_name:
            idx.setdefault(d.step_name, []).append(cn)
    return idx


#: ══════════════════════════════════════════════════════════════════════
# 二、名字解析（★ C3 —— ★ 规格 §3 FR-001/002/003）
#: ══════════════════════════════════════════════════════════════════════

def resolve_step_name(step: str, reg: dict[str, ToolDescriptor]) -> str:
    """★ 裸步名 → **唯一**规范工具名。

    ★★ 三种失败都**显式抛**（★ 不静默、不猜 —— ★ FR-002）：
      · 解析不到          ⇒ `unresolved-step-name`
      · 映射到多个规范名  ⇒ `ambiguous-step-name`（★ FR-003）
      · 解析到但未准入    ⇒ `tool-not-admitted`

    ★★ 为什么只用「去前缀」这一条规则：本仓**事实 53** ——
      「启发式需要连续 ≥3 次修补才「看起来对」时，回退 + 记证据」。
      名字回退那一族试过 **6 版**都不对（30/4/1 → … → 29/6/0）。
      ⇒ **这里只认确定性规则，规则之外一律拒绝。**
    """
    idx = step_index(reg)
    hits = idx.get(step, [])
    if not hits:
        #: ★★ 先判「是不是另一个**方法 id**」—— 那是阶段 2 的「子方法展开」，
        #:   ★ **不是**拼写错误 ⇒ 给**专属码**，免得后人按错字排查（★ 事实 102 那族的教训）
        try:
            from .compiler import METHOD_LIBRARY as _ML
            if step in _ML:
                raise RegistryError(
                    "sub-method-not-expanded",
                    "★ %r 是**另一个方法 id**（%s）⇒ 属阶段 2「子方法展开」，"
                    "★ 不是拼写错误" % (step, _ML[step].goal[:40]))
        except RegistryError:
            raise
        except Exception:                                                  # noqa: BLE001
            pass
        raise RegistryError("unresolved-step-name",
                            "★ 裸步名 %r 解析不到规范工具名（★ 不猜）" % step)
    if len(hits) > 1:
        raise RegistryError("ambiguous-step-name",
                            "★ 裸步名 %r 映射到 %d 个规范名：%s" % (step, len(hits), hits))
    cn = hits[0]
    d = reg[cn]
    if not d.admitted:
        raise RegistryError("tool-not-admitted",
                            "★ %s 未准入：%s" % (cn, d.reject_reason))
    return cn


#: ══════════════════════════════════════════════════════════════════════
# 三、PlanStep / ExecutablePlan（★ C2 —— ★ 规格 §3 FR-009）
#: ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PlanStep:
    """★ 计划里的一步（★ 规格 §3 FR-009：必须带 `params` 与 `derive`）。"""

    step: str
    params: dict = field(default_factory=dict)
    derive: str = ""
    tool: str = ""            #: ★ 由 `resolve` 填，**不手写**（★ 不变式 I6）
    #: ★★ 阶段 2 · D2（共享基准）：本步**引用**哪些具名基准。
    #:   ★ 判据：改基准名 ⇒ **所有引用它的步骤都改**（★ 靠 `expand.datum_index` 查）。
    datums: tuple = ()


@dataclass(frozen=True)
class ExecutablePlan:
    method_id: str
    steps: tuple = ()
    device_class: str = ""


#: ══════════════════════════════════════════════════════════════════════
# 四、参数绑定（★ C4 —— ★ 规格 §3 FR-010）
#: ══════════════════════════════════════════════════════════════════════

def bind_params(step: PlanStep, reg: dict[str, ToolDescriptor]) -> dict:
    """★ 把 `PlanStep.params` 校验并绑定到该工具的**声明形参**。

    ★★ 判据（★ 只校验**名字与必填**；**单位换算由工具层做** —— ★ 不变式 I8）：
      · 参数名不在声明形参里 ⇒ `unknown-param`（★ 多一个就拒绝）
      · 缺必填形参           ⇒ `missing-required-param`
    """
    if not step.tool:
        raise RegistryError("unresolved-step-name",
                            "★ `PlanStep.tool` 为空 ⇒ 先调 `resolve_plan`")
    d = reg.get(step.tool)
    if d is None:
        raise RegistryError("unresolved-step-name", "★ %s 不在目录里" % step.tool)

    known = set(d.params)
    #: ★ 注入形参由执行器补（`inject`），调用方不必给
    inject = d.inject
    if inject:
        known.add(inject)

    for k in step.params:
        if k not in known:
            raise RegistryError(
                "unknown-param",
                "★ %s 没有形参 %r（声明的是 %s）" % (step.tool, k, sorted(known)))

    missing = [r for r in d.required if r not in step.params and r != inject]
    if missing:
        raise RegistryError(
            "missing-required-param",
            "★ %s 缺必填形参 %s" % (step.tool, missing))
    return dict(step.params)


#: ══════════════════════════════════════════════════════════════════════
# 五、编译：方法 → 可执行计划（★ 把 C1/C3/C4 串起来）
#: ══════════════════════════════════════════════════════════════════════

def resolve_plan(plan: ExecutablePlan,
                 reg: dict[str, ToolDescriptor] | None = None) -> ExecutablePlan:
    """★ 把计划里每个 `PlanStep.tool` 用 `resolve_step_name` 填上（★ 不变式 I6）。

    ★★ 任一步解析失败 ⇒ **整计划拒绝**（★ 不执行前半段 —— 那会留下半成品）。
    """
    reg = reg if reg is not None else build_registry()
    out = []
    for st in plan.steps:
        cn = resolve_step_name(st.step, reg)
        bind_params(PlanStep(step=st.step, params=st.params,
                             derive=st.derive, tool=cn), reg)
        out.append(PlanStep(step=st.step, params=dict(st.params),
                            derive=st.derive, tool=cn))
    return ExecutablePlan(method_id=plan.method_id, steps=tuple(out),
                          device_class=plan.device_class)
