r"""@brief 把「给 `Int32&` 出参传裸 0」的调用点批量改为 `out_i4()`（AST 精确定位）。

真机实测（2026-10-01，SW 2026 SP4.1）证明裸值必抛 `类型不匹配`，
正确形态是 `VARIANT(VT_BYREF|VT_I4, 0)`（`sw_connect.out_i4`）。
本脚本用 AST 拿到**那个裸 0 的精确行列**再替换 —— 不用正则，避免改错别处的 0。

修复后**必须**跑 `scripts/audit_call_arity.py` 与测试套件复核。

# ── 来源 ──
# 仓库:   本项目自身（批量修复工具）
# 文件:   D:\AI\SW\fix_bare_outparams.py
# 定位:   AGENTS.md 铁律 2「静态比对 → 本机实测」里实测结论的**回写**动作。
# 官方签名依据: 反射清单 iface_cosworks.txt / iface_sldworks.txt 里带 `&` 的参数
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 纯静态改写，改完必须实测（见 AGENTS.md 铁律 2）。
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

OUTPARAMS: set[str] = set()


def load() -> None:
    pat = re.compile(r"^\s*\S+\s+(\w+)\(([^)]*)\)")
    for path in REFLECTIONS:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = pat.match(line)
            if m and any(p.strip().endswith("&") for p in m.group(2).split(",") if p.strip()):
                OUTPARAMS.add(m.group(1))


def targets(src: str) -> list[tuple[int, int, int]]:
    """返回 [(行, 列起, 列止)]（0-based 行列，指向那个裸 0）。"""
    out = []
    for node in ast.walk(ast.parse(src)):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        nm = getattr(f, "id", None) or getattr(f, "attr", None)
        # ⚠ 必须 len(args) >= 3：只有 2 个实参时 args[-1] 是**成员名字符串本身**，
        #   不是出参（这正是首轮扫描把 GetFaces()/GetEdges() 误报成违规的原因）。
        if nm != "get_com_member" or len(node.args) < 3:
            continue
        m = node.args[1]
        if not (isinstance(m, ast.Constant) and isinstance(m.value, str) and m.value in OUTPARAMS):
            continue
        tail = node.args[-1]
        if isinstance(tail, ast.Constant) and tail.value == 0:
            out.append((tail.lineno - 1, tail.col_offset, tail.end_col_offset))
    return out


def main() -> int:
    apply = "--apply" in sys.argv
    load()
    print("反射里含出参的成员: %d 个" % len(OUTPARAMS))
    total = 0
    for p in sorted(list((REPO / "scripts").rglob("*.py")) + list((REPO / "apps").rglob("*.py"))):
        rel = p.relative_to(REPO).as_posix()
        src = p.read_text(encoding="utf-8")
        hits = targets(src)
        if not hits:
            continue
        lines = src.splitlines(keepends=True)
        # 从后往前改，避免列偏移失效
        for ln, c0, c1 in sorted(hits, reverse=True):
            lines[ln] = lines[ln][:c0] + "out_i4()" + lines[ln][c1:]
            total += 1
        new = "".join(lines)
        # 确保导入了 out_i4
        if "out_i4" in new and "out_i4" not in _existing_imports(src):
            new = _add_import(new, rel)
        print("  %-42s %d 处%s" % (rel, len(hits), "" if apply else "（dry-run）"))
        if apply:
            p.write_text(new, encoding="utf-8")
    print()
    print("共 %d 处%s。" % (total, "" if apply else "  —— 加 --apply 落地"))
    return 0


def _existing_imports(src: str) -> str:
    return "\n".join(l for l in src.splitlines() if l.startswith(("from ", "import ")))


def _add_import(src: str, rel: str) -> str:
    """把 out_i4 加进已有的 sw_connect 导入行；没有就新加一行。"""
    if re.search(r"from\s+\.?sw_connect\s+import\s+[^\n]*\bget_com_member\b", src):
        return re.sub(
            r"(from\s+\.?sw_connect\s+import\s+)([^\n]*\bget_com_member\b)",
            lambda m: m.group(1) + "out_i4, " + m.group(2),
            src, count=1,
        )
    if re.search(r"from\s+\.?sw_connect\s+import\s+", src):
        return re.sub(r"(from\s+\.?sw_connect\s+import\s+)",
                      lambda m: m.group(1) + "out_i4, ", src, count=1)
    depth = rel.count("/")
    prefix = "." * 0 if depth == 0 else "."
    anchor = "from __future__ import annotations\n"
    add = "%sfrom %ssw_connect import out_i4  # noqa: E402\n" % ("", prefix)
    if anchor in src:
        return src.replace(anchor, anchor + add, 1)
    return add + src


if __name__ == "__main__":
    raise SystemExit(main())
