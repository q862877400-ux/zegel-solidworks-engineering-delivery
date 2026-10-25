"""扫描判定器里「守护式判据」：`if <真值>:` 体内 return FAIL，假分支直接落到 PASS。

## 为什么这是本仓最系统性的弱点

第 33 / 35 / 36 轮各修一处，机制完全相同：

| 轮 | 位置 | 手法 |
|---|---|---|
| 33 | 孔量测 / 特征树 | 数据没取到，`complete` 仍为 True ⇒ 判 fail（误判） |
| 35 | `required_checks` | 空就跳过「删除必需检查」这条判据 |
| 36 | `evidence_version` | 空就跳过「旧版本证据」这条判据 |

共性：**判据写成 `if x and y:` 的形式，`else` 什么都不做** ⇒
只要不声明（让 `x` 或 `y` 为假），判据就不生效，函数一路走到 `PASS`。

## 本工具的判据

扫 `scripts/engineering/acceptance/*.py` 里**判定器**（`judge_*`）中的 `if`：

- 条件**不是比较式**（是 `v["a"]`、`v["a"] and v["b"]`、`x` 这种真值测试）
- `if` 体内 `return ... Status.FAIL`

⇒ 列为**可疑**：请人工确认「条件为假」时是 `unknown`（可接受）还是 `pass`（缺口）。

★ 本工具**只报不判** —— 是不是缺口要看它上方有没有 `complete` 守着，
  而那需要读上下文。工具负责**把可疑点列全**，不负责下结论。

## 用法

```
python -B tools/audit_silent_pass_guards.py          # 列表
python -B tools/audit_silent_pass_guards.py --json   # 机读
```
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把「不声明就能绕过判据」这类缺陷做成可扫描项）
# 文件:   tools/audit_silent_pass_guards.py
# 定位:   扫描 scripts/engineering/acceptance/ 里 judge_* 中的「字段守护式判据」——
#          条件直接读字段真值、体内 return FAIL、假分支什么都不做。
#          这类写法只要「不声明」，判据就不生效 ⇒ 一路走到 PASS。
#          ★ 第 33/35/36 轮各修一处，机制完全相同 ⇒ 值得做成可重复扫描。
#          ★ 只报不判：是否缺口取决于它上方有没有 `complete` 守着。
# 官方依据: 不适用（纯本地 AST 静态扫描，不调 SolidWorks API、不联网）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "engineering" / "acceptance"


def _returns_fail(node: ast.If) -> bool:
    """★ `if` 体内是否 `return ... Status.FAIL`（允许 return CheckResult(**)）。"""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Return) and sub.value is not None:
            src = ast.dump(sub.value)
            if "FAIL" in src:
                return True
    return False


def _tests_field_directly(test: ast.expr) -> bool:
    """★ 条件是否**直接读字段**（`v["x"]` / `not v["y"]` / 二者的 bool 组合）。

    ⇒ 排除「问题清单非空」这种正常形态（条件根是局部名字）。
    """
    node = test
    while isinstance(node, (ast.BoolOp, ast.UnaryOp)):
        if isinstance(node, ast.UnaryOp):
            node = node.operand
            continue
        #: BoolOp：任一分支直接读字段就算
        return any(_tests_field_directly(v) for v in node.values)
    if isinstance(node, ast.Compare):
        return any(_tests_field_directly(v) for v in [node.left, *node.comparators])
    return isinstance(node, ast.Subscript)


def _is_comparison(test: ast.expr) -> bool:
    """★ 条件里有没有比较/成员测试 —— 有的话它是「判值」，不是「判有没有」。"""
    for sub in ast.walk(test):
        if isinstance(sub, (ast.Compare, ast.In, ast.NotIn)):
            return True
    return False


def _names_in(test: ast.expr) -> list:
    out = []
    for sub in ast.walk(test):
        if isinstance(sub, ast.Subscript):
            seg = sub.slice
            if isinstance(seg, ast.Constant) and isinstance(seg.value, str):
                out.append(seg.value)
            else:
                out.append("<expr>")
        elif isinstance(sub, ast.Call):
            fn = getattr(sub.func, "id", None) or getattr(sub.func, "attr", None)
            if fn:
                out.append("%s()" % fn)
    return out


def scan(path: Path) -> list:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    rows = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not fn.name.startswith("judge_"):
            continue
        for node in ast.walk(fn):
            if not isinstance(node, ast.If):
                continue
            if not _returns_fail(node):
                continue
            if _is_comparison(node.test):
                continue
            #: ★ 只留「直接测字段值」的 —— 「问题清单非空」是正常形态，不报
            if not _tests_field_directly(node.test):
                continue
            rows.append(
                {
                    "file": path.relative_to(ROOT).as_posix(),
                    "judge": fn.name,
                    "line": node.lineno,
                    "test": ast.unparse(node.test)[:80],
                    "touched": _names_in(node.test),
                    "has_else": bool(node.orelse),
                }
            )
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows = []
    for p in sorted(TARGET.glob("*.py")):
        rows.extend(scan(p))

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    print("★ 守护式判据扫描（条件不是比较式、体内 return FAIL）")
    print("  ★ 只报不判：是否缺口取决于它上方有没有 `complete` 守着\n")
    for r in rows:
        print(
            "%-38s %-24s L%-5d %s"
            % (r["file"].split("/")[-1], r["judge"], r["line"], r["test"])
        )
        print(
            "    触及字段：%s · 有 else 分支：%s"
            % (", ".join(r["touched"]) or "—", "是" if r["has_else"] else "**否**")
        )
    print("\n共 %d 处" % len(rows))
    print("★ 其中没有 else 分支的 %d 处最可疑（假分支直接往下走）"
          % len([r for r in rows if not r["has_else"]]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
