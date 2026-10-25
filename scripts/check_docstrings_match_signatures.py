"""★ docstring 的「参数:」块必须与函数签名**逐个对得上**。

## 为什么（本轮错误的第三个根因）

`add_component` 的形参早已改名成 `x_m, y_m, z_m`，而 docstring 还写着

```
x, y, z: 放置位置（米）
```

⇒ 我读文档，以为「就是位置」，**从没意识到还有轴方向的问题** ⇒ 把 +Z 说成「抬高」。

★★ 这不是笔误，是**签名与文档分叉**这一类 bug。它特别坏：
   - 代码能跑（Python 不看 docstring）
   - 静态检查抓不到（ruff 不管这个）
   - **而人是靠文档理解参数的** ⇒ 文档骗人比代码写错更隐蔽

## 判据

对 `scripts/` 里每个函数的 docstring：
- 若含 `参数:`（或 `Args:`）块 ⇒ 逐行取 `名字:` 的**裸名字**
- 每个声明名**必须**是真实形参（去掉类型注解、默认值、`*`/`**`）
- 每个真实形参（除 `self`/`cls`）**必须**在块里被声明

## 棘轮

存量违规写进 `docs/docstring-params-baseline.json`，**只许降不许升**。
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
BASELINE = R / "docs" / "docstring-params-baseline.json"
SCAN_DIRS = ("scripts",)

#: 形参块里允许出现、但**不是形参**的行（说明性文字）
_IGNORE_NAMES = {"参数", "返回", "备注", "注意", "说明", "yields", "returns", "args"}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（门禁 · 文档与签名一致）
# 文件:   scripts/check_docstrings_match_signatures.py
# 定位:   查「docstring 的『参数:』块」与「函数真实签名」是否逐个对得上。
#          起因 2026-10-26：`add_component` 形参已改名 `x_m,y_m,z_m`，
#          而文档仍写 `x, y, z: 放置位置（米）` ⇒ 我据此把 +Z 说成「抬高」，
#          业主从屏幕上看出两块一样高。★ 文档骗人比代码写错更隐蔽。
# 官方依据: 不适用（本仓自定口径）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def _declared_params(doc: str) -> list:
    """从 docstring 的 `参数:` / `Args:` 块里取声明的名字（保序去重）。"""
    if not doc:
        return []
    lines = doc.splitlines()
    names: list = []
    in_block = False
    #: 块的缩进基准（`参数:` 那行的缩进）
    base = 0
    for ln in lines:
        stripped = ln.strip()
        low = stripped.lower()
        if re.match(r"^(参数|args|arguments)\s*[:：]?\s*$", low) or low.startswith(
            ("参数:", "参数：", "args:", "arguments:")
        ):
            in_block = True
            base = len(ln) - len(ln.lstrip())
            continue
        if not in_block:
            continue
        #: 结束条件：出现「返回/备注/注意/说明/Raises/Returns」等块标题，或缩进回到基准
        if re.match(r"^(返回|return|yields|备注|注意|说明|raises)\s*[:：]?", low):
            break
        indent = len(ln) - len(ln.lstrip())
        if stripped and indent <= base:
            break
        m = re.match(
            r"^([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)"
            r"\s*(?:\([^)]*\))?\s*[:：]",
            stripped,
        )
        if m:
            #: ★ 一行可能声明**多个**名字：`cx, cy: 圆心坐标（毫米）`
            #:   （第一版只取第一个 ⇒ `sketch_arc` 等被误报为「文档漏了」）
            for nm in re.split(r"\s*,\s*", m.group(1).strip()):
                if nm and nm.lower() not in _IGNORE_NAMES:
                    names.append(nm)
    return names


def _real_params(fn: ast.AST) -> list:
    out = []
    for a in list(fn.args.args) + list(fn.args.kwonlyargs):
        if a.arg in ("self", "cls"):
            continue
        out.append(a.arg)
    return out


def scan() -> tuple:
    """回 `(violations, files)`。

    违规格为 `{"target", "missing_in_doc", "missing_in_sig"}`。
    """
    violations = []
    files = 0
    for d in SCAN_DIRS:
        for p in sorted((R / d).rglob("*.py")):
            try:
                src = p.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src)
            except SyntaxError:
                continue
            files += 1
            rel = p.relative_to(R).as_posix()
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                declared = _declared_params(ast.get_docstring(node) or "")
                if not declared:
                    continue
                real = _real_params(node)
                miss_doc = [x for x in real if x not in declared]
                miss_sig = [x for x in declared if x not in real]
                if miss_doc or miss_sig:
                    violations.append(
                        {
                            "target": "%s::%s" % (rel, node.name),
                            "missing_in_doc": miss_doc,
                            "missing_in_sig": miss_sig,
                        }
                    )
    return violations, files


def main() -> int:
    violations, files = scan()
    n = len(violations)
    base = {}
    if BASELINE.is_file():
        try:
            base = json.loads(BASELINE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            base = {}
    ceiling = int(base.get("ceiling", n))

    print("[扫描] %s 下 %d 个 .py · 签名/文档不一致 %d 处（上界 %d）"
          % ("/".join(SCAN_DIRS), files, n, ceiling))
    for v in violations[:10]:
        bits = []
        if v["missing_in_doc"]:
            bits.append("文档漏了 %s" % v["missing_in_doc"])
        if v["missing_in_sig"]:
            bits.append("文档写了不存在的 %s" % v["missing_in_sig"])
        print("   %-56s %s" % (v["target"], "；".join(bits)))

    if n > ceiling:
        print(
            "★ [FAIL] 新增签名/文档分叉（%d > %d）—— 改了形参就要改文档"
            % (n, ceiling)
        )
        return 1
    print("★ [PASS] 签名与文档一致（%d 处 ≤ 上界 %d，棘轮只许降）" % (n, ceiling))
    if not BASELINE.is_file():
        BASELINE.write_text(
            json.dumps({"ceiling": n, "note": "初始基线（第 69 轮）"},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print("   已写初始基线：%s" % BASELINE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
