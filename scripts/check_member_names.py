"""门禁：所有 ``get_com_member(obj, "X")`` 的 X 必须在官方反射清单里查得到。

为什么要有这道门禁
------------------
本任务里「凭印象写 API」栽过 **9 次**（7 次多写、1 次删多、1 次拼错）。
其中：

* ``IDisplayDimension.GetValue``  → 官方无此成员
* ``ISectionViewData.AccessSelections`` → 5 个成员全是凭印象从别的族搬来的
* ``ITableAnnotation.SetText`` → 方法形态没有（属性形态有）
* ``IModelDocExtension.MateType`` → 官方是 ``Type()``
* ``ICurve.IsArc`` → **官方没有「圆弧」这个独立类型**
* ``IView.OrientToward`` → 两套官方源都查不到（已按铁律 5 删除封装）

这些**单文件测试全都抓不到**——契约测试只验「引用的成员在登记表里」，
而登记表本身可能就是错的。**全仓扫描才查得出**（见 AGENTS.md 铁律 4）。

⚑ 本门禁只查**名字存在性**，不查 arity —— arity 由 audit_call_arity.py 负责。
⚑ 允许「查不到」白名单（`ALLOW_UNKNOWN`），但每条都必须写明原因；
   白名单为空时，任何查不到的成员都让门禁失败。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（与 check_provenance.py / check_diff_markers.py 同为门禁）
# 文件:   scripts/check_member_names.py —— 本文件自身
# 定位:   成员名存在性门禁的实现。
# 依据:   AGENTS.md 铁律 4「签名以官方文档为准」+ 铁律 5「查不到就说查不到」
# 覆盖:   后续同级定义
# ⚠ 本门禁为静态检查，未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import ast
import io
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: 官方 interop 程序集的纯元数据反射清单（AGENTS.md §四.1③）
REFLECTIONS = [
    Path(
        Path(__file__).resolve().parents[1]
        / "_raw"
        / "reflect_sldworks"
        / "iface_sldworks.txt"
    ),
    Path(
        Path(__file__).resolve().parents[1] / "_raw" / "reflect" / "iface_cosworks.txt"
    ),
    Path(
        Path(__file__).resolve().parents[1]
        / "_raw"
        / "reflect"
        / "iface_swdocumentmgr.txt"
    ),
    Path(
        Path(__file__).resolve().parents[1]
        / "_raw"
        / "reflect"
        / "iface_SWRoutingLib.txt"
    ),
    Path(
        Path(__file__).resolve().parents[1]
        / "_raw"
        / "reflect"
        / "iface_sldcostingapi.txt"
    ),
    Path(Path(__file__).resolve().parents[1] / "_raw" / "reflect" / "iface_fworks.txt"),
]

#: 本项目自身的常量名（SW_DOC_TYPES 等）不是 API 成员，不必去反射里找
OWN_CONSTANTS = re.compile(
    r"^(SW_|ARITY|FAMILIES|PROPERTIES|OVERLOAD_"
    r"GETTERS|UNWRAPPED|TRAPS|SELECTION_|SEEN_)"
)

SIG = re.compile(r"^\S+\s+(\w+)\s*\(")
#: get_com_member(obj, "X") 与 obj.X() 两种形态
#: ⚑⚑ 2026-10-01（轮 145）：原正则**只认 `get_com_member`** ⇒
#:   ① 它一直**漏掉了 `safe_get_com_member`**（`\b` 在 `_` 之后不成立）；
#:   ② 本轮把 24 处「故意要调」的调用改名成 `call_com_member` 后，
#:      那 24 处**也不再被计数**。
#:   ★ 根因是同一个：**"有几个取成员的同义词"这件事没有单一真源**。
#:   ⇒ 修法：把三种**都**认上（它们都是"取/调 COM 成员"的调用点）。
#:   ⚠ 这是**轮 145 的**修法；若将来再加同义词，**这里要同步**。
WRAPPER = re.compile(
    r"(?:\bget_com_member|\bcall_com_member|\bsafe_get_com_member)\s*\(\s*[^,()]+,\s*[\"']([A-Za-z_]\w*)[\"']"
)
DOTCALL = re.compile(r"[.\s]([A-Za-z_]\w*)\s*\(")
SKIP_LINE = re.compile(r"^\s*(#|\"\"\"|''')")
FUNCDEF = re.compile(r"^\s*def\s+")

#: 显式白名单：{成员名: 为什么官方查不到}
# ⚠⚑ 铁律 5：两套官方源都查不到的成员，**不提供封装**，因此不会出现在代码里。
#   这张表应当保持为空或极短；新增一条必须写明查证过程。
ALLOW_UNKNOWN: dict[str, str] = {}


def _official_members() -> set[str] | None:
    """全部反射清单里的成员名（已把 get_/set_ 归一化到 COM 名）。"""
    if not any(r.is_file() for r in REFLECTIONS):
        return None
    names: set[str] = set()
    for r in REFLECTIONS:
        if not r.is_file():
            continue
        for line in r.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("## "):
                continue
            m = SIG.match(line)
            if not m:
                continue
            names.add(re.sub(r"^(get|set)_", "", m.group(1)))
    return names


def scan() -> list[tuple[str, int, str]]:
    """扫 scripts/ 下所有 .py 的 get_com_member 调用，返回 (文件, 行号, 成员名)。"""
    out = []
    for p in sorted((REPO / "scripts").glob("*.py")):
        for i, line in enumerate(
            p.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            if SKIP_LINE.match(line):
                continue
            for mem in WRAPPER.findall(line):
                out.append((p.name, i, mem))
    return out


# ══════════════════════════════════════════════════════════════════════
# 「**直接属性访问**」这一类的成员名检查（2026-10-01 轮 160 新增）
#
# ⚠⚠⚠ **为什么要加**：本文件原来只认 `get_com_member` / `call_com_member` /
#   `safe_get_com_member` 三种**包装形态** ⇒ ★ **直接属性访问（`obj.Member(...)`）
#   是它的盲区** —— 而 `077`（`model.GetSldWorksObject()`）与 `159`
#   （`asm_model.InterferenceDetection` / `GetInterference`）**两个真缺陷都是这个形态**。
#
# ★ 判据的**三版演进**（每一版的教训都留在代码里）：
# ① 「大驼峰 + 不在反射里」⇒ 实测**假阳性 ≈100%**（`argparse` / `winreg` / OCP 全进来）⇒
#  弃用；
#   ② 「对象名从 `get_com_member(<OBJ>, …)` 推导」⇒ 12 处，但仍混着 docstring 举例、
#      COM 基础设施、**跨函数同名变量**（事实 51）；
#   ③ **本函数**：`ast` 只查代码 + **按函数定作用域** + COM 基础设施白名单 +
#      **「从 COM 对象属性派生」的传播**。
#      ⇒ ⚠ 少了最后那条「传播」会**漏检**最常见的形态
#        （`interference = asm_model.InterferenceDetectionManager` 之后 `interference.X(...)`）
#        —— ★ 这是**「能响测试」当场抓出来的**（收窄修掉了假阳性，却引入了一个漏检）。
#
# ★ **判据已被证明能响**：`tests/test_direct_member_probe_can_fire.py`（6 条：
#   2 条正例喂真缺陷形态 ⇒ 必须命中；4 条反例 ⇒ 不许误报）。
# ══════════════════════════════════════════════════════════════════════
COM_INFRA = {
    "QueryInterface",
    "AddRef",
    "Release",
    "GetTypeInfo",
    "GetIDsOfNames",
    "Invoke",
}
_WRAP_NAMES = {
    "get_com_member",
    "call_com_member",
    "safe_get_com_member",
    "get_com_member_raw",
}


#: ★ 2026-10-22 统一化：本函数与 tools/probe_direct_member_access 里的嵌套 ident
#:   逐字相同，已收敛到 scripts/ast_helpers.base_name
try:
    from .ast_helpers import base_name as _base_name
except ImportError:
    from ast_helpers import base_name as _base_name


def find_direct_member_access(path, known):
    """在一个文件里找「**已当 COM 对象用过的**变量上、调用了**反射里没有**的大驼峰成员」。

    :param path: 要扫的 `.py` 路径。
    :param known: 出厂反射里的全部成员名（**唯一真源**）。
    :returns: `[{"file", "line", "fn", "obj", "name"}]`
    """
    try:
        tree = ast.parse(Path(path).read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    out = []
    for fn in [
        n
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]:
        com_objs = set()
        for sub in ast.walk(fn):
            if (
                isinstance(sub, ast.Call)
                and isinstance(sub.func, ast.Name)
                and sub.func.id in _WRAP_NAMES
                and sub.args
            ):
                o = _base_name(sub.args[0])
                if o:
                    com_objs.add(o)
        #: ★ **传播**：从 COM 对象属性派生的变量也算 COM 对象（三层足够）
        for _ in range(3):
            grew = False
            for sub in ast.walk(fn):
                if (
                    isinstance(sub, ast.Assign)
                    and len(sub.targets) == 1
                    and isinstance(sub.targets[0], ast.Name)
                    and isinstance(sub.value, (ast.Attribute, ast.Call))
                ):
                    v = sub.value.func if isinstance(sub.value, ast.Call) else sub.value
                    if _base_name(v) in com_objs and sub.targets[0].id not in com_objs:
                        com_objs.add(sub.targets[0].id)
                        grew = True
            if not grew:
                break
        if not com_objs:
            continue
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                o = _base_name(sub.func.value)
                name = sub.func.attr
                if o in com_objs and name not in known and name not in COM_INFRA:
                    out.append(
                        {
                            "file": Path(path).name,
                            "line": getattr(sub, "lineno", 0),
                            "fn": fn.name,
                            "obj": o,
                            "name": name,
                        }
                    )
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    official = _official_members()
    if official is None:
        print("[SKIP] 反射清单不在本机，无法校验（这是静默通过，不算通过）")
        return 0
    print(
        f"成员名门禁 · 官方成员 {len(official)} 个"
        f"（{sum(1 for r in REFLECTIONS if r.is_file())} 份反射清单）"
    )
    rows = scan()
    bad = []
    for fname, lineno, mem in rows:
        if OWN_CONSTANTS.match(mem):
            continue
        if mem in official or mem in ALLOW_UNKNOWN:
            continue
        bad.append((fname, lineno, mem))
    print(f"  get_com_member 调用点 {len(rows)} 个")
    #: ★★ **第二个 pass：直接属性访问**（`obj.Member(...)`）——
    #: 本文件原来只认包装形态，这是它的盲区（`077`/`159` 两个真缺陷都在这里漏过去）。
    #: ⚠ 判据**已被证明能响**（`tests/test_direct_member_probe_can_fire.py` 6 条：
    #: 2 条正例喂真缺陷形态 ⇒ 必须命中；4 条反例 ⇒ 不许误报）。
    direct = []
    for p in sorted((REPO / "scripts").glob("*.py")):
        for h in find_direct_member_access(p, official):
            if OWN_CONSTANTS.match(h["name"]) or h["name"] in ALLOW_UNKNOWN:
                continue
            direct.append((h["file"], h["line"], h["name"], h["fn"], h["obj"]))
    print(
        f"  直接属性访问命中 {len(direct)} 个"
        "（只查「已当 COM 对象用过的变量」上的大驼峰成员）"
    )
    for fname, lineno, mem, fn, obj in direct[:40]:
        print(f"  {fname}:{lineno}  {obj}.{mem}()  ← 函数 {fn}()")
    if not bad and not direct:
        print("[PASS] 全部成员名都能在官方反射里查到（含**直接属性访问**那一类）")
        return 0
    bad = bad + [(f, ln, m) for f, ln, m, _fn, _ob in direct]
    print(f"[FAIL] {len(bad)} 个成员名在官方反射里查不到：")
    for fname, lineno, mem in bad[:40]:
        print(f"  {fname}:{lineno}  {mem}")
    if len(bad) > 40:
        print(f"  …… 另有 {len(bad) - 40} 个")
    print(
        "\n⚑ 处置：两套官方源都查不到 ⇒ 按铁律 5 写明「查不到」并删除封装，"
        "\n  不要拿相似名字蒙混；确属本项目自有常量则登记进 ALLOW_UNKNOWN。"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
