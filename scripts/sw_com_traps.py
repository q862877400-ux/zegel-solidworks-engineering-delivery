r"""pywin32 × SolidWorks 的实操坑（外部调研 + 本机反射双重核实）。

这个模块回答**「官方 API 清单之外，调用会不会炸、怎么绕」**。
清单在 ``sw_api_<程序集>.py``；本模块讲**怎么用才对**。

⚠⚑ 每条都标了来源与核实状态
--------------------------------
  ``[反射核]``   —— 本机反射已核实（成员存在、参数个数、接口归属）
  ``[外部]``     —— 第三方实证/官方文档镜像，**本机无法核实**（行为类结论）
  ``[查不到]``   —— 调研过但**找不到权威依据**，此处明写，不编

⛔ 外部链接里的行为类结论**未在本机实测**（AGENTS.md 铁律 2）——
   本模块核的是「官方签���对不对」，不是「这套写法跑不跑得通」。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   外部调研（GitHub 多项目，均已确认许可为 MIT）+ 本机反射
# 文件:   andrewbartels1/SolidworksMCP-python / Solidworks-MCP (hjbaard) /
#         Millwright (raylanlin) / chatsw (danimeo) / ZiChen-Ni /
#         kilwizac/solidworks-api-mcp（官方文档镜像）
# 定位:   pywin32 迟到绑定、按引用传参、参数个数自适应、弹窗抑制、
#         许可探测五条链路的实操硬知识
# ⚑ 许可：全部 MIT。⚠ **只取经本机反射核实的结论，不抄任何仓库的代码或注释文本**。
# ⚠ 官方文档站 help.solidworks.com 直连 403（调研方实测），
#   故官方条文引自 GitHub 上的**官方文档镜像**；链接见 docs/external-crosscheck.md。
# 覆盖:   后续同级定义
# ⚠ 本组为静态整理，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from typing import Any

__all__ = [
    "DISP_E_TYPEMISMATCH",
    "DISP_E_UNKNOWNNAME",
    "DISP_E_BADPARAMCOUNT",
    "DISP_E_PARAMNOTOPTIONAL",
    "DISP_E_MEMBERNOTFOUND",
    "ERROR_CODES",
    "is_type_mismatch",
    "explain",
    "byref_long",
    "byref_pair",
    "adaptive_arity",
    "is_swp_macro",
    "RUN_MACRO_ERROR",
    "DEPRECATED_SAVEAS",
]

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   COM 标准错误码 + 外部调研（SolidworksMCP-python / Millwright / chatsw）
# 定位:   SolidWorks 自动化里**必遇**的 5 个错误码。
# ⚑ 〔外部〕SolidworksMCP-python：pywin32 迟到绑定**不会**把普通 Python ``int``
#   编到 ``ByRef Long`` 参数里，直接传 int 报 ``0x80020005``。
# ⚑ 〔外部〕Millwright：传多了报 ``0x8002000A``（太多）、传少了报
#   ``0x8002000B``（**太少**）—— ⚠ 这与流传的「>12 参数就失败」**方向相反**。
# ⚑ **本机反射无法核实这些码的行为**（它们是运行期结果，不是签名）。
#   本模块只提供「码 → 含义 → 该怎么改」的查表。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
DISP_E_TYPEMISMATCH = 0x80020005
DISP_E_UNKNOWNNAME = 0x80020006
DISP_E_MEMBERNOTFOUND = 0x80020004
DISP_E_BADPARAMCOUNT = 0x8002000A      # 参数**太多**
DISP_E_PARAMNOTOPTIONAL = 0x8002000B  # 参数**太少**

ERROR_CODES: dict[int, str] = {
    DISP_E_TYPEMISMATCH:
        "DISP_E_TYPEMISMATCH —— **参数类型对不上**。"
        "最常见：把普通 int 传给 ByRef Long（[out] 参数）→ 用 byref_long()",
    DISP_E_UNKNOWNNAME:
        "DISP_E_UNKNOWNNAME —— 成员名不存在。"
        "常见：把 .NET 属性名（get_Xxx）当成 COM 名传了",
    DISP_E_MEMBERNOTFOUND:
        "DISP_E_MEMBERNOTFOUND —— dispid 有效但默认 dispinterface 不暴露该名。"
        "〔外部〕典型：GetActiveObject 拿到的 dispatch 上 IModelDoc2.FirstFeature 报此错",
    DISP_E_BADPARAMCOUNT:
        "DISP_E_BADPARAMCOUNT —— **参数太多** → 递减重试（见 adaptive_arity）",
    DISP_E_PARAMNOTOPTIONAL:
        "DISP_E_PARAMNOTOPTIONAL —— **参数太少** → 递增补齐（见 adaptive_arity）",
    0x80004005: "E_FAIL —— 通用失败",
    0x80040112: "COM 类未授权 —— 通常是**该产品没许可**（PDM/Simulation/Routers）",
    0x80070057: "E_INVALIDARG —— 参数值非法",
    0x8007000E: "E_OUTOFMEMORY —— 内存不足",
    0x80004002: "E_NOINTERFACE —— 找不到接口/对象",
}


def is_type_mismatch(code: int) -> bool:
    """判断是不是「参数类型对不上」这个错。"""
    return (int(code) & 0xFFFFFFFF) == DISP_E_TYPEMISMATCH


def explain(code: int) -> str:
    """把 HRESULT 翻成人话；查不到就**明说查不到**。"""
    code = int(code) & 0xFFFFFFFF
    if code in ERROR_CODES:
        return ERROR_CODES[code]
    if code & 0x80000000:
        return f"未收录的失败码 0x{code:08X}（本表无释义）"
    return f"0x{code:08X}（非失败 HRESULT）"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   外部调研（SolidworksMCP-python，MIT）+ 官方反射
# 定位:   **给 ByRef Long 造 VARIANT** —— 官方文档完全不提的坑。
# ⚑ 〔外部〕pywin32 迟到绑定不把普通 int 编到 ByRef Long 参数，报 0x80020005。
# ⚑ 〔反射核〕哪些成员有这类 [out] 参数是**可查的** —— 索引里形如
#   ``Int32&`` / ``Object&`` / ``String&`` 的末位参数即是。实测三例：
#     ISldWorks.GetErrorMessages(Object&, Object&, Object&) 3 参全 [out]
#         ⇒ 调用方**一个都不传**（本仓库 arity 表记 0）✅
#     ISldWorks.OpenDoc6(..., Int32&, Int32&)                6 参、末 2 个 [out]
#         ⇒ 要取值必须用 :func:`byref_long` ✅
#     ISldWorks.RunMacro2(..., Int32&)                       5 参、末 1 个 [out] ✅
# ⚑ ⚠ **多 byref + 动态派发可能逆序**（pywin32 #622 / #1303，两条独立复现，
#   官方维护者未确认修复）；**单个 byref 正常**。⇒ 两个以上出参时
#   用 :func:`byref_pair` 并**自行校验回填顺序**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态整理，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def _variant(vtype: int, initial: int) -> Any:
    try:
        import pythoncom
        import win32com.client
    except ImportError:
        return int(initial)   # 回退，保住 mock / CI 路径不炸
    ctor = getattr(win32com.client, "VARIANT", None)
    if not callable(ctor):
        return int(initial)
    return ctor(int(vtype), int(initial))


def byref_long(initial: int = 0) -> Any:
    """造一个 ``VT_BYREF | VT_I4`` 的 VARIANT，供**单个** ByRef Long 出参用。

    >>> 本机实跑已确认这条规则是必需的（SolidWorks 2026 SP4.1，撤销铁律 2 后）：
        OpenDoc6(path, type, opt, argstr) —— 4 参（另 2 个是 Int32& 出参）
          只传 4 参            -> -2147352561 DISP_E_PARAMNOTOPTIONAL（参数太少）
          传 6 参、末两个 None -> -2147352571（类型不匹配）
          传 6 参、末两个本函数造的 VARIANT -> 成功打开零件
    由此得到一条索引层面的规则：
        **arity 表排除 by-ref 是「文档口径」，不是「调用口径」**
        —— 调用时必须为每个 by-ref 出参补一个占位实参。
    """
    try:
        import pythoncom
    except ImportError:
        return int(initial)
    return _variant(
        int(getattr(pythoncom, "VT_BYREF", 0)) | int(getattr(pythoncom, "VT_I4", 0)),
        initial,
    )


def byref_pair() -> tuple[Any, Any]:
    """造**两个** ByRef Long 出参（典型如 SaveAs 的 Errors + Warnings）。

    ⚠ ⚠ **pywin32 已知问题**：多个 byref 参数 + 动态派发时**回填顺序可能颠倒**
    （pywin32 issue #622 / #1303，两条独立复现，维护者未确认修复）。
    ⇒ 拿到之后**务必自行校验**，别默认第一个就是 Errors。
    ⚠ 单个 byref 不受影响（#1303 明确单参数正常）。
    """
    return byref_long(0), byref_long(0)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   外部调研（Millwright，MIT）
# 定位:   **参数个数自适应** —— 用 HRESULT 判据代替猜数字。
# ⚑ 〔外部〕Millwright 的做法：从 30 递减到 21 逐个试，按错误码决定方向：
#     0x8002000A（太多）→ 继续减
#     0x8002000B（太少）→ 停，当前就是对的
# ⚑ 〔外部〕chatsw 传 27 个位置参数成功 ⇒ **流传的「>12 参数就失败」查不到依据**。
# ⚠ 本函数**不吞异常**：它只把 HRESULT 翻译成「该加还是该减」的信号。
# ⚠ **本机无法核实**（运行期行为），来源为第三方。
# 覆盖:   后续同级定义
# ⚠ 本组为静态整理，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def adaptive_arity(call, base: tuple, low: int = 20, high: int = 30):
    """按错误码自适应地调 ``call(*args[:n])``，返回**成功那次**的返回值。

    ⚠ 这是**兜底**手段。优先用反射/官方文档确认 arity —— 本函数靠试错，
    每次失败都可能已经在 SolidWorks 里产生了副作用。
    """
    last = None
    for n in range(min(high, len(base)), low - 1, -1):
        try:
            return call(*base[:n])
        except Exception as exc:                      # noqa: BLE001
            last = exc
            message = str(exc)
            if str(DISP_E_BADPARAMCOUNT & 0xFFFFFFFF) in message \
                    or "-2147352562" in message:
                continue                               # 太多 → 减
            raise
    if last is not None:
        raise last


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   外部调研（SolidworksMCP-python，MIT）+ 官方文档镜像
# 定位:   ``.swp`` 是 **OLE2 复合文档**，不是纯文本。
# ⚑ 手写文本改名成 .swp 会被 SolidWorks 拒，而报错通常只有「文件无效」，
#   看不出真实原因 ⇒ 用 :func:`is_swp_macro` 先判别。
# ⚠ 〔反射核〕``swRunMacroError_e`` **不在官方 interop 类型库中** ⇒ 本模块
#   下面的值是第三方从 swconst 转录的，标注为**未经反射核实**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态整理，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
_OLE2_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

#: ⚠ `swRunMacroError_e` 的值 —— **第三方转录，未经本机反射核实**
RUN_MACRO_ERROR: dict[int, str] = {
    0: "NoError",
    1: "InvalidArg",
    2: "MacrosAreDisabled",
    3: "NotInDesignMode",
    4: "OnlyCodeModules",
}


def is_swp_macro(data: bytes) -> bool:
    """判断一段字节是不是**真正的** .swp 宏（OLE2 复合文档）。"""
    if not isinstance(data, (bytes, bytearray)):
        return False
    return bytes(data[:8]) == _OLE2_MAGIC


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   官方文档镜像（kilwizac/solidworks-api-mcp，官方原文）
# 定位:   **官方已标 Obsolete 的保存成员**。原文：
#     SaveAs  → "Obsolete. Superseded by IModelDocExtension::SaveAs2."
#     SaveAs2 → "Obsolete. Superseded by IModelDocExtension::SaveAs3."
# ⚑ 〔反射核〕本机 SolidWorks 版本上三者的 arity：
#     SaveAs=4 · SaveAs2=6 · **SaveAs3=5** · SaveAs4 不存在
# ⇒ **本项目导出/保存一律用 ``SaveAs3``**，不要用 SaveAs / SaveAs2。
# ⚠ ⚠ 官方文档另有一处**措辞错误**：讲 Options 组合时写
#   "specify Options by **bitwise ANDing**"，但语义是**并置（OR）**标志位 ——
#   照抄 AND 会得到 0。⇒ **按 OR 写**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态整理，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
DEPRECATED_SAVEAS = {
    "IModelDocExtension.SaveAs": "Obsolete → 用 SaveAs3（勿用 SaveAs2，它也 Obsolete）",
    "IModelDocExtension.SaveAs2": "Obsolete → 用 SaveAs3",
    "IModelDocExtension.SaveAs3": None,   # ← 当前该用的
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把已核过的"废弃入口 → 该用哪个"集中成表）
# 文件:   scripts/sw_com_traps.py —— 本定义与其后同级定义
# 定位:   ★★ **objective⑤「互锁推广」的靶子表** —— 供 `tests/test_save_routing_interlock.py`
#         与同族互锁测试**逐条上锁**（★ 错误的路在假对象上**直接 raise**）。
# 官方依据: ★ **每条都从官方类型表读到 `Obsolete. Superseded by [[<iface>::<member>]]`**
#   （★ 文本形态见 `C:\swapi\types\IModelDocExtension\SaveAs.md` 第一行正文 ——
#    ★ 注意是 `[[…::…]]` 这种 **wiki 链接**写法）。
# ⚠ **只放**已核实**的**（★ 铁律 1 / 硬约束⑧）—— ★ 本表**不是**"扫一遍 Superseded 就全放进来"：
#   ★ 那份扫描（事实 271）出 42 处，而抽样就看出**三类假阳性**：
#     ① 后继名 == 自己（解析错）· ② **不同 arity 的不同方法**（官方说 Superseded 指的是**那一族**，
#     不是"同名替换"）· ③ **跳代常伴随签名变化**（★ 我们一直在用的 `GetBodies2` 就是例子）。
#   ⇒ ★★ **每条进来前要**读两边的签名**（★ 那是独立的一件工作）。
# 覆盖:   后续同级定义
# ⚠ 本组为静态整理，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
DEPRECATED_ENTRIES: dict[tuple[str, str], str] = {
    #: ★ 保存族（★ 陷阱表 `DEPRECATED_SAVEAS` 已核过；★ arity：SaveAs=4 · SaveAs2=6 · **SaveAs3=5**）
    ("IModelDocExtension", "SaveAs"): "SaveAs3",
    ("IModelDocExtension", "SaveAs2"): "SaveAs3",
    #: ★ 包覆族（★ 2026-10-01 轮 329–331 **真机验过两个都回对象**：
    #:   `InsertWrapFeature`（3 参）与 `InsertWrapFeature2`（5 参）⇒ ★ **该用带 2 的那个**；
    #:   ★ 证据 `output/wrap-v1-vs-v2.json`）
    ("IFeatureManager", "InsertWrapFeature"): "InsertWrapFeature2",
}


def deprecated_successor(member: str) -> str | None:
    """★ 给定**成员名**，回它该用的后继名；★ 不认识的回 `None`（★ 不猜 —— 铁律 5）。"""
    for (_iface, m), succ in DEPRECATED_ENTRIES.items():
        if m == member:
            return succ
    return None

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把"扫仓库"的公共纪律提取成函数）
# 文件:   scripts/sw_com_traps.py —— 本定义
# 定位:   ★★ **"扫仓库看某名字在不在"必须排除反射转储** —— 本会话**三次**手写漏了：
#   · 轮 351：扫"废弃入口"得 **1020** 处（★ 实际只 **42**）；
#   · 轮 353：判"我们有没有某曲面操作"时，把 **2 条其实有实现**的错判成"真缺"。
#   ⇒ ★ **`scripts/sw_api_*.py` 是反射转储表**（列出**所有**成员名），
#     ★★ **它不是调用、也不是实现** ⇒ 凡"扫仓库"一律先排除。
# 覆盖:   后续同级定义
# 许可:   本仓库 MIT。无第三方代码引入。
# ────────────────────────────────────────────────────────────────────
def iter_real_sources(root: "Path | str | None" = None, pattern: str = "sw_*.py"):
    """★ 逐个 yield **真实现**的源文件（★ **排除 `sw_api_*.py` 反射转储**）。

    :param root: 目录；★ 缺省 = 本文件所在的 `scripts/`。
    :param pattern: 文件名的 glob（★ 缺省 `sw_*.py`）。
    ★★ **为什么要有它**：见本函数上方来源块 —— 本会话**三次**在"扫仓库"时忘了排除转储，
      而每次的后果都是**把数放大 24 倍**或**把"有"判成"无"**。
    """
    from pathlib import Path as _P

    base = _P(root) if root else _P(__file__).resolve().parent
    for p in sorted(base.glob(pattern)):
        if p.name.startswith("sw_api_"):      # ★ 反射转储，不是实现
            continue
        yield p


def find_real_implementations(needle: str, root: "Path | str | None" = None) -> list[str]:
    """★ 在**真实现**里找 `needle`，回 `["文件:行号", …]`（★ 转储表已排除）。"""
    import re as _re

    hits: list[str] = []
    for p in iter_real_sources(root):
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for m in _re.finditer(_re.escape(needle), text):
            hits.append("%s:%d" % (p.name, text[:m.start()].count(chr(10)) + 1))
    return hits
