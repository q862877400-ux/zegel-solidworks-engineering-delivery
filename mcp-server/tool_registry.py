"""声明式 MCP 工具注册 —— 把「加一个工具」从 54 行手写降到 1 条声明。

## 为什么需要它
`mcp-server/server.py` 现在 **2455 行 / 45 个 `@mcp.tool` / 46 个 `BaseInput` 类**
⇒ **平均 54 行一个工具**。而 `AGENTS.md` 已知事实 25 记着：
`server.py` 只引用 **25** 个 `scripts` 模块，**本仓库后补的 61 个模块一个都没进**（交集 = 0）。

按老办法补齐 ⇒ **~120 个函数 × 54 行 ≈ 4800 行**手写样板
（评估见 `docs/T-011-expose-capabilities-assessment.md` —— 真实工作量是 ~120 个函数，不是 814）。

**⇒ 本模块把「简单工具」变成一条声明**：
```python
ToolSpec(
    name="solidworks_topology_create_study",
    title="Create SolidWorks Topology Study",
    module="sw_topology", function="create_topology_study",
    params=[Param("study_name", str, default="Topology Study 1"), ...],
    needs_model=False,
)
```

## 设计边界（**明确不做**什么）
| 做 | 不做 |
|---|---|
| 覆盖「**调一个既有函数、参数直传**」这类工具（评估里 120 个的绝大多数） | **不**覆盖有自定义后处理的工具（如 `cadstudio_build_dxf_preview_scene`） —— 它们**继续手写**，本模块给 `extra_op` 逃生口 |
| 生成 `@mcp.tool` 装饰器 + 函数 + `op()` 闭包 | **不**自动猜参数语义（`_mm` / `_deg` / `selection` 要**显式声明**） |
| 把三条硬约束做成**注册时即报错**的门禁 | **不**改 `server.py`（本模块只提供 `register()`，接入与否由人决定） |

## 为什么「不自动猜参数语义」很重要
六条规则里的 1/2/3 是**人工判断**的：
- 规则 1：工具名 `solidworks_<域>_<动作>` —— 要判「域是什么」
- 规则 2：长度 `_mm`、角度 `_deg`，换算**只在边界做一次**（`sw_connect.mm()`）
- 规则 3：**声明式 `selection`**，禁裸坐标

**⇒ 自动生成名字会造出语义不清的名字；自动猜单位会造出静默的 1000× 错误
（本项目刚在 `CreateMesh` 上踩过：把毫米当米 ⇒ 1950 万个单元 / 20–25 GB）。**
**故本模块只做「把已判好的东西写成代码」，不做判断。**

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   mcp-server/tool_registry.py
# 定位:   AGENTS.md 已知事实 25「我们补的能力没被 MCP 暴露」的**工程解法**；
#         `docs/T-011-expose-capabilities-assessment.md` 的实现层。
#         写法照 `server.py` 既有 45 个工具的形状抽取（见该文件 1031/1045/1090 行附近）。
# 官方签名依据: 不适用（本模块只做 Python 层注册，不直接调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **本模块尚未接入 `mcp-server/server.py`** —— 那正是本会话 `mcp__solidworks__*` 工具的来源，
#   改它会动**正在运行的** MCP 表面（「单源运行」原则，已知事实 24）。
#   接入 = 在 `server.py` 里 `from tool_registry import register, SPECS` + `register(mcp, SPECS)`。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Optional

__all__ = [
    "Param",
    "ToolSpec",
    "GateError",
    "check_spec",
    "check_specs",
    "build_input_model",
    "make_tool_function",
    "register",
    "effective_inject",
    "SOLIDWORKS_NAME_RE",
    "CADSTUDIO_NAME_RE",
]

#: 六条规则 1：工具名统一 `solidworks_<域>_<动作>`；headless 用 `cadstudio_*`
SOLIDWORKS_NAME_RE = re.compile(r"^solidworks_[a-z0-9_]+$")
CADSTUDIO_NAME_RE = re.compile(r"^cadstudio_[a-z0-9_]+$")

#: 六条规则 2：长度以 `_mm` 结尾、角度以 `_deg` 结尾
_LEN_SUFFIX = "_mm"
_ANGLE_SUFFIX = "_deg"

#: 六条规则 3：选择必须用声明式 `selection`，禁裸坐标
#: ★★★ 2026-10-03（轮 433）**去掉了 `x_mm` / `y_mm` / `z_mm`** —— 而理由是
#:   **规则 2 与规则 3 在这三个名字上自相矛盾**：
#:     · 规则 2 要求**长度参数以 `_mm` 结尾**（`x_mm` 正是它要的写法）；
#:     · 规则 3 却把 `x_mm` 当"裸坐标"拦掉。
#:   ★★ 而**"裸"的定义本该是「没有单位信息、也没有具名实体」** ⇒
#:     `x_mm` **带着单位**（★ 不裸）；★ 而 `x` / `boundary_z` / `d1_x` **都不带**（★ 才裸）。
#:   ★ 依据：`AGENTS.md` 明写规则 3 **有一条文档化的例外** ——
#:     「*Sketch geometry MUST be given as in-plane coordinates — this is the documented
#:      exception in rule 3*」⇒ 草图几何**本来就该给坐标** ✓
#:   ⚠ 而**没被放过的那条**（`solidworks_surface_fill.boundary_z`）是**真欠账** ——
#:     ★ 它是"**用坐标去选那一圈边**"，★ 那**正是**规则 3 要禁的形态 ⇒ 它照旧被拦 ✓
_BARE_COORD_NAMES = {"x", "y", "z", "point", "coordinate"}


def _looks_like_coord_component(name: str) -> bool:
    """★ **结构性判据**：这个参数名看着像"**坐标的一个分量**"吗？

    ★★ 为什么加它（2026-10-01 轮 261 · **修地基 D5**）：
      原判据只有一张 **8 个名字**的表 ⇒ ★ 而本仓库实际存在的裸坐标参数**远不止**：
        `x1` / `y1` / `x2` / `y2`（草图弧/中心线/槽的端点）· `cx` / `cy`（圆心）·
        `major_x` / `minor_y`（椭圆长短轴分量）· `d1_x` / `d1_y` / `d1_z`（阵列方向分量）
      ⇒ ★ 它们**全都漏过**了规则 3 的门禁（★ 事实 153：规则有**三句**，机器只验过第一句）。
    ★★★ **而判据要"结构"不要"枚举"**（★ 同轮 249 用 `GetTypeName2` 判特征、不枚举容器名的同一思路）：
      · **`^[a-z]\\d?_[xyz]$`** ⇒ `d1_x` / `major_y` / `x1`… ⚠ 不，那会命中 `x1`
      · 形式① **`^[xyz]\\d*$`** ⇒ `x` / `x1` / `y2` / `z`（★ 轴名 + 可选编号）
      · 形式② **`^c[xyz]$`** ⇒ `cx` / `cy` / `cz`（★ 圆心）
      · 形式③ **`(^|_)[xyz]\\d*$`** ⇒ `major_x` / `d1_x` / `minor_y`（★ 以轴名结尾）
      · 形式④ **`^[\\w]*[dD]\\d_[xyz]$`** ⇒ `d1_x` / `d2_y`（★ 已由形式③覆盖，留作说明）
    ⚠⚠ **刻意不收的**（★ 事实 74：按名字判语义在本项目失败过 8 次）：
      · `w` / `h` ⇒ ★ 在非几何语境里同样常用（`lot_size` 是批量、`h` 可能是句柄）
      · `center` ⇒ ★ 它是**元组名**、语义上算坐标，**但名字本身不表态**（★ 收进来会误伤
        「用户自定义的中心名」这类参数）⇒ ★ **只登记不判**（★ 见 `_COORD_COMPONENT_NOTE`）。
    """
    import re

    low = str(name).strip().lower()
    if not low:
        return False
    #: ★★★ 2026-10-03（轮 433）**"裸"的定义就是「没有单位信息」** ——
    #:   ★ 而 `_mm` 后缀**恰恰携带着单位信息**（★ 规则 2 **要求**长度参数以 `_mm` 结尾）。
    #:   ★★ 所以**以 `_mm` 结尾的坐标不是裸坐标** ⇒ 放过。
    #:   ⚠ 而这条**不是新例外** —— ★ 门禁**本来就在**放过它：`sketch_add_line` 的
    #:     `start_x_mm` / `end_x_mm` **从没被拦过**（★ 因为它们不以 `_x$` 结尾）。
    #:   ★★★ 矛盾在**精确黑名单**那三个条目（`x_mm`/`y_mm`/`z_mm`）：
    #:     ★ 它们**同时**被规则 2 要求、★ 被规则 3 拦 —— ★ **两条规则自相矛盾** ⚠（本轮查明）
    #:   ⇒ ★ 而**无单位**的（`x` · `boundary_z` · `d1_x` · `major_y`）**照旧拦** ✓
    if low.endswith("_mm"):
        return False
    if re.fullmatch(r"[xyz]\d*", low):            #: x / x1 / y2 / z
        return True
    if re.fullmatch(r"c[xyz]", low):              #: cx / cy / cz
        return True
    if re.search(r"(^|_)[xyz]\d*$", low):         #: major_x / d1_x / minor_y / point_x
        return True
    return False


#: ★ 语义上是坐标、**但名字不表态**的那些（★ 只登记，**不判** —— 免得制造假阳性）
_COORD_COMPONENT_NOTE = ("center", "w", "h")

#: 规则 2 的**长度词汇**：参数名里出现这些词 ⇒ 认为是长度参数，必须以 `_mm` 结尾。
#: ⚠ 这是**有界词表**，刻意保守（只收"几乎必然是长度"的词）。
#: ⚠⚠ **不包含** `size` / `w` / `h` —— 它们在非几何语境里同样常用
#: （`lot_size` 是批量、`h` 可能是句柄）⇒ 收进来只会制造假阳性
#: （见已知事实 74：按名字判语义的检查在本项目的失败记录）。
_LEN_WORDS = (
    "radius", "diameter", "depth", "thickness", "distance",
    "width", "height", "length", "offset", "spacing", "pitch",
)

#: ⚑⚑ **规则 2 的显式豁免**：这些参数的**单位不是毫米**，`_mm` 后缀会**说错话**。
#: 判据：该参数的值是**直接交给 SolidWorks 的"文档默认量"**，而不是我们换算出的毫米。
#: ⚠ 照 `check_interface_member_ownership.MANUAL_MAP` 的先例：
#: **每条都要写清"为什么它不属于这一条"**，没依据的不许进来。
#: 规则 2 的**角度词汇**。⚠ 刻意**不含** `rad` —— 它会**子串命中 `radius`**
#: （本轮实测：`bend_radius_mm` / `use_default_radius` 一共 **7 处**假阳性就是这么来的）。
_ANGLE_WORDS = ("angle", "degrees", "draft")

#: ⚑⚑ **规则 2 的角度那一半的显式豁免**（判据同长度表：值是**交给 SolidWorks 的
#: 文档默认量**，不是我们换算出的度）。
_ANGLE_SUFFIX_EXEMPT: dict = {
    ("solidworks_mold_parting_surface", "angle"):
        "官方参数 `Angle`；本工具的文档写明「**0.0 = 用文档默认**」⇒ "
        "是**交给 SolidWorks 的文档默认量** ⇒ 加 `_deg` 反而**说错话**。",
}

_LEN_SUFFIX_EXEMPT: dict = {
    ("solidworks_mold_core_cavity_split", "thickness"):
        "官方参数 `Thickness`；本工具的文档写明「0.0 = 用文档默认」⇒ "
        "它是**交给 SolidWorks 的文档默认量**，不是我们换算出的毫米 ⇒ "
        "加 `_mm` 反而**说错话**。",
    ("solidworks_mold_core_cavity_split", "offset"):
        "同 `thickness`：官方 `Offset`，文档写明「0.0 = 用文档默认」。",
    ("solidworks_mold_parting_surface", "distance"):
        "同 `thickness`：官方 `Distance`，文档写明「0.0 = 用文档默认」。",
    ("solidworks_export_bmp", "pixel_width"):
        "★ 它**不是长度**，是**像素** —— 官方 `ExportToBMP(FileName, Width, Height)` 的两个尺寸"
        "单位是像素。⚠ 而门禁按**子串**匹配（`width` ∈ `pixel_width`）⇒ ★ **改名解决不了**，"
        "只能在这里登记。★ 登记的理由要写清：加 `_mm` 会把「像素」说成「毫米」——**那是说错话**。",
    ("solidworks_export_bmp", "pixel_height"):
        "同 `pixel_width`：官方 `ExportToBMP` 的 `Height`，单位是**像素**不是长度。",
}


class GateError(ValueError):
    """注册时违反「并入六条规则」⇒ 直接抛，不让它进到运行期。"""


@dataclass(frozen=True)
class Param:
    """一个入参的**显式**声明。

    :param name: 参数名。长度参数**必须以 `_mm` 结尾**、角度以 `_deg` 结尾（规则 2）。
    :param kind: Python 类型注解（`str` / `float` / `int` / `bool`）。
    :param default: 默认值；给 `...` 表示必填。
    :param description: 给人看的说明（会进 Pydantic 的 `Field(description=...)`）。
    :param required: 覆盖「没有默认值即必填」的推断。
    """

    name: str
    kind: type
    default: Any = ...
    description: str = ""
    required: Optional[bool] = None

    @property
    def is_required(self) -> bool:
        return self.required if self.required is not None else self.default is ...


def effective_inject(spec: "ToolSpec") -> str:
    """把 ``inject`` 与兼容别名 ``needs_model`` 归一成一个字符串。

    ⚠ 两者都给且冲突 ⇒ 抛 :class:`GateError`（**不静默取其一**）。
    """
    if spec.inject and spec.needs_model:
        raise GateError(
            "工具 %r 同时给了 inject=%r 与 needs_model=True —— 二者等价，只留一个"
            % (spec.name, spec.inject)
        )
    if spec.inject:
        return spec.inject
    return "model" if spec.needs_model else ""


@dataclass
class ToolSpec:
    """一个工具的**声明**。

    :param name: MCP 工具名（规则 1 的正则会被检查）。
    :param title: 给人看的标题。
    :param module: `scripts` 下的模块名，如 `"sw_topology"`。
    :param function: 该模块里的函数名。
    :param params: 入参声明列表（**不含** `response_format`，注册器自动加）。
    :param inject: **注入哪种宿主对象**（注册器负责造并把它作为实参传进去；空串 = 不注入）。
        取值由**调用方注册的解析器**决定 —— 本模块**不硬编码任何宿主 API**，
        因此可独立测试（见 `tests/test_tool_registry.py` 的假宿主）。
        约定俗成的四个：``""`` / ``"model"``（活动文档）/ ``"sw_app"``（ISldWorks）/
        ``"study"``（按 ``study_name`` 入参解析）。
        ⚠ 注入用的**关键字名**必须与目标函数的**真实形参名**一致
        （``model`` / ``sw_app`` / ``study``）。
    :param needs_model: **兼容别名**（等价于 ``inject="model"``）；新声明请直接用 ``inject``。
    :param param_alias: **对外参数名 → 目标函数形参名** 的显式映射。
        值为 ``None`` 表示「该参数由解析器消费，**不传给目标函数**」。
        未列出的参数**同名直传**。
        ⚠ 为什么要显式：MCP 表面用 ``study_name`` 比 ``name`` 清楚、
        ``element_size_mm`` 比 ``element_size`` 合规（规则 2），
        而实现里的名字不该为了对外好看去改。
        **但别名必须写出来** —— 否则与「拼错了参数名」无法区分。
    :param derived_args: **从已声明的标量入参派生额外实参**，形如
        ``lambda params: {"spec": BaseFlangeSpec(...)}``。返回的字典会**并进**
        调用目标函数的关键字实参里。
        ⚠ 与 `extra_op` 的分工：`extra_op` **替换整个调用**（用了就放弃声明式）；
        `derived_args` **只补一个实参**，`module`/`function`/同名直传都还在。
        **能不退就退。**
        ⚠ 单位换算也放这里，且**只做一次**（并入规范规则 2）：spec 说「米」、
        MCP 表面按规则 2 用 ``_mm`` ⇒ 在派生函数里 ``/1000.0``。
    :param pre_call: **调用前的副作用钩子**，形如 ``lambda params: None``。
        用途：那些**实现里明写「调用前必须先选好」**的函数（如钣金 C2 类：
        `create_edge_flange` / `create_gusset` / `create_draft`）。
        ⚠ 与 `derived_args` 的分工：`derived_args` **产出实参**，
        `pre_call` **只做副作用、不产出实参**。给字段安它没有的含义是本项目反对的。
    :param omitted_params: **故意不暴露**的形参名（如 ``Object`` 型的 ``colors``）。
    :param read_only: 只读工具 ⇒ `readOnlyHint=True`。
    :param idempotent: 幂等 ⇒ `idempotentHint=True`。
    :param load_automation: 是否需要加载 SolidWorks 自动化（headless 工具传 False）。
    :param extra_op: 逃生口 —— 有自定义后处理的工具给一个 `op(params) -> Any`，
        此时 `module`/`function` 可省。
    :param doc: 函数 docstring（会变成 MCP 工具描述）。
    :param omitted_params: **故意不暴露**的形参名（如 `Object` 型的 `colors`）。
        ⚠ 必填理由：**省略必须是显式的**，否则它和「手抄漏了」无法区分 ——
        `tests/test_tool_specs_batch1.py` 就靠这个字段区分二者。
    """

    name: str
    title: str
    module: str = ""
    function: str = ""
    params: list[Param] = field(default_factory=list)
    inject: str = ""
    needs_model: bool = False
    read_only: bool = False
    idempotent: bool = True
    load_automation: bool = True
    extra_op: Optional[Callable[[Any], Any]] = None
    doc: str = ""
    omitted_params: tuple[str, ...] = ()
    param_alias: dict[str, Optional[str]] = field(default_factory=dict)
    derived_args: Optional[Callable[[Any], dict]] = None
    pre_call: Optional[Callable[[Any], None]] = None


def check_spec(spec: ToolSpec) -> None:
    """把三条可由机器判定的规则**在注册时**验掉；违者抛 :class:`GateError`。

    ⚠ 这里只验**机器能判**的（名字正则、后缀、裸坐标）；
    「域判得对不对」「单位换算对不对」属人工判断，本模块**不假装能验**。
    """
    if not (SOLIDWORKS_NAME_RE.match(spec.name) or CADSTUDIO_NAME_RE.match(spec.name)):
        raise GateError(
            "规则 1 违反：工具名 %r 必须匹配 %s 或 %s（域在前、动在后、蛇形）"
            % (spec.name, SOLIDWORKS_NAME_RE.pattern, CADSTUDIO_NAME_RE.pattern)
        )
    if not spec.title.strip():
        raise GateError("工具 %r 缺 title" % spec.name)
    if spec.pre_call is not None and spec.extra_op is not None:
        raise GateError(
            "工具 %r 同时给了 pre_call 与 extra_op —— extra_op 自己就是完整执行体，"
            "pre_call 无处安放" % spec.name
        )
    if spec.derived_args is not None and spec.extra_op is not None:
        raise GateError(
            "工具 %r 同时给了 derived_args 与 extra_op —— 前者是「补一个实参」，"
            "后者是「替换整个调用」，语义冲突，只留一个" % spec.name
        )
    inj = effective_inject(spec)
    if inj and not inj.isidentifier():
        raise GateError("工具 %r 的 inject=%r 不是合法标识符" % (spec.name, inj))
    if inj and spec.extra_op is not None:
        raise GateError(
            "工具 %r 同时给了 inject=%r 与 extra_op —— extra_op 自己负责注入，二者互斥"
            % (spec.name, inj)
        )
    if not (spec.extra_op or (spec.module and spec.function)):
        raise GateError(
            "工具 %r 既没给 (module, function) 也没给 extra_op ⇒ 没有可执行体" % spec.name
        )
    if spec.name.startswith("solidworks_") and not spec.load_automation:
        raise GateError(
            "工具 %r 以 solidworks_ 开头却 load_automation=False —— "
            "headless 路线应当用 cadstudio_*（规则 1：两者不混用）" % spec.name
        )
    for src, dst in spec.param_alias.items():
        if src not in {p.name for p in spec.params}:
            raise GateError(
                "工具 %r 的 param_alias 指向未声明的参数 %r" % (spec.name, src)
            )
        if dst is not None and not dst.isidentifier():
            raise GateError(
                "工具 %r 的 param_alias[%r]=%r 不是合法形参名" % (spec.name, src, dst)
            )
        if dst is not None and dst in spec.omitted_params:
            raise GateError(
                "工具 %r 的 param_alias[%r] 指向被省略的形参 %r" % (spec.name, src, dst)
            )
    seen: set[str] = set()
    for p in spec.params:
        if p.name in seen:
            raise GateError("工具 %r 的参数 %r 重复" % (spec.name, p.name))
        seen.add(p.name)
        if p.name in _BARE_COORD_NAMES or _looks_like_coord_component(p.name):
            raise GateError(
                "规则 3 违反：工具 %r 的入参 %r 是裸坐标 —— "
                "必须改用具名实体 + 声明式 selection" % (spec.name, p.name)
            )
        #: ★★ 规则 3 的**第二句**（2026-10-01 轮 218 接上，地基③）。
        #:    ⚠ 规则 3 在文档里有**三句**，机器**只验过第一句**（参数名）⇒ 后两句无人看守（事实 153）。
        #:    ★ 而**能被机器判的其实只有两句**：
        #:      句1「不许裸坐标」    ⇒ 上面那段（参数名黑名单）
        #:      句2「必须是声明式选择」⇒ **本段**：声明式选择在参数上就是 `selection: str`
        #:      句3「按 mark 分配」   ⇒ ★ **静态判不了** —— 那是**运行行为**
        #:                              （多引用特征读 mark 0/1/2，不读选择顺序）⇒ 只能靠真机证据
        #:    ⚠⚠ 我一度还加了「说明里必须写合法取值」「mark 必须说明」两条 ——
        #:       ★ **那是我自己的好习惯，不是规则的内容** ⇒ 已撤掉：
        #:       门禁**只验规则真正要求的**，不把偏好伪装成规则。
        #:       撤掉的理由有证据：既有的 `test_rule3_named_entity_selection_is_ok`
        #:       断言「`Param("selection", str)` 无说明也应通过」—— 那条测试编码的是**本意**。
        if p.name == "selection" and p.kind is not str:
            raise GateError(
                "规则 3 违反：工具 %r 的 selection 必须是 str（声明式选择器），"
                "现为 %r —— 传数字/坐标不是声明式选择" % (spec.name, p.kind.__name__)
            )
        if p.name in ("response_format",):
            raise GateError(
                "工具 %r 不要自己声明 response_format —— 注册器会自动加" % spec.name
            )
        # ⚑⚑ 规则 2 的**长度那一半**（2026-10-01 轮 134 接上）。
        #    ⚠⚠ **接上之前，这一半从未生效** —— `_LEN_SUFFIX` 是个**死常量**
        #    （只在定义处出现一次）。⇒ 规则 2 一直被算进「五统一门禁通过」，
        #    但它的长度那一半**从来没拦过任何东西**（已知事实 40：存在但没人用的守卫）。
        #    证据：`tests/test_rule2_length_suffix_is_enforced.py` 的负例。
        low = p.name.lower()
        #: ⚠ `bool` **不是长度**（`use_default_radius` / `reverse_thickness` 是**标志**）
        if p.kind is not bool and any(w in low for w in _LEN_WORDS) \
                and not low.endswith(_LEN_SUFFIX):
            if (spec.name, p.name) not in _LEN_SUFFIX_EXEMPT:
                raise GateError(
                    "规则 2 违反：工具 %r 的入参 %r 像是**长度**，却不以 %r 结尾 —— "
                    "要么改名（`%s%s`），要么在 `_LEN_SUFFIX_EXEMPT` 里"
                    "**写明为什么它不是毫米**"
                    % (spec.name, p.name, _LEN_SUFFIX, p.name, _LEN_SUFFIX)
                )
        # ⚑⚑ 规则 2 的**角度那一半**（2026-10-01 轮 135 接上；同 `_LEN_SUFFIX` 一样，
        #    它此前也是**死常量** —— `probe_dead_guards.py` 扫出来的）。
        if p.kind is not bool and any(w in low for w in _ANGLE_WORDS) \
                and not low.endswith(_ANGLE_SUFFIX):
            if (spec.name, p.name) not in _ANGLE_SUFFIX_EXEMPT:
                raise GateError(
                    "规则 2 违反：工具 %r 的入参 %r 像是**角度**，却不以 %r 结尾 —— "
                    "要么改名（`%s%s`），要么在 `_ANGLE_SUFFIX_EXEMPT` 里"
                    "**写明为什么它不是度**"
                    % (spec.name, p.name, _ANGLE_SUFFIX, p.name, _ANGLE_SUFFIX)
                )


def check_specs(specs: list[ToolSpec]) -> list[str]:
    """批量校验，返回**所有**问题（不短路）；空列表 = 全过。"""
    problems: list[str] = []
    names: set[str] = set()
    for s in specs:
        try:
            check_spec(s)
        except GateError as exc:
            problems.append(str(exc))
        if s.name in names:
            problems.append("工具名重复：%r" % s.name)
        names.add(s.name)
    return problems


def build_input_model(spec: ToolSpec, base: type, response_enum: Any) -> type:
    """由声明生成 Pydantic 输入模型（`class <Name>Input(base)`）。

    `response_format` 由**入参顺序的最后一位**固定加上 —— 与 `server.py` 既有 45 个工具一致。
    """
    from pydantic import Field

    model_name = "".join(part.capitalize() for part in spec.name.split("_")) + "Input"
    fields: dict[str, Any] = {}
    for p in spec.params:
        kwargs: dict[str, Any] = {}
        if p.description:
            kwargs["description"] = p.description
        if p.is_required:
            fields[p.name] = (p.kind, Field(..., **kwargs))
        else:
            fields[p.name] = (p.kind, Field(default=p.default, **kwargs))
    fields["response_format"] = (
        response_enum,
        Field(default=response_enum.JSON, description="Return format."),
    )
    return type(model_name, (base,), {"__annotations__": {k: v[0] for k, v in fields.items()},
                                      **{k: v[1] for k, v in fields.items()}})


def make_tool_function(spec: ToolSpec, input_model: type, run_locked: Callable[..., str],
                       resolve_model: Optional[Callable[[], Any]] = None,
                       resolvers: Optional[dict[str, Callable[[Any], Any]]] = None,
                       inject_as: Optional[str] = None) -> Callable[..., str]:
    """生成与 `server.py` 既有工具**同形状**的函数体。

    形状（照 `server.py:1077` 的 `cadstudio_write_open_format` 抽取）::

        def <name>(params: <X>Input) -> str:
            \"\"\"<spec.doc>\"\"\"
            def op():
                from scripts.<module> import <function>
                return <function>(<kwargs>)
            return run_locked(op, params.response_format, load_automation=...)
    """

    def _impl(params: Any) -> str:  # noqa: ANN401
        def op():
            kwargs = {}
            for p in spec.params:
                # `param_alias` 里 None = 由解析器消费，不进目标函数
                if p.name in spec.param_alias and spec.param_alias[p.name] is None:
                    continue
                target = spec.param_alias.get(p.name, p.name)
                kwargs[target] = getattr(params, p.name)
            inj = effective_inject(spec)
            if inj:
                resolver = (resolvers or {}).get(inj)
                if resolver is None:
                    raise RuntimeError(
                        "工具 %r 声明了 inject=%r，但注册时没给对应的解析器"
                        "（已给的：%r）" % (spec.name, inj, sorted((resolvers or {}).keys()))
                    )
                kwargs[inject_as or inj] = resolver(params)
            if spec.extra_op is not None:
                return spec.extra_op(params)
            if spec.pre_call is not None:
                # ⚠ 在**调用目标函数之前**执行（选择类副作用）——
                #   实现里明写「调用前必须先选好」的函数靠它。
                spec.pre_call(params)
            if spec.derived_args is not None:
                # ⚠ 派生实参**不得覆盖**已直传的参数名 —— 覆盖会静默改变语义。
                extra = spec.derived_args(params) or {}
                clash = set(extra) & set(kwargs)
                if clash:
                    raise GateError(
                        "工具 %r 的 derived_args 想覆盖已直传的参数 %r —— 不允许"
                        % (spec.name, sorted(clash))
                    )
                kwargs.update(extra)
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            return getattr(mod, spec.function)(**kwargs)

        return run_locked(op, params.response_format,
                          load_automation=spec.load_automation)

    _impl.__name__ = spec.name
    _impl.__doc__ = spec.doc or spec.title
    _impl.__annotations__ = {"params": input_model, "return": str}
    return _impl


def register(mcp: Any, specs: list[ToolSpec], base: type, response_enum: Any,
             run_locked: Callable[..., str],
             resolve_model: Optional[Callable[[], Any]] = None,
             resolvers: Optional[dict[str, Callable[[Any], Any]]] = None) -> list[str]:
    """把声明注册成 MCP 工具。返回**已注册的工具名**（供日志与门禁核对）。

    先 `check_specs` 全量校验 —— **有任何问题就整体不注册**（不让半套工具进到运行期）。

    :param resolvers: 注入解析器表：``{注入名: (params) -> 宿主对象}``。
        **由调用方提供** ⇒ 本模块保持宿主无关（其自测用假宿主）。
        典型：``{"model": lambda p: active_doc(), "sw_app": lambda p: sw(),
                 "study": lambda p: study_by_name(sw(), p.study_name)}``。
        兼容：只给 ``resolve_model`` 时等价于 ``{"model": lambda p: resolve_model()}``。
    """
    if resolvers is None and resolve_model is not None:
        resolvers = {"model": lambda _p: resolve_model()}

    problems = check_specs(specs)
    if problems:
        raise GateError("声明未过门禁，未注册任何工具：\n  - " + "\n  - ".join(problems))
    registered: list[str] = []
    for spec in specs:
        model = build_input_model(spec, base, response_enum)
        fn = make_tool_function(spec, model, run_locked, resolve_model, resolvers)
        decorated = mcp.tool(
            name=spec.name,
            title=spec.title,
            annotations={
                "readOnlyHint": bool(spec.read_only),
                "destructiveHint": False,
                "idempotentHint": bool(spec.idempotent),
                "openWorldHint": False,
            },
        )(fn)
        registered.append(spec.name)
        # 保持模块级可见（MCP 库会按名字解析）
        globals()[spec.name] = decorated
    return registered
