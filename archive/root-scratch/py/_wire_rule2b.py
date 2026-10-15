import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_registry.py")
t = P.read_text(encoding="utf-8")

OLD_CHECK = '''        if p.name in ("response_format",):
            raise GateError(
                "工具 %r 不要自己声明 response_format —— 注册器会自动加" % spec.name
            )'''
NEW_CHECK = OLD_CHECK + '''
        # ⚑⚑ 规则 2 的**长度那一半**（2026-10-01 轮 134 接上）。
        #    ⚠⚠ **接上之前，这一半从未生效** —— `_LEN_SUFFIX` 是个**死常量**
        #    （只在定义处出现一次）。⇒ 规则 2 一直被算进「五统一门禁通过」，
        #    但它的长度那一半**从来没拦过任何东西**（已知事实 40：存在但没人用的守卫）。
        #    证据：`tests/test_rule2_length_suffix_is_enforced.py` 的负例。
        low = p.name.lower()
        #: ⚠ `bool` **不是长度**（`use_default_radius` / `reverse_thickness` 是**标志**）
        if p.kind is not bool and any(w in low for w in _LEN_WORDS) \\
                and not low.endswith(_LEN_SUFFIX):
            if (spec.name, p.name) not in _LEN_SUFFIX_EXEMPT:
                raise GateError(
                    "规则 2 违反：工具 %r 的入参 %r 像是**长度**，却不以 %r 结尾 —— "
                    "要么改名（`%s%s`），要么在 `_LEN_SUFFIX_EXEMPT` 里"
                    "**写明为什么它不是毫米**"
                    % (spec.name, p.name, _LEN_SUFFIX, p.name, _LEN_SUFFIX)
                )'''
if "规则 2 的**长度那一半**" not in t:
    assert OLD_CHECK in t, "判据锚点不符"
    t = t.replace(OLD_CHECK, NEW_CHECK, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已接上规则 2 的长度那一半")
else:
    print("  判据已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
