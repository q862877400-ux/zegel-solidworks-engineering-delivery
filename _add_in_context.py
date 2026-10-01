import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_assembly_doc.py")
t = P.read_text(encoding="utf-8")

BLOCK = '''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（照官方签名新写；**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_assembly_doc.py —— 「在上下文编辑」与「外部参考」这两段
#         （2026-10-01 轮 161 新增）。
# 定位:   补 `D:\\AI\\SW-transfer\\in-context-reference-proposal.md` 指出的缺口 ——
#         但**只补真缺的那两块**：该提案说「五项全没实现」，经核实**三项早已实现**
#         （加关系/读关系在 `scripts/sketch_relations.py`，进/出在上下文编辑的**arity 通道**
#         在**本文件**的 `ASSEMBLY_DOC_ARITY` 里）⇒ 缺的是**封装**与**外部参考计数**。
# 官方签名依据（出厂反射 `iface_sldworks.txt`，三源一致）:
#     Int32 EditPart2(Boolean, Boolean, Int32&)          ← 第 3 参是 **ref Int32**
#     Void  EditAssembly()                               ← 零参
#     Int32 ListExternalFileReferencesCount(Boolean)     ← 有 **1 参重载**
#     Void  ListExternalFileReferences2(Object&×7)       ← ⚠ **7 个 Object& 出参**
# ⚠⚠ **本轮的范围与限度**：`ListExternalFileReferences2` 那 7 个 `Object&` 出参
#    **没有**去啃（事实 47/68：pywin32 迟到绑定下多出参接口常拿不到值）
#    ⇒ 本模块**只提供计数**；**内容读取标注「未查明」**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化下面三个函数。
# ─────────────────────────────────────────────────────────────────────
def edit_part_in_context(asm_model, component_keyword, *, silent=True,
                         allow_read_only=True):
    """进入**装配体里的零件在上下文编辑**态（官方 `IAssemblyDoc.EditPart2`）。

    :param asm_model: `IAssemblyDoc`
    :param component_keyword: 组件名的关键词（用既有的 `_select_by_id` 选它）
    :returns: 官方返回的 `Int32` 状态码（`swEditPartCommandStatus_e`；
        ⚠ 该枚举**在 `C:\\swapi\\enums\\` 里查不到**（铁律 5）⇒ **原样透出数字，不翻译**）。

    ⚠ 官方签名第 3 参是 **`ref Int32`** ⇒ 用本仓库既有的 `out_i4()` 给出参占位。
    """
    _select_by_id(asm_model.Extension, component_keyword, "COMPONENT")
    code = call_com_member(asm_model, "EditPart2",
                           bool(silent), bool(allow_read_only), out_i4())
    return int(code) if isinstance(code, int) else code


def exit_edit_part_in_context(asm_model):
    """退出在上下文编辑态（官方 `IAssemblyDoc.EditAssembly`，**零参**）。"""
    call_com_member(asm_model, "EditAssembly")
    return True


def list_external_file_references_count(component, *, include_hidden=False):
    """数一个组件**对外部文件的参考条数**（官方 `IComponent2.ListExternalFileReferencesCount`）。

    :param component: `IComponent2`
    :param include_hidden: 对应官方那个 **1 参重载**的 `Boolean`。
    :returns: `int`。

    ★ **为什么只做计数**：官方取内容的 `ListExternalFileReferences2` 有
    **7 个 `Object&` 出参**（另有一个 9 参变体）⇒ 按事实 47/68，
    pywin32 迟到绑定下多出参接口常拿不到值 ⇒ ⚠ **本轮没去啃**，
    只做**能验的计数**（`0 → ≥1` 就是提案 §六.② 那条判据）。
    """
    return int(call_com_member(component, "ListExternalFileReferencesCount",
                               bool(include_hidden)) or 0)
'''

if "def edit_part_in_context(" not in t:
    t = t.rstrip() + "\n" + BLOCK
    P.write_text(t, encoding="utf-8")
    print("  ok 已加 edit_part_in_context / exit_edit_part_in_context / list_external_file_references_count")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
