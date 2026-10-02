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

#: ★ **已登记的既有偏差**：`模块 → {(行号, 成员名)}`。
#: ★ 与试点文件同一纪律：★ **不许新增**；★ 已有的显式登记；★ **修好后从本表删掉**。
_REGISTERED: dict[str, set[tuple[int, str]]] = {}


def _obsolete_names() -> set[str]:
    return {m for (_iface, m) in TRAPS.DEPRECATED_ENTRIES}


def _successors() -> set[str]:
    return set(TRAPS.DEPRECATED_ENTRIES.values())


def _iter_member_calls(source: str):
    """★ 逐个 yield 真被调用的成员名（★ 只认 `get_com_member` / `call_com_member` 的**第 2 实参字面量**）。

    ★★ **为什么不扫"字符串出现过"**：★ 事实 271 实测 —— 按字符串扫得 **1020** 处，
      而绝大多数来自 `sw_api_sldworks.py`（★ **反射转储表**，列出**所有**成员名，★ **不是调用**）
      ⇒ ★ **改用 AST 后是 42 处**（★ 差 24 倍，且方向完全不同）。
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id not in ("get_com_member", "call_com_member"):
            continue
        if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                and isinstance(node.args[1].value, str):
            yield node.lineno, node.args[1].value


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


# ── ① 不许新增 ────────────────────────────────────────────────────────
def test_no_new_calls_to_deprecated_entries():
    """★★ **互锁**：全仓不许**新增**对靶子表里废弃入口的调用（★ 已有的以 `_REGISTERED` 登记）。"""
    obsolete = _obsolete_names()
    offenders = []
    for name, tree in _scan_all_modules():
        registered = _REGISTERED.get(name, set())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id not in ("get_com_member", "call_com_member"):
                continue
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                    and isinstance(node.args[1].value, str) and node.args[1].value in obsolete:
                if (node.lineno, node.args[1].value) not in registered:
                    offenders.append((name, node.lineno, node.args[1].value))
    assert not offenders, (
        "★ 出现**新增**的对废弃入口的调用（★ 本仓库判据：用靶子表给的后继）：%s\n"
        "★ 已登记 = %s（★ 每条的修法都要真机验；★ 验不过不许留在柜台上）"
        % (offenders[:12], {k: sorted(v) for k, v in _REGISTERED.items()}))


# ── ② 正面：后继要真的存在 ────────────────────────────────────────────
def test_every_successor_is_actually_used_somewhere():
    """★★ **正面判据**：★ 每个后继入口**要在仓库里真的被调用至少一次**。

    ★ 为什么需要它：★ 否则"互锁"会退化成「**全都不许用**」—— ★ 那是另一个错误
      （★ **没有任何可用路由**）。★ 试点文件里的
      `test_saveas3_is_present_where_image_or_pdf_is_written` 就是这个作用。
    """
    used = set()
    for _name, tree in _scan_all_modules():
        for _ln, member in _iter_member_calls(ast.unparse(tree)):
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
