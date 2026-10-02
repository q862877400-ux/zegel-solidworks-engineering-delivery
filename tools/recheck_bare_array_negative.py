r"""@brief **负例校验**：证明 `scan_bare_array_args.py` 的判据抓得到它要抓的那个形态。

## 为什么（轮 185）
`tools/scan_bare_array_args.py` 在当前仓库上命中 **0 处** —— ⚠ 而「0 处」**既可能是**真的干净**，
也可能是**判据没生效****（事实 46 的假绿）。
★ 事实 62 定则：**负例是唯一的证明** ⇒ 把轮 183 **修复前**的 `sketch_relations.py`
（它里面 `CreateSpline` 收的是**形参** `points`）喂给判据，**应当命中**。

## 判据（可证伪）
```
① 取出 `git show <轮183修复前>:scripts/sketch_relations.py`（**修复前的原文**，不是手写的样本）
② 该文件里 `CreateSpline` / `CreateSpline2` 的**第 0 个实参** ⇒ 官方签名是 `Object` ⇒ **必须命中**
③ 命中数 == 0 ⇒ **判据没生效** ⇒ **非 0 退出**（否则"0 处"这个结论不成立）
```

## ⚠ 安全
**纯静态**：只 `git show` 一个历史文件 + 读反射；**不连 SolidWorks、不改任何文件**。

# ── 来源 ──
# 仓库:   本项目自身
# 文件:   tools/recheck_bare_array_negative.py
# 定位:   给 Spec Kit `105` 提供「判据站得住」的证据（事实 62 的用法）。
# 官方依据: 出厂反射 `D:/AI/SW/_raw/reflect_sldworks/iface_sldworks.txt`
#          （`SketchSegment CreateSpline(Object)` / `CreateSpline2(Object, Boolean)`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

import scan_bare_array_args as S  # noqa: E402

#: ★ 轮 183 修 `create_spline` 的那个提交（**修复前**的父提交就是要的原文）
FIX_COMMIT = "482b2f3"
TARGET = "scripts/sketch_relations.py"
MEMBERS = ("CreateSpline", "CreateSpline2")


def main() -> int:
    rev = "%s^:%s" % (FIX_COMMIT, TARGET)
    r = subprocess.run(["git", "show", rev], cwd=str(ROOT), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("  ✗ 取不到负例原文（%s）: %s" % (rev, (r.stderr or "")[:80]))
        return 2
    src = r.stdout
    print("  负例原文: `%s`（%d 字节）" % (rev, len(src)))

    tree = ast.parse(src)
    hits = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        nm = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
        if nm not in S.CALLS or len(n.args) < 3:
            continue
        member = n.args[1].value if isinstance(n.args[1], ast.Constant) else None
        if member not in MEMBERS:
            continue
        #: ★ 判据：官方签名第 0 参是 `Object` ⇒ 该调用点**应当**被扫出来
        obj = S.arg_is_object(member, 0)
        print("    L%-5d %-56s 签名第 0 参是 Object? **%s**"
              % (n.lineno, ast.unparse(n)[:56], obj))
        if obj:
            hits.append(n.lineno)

    print()
    if hits:
        print("  ✓ **命中 %d 处**（L%s）⇒ 判据**抓得到**目标形态" % (len(hits), ", ".join(map(str, hits))))
        print("  ⇒ ★ 因此当前仓库上的「0 处」是**真的干净**，不是「没扫到」")
        return 0
    print("  ✗ **命中 0 处** ⇒ 判据**没生效** ⇒ 「0 处」这个结论**不成立**（事实 62）")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
