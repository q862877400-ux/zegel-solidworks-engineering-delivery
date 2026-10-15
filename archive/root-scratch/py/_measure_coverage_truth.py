"""量准 check_provenance 覆盖范围的**真实**语义。"""
import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import check_provenance as cp

BLOCK = """# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   （夹具）
# 定位:   （夹具）
# 未在本机实测
# 覆盖:   {mark}
# ─────────────────────────────────────────────────────────────────────

"""


def report(label, src):
    lines = src.splitlines()
    defs = [i + 1 for i, l in enumerate(lines) if l.startswith("def ")]
    blocks = cp._source_blocks(src)
    cover = [(s, e) for s, e, _f in blocks]
    print("  %-34s def 行=%s  块覆盖=%s" % (label, defs, cover))
    for d in defs:
        hit = [c for c in cover if c[0] <= d <= c[1]]
        print("        def@%-3d %s" % (d, ("**覆盖**" if hit else "**未覆盖**")))


# ① 不写标记，两个 def
report("无标记 + 2 def",
       BLOCK.format(mark="（无）") + "def a():\n    pass\n\n\ndef b():\n    pass\n")

# ② 后续同级定义 + 2 def（**同一个块**下面）
report("后续同级 + 2 def（同块下）",
       BLOCK.format(mark="后续同级定义") + "def a():\n    pass\n\n\ndef b():\n    pass\n")

# ③ 后续同级定义，然后**另一个块**，然后 def c
report("后续同级 + 另起一块 + def c",
       BLOCK.format(mark="后续同级定义") + "def a():\n    pass\n\n\n"
       + BLOCK.format(mark="后续同级定义") + "def c():\n    pass\n")

# ④ ★ **上轮的真实形态**：新 def 插在**块之前**
report("★ def 插在块**之前**",
       "def x():\n    pass\n\n\n" + BLOCK.format(mark="后续同级定义") + "def a():\n    pass\n")

# ⑤ 全文件
report("全文件 + 2 def",
       BLOCK.format(mark="全文件") + "def a():\n    pass\n\n\ndef b():\n    pass\n")
