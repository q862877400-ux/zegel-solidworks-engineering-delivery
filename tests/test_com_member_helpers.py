"""钉住 `sw_connect` 三个成员帮助函数的**用法与导入一致**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_com_member_helpers.py
# 定位:   轮 145 把 24 处「故意要调」的零参调用从 `get_com_member` 迁到
#         **`call_com_member`**（名字即意图）。⚠ 迁移时**漏了 import**，
#         而「模块能 import 成功」**掩盖**了它（`NameError` 只在调用时才出现）
#         ⇒ ★ 本文件把那条**钉住**。
# 官方依据: 不适用（本项目内部纪律）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

HELPERS = ("get_com_member", "get_com_member_raw", "call_com_member")

#: ★★ 导入形态：`from sw_connect import …` / `from .sw_connect import …`，
#:   ★ **含括号多行那种**（`from sw_connect import (\n  a,\n  b,\n)`）✓
_IMPORT_RE = re.compile(r"from\s+[\.\w]*sw_connect\s+import\s+(\([^)]*\)|[^\n]*)", re.S)


def _source_imports_helper(src: str, helper: str) -> bool:
    """★ **纯函数**：这段源码里有没有把 `helper` 导进来 —— ★ **模块级与函数内都算** ✓

    ★★ 2026-10-07（接手轮 · 规格 214 T-214-05）**为什么要加它**：
      ★ 原判据只用 `hasattr(mod, helper)` ⇒ ★★ **看不见"函数内导入"** ✗，
      ★ 而"函数内导入"**正是本仓既有模式**（详见下面 `_modules_using` 上方那段）✓
      ★ 实测假阳性 **3 个**（`sw_applicability` / `sw_macro` / `sw_preference_guard`）——
        它们都在各自函数里写了 `from sw_connect import get_com_member`，★ **调用是好的** ✓
    ⚠ 判据**没有被放宽**：★ 一个"只调用、哪儿都没导入"的模块，★ **两条都不过 ⇒ 仍然被抓**
      （★ 见本文件的负例 `test_negative_no_import_anywhere_is_still_caught`）✓
    """
    for m in _IMPORT_RE.finditer(src):
        if re.search(r"(?<![\w])%s(?![\w])" % re.escape(helper), m.group(1)):
            return True
    return False


def _modules_using(helper: str) -> list:
    """`scripts/` 下**源码里用到** `helper(` 的模块名。"""
    out = []
    for p in sorted((REPO_ROOT / "scripts").glob("sw_*.py")):
        src = p.read_text(encoding="utf-8", errors="replace")
        #: 只看**调用形态**（`helper(`），且排除它自己那个文件
        if re.search(r"(?<![\w.])%s\s*\(" % helper, src) and p.stem != "sw_connect":
            out.append(p.stem)
    return out


def test_every_helper_user_can_actually_import_it():
    """@brief ★★★ 用到某个帮助函数 ⇒ **那个名字必须真的在模块里**。

    ⚠⚠ 这条判据的由来：轮 145 迁移时**改了调用、漏了 import**，
    而 `import scripts.sw_view` **成功**（`NameError` 要到调用时才炸）
    ⇒ 只测"能不能导入"**测不出**这个问题。本判据测的是 **`hasattr`**。
    """
    import importlib
    problems = []
    for helper in HELPERS:
        for stem in _modules_using(helper):
            mod = None
            for pre in ("scripts.", ""):
                try:
                    mod = importlib.import_module(pre + stem)
                    break
                except Exception:      # noqa: BLE001
                    continue
            if mod is None:
                problems.append("%s: 导入失败" % stem)
                continue
            if hasattr(mod, helper):
                continue
            #: ★★ 2026-10-07（T-214-05）：`hasattr` **看不见函数内导入**（★ 本仓既有模式）
            #:   ⇒ ★ 再查**源码**：模块级**或**函数内把该名字导进来都算「能解析」✓
            src = (REPO_ROOT / "scripts" / (stem + ".py")).read_text(
                encoding="utf-8", errors="replace")
            if _source_imports_helper(src, helper):
                continue
            problems.append(
                "%s 用了 `%s(` 却没有这个名字（★ 模块级与函数内**两处都没有导入**）" % (stem, helper))
    assert not problems, "调用与导入不一致：\n  " + "\n  ".join(problems)


def test_negative_no_import_anywhere_is_still_caught() -> None:
    """★★ **负例**（事实 62）：★ 「只调用、哪儿都没导入」⇒ ★ **判据必须仍然抓得到** ✓

    ★ 本判据 2026-10-07 被加宽过一次（接受**函数内导入**）⇒ ★ 这条负例就是那次加宽的**守卫**：
      ★ 加宽**不许**宽到"完全没导入也算能解析" ✓
    """
    call_only = "def f(doc):\n    return get_com_member(doc, 'GetType')\n"
    assert not _source_imports_helper(call_only, "get_com_member"), (
        "★ 加宽后把「完全没导入」也认了 ⇒ 判据失去意义（轮 145 那个 bug 会再也抓不到）")
    #: ★ 正例三种形态都要认：模块级 / 函数内 / **括号多行**
    assert _source_imports_helper("from sw_connect import get_com_member\n", "get_com_member")
    assert _source_imports_helper(
        "def f():\n    from sw_connect import get_com_member\n", "get_com_member")
    assert _source_imports_helper(
        "from sw_connect import (\n    get_com_member,\n    out_i4,\n)\n", "get_com_member")
    #: ★ 也认相对导入（本仓有 `from .sw_connect import …` 那种写法）✓
    assert _source_imports_helper(
        "def f():\n    from .sw_connect import call_com_member\n", "call_com_member")


def test_call_com_member_exists_and_is_documented():
    """@brief ★★ `call_com_member` 必须存在，且 docstring 写明它是"名字即意图"。"""
    import sw_connect
    assert hasattr(sw_connect, "call_com_member")
    doc = inspect.getdoc(sw_connect.call_com_member) or ""
    assert "就是去调它" in doc, "要写明它是「就是去调它」"
    assert "get_com_member_raw" in doc, "要指向「只取不调」那个替代"


def test_call_com_member_behaves_like_get_com_member():
    """@brief ★ 行为完全相同（它是**命名**，不是新语义）—— 免得两处走偏。"""

    class _O:
        def __init__(self):
            self.n = 0

        def DoIt(self):
            self.n += 1
            return "done"

    a, b = _O(), _O()
    import sw_connect
    assert sw_connect.call_com_member(a, "DoIt") == sw_connect.get_com_member(b, "DoIt")
    assert a.n == b.n == 1


#: ⚠⚠ **被撤掉的一条判据（轮 145，如实留档）**
#
# 我原本想钉住「反射里有**零参重载**的方法，不许再用 `get_com_member`」
# （理由是那个调用**会真的执行**它）。**两版都失败**：
# ```
# 第一版用**名字前缀**（Insert* / Run* / Select* / Load* …）
#   ⇒ 立刻 5 个假阳性：`SelectionManager` / `LoadsAndRestraintsManager` **是属性**
# 第二版改用**反射零参重载**（结构，更严）
#   ⇒ 它把**所有只读 getter** 也报了（GetTitle / GetName / GetCostingManager …）
# ```
# ⇒ ★★ **根因**：区分「getter」与「改东西的」**需要语义**，而**结构判不出来**
#   （事实 74 那一族的**第 6 次**）。
# ⇒ ★ **结论**：那 24 处从 `get_com_member` 迁到 `call_com_member` 是一次
#   **逐条读过之后的判断**（轮 144/145 各读了 8 处 + 16 处），
#   **不是**一条可以机械校验的规则 ⇒ **不设这条判据**。
#   ⚠ 留下的只有两条**结构性**的（下面那两个测试）：**导入一致** 与 **帮助函数行为**。
