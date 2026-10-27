"""★ 批次 91：**弹窗护栏 / 焦点 / 倒角几何 / 曲面运行时** —— 11 个（★ 首参全是标量或窗口句柄）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_gui_modal.py`（弹窗护栏）· `scripts/sw_gui_focus.py`（焦点）·
# `scripts/sw_chamfer_geometry.py`（倒角几何**纯计算**）· `scripts/sw_surface.py`（运行
# 时可用性）
# 定位:   ★ 规格 `specs/205-tool-ramp/` §8 的**批 91** —— ★ 本批的选域依据是**漏斗勘探**
# （`tools/bunny_toolspec_pipeline.py survey`）：★ 我把候选按"参数是否**全是显式标量**"
# 筛过，
#         只留 **25 个**，再剔掉基础设施/内部件 ⇒ ★ 本批 11 个 ✓
# 官方依据: ★★ **四个模块都没有官方 md 页**（它们全是**本仓自研**的设备层/几何层）——
#   `sw_gui_modal` / `sw_gui_focus` 是 **Win32 GUI 层**（pywin32，不是 SolidWorks API）；
#   `sw_chamfer_geometry` 是**纯数学**（倒角切掉的体积）；`sw_surface.runtime_available`
#   读的是本仓自己的 `IMODELER_RUNTIME_*` 实测表 ⇒ ★ 真源 = **本仓源码**，如实写进 doc，
#   ★ **不编官方签名**（铁律 5）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **11 个工具** ⇒ 工具数 422 → **433**
# ★★ 本批**不做**的（FR-002/D-5）：
#     · `sw_capture.capture(...)` —— 返回 **PIL `Image`** ⇒ ★ 过不了 MCP 的 JSON 边界
#       （★ 要有截图能力，用既有 `solidworks_export_image` / `solidworks_export_bmp`）✓
# · `sw_com_traps.{is_type_mismatch,explain,byref_long}` —— ★ 政策不做（详见 `REFUSED`）
# ✓
#     · `sw_sensor.{out_double,out_bstr}` —— ★ COM 出参工厂，**内部管道** ✓
# · `sw_sheet_metal.require_verified` / `sw_isolate.run_isolated` / `sw_simulation_worke
# r.*`
#       —— ★ 属于**基础设施/隔离执行**（FR-007），不是用户动作 ⇒ 本批不发 ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH91"]

#: ★ 窗口句柄的说明（四个 GUI 工具共用）—— ★ 它不是几何坐标 ⇒ **不违反规则 3** ✓
_HWND = (
    "主窗口句柄（★ **窗口句柄**，不是几何坐标 —— 规则 3 说的是几何 x/y/z）。"
    "★ **传 0 = 让本工具自己去找**（本模块的默认行为）✓ "
    "★ 要显式给：先用 `solidworks_gui_get_foreground_window` 取回句柄再传进来 ✓"
)

SPECS_BATCH91 = [
    # ── ① 弹窗护栏（4）—— ★★ 本仓的看家机制（事实 527 的常驻监控就是它）───────────────
    # ─
    ToolSpec(
        name="solidworks_gui_find_modals",
        title="Find Visible Top-Level Modals Owned by This Process",
        module="sw_gui_modal",
        function="find_modals",
        inject="",
        params=[Param("main_hwnd", int, default=0, description=_HWND)],
        evidence=(
            "找出**同进程、与主窗口分离的可见顶层对话框**（★ 判据：Win32 类 `#32770` **或** 有 Button **或** 有可读文本"
            " —— ★ 本仓刻意**不认类名**，因为那是偶然的）✓ ★ 官方依据：**本仓自研**（`scripts/sw_gui_modal.py`，pywin32"
            " + Win32 API，**不是** SolidWorks API 成员）⇒ ★ 真源是源码本身 ✓ ★★ 为什么它值得挂：弹窗会让 COM 调用**永"
            "久冻住**（本仓多轮实测）⇒ **先看有没有弹窗**是无人值守的第一步 ✓ 返回 `[{hwnd, cls, title, rect}, …]`。"
        ),
        doc="找出**同进程、与主窗口分离的可见顶层对话框**（★ 判据：Win32 类 `#32770` **或** 有 Button "
        "**或** 有可读文本 —— ★ 本仓刻意**不认类名**，因为那是偶然的）✓ "
        "★ 官方依据：**本仓自研**（`scripts/sw_gui_modal.py`，pywin32 + Win32 API，"
        "**不是** SolidWorks API 成员）⇒ ★ 真源是源码本身 ✓ "
        "★★ 为什么它值得挂：弹窗会让 COM 调用**永久冻住**（本仓多轮实测）⇒ "
        "**先看有没有弹窗**是无人值守的第一步 ✓ 返回 `[{hwnd, cls, title, rect}, …]`。",
    ),
    ToolSpec(
        name="solidworks_gui_modal_report",
        title="Modal Guard Report (what is open, and what it looks like)",
        module="sw_gui_modal",
        function="modal_report",
        inject="",
        params=[Param("main_hwnd", int, default=0, description=_HWND)],
        evidence=(
            "把当前弹窗状况打成一份**可判的报告**（★ 给「要不要点 / 能不能继续」提供判据）✓ ★ 官方依据：**本仓自研**（`"
            "scripts/sw_gui_modal.py`）⇒ 真源是源码 ✓ ★ 与 `solidworks_gui_find_modals` 的分工：那个只列句柄，这个给**"
            "可读的判据** ✓"
        ),
        doc="把当前弹窗状况打成一份**可判的报告**（★ 给「要不要点 / 能不能继续」提供判据）✓ "
        "★ 官方依据：**本仓自研**（`scripts/sw_gui_modal.py`）⇒ 真源是源码 ✓ "
        "★ 与 `solidworks_gui_find_modals` 的分工：那个只列句柄，这个给**可读的判据** ✓",
    ),
    ToolSpec(
        name="solidworks_gui_assert_no_modal",
        title="Assert No Modal Is Open (raises if one is)",
        module="sw_gui_modal",
        function="assert_no_modal",
        inject="",
        params=[
            Param("main_hwnd", int, default=0, description=_HWND),
            Param(
                "where",
                str,
                default="",
                description="★ 出错信息里写「在哪个动作前发现弹窗」"
                "（便于定位）—— 留空则用默认措辞。",
            ),
        ],
        evidence=(
            "★ **每个动作之前调用**：发现弹窗就**抛**，不让它吃掉后续输入 ✓ ★★ 本仓的死因里，「弹窗把 COM 调用冻住」是"
            "头号 ⇒ ★ 这条断言就是那个前置闸 ✓ ★ 官方依据：**本仓自研**（`scripts/sw_gui_modal.py`）⇒ 真源是源码 ✓"
        ),
        doc="★ **每个动作之前调用**：发现弹窗就**抛**，不让它吃掉后续输入 ✓ "
        "★★ 本仓的死因里，「弹窗把 COM 调用冻住」是头号 ⇒ ★ 这条断言就是那个前置闸 ✓ "
        "★ 官方依据：**本仓自研**（`scripts/sw_gui_modal.py`）⇒ 真源是源码 ✓",
    ),
    ToolSpec(
        name="solidworks_gui_close_modals",
        title="Dismiss All Modals (two-stage: PostMessage, then real input)",
        module="sw_gui_modal",
        function="close_modals",
        inject="",
        params=[
            Param("main_hwnd", int, default=0, description=_HWND),
            Param(
                "rounds",
                int,
                default=1,
                description="最多循环几**轮**（★ 计数，不是长度）—— "
                "每轮「扫 → 点 → 验窗口是否真消失」✓",
            ),
        ],
        evidence=(
            "关掉所有模态框并**回读**，返回关掉几个 ✓ ★★ 本仓的两段式处置：先 `PostMessage`（快）⇒ **验窗口是否真消失**"
            " ⇒ 没消失才上**真实输入事件**；★ 因为 `hung=True` 的窗口**消息永远不被取出**，只有真输入事件有效 ✓ ★ 官方"
            "依据：**本仓自研**（`scripts/sw_gui_modal.py`）⇒ 真源是源码 ✓"
        ),
        doc="关掉所有模态框并**回读**，返回关掉几个 ✓ ★★ 本仓的两段式处置："
        "先 `PostMessage`（快）⇒ **验窗口是否真消失** ⇒ 没消失才上**真实输入事件**；"
        "★ 因为 `hung=True` 的窗口**消息永远不被取出**，只有真输入事件有效 ✓ "
        "★ 官方依据：**本仓自研**（`scripts/sw_gui_modal.py`）⇒ 真源是源码 ✓",
    ),
    #: ★★★ 2026-10-10 **倒角几何三个工具已移除**（★ 业主架构指令）：
    #:   ★ 业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
    #:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**」✓
    #:   ★★ **判据**：★ 「**那个数字错了，回读能不能查出来**」——
    #:     ★ 它们是**倒角切除体积公式**（★ `V = …` 几何闭式解）⇒
    #:     ★★ **公式错了，回读几何查不出来**（★ 倒角看起来照样"倒上了"）⇒ ★ **是方法** ✗
    #: ★ 已移出：★ `scripts/sw_chamfer_geometry.py` → `archive/inherited-methods/scripts
    #: /` ✓
    #:   ★★ 移出的三个工具：★ `solidworks_chamfer_straight_edge_volume` ·
    #:     `solidworks_chamfer_circular_rim_volume` · `solidworks_chamfer_volume_report`
    #:   ⚠ **本批其余都是工具**（★ GUI 护栏 / 焦点 / 曲面运行期查询）⇒ ★ **全部保留** ✓
    # ── ③ 焦点（3）—— ★ 与既有 `solidworks_gui_get_foreground_window` 同族的不同面 ────
    # ─────
    ToolSpec(
        name="solidworks_gui_focus_state",
        title="Read the Current Focus State",
        module="sw_gui_focus",
        function="focus_state",
        inject="",
        params=[
            Param(
                "want",
                int,
                description="期望处于前台的窗口句柄（★ 句柄，不是坐标）。"
                "★ 先用 `solidworks_gui_get_foreground_window` 取。",
            )
        ],
        evidence=(
            "读当前焦点状态（★ 期望窗口是否真的在前台）✓ ★ 官方依据：**本仓自研**（`scripts/sw_gui_focus.py`，pywin32 `"
            "GetForegroundWindow`）⇒ 真源是源码 ✓ ★ 本仓的焦点三规则之一：**每次动作前断言前台窗口**，不是就修复 ✓"
        ),
        doc="读当前焦点状态（★ 期望窗口是否真的在前台）✓ "
        "★ 官方依据：**本仓自研**（`scripts/sw_gui_focus.py`，pywin32 `GetForegroundWindow`）"
        "⇒ 真源是源码 ✓ ★ 本仓的焦点三规则之一：**每次动作前断言前台窗口**，不是就修复 ✓",
    ),
    ToolSpec(
        name="solidworks_gui_ensure_focus",
        title="Bring a Window to the Foreground and Verify It",
        module="sw_gui_focus",
        function="ensure_focus",
        inject="",
        #: ★ 规则 2 的合法改名：源形参叫 `settle`（**秒**），按本仓"时长带 `_seconds`"的
        #: 口径改名
        #: ⇒ ★ 必须配 `param_alias` 指回真形参名（★ 不配 ⇒ `check_param_binding` 当场抓
        #: 到）✓
        param_alias={"settle_seconds": "settle"},
        params=[
            Param("hwnd", int, description="要置前的窗口句柄（★ 句柄，不是坐标）。"),
            Param("retries", int, default=5, description="重试次数（★ 计数）。"),
            Param(
                "settle_seconds",
                float,
                default=0.2,
                description="每次尝试之间等多少**秒**（★ 时长 ⇒ 用 `_seconds`，不是 `_mm`）。",
            ),
        ],
        evidence=(
            "把 `hwnd` 置为前台并**回读确认**，返回**是否真的成功** ✓（★ 判据是回读，不是调用返回）★ 官方依据：**本仓自"
            "研**（`scripts/sw_gui_focus.py`）⇒ 真源是源码 ✓"
        ),
        doc="把 `hwnd` 置为前台并**回读确认**，返回**是否真的成功** ✓（★ 判据是回读，不是调用返回）"
        "★ 官方依据：**本仓自研**（`scripts/sw_gui_focus.py`）⇒ 真源是源码 ✓",
    ),
    ToolSpec(
        name="solidworks_gui_assert_focus",
        title="Assert (and Repair) Focus Before an Action",
        module="sw_gui_focus",
        function="assert_focus",
        inject="",
        params=[
            Param(
                "hwnd", int, description="应当处于前台的窗口句柄（★ 句柄，不是坐标）。"
            ),
            Param(
                "where",
                str,
                default="",
                description="出错信息里写「在哪个动作前发现焦点不对」。",
            ),
        ],
        evidence=(
            "★ **每个动作之前调用**：焦点不对就**修复**，**修不好就抛** ✓ ★ 官方依据：**本仓自研**（`scripts/sw_gui_foc"
            "us.py`）⇒ 真源是源码 ✓"
        ),
        doc="★ **每个动作之前调用**：焦点不对就**修复**，**修不好就抛** ✓ "
        "★ 官方依据：**本仓自研**（`scripts/sw_gui_focus.py`）⇒ 真源是源码 ✓",
    ),
    # ── ④ 曲面运行时（1）—— ★ 只读前置检查 ────────────────────────────────────────────
    # ─
    ToolSpec(
        name="solidworks_surface_runtime_available",
        title="Is This IModeler Surface Method Usable on This Machine?",
        module="sw_surface",
        function="runtime_available",
        inject="",
        params=[
            Param(
                "method",
                str,
                description="成员名（如 `CreateCylindricalSurface` / `…2`）。",
            )
        ],
        evidence=(
            "★ 查某方法在**本机实测**里是否可取（`True` = 可取；**未实测的返回 `False`**）✓ ★★ 为什么它重要：`IModeler."
            "Create*Surface` 那一族**返回值不可靠**（事实 40：**同一个调用跨次也会变**）⇒ ★ 本仓把实测结果做成表，而 `_"
            "invoke` 对 `None` **抛带原因的 `RuntimeError`** ✓ ★ 官方依据：**本仓自研**（读自己的 `IMODELER_RUNTIME_*` "
            "实测表）⇒ 真源是源码；⚠ **未在本机实测本工具**（铁律 2）✓"
        ),
        doc="★ 查某方法在**本机实测**里是否可取（`True` = 可取；**未实测的返回 `False`**）✓ "
        "★★ 为什么它重要：`IModeler.Create*Surface` 那一族**返回值不可靠**"
        "（事实 40：**同一个调用跨次也会变**）⇒ ★ 本仓把实测结果做成表，"
        "而 `_invoke` 对 `None` **抛带原因的 `RuntimeError`** ✓ "
        "★ 官方依据：**本仓自研**（读自己的 `IMODELER_RUNTIME_*` 实测表）⇒ 真源是源码；"
        "⚠ **未在本机实测本工具**（铁律 2）✓",
    ),
]
