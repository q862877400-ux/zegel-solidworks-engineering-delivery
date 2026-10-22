"""
SolidWorks 连接工具
提供连接到 SolidWorks 实例的各种方法
"""
import glob
import os
import tempfile
import time
from pathlib import Path

try:
    from .sw_preflight import ensure_solidworks_installed, import_com_dependencies
except ImportError:
    from sw_preflight import ensure_solidworks_installed, import_com_dependencies

pythoncom, win32com_client, VARIANT = import_com_dependencies()


DOC_TYPE_MAP = {
    "part": 1,
    "prt": 1,
    "sldprt": 1,
    "assembly": 2,
    "asm": 2,
    "sldasm": 2,
    "drawing": 3,
    "drw": 3,
    "slddrw": 3,
}

DOC_TYPE_LABELS = {
    "part": "零件",
    "assembly": "装配体",
    "drawing": "工程图",
}

DEFAULT_TEMPLATE_PREFS = {
    "part": 8,       # swUserPreferenceStringValue_e.swDefaultTemplatePart
    "assembly": 9,   # swUserPreferenceStringValue_e.swDefaultTemplateAssembly
    "drawing": 10,   # swUserPreferenceStringValue_e.swDefaultTemplateDrawing
}

SW_ALWAYS_USE_DEFAULT_TEMPLATES = 111


class SolidWorksConnectionError(RuntimeError):
    """带阶段和错误码的 SolidWorks 连接错误。"""

    def __init__(self, code, stage, message):
        self.code = code
        self.stage = stage
        super().__init__(f"[{code}] {stage}: {message}")


class _LaunchGuard:
    """跨进程启动互斥；Windows 使用命名 Mutex，其它平台使用独占锁文件。"""

    def __init__(self, name="CADStudio.SolidWorks.Launch"):
        self.name = name
        self.handle = None
        self.path = Path(tempfile.gettempdir()) / "cad-studio-solidworks-launch.lock"
        self._owns_file = False

    def __enter__(self):
        if os.name == "nt":
            import ctypes

            kernel32 = ctypes.windll.kernel32
            self.handle = kernel32.CreateMutexW(None, False, self.name)
            if not self.handle:
                raise SolidWorksConnectionError("SW_MUTEX", "locking", "无法创建 SolidWorks 启动互斥锁")
            wait_result = kernel32.WaitForSingleObject(self.handle, 15000)
            if wait_result not in (0, 0x80):
                kernel32.CloseHandle(self.handle)
                self.handle = None
                raise SolidWorksConnectionError("SW_MUTEX_TIMEOUT", "locking", "等待其它启动任务超时")
            return self

        try:
            fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("ascii"))
            os.close(fd)
            self._owns_file = True
        except FileExistsError as exc:
            try:
                stale_pid = int(self.path.read_text(encoding="ascii").strip())
                os.kill(stale_pid, 0)
            except (ProcessLookupError, ValueError):
                self.path.unlink(missing_ok=True)
                return self.__enter__()
            raise SolidWorksConnectionError("SW_MUTEX_BUSY", "locking", "已有 SolidWorks 启动任务") from exc
        return self

    def __exit__(self, *_):
        if os.name == "nt" and self.handle:
            import ctypes

            ctypes.windll.kernel32.ReleaseMutex(self.handle)
            ctypes.windll.kernel32.CloseHandle(self.handle)
            self.handle = None
        elif self._owns_file:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass
            self._owns_file = False


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游 `wzyn20051216/solidworks-automation-skill` 的写法**发展而
# 来）。
# 文件:   scripts/sw_connect.py —— 「成员读取」这一段（`get_com_member` / `safe_get_com_
# member`）。
# 定位:   2026-10-01（轮 143）**改了一处**：把 `DISP_E_PARAMNOTOPTIONAL`（`0x8002000F`）
#         纳入「**返回成员、不调用**」的白名单。
#         ★★ 起因：`get_com_member` 在**没有实参**时会「先试调一次」来分辨属性与方法
#         ⇒ **对 COM 成员，「取」就等于「调」** ⇒ 有副作用的成员会被静默执行
#         （详见已知事实 84；实测 `tools/diag_insert_dome.py`）。
#         ⚠ 本轮**没有**改成「永不调用」—— 那会动到全仓库依赖的既有语义。
# 官方签名依据: 本段本身不调具体接口；它服务于 `IModelDocExtension::SelectByID2` /
#         `IModelDoc2::InsertDome` 之类的调用点，那些调用的签名依据在各自模块的来源块里。
# 许可:   上游 MIT（见 `THIRD-PARTY-NOTICES.md` §一.1）。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块涵盖这一段（`get_com_member` / `safe_get_com_member`）。
# ─────────────────────────────────────────────────────────────────────

#: ══ ★★ 阶段 1 · C6：COM 写调用计数器（★ SC-009 的唯一判据来源）══════════
#: ★ 为什么在这里：`get_com_member` 是**全仓唯一的 COM 取/调入口**（471 个调用点）
#:   ⇒ 它是**唯一**能在边界上数清「写了几次」的位置 ✓
#: ★ 判据用**成员动词**（与 `scripts/engineering/effects.py` 同族口径）
#:   ⇒ 只读路径（`Get*`/`Is*`/`Has*`）**不计数** ✓
#: ⚠ **未 arm 时是空操作** ⇒ 对既有行为**零影响**（无性能与语义代价）。
_WRITE_VERB = (
    "Insert", "Create", "Add", "Set", "Delete", "Remove", "Modify", "Edit",
    "Clear", "Save", "Close", "Open", "Export", "Import", "Rebuild", "Force",
    "Update", "Replace", "Move", "Copy", "Scale", "Mirror", "Pattern",
    "Extrude", "Revolve", "Fillet", "Chamfer", "Shell", "Draft", "Thicken",
    "Sketch", "Select", "Unselect", "Activate", "Exit", "Run", "Load",
    #: ★★ 实测补（2026-10-11）：`FeatureExtrusion3` / `FeatureCut4` /
    #:   `FeatureRevolve2` / `FeatureCircularPattern4` 都是**建特征**的写调用，
    #:   而它们以 **`Feature`** 开头 ⇒ 漏了它会把最核心的建模调用**记成只读**
    #:   （★ 实测踩过：`_bump_if_write('FeatureExtrusion3')` 当时没记上）。
    "Feature",
)
_READ_VERB = ("Get", "Is", "Has", "Read", "List", "Count", "Find", "Query",
              "Collect", "Inspect", "Check", "Measure", "Evaluate", "Test", "Describe")


def _bump_if_write(attr_name: str) -> None:
    """★ 若成员名**像写**，给 `COUNTER` 记一笔（★ 只读不记）。

    ⚠ 计数器从 `scripts/engineering/executor.py` 取（★ **不 import** ——
      避免 `sw_connect` → `engineering` 的循环依赖；用**注册式**注入）。
    """
    fn = globals().get("_COM_WRITE_HOOK")
    if fn is None:
        return
    if attr_name.startswith(_READ_VERB):
        return
    if attr_name.startswith(_WRITE_VERB):
        try:
            fn(attr_name)
        except Exception:      # noqa: BLE001
            pass               #: ★ 计数失败**不得**影响 COM 调用


def set_com_write_hook(fn) -> None:
    """★ 注入写调用钩子（★ 由 `scripts/engineering/executor.py` 调）。"""
    globals()["_COM_WRITE_HOOK"] = fn


def get_com_member(obj, attr_name, *args):
    """★ 「**取或调**」—— 这是本函数的**真实语义**，2026-10-01（轮 144）写明白。

    :param obj: COM 对象
    :param attr_name: 成员名称
    :param args: 有实参 ⇒ 一定**调用**；无实参 ⇒ **见下**
    :returns: 成员值，或**调用的结果**

    ⚠⚠ **无实参时的行为（重要）**：本函数会**先无参调一次**，
    成功了就返回**调用的结果**；失败了（不是"找不到成员"）才把**成员本身**返回。
    ⇒ ★★ **对 COM 成员，「取」可能等于「调」。**

    ★ **审计结论（轮 144，`tools/audit_get_com_member_semantics.py`）**：
    这个"双用"**不是缺陷，是被依赖的特性** —— 全仓库**471** 个无实参调用点里，
    很多**正是靠它去执行**的（例：`get_com_member(study, "RunAnalysis")` 拿返回码、
    `get_com_member(view, "Activate")` 就是要激活视图、
    `get_com_member(fm, "InsertMoldShutOffSurface")` 就是要建面）。
    ⇒ ⚠ 所以**没有**把它改成"永不调用"。

    ⚠ **但仍然危险**，危险在于**名字读不出来它在调**：
    ```
    471 个无实参调用点
      ├─ 193 处的成员在反射里**有零参重载** ⇒ 探测调用**会成功执行**
      │    ├─ 其中绝大多数是**只读 getter**（GetTitle / GetPoints / IsCylinder…）
      │    │   ⇒ 「取即调」正是想要的 ✓
      │    └─ 24 处名字**像「改东西」**（Insert* / Run* / Mesh* / Scale / Update*…）
      │        ⇒ ⚠ 这些是**要人工确认"作者是不是故意的"**的
      └─ 其余：成员的必填参数 ⇒ 探测调用失败 ⇒ **返回成员本身**（轮 143 的修复覆盖这里）
    ```
    ⇒ ★ **要"只取不调"时，用 `get_com_member_raw`**（本模块下一个函数）。
    """
    member = getattr(obj, attr_name)
    if args:
        #: ★★★ 2026-10-03（轮 493）**让这一类失败可见**（★ 而**不改**既有语义）——
        #:
        #: ⚠ 原来这里直接 `member(*args)`，**不检查它是不是可调用的**。
        #:   而 pywin32 迟到绑定下，`getattr` **可能回一个不是方法的元组** ——
        #:   此时报的是 **`TypeError: 'tuple' object is not callable`**，
        #:   ★★ **那个错误完全看不出是「后端限制」**（★ 会被误当成"参数没传对"）。
        #:
        #: ★ 真机实证（轮 492）：`IModelDocExtension.InsertChainDimensions`
        #:   —— 官方 `kind: method`、`System.object …(System.object Entities)`，
        #:   而 `type(getattr(ext, "InsertChainDimensions"))` = **`tuple`**、
        #:   `callable(...)` = **`False`**、`repr(...)` = **`(None, None, None)`**、
        #:   且 `dir(ext)` 里**没有该名字** ⇒ ★ **pywin32 这层给不出可调用的包装**。
        #:
        #: ★ 与**事实 28**（「反射里有」≠「运行期调用得到」）**同族**，
        #:   已记成**事实 386**。★ 而本仓**事实 40** 的定则在此适用：
        #:   「★ **修的只能是「让失败可见」**」—— 故这里**只加一个守卫**，
        #:   ★ **不改**"该返回就返回"的既有语义（★ 无实参那条路 L172 早就检查了）。
        if not callable(member):
            raise TypeError(
                "get_com_member(%s, %r, *%d args)：取回来的成员**不可调用**"
                "（`getattr` 回了 `%s`，★ 而它通常是 `(None, None, None)`）—— "
                "★ 这**多半是 pywin32 迟到绑定造不出该方法的调用包装**，"
                "★ **不是参数没传对**（★ 事实 28 / 386）。"
                "★ 官方签名里该成员可能是存在的（`kind: method`）⇒ "
                "★ 请查 `type(getattr(obj, %r))` 与 `callable(...)`，不要改参数重试。"
                % (type(obj).__name__, attr_name, len(args), type(member).__name__, attr_name))
        #: ★★ 阶段 1 · C6（2026-10-11）：**在 COM 边界上数写调用** ——
        #:   ★ 这是 SC-009「负例的 COM 写调用数必须为 0」的**唯一判据来源**
        #:   （★ 事实 8：返回值不可信 ⇒ 判「写没写」只能**在边界计数**）。
        #:   ★ 判据用**成员动词**（与 `scripts/engineering/effects.py` 同族口径）
        #:     ⇒ **只读路径不计数**（否则负例会因「读了一下」误报）。
        #:   ⚠ 计数器**未 arm 时是空操作** ⇒ 对既有行为**零影响**。
        _bump_if_write(attr_name)
        return member(*args)
    # ⚠⚠⚠ **2026-10-01（轮 143）发现本函数的一个危险设计**：
    #   下面那句"没有实参就先调一次" —— 对**有副作用**的 COM 成员，
    #   **"取"就等于"调"**！
    #   实证：`get_com_member(doc, "InsertDome")` **自己抛了**
    #   `0x8002000F`（`DISP_E_PARAMNOTOPTIONAL`，因为 `InsertDome` 有 3 个必填参数）
    #   ⇒ 说明它**真的把 `InsertDome` 调了一次**。
    #   ⇒ ★ 危险在于：**无必填参数**且有副作用的方法（如 `InsertDeleteHole()`、
    #     任何 `File*` 写盘方法）会**被"取"这个动作静默执行**。
    #   ⚠ 本函数的白名单原本只认 `找不到成员`（`0x80020005`/`-2147352573`），
    #     所以 `DISP_E_PARAMNOTOPTIONAL` **会抛出去** —— 那让"取不到"与"取到了但参数不够"
    #     看起来一样。
    #   ★ 本轮的最小修法：把 `DISP_E_PARAMNOTOPTIONAL` 也纳入"**返回成员、不调用**"。
    #     （不改成"永不调用"—— 那会动到全仓库依赖的既有语义。）
    try:
        return member() if callable(member) else member
    except Exception as exc:
        message = str(exc)
        if ("-2147352573" in message or "找不到成员" in message or "Member not found" in message
                #: `DISP_E_PARAMNOTOPTIONAL` —— 说明"它是个**需要实参的方法**"，
                #: 而不是"读不到这个成员"。
                or "-2147352561" in message or "非选择性的参数" in message
                or "Parameter not optional" in message):
            return member
        raise


#: dispatch-guard: covered-wrappers
def call_com_member(obj, attr_name, *args):
    """★ 「**就是去调它**」—— 与 `get_com_member` **行为完全相同**，差别在**名字**。

    :returns: **调用的结果**（会把成员调一次）。

    ⚠ **为什么要单独一个名字**（2026-10-01 轮 145）：审计 24 处「会改东西的零参调用」
    时发现，**作者全部是故意的**（拿返回值当成败 / 要的就是那个动作）——
    但**代码里读不出来**：`get_com_member(study, "RunAnalysis")` 看不出它会**跑求解**。
    ⇒ ★ 在**故意要调**的地方用本函数，**名字即意图**，读代码的人不必再去查语义。

    ⚠ 只在**确实要调用**时用它；**要"只取不调"用 `get_com_member_raw`**；
    两者都拿不准时用 `get_com_member`（语义是"取或调"，**名字不表态**）。
    """
    return get_com_member(obj, attr_name, *args)


#: 官方 `swProcessType_e` 之类与「模态框」相关的常量**没有官方枚举** ⇒ 本模块只用两个
#: **Win32 公开常量**（不是魔法数）：
_WM_COMMAND = 0x0111        #: Win32 `WM_COMMAND`
_IDOK = 1                   #: Win32 标准「确定 / OK」按钮的命令 ID
_DIALOG_CLASS = "#32770"    #: Win32 **预定义对话框类**（官方常量 `WC_DIALOG`）


def solidworks_process_id(sw):
    """★ **从 COM 拿 SolidWorks 的进程 ID**（官方 `ISldWorks.GetProcessID()`）。

    ⚠⚠⚠ **为什么要有这个函数**（2026-10-01 轮 167）：此前**37 处**工具里**写死**
    `SW_PID = 20456` —— 那是**硬编码**：换机器、换会话、SolidWorks 重启后**全部失效**，
    而失效的表现是「**查不到残留模态框**」⇒ **一个静默失效的安全检查**。
    ★ 官方的 `ISldWorks.GetProcessID()` 直接给出真值 ⇒ **零硬编码**。
    （另有 `GetHWnd64()` / `get_HWnd()` 可取窗口句柄，本模块用不到。）
    """
    return int(call_com_member(sw, "GetProcessID"))


def _resolve_pid(target=None):
    """把 `target` 解析成 PID —— **三种来源，全部零硬编码**。

    * `ISldWorks` 对象 ⇒ `solidworks_process_id(sw)`（官方 `GetProcessID()`）
    * `int` ⇒ 直接用（**调用方明确给了就用它**，不覆盖）
    * `None`（**默认**）⇒ ★ **本函数自己连上正在运行的 SolidWorks 再派生**
      ⇒ 这样调用方**不必**知道 PID，也**不必**先拿到 `sw`：
      `residual_dialogs()` / `dismiss_residual_dialogs()` 无参调用即可。

    ⚠⚠⚠ **为什么要有 `None` 这条**（2026-10-01 轮 167）：此前 **36 处**工具里写死
    `SW_PID = 20456` 再传给 `residual_dialogs()` —— **硬编码**，
    换机器 / 换会话 / SolidWorks 重启后**全部失效**，而失效的表现是
    「**查不到残留模态框**」⇒ **一个静默失效的安全检查**（比没有更糟）。
    """
    if target is None:
        import win32com.client
        #: ⚠ 用 `call_com_member` 而**不是**直接 `.GetProcessID()` —— pywin32 迟到绑定下
        #: 成员**有时解析成属性、有时解析成方法**（轮 167 实测：直接
        #: `(...).GetProcessID()` 报 `TypeError: 'int' object is not callable`，
        #: 因为它已被求值成 int）。★ 这正是 `call_com_member` 存在的理由。
        return int(call_com_member(
            win32com.client.GetActiveObject("SldWorks.Application"), "GetProcessID"))
    if isinstance(target, int):
        return target
    return solidworks_process_id(target)


def _dialog_handles(pid, *, only_visible=False):
    """枚举某 PID 的顶层窗口里 class 为 `#32770` 的那些（**Win32 `WC_DIALOG`**）。"""
    import ctypes
    import ctypes.wintypes as _w
    u = ctypes.windll.user32
    out: list = []
    total = [0]

    @ctypes.WINFUNCTYPE(ctypes.c_bool, _w.HWND, _w.LPARAM)
    def cb(h, _l):      # noqa: ANN001
        p = _w.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value != pid:
            return True
        if only_visible and not u.IsWindowVisible(h):
            return True
        total[0] += 1
        cls = ctypes.create_unicode_buffer(128)
        u.GetClassNameW(h, cls, 128)
        if cls.value == _DIALOG_CLASS:
            out.append(h)
        return True

    u.EnumWindows(cb, 0)
    return out, total[0]


def count_residual_dialogs(target=None, *, settle_seconds=0.0, poll_ms=200):
    """★ **只读**检测残留模态框（**不点掉任何东西**）。

    ⚠ 与 `dismiss_residual_dialogs` 分开，是为了让调用方能**分别报告**
    「**发现**了几个」与「**点掉**了几个」—— 2026-10-01（轮 167）实测时把两者混在一个
    计数里，读日志时误判成「没点掉」。**发现与处置是两件事，计数也要分开。**
    """
    import time
    pid = _resolve_pid(target)
    best_n = 0
    #: ⚠ `scanned` **每一轮都更新**（不是只在发现对话框时）—— 否则"没发现"会报成
    #: "**扫了 0 个窗口**"，读日志时无法区分「没弹框」与「根本没扫到」（事实 62/79/81 同
    #: 族）。
    scanned = 0
    deadline = time.time() + max(0.0, float(settle_seconds))
    while True:
        handles, total = _dialog_handles(pid)
        scanned = max(scanned, total)
        best_n = max(best_n, len(handles))
        if time.time() >= deadline:
            break
        time.sleep(max(0.02, poll_ms / 1000.0))
    return best_n, scanned


def dismiss_residual_dialogs(target=None, *, settle_seconds=0.0, poll_ms=200):
    """★ 把残留的**模态对话框**点掉 —— **不认按钮文本、不依赖可见性、零硬编码**。

    :param target: `ISldWorks`（**自动派生 PID**）或 `int` PID。
    :param settle_seconds: 在返回前**轮询**多久（⚠ **弹窗是异步弹出的**，见下）。
    :param poll_ms: 轮询间隔毫秒。
    :returns: `(dismissed, scanned)` —— 点掉了几个 / 扫到多少个顶层窗口。

    ⚠⚠⚠ **为什么要轮询**（2026-10-01 轮 167 的根因之一）：模态框**不是**在发调用的那一刻
    弹出来的 —— COM 调用返回后它**才**出现。原先各工具在收尾处**只查一次**
    ⇒ **查得太早** ⇒ 报「无残留」而屏幕上明明有一个（★ 那次会话就是这样**卡住的**）。

    ★ **怎么点掉**：给对话框发 `WM_COMMAND` + `IDOK`（Win32 标准命令）——
    **不看按钮叫什么、不按坐标** ⇒ 中英文界面、任何按钮布局都适用（用户明确要求**禁止硬编码**）。
    """
    import ctypes
    import time
    pid = _resolve_pid(target)
    dismissed = 0
    scanned = 0
    deadline = time.time() + max(0.0, float(settle_seconds))
    while True:
        handles, total = _dialog_handles(pid)
        scanned = total
        for h in handles:
            ctypes.windll.user32.PostMessageW(h, _WM_COMMAND, _IDOK, 0)
            dismissed += 1
        if time.time() >= deadline:
            break
        time.sleep(max(0.02, poll_ms / 1000.0))
    return dismissed, scanned


def settle_residual_dialogs(target=None, *, settle_seconds=1.0, poll_ms=200):
    """★★★ **收尾专用**：轮询查残留模态框，**发现就点掉**，并把三件事分开报。

    :returns: `(found, dismissed, scanned)` —— **发现几个 / 点掉几个 / 扫过多少窗口**。

    ⚠⚠⚠ **为什么需要它**（2026-10-01 轮 169 的审计发现）：
    仓库里 **35 个脚本**都会"查残留模态框"，而其中 **34 个只查、不点掉** ——
    它们**打印一行**就继续 ⇒ ★ **若真的发现了弹窗，弹窗还在**，
    于是**下一轮（或同一轮的后续调用）就挂在那儿**（这正是轮 167 用户看到的情形）。
    ⇒ ★★ **"发现"和"处置"是两件事**：
    * `residual_dialogs()`  —— **只读**（可证伪性、测试用），**默认不点掉**；
    * `count_residual_dialogs()` —— **只读**且只报计数；
    * `settle_residual_dialogs()` —— ★ **收尾用：查 + 点掉**（本函数）；
    * `dismiss_residual_dialogs()` —— 只点掉，不报发现数。

    ★ 点掉的方式与其它函数一致：**`WM_COMMAND` + `IDOK`**（Win32 标准命令）——
    **不看按钮文本、不按坐标**。
    """
    found = 0
    dismissed = 0
    scanned = 0
    import time
    pid = _resolve_pid(target)
    deadline = time.time() + max(0.0, float(settle_seconds))
    while True:
        handles, total = _dialog_handles(pid)
        scanned = max(scanned, total)
        found = max(found, len(handles))
        for h in handles:
            import ctypes
            ctypes.windll.user32.PostMessageW(h, _WM_COMMAND, _IDOK, 0)
            dismissed += 1
        if time.time() >= deadline:
            break
        time.sleep(max(0.02, poll_ms / 1000.0))
    return found, dismissed, scanned


def residual_dialogs(pid=None, *, only_visible=False, settle_seconds=1.0, poll_ms=200):
    """★★ 数某个进程的**残留模态框**（Win32 类名 `#32770`）—— **可证伪**版。

    :param pid: 目标进程 ID；**默认 `None` ⇒ 自己从 COM 派生**（`ISldWorks.GetProcessID()`，
        **不必硬编码 `20456`**）。
    :param only_visible: ⚠⚠ **默认 `False`** —— 见下。
    :param settle_seconds: ★★ **默认 `1.0` 秒 —— 会**轮询**，不是查一次**
        （2026-10-01 轮 167 实测：模态框**第 0.86 秒**才出现 ⇒ 一次性检查**会漏**，
        而那次漏检让一次会话谎报「无残留」并**永久挂起**）。
        ⚠ 需要"只看此刻一眼"时显式传 `settle_seconds=0.0`。
    :param poll_ms: 轮询间隔毫秒。
    :returns: `(dialogs, all_windows)`：前者是 `#32770` 的标题列表，
        后者是**扫到的全部顶层窗口数**（用于判断这次扫描**有没有真的扫到东西**）。

    ⚠⚠⚠ **为什么要返回 `all_windows`**（2026-10-01 轮 148 查出的一个真问题）：
    此前本仓库在 **21 个工具**里各复制了一份"查残留模态框"的代码，
    **每份都带 `IsWindowVisible(h)` 过滤**。而本轮实测：
    ```
    PID 20456 的顶层窗口 **49 个，全部 IsWindowVisible == 0**（SolidWorks 主框架不可见）
    ⇒ 那个过滤让**枚举结果恒为空** ⇒ 检查**永远报「无残留」** ⇒ **一个不可能失败的门禁**
    ```
    ⇒ ★ 所以本函数**默认不过滤可见性**，并**把 `all_windows` 一并返回** ——
    调用方应当**先看 `all_windows > 0`** 再相信 `dialogs` 为空（否则是"没扫到"，不是"没有"）。

    ⚠ 这与已知事实 62/79/81 同族（**"绿"不等于"对"**），但更严重：
    它守的是**每轮收尾的安全底线**（模态框会把会话永久挂起）。
    """
    import ctypes
    import ctypes.wintypes as _w
    import time
    pid = _resolve_pid(pid)          #: ★ `None` ⇒ 自己从 COM 派生（零硬编码）
    u = ctypes.windll.user32

    def one_pass():
        dialogs: list = []
        total = [0]

        @ctypes.WINFUNCTYPE(ctypes.c_bool, _w.HWND, _w.LPARAM)
        def cb(h, _l):      # noqa: ANN001
            p = _w.DWORD()
            u.GetWindowThreadProcessId(h, ctypes.byref(p))
            if p.value != pid:
                return True
            if only_visible and not u.IsWindowVisible(h):
                return True
            total[0] += 1
            cls = ctypes.create_unicode_buffer(128)
            u.GetClassNameW(h, cls, 128)
            if cls.value == "#32770":
                txt = ctypes.create_unicode_buffer(256)
                u.GetWindowTextW(h, txt, 256)
                dialogs.append(txt.value)
            return True

        u.EnumWindows(cb, 0)
        return dialogs, total[0]

    #: ★★ **轮询**：模态框是**异步**弹出的（实测第 0.86 秒才出现）⇒
    #: 查一次**会漏**，而漏检的后果是「谎报无残留」+ 会话挂起。
    #: 取**整个窗口期内见过的最大值**（弹窗可能已被别人点掉，但"**弹过**"这个事实更重要
    #: ）。
    best: list = []
    scanned = 0
    deadline = time.time() + max(0.0, float(settle_seconds))
    while True:
        got, total = one_pass()
        scanned = max(scanned, total)
        if len(got) > len(best):
            best = got
        if time.time() >= deadline:
            break
        time.sleep(max(0.02, poll_ms / 1000.0))
    return best, scanned


def get_com_member_raw(obj, attr_name):
    """★ 「**只取不调**」—— `get_com_member` 的安全替代（2026-10-01 轮 144 加）。

    :returns: **成员本身**（方法对象或属性值），**绝不调用它**。

    ⚠ **什么时候必须用它**：当你要的是**方法对象**（例如要传给别处、或要自己控制
    参数与时机），而**不是**它的返回值时 —— 用 `get_com_member` 会**先无参调一次**，
    那对**有副作用**的成员（`Insert*` / `Run*` / `Save*` / `Scale`…）是**真做了那件事**。
    ⚠ 反过来：**要执行**的时候，继续用 `get_com_member`（那是它的语义）。
    """
    return getattr(obj, attr_name)

#: dispatch-guard: covered-wrappers

def safe_get_com_member(obj, attr_name, *args):
    """
    读取 COM 成员，兼容 pywin32 中伪可调用属性。

    保留该别名便于其它模块表达“安全读取”的意图；核心逻辑统一在 get_com_member。
    """
    return get_com_member(obj, attr_name, *args)


def create_empty_dispatch_variant():
    """创建可传给 COM 接口的空 Dispatch 参数。"""
    return VARIANT(pythoncom.VT_DISPATCH, None)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本机实测结论的固化，非第三方移植）
# 文件:   scripts/sw_connect.py —— 本文件自身的 out_i4 / create_empty_dispatch_variant
# 定位:   AGENTS.md 铁律 2「本机实测」与铁律 4「冲突以出厂类型库为准」的交汇点：
#         静态反射只说得清「有几个参数、哪些是 `&` 出参」，**说不清出参在 pywin32
#         迟到绑定下该怎么传**。本块记录的是 2026-10-01 在 SolidWorks 2026 SP4.1
#         （34.4.1）上逐一试出来的唯一可用形态，实测脚本见
#         D:\AI\SW\probe_outparam_convention.py 与 D:\AI\SW\probe_dispatch_variant.py。
# 官方签名依据: ICWStudyManager.CreateNewStudy3(String, Int32, Int32, Int32&)；
#         ICWLoadsAndRestraintsManager.AddRestraint(Int32, Object, Object, Int32&)；
#         IModelDocExtension.SelectByID2(String, String, Double, Double, Double, Boolean,
#         Int32, Callout, Int32) 与 AddRenderMaterial(RenderMaterial, Int32&)。
#         反射清单：D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   从本行到本文件内 out_i4 / create_empty_dispatch_variant 两个函数结束。
# ────────────────────────────────────────────────────────────────────
def out_i4(value: int = 0):
    """创建 `Int32&` 出参的 VARIANT 包装 —— **唯一被真机验证通过的形态**。

    官方接口里大量方法以 `Int32&` 作 [out] 错误码，例如
    ``ICWStudyManager.CreateNewStudy3(String, Int32, Int32, Int32&)``。

    ⚑ 2026-10-01 在 SolidWorks 2026 SP4.1 上逐一实测，**五种形态只有一种通过**：

        VARIANT(VT_BYREF | VT_I4, 0)   ✓ 通过
        VARIANT(VT_I4, 0)              ✗ 类型不匹配（DISP_E_TYPEMISMATCH, 第 4 参）
        VARIANT(VT_BYREF | VT_VARIANT) ✗ 类型不匹配
        VARIANT(VT_EMPTY, None)        ✗ 类型不匹配
        裸 int / 裸 0                   ✗ 类型不匹配
        省略该参数                      ✗ DISP_E_PARAMNOTOPTIONAL（「非选择性的参数」）

    ⇒ **该参数必需（不能省），且必须按引用传 `VT_I4`。**

    ⚠ 这条推翻了本仓库既有做法：`scripts/sw_simulation.py` 的 `create_static_study` /
    `apply_fixed_restraint` / `apply_normal_force` 都传裸 `0`，
    **按本实测它们必然全部失败** —— 即那些函数从未真正跑通过。
    （`scripts/audit_call_arity.py` 的「`&` 出参不计入 arity」口径也不对：
    它算 arity 时排除出参是对的，但**调用方仍须传一个 byref VARIANT**。）
    """
    return VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, int(value))


def out_dispatch(value=None):
    """★ 创建 `IDispatch&`（**对象出参**）的 VARIANT 包装 —— ★ `out_i4` 的对偶。

    ★ 官方接口里另有一族方法以 **对象** 作 [out] 参数，例如
    `IHoleStandardsData.GetFastenerTable(String, Int32, Int32, **IHoleDataTable&**)`
    —— ★ 而 `out_i4()` 只解决 `Int32&`，**这一族一直没有包装** ⚠
    （★ 本仓 `docs/dead-ends.md` 里 `get_fastener_table` 那条就卡在这里。）

    ⚠★ **本函数是「照对偶推出来的」，★ 而真机验证在调用方** ——
      ★ 本仓的纪律是**不凭类推**：`out_i4` 那条是**逐形态实测**出来的
      （五种只有 `VT_BYREF|VT_I4` 通），★ 故 `IDispatch&` 这条也**必须在真机上试过才算**。
      ★ 试过之后要**回来把结论写进这里**（★ 通过 / 各形态的错误码）。

    ✅★ **2026-10-03（轮 499）真机已验证通过** —— ★ 测的是
      `IHoleStandardsData.GetFastenerTable(String, Int32, Int32, **IHoleDataTable&**)`，
      在 SolidWorks 2026 SP4.1 上**逐形态实测**，结论**与 `out_i4` 完全对偶**：

          VARIANT(VT_BYREF | VT_DISPATCH, None)   ✓ 通过（返回 `False` = "没查到该表"）
          VARIANT(VT_BYREF | VT_VARIANT, None)    ✗ 类型不匹配（第 4 参）
          VARIANT(VT_DISPATCH, None)              ✗ 类型不匹配（第 4 参）
          裸 `None`                                ✗ 类型不匹配（第 4 参）

      ⇒ ★★ **定则：`out` 参数一律「`VT_BYREF | VT_<该出参的类型>`」** ——
        ★ 而**不是** `VT_VARIANT`、★ 也**不是**省掉 `BYREF` ✓

    ★★ 顺带更正：`docs/dead-ends.md` 里 `get_fastener_table` 那条原写「**到不了**」——
      ★ 而真机证明它**能调**（★ 只是那次回了 `False`，★ 那是**参数/前置**问题、
      ★ **不是后端限制**）✓
    """
    return VARIANT(pythoncom.VT_BYREF | pythoncom.VT_DISPATCH, value)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本机实测结论的固化）
# 文件:   scripts/sw_connect.py 的 set_com_member
# 定位:   `get_com_member`（已知事实 4）的**对偶面**。事实 4 说「迟到绑定下同一成员
#         可能是属性也可能是方法，读要用 get_com_member」；2026-10-01 真机补上另一半：
#         **写必须用属性赋值（`setattr`）**。
# 官方签名依据: ICWForce 的 `set_ForceType(Int32)` / `set_Unit(Int32)` /
#         `set_NormalForceOrTorqueValue(Double)`（反射里是 `set_` 前缀）
#         ⇒ 但在 pywin32 迟到绑定下**这三个名字都取不到**，只有属性赋值可用。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ─────────────────────────────────────────────────────────────────────────
def set_com_member(obj, attr_name, value):
    """设置 COM 成员的**唯一被真机验证通过的形态**：属性赋值。

    反射里 `ICWForce` 的 ForceType / Unit / NormalForceOrTorqueValue 是 `set_` 前缀的
    方法，但 2026-10-01 真机（工作区 `probe_setter_forms.py`）逐形态实测三种写法：

    ============================================  ==========================
    写法                                            结果
    ============================================  ==========================
    以 `get_com_member(obj, "set_<名>", 值)` 调用    ✗ 该名字在迟到绑定下取不到
    以 `get_com_member(obj, "put_<名>", 值)` 调用    ✗ 同上
    ``obj.<名> = 值``（**本函数**）                   **✓ 唯一可行**
    ============================================  ==========================

    ⇒ 与已知事实 4（读用 `get_com_member`）成对：**读走 get_com_member，写走本函数。**

    .. note::
       上文刻意不写具体的 `get_com_member(...)` 调用字面量 ——
       `scripts/check_member_names.py` 会把文档里的调用字面量当成真调用去核反射，
       而那些名字**故意**是不存在的（它们就是要被否定的写法）。

    :raises AttributeError: 该成员在对象上不可写（迟到绑定下常见于只读属性）。
    """
    setattr(obj, attr_name, value)
    return value


def normalize_doc_type(doc_type):
    """
    规范化文档类型名称。

    参数:
        doc_type: "part"、"assembly"、"drawing" 或常见缩写/扩展名

    返回:
        (name, enum_value) 元组
    """
    key = str(doc_type).strip().lower().lstrip(".")
    enum_value = DOC_TYPE_MAP.get(key)
    if enum_value is None:
        raise ValueError(f"未知文档类型: {doc_type}")

    name_map = {1: "part", 2: "assembly", 3: "drawing"}
    return name_map[enum_value], enum_value


def _expand_path(file_path):
    """展开用户目录和环境变量，并返回绝对路径。"""
    return os.path.abspath(os.path.expandvars(os.path.expanduser(file_path)))


def _ensure_parent_dir(file_path):
    """确保输出文件的父目录存在。"""
    parent = os.path.dirname(_expand_path(file_path))
    if parent:
        os.makedirs(parent, exist_ok=True)


def _prog_id_for_version(version):
    """返回 SolidWorks 年份对应的 ProgID。"""
    if version is None:
        return "SldWorks.Application"
    try:
        year = int(version)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"SolidWorks 版本必须是年份，例如 2024: {version}") from exc
    if year < 2010 or year > 2035:
        raise ValueError(f"不支持的 SolidWorks 版本年份: {year}")
    return f"SldWorks.Application.{(year - 2000) + 8}"


def _read_active_document(sw):
    """读取活动文档，兼容 COM 属性/方法差异。"""
    try:
        return get_com_member(sw, "ActiveDoc")
    except Exception:
        return None


def _wait_until_ready(sw, timeout_seconds):
    """等待 COM 服务器可读，避免固定 sleep 导致 UI 假死。"""
    deadline = time.monotonic() + max(0.1, float(timeout_seconds))
    last_error = None
    while time.monotonic() < deadline:
        try:
            get_com_member(sw, "RevisionNumber")
            return
        except Exception as exc:
            last_error = exc
            time.sleep(0.1)
    raise SolidWorksConnectionError(
        "SW_START_TIMEOUT", "ready", f"SolidWorks 启动超时（{timeout_seconds:.1f}s）: {last_error or 'COM 未就绪'}"
    )


#: 我们启动过的 SolidWorks 实例的 PID 标记（跨进程、跨轮可读）。
#: 落盘位置在 output/（已 gitignore），不进版本库。
OWNED_MARKER = Path(__file__).resolve().parents[1] / "output" / ".sw-started-by-us.json"


def _record_owned_instance(sw, prog_id: str) -> None:
    """记下**我们自己启动**的实例 PID —— 回收时只认它，绝不按进程名杀。"""
    try:
        import json as _json
        import time as _time
        pid = None
        try:
            pid = int(get_com_member(sw, "GetProcessID"))
        except Exception:
            pass
        OWNED_MARKER.parent.mkdir(parents=True, exist_ok=True)
        OWNED_MARKER.write_text(_json.dumps(
            {"pid": pid, "prog_id": prog_id, "at": _time.strftime("%Y-%m-%dT%H:%M:%S")},
            ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        #: 标记写失败**不许影响连接** —— 代价只是"这次回收时证不出归属"。
        pass


def read_owned_instance() -> dict | None:
    """读归属标记；没有就回 None。"""
    try:
        import json as _json
        return _json.loads(OWNED_MARKER.read_text(encoding="utf-8"))
    except Exception:
        return None


def clear_owned_instance() -> None:
    """清掉归属标记（成功回收之后）。"""
    try:
        OWNED_MARKER.unlink()
    except Exception:
        pass


def close_owned_solidworks(sw, started_by_cad_studio):
    """只退出由当前 CAD Studio 会话启动的 SolidWorks 实例。"""
    if not started_by_cad_studio:
        return False
    for member_name in ("ExitApp", "Quit"):
        try:
            member = getattr(sw, member_name)
            member() if callable(member) else None
            return True
        except Exception:
            continue
    return False


def connect_solidworks(version=None, wait_seconds=5, visible=True, return_metadata=False):
    """
    连接到 SolidWorks 实例。

    参数:
        version: SolidWorks 版本年份（如 2024），None 则自动检测
        wait_seconds: 启动新实例后等待秒数
        visible: 启动新实例后是否显示窗口

    返回:
        (sw, model) 元组，model 可能为 None（无打开的文档时）
    """
    ensure_solidworks_installed()
    prog_id = _prog_id_for_version(version)
    sw = None
    launched_here = False

    # 启动和附着共享同一把互斥锁，避免多个 worker 同时拉起实例。
    with _LaunchGuard():
        try:
            sw = win32com_client.GetActiveObject(prog_id)
            print(f"已连接到运行中的 SolidWorks 实例（ProgID: {prog_id}）")
        except Exception as attach_error:
            try:
                sw = win32com_client.Dispatch(prog_id)
                launched_here = True
                #: 落「我们启动的实例」标记 —— 用户要求「不要误杀别的对话打开的 solidwor
                #: ks，
                #: 只关闭你自己打开的窗口」。进程内的 launched_here 传不出本进程，
                #: 所以把 PID 写进一个跨进程可读的标记文件；回收时只认这个标记。
                _record_owned_instance(sw, prog_id)
                try:
                    sw.Visible = visible
                except Exception:
                    pass
                print(f"启动了新的 SolidWorks 实例（ProgID: {prog_id}）")
                _wait_until_ready(sw, wait_seconds)
            except SolidWorksConnectionError:
                close_owned_solidworks(sw, launched_here)
                raise
            except Exception as launch_error:
                close_owned_solidworks(sw, launched_here)
                raise SolidWorksConnectionError(
                    "SW_LAUNCH_FAILED", "launch", f"无法启动 {prog_id}: {launch_error}; attach={attach_error}"
                ) from launch_error

    if sw is None:
        raise SolidWorksConnectionError("SW_NO_INSTANCE", "connect", "未获得 SolidWorks COM 实例")

    model = _read_active_document(sw)
    if model:
        doc_types = {1: "零件", 2: "装配体", 3: "工程图"}
        doc_type = get_com_member(model, "GetType")
        title = get_com_member(model, "GetTitle")
        print(f"当前文档: {title} (类型: {doc_types.get(doc_type, '未知')})")
    else:
        print("当前没有打开的文档")

    #: ★★ 2026-10-07（接手轮 · 规格 216）**补上 `revision`** ——
    #:   ★ 起因（**实测到的真缺陷**）：`tools/verify_costing_e2e.py` 写的是
    #: `str((meta or {}).get("revision", ""))`，★ 而**本字典里从来没有 `revision` 这个键
    #: ** ✗
    #: ⇒ ★★ 证据文件 `output/costing-evidence.json` 的 `solidworks_revision` **恒为空串*
    #: *
    #:     （★ 实测：该文件里逐字 `"solidworks_revision": ""`）✓
    #: ⇒ ★ 连带 `capabilities.yaml` 的 costing 条目那句「证据文件…（含时间戳与版本）」**
    #: 不成立** ✓
    #: ★ 复用既有函数：`get_sw_version(sw)`（★ 本文件里就有，回 `{"revision", "year", "m
    #: ajor"}`）✓
    #:   ⚠ **防御式**：取版本要读 COM（`ISldWorks.RevisionNumber`）——
    #:     ★ 它**失败了也不该拖垮"连接"这件正事** ⇒ 包 try/except，★ 取不到就记 `None`
    #:     （★ 与"没这个键"区分开：★ **键一定在**、值可能是 `None`）✓
    try:
        revision = get_sw_version(sw)["revision"]
    except Exception:                                                  # noqa: BLE001
        revision = None
    metadata = {
        "prog_id": prog_id,
        "requested_version": int(version) if version is not None else None,
        "started_by_cad_studio": launched_here,
        "revision": revision,
    }
    return (sw, model, metadata) if return_metadata else (sw, model)


def get_sw_version(sw):
    """获取 SolidWorks 版本信息。"""
    rev = get_com_member(sw, "RevisionNumber")
    major = int(rev.split(".")[0])
    year = major - 8 + 2000
    return {"revision": rev, "year": year, "major": major}


def find_template(sw, doc_type="part"):
    """
    自动查找 SolidWorks 文档模板。

    参数:
        sw: SolidWorks 应用对象
        doc_type: "part" | "assembly" | "drawing"

    返回:
        模板文件路径字符串
    """
    doc_type, _ = normalize_doc_type(doc_type)

    type_map = {
        "part": (sw.GetUserPreferenceStringValue(DEFAULT_TEMPLATE_PREFS["part"]), "*.prtdot"),
        "assembly": (sw.GetUserPreferenceStringValue(DEFAULT_TEMPLATE_PREFS["assembly"]), "*.asmdot"),
        "drawing": (sw.GetUserPreferenceStringValue(DEFAULT_TEMPLATE_PREFS["drawing"]), "*.drwdot"),
    }

    default_path, pattern = type_map.get(doc_type, type_map["part"])
    if default_path:
        for candidate_root in str(default_path).split(";"):
            candidate_root = _expand_path(candidate_root.strip().strip('"'))
            if not candidate_root:
                continue

            if os.path.isfile(candidate_root):
                return candidate_root

            if os.path.isdir(candidate_root):
                matches = glob.glob(os.path.join(candidate_root, pattern))
                if matches:
                    return matches[0]

    search_dirs = [
        r"C:\ProgramData\SolidWorks\SOLIDWORKS *\templates",
        r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\chinese-simplified",
        r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english",
    ]
    for search_dir in search_dirs:
        matches = glob.glob(os.path.join(os.path.expandvars(search_dir), pattern))
        if matches:
            return matches[0]

    raise FileNotFoundError(f"无法找到 {doc_type} 模板文件，请手动指定路径")


def ensure_default_templates(sw):
    """
    @brief 配置默认模板并关闭新建文件模板选择提示 —— ★★ **并把旧值记下来，供调用方还原**。
    @param sw SolidWorks 应用对象。
    @return 字典：`{"templates": {...}, "restore": [...]}`。

    ★★★ 2026-10-04（接手轮）**交付纪律修正**（★ 事实 525）：本函数改的是
      **SolidWorks 全局用户偏好**（默认模板路径 ×3 + 新建提示 ×1）——
      ★ 原文**改完永不还原** ⇒ 别人装一次我们的工具，他的设置就被永久改掉。
      ⇒ ★ 现在它**额外回一个 `restore` 列表**（每条带 `kind` / `preference` / `old`），
      ★ 调用方**必须**在 `finally` 里交给 `restore_default_templates` 还回去
      （★ 本文件 `open_document` 的 `LoadFile4` 分支就是这么用的）✓
      ⚠ ★ 本函数**自己不改回**：因为这几条偏好必须在 SolidWorks **内部创建文档**那一步
        仍然生效（★ 提前还原 = 那一步会弹"选模板"对话框而阻塞自动化）✓
    """
    templates = {}
    restore: list[dict] = []
    # preference-guard: 本函数只"设"，★ 旧值全记进 `restore` 并由 restore_default_templa
    # tes
    #   在调用方的 `finally` 里还回去（★ 事实 525 —— 见 open_document 的 LoadFile4 分支）
    for doc_type, preference in DEFAULT_TEMPLATE_PREFS.items():
        template_path = find_template(sw, doc_type)
        templates[doc_type] = template_path
        current_path = str(sw.GetUserPreferenceStringValue(preference) or "")
        restore.append({"kind": "string", "preference": preference, "old": current_path})
        if _expand_path(current_path) != _expand_path(template_path):
            sw.SetUserPreferenceStringValue(preference, template_path)
    try:
        old_toggle = sw.GetUserPreferenceToggle(SW_ALWAYS_USE_DEFAULT_TEMPLATES)
        restore.append({"kind": "toggle", "preference": SW_ALWAYS_USE_DEFAULT_TEMPLATES,
                        "old": old_toggle})
        sw.SetUserPreferenceToggle(SW_ALWAYS_USE_DEFAULT_TEMPLATES, True)
    except Exception as exc:
        print(f"提示: 无法设置始终使用默认模板: {exc}")
    return {"templates": templates, "restore": restore}


def restore_default_templates(sw, template_info):
    """★ 把 `ensure_default_templates` 改过的偏好**还回去**（★ 事实 525 · 交付纪律）。

    ★ 判据：**旧值读不到的条目不写回**（★ 免得把"读不到"变成"写了个错的旧值"）；
    ★ **写回后读一次校验**，逐条给 `match` —— ★ 不把"设了"当成"还原了" ✓
    """
    info = template_info or {}
    restored, skipped, errors = [], [], []
    # preference-guard: 本函数就是"还原那一步"（★ 写回 `ensure_default_templates` 记下的
    # 旧值 —— 事实 525）
    for item in info.get("restore") or []:
        kind, preference, old = item.get("kind"), item.get("preference"), item.get("old")
        if old is None or (kind == "string" and old == ""):
            skipped.append({"kind": kind, "preference": preference,
                            "why": "★ 旧值读不到/为空 ⇒ 不写回（免得写错）"})
            continue
        try:
            if kind == "string":
                sw.SetUserPreferenceStringValue(preference, old)
                back = str(sw.GetUserPreferenceStringValue(preference) or "")
                match = _expand_path(back) == _expand_path(old)
            else:
                sw.SetUserPreferenceToggle(preference, bool(old))
                back = sw.GetUserPreferenceToggle(preference)
                match = bool(back) == bool(old)
            restored.append({"kind": kind, "preference": preference, "old": old,
                             "readback": back, "match": match})
        except Exception as exc:                               # noqa: BLE001
            errors.append({"kind": kind, "preference": preference,
                           "error": f"{type(exc).__name__}: {str(exc)[:120]}"})
    info["restored"], info["restore_skipped"], info["restore_errors"] = restored, skipped, errors
    if errors:
        print(f"⚠ 默认模板偏好的还原有失败项 ⇒ {errors}")
    return info


def new_document(sw, doc_type="part", template_path=None):
    """
    创建新文档。

    参数:
        sw: SolidWorks 应用对象
        doc_type: "part" | "assembly" | "drawing"
        template_path: 模板路径，None 则自动查找

    返回:
        新建的 IModelDoc2 对象
    """
    doc_type, _ = normalize_doc_type(doc_type)
    if not template_path:
        template_path = find_template(sw, doc_type)
    else:
        template_path = _expand_path(template_path)

    model = sw.NewDocument(template_path, 0, 0, 0)
    if model is None:
        for _ in range(20):
            model = sw.ActiveDoc
            if model is not None:
                break
            time.sleep(0.25)

    if model is None:
        raise RuntimeError(f"创建{DOC_TYPE_LABELS.get(doc_type, doc_type)}文档失败，SolidWorks 未返回活动文档")

    print(f"已创建新{DOC_TYPE_LABELS.get(doc_type, doc_type)}文档")
    return model


# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_connect.py —— `open_document`（本函数整体）。
# 定位:   打开文档；★ 含 **2026-10-01（轮 335/337）** 两处：
#         ① **根因修复**：`options |= 512`（`swOpenDocOptions_LoadExternalReferencesInMemory`）
#            —— ★ 官方原话「Open external references in memory only」，且官方明说
#            **通过 API 打开时系统选项被忽略、只有这个选项有效** ⇒ 「打开外部参考的零件」不再弹；
#         ② **兜底收尾**：`settle_residual_dialogs` 轮询 1.5 s，发现未知弹窗就按 Win32
#            `WM_COMMAND`+`IDOK` 点掉（★ 零硬编码）—— ★ 按纪律（自我纠错 §9）它只是**兜底**，
#            用完必须补根因修复。
# 官方签名依据: `C:\swapi\enums\swOpenDocOptions_e.md`（512 = LoadExternalReferencesInMe
# mory、
#   1 = Silent、2 = ReadOnly）· `ISldWorks/OpenDoc6.md` · `IFeatureManager` 不涉及。
# 未在本机实测: 不适用 —— ★ 本函数**已真机实测**（`output/open-doc-rootfix-evidence.json
# `：
#   ★ `external_ref_left = []` ⇒ 那个对话框**根本没有出现**）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ─────────────────────────────────────────────────────────────────────────────
def open_document(sw, file_path, read_only=False, silent=False, raise_on_error=False):
    """
    打开已有文档。

    参数:
        sw: SolidWorks 应用对象
        file_path: 文件完整路径
        read_only: 是否以只读模式打开
        silent: 是否静默打开
        raise_on_error: 打开失败时是否抛出异常

    返回:
        IModelDoc2 对象
    """
    file_path = _expand_path(file_path)
    #: ★★★ **B5-3 的咽喉点**：会打开文档的调用**几乎都经过这里** ⇒ 沙盒策略就挂在这一处 
    #: ✓
    #: ★★ 评审的判决：要守的**不是**"输出不落在输入旁边"，而是「**打开的永远不是原件**」
    #: ——
    #:     ★ 出事的根因正是"对**原件路径**直接开了分析"⇒ ★ 外部路径在这里被**复制进沙盒**，
    #:     ★ 后面 `OpenDoc6` 打开的是**副本** ✓
    #:   ★ 默认 `passthrough`（不改变既有行为）；★ **护栏**会给探针设 `enforce` ✓
    try:
        import sw_sandbox as _sb
    except ImportError:                                                 # pragma: no cover
        try:
            from . import sw_sandbox as _sb
        except ImportError:
            _sb = None
    if _sb is not None:
        _resolved = _sb.resolve_input(file_path)
        if _resolved.get("materialized"):
            print("  " + _resolved["why"])
        file_path = _resolved["path"]
    if not os.path.exists(file_path):
        message = f"文件不存在: {file_path}"
        if raise_on_error:
            raise FileNotFoundError(message)
        print(message)
        return None

    # 装配体会把组件文档加载到当前会话；再次 OpenDoc6 可能返回
    # swFileWithSameTitleAlreadyOpen。复用同一路径对象也能保留文档所有权。
    try:
        existing_model = sw.GetOpenDocumentByName(file_path)
    except Exception:
        existing_model = None
    if existing_model is not None:
        print(f"已复用打开文档: {file_path}")
        return existing_model

    ext = os.path.splitext(file_path)[1].lower()
    foreign_exts = {".step", ".stp", ".igs", ".iges"}
    type_map = {".sldprt": 1, ".sldasm": 2, ".slddrw": 3}

    errors = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    warnings = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    options = 2 if read_only else 0  # swOpenDocOptions_ReadOnly = 2
    if silent:
        options |= 1  # swOpenDocOptions_Silent = 1
    #: ★★★★★ 2026-10-01（轮 335）**根因修复（★ 用户指出：光点弹窗没解决根因，点了还会再
    #: 弹）**：
    #:   ★ 现象：★ 打开**带外部参考**的工程图/装配体时，SolidWorks 每次都弹
    #:   「**打开外部参考的零件**」对话框 ⇒ ★ 机械点掉**只是把这一次糊过去**，
    #:   ★ **下一次再打开同一个文件还会弹**（★ 而某一次没人点 ⇒ 会话卡死）。
    #: ★ 根因：★ `OpenDoc6` 用的是**默认选项** ⇒ ★ SolidWorks 只能**问用户**要不要加载参
    #: 考件。
    #:   ★★ 官方开关（★ `swOpenDocOptions_e` 枚举）：
    #:     **`swOpenDocOptions_LoadExternalReferencesInMemory = 512 (0x200)`**
    #:     —— 官方原话「**Open external references in memory only**」。
    #: ★★★ **而官方还明说**：「`swExtRefLoadRefDocsInMemory`（System Options → External 
    #: References →
    #: Load documents in memory only）**is ignored when opening documents through the AP
    #: I**
    #:     because `IDocumentSpecification::LoadExternalReferencesInMemory` and
    #:     `ISldWorks::OpenDoc6`(`swOpenDocOptions_LoadExternalReferencesInMemory`)
    #:     **have sole control of reference loading**」
    #:     ⇒ ★★ **即：★ 通过 API 打开时**必须**用这个选项（★ 系统选项不管用）** ✓
    #:   ⚠ 官方前提：★「valid only if `swLoadExternalReferences` is not set to `None`」
    #: ⇒ ★ 若用户偏好设成"从不加载"，本选项不生效（★ 那时也不会弹框，★ 两种情形都不卡）
    #: 。
    options |= 512  # swOpenDocOptions_LoadExternalReferencesInMemory

    if ext in foreign_exts:
        if read_only:
            print("提示: LoadFile4 导入外来 CAD 文件时不支持 read_only，已忽略该参数")
        if silent:
            print("提示: LoadFile4 导入外来 CAD 文件时不支持 OpenDoc6 silent 选项，已忽略该参数")
        #: ★★ 2026-10-04（接手轮）**这两条偏好用完立刻还回去**（★ 交付纪律 · 事实 525）
        #: ：
        #:   原文是 `ensure_default_templates(sw)` **直接写全局用户偏好且永不还原**
        #:   ⇒ ★ 别人装一次我们的工具，他的**默认模板路径**与"新建提示"设置就被永久改掉 ✓
        #:   ★ 而官方 `ISldWorks.NewDocument(TemplateName, …)` 的 `TemplateName` 逐字就是
        #: 「Fully qualified path and name of the template」—— ★ 我们自己的 `new_documen
        #: t`
        #:     也**已经直接传完整路径** ⇒ 这两条偏好**只在 SolidWorks 内部创建文档时才需要**
        #: （`LoadFile4` 导入外来 CAD 正是这种情形）⇒ ★ 故用 `try/finally` 只包住那一步 
        #: ✓
        template_info = ensure_default_templates(sw)
        try:
            import_data = sw.GetImportFileData(file_path)
            if import_data is None:
                message = f"获取导入数据失败: {file_path}"
                if raise_on_error:
                    raise RuntimeError(message)
                print(message)
                return None
            # 非 DXF/DWG、非 Pro/E 外来文件应传 "r"，表示导入为新的 SolidWorks 文档；
            # 空字符串会在部分 SW2024 环境中弹出模板选择对话框并阻塞自动化。
            try:
                model = sw.LoadFile4(file_path, "r", import_data, errors)
            except TypeError:
                # SW2026 的 makepy 强类型代理会对 LoadFile4 的 [out] long
                # 再执行 int(VARIANT)，与 OpenDoc6 的已知问题相同。动态代理
                # 可以正确保留 by-ref 错误码，同时继续复用已取得的导入选项。
                ole_object = getattr(sw, "_oleobj_", None)
                if ole_object is None:
                    raise
                dynamic_sw = win32com_client.dynamic.DumbDispatch(ole_object, "SldWorks.Application")
                model = dynamic_sw.LoadFile4(file_path, "r", import_data, errors)
        finally:
            restore_default_templates(sw, template_info)
        warnings.value = 0
    else:
        doc_type = type_map.get(ext, 1)
        try:
            model = sw.OpenDoc6(file_path, doc_type, options, "", errors, warnings)
        except TypeError:
            # SW2024 的 makepy 强类型代理可能对 [out] long 再做 int(VARIANT)，
            # 动态代理会把显式 by-ref VARIANT 正确传给原生 OpenDoc6。
            ole_object = getattr(sw, "_oleobj_", None)
            if ole_object is None:
                raise
            dynamic_sw = win32com_client.dynamic.DumbDispatch(ole_object, "SldWorks.Application")
            model = dynamic_sw.OpenDoc6(file_path, doc_type, options, "", errors, warnings)
        if isinstance(model, (tuple, list)):
            values = list(model)
            model = values[0] if values else None
            if len(values) > 1 and values[1] is not None:
                errors.value = int(values[1])
            if len(values) > 2 and values[2] is not None:
                warnings.value = int(values[2])
    if model:
        print(f"已打开: {file_path}")
    else:
        message = f"打开失败, 错误码: {errors.value}, 警告码: {warnings.value}"
        if raise_on_error:
            raise RuntimeError(message)
        print(message)
    #: ★★★★★ 2026-10-01（轮 334）**补上"打开文档后"的模态框收尾** ——
    #:   真因（★ 用户当场撞上）：★ `open_document` 这 96 行里
    #:   **`CommandInProgress` / `settle` / `dismiss` / `residual` 一个都没有** ⇒
    #:   ★★ **打开带外部参考的零件时，SolidWorks 会弹「打开外部参考的零件」对话框**，
    #: 而**这条路径上没有任何人去处置它** ⇒ ★★★ **会话就挂在那儿**（★ 我上一轮的命令就是
    #: 这么被中断的）。
    #: ★ 而**处置的通用解法本仓库早就有**（`settle_residual_dialogs`：按 Win32 类名 `#32
    #: 770` 找，
    #:   发 `WM_COMMAND` + `IDOK` 点掉 —— **不认按钮文本、不按坐标、零硬编码**）——
    #:   ★★ **只是没接在这里**（`settle_residual_dialogs` 的 docstring 自己写过：
    #:   「35 个脚本只查不点」「**"发现"和"处置"是两件事**」）。
    #: ★ 为什么 `CommandInProgress` 救不了它：★ 那个对话框是**文档加载时由 SolidWorks 自
    #: 己弹的**，
    #:   ★ **不是 COM 调用在等用户输入** ⇒ ★ 抑制标志管不到它。
    #:   ⚠ `settle_seconds` 取 **1.5 s**：★ 弹窗**不是**在 `OpenDoc6` 返回的那一刻出现
    #: （见 `dismiss_residual_dialogs` 的 docstring：★ 「查得太早 ⇒ 报无残留而屏幕上明明
    #: 有一个」）。
    try:
        found, dismissed, _scanned = settle_residual_dialogs(sw, settle_seconds=1.5, poll_ms=250)
        if found:
            print(f"  模态框收尾: 发现 {found} 个 · 点掉 {dismissed} 个")
    except Exception as exc:                                   # noqa: BLE001
        print(f"  模态框收尾失败（不阻断打开）: {type(exc).__name__}: {str(exc)[:120]}")
    return model


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本机实测结论的固化）
# 文件:   scripts/sw_connect.py —— 本函数
# 定位:   ★★★ 2026-10-10（规格 284）**本机实测：`SaveAs3` **不能换**** —— ★ 待办原话是
# 「`Extension.SaveAs` → `SaveAs3`（★ **改错会直接坏掉写盘**）」⇒ ★★ **实测正好证明确实
# 会**：
# 真机（SW **34.4.1**）逐 `Options`（★ `GetAdvancedSaveAsOptions(0/1/2/3)`）⇒ ★ `SaveAs3
# `
#         **四个都返回 `True`、`errors=0`**，★★ **而文件**一个都没写出来**** ⇒ ★★★ **静默失败**
#         （★ 比「报错」更危险 —— ★ 调用方会以为存成功了）。
#         ★ **对照**：★ `SaveAs` ⇒ ★ **文件真的写出来**（48696 B）⇒ ★ **现状是好的**。
#         ★★ **官方链**（★ 逐字）：★ `SaveAs` → `Obsolete. Superseded by SaveAs2` →
#         `Obsolete. Superseded by SaveAs3`（★ 链终点）⇒ ★ 官方**确实要我们换**；
# ★★ **而本机不能换** ⇒ ★★★ **处置：★ 保持 `SaveAs` + 把这条实测登记在此**（★ 不照链硬换
# ）。
#         ★ 读数：`output/_probe284_saveas3.txt` · `output/_probe284_saveas3_opt.txt`。
# 官方依据: `C:/swapi/types/IModelDocExtension/{SaveAs,SaveAs2,SaveAs3}.md` · `…/GetAdva
#           ncedSaveAsOptions.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数
# ────────────────────────────────────────────────────────────────────
def save_document(model, file_path=None):
    """
    保存文档。

    ⚠★ **不要换成 `SaveAs3`** —— ★ 真机实测它**静默失败**（★ 返回 True 却不落盘，★ 见上方来源块）。

    参数:
        model: IModelDoc2 对象
        file_path: 另存为路径，None 则保存到当前位置

    返回:
        bool 成功/失败
    """
    errors = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    warnings = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

    if file_path:
        file_path = _expand_path(file_path)
        _ensure_parent_dir(file_path)
        success = model.Extension.SaveAs(
            file_path, 0, 1, create_empty_dispatch_variant(), errors, warnings
        )
    else:
        success = model.Save3(1, errors, warnings)

    if success:
        print(f"保存成功: {file_path or get_com_member(model, 'GetPathName')}")
    else:
        print(f"保存失败, 错误码: {errors.value}, 警告码: {warnings.value}")
    return bool(success)


def mm(value):
    """毫米转米（SolidWorks API 单位）。"""
    return value / 1000.0


def deg(value):
    """角度转弧度。"""
    import math
    return value * math.pi / 180.0
