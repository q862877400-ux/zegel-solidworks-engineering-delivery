"""@brief 审计：**标量 by-ref 出参**（`Int32&` 等）有没有被**裸传**。

## 为什么需要它（这是**静默失败**类）
官方反射里 `Int32&` 这类**标量出参**，**调用方必须传一个 by-ref `VARIANT`**
（本项目的包装器是 `sw_connect.out_i4()` → `VARIANT(VT_BYREF | VT_I4, 0)`）。

**裸传**（例如漏了、或传了个普通整数）会：
* 有的直接抛 `DISP_E_PARAMNOTOPTIONAL`（**还算好**）；
* **有的静默不做那件事** —— 而「静默无效」正是本项目反复踩的头号敌人
  （已知事实 8 的 `AddSelectionListObject` 返回 12 次 false；
   已知事实 30 的「可取 ≠ 调用成功」）。

**⚠ 记忆里记着「AST 审计发现 18 个裸出参（6 在 `sw_simulation.py` / 11 在 `sw_topology.py` /
1 在 `sw_render_material.py`），`fix_bare_outparams.py` 可修」—— 但那个工具**不存在**，
所以这条一直没做。本工具把它补上。**

## 判据（与 `audit_call_arity.py` 的口径**同源**，不另立一套）
`audit_call_arity.py` 已经确立了「**调用方要传的实参个数**」口径：
`Int32&` **算**一个（必须传），`Object&` / `Variant&` / `Dispatch&` **不算**（纯出参，不用传）。
**⇒ 本工具复用同一套「计入列表」，于是「第 i 个实参 ↔ 第 i 个计位形参」是确定的。**

⚠⚠⚠ **2026-10-01（轮 189）：上面这条口径**来自反射文本**，而反射的 `&` **只说明"按引用"、
不区分方向** —— 所以「`Object&` 是否真的"纯出参"」原本是**假设**，不是查证过的。**
★ 本轮用**第 4 套签名源**（类型库方法表，见 `tools/audit_inout_array_params.py`）查了这件事：
```
· 类型库 `sldworks.tlb` 里**含 `in,out` 数组类形参**（`VARIANT` / `LP_tagVARIANT` /
  `POINTER(IDispatch)` / `POINTER(IUnknown)`）的成员 = **62** 个（扫了 507 个接口）
· ★ 其中**本仓库生产代码按字面量调用过的 = 0**（命中的 2 个 `PackVariant` / `PutDouble`
  只出现在探针 `tools/probe_safearray_utility.py` 里）
⇒ ★★ **那条口径在实践中**目前**无害** —— 不是因为它对，而是因为**我们还没碰那 62 个成员**。
⇒ ★ **将来若要调它们**（它们**必须先传一个已构造的数组**），**先查**
  `tools/audit_inout_array_params.py` 的 `output/inout-array-params.json`（清单已存档），
  并按 `in,out` 语义**传数组**，而**不能**沿用上面这条"不算"的口径。
```
⚠ 已知的机制性反例（轮 188 实测）：`ISafeArrayUtility.PutDouble(VariantArray = **in,out**)` ——
  它按本条口径会被当成「纯出参、不用传」，而它**确实要传**。

**⇒ 违规 = 某个计位形参以 `&` 结尾，而对应的实参**不是** by-ref 包装器。**

## 什么算「by-ref 包装器」
* `out_i4()` / `out_i4(0)` —— 本项目的标量出参包装（首选）
* `VARIANT(VT_BYREF | ..., ...)` —— 直接包
* 任何名字以 `out_` 开头的调用
**⇒ 其余一律视为裸传**（宁可误报，不可漏报 —— 这一类的代价不对称）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 反射（`D:\\AI\\SW\\_raw\\...\\iface_*.txt`，由
#         `reflect-interop.ps1` 纯元数据枚举生成）
# 文件:   `sw_connect.out_i4(Int32) -> VARIANT(VT_BYREF|VT_I4)`
# 定位:   补上 `audit_call_arity.py` 的**姊妹检查**：arity 管「个数对不对」，
#         本工具管「该 by-ref 的有没有 by-ref」。**两者合起来才覆盖调用形状。**
#  ⚠ 本工具的**解析层从 `audit_call_arity.py` 导入**（`load_signatures` / `call_sites`
#    的同一套正则与 AST），**不重写一份** —— 口径必须同源，否则两边会漂移。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 本工具**未在本机实测 SolidWorks**（它是静态文本/AST 工具）；
#   其判据的正确性来自已被真机验证过的 `out_i4()` 契约（`sw_connect.py` 的来源块）。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from audit_call_arity import IFACE_HEAD, IFACE_SIG, WRAPPERS, call_sites  # noqa: E402

#: 纯出参的容器类型 —— **不计入**「调用方要传的实参」
PURE_OUT = re.compile(r"^(Object|Variant|Dispatch)&\s*$", re.I)

#: 标量出参（**计入**，必须由调用方包 by-ref）
SCALAR_OUT = re.compile(r"^(Int32|Long|Double|Boolean|Int16|Single|String)&\s*$", re.I)

#: 认作「by-ref 包装器」的实参文本
#: ★★ 2026-10-07（接手轮 · 规格 214 T-214-06）**第二次修同一类假阳性** ——
#:   ★ 上一版只认**裸名**（`out_i4(` / `VARIANT(`），★ 而**限定名** `sw_connect.out_i4()`
#:     是**本文件自己**在来源块与修法提示里点名的**正确形态**（L5 · L49 · L310 逐字写着
#:     「本项目的包装器是 `sw_connect.out_i4()`」）⇒ ★ 反而被报成"裸传" ✗
#:   ★ 实测命中 **1 处**：`tools/probe_analysis_run_long_timeout.py:142`
#:     （`GetLoadsAndRestraints(_i, sw_connect.out_i4())` —— ★ 那一处**本来就是对的**）✓
#:   ⚠ 与下面那条注释**同源**：★ **工具自己的假阳性** ——
#:     ★ 判据必须覆盖「**我自己推荐的写法**」，★ 否则它会去告自己写对的代码 ✓
BYREF_OK = re.compile(
    r"^\s*(?:[\w.]+\.)?_?out_\w*"        # out_i4() · _out_i4() · sw_connect.out_i4()
    r"|^\s*(?:[\w.]+\.)?_?VARIANT\s*\("  # VARIANT( · win32com.client.VARIANT(
)
# ⚠ 前导下划线是**必须**的：本项目既有 `out_i4`（`sw_connect`）也有 `_out_i4`（工具里的别名），
#   第一版正则只认 `out_` 开头 ⇒ 把我自己正确的调用报成违规（**工具自己的假阳性**）。


def load_full_signatures(paths) -> dict[str, list[tuple[str, list[str]]]]:
    """解析反射清单 → ``{成员名: [(接口.签名, [参数类型...]), ...]}``。

    ⚠ 与 `audit_call_arity.load_signatures` 的差别：**保留完整参数类型列表**，
    因为本工具需要知道**哪一位**是 `&`。
    """
    table: dict[str, list[tuple[str, list[str]]]] = {}
    for path in paths:
        current = None
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        for raw in text.splitlines():
            head = IFACE_HEAD.match(raw)
            if head:
                current = head.group(1)
                continue
            sig = IFACE_SIG.match(raw)
            if not (sig and current):
                continue
            _ret, name, params = sig.groups()
            if name.startswith(("get_", "set_")):
                name = name[4:]
            plist = [p.strip() for p in params.split(",")] if params.strip() else []
            table.setdefault(name, []).append(("%s.%s" % (current, name), plist))
    return table


def counted_positions(plist: list[str]) -> list[tuple[int, str]]:
    """返回「计入调用方实参」的 ``[(下标, 类型), ...]``（顺序保持）。

    ⚠ 口径与 `audit_call_arity.py` 一致：`Int32&` **计入**，`Object&` 等**不计入**。
    """
    out: list[tuple[int, str]] = []
    for i, p in enumerate(plist):
        if PURE_OUT.match(p):
            continue
        out.append((i, p))
    return out


def byref_alias_names(path: Path) -> set[str]:
    """★ 收集**本文件里 by-ref 构造器的别名**（`from sw_connect import out_i4 as _oi4` ⇒ `{"_oi4"}`）。

    ★★★ 2026-10-03（接手轮）**为什么必须补这一条**：`byref_variables` 的正则只认
      `out_\\w*` 或 `VARIANT` ⇒ ★ **别名 `_oi4` 两边都不匹配** ⇒ 真机代码里
      `err_out = _oi4()` 之后把 `err_out` 传出去时，被判「**裸传标量出参**」
      ⇒ ★★ **工具自己的假阳性**（★ 实测 **7 处**，全在 `InsertCutSurface` 第 5 位；
        ★ 而它们**都**在上一行用 `out_i4` 的别名构造好了 —— `err_out = _oi4()`）。
    ★ 口径（★ 不放宽、不猜）：**只认「从别处 `import` 进来的、名字形如 `_?out_*` 或 `VARIANT` 的构造器」**；
      ★ 与本文件既有的那条"**元组解包**"补法**同一性质** —— ★ **把同一个语义的另一种写法补齐**，
      而不是把判据放松。
    """
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for a in node.names:
                if re.fullmatch(r"_?out_\w*", a.name) or a.name == "VARIANT":
                    names.add(a.asname or a.name)
    return names


def byref_variables(path: Path) -> set[str]:
    """收集**先构造 by-ref、后传出去**的局部变量名。

    ⚠ 为什么需要：真机代码常写成
        ``v = VARIANT(VT_BYREF | VT_R8, 0.0)`` … ``get_com_member(..., v)``
    —— **`v` 是合法的 by-ref 实参**，但它不是「一次调用表达式」，
    第一版只看实参文本 ⇒ **把它误报成裸传**（工具自己的假阳性）。

    ⚠ 范围：**按文件**收集（不做函数级作用域）。同名变量跨函数的误判概率极低，
    而按文件做能覆盖绝大多数真实写法。**这是有意的取舍，写在注释里。**
    """
    src = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    names: set[str] = set()
    #: ★★ 2026-10-03（接手轮）：把**本文件里构造器的别名**（`import out_i4 as _oi4`）也算进去 ——
    #:   ★ 否则 `err_out = _oi4()` 这种"先构造后传出"会被漏记 ⇒ **假阳性**（实测 7 处）。
    _aliases = sorted(byref_alias_names(path))
    _alias_alt = ("|" + "|".join(re.escape(a) for a in _aliases)) if _aliases else ""
    _ctor = re.compile(r"(^|[^\w])(_?(out_\w*|VARIANT)%s)\s*\(" % _alias_alt)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        rhs = ast.get_source_segment(src, node.value) or ""
        if not _ctor.search(rhs):
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name):
                names.add(tgt.id)
            #: ★★★ 2026-10-03（轮 470）**补上"元组/解包赋值"** ——
            #:   真机代码常写成一次拿**两个**出参：
            #:     `id1, id2 = out_i4(), out_i4()`
            #:   ★ 而原先只收 `ast.Name` 目标 ⇒ **`ast.Tuple` 被整条跳过**
            #:   ⇒ `id1` / `id2` **没被记为合法 by-ref 变量** ⇒ 下一行传它俩时
            #:     被判「裸传标量出参」⇒ ★★ **工具自己的假阳性**
            #:     （★ 实测：`tools/prove_render_material_sequence.py:108` 那一处，
            #:       而它**明明**在上一行构造好了）。
            #:   ★ 这不是放宽判据：★ **`byref_variables` 的语义就是"先构造后传出"**，
            #:     元组解包只是同一个语义的**另一种写法** ⇒ ★ 补全它才算完整 ✓
            elif isinstance(tgt, ast.Tuple):
                for elt in tgt.elts:
                    if isinstance(elt, ast.Name):
                        names.add(elt.id)
    return names


def own_call_sites(path: Path):
    """**自己的** AST 取点：返回 ``[(行号, 包装名, 成员名, [实参源码文本...])]``。

    ⚠ 为什么不直接用 `audit_call_arity.call_sites`：它只回**实参个数**，
    而本工具需要**每一位实参的源码文本**才能判断「包没包 `out_i4()`」。
    **⇒ 签名口径仍从那边 import（不重写），只有取文本这一步自己来。**
    """
    src = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or len(node.args) < 2:
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name not in WRAPPERS:
            continue
        m = node.args[1]
        if not (isinstance(m, ast.Constant) and isinstance(m.value, str)):
            continue
        texts = []
        for a in node.args[2:]:
            seg = ast.get_source_segment(src, a)
            texts.append((seg or "").strip().replace("\n", " "))
        rows.append((node.lineno, name, m.value, texts))
    return sorted(rows)


def scan(path: Path, table) -> tuple[list[dict], int]:
    """扫一个文件，返回 ``(违规列表, 检查过的调用点数)``。"""
    bad: list[dict] = []
    checked = 0
    byref_vars = byref_variables(path)          # 先构造后传出的合法 by-ref 变量
    #: ★★ 2026-10-03（接手轮）：**内联**用别名构造的也算合法（如 `_oi4()` 直接写进实参）。
    _aliases = byref_alias_names(path)
    _alias_inline = ([re.compile(r"^\s*%s\s*\(" % re.escape(a)) for a in _aliases]
                     if _aliases else [])
    for lineno, wrapper, member, args in own_call_sites(path):
        if wrapper not in WRAPPERS:
            continue
        variants = table.get(member)
        if not variants:
            continue
        # 只看「实参个数」能对上的那些签名（个数不对是 arity 审计的活）
        cands = [v for v in variants if len(counted_positions(v[1])) == len(args)]
        if not cands:
            continue
        checked += 1
        # 任一候选签名认为「这位是 &」且实参没包 ⇒ 可疑
        # ⚠ 每个调用点**只报一次**：第一版把 break 放在内层 ⇒ 两个候选签名会报两遍（重复）。
        reported = False
        for sig_name, plist in cands:
            if reported:
                break
            for pos, (raw_i, ptype) in enumerate(counted_positions(plist)):
                if not ptype.endswith("&") or not SCALAR_OUT.match(ptype):
                    continue                      # 只关注标量出参
                actual = args[pos]
                if BYREF_OK.match(actual):
                    continue
                if any(rx.match(actual) for rx in _alias_inline):
                    continue                        # ★ 内联的**别名**构造（如 `_oi4()`）
                if actual in byref_vars:            # 该变量是从 by-ref 构造赋来的
                    continue
                bad.append({
                    "file": str(path.name), "line": lineno, "member": member,
                    "position": pos, "type": ptype.strip(),
                    "actual": actual, "signature": sig_name,
                })
                reported = True
                break
    return bad, checked


def main() -> int:
    ap = argparse.ArgumentParser(description="裸 by-ref 标量出参审计")
    ap.add_argument("target", nargs="?", default="", help="单文件；省略则扫 scripts/ + tools/")
    ap.add_argument("reflection", nargs="*", help="iface_*.txt 反射清单")
    ap.add_argument("--all", action="store_true", help="扫 scripts/ + tools/")
    args = ap.parse_args()

    sig_paths = args.reflection
    if not sig_paths:
        raw = Path(r"D:\AI\SW\_raw")
        sig_paths = [str(p) for p in sorted(raw.rglob("iface_*.txt"))]
        if not sig_paths:
            print("⚠ 找不到反射清单（D:\\AI\\SW\\_raw\\**\\iface_*.txt）")
            return 2
    table = load_full_signatures(sig_paths)

    if args.target:
        targets = [Path(args.target)]
    else:
        targets = sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "tools").glob("*.py"))

    total_bad, total_checked = [], 0
    per_file: dict[str, int] = {}
    for t in targets:
        if not t.is_file():
            continue
        bad, checked = scan(t, table)
        total_checked += checked
        if bad:
            per_file[t.name] = len(bad)
        total_bad.extend(bad)

    print("反射清单 %d 份；扫描 %d 个文件；检查过的调用点 **%d**" % (len(sig_paths), len(targets), total_checked))
    print("⇒ **标量出参裸传 %d 处**" % len(total_bad))
    if total_bad:
        print()
        for f, n in sorted(per_file.items(), key=lambda kv: -kv[1]):
            print("  %-30s %d 处" % (f, n))
        print()
        print("  明细（前 30）：")
        for b in total_bad[:30]:
            print("    %s:%d  %s(...)  第 %d 位应为 %s，实参是 `%s`"
                  % (b["file"], b["line"], b["member"], b["position"], b["type"], b["actual"][:40]))
        print()
        print("  修法：把该实参换成 `out_i4()`（`sw_connect.out_i4`）。")
        print("        ⚠ **不要**凭本工具的输出批量替换 —— 先逐条核对官方签名与调用上下文。")
    return 0 if not total_bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
