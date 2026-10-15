import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_mcp_protocol_layer.py")
t = P.read_text(encoding="utf-8")

ADD = '''

# ── 轮 138：**两条注册路径**之间的一致性（此前无人检查）────────────────
#
# `server.py` 与 `batch` 模块是**两条**注册路径：
#   `server.py`     `@mcp.tool(name="solidworks_…")` 直接声明（当前 **45** 条）
#   batch 模块      `register_capabilities` 注册 `all_specs()`（当前 **41** 条）
# ⇒ 45 + 41 = **86**（与协议层实测一致）
#
# ⚠⚠ **本轮查出一件事**：`tool_registry.check_specs` 只查 **batch 路径内部**的重名；
#   **两条路径之间的重名没有任何检查** ⇒ 若有人把同一个名字加到两处，**没人会拦**
#   （而那时"哪一个赢"是不确定的）。本节的第 ② 条就是补这个。

SERVER_SRC = REPO_ROOT / "mcp-server" / "server.py"
NAME_LITERAL = re.compile(r'name\\s*=\\s*"((?:solidworks|cadstudio)_[a-z0-9_]+)"')


def _declared_in_server() -> list:
    return NAME_LITERAL.findall(SERVER_SRC.read_text(encoding="utf-8"))


def _declared_in_batches() -> list:
    sys.path.insert(0, str(REPO_ROOT / "mcp-server"))
    import importlib
    rc = importlib.import_module("register_capabilities")
    return [s.name for s in rc.all_specs()]


def test_two_paths_together_equal_the_protocol_tool_set(tools):
    """@brief ★★ `server.py` ∪ `batch` 必须**恰好等于**协议层给出的工具集合。"""
    live = {t["name"] for t in tools}
    both = set(_declared_in_server()) | set(_declared_in_batches())
    assert both == live, (
        "两边对不上：只在声明里 %s · 只在协议层 %s"
        % (sorted(both - live), sorted(live - both)))


def test_no_tool_is_declared_in_both_paths(tools):
    """@brief ★★ **两条路径不许重名** —— 此前**没有任何检查**（本轮补上）。

    ⚠ 若重名，`tools/list` 只会出现一次（集合去重）⇒ 从协议层**看不出来**；
    而"哪一个赢"取决于注册顺序 ⇒ **不确定**。⇒ 必须在**声明层**拦。
    """
    overlap = sorted(set(_declared_in_server()) & set(_declared_in_batches()))
    assert not overlap, "这些工具名在 server.py 与 batch 里**都声明了**: %s" % overlap


def test_no_duplicate_declarations_within_each_path():
    """@brief ★ 每条路径**内部**也不许重名。"""
    from collections import Counter
    for label, names in (("server.py", _declared_in_server()),
                         ("batch 模块", _declared_in_batches())):
        dup = {k: v for k, v in Counter(names).items() if v > 1}
        assert not dup, "%s 内部重名: %s" % (label, dup)


def test_protocol_tool_count_matches_the_two_paths_sum():
    """@brief ★ 数量关系：`len(server) + len(batch) == len(协议层)`。"""
    n = len(_declared_in_server()) + len(_declared_in_batches())
    assert n == 86, (
        "两条路径合计 %d 条，而协议层此前实测 86 条 ⇒ 数字变了就说明有人加了东西"
        "（**本测试是"钉死数量"的守卫，加了就要同时改这里**）" % n)
'''
if "test_no_tool_is_declared_in_both_paths" not in t:
    t = t.rstrip() + ADD
    if "\nimport re\n" not in t:
        t = t.replace("import json\n", "import json\nimport re\n", 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已加 4 条两条路径一致性的测试")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
