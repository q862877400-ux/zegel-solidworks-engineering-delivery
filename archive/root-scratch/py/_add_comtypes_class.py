import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\audit_call_arity.py")
t = P.read_text(encoding="utf-8")

# ① 加一张**带理由的**显式分类表（照 `check_interface_member_ownership.MANUAL_MAP` 的做法）
TABLE = '''
# ⚑⚑ **2026-10-01（轮 130）：`comtypes` 早绑定的调用点，本工具判不了 —— 单独归类，不算「存疑」。**
#
# ## 为什么本工具的 arity 规则管不到它们
# 本工具的 arity 口径（见上）是在 **pywin32 迟到绑定**上**真机量出来**的
# （`tools/probe_outparam_object_byref.py`，已知事实 68）。
# 而 `comtypes` 的**早绑定**代理对 `[out]` 参数的处理**不同**：
# 它会**自己分配** [out] 数组/VARIANT ⇒ 调用方**只传入参就是对的**。
# ⇒ 拿 pywin32 的规矩去判 comtypes 的调用点，是**类别错误**，不是"代码有问题"。
#
# ## 为什么要写成**显式表**而不是启发式
# ⚠ 与 `check_interface_member_ownership.MANUAL_MAP` 同一理由：
# **没有依据的不许自动进来**；每一条都要写清"为什么它属于这一类"，
# 而且**在输出里单独列出来**（不是静默吞掉）。
#
# ## 表的结构
# `(文件名后缀, 行号)` → 理由
COMTYPES_CALL_SITES: dict[tuple[str, int], str] = {
    ("sw_delivery.py", 635):
        "`package.IGetDocumentNames(document_count)` —— 走 **comtypes 早绑定**"
        "（`_comtypes_document_names()`，由 `comtypes.client.GetModule` 得到）。
        "注释写明：「comtypes 会自动分配 [out] 数组，只需传入 Count」。"
        "官方 arity = 2（`Int32&` + `Object&`）⇒ 在 **pywin32** 上要传 2，"
        "在 **comtypes** 上只传入参即正确。**不是缺陷。**",
    ("sw_delivery.py", 884):
        "`sw.OpenDoc6(path, type, options, \"\")` —— 同样是 **comtypes 早绑定**"
        "（`sw` 由 `comtypes` 创建）。官方 arity = 6（含两个 `[out] long`）⇒ "
        "comtypes 代理自行分配出参。**不是缺陷。**"
        "⚠ 另：本仓库另有纪律「不经 pywin32 的 OpenDoc6 打开零件」，本条只在 Pack and Go 路径使用。",
}

'''

ANCHOR = "def audit(target, signature_paths):"
if "COMTYPES_CALL_SITES" not in t:
    i = t.index(ANCHOR)
    t = t[:i] + TABLE + t[i:]
    print("  ok 已加 COMTYPES_CALL_SITES 表")
else:
    print("  表已存在")

# ② audit() 里分流：comtypes 站点走单独一组
OLD_AUDIT = '''    ok, doubt, missing, dynamic = [], [], [], []
    for lineno, fn, member, argc in sites:
        if argc is None:
            dynamic.append((lineno, member, fn))
        elif member not in table:
            missing.append((lineno, member, argc, fn))
        elif argc in table[member]:
            ok.append((lineno, member, argc))
        else:
            doubt.append((lineno, member, argc, sorted(table[member].items())))
    return ok, doubt, missing, dynamic'''
NEW_AUDIT = '''    ok, doubt, missing, dynamic, comtypes = [], [], [], [], []
    stem = _stem(target)
    for lineno, fn, member, argc in sites:
        # ⚑ 轮 130：先看是不是**已知的 comtypes 早绑定站点** —— 那类本工具判不了
        reason = COMTYPES_CALL_SITES.get((stem, lineno))
        if reason is not None:
            comtypes.append((lineno, member, argc, reason))
            continue
        if argc is None:
            dynamic.append((lineno, member, fn))
        elif member not in table:
            missing.append((lineno, member, argc, fn))
        elif argc in table[member]:
            ok.append((lineno, member, argc))
        else:
            doubt.append((lineno, member, argc, sorted(table[member].items())))
    return ok, doubt, missing, dynamic, comtypes


def _stem(path) -> str:
    """取文件名（用于 `COMTYPES_CALL_SITES` 的键）。"""
    from pathlib import Path as _P
    return _P(str(path)).name'''
if OLD_AUDIT in t:
    t = t.replace(OLD_AUDIT, NEW_AUDIT, 1)
    print("  ok audit() 已分流 comtypes")
else:
    print("  ⚠ audit() 锚点不符")

P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
