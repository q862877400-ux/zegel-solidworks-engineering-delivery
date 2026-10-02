"""钉住「查残留模态框」**只有一个实现** —— 不许再抄。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_modal_dialogs_single_source.py
# 定位:   轮 148 查出 `tools/` 下 **21 个文件**各抄了一份 `modal_dialogs`，
#         **每份都带 `IsWindowVisible` 过滤** ⇒ 实测 SolidWorks 的 **49 个顶层窗口里
#         只有 1 个可见** ⇒ 每份都**漏检 48/49（约 98%）**。
#         轮 149 把 21 份**全部**改成委托共享实现。本文件**钉住那次迁移**。
# 官方依据: 不适用（本项目内部纪律）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

TOOLS = REPO_ROOT / "tools"
#: ⚠ **唯一豁免**：这个探针**本身**要用可见性做对照实验（它的 `main_windows()` 需要它），
#: 而它**不**在收尾路径上。
EXEMPT = {"probe_window_vs_graphics.py"}


def _func_src(path: Path, name: str):
    """取某个顶层函数的源码片段（找不到返回 `None`）。"""
    src = path.read_text(encoding="utf-8", errors="replace")
    if "def %s(" % name not in src:
        return None
    i = src.index("def %s(" % name)
    j = len(src)
    for m in re.finditer(r"(?m)^(def |class |if __name__)", src[i + 1:]):
        j = i + 1 + m.start()
        break
    return src[i:j]


def test_every_modal_dialogs_delegates_to_the_shared_impl():
    """@brief ★★ 每个 `modal_dialogs` 都必须**委托** `residual_dialogs`。

    ⚠ 自抄一份的代价：**口径会跟着抄错**（21 份里每份都带着同一个 `IsWindowVisible`）。
    """
    bad = []
    for p in sorted(TOOLS.glob("*.py")):
        body = _func_src(p, "modal_dialogs")
        if body is None:
            continue
        if "residual_dialogs" not in body:
            bad.append(p.name)
    assert not bad, ("这些文件的 `modal_dialogs` 没有委托共享实现 —— "
                     "**不许再抄**（口径会跟着抄错）：\n  " + "\n  ".join(bad))


def test_no_modal_dialogs_filters_on_visibility():
    """@brief ★★★ `modal_dialogs` 里**不许**再出现 `IsWindowVisible`。

    ⚑ 实测：那个过滤让 21 份抄本**都只扫到 1 个窗口**（实际 49 个）⇒ **漏检 98%**。
    """
    bad = []
    for p in sorted(TOOLS.glob("*.py")):
        if p.name in EXEMPT:
            continue
        body = _func_src(p, "modal_dialogs")
        if body is None:
            continue
        if "IsWindowVisible" in body:
            bad.append(p.name)
    assert not bad, ("这些 `modal_dialogs` 还在用可见性过滤（会漏检约 98%）：\n  "
                     + "\n  ".join(bad))


def test_shared_impl_returns_the_scanned_total():
    """@brief ★★ 共享实现必须返回 `(dialogs, all_windows)` —— 空列表才可解释。"""
    import sw_connect
    import inspect
    sig_ok = "all_windows" in (inspect.getdoc(sw_connect.residual_dialogs) or "")
    assert sig_ok, "docstring 要写明返回总数及其用途"
    out = sw_connect.residual_dialogs(0)      #: PID 0 ⇒ 一定扫不到，但形状要对
    assert isinstance(out, tuple) and len(out) == 2


def test_the_exempt_probe_is_the_only_one_left():
    """@brief ★ 豁免名单要**小而明确** —— 目前只该有那一个对照实验探针。"""
    assert EXEMPT == {"probe_window_vs_graphics.py"}, "豁免名单变了就要说明理由"
