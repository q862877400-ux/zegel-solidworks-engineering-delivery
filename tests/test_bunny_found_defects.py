"""★ 两处**由 Bunny 扇出如实上报、经主线核实**的修复的回归测试。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_hole_features.py` 的 `create_semicircular_slot`（返回字典重复键）·
#         `mcp-server/register_capabilities.py` 的 `resolve_study_options`（family 静默默认）
# 定位:   ★ 这两处**都不是我发现的**，而是 Bunny 扇出在**做别的判读时只读发现**并如实上报的
#         （★ 它不自己改 ⇒ 交主线拍板）⇒ ★ 本测试把它们**钉住**，防回归 ✓
# 官方依据: 不适用（本仓自身代码的回归判据）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402


def test_no_duplicate_dict_keys_in_hole_features():
    """★★ 回归：`sw_hole_features.py` 里**不许再有重复的字典字面量键**。

    ★ 原缺陷：`create_semicircular_slot` 的返回字典里 `start_mm` / `end_mm` / `width_mm` /
      `depth_mm` **各写两遍**（后者覆盖前者）⇒ ★ 输出碰巧对，但**死代码会误导读者**
      （看着像"以 `_mm` 命名却存米"），且任何 linter 都会报 ✓
    ★ 判据用 AST 逐个数（★ 不靠 grep —— 字符串里的同名文本不该算）。
    """
    src = (ROOT / "scripts" / "sw_hole_features.py").read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    bad = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = [k.value for k in node.keys if isinstance(k, ast.Constant)
                and isinstance(k.value, str)]
        dup = sorted({k for k in keys if keys.count(k) > 1})
        if dup:
            bad.append((node.lineno, dup))
    assert not bad, "★ 仍有重复的字典键: %r" % (bad,)


def test_resolve_study_options_refuses_to_guess_family():
    """★★ 回归：`options` 注入键**拿不到 `family` 就必须报错**，不许静默默认成静态族。

    ★ 原缺陷：第一版把 `family` 缺省成 `ICWStaticStudyOptions` —— 而频率/屈曲那两个原始函数
      **形参里没有 `family`**（各自硬编码自己的族）⇒ ★ 缺省值会把**别的族的选项注成静态选项对象**
      （★ 事实 36 那一族：对象错了表现为"什么都没发生"）✓
    """

    class _P:                       #: ★ 假 params：只有 study_name，**没有 family**
        study_name = ""

    try:
        rc.resolve_study_options(_P())
    except RuntimeError as exc:
        assert "family" in str(exc), str(exc)
    else:
        raise AssertionError("★ 没报错 ⇒ 它又在替调用方猜选项族了")
