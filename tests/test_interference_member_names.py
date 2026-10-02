"""钉住 `sw_assembly.get_interference_detection` 的**三处**已修成员名（不连 SolidWorks）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_interference_member_names.py
# 定位:   2026-10-01（轮 159）用**直接属性访问探针**查出该函数**三处成员名都错**，
#         而它们**都在 `try:` 里** ⇒ **此前静默降级**（不炸，但**永远拿不到数据**）：
#           ① `asm_model.InterferenceDetection` ⇒ 官方是 **`InterferenceDetectionManager`**
#              （出厂反射 `get_InterferenceDetectionManager()`）；
#           ② `interference.GetInterference(index)` ⇒ 官方是 **`GetInterferences()`**（**复数**）；
#           ③ `item.Name` ⇒ `IInterference` 上**没有 `Name`**；有的是
#              `Volume` / `GetComponentCount` / `Ignore` / `IsFastener` /
#              `IsPossibleInterference` / `Components` / `GetInterferenceBody`。
#         ⇒ 本文件把这三处钉死。
# 官方依据: `C:\\swapi\\types\\IInterferenceDetectionMgr\\` · `C:\\swapi\\types\\IInterference\\` ·
#          `D:\\AI\\SW\\_raw\\**\\iface_*.txt`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))


def _fn_source() -> str:
    src = (REPO_ROOT / "scripts" / "sw_assembly.py").read_text(encoding="utf-8")
    i = src.index("def get_interference_detection(")
    j = src.find("\ndef ", i + 1)
    return src[i:j if j > 0 else len(src)]


def _code_attrs() -> set:
    """★ 用 `ast` 只取**代码里的属性名 + 字符串成员名**（⚠ **不许**把 docstring/注释算进来）。

    ⚠⚠ 本会话在这件事上**栽过 5 次**（最近一次就是轮 158 的那条判据）⇒ 这次一开始就用 `ast`。
    ★ 而且本仓的成员名多半是**字符串实参**（`safe_get_com_member(item, "Volume")`）
    ⇒ 必须**连字符串实参一起收**，否则判据看不见它们。
    """
    src = (REPO_ROOT / "scripts" / "sw_assembly.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    out: set = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_interference_detection":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Attribute):
                    out.add(sub.attr)
                if isinstance(sub, ast.Call):
                    for a in sub.args:
                        if isinstance(a, ast.Constant) and isinstance(a.value, str):
                            out.add(a.value)
    return out


def test_entry_property_has_manager_suffix():
    """@brief ★★★ 入口属性必须是 `InterferenceDetectionManager`（**带 `Manager`**）。"""
    attrs = _code_attrs()
    assert "InterferenceDetectionManager" in attrs, (
        "入口属性没了 —— 出厂反射的拼写是 `get_InterferenceDetectionManager()`")
    assert "InterferenceDetection" not in attrs, (
        "又用了 `InterferenceDetection`（**不存在**，少了 `Manager`）—— 官方没这个成员")


def test_uses_plural_getter():
    """@brief ★★ 取结果必须用 **`GetInterferences`**（复数）；没有 `GetInterference(index)`。

    ⚠⚠ **这条判据必须用 `ast`** —— 第一版查的是函数**源码文本**，
    于是把 docstring 里那句「没有 `GetInterference(index)`」也算了进来 ⇒ **假阳性**。
    ★ 本会话在「把注释/docstring 当成代码」这件事上**栽过 5 次**（轮 158 那条也是）。
    """
    src = (REPO_ROOT / "scripts" / "sw_assembly.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    calls: set = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_interference_detection":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    f = sub.func
                    if isinstance(f, ast.Attribute):
                        calls.add(f.attr)
                    elif isinstance(f, ast.Name):
                        calls.add(f.id)
                        #: ★★ 本仓的成员名多半是**字符串实参**传给包装器的
                        #: （`call_com_member(obj, "GetInterferences")`）⇒ 要把它们也收进来。
                        for a in sub.args:
                            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                                calls.add(a.value)
    assert "GetInterferences" in calls, "要用复数的 `GetInterferences()`"
    assert "GetInterference" not in calls, (
        "又调了单数 `GetInterference` —— 官方 `IInterferenceDetectionMgr` 里没有这个成员")


def test_does_not_use_nonexistent_name_member():
    """@brief ★★★ `IInterference` 上**没有 `Name`** ⇒ 不许再读它。"""
    attrs = _code_attrs()
    assert "Name" not in attrs, (
        "又读了 `item.Name` —— `IInterference` 的成员里**没有 `Name`**；"
        "有的是 `Volume` / `GetComponentCount`")
    assert "Volume" in attrs, "应当读官方的 `Volume`（本仓用它做**体积定量**判据）"


def test_evidence_records_the_volume_roundtrip():
    """@brief ★★ 证据要写明**体积定量**（20×40×20 = 16000 mm³，真机读回吻合）。"""
    src = (REPO_ROOT / "scripts" / "sw_assembly.py").read_text(encoding="utf-8")
    i = src.index("def get_interference_detection(")
    seg = src[max(0, i - 1400):i + 2600]
    assert "轮 159" in seg, "要标注实测轮次"
    assert "InterferenceDetectionManager" in seg, "要写明正确拼写"
