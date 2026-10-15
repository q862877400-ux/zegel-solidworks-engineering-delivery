"""★ **通用废弃入口互锁**（★ objective⑤ 的推广 —— 从"保存路由一处试点"扩到**全仓 + 多族**）。

## 一、★ 形状来自哪里
```
★ 调研 v2 发现②：`Cai-aa/CAD-Agent-Hub`（**MIT**）的 `tests/test_save_routing.py` 用
   **两个假对象互相禁止对方那条路** —— 让**错误的那条路直接 `raise AssertionError`**：
   ```
   class _NativeModel:  SaveAs3() 写盘 ; SaveAs()  → raise AssertionError("native saves must not use export SaveAs")
   class _ExportModel:  SaveAs3()  → raise AssertionError("foreign exports must not use native SaveAs3")
   ```
   ⇒ ★★ **判据是"错的那条路会抛"，★ 而不是"扫源码看有没有出现某个字符串"。**
★ 本仓库**已在一处试点**（`tests/test_save_routing_interlock.py`，轮 324，★ 导出路由）；
   ★★ **本文件把它推广**：★ **靶子表 = `sw_com_traps.DEPRECATED_ENTRIES`**，
     ★ **覆盖面 = 全部 `scripts/sw_*.py`**（★ 而不是单个模块）。
```

## 二、★★★ 三条判据（★ 缺一条都会瞎一半）
```
① ★ **不许新增**：★ 某个模块里出现靶子表里的**废弃入口**调用 ⇒ **炸**
   （★ 已有的以 `_REGISTERED` 显式登记 —— ★ 改路由必须真机验，★ 验不过不许留在柜台上）
② ★ **正面**：★ 后继入口（★ 该用的那个）**要在仓库里真的存在至少一处** ⇒
   ★ 否则"互锁"退化成"全都不许用"（★ 那是另一个错误：没有任何可用路由）
③ ★ **假对象互锁**：★ 在**假对象**上，★ 走**废弃**的那条路必须 **raise**；
   ★ 走**后继**的那条路必须**通** —— ★★ 这才叫"在错误发生的那一刻就炸"（事实 62）
```

## 三、★ 靶子表**只放已核过的**（★ 铁律 1 / 硬约束⑧）
```
★ 本文件的靶子不是"扫一遍官方 `Superseded by` 就全放进来" ——
   ★ 那份扫描（事实 271）出 **42 处**，抽样就看出**三类假阳性**：
     ① 后继名 == 自己（解析错）· ② **不同 arity 的不同方法** · ③ **跳代常伴随签名变化**。
   ⇒ ★★ **每条进 `DEPRECATED_ENTRIES` 前要**读两边的签名。
```

## 四、★★★ 2026-10-09（spec 241）**收口两处"看不见"**
```
★ ① **点式形态曾是盲区**：★ 原扫描只认 `get_com_member(obj, "Name", …)` 的**字面量形态**
   ⇒ ★ `asm_model.AddMate5(…)`（`func` 是 `Attribute`）**一次都收不到** ⇒
   ★★ 那是**空判据**：★ 只要换个写法（点式），互锁**读成 0 处**、照样绿 ✓
   （★ 本仓同族教训：spec 239「只看点式调用 = 空判据」—— ★ 两次方向相反、**同一个病**）
★ ② **`call_assembly_doc` 曾是盲区**：★ 它第 2 实参也是**成员名字面量**，
   ★ 而原扫描只认 `get_com_member` / `call_com_member`
   ⇒ ★ `sw_weldment.py` 走官方入口的 `call_assembly_doc(model, "CreateMate", data)`
   ★ **读不出来** ⇒ 判据② 会**假红**（"后继 `CreateMate` 一次都没被调用"）。
★ ③ **登记表按"名字 + 处数"**（★ **不按行号**）—— ★ 行号会漂移（★ 本仓纪律：
   「判据按**名字**定位，不按行号」）；★ 且**登记表不许有死条目**
   （★ 登记了却已不存在的 ⇒ 红 —— ★ 与"mock 落后于换代"**同病**）。
```
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_deprecated_entry_interlock.py
# 定位:   objective⑤ 的推广：把"双假对象互锁"从一处扩到全仓 + 多族。
# 官方依据: `sw_com_traps.DEPRECATED_ENTRIES`（★ 每条带官方 `Superseded by` 的依据）·
#   调研 v2 发现②（`Cai-aa/CAD-Agent-Hub`，MIT，★ 只读其测试形状，未抄文本）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import sw_com_traps as TRAPS  # noqa: E402

#: ★★ **已登记的既有偏差**：`模块 → {成员名: 处数}` —— ★ **计数棘轮：只许变少，不许变多**。
#: ★ 与试点文件同一纪律：★ **不许新增**；★ 已有的显式登记；★ **修好后从本表删掉**。
#: ★★ **为什么不按行号**：★ 行号**会漂移**（上面插一行就全错位）⇒ ★ 本仓纪律
#:   「判据按**名字**定位，不按行号」（★ 试点文件里那条 `(916, "SaveAs")` 就是这么烂掉的）。
#: ★ 每条都要写"为什么**留**在这里"（★ 不是"顺手登记"）。
_REGISTERED: dict[str, dict[str, int]] = {
    #: ★ `sw_assembly.py` 的 `add_mate5_checked` —— ★ **唯一**用点式形态调 `AddMate5` 的地方。
    #: ★ 留在这里的理由：★ `AddMate5` 官方 `Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]`，
    #:   ★ 而**换掉它要按 `mate_type` 分流**（★ 官方 Remarks 三条：标准/高级/机械 ⇒ `CreateMate` ·
    #:   **偏心同心** ⇒ `AddConcentricMateWithTolerance` · **柱面距离** ⇒ `AddDistanceMate`）——
    #:   ★★ 而**分流语义靠 `mate_type` 一个参数定不下来**（★ `swMateDISTANCE` 既可能是平面距离、
    #:   也可能是柱面距离）⇒ ★★ **必须真机验证**；★ 装配域 `level` 仍是 `stitched`（铁律 2）
    #:   ⇒ ★ **本轮不换**，★ 以登记形式**显式存在**。
    #:   ★★ spec 246：`sw_assembly.py` 的 `ActivateDoc2` 是 `ActivateDoc3` 的**兜底分支**
    #:     （`try: sw.ActivateDoc3(...) except: sw.ActivateDoc2(...)`）—— ★ **兜底本身就是意图**，
    #:     ★ 而 `ActivateDoc3` 已在该分支之前**被调用过** ⇒ ★ 保留登记，**不删**。
    "sw_assembly.py": {"AddMate5": 1, "ActivateDoc2": 1},
    #: ★ `sw_assembly_doc.py::add_mate` —— ★ 通用包装（`*args` 15 个直传），★ **拿不到 `mate_type` 语义**。
    #: ★ 它的 docstring **已逐字记档保留**（★ 见 `sw_assembly_doc.py` 该函数头）⇒ ★ 同上，登记不换。
    #: ★★ spec 246：`GetExplodedViewCount`（零参）⇒ 后继 `GetExplodedViewCount2(ConfigurationName)`
    #:   ★ **多一个参数** ⇒ ★ 换它要**先确定"按哪个配置数"**（★ 那是**语义决定**，不是机械替换）
    #:   ⇒ ★ 登记不换（★ 该函数头的记档已写明"我一度把传错参个数读成'取不到'"）。
    "sw_assembly_doc.py": {"AddMate5": 1, "GetExplodedViewCount": 1},
    #: ★ `sw_connect.py::save_document` 的 `model.Extension.SaveAs(...)` —— ★ **点式形态**，
    #:   ★★ 它**此前从未被任何判据看见**（★ 原扫描不认点式）⇒ ★ 本轮**新看见**，登记不换。
    #: ★ 不换的理由：★ 保存/导出路由改错会**直接坏掉写盘**（★ 试点文件逐字：「改路由必须真机验」）
    #:   ⇒ ★ 按硬约束⑥，★ 它**以登记形式显式存在**，★ 而不是被跳过。
    "sw_connect.py": {"SaveAs": 1},
    #: ★★ spec 246 新增的四处登记 —— ★ 都是「**新收进靶子表**的废弃入口**在真树里已有调用**」
    #:   （★ 242 的教训 40：★ 加一条进表 ⇒ 必须同步补 `_REGISTERED`，★ 否则判据①当场红）。
    #:   ★ `sw_export.py` 的两处 `ActivateDoc2` 与 `sw_review.py` 的一处**同型**：★ 都是 `ActivateDoc3` 的兜底
    #:     （★ 且 `dynamic_sw` 那处是 `DumbDispatch` 迟到绑定兜底 —— ★ 官方入口在该后端上失败时才走）
    #:     ⇒ ★ **保留登记**（★ 删掉就等于把兜底删了，★ 那是**行为变更**、必须真机验）。
    "sw_export.py": {"ActivateDoc2": 2},
    "sw_review.py": {"ActivateDoc2": 1},
    #: ★ `sw_part.py:934` 的 `AutoDimension2` —— ★ 该函数头**逐字记档**：
    #:   ★★ 「后继**已验证可调**…★ 而**替换要等一个能证明"尺寸真的建出来了"的判据** ⇒ ★ **再换**」
    #:   ⇒ ★ 登记不换（★ 与事实 40 同族：★ 「后继能调」与「后继能替」是**两件事**）。
    #: ★ `sw_part.py:1677` 的 `FeatureCircularPattern4` —— ★ 后继链终点 `CreateFeature` 收
    #:   `System.object FeatureData` ⇒ ★ **要先造 `ICircularPatternFeatureData`** ⇒ 换它是**重写**，须真机验。
    #: ★★ spec 247：`sw_part.py:1536` / `2544` 的 `FeatureLinearPattern5`（**2 处**）——
    #:   ★ 官方那句是「`See [[CreateFeature]] and the Remarks in [[ILinearPatternFeatureData]] and
    #:   [[ILocalLinearPatternFeatureData]]`」⇒ ★ **真后继 = `CreateFeature`**（后两个是**数据接口**）
    #:   ⇒ ★ 收表并登记；★ 不换的理由同上（★ 要**先造 `ILinearPatternFeatureData`**）。
    "sw_part.py": {"AutoDimension2": 1, "FeatureCircularPattern4": 1, "FeatureLinearPattern5": 2},
    #: ★★ spec 247 新增：`sw_pattern.py:548` 的 `FeatureLocalCurveDrivenPattern` ——
    #:   ★ 官方那句是「`See [[CreateFeature]] and the Remarks in [[ILocalCurvePatternFeatureData]]`」
    #:   ⇒ ★ 真后继 = `CreateFeature`（★ 后一个链接是**数据接口**、不是后继）⇒ ★ 收表并登记。
    #:   ★ 不换的理由：★ 后继收 `System.object FeatureData` ⇒ ★ 要**先造 `ILocalCurvePatternFeatureData`**
    #:   ⇒ 换它是**重写**、须真机验（★ 与 `FeatureCircularPattern4` 同型）。
    "sw_pattern.py": {"FeatureLocalCurveDrivenPattern": 1},
    #: ★ `sw_selection.py:337` 的 `ResumeSelectionList` —— ★ **零参版**，而后继 `ResumeSelectionList2(Append)`
    #:   ★ 多一个"是否追加"的语义参数 ⇒ ★ 换它要**先决定追加语义**（★ 同文件 335 行已在 `report_errors` 分支用 `2` 版）
    #:   ⇒ ★ 登记不换。
    "sw_selection.py": {"ResumeSelectionList": 1},
}

#: ★★ 被识别为「成员名载体」的包装器（★ **第 2 实参**是成员名的**字面量**）。
#: ★ `call_assembly_doc(doc, member, *args)` 是 spec 228 的受登记访问器 ——
#:   ★★ **它的第 2 实参同样是成员名** ⇒ ★ 不收它，`CreateMate` 就**读不出来**（判据②假红）。
_WRAPPERS = ("get_com_member", "call_com_member", "call_assembly_doc")


def _obsolete_names() -> set[str]:
    return {m for (_iface, m) in TRAPS.DEPRECATED_ENTRIES}


def _successors() -> set[str]:
    return set(TRAPS.DEPRECATED_ENTRIES.values())


def _scan_calls(tree: ast.AST):
    """★ 逐个 yield `(行号, 成员名)` —— ★★ **两种形态都收**（★ spec 241 的收口）。

    ★ 形态①（**字面量**）：`get_com_member(obj, "AddMate5", …)` ⇒ 取第 2 实参字符串。
    ★ 形态②（**点式**）：`asm_model.AddMate5(…)` ⇒ `func` 是 `Attribute` ⇒ 取 `.attr`。
    ★★ **为什么必须两种都收**：★ 只收形态① ⇒ ★ 换个写法就**绕过互锁**（★ 实测：`AddMate5`
      在真树上是**点式**调的 ⇒ 原扫描读成 **0 处** ⇒ 那是**空判据**）。
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute):
            yield getattr(node, "lineno", 0), func.attr
        elif isinstance(func, ast.Name) and func.id in _WRAPPERS:
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                    and isinstance(node.args[1].value, str):
                yield getattr(node, "lineno", 0), node.args[1].value


def _iter_member_calls(source: str):
    """★ 兼容旧接口：逐行 yield `(行号, 成员名)`（★ 只认**成员名载体**，不筛靶子表）。"""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return
    yield from _scan_calls(tree)


def _scan_all_modules():
    """★ 扫全部 `scripts/sw_*.py`（★ 排除 `sw_api_*.py` —— 那是反射转储，不是调用）。"""
    for path in sorted(SCRIPTS.glob("sw_*.py")):
        if path.name.startswith("sw_api_"):
            continue
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):          # noqa: PERF203
            continue
        yield path.name, tree


def _count_deprecated_calls() -> dict[str, dict[str, int]]:
    """★ 真树读数：`文件 → {靶子表成员名: 处数}`（★ 两种形态都算）。"""
    obsolete = _obsolete_names()
    counts: dict[str, dict[str, int]] = {}
    for name, tree in _scan_all_modules():
        for _ln, member in _scan_calls(tree):
            if member in obsolete:
                counts.setdefault(name, {})
                counts[name][member] = counts[name].get(member, 0) + 1
    return counts


# ── ① 不许新增 ────────────────────────────────────────────────────────
def test_no_new_calls_to_deprecated_entries():
    """★★ **互锁**：全仓不许**新增**对靶子表里废弃入口的调用（★ 已有的以 `_REGISTERED` 登记）。

    ★ 判据是**处数棘轮**（★ 不按行号 —— ★ 行号会漂移）：★ 某个 (文件, 成员) 的**处数超过登记值** ⇒ 红。
    """
    counts = _count_deprecated_calls()
    offenders = {}
    for fname, per in counts.items():
        reg = _REGISTERED.get(fname, {})
        for member, n in per.items():
            allowed = reg.get(member, 0)
            if n > allowed:
                offenders.setdefault(fname, {})[member] = {"now": n, "registered": allowed}
    assert not offenders, (
        "★ 出现**新增**的对废弃入口的调用（★ 本仓库判据：用靶子表给的后继）：%s\n"
        "★ 已登记 = %s（★ 每条的修法都要真机验；★ 验不过不许留在柜台上）"
        % (offenders, {k: dict(v) for k, v in _REGISTERED.items()}))


# ── ①b ★ 登记表不许有死条目 ────────────────────────────────────────────
def test_registration_table_has_no_dead_entries():
    """★★★ **登记表不许有死条目**：★ 登记了、而真树上**已经不存在**（或变少）⇒ **红**。

    ★ 为什么单列一条：★ **登记表是"现状"，不是"历史"** —— ★ 有人把废弃路由修好之后
      忘了删登记 ⇒ ★ 那条登记就变成**假数据**，★ 而**它不会自己报错**
      （★ 与"mock 落后于换代"**同病**：★ 试点文件里那条 `sw_connect.py: (916, "SaveAs")`
      ★ 就是这么烂掉的 —— ★ 行号早漂了、且**从没被任何判据读过**）。
    ★ 修法：★ 真修好了 ⇒ ★ **把登记删掉**（★ 这是好事，不是失败）。
    """
    counts = _count_deprecated_calls()
    dead = {}
    for fname, per in _REGISTERED.items():
        actual = counts.get(fname, {})
        for member, allowed in per.items():
            now = actual.get(member, 0)
            if now < allowed:
                dead.setdefault(fname, {})[member] = {"now": now, "registered": allowed}
    assert not dead, (
        "★ 登记表里有**死条目**（★ 登记值 > 真树处数）⇒ ★ 要么是**修好了**（请删掉登记）、"
        "要么是**改名/搬家了**（请把登记改对）：%s" % (dead,))


# ── ② 正面：后继要真的存在 ────────────────────────────────────────────
def test_every_successor_is_actually_used_somewhere():
    """★★ **正面判据**：★ 每个后继入口**要在仓库里真的被调用至少一次**。

    ★ 为什么需要它：★ 否则"互锁"会退化成「**全都不许用**」—— ★ 那是另一个错误
      （★ **没有任何可用路由**）。★ 试点文件里的
      `test_saveas3_is_present_where_image_or_pdf_is_written` 就是这个作用。
    ★★ **注意**：★ 后继**不一定**走 `get_com_member` ——
      ★ `CreateMate` 在 `sw_weldment.py` 走的是 `call_assembly_doc` ⇒ ★ 扫描器必须认它
      （★ 否则本判据**假红**）。
    """
    used = set()
    for _name, tree in _scan_all_modules():
        for _ln, member in _scan_calls(tree):
            used.add(member)
    missing = sorted(s for s in _successors() if s not in used)
    assert not missing, (
        "★ 这些后继入口在仓库里**一次都没被调用** ⇒ 那说明对应的废弃入口要么还该用、"
        "要么后继名写错了：%s" % (missing,))


# ── ③ 双假对象互锁（★ 教科书形态 —— 事实 62）─────────────────────────
class _Interlocked:
    """★ **假对象**：★ 后继成员**通**，废弃成员**直接 raise**（★ 这就是互锁）。"""

    def __init__(self):
        self.calls: list[str] = []

    def __getattr__(self, name):
        obsolete = _obsolete_names()
        if name in obsolete:
            raise AssertionError(
                "★ 走了废弃入口 %r ⇒ 互锁触发（★ 该用 %r）"
                % (name, TRAPS.deprecated_successor(name))
            )
        if name in _successors():
            self.calls.append(name)
            return lambda *a, **k: "OK"
        raise AttributeError(name)


def test_interlock_fires_on_deprecated_and_passes_on_successor():
    """★★★ **双假对象互锁**：★ 错误的调用路径**直接 raise AssertionError**（事实 62 的教科书形态）。

    ★ 判据两条**都要**：
      · ★ 走**废弃**入口 ⇒ **必炸**（★ 否则互锁是装饰）
      · ★ 走**后继**入口 ⇒ **必通**（★ 否则互锁把正路也堵了）
    """
    obj = _Interlocked()
    #: ★ 正路：后继入口通
    for succ in sorted(_successors()):
        obj.__getattr__(succ)
    assert sorted(obj.calls) == sorted(_successors()), obj.calls
    #: ★ 错路：废弃入口炸 —— ★ **逐条**验（★ 不能只验一条就当"整个互锁有效"）
    for name in sorted(_obsolete_names()):
        try:
            obj.__getattr__(name)
        except AssertionError as exc:
            assert "互锁触发" in str(exc), exc
            continue
        raise AssertionError("★ 废弃入口 %r **没有触发互锁** —— 那这个互锁是装饰" % name)


def test_target_table_entries_all_have_successors():
    """★ 靶子表**形状**自检：★ 每条都要有非空后继 + 名字不能是它自己。

    ★ 依据：事实 271 的一类假阳性就是「**后继名 == 自己**」（★ 解析错）。
    """
    for (iface, member), succ in TRAPS.DEPRECATED_ENTRIES.items():
        assert iface and member, (iface, member)
        assert succ and succ != member, (member, succ)
        assert succ.startswith(member.split("SaveAs")[0]) or True  #: ★ 只作记录，不强制前缀


# ── ④ ★ 点式形态**不是**盲区（★ spec 241 的收口自证）──────────────────
def test_dotted_call_form_is_not_a_blind_spot():
    """★★★ **点式形态必须被抓出** —— ★ 否则"换个写法就绕过互锁"（★ 那就是**空判据**）。

    ★ 本仓同族教训（★ 两次方向相反、**同一个病**）：
      · spec 239：「**只看点式调用 = 空判据**」（★ 调用藏在共用骨架里 ⇒ 读成 0）；
      · spec 241：**只认字面量形态 = 空判据**（★ 点式调用 ⇒ 读成 0）。
    ★★ **合成负例**（★ 判据必须能在**合成输入**上红，而不是只在真树上绿）。
    """
    obsolete = _obsolete_names()
    assert "AddMate5" in obsolete, (
        "★ 靶子表里没有 `AddMate5` ⇒ 本判据的前提不成立"
        "（★ 官方 `C:\\swapi\\types\\IAssemblyDoc\\AddMate5.md:12` 逐字 "
        "`Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]`）")
    #: ★ 形态②：点式 ⇒ 必须抓出
    dotted = "def f(asm):\n    return asm.AddMate5(0, 0, False)\n"
    got = [m for _ln, m in _scan_calls(ast.parse(dotted)) if m in obsolete]
    assert got == ["AddMate5"], "★ 点式形态**没被抓出** ⇒ 互锁有盲区：%s" % got
    #: ★ 形态①：字面量 ⇒ 必须抓出
    literal = 'def g(asm):\n    return get_com_member(asm, "AddMate5", 0)\n'
    got2 = [m for _ln, m in _scan_calls(ast.parse(literal)) if m in obsolete]
    assert got2 == ["AddMate5"], "★ 字面量形态没被抓出：%s" % got2
    #: ★ `call_assembly_doc` 也是成员名载体 ⇒ 必须抓出（★ 否则判据②假红）
    via_wrapper = 'def h(asm, d):\n    return call_assembly_doc(asm, "AddMate5", d)\n'
    got3 = [m for _ln, m in _scan_calls(ast.parse(via_wrapper)) if m in obsolete]
    assert got3 == ["AddMate5"], "★ `call_assembly_doc` 形态没被抓出：%s" % got3
    #: ★★ **边界冻结**：正确后继**不得**被误报（★ 放宽扫描面必须配"不加什么"的断言）
    good = "def i(asm, data):\n    return asm.CreateMate(data)\n"
    assert [m for _ln, m in _scan_calls(ast.parse(good)) if m in obsolete] == []
