import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_sketch_contract.py")
t = P.read_text(encoding="utf-8")
Q = chr(34)
ADD = '''

class GetLinesReturnShapeTests(unittest.TestCase):
    """@brief ★★ `get_lines` 返回的是**数值数组**（每条直线 12 个 float），**不是对象列表**。

    ⚑ 实测（2026-10-01 轮 140，真机 SW 2026 SP4.1，`tools/probe_getlines_count.py`）：
    ```
    画 1 条 ⇒ get_sketch_segments=1 · get_lines=12（元素类型 float）
    画 2 条 ⇒ 2 · 24
    画 3 条 ⇒ 3 · 36
    ```
    ★ 这条**钉住语义**而不是"能不能跑" ——
    ⚠ 此前冒烟只查「非空」⇒ **12 对 1 也照样绿**，于是这个语义**一直没人写下来**。
    """

    def test_docstring_states_the_measured_shape(self):
        """@brief ★★ docstring 必须写明「数值数组」与「每条 12 个 float」。"""
        src = (ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
        i = src.index("def get_lines(")
        doc = src[i:i + 1600]
        self.assertIn("数值数组", doc, "要写明返回的是数值数组")
        self.assertIn("12", doc, "要写明每条占 12 个 float")
        self.assertIn("get_sketch_segments", doc, "要给出「要几条线」的正确替代")

    def test_getter_still_calls_the_successor(self):
        """@brief 仍是后继 `GetLines2`（轮 111 的结论不能被这次改动回退）。"""
        src = (ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
        i = src.index("def get_lines(")
        self.assertIn("GetLines2", src[i:i + 1600])

    def test_no_caller_treats_the_result_as_line_objects(self):
        """@brief ★★ 仓库里**不许**有人把 `get_lines(...)` 的结果当线对象用。

        ⚠ 判据是**正向**的：结果元素是 `float` ⇒ `.X` / `.GetStartPoint2` 之类**必然错**。
        ⚠ 排除内嵌快照（`resources/skill`）—— 它是**构建产物**，由同步脚本生成。
        """
        import re
        bad = []
        for p in list(ROOT.rglob("*.py")):
            rel = str(p.relative_to(ROOT))
            if any(x in p.parts for x in (".git", "node_modules", "__pycache__")) \\
                    or "resources" in rel:
                continue
            for i, line in enumerate(p.read_text(encoding="utf-8",
                                                errors="replace").splitlines(), 1):
                if line.strip().startswith("#"):
                    continue
                if re.search(r"get_lines\\s*\\([^)]*\\)\\s*\\.", line):
                    bad.append("%s:%d %s" % (rel, i, line.strip()[:70]))
        self.assertEqual(bad, [],
                         "这些地方把 get_lines 的结果当对象用了:\\n  " + "\\n  ".join(bad))
'''
if "GetLinesReturnShapeTests" not in t:
    P.write_text(t.rstrip() + ADD, encoding="utf-8")
    print("  ok 契约测试已加 3 条")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
