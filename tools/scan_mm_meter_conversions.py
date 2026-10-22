"""★ 扫全仓「把毫米当米 / 把米当毫米」的硬编码换算 —— ★ 上一条真 bug 的**扩散检查**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/scan_mm_meter_conversions.py
# 定位:   ★ 轮 56 真机定案了一个真 bug：★ `Get/SetSystemValue3` 吃的**就是文档单位**、
#   而代码**硬编码 `/1000` 与 `×1000`（★ 假定是米）** ⇒ ★ 那是**一个假设**。
#   ★★ **本脚本查那个假设有没有扩散到别处** —— ★ 因为本会话**反复**见到「同一个错
#     被抄到多处」（★ `add_dimension` 的旧断言 · ★ 4 个钣金 doc · ★ `Spacing1` 的单位）✓
#   ★★★ **判据（★ 可核）**：★ 出现 `* 1000` / `/ 1000` / `* 0.001` / `/ 0.001` 的行，
#     ★★ **逐个问「它凭什么假定那个值是米（或毫米）」** ✓
#   ★ **只报不动** ✓
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import io
import json
import re
import sys
import tokenize
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = REPO / "output" / "mm-meter-scan.json"
#: ★ 换算形态
PAT = re.compile(r"(\*\s*1000\.?0?|\/\s*1000\.?0?|\*\s*0\.001|\/\s*0\.001)")
#: ★★ "我知道自己在换单位"的标记（★ 命中就降级为"已声明"）
DECLARED = (
    "毫米",
    "米",
    "mm",
    "MM",
    "in meters",
    "单位",
    "文档单位",
    "GetUnits",
    "swLengthUnit",
    "scale",
    "换算",
)


def _code_only(text: str) -> str:
    """★ 剥注释与 docstring（★ 事实 513）。"""
    try:
        toks = [
            t
            for t in tokenize.generate_tokens(io.StringIO(text).readline)
            if t.type != tokenize.COMMENT
        ]
        s = tokenize.untokenize(toks)
    except Exception:  # noqa: BLE001
        s = text
    try:
        tree = ast.parse(s)
        for n in ast.walk(tree):
            if isinstance(
                n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                b = getattr(n, "body", None) or []
                if (
                    b
                    and isinstance(b[0], ast.Expr)
                    and isinstance(getattr(b[0], "value", None), ast.Constant)
                    and isinstance(b[0].value.value, str)
                ):
                    b[0].value.value = ""
        s = ast.unparse(tree)
    except Exception:  # noqa: BLE001
        pass
    return s


def main() -> int:
    rows = []
    for d in ("scripts", "mcp-server", "tools"):
        for f in sorted((REPO / d).rglob("*.py")):
            raw = f.read_text(encoding="utf-8", errors="replace")
            code = _code_only(raw)
            for i, line in enumerate(code.splitlines(), 1):
                if not PAT.search(line):
                    continue
                rows.append(
                    {
                        "file": str(f.relative_to(REPO)).replace("\\", "/"),
                        "line": i,
                        "code": line.strip()[:120],
                        "has_declaration": any(k in line for k in DECLARED),
                    }
                )
    undeclared = [r for r in rows if not r["has_declaration"]]
    byfile: dict = {}
    for r in rows:
        byfile.setdefault(r["file"], []).append(r)
    r_ = {
        "★_判据": "★ 找 `*1000` / `/1000` / `*0.001`；★ 标记「同行没写单位依据」的为**待判**",
        "★_合计": len(rows),
        "★★_同行无单位声明": len(undeclared),
        "按文件": {
            k: len(v) for k, v in sorted(byfile.items(), key=lambda x: -len(x[1]))[:20]
        },
        "待判明细": undeclared[:60],
    }
    OUT.write_text(json.dumps(r_, ensure_ascii=False, indent=1), encoding="utf-8")
    print(
        "★ 命中 %d 处换算 · ★★ 其中**同行没写单位依据**的 %d 处"
        % (len(rows), len(undeclared))
    )
    print()
    print("★ 按文件（前 12）:")
    for k, v in list(r_["按文件"].items())[:12]:
        print("   %-46s %d" % (k, v))
    print()
    print("★★ 待判前 22 条（★ 逐个问「凭什么假定是米」）:")
    for r in undeclared[:22]:
        print("   %-38s L%-5d %s" % (r["file"][-37:], r["line"], r["code"][:78]))
    print()
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
