"""★ 枚举「采集器收布尔、判定器当结论用」的字段 —— 第 38 轮那类缺陷的全景。

## 为什么

第 38 轮发现 E2 的 `downstream_linked` 是**调用方断言**而非实测推导
⇒ 声明 True 就能让 E2 通过。

这类字段的共同特征：**采集器的形参是 `bool`，且它被原样塞进 `values`**。
唯一合法的用法是采集器**自己推导**它（像 `downstream_linked` 现在这样）。

## 本工具的判据

扫 `scripts/engineering/acceptance/*.py` 的 `collect_*`：

- 形参类型标注是 `bool`
- 该名字在同一个函数的 `values={...}` 里出现（即原样透传）

⇒ 列为**可疑**：判定器如果拿它当结论，就是「声明了就算数」。

★ 只报不判：有些布尔**本来就该由调用方给**（比如 `opened_existing` —— 「我是打开了
  既有件还是新建的」只有调用方知道，采集器无法从产物反推）。
  工具负责把清单列全，人去判断每一条能不能推导。

## 用法

```
python -B tools/audit_caller_asserted_bools.py
python -B tools/audit_caller_asserted_bools.py --json
```
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把「调用方断言冒充实测」这类缺陷做成可扫描项）
# 文件:   tools/audit_caller_asserted_bools.py
# 定位:   扫 scripts/engineering/acceptance/ 的 collect_* ——
#          形参标注是 `bool` 且该名字原样进 values 的字段。
#          判定器若拿它当结论，就是「声明了就算数」。
#          ★ 第 38 轮在 E2 的 downstream_linked 上修过一次；本工具给全景。
#          ★ 只报不判：有些布尔本来就只能由调用方给（如 opened_existing）。
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


def _is_bool_ann(node: ast.expr | None) -> bool:
    if node is None:
        return False
    if isinstance(node, ast.Name):
        return node.id == "bool"
    if isinstance(node, ast.Constant):
        return node.value is bool
    return False


def _values_keys(fn: ast.FunctionDef) -> set:
    """★ 函数里 `values={...}` 的键名集合。"""
    keys = set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Dict):
            continue
        for k in node.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                keys.add(k.value)
    return keys


def scan(path: Path) -> list:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    rows = []
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef):
            continue
        if not fn.name.startswith("collect_"):
            continue
        pairs = list(zip(fn.args.kwonlyargs, fn.args.kw_defaults))
        keys = _values_keys(fn)
        for arg, _default in pairs:
            if not _is_bool_ann(arg.annotation):
                continue
            if arg.arg not in keys:
                continue
            rows.append(
                {
                    "file": path.relative_to(ROOT).as_posix(),
                    "collector": fn.name,
                    "field": arg.arg,
                    "line": arg.lineno,
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

    print("★ 「采集器收布尔、原样透传」的字段清单")
    print("  ★ 只报不判：有些本来就只能由调用方给（如 opened_existing）\n")
    by_file: dict = {}
    for r in rows:
        by_file.setdefault(r["file"].split("/")[-1], []).append(r)
    for fname, items in by_file.items():
        print("%s" % fname)
        for r in items:
            print("   %-34s %-22s L%d" % (r["collector"], r["field"], r["line"]))
    print("\n共 %d 处" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
