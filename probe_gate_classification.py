r"""@brief 精确判定：`release_check.py` 里每个 `*_run_*()` 调用点是**硬门禁**还是**诊断**。

## 为什么需要（2026-10-01 轮 72）
轮 71 的元门禁只解决了「门禁**接线了没**」，但**接线的方式**没管：
```
ownership = _run_interface_ownership_probe()      ← 诊断：**不 raise**（不拦发布）
provenance = _run_provenance_gate()               ← 硬门禁
if provenance.get("status") == "fail":
    raise AssertionError(...)                     ← 拦发布
```
⚠ **两者混在一起、没有机制保证分类正确** ⇒ 一个本该拦的门禁写成诊断，就会**静默放行**
（正是「守卫存在但没人用」的第三种面孔）。

## 判据（**精确到兄弟语句**，不用行窗口）
对每个 `x = _run_yyy()` **赋值节点**，看它在**同一函数体里的下一个兄弟语句**：
* 若是 `if x.get("status") == "fail":` 且其**体内含 `raise`** ⇒ **硬门禁**；
* 否则 ⇒ **诊断**。
⚠ 用「行窗口」判会**误判**（实测：18 行窗口把 `_run_interface_ownership_probe` 也算成了 raise，
因为它后面紧跟的是**另一件事**（`bundled_drift`）的 `raise`）。
★ 与已知事实 51 同族：**判据的范围必须贴合它要抓的那件事**（这里是「该调用的**直接后果**」，
不是「附近有没有 raise」）。

# ── 来源 ──
# 仓库:   本项目自身（只读判定，非第三方移植）
# 文件:   D:\AI\SW\probe_gate_classification.py
# 定位:   给 `check_gate_wiring` 的「接线方式」扩展提供**先查证的事实**
#         （先把真相跑出来，再决定登记表怎么写）。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SRC = Path(r"C:\swprojects\sw-skill-fork\scripts\release_check.py")


def _has_raise(node: ast.AST) -> bool:
    return any(isinstance(n, ast.Raise) for n in ast.walk(node))


def _is_fail_check(stmt: ast.stmt, var: str) -> bool:
    """`if <var>.get("status") == "fail": ... raise ...` 形态。"""
    if not isinstance(stmt, ast.If):
        return False
    src = ast.dump(stmt.test)
    if f"'{var}'" not in src and f'"{var}"' not in src:
        return False
    if "status" not in src or "fail" not in src:
        return False
    return _has_raise(stmt)


def main() -> int:
    src = SRC.read_text(encoding="utf-8")
    tree = ast.parse(src)

    results = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = fn.body
        for idx, stmt in enumerate(body):
            if not (isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call)):
                continue
            callee = getattr(stmt.value.func, "id", None) or getattr(stmt.value.func, "attr", None)
            if not (callee and callee.startswith("_run_")):
                continue
            var = getattr(stmt.targets[0], "id", "?") if stmt.targets else "?"
            # 只看到**下一个兄弟语句**为止（这就是"该调用的直接后果"）
            nxt = body[idx + 1] if idx + 1 < len(body) else None
            kind = "hard" if (nxt is not None and _is_fail_check(nxt, var)) else "diagnostic"
            results.append((stmt.lineno, callee, var, kind))

    results.sort()
    print("  release_check.py 里 %d 个 `_run_*` 调用点：" % len(results))
    for ln, callee, var, kind in results:
        print("    L%-4d %-40s %s" % (ln, callee, "**硬门禁**（紧跟 raise）" if kind == "hard"
                                      else "**诊断**（不 raise）"))
    print()
    hard = [c for _l, c, _v, k in results if k == "hard"]
    diag = [c for _l, c, _v, k in results if k == "diagnostic"]
    print("  硬门禁 %d 个 · 诊断 %d 个" % (len(hard), len(diag)))
    for c in diag:
        print("    ⚠ 诊断：%s" % c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
