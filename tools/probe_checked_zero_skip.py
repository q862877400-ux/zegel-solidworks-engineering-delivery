r"""@brief 探针：复现「反射转储在、但**本仓库模块一个都解析不出**」时，
`check_signature_audit_freshness` 是 `SKIP` 还是 `FAIL`。

## 为什么探（2026-10-01 轮 84，Spec Kit `008`）
轮 83 系统排查 SKIP 语义时，**如实记下一处未查证**：
```
if checked == 0:
    print("**SKIP** —— 一个模块都没能实跑（便携性守卫）")
    return 0
```
⚠ **轮 55 首跑就撞上过**：`resolve_module` 的解析写法不对 ⇒ **6/6 全报「跑不了」⇒ 误 SKIP**
（当时靠人发现并修了路径，注释留在 `resolve_module` 的 docstring 里）。

## 判据（照 007 的规则）
> **被读的那个东西，是本仓库自己的产物，还是本机/外部才有的数据源？**
* `refs`（反射转储）为空 ⇒ **外部数据源缺** ⇒ SKIP 正确（L238 已守）；
* `refs` **非空**却 `checked == 0` ⇒ 表里的模块是**本仓库自己的 `.py`**，
  一个都解析不出 = **解析坏了**（或仓库残缺）⇒ **必须 FAIL**。

## 复现手法
`--repo` 指向一个**空临时目录**（模块全解析不出）+ `--raw` 指向**真实反射转储**
⇒ 逼出 `refs` 非空、`checked == 0` 那条路径。**不改任何仓库文件。**

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_checked_zero_skip.py
# 定位:   为 Spec Kit `008` 取证（「反射在、模块全解析不出」到底是便携性还是故障）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
REPO = Path(r"" + _ROOT_S + r"")
GATE = REPO / "scripts" / "check_signature_audit_freshness.py"
sys.stdout.reconfigure(encoding="utf-8")


def _default_raw() -> str:
    """从源码读 `RAW` 的默认值并**取出真正的路径**（**不猜**）。

    ⚠ 第一版直接把源码文本（`Path(r"D:\\AI\\SW\\_raw")`）当路径传进去 ⇒
    门禁判「找不到反射文件」⇒ 走的是**另一条** SKIP 分支（那是合法的便携性守卫），
    **根本没测到 `checked == 0`**。★ 又一次「探针本身要贴合实际形态」。
    """
    text = GATE.read_text(encoding="utf-8")
    m = re.search(r"^RAW\s*=\s*(.+)$", text, re.M)
    if not m:
        return "?"
    raw = m.group(1).strip()
    inner = re.search(r"""["']([^"']+)["']""", raw)  # 取引号里的真路径
    if inner:
        return inner.group(1)
    return raw  # 兜底：不是字面量就原样传（可能是别的表达式）


def _run(args: list) -> tuple:
    p = subprocess.run(
        [sys.executable, str(GATE)] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO),
        stdin=subprocess.DEVNULL,
    )
    return p.returncode, (p.stdout or "")


def main() -> int:
    print("══ `check_signature_audit_freshness` 的 `checked == 0` 分支 ══")
    print("  `RAW` 源码默认值: %s" % _default_raw())
    print()

    print("── ① 正例：真仓库 + 真反射 ⇒ 应 exit 0 且 checked = 6 ──")
    rc, out = _run([])
    for l in out.splitlines():
        if "反射文件" in l or "[PASS]" in l or "[FAIL]" in l:
            print("     %s" % l.strip()[:96])
    print("     ⇒ exit=%d" % rc)

    print()
    print("── ② ★ 关键：**空仓库** + 真反射 ⇒ refs 非空、checked = 0 ──")
    empty = Path(tempfile.mkdtemp()) / "emptyrepo"
    empty.mkdir()
    rc2, out2 = _run(["--repo", str(empty), "--raw", _default_raw()])
    print(
        "     反射文件行: %s"
        % next((l.strip() for l in out2.splitlines() if "反射文件" in l), "（无）")[:96]
    )
    for l in out2.splitlines():
        if "SKIP" in l or "[FAIL]" in l or "跑不了" in l:
            print("     %s" % l.strip()[:96])
    print("     ⇒ exit=%d  ← **当前是多少？该是多少？**" % rc2)
    shutil.rmtree(empty.parent, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
