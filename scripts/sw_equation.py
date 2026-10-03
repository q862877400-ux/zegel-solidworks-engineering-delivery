"""
方程式（Equations）—— 增 / 列 / 删 / 求解。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   **本项目自建**（不是从外部项目移植）。
#
# ⚠ 本模块补 `docs/union-gap-triage.md`「**真缺**」档里的一条：`equation`。
#   `022` 的核样确认它确实没有实现（`EquationMgr` 只作为**参数名**在别处出现过）。
#
# ## 官方签名依据（**两源互证**，铁律 4）
#   ① 出厂反射 `iface_sldworks.txt`：
#        `IEquationMgr EquationMgr GetEquationMgr()`            （在 `IModelDoc2` 上，**0 参**）
#        `Int32 Add2(Int32, String, Boolean)`
#        `Int32 GetCount()`
#        `Int32 Delete(Int32)`
#        `Int32 EvaluateAll()`
#   ② 结构化 md `C:\\swapi\\types\\IEquationMgr\\*.md`：
#        `System.int Add2(System.int Index, System.string Equation, System.bool Solve)`
#        `System.int GetCount()` · `System.int Delete(System.int Index)`
#        `System.int EvaluateAll()`
#   ⇒ **两源逐条一致**，无需类型库裁决。
#
# ## ⚠⚠ `Add` 已废弃 —— 走 `Add2`
#   官方 md 明写 `IEquationMgr.Add` 是 **Obsolete. Superseded by IEquationMgr::Add2.**
#   ⇒ 本模块用 **`Add2`**（`Add` 少一个 `Solve` 参数）。
#
# ## 「方程式字符串」的格式（官方 Remarks 原文，**照抄不解释**）
#   必须按**在 UI 里输入那样**写，**维度名要带双引号**：
#   ```
#   "B" = 2                                      （全局变量赋值）
#   "N_SPOKES@CirPattern" = "BARLENGTH@Sketch2" /10   （零件方程式）
#   "D1@Extrude2" = (IIf("D1@Extrude3">20, 15, 6))+5  （用到 VB 的 IIf 函数）
#   ```
#
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚑ **验证等级：`verified`**（2026-10-01 轮 116 由 `stitched` 升上来）——
#   依据 **真机冒烟** `python tools/verify_equation_smoke.py`（**5/5 通过**，SW 2026 SP4.1 / 34.4.1）：
#     新建临时零件 → `add_equation('"SMOKE_B" = 2')` 返回下标 **0** →
#     `list_equations` 读回 **1 条且内容原样**（★ **往返一致** ⇒ 真写进去了、不是空操作）→
#     `evaluate_equations` 不抛 → **收尾无残留模态框** → 临时件已关且未保存。
#   ⚠ 只验了**全局变量方程式**这一种；**维度方程式**与 `delete_equation` **未测**。
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

try:
    from .sw_connect import get_com_member, set_com_member
except ImportError:      # pragma: no cover - 直接以 scripts/ 为根导入时
    from sw_connect import get_com_member, set_com_member          # type: ignore, set_com_member

#: 官方 `Add2` 的 `Index` 语义：`-1` 表示**追加到末尾**。
APPEND_AT_END = -1


def _manager(model):
    """取 `IEquationMgr`（官方 `IModelDoc2.GetEquationMgr()`，**0 参**）。"""
    mgr = get_com_member(model, "GetEquationMgr")
    if mgr is None:
        raise RuntimeError(
            "IModelDoc2.GetEquationMgr() 返回 None ⇒ 拿不到方程式管理器"
            "（常见原因：当前文档类型不支持方程式，或不在可编辑态）"
        )
    return mgr


def add_equation(model, equation: str, *, index: int = APPEND_AT_END, solve: bool = True):
    """加一条方程式。

    ⚠ **走 `Add2`**（`Add` 官方已标 **Obsolete**）。

    :param equation: 方程式字符串，**按 UI 里那样写、维度名带双引号** ——
        例 `'"B" = 2'` · `'"N_SPOKES@CirPattern" = "BARLENGTH@Sketch2" /10'`。
    :param index: 0 基下标；**`-1` = 追加到末尾**（官方语义）。
    :param solve: `True` 立即求解（官方 `Solve`）。
    :returns: 新方程式的下标（官方：失败返回 `-1`）。
    :raises RuntimeError: 传空串，或官方返回 `-1`（**不静默成功**）。
    """
    text = (equation or "").strip()
    if not text:
        raise RuntimeError("方程式字符串为空 —— 官方 `Add2` 会返回 -1，这里提前拦下")
    mgr = _manager(model)
    got = get_com_member(mgr, "Add2", int(index), text, bool(solve))
    if got is None or int(got) == -1:
        raise RuntimeError(
            "IEquationMgr.Add2 返回 -1（失败）—— 常见原因："
            "**方程式的维度名没带双引号**，或引用的维度在本模型中不存在。"
            "官方 Remarks：字符串必须按「在 UI 里输入那样」写。"
        )
    return int(got)


def list_equations(model):
    """列出全部方程式（`GetCount()` + `Equation[i]`）。"""
    mgr = _manager(model)
    count = int(get_com_member(mgr, "GetCount") or 0)
    out = []
    for i in range(count):
        #: ★★ 2026-10-03（轮 470）**修正一次过度替换** ——
        #:   本行原本是 `get_com_member(mgr, "Equation", i)`（★ **读**）：
        #:   `Equation` 是**索引属性**，`i` 是**下标**，**返回值**是要取的等式文本。
        #:   ⚠ 同轮我把 98 处「写 COM 属性」从 `get_com_member(对象, 名, 值)` 批量改名为
        #:     `set_com_member` 时，**按形态匹配 ⇒ 把这一处也改了** ⇒ 于是它变成"写下标"
        #:     并回 0/1/2 ⇒ 测试 `assert [0,1,2] == ['"A" = 1', …]` 当场失败。
        #:   ★ **判据（可静态判）**：**返回值被使用 ⇒ 那是读**；返回值被丢掉才是写。
        #:     ★★ 同族共 3 处（此处 + `sw_assembly.py` 的 `MateEntityType` / `MateComponentName`），
        #:     已由「返回值被使用」这一条一次找全。
        out.append(get_com_member(mgr, "Equation", i))
    return out


def delete_equation(model, index: int):
    """删掉第 `index` 条方程式（官方 `Delete(Int32)`）。"""
    mgr = _manager(model)
    got = get_com_member(mgr, "Delete", int(index))
    if got is None or int(got) == -1:
        raise RuntimeError("IEquationMgr.Delete 返回 -1（失败）—— 下标越界？index=%d" % index)
    return int(got)


def evaluate_equations(model):
    """让官方把全部方程式求一遍值（`EvaluateAll()`）。"""
    mgr = _manager(model)
    got = get_com_member(mgr, "EvaluateAll")
    if got is None:
        raise RuntimeError("IEquationMgr.EvaluateAll() 返回 None ⇒ 无法确认是否求解成功")
    return int(got)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自建（**不是**从四家外部 MCP 项目移植）。
# 依据:   ① 出厂类型库反射 `iface_sldworks.txt`（`GetEquationMgr` / `Add2` / `GetCount` /
#            `Delete` / `EvaluateAll` 逐条核过）
#         ② `C:\swapi\types\IEquationMgr\*.md`（参数名 + **`Add` 已 Obsolete** + 字符串格式 Remarks）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：**无本机运行证据**，不得标 `verified`。
# ─────────────────────────────────────────────────────────────────────
