"""给 `ToolSpec` 加 `pre_call`（调用**前**的副作用钩子 —— 选择就属于这一类）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_pre_call.py
# 定位:   C2 类（`create_edge_flange` / `create_gusset` / `create_draft`）的实现里明写
#         「**调用前必须先用 `_select_by_id` 把目标边选入选区**」「支撑面须由调用方先用
#         `SelectByID2` 选好」⇒ MCP 工具必须在**调用前**完成选择。
#
#  ⚠⚠ 为什么**不**复用 `derived_args`（三个机制各管一件事，不混）：
#     · `inject`       —— 注入**宿主对象**（model / sw_app / study）
#     · `derived_args` —— 从**已声明入参**派生**一个额外实参**（如 `spec=`）
#     · `pre_call`     —— 调用**前**做**副作用**（选中实体），**不产出实参**
#     把「选择」塞进 `derived_args` 能跑，但那会让「派生实参」这个名字
#     **承担它没有的含义** —— 本项目一贯反对给字段安它没有的含义。
#
# 官方签名依据: 不适用（纯 Python 文本补丁）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REG = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_registry.py")

OLD_DOC = '''    :param omitted_params: **故意不暴露**的形参名（如 ``Object`` 型的 ``colors``）。'''
NEW_DOC = '''    :param pre_call: **调用前的副作用钩子**，形如 ``lambda params: None``。
        用途：那些**实现里明写「调用前必须先选好」**的函数（如钣金 C2 类：
        `create_edge_flange` / `create_gusset` / `create_draft`）。
        ⚠ 与 `derived_args` 的分工：`derived_args` **产出实参**，
        `pre_call` **只做副作用、不产出实参**。给字段安它没有的含义是本项目反对的。
    :param omitted_params: **故意不暴露**的形参名（如 ``Object`` 型的 ``colors``）。'''

OLD_FIELDS = '''    derived_args: Optional[Callable[[Any], dict]] = None'''
NEW_FIELDS = '''    derived_args: Optional[Callable[[Any], dict]] = None
    pre_call: Optional[Callable[[Any], None]] = None'''

OLD_BODY = '''            if spec.extra_op is not None:
                return spec.extra_op(params)'''
NEW_BODY = '''            if spec.extra_op is not None:
                return spec.extra_op(params)
            if spec.pre_call is not None:
                # ⚠ 在**调用目标函数之前**执行（选择类副作用）——
                #   实现里明写「调用前必须先选好」的函数靠它。
                spec.pre_call(params)'''

OLD_CHECK = '''    if spec.derived_args is not None and spec.extra_op is not None:'''
NEW_CHECK = '''    if spec.pre_call is not None and spec.extra_op is not None:
        raise GateError(
            "工具 %r 同时给了 pre_call 与 extra_op —— extra_op 自己就是完整执行体，"
            "pre_call 无处安放" % spec.name
        )
    if spec.derived_args is not None and spec.extra_op is not None:'''


def main() -> int:
    t = REG.read_text(encoding="utf-8")
    edits = [
        ("doc(pre_call)", OLD_DOC, NEW_DOC),
        ("fields(pre_call)", OLD_FIELDS, NEW_FIELDS),
        ("make_tool_function(调用前钩子)", OLD_BODY, NEW_BODY),
        ("check_spec(与 extra_op 互斥)", OLD_CHECK, NEW_CHECK),
    ]
    missed = []
    for label, old, new in edits:
        if old not in t:
            missed.append(label)
            continue
        t = t.replace(old, new, 1)
        print("  ✓ %s" % label)
    REG.write_text(t, encoding="utf-8")
    if missed:
        print("  ✗ 未匹配：%r" % missed)
        return 1
    print("  ⇒ 全部命中")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
