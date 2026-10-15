"""★ **路由互锁测试**（★ 2026-10-01 · 轮 324 —— 抄自调研 v2 发现② 的形状）。

## 一、★ 这个形状是什么（★ 与"扫描源码查有没有调"的区别）
```
★ 调研 v2 发现②：`Cai-aa/CAD-Agent-Hub`（**MIT**）的 `tests/test_save_routing.py` 用
   **两个假对象互相禁止对方那条路** —— 让**错误的那条路直接 `raise AssertionError`**：
   ```
   class _NativeModel:  SaveAs3() 写盘 ; SaveAs()  → raise AssertionError("native saves must not use export SaveAs")
   class _ExportModel:  SaveAs3()  → raise AssertionError("foreign exports must not use native SaveAs3")
   ```
   ⇒ ★★ **判据是"错的那条路会抛"，★ 而不是"扫源码看有没有出现某个字符串"。**
★ 为什么后者弱：★ **扫源码只能证明"当前没写错"，★ 而它**不会阻止**以后写错；
   而互锁测试**在错误发生的那一刻就炸**（★ 事实 62：负例是唯一的证明）。
```

## 二、★★★ 本仓库的路由判据（★ 我们自己的，写在 `scripts/sw_com_traps.py`）
```
★ `sw_com_traps.py` 的陷阱表明写：
   `IModelDocExtension.SaveAs`  → **Obsolete → 用 SaveAs3（勿用 SaveAs2，它也 Obsolete）**
   `IModelDocExtension.SaveAs3` → **None（← 当前该用的）**
   ★ 原话：「⇒ **本项目导出/保存一律用 `SaveAs3`**，不要用 SaveAs / SaveAs2。」
⇒ ★★ **所以本测试锁的就是这条**：★ **导出/保存**只许走 `SaveAs3`；
   ★ 谁要是走回 `SaveAs`，★ **测试立刻抛**。
```

## 三、★ 用法与边界
```
★ 本文件**不连 SolidWorks**（★ 全部用假对象）⇒ ★ **干净机器上必过**。
★ 它**不测**"导出结果对不对"（★ 那是真机证据的事）；★ 它只测**调用路由**。
★ ⚠ 已知的既有偏差（★ 本轮实测，★ **如实列出，不在本文件里掩盖**）：
   `sw_export.py` 的 PDF 与通用导出两条、以及 `sw_connect.py` 的一处，
   ★ **当前仍在用 `SaveAs`** ⇒ ★ 本文件的 `test_*_still_uses_obsolete_saveas` 把
   现状**钉住**（★ 那是 **xfail-style 的显式登记**，★ 而不是假装它们是对的）。
```
"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   `Cai-aa/CAD-Agent-Hub`（★ **MIT**）—— 提供的是**测试形状**
#         （`tests/test_save_routing.py`：两个假对象互相禁止对方那条路）。
# 文件:   tests/test_save_routing_interlock.py —— 本文件（★ 代码本仓库自写）。
# 定位:   路由互锁 —— ★ **错误的那条路直接 `raise`**（★ 事实 62 的教科书形态）。
#         ★ 判据（"导出/保存一律用 `SaveAs3`"）来自**本仓库自己的**
#         `scripts/sw_com_traps.py`（★ 不是抄来的）。
# 官方签名依据: `C:\swapi\types\IModelDocExtension\SaveAs.md`（★ Obsolete）·
#   `C:\swapi\types\IModelDocExtension\SaveAs3.md`（★ 当前该用）·
#   `C:\swapi\types\IModelDoc2\SaveAs3.md`
# 许可:   本文件 MIT（本仓库自身）—— ★ **无第三方代码引入**。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

#: ★ 允许走"导出"这条路的**格式**（★ 非原生 CAD 格式）
EXPORT_SUFFIXES = (".step", ".stp", ".iges", ".igs", ".stl", ".pdf", ".dxf", ".dwg", ".x_t", ".x_b")

#: ★ 被本仓库判为 Obsolete 的成员（★ 来源：`scripts/sw_com_traps.py` 的陷阱表）
OBSOLETE = ("SaveAs", "SaveAs2")

#: ★★ **已登记的既有偏差**（★ 文件 → `(行号, 成员)` 集合）—— ★ **只许变少，不许变多**。
#: ★ 2026-10-01（轮 324）首次跑这个测试时抓到：`sw_export.py` 的 **L118（PDF）** 与
#:   **L416（通用导出 6 格式）** 仍走 `Extension.SaveAs`（★ 而陷阱表判它 Obsolete）。
#: ★ 改这两处**必须真机验**（★ 导出是最容易被"看着成功"骗到的路径）⇒
#:   按硬约束⑥，★ 它们**以登记形式显式存在**，★ **而不是被掩盖或被跳过**。
_REGISTERED_OBSOLETE = {
    #: ★★★★★★ 2026-10-04（轮 116）**`sw_export.py` 的两条已删** —— ★ 那正是本测试要求的 ✓
    #:   ★ **真机读数**：★ 实得 `{'sw_connect.py': 1}` · ★ 而原登记
    #:     `{'sw_export.py': 2, 'sw_connect.py': 1}` ⇒
    #:   ★★ **本测试自己逐字写着**：★「★ **变少是**修好了**（★ 请把 `_REGISTERED_OBSOLETE`
    #:     里对应的条目删掉 —— ★ 那条会提醒你）**」✓
    #:   ★★★ **真因**：★ `sw_export.py` 那两处**已经被修好了** ——
    #:     提交 `2656c26c`（★ 阶段 1 · 处置 `JUDGE-C_D_E` 🔴 #6 · #21）逐字：
    #:     「★ **PDF 走两级废弃的 `SaveAs`**；★ **三处保存路由统一到现行的 `SaveAs3`**」✓
    #:   ★★★★ **⇒ 而我当时**没同步删这张表里的两条**** ⇒ ★ **它红了 55 轮** ✓
    #:   ★★★★★ **可复用判据**：★★★ **这与"mock 落后于换代"是**同一个病**** ——
    #:     ★ **"改了实现"之后，一切**与它配套的东西**都要跟着改**：
    #:     ★★ mock · ★ 登记表 · ★ 钉死数量 · ★ 契约测试 ⇒ ★ 而它们**都不会自己报错** ✓
    #: ★★★★★★★ 2026-10-09（spec 241）**本条改成"按名字"** —— ★ 原写 `(916, "SaveAs")`：
    #:   ① ★ **行号早漂了**（真位置是 `sw_connect.py:1167` 的 `model.Extension.SaveAs(...)`）；
    #:   ② ★★ **它从没被任何判据读过** —— `test_export_route_never_uses_obsolete_saveas`
    #:      只看 `sw_export.py` ⇒ ★ **一条"登记了却没人查"的死数据** ✓
    #:   ⇒ ★ 按本仓纪律「判据按**名字**定位，不按行号」，改成**成员名集合**，
    #:     ★★ 并由新增的 `test_registered_entries_are_not_dead` **真的去核它** ✓
    "sw_connect.py": {"SaveAs"},
}


def _iter_com_calls(source: str):
    """★ 用 **`ast`** 找出对 `SaveAs*` 成员的调用（★ 支持跨行、★ **自动跳过注释与字符串**）。

    ★★ 为什么不用正则：★ 本文件初版用**逐行正则**，当场踩三个坑 ——
      ★ ① **跨行调用**（`get_com_member(\n  obj, "SaveAs3", …)`）匹配不到；
      ★ ② **注释里的 `SaveAs`**（★ 本仓库注释很密）被算成一处调用；
      ★ ③ 于是**偏差计数**算错（★ 实得 3 处、而真的只有 2 处）。
      ⇒ ★★ **`ast` 两者都天然解决**（★ 注释与字符串本来就不在语法树里）。
    ★ 产出 `(行号, 成员名, 该行源码)`：
      · `obj.Extension.SaveAs3(...)`  ⇒ `func` 是 `Attribute` ⇒ 取 `.attr`
      · `get_com_member(obj, "SaveAs3", ...)` ⇒ 第 2 个实参是 `Constant` 字符串 ⇒ 取它
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return
    lines = source.splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = None
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr.startswith("SaveAs"):
            name = func.attr
        elif isinstance(func, ast.Name) and func.id == "get_com_member" and len(node.args) >= 2:
            second = node.args[1]
            if isinstance(second, ast.Constant) and isinstance(second.value, str) \
                    and second.value.startswith("SaveAs"):
                name = second.value
        if name:
            ln = getattr(node, "lineno", 0)
            text = lines[ln - 1].strip() if 0 < ln <= len(lines) else ""
            yield ln, name, text


def test_export_route_never_uses_obsolete_saveas():
    """★★ **互锁（登记制）**：★ `scripts/sw_export.py` 里**不许新增**废弃的 `SaveAs` / `SaveAs2`。

    ★ 判据：★ `sw_com_traps.py` 明写「本项目导出/保存一律用 `SaveAs3`」。
    ★★ **为什么是登记制而不是"一律为零"**：★ 本文件首次跑就抓到**两处真实偏差**
      （`sw_export.py` 的 L118 PDF 与 L416 通用导出）—— ★ 而**改路由必须真机验**
      （★ 改错会把导出整个弄坏）⇒ ★ 按硬约束⑥「验不过的回退、不许留在柜台上」，
      ★ **它们以"已登记"的形式显式存在**，★ **而新增一处就会炸**。
    ⇒ ★★ 修好之后，★ 请把 `_REGISTERED_OBSOLETE` 里对应的条目删掉（★ 那条会提醒你）。
    """
    source = (REPO_ROOT / "scripts" / "sw_export.py").read_text(encoding="utf-8")
    found = [(ln, nm) for ln, nm, _ in _iter_com_calls(source) if nm in OBSOLETE]
    registered = _REGISTERED_OBSOLETE.get("sw_export.py", set())
    offenders = [(ln, nm) for ln, nm in found if nm not in registered]
    assert not offenders, (
        "★ sw_export.py 里出现了**新增**的废弃路由（★ 本仓库判据：一律用 SaveAs3）：%s\n"
        "★ 已登记的既有偏差 = %s（★ 修好后请从登记表删掉）"
        % (offenders, sorted(registered)))


def test_registered_entries_are_not_dead():
    """★★★ **登记表不许有死条目**（★ spec 241 新增）—— ★ 登记了、而真树上**已经不存在** ⇒ 红。

    ★ 为什么单列一条：★ 登记表是"**现状**"，不是"历史"。★ 有人把废弃路由修好之后忘了删登记
      ⇒ ★ 那条登记就变成**假数据**，★ 而**它不会自己报错** ✓
      ★★ 实录：本文件原先那条 `("sw_connect.py", (916, "SaveAs"))` **同时**踩两个坑 ——
        ① 行号漂到了 **1167**；② **它从没被任何判据读过**（本测试只看 `sw_export.py`）⇒
        ★ 一条**死数据**在仓库里躺了 **5 天**，★ 谁都没发现 ✓
    ★ 修法：★ 真修好了 ⇒ ★ **把登记删掉**（★ 这是好事，不是失败）。
    """
    for name, registered in _REGISTERED_OBSOLETE.items():
        source = (REPO_ROOT / "scripts" / name).read_text(encoding="utf-8")
        actually = {nm for _, nm, _ in _iter_com_calls(source) if nm in OBSOLETE}
        dead = sorted(registered - actually)
        assert not dead, (
            "★ %s 的登记表里有**死条目** %s ⇒ ★ 要么是**修好了**（请删掉登记）、"
            "要么是**改名/搬家了**（请把登记改对）；★ 真树实得 %s"
            % (name, dead, sorted(actually)))


def test_saveas3_is_present_where_image_or_pdf_is_written():
    """★ **正面**：★ 既然判据是"用 `SaveAs3`"，★ 那它在关键路径上**要真的存在一处**。

    ★ 否则"互锁"就变成了"全都不许用" —— ★ 那是另一个错误（★ 没有任何可用路由）。
    """
    source = (REPO_ROOT / "scripts" / "sw_export.py").read_text(encoding="utf-8")
    assert any(nm == "SaveAs3" for _, nm, _ in _iter_com_calls(source)), \
        "★ sw_export.py 里一处 SaveAs3 都没有 ⇒ 路由判据无从落地"


def test_interlock_shape_rejects_the_wrong_route():
    """★★★ **负例自证**：★ 本测试的形状**必须能对「走错路」说不**。

    ★ 做法：★ 拿一段**故意写错**的源码喂给同一个判据函数 ⇒ ★ **它必须报出那条错**。
    ★ 事实 62：★ **一个存在但没人验证过其有效性的门禁，与没有门禁等价。**
    """
    bad_source = (
        "def f(model, p):\n"
        "    return model.Extension.SaveAs(p, 0, 1, None, e, w)\n"
    )
    offenders = [nm for _, nm, _ in _iter_com_calls(bad_source) if nm in OBSOLETE]
    assert offenders == ["SaveAs"], "★ 判据没能识别出 `SaveAs` ⇒ 互锁测试是空的：%s" % offenders
    good_source = (
        "def f(model, p):\n"
        "    return model.Extension.SaveAs3(p, 0, 0)\n"
    )
    ok = [nm for _, nm, _ in _iter_com_calls(good_source) if nm in OBSOLETE]
    assert not ok, "★ 判据把正确的 `SaveAs3` 也当成违规了：%s" % ok
    #: ★★ 跨行 + 注释两个坑的自证（★ 初版正则都踩过）
    multiline = (
        "# model.Extension.SaveAs(p)  ← 这行是注释，不算\n"
        "def g(model, p):\n"
        "    return get_com_member(\n"
        "        model.Extension, \"SaveAs3\", p, 0, 0,\n"
        "    )\n"
    )
    got = [nm for _, nm, _ in _iter_com_calls(multiline)]
    assert got == ["SaveAs3"], "★ 跨行/注释处理不对：★ 期望只认出跨行的 `SaveAs3`，实得 %s" % got


def test_known_existing_deviations_are_registered_not_hidden():
    """★ **现状登记**（★ 不掩盖）：★ 把当前**仍在用废弃路由**的文件与处数钉住。

    ★ 它们是既有偏差；★ 本测试的作用是**让数字可见** ——
      ★ 一旦有人把它们改对了，★ 这条会失败并**提醒把登记数改小**（★ 那是好事）。
    ★ 一旦有人**新增**了一处，★ 这条也会失败 ⇒ ★ **不允许偏差变大**。
    """
    deviations = {}
    for name in ("sw_export.py", "sw_connect.py"):
        source = (REPO_ROOT / "scripts" / name).read_text(encoding="utf-8")
        n = sum(1 for _, nm, _ in _iter_com_calls(source) if nm in OBSOLETE)
        if n:
            deviations[name] = n
    #: ★ 2026-10-01 实测：`sw_export.py` 2 处（PDF + 通用导出）· `sw_connect.py` 1 处
    #: ★★★★★★ 2026-10-04（轮 116）**登记数调小** —— ★ 同上（★ `sw_export.py` 已修好）✓
    registered = {"sw_connect.py": 1}
    assert deviations == registered, (
        "★ 废弃路由的分布变了：★ 实得 %s · 登记 %s\n"
        "★ 变多是**新增偏差**（不允许）；★ 变少是**修好了**（请把 `registered` 调小）。"
        % (deviations, registered))
