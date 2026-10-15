import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)

#: 找 L840 与 L875 各自所在的顶层 def（往上找第一个形如 `def ` 且缩进为 0 的行）
def enclosing_def(line_no: int) -> int:
    for i in range(line_no - 1, -1, -1):
        if lines[i].startswith("def "):
            return i
    raise SystemExit("找不到")


d1, d2 = enclosing_def(840), enclosing_def(875)
print("  L840 所在 def 在 L%d: %s" % (d1 + 1, lines[d1].strip()[:60]))
print("  L875 所在 def 在 L%d: %s" % (d2 + 1, lines[d2].strip()[:60]))

BLOCK = """# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   `wzyn20051216/solidworks-automation-skill`（**上游**，MIT）—— 上游继承的函数。
# 文件:   scripts/sw_part.py —— 这一段（L%d 起，到下一个来源块之前）。
# 定位:   2026-10-01（轮 132）**只做了一件事**：把长度单位声明从「米」校正为「**毫米**」。
#         实测依据见 `tools/verify_ellipse_smoke.py`（圆半径 25 ⇒ 边界框跨度 50 毫米）；
#         ★ 与已知事实 71（`GetBodyBox` 返回毫米）一致。
# 官方签名依据: 见**原上游代码**与 `docs/signature-audit.md`；本块**不改任何调用**。
# 许可:   上游 MIT（见 `THIRD-PARTY-NOTICES.md` §一.1）。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块涵盖这两个助手，**止于下一个来源块**。
# ─────────────────────────────────────────────────────────────────────

""" % (d1 + 2)

if "L%d 起，到下一个来源块之前）。" % (d1 + 2) not in "".join(lines):
    lines.insert(d1, BLOCK)
    P.write_text("".join(lines), encoding="utf-8")
    print("  ok 已在 L%d 前插入来源块" % (d1 + 1))
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
