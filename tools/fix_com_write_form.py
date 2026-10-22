"""★ 批量修：把「用 get_com_member 写**属性**」改成 `set_com_member`（★ 按 AST span，不用正则）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/fix_com_write_form.py
# 定位:   ★ 2026-10-03（轮 468）★ 承门禁 `tools/check_com_write_form.py` 报出的 **98 
#           处**。
#   ★★ **为什么可以批量**：★ 那是**同一条规矩的机械违反** ——
#     `get_com_member(obj, "<属性>", 值)` 与 `set_com_member(obj, "<属性>", 值)`
#     **实参完全相同**，只差**函数名**（★ 本仓两个 helper 的签名形状一致）⇒
#     ★★ 故替换 = **只改那一个标识符**，不动任何实参 ✓
#   ★★★ **做法（★ 与正则的差别）**：★ 用 `ast` 找到每个**违规调用**的 `func` 节点，
#     拿它的 `lineno/col_offset/end_lineno/end_col_offset` **精确替换那一小段** ——
#     ★ 这样**不会误伤**字符串里的同名字样、也不会动别的实参 ✓
#   ★ **安全**（事实 61）：改完**必须** `git diff --stat`（★ 只有增删相等的行数），
#     并**回读**每个被改文件（事实 48 定则②）✓
#   ⚠ **幂等**：已经改过的不会重复改（★ 它只找 `get_com_member` 那个名字）✓
# 官方依据: `C:\swapi\types\**\*.md` 的 `kind: property`（★ 与门禁同一判据）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   `scripts/**` · `tools/**`（★ 测试目录不动 —— 它们可能在**断言**那种写法）。
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 改完 `tools/check_com_write_form.py` 退出 0。

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
SCAN = R / "output" / "com-write-form-scan.json"


def main() -> int:
    if not SCAN.exists():
        print("  先跑 tools/check_com_write_form.py 生成扫描表")
        return 1
    hits = json.loads(SCAN.read_text(encoding="utf-8"))["hits"]
    by_file: dict = {}
    for h in hits:
        by_file.setdefault(h["file"], []).append(h)

    total = 0
    for rel, rows in sorted(by_file.items()):
        p = R / rel
        if not p.exists():
            continue
        src = p.read_text(encoding="utf-8")
        tree = ast.parse(src)
        want = {(r["line"], r["member"]) for r in rows}
        #: \u2605 \u6536\u96c6\u8981\u66ff\u6362\u7684 func \u8282\u70b9\uff08\u2605 \u53d6\u5b83\u7684**\u540d\u5b57**\u90a3\u4e00\u5c0f\u6bb5\uff09
        spans = []
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            fn = n.func
            nm = getattr(fn, "id", None) or getattr(fn, "attr", None)
            if nm != "get_com_member" or len(n.args) < 3:
                continue
            a1 = n.args[1]
            if not (isinstance(a1, ast.Constant) and isinstance(a1.value, str)):
                continue
            if (fn.lineno, a1.value) not in want:
                continue
            spans.append((fn.lineno, fn.col_offset, fn.end_lineno, fn.end_col_offset))
        if not spans:
            continue
        lines = src.splitlines(keepends=True)
        #: \u2605 \u4ece**\u540e\u5f80\u524d**\u6362\uff08\u2605 \u4f4d\u7f6e\u4e0d\u4f1a\u56e0\u524d\u9762\u7684\u6539\u52a8\u800c\u504f\u79fb\uff09
        for (l0, c0, l1, c1) in sorted(spans, reverse=True):
            if l0 != l1:
                print("    \u26a0 \u8df3\u8fc7\u8de8\u884c\u8c03\u7528 %s:%d" % (rel, l0))
                continue
            line = lines[l0 - 1]
            seg = line[c0:c1]
            if seg != "get_com_member":
                print("    \u26a0 \u8df3\u8fc7\uff08\u53d6\u5230 %r\uff09%s:%d" % (seg[:30], rel, l0))
                continue
            lines[l0 - 1] = line[:c0] + "set_com_member" + line[c1:]
            total += 1
        new = "".join(lines)
        try:
            compile(new, str(p), "exec")
        except SyntaxError as e:                                  # noqa: BLE001
            print("    **\u8bed\u6cd5\u574f\uff0c\u4e0d\u5199** %s: %s" % (rel, str(e)[:60]))
            continue
        p.write_text(new, encoding="utf-8")
        print("    \u6539\u4e86 %-46s %d \u5904" % (rel, len(spans)))
    print("  \u5408\u8ba1\u6539\u4e86 **%d** \u5904" % total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
