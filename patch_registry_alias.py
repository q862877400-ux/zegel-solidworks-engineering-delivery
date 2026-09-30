"""给 tool_registry.py 加 `param_alias`（对外参数名 → 目标函数真名，显式映射）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁脚本，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_registry_alias.py
# 定位:   batch1 里 `study_name`→`name`、`element_size_mm`→`element_size` 这类
#         **对外名与实现名不同**的情形。**别名必须显式**，否则与「拼错了」无法区分。
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

OLD_DOC = "    :param needs_model: **兼容别名**（等价于 ``inject=\"model\"``）；新声明请直接用 ``inject``。"
NEW_DOC = """    :param needs_model: **兼容别名**（等价于 ``inject="model"``）；新声明请直接用 ``inject``。
    :param param_alias: **对外参数名 → 目标函数形参名** 的显式映射。
        值为 ``None`` 表示「该参数由解析器消费，**不传给目标函数**」。
        未列出的参数**同名直传**。
        ⚠ 为什么要显式：MCP 表面用 ``study_name`` 比 ``name`` 清楚、
        ``element_size_mm`` 比 ``element_size`` 合规（规则 2），
        而实现里的名字不该为了对外好看去改。
        **但别名必须写出来** —— 否则与「拼错了参数名」无法区分。
    :param omitted_params: **故意不暴露**的形参名（如 ``Object`` 型的 ``colors``）。"""

OLD_FIELDS = '''    extra_op: Optional[Callable[[Any], Any]] = None
    doc: str = ""
    omitted_params: tuple[str, ...] = ()'''
NEW_FIELDS = '''    extra_op: Optional[Callable[[Any], Any]] = None
    doc: str = ""
    omitted_params: tuple[str, ...] = ()
    param_alias: dict[str, Optional[str]] = field(default_factory=dict)'''

OLD_MAKE_BODY = '''            kwargs = {p.name: getattr(params, p.name) for p in spec.params}
            inj = effective_inject(spec)'''
NEW_MAKE_BODY = '''            kwargs = {}
            for p in spec.params:
                # `param_alias` 里 None = 由解析器消费，不进目标函数
                if p.name in spec.param_alias and spec.param_alias[p.name] is None:
                    continue
                target = spec.param_alias.get(p.name, p.name)
                kwargs[target] = getattr(params, p.name)
            inj = effective_inject(spec)'''

# check_spec：别名目标不得与 omitted / 注入名冲突；别名值必须已在 params 里声明
OLD_CHECK = '''    seen: set[str] = set()'''
NEW_CHECK = '''    for src, dst in spec.param_alias.items():
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
    seen: set[str] = set()'''


def main() -> int:
    text = REG.read_text(encoding="utf-8")
    edits = [
        ("doc(param_alias)", OLD_DOC, NEW_DOC),
        ("fields(param_alias)", OLD_FIELDS, NEW_FIELDS),
        ("make_tool_function(用别名)", OLD_MAKE_BODY, NEW_MAKE_BODY),
        ("check_spec(别名校验)", OLD_CHECK, NEW_CHECK),
    ]
    missed = []
    for label, old, new in edits:
        if old not in text:
            missed.append(label)
            continue
        text = text.replace(old, new, 1)
        print("  ✓ %s" % label)
    REG.write_text(text, encoding="utf-8")
    if missed:
        print("  ✗ 未匹配：%r" % missed)
        return 1
    print("  ⇒ 全部命中")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
