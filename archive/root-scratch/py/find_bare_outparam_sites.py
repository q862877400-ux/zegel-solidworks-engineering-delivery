r"""@brief 找出所有「给 `Int32&` 出参传裸值」的调用点 —— 一类潜伏缺陷的完整清单。

原理：对反射清单里**含 `&` 参数**的成员，检查 Astra 调用里对应位置传的是不是裸值。
真机实测（2026-10-01，SW 2026 SP4.1）证明：裸值 ⇒ 类型不匹配，必须传
`VARIANT(VT_BYREF|VT_I4, 0)`（见 `sw_connect.out_i4` 的 docstring）。

# ── 来源 ──
# 仓库:   本项目自身（静态交叉比对工具）
# 文件:   D:\AI\SW\find_bare_outparam_sites.py
# 定位:   AGENTS.md 铁律 2「静态签名比对 → 本机实测」的顺序里，把**一类**缺陷一次性找全，
#         而不是逐个撞。与 scripts/audit_call_arity.py 互补：那个查 arity，
#         这个查**出参的传值形态**。
# 官方签名依据: D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt 与
#         D:\AI\SW\_raw\topo-sldworks\iface_sldworks.txt
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 纯静态解析，未在本机实测（见 AGENTS.md 铁律 2）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(r"C:\swprojects\sw-skill-fork")
REFLECTIONS = [
    Path(r"D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt"),
    Path(r"D:\AI\SW\_raw\topo-sldworks\iface_sldworks.txt"),
    Path(r"D:\AI\SW\_raw\reflect\iface_sldworks.txt"),
]

#: 成员名 → 该成员所有重载里「出参个数」的集合
OUTPARAM_COUNTS: dict[str, set[int]] = {}


def load_reflections() -> None:
    pat = re.compile(r"^\s*\S+\s+(\w+)\(([^)]*)\)")
    for path in REFLECTIONS:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = pat.match(line)
            if not m:
                continue
            name, params = m.group(1), m.group(2)
            if not params.strip():
                continue
            parts = [p.strip() for p in params.split(",") if p.strip()]
            n_out = sum(1 for p in parts if p.endswith("&"))
            if n_out:
                OUTPARAM_COUNTS.setdefault(name, set()).add(n_out)


def scan(rel: str) -> list[tuple[int, str, str, int]]:
    """返回 [(行号, 成员名, 尾参源码, 出参个数)]。"""
    p = REPO / rel
    if not p.is_file():
        return []
    src = p.read_text(encoding="utf-8")
    out = []
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        nm = getattr(f, "id", None) or getattr(f, "attr", None)
        if nm != "get_com_member" or len(node.args) < 2:
            continue
        m = node.args[1]
        if not (isinstance(m, ast.Constant) and isinstance(m.value, str)):
            continue
        member = m.value
        counts = OUTPARAM_COUNTS.get(member)
        if not counts:
            continue
        tail = node.args[-1]
        tail_src = ast.unparse(tail)
        # 裸值 = 常量（0 / None / 数字），不是 out_i4() / VARIANT(...) 调用
        if isinstance(tail, ast.Constant):
            out.append((node.lineno, member, tail_src, max(counts)))
    return out


def main() -> int:
    load_reflections()
    print("反射里含出参的成员名: %d 个" % len(OUTPARAM_COUNTS))
    print()
    total = 0
    for rel in sorted(
        [str(q.relative_to(REPO)).replace("\\", "/") for q in (REPO / "scripts").rglob("*.py")]
        + [str(q.relative_to(REPO)).replace("\\", "/") for q in (REPO / "apps").rglob("*.py")]
    ):
        hits = scan(rel)
        if not hits:
            continue
        print("── %s ──" % rel)
        for lineno, member, tail_src, n_out in hits:
            print("   L%-5d %-34s 尾参=%-8s 该成员有 %d 个出参 ⇒ 应传 out_i4()"
                  % (lineno, member + "()", tail_src, n_out))
            total += 1
        print()
    print("合计 %d 处需要改为 out_i4()。" % total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
