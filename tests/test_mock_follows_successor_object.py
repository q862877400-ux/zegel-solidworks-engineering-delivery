"""★ 测「mock 落后于换代」的第 6 种形态：★ **对象归属变了**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `tests/test_sw_delivery.py`（★ 改的就是它）· `output/_full_baseline_failures.txt`
# 定位:   ★ 轮 113 拿到真基线 **25 failed / 1711 passed** ⇒ ★★ 轮 114–115 **逐组修** ✓
#   ★★★ **本轮修的是一族 9 条**（★ `tests/test_sw_delivery.py`）——
#     ★ **真机读数**：★ 从 **9 failed / 8 passed** ⇒ ★★ **17 passed** ✓
#   ★★★★ **而修的是**四个结构性缺口**（★ 全是"mock 没跟上真实契约"）**：
#     ★ **① `FakePackAndGo` 缺 `_oleobj_`** ⇒
#       ★ 判据（★ `sw_delivery.py` L774 逐字）`hasattr(package, "_oleobj_")` ⇒
#       ★★ **实测报「★ 类型 FakePackAndGo —— 多半是 bound method」** ✓
#     ★ **② `FakePackAndGo` 缺 `SetSaveToName2`** ⇒
#       ★ 官方「**Obsolete. Superseded by `IPackAndGo::SetSaveToName2`**」⇒
#       ★★ **实报 `'FakePackAndGo' object has no attribute 'SetSaveToName2'`** ✓
#     ★ **③ `FakeComponent` 缺 `GetExcludeFromBOM2`**（★ 轮 114 修的）✓
#     ★★ **④ `FakeDependencyAssembly` 的依赖挂在**错的对象**上** —— ★★ **本轮首次出现这一形态**：
#       ★ 官方「**Obsolete. Superseded by `IModelDocExtension::GetDependencies`**」⇒
#       ★★ 旧的在 **`model`** 上（★ 3 参）、★ 新的在 **`model.Extension`** 上（★ 5 参）⇒
#       ★★★ **⇒ fake 装了 `GetDependencies2` ⇒ 实现读不到它**
#         ⇒ `missing = []` ⇒ **原生路"成功"** ⇒ **而测试期望的 `pilot` / `blocked` 分支没走到** ✓
#   ★★★★★ **可复用判据**：★★★ **换代时**"对象归属"也会变**** ——
#     ★ 旧的在 `model` 上、★ 新的在 `model.Extension` 上 ⇒
#     ★★ **⇒ mock 光改名字不够、★ 还要把它挂到**对的对象**上** ✓
#     ★★★ **⇒ 而"读不到它"的表现是**沉默的****（★ `missing = []`、★ **没有报错**）——
#       它看起来像"依赖本来就为空" ✓（★ 与**事实 40**同族）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
T = REPO / "tests" / "test_sw_delivery.py"


def test_the_four_structural_gaps_are_filled() -> None:
    """★★★ 核心断言：★ 那**四个**结构特征都在 fake 里 ✓"""
    t = T.read_text(encoding="utf-8", errors="replace")
    for need, why in (("self._oleobj_", "COM 对象的结构特征（判据读它）"),
                      ("def SetSaveToName2", "后继成员（官方 Superseded by）"),
                      ("GetExcludeFromBOM2", "后继成员（官方 Superseded by）"),
                      ("self.Extension.GetDependencies", "后继挂到 Extension 上")):
        assert need in t, "★ fake 里少了 `%s`（★ %s）" % (need, why)


def test_the_successor_is_hung_on_the_right_object() -> None:
    """★★★★ 核心断言：★ `GetDependencies` 挂在 **`Extension`** 上、★ 不是 model 上 ✓

    ★★ **为什么**：★ 实现在 `sw_delivery.py` 走的是
      ★ `ext.GetDependencies(False, True, False, False, False)`（★ 5 参）⇒
      ★★ **⇒ 挂在 model 上时**实现读不到**、★ 而**不报错**（★ 表现为 `missing = []`）✓
    """
    t = T.read_text(encoding="utf-8", errors="replace")
    assert "self.Extension.GetDependencies = " in t, (
        "★ `GetDependencies` 没挂到 `Extension` 上 ⇒ 实现读不到")
    #: ★★ 而**旧的**那一份也留着（★ 两代都留、★ 与其它几处同办）✓
    assert "def GetDependencies2" in t, "★ 旧入口被删了（★ 应当两代都留）"


def test_negative_case_implementation_still_uses_the_successor() -> None:
    """★★★ **负例 · 实现那边也要核查**：★ `sw_delivery.py` **确实**在走后继 ✓

    ★★ 判据：★ 实现的调用形态必须是 `"GetDependencies"`（★ 在 ext 上）⇒
      ★★★ **若哪天实现退回旧的、★ 本测试会红** ✓
    """
    src = (REPO / "scripts" / "sw_delivery.py").read_text(encoding="utf-8", errors="replace")
    assert '"GetDependencies"' in src, "★ 实现不再走后继 `GetDependencies` 了"
    assert '"SetSaveToName2"' in src or "package.SetSaveToName2(" in src, (
        "★ 实现不再走后继 `SetSaveToName2` 了")
    #: ★★ 而**旧的入口不该被调**（★ 只许出现在注释/字符串里）✓
    code = src
    assert not re.search(r'"GetDependencies2"\s*,', code), (
        "★ 实现里出现了 `get_com_member(…, \"GetDependencies2\", …)` 形态 ⇒ 退回旧的了")


def test_negative_case_the_file_is_green() -> None:
    """★★★★ **负例 · 用 `pytest` 真的跑一遍**（★ 文本判据证明不了"测试真的过"）✓"""
    import subprocess
    import sys
    p = subprocess.run([sys.executable, "-m", "pytest", "tests/test_sw_delivery.py", "-q"],
                       cwd=str(REPO), capture_output=True)
    out = (p.stdout or b"").decode("utf-8", "replace") + \
          (p.stderr or b"").decode("utf-8", "replace")
    assert p.returncode == 0, "★ `test_sw_delivery.py` 还是红的：%s" % out[-500:]
    assert " failed" not in out, "★ 有 failed：%s" % out[-300:]
    #: ★★ 而**成功条数**要对（★ 17 条）—— ★ 变了就说明有人加了/删了测试 ✓
    m = re.search(r"(\d+) passed", out)
    assert m and int(m.group(1)) == 17, "★ 通过条数不是 17：%r" % out[-200:]
