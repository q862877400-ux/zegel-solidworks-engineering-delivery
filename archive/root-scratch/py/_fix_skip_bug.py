import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_mcp_protocol_layer.py")
t = P.read_text(encoding="utf-8")

OLD = '''def test_no_tool_is_declared_in_both_paths(tools):
    """@brief ★★ **两条路径不许重名** —— 此前**没有任何检查**（本轮补上）。

    ⚠ 若重名，`tools/list` 只会出现一次（集合去重）⇒ 从协议层**看不出来**；
    而"哪一个赢"取决于注册顺序 ⇒ **不确定**。⇒ 必须在**声明层**拦。
    """'''
NEW = '''def test_no_tool_is_declared_in_both_paths():
    """@brief ★★ **两条路径不许重名** —— 此前**没有任何检查**（轮 138 补上）。

    ⚠ 若重名，`tools/list` 只会出现一次（集合去重）⇒ 从协议层**看不出来**；
    而"哪一个赢"取决于注册顺序 ⇒ **不确定**。⇒ 必须在**声明层**拦。

    ⚠⚠ **本测试刻意不收 `tools` fixture**（轮 138 的故障注入抓出来的）：
    重名会让**注册失败 ⇒ server 起不来** ⇒ `tools` fixture 拿不到响应就 **`skip`**
    ⇒ ★ **判据会"恰好在被测故障发生时静默跳过"** —— 那是**最坏**的失效方式。
    ⇒ 所以本测试**只看两个声明来源**（源码 + `all_specs()`），**不碰协议层**。
    """'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已去掉那条测试的 tools fixture（并写明为什么）")
