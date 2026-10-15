"""给 `ToolSpec` 加 `derived_args`（C 类的「spec 展平层」）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_derived_args.py
# 定位:   T-011 分类表里的 **C 类（「需 spec 展平层」）** 的基础设施。
#         那一类的函数入参是 **typed spec dataclass**，例如
#             `create_base_flange(model, sketch_ref, spec: BaseFlangeSpec)`
#         MCP 表面不能收一个 dataclass ⇒ 要把字段**展平**成标量入参。
#
#  ⚠⚠ 与 `extra_op` 的区别（为什么不复用逃生口）：
#     `extra_op` **替换整个调用**（连 `module`/`function` 都不要了）
#     ⇒ 用了它就等于**放弃声明式**，退回到「在声明文件里写执行逻辑」。
#     `derived_args` 只**从已声明的标量入参派生**一个额外实参（如 `spec=`）
#     ⇒ **调用本身仍是声明式的**（`module`/`function`/参数同名直传都还在）。
#     **这是本轮要守住的东西：能不退就退。**
#
#  ⚠ 单位换算放在这里，且**只做一次**（并入规范规则 2）：
#     这些 spec 的 docstring 明写「长度单位为米」，而 MCP 表面按规则 2 用 `_mm`
#     ⇒ 在 `derived_args` 里 `/1000.0`。角度字段本来就是**度**，原样传。
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
NEW_DOC = '''    :param derived_args: **从已声明的标量入参派生额外实参**，形如
        ``lambda params: {"spec": BaseFlangeSpec(...)}``。返回的字典会**并进**
        调用目标函数的关键字实参里。
        ⚠ 与 `extra_op` 的分工：`extra_op` **替换整个调用**（用了就放弃声明式）；
        `derived_args` **只补一个实参**，`module`/`function`/同名直传都还在。
        **能不退就退。**
        ⚠ 单位换算也放这里，且**只做一次**（并入规范规则 2）：spec 说「米」、
        MCP 表面按规则 2 用 ``_mm`` ⇒ 在派生函数里 ``/1000.0``。
    :param omitted_params: **故意不暴露**的形参名（如 ``Object`` 型的 ``colors``）。'''

OLD_FIELDS = '''    omitted_params: tuple[str, ...] = ()
    param_alias: dict[str, Optional[str]] = field(default_factory=dict)'''
NEW_FIELDS = '''    omitted_params: tuple[str, ...] = ()
    param_alias: dict[str, Optional[str]] = field(default_factory=dict)
    derived_args: Optional[Callable[[Any], dict]] = None'''

OLD_BODY = '''            if spec.extra_op is not None:
                return spec.extra_op(params)
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            return getattr(mod, spec.function)(**kwargs)'''
NEW_BODY = '''            if spec.extra_op is not None:
                return spec.extra_op(params)
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
            return getattr(mod, spec.function)(**kwargs)'''

OLD_CHECK = '''    inj = effective_inject(spec)'''
NEW_CHECK = '''    if spec.derived_args is not None and spec.extra_op is not None:
        raise GateError(
            "工具 %r 同时给了 derived_args 与 extra_op —— 前者是「补一个实参」，"
            "后者是「替换整个调用」，语义冲突，只留一个" % spec.name
        )
    inj = effective_inject(spec)'''


def main() -> int:
    t = REG.read_text(encoding="utf-8")
    edits = [
        ("doc(derived_args)", OLD_DOC, NEW_DOC),
        ("fields(derived_args)", OLD_FIELDS, NEW_FIELDS),
        ("make_tool_function(并入派生实参)", OLD_BODY, NEW_BODY),
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
