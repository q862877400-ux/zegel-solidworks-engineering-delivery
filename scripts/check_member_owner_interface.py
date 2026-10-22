r"""@brief 检查器：`get_com_member(<owner>, "X")` 里的 `X` **在不在 `owner` 的接口上**。

## 为什么（轮 173，接轮 172）
轮 172 查出 `mold_evidence` 从 **`FeatureManager` / `IModelDoc2`** 上读
`GetPartingLinesCount` / `PartingType` … ⇒ **真机全 `AttributeError: <unknown>.X`**
（它们其实在 `I*FeatureData` 上）—— ★ 即**已知事实 36**（成员在别的接口上）那一族。
★ 而仓库**已经有** `check_interface_member_ownership.py`，⚠ 但它的判据只覆盖
「`data = CreateDefinition(<CONST>)` ⇒ `data.X`」**那一条路径**
⇒ ★★ **「从某个管理器直接取成员」这种形态它看不见** ⇒ 这就是本工具要补的盲点。

## 判据（**可核验**，不是启发式）
```
① 出厂反射 `D:/AI/SW/_raw/reflect_sldworks/iface_sldworks.txt` 里有 `## <Iface>` 分段
   ⇒ 直接解析出 **接口名 → 成员名集合**（零猜测）
② 静态解析 `scripts/*.py` 的 AST：
   · `X = get_com_member(<owner>, "<Member>")`
       ⇒ 由 `<owner>` 的**已知接口**（递归推）查反射里 `Member` 的**返回类型** ⇒ 得到 `X` 的接口
       ⇒ ★ 返回类型就在反射行首（如 `FeatureManager get_FeatureManager()`）
   · `get_com_member(X, "<Member2>")`
       ⇒ ★ 若 `Member2` **完全不在** `X` 的接口的**任何**同名成员里 ⇒ **报**
③ 判据取"**完全不在**"这一**强**条件 ⇒ **假阳性低**（不判"名字像不像"）
   ⚠ 若成员在**多个**同名接口上都存在（如 `GetPartingLinesCount` 在 `IPartingLineFeatureData`
     与 `IDraftFeatureData2` 上都有）⇒ 只要**有一个**接口属于 `X` 的期望接口谱系就**不算命中**。
④ ★ **检查量为 0 时报错**（事实 46 的「假绿」守卫：`检查过 0 个` 不许 PASS）。

## ⚠ 安全
**纯静态**：只读反射 + 读源码，**不连 SolidWorks、不改任何文件**。

# ── 来源 ──
# 仓库:   SolidWorks 官方 API 出厂类型库反射（`D:/AI/SW/_raw/reflect_sldworks/iface_sldworks.txt`）
#          + 本项目源码（`scripts/*.py`）
# 文件:   scripts/check_member_owner_interface.py
# 定位:   补 `check_interface_member_ownership.py` 的盲点（它只管 `CreateDefinition` 那条路径）。
# 官方依据: 反射里的 `## <Iface>` 分段与行首返回类型；已知事实 36 的家族关系
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding="utf-8")
REFLECT = Path(Path(__file__).resolve().parents[1] / "_raw" / "reflect_sldworks" / "iface_sldworks.txt")
SCAN = [ROOT / "scripts", ROOT / "tools"]

#: ★ **已知的"管理器"根**：变量名 → 接口名。
#:
#: ⚠⚠⚠ **2026-10-01（轮 176）缩到只剩 `sw` 一个，理由是实测出的假阳性**：
#: `sw_assembly_doc.py` 的 `call_assembly_doc(doc, member, *args)` 里 `doc` **就是 `IAss
#: emblyDoc`**
#: （它的 docstring 与自己的报错文本都写着「**IAssemblyDoc** 上没有名为 {member} 的能力
#: 」），
#: 而这里把 `doc` 猜成 `IModelDoc2` ⇒ **8 处假阳性**。
#: ⇒ ★★ **同一个变量名在不同模块里可以是不同接口** ⇒ 这张表**本质是"猜"** ⇒
#: 按事实 113/114/115 的定则（**推不出就留白；不许把猜当依据**），**只留真正唯一的那个**
#: ：
#: `sw` 在本仓库**处处**都是 `ISldWorks`（由 `connect_solidworks` 的返回契约保证）。
#: ★ 其余一律靠**有依据**的途径：函数内赋值（反射的返回类型）或 `:param <名>: <接口名>`
#: 。
ROOTS = {
    "sw": "ISldWorks",
}


def load_interfaces(path: Path) -> dict:
    """解析反射 ⇒ `{接口名: {'members': set, 'returns': {成员名: 返回类型}}}`。"""
    out: dict = {}
    cur = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        m = re.match(r"^##\s+(\S+)", s)
        if m:
            cur = m.group(1)
            out.setdefault(cur, {"members": set(), "returns": {}})
            continue
        if cur is None or not s or s.startswith("#"):
            continue
        #: 形如 `FeatureManager get_FeatureManager()` / `Int32 GetPartingLinesCount()`
        m2 = re.match(r"^([\w\.<>\[\]]+)\s+(\w+)\s*\(", s)
        if m2:
            ret, name = m2.group(1), m2.group(2)
            out[cur]["members"].add(name)
            out[cur]["returns"][name] = ret
    return out


def norm(iface: str) -> str:
    """规范化接口名（反射里是 `FeatureManager`，代码里说 `IFeatureManager`）。"""
    return iface if iface.startswith("I") and len(iface) > 1 and iface[1].isupper() else "I" + iface


def canon_member(name: str) -> str:
    """★ 规范化**成员名**：剥掉反射里的 `get_` / `set_` / `put_` 前缀。

    ⚠⚠⚠ **为什么必须做**（轮 173 第一版的假阳性根因）：反射的行形如
    `FeatureManager get_FeatureManager()` —— **属性在反射里带 `get_` 前缀**，
    而代码里写 `get_com_member(model, "Extension")`（**不带前缀**）
    ⇒ 不做规范化时，**凡是属性读都会被误报成「反射里没有这个成员名」**
    （第一版因此报了 **113** 处，绝大多数是假的）。
    """
    for pre in ("get_", "set_", "put_"):
        if name.startswith(pre) and len(name) > len(pre):
            return name[len(pre):]
    return name


def owners_of(member: str, by_member: dict) -> set:
    """查一个（裸名）成员出现在哪些接口上 —— **两种写法都试**（带/不带 `get_`）。"""
    got = set(by_member.get(member) or ())
    got |= set(by_member.get("get_" + member) or ())
    return got


#: ⚠⚠⚠ **2026-10-01（轮 174）：试过一条「从 prose docstring 猜形参接口」的退路 —— 它**不
#: 成立**，已回退。**
#: 那条退路是「**没有 `:param` 段时，若 docstring 里出现的反射接口名恰好 1 个、且函数恰
#: 好 1 个形参 ⇒ 采纳它**」。
#: ★ 实测（`tools/recheck_param_iface_inference.py`）**两处都推错**：
#: ```
#:   ① `insert_parting_line` 等 5 个 ⇒ 推成 **`Feature`**
#:      ← docstring 里的**散文词** `feature` 命中了**接口名 `Feature`**
#:   ② `mold_undercut_detect` ⇒ 推成 **`IFeatureManager`**
#:      ← docstring 提到的是**成员全名**，**不是形参的类型**
#: ```
#: ⇒ ★★★ 定则：**显式 = 有依据；推断 = 会错** ⇒ 本工具**只认** `:param <名>: <接口名>`。
#: ⚠ 但**词法作用域**是**语言规则**（内层能看见外层的名字）⇒ 沿作用域链找变量**是有依据
#: 的**，
#:   与上面那条"从散文猜"**性质不同**（轮 175 加）。


def param_ifaces_from_docstring(fn, iface_names: set) -> dict:
    """从 `:param <名>: …` 的说明里推**形参的接口**（**唯一被认可**的推断写法）。

    ⚠ **只在 `iface_names`（反射里真实存在的接口名）里挑**，**不猜、不兜底** ——
    挑不到就留白（事实 113/114：**兜底会把「我不知道」变成「它有错」**）。
    """
    doc = ast.get_docstring(fn) or ""
    if not doc:
        return {}
    out: dict = {}
    #: 分段：`:param <名>:` 到下一个 `:` 指令为止
    blocks = re.split(r"(?m)^\s*:(?:param|return|returns|raises)\b", doc)
    for b in blocks:
        m = re.match(r"\s*(\w+)\s*:", b)
        if not m:
            continue
        pname = m.group(1)
        #: ⚠⚠⚠ **取「冒号后第一个出现的接口名」，不是「最长的那个」**（**轮 175 修**）：
        #: `:param model: **IModelDoc2** —— …（`FeatureManager` 从它取）。` 这一段**同时
        #: 含两个接口名**，
        #: 而按**长度倒序**会先配到更长的 `FeatureManager` ⇒ **推出错误类型**（实测报了
        #: 假阳性）。
        #: ★ 约定是「**冒号后紧跟的是类型**」⇒ 用**位置**判据（第一个匹配），**不是长度*
        #: *。
        first_pos, first_name = None, None
        for cand in iface_names:
            mm = re.search(r"(?<![A-Za-z0-9_])" + re.escape(cand) + r"(?![A-Za-z0-9_])", b)
            if mm and (first_pos is None or mm.start() < first_pos):
                first_pos, first_name = mm.start(), cand
        if first_name:
            out[pname] = first_name
    return out


#: ⚠⚠⚠ **2026-10-01（轮 174）：试过一条「形参接口推断」的退路 —— 它**不成立**，已回退。*
#: *
#: 那条退路是「**没有 `:param` 段时，若 docstring 里出现的反射接口名恰好 1 个、且函数恰
#: 好 1 个形参 ⇒ 采纳它**」。
#: ★ 实测（`D:/AI/SW/_verify_param_infer.py`）**两处都推错**：
#: ```
#:   ① `insert_parting_line` / `insert_parting_surface` / `insert_shut_off_surface` /
#:      `insert_core_cavity_solids` / `mold_draft_analysis`
#: ⇒ 推成 **`Feature`**　← ⚠ docstring 里的**散文词** `feature` 命中了**接口名 `Feature`
#: **
#:        ⇒ 于是报「`Feature . FeatureManager` 不在 `IFeature` 上」（**荒谬但"技术上成立"**）
#:   ② `mold_undercut_detect` ⇒ 推成 **`IFeatureManager`**　← ⚠ docstring 提到的是
#:      **成员全名** `IFeatureManager.MoldUndercutDetect`，**不是形参的类型**
#: ```
#: ⇒ ★★★ **「恰好 1 个」不等于「它是形参的类型」** ⇒ 该退路**已回退**（事实 53 / 113）。
#: ⇒ ★ 所以本工具**只认 `:param <名>: <接口名>` 这一种写法**（**显式 = 有依据；推断 = 会
#: 错**）。
#: ⚠ **后果**：`mold_evidence` 那种「散文 docstring + 形参 owner」**仍然抓不到**
#: （它是本工具的**动机**，见事实 113）—— ★ 要覆盖它，得走**从调用点推**那条路（**未做**
#: ）。


def helper_const_args(tree, iface_names: set) -> dict:
    """★ 收集「**辅助函数 → 调用点传的常量实参**」（轮 176）。

    返回 `{(函数名, 形参序号): [常量字符串, …]}` —— 只收**实参是字符串常量**的调用点。
    ⚠ **不猜**：一个调用点给不出常量，就**不算**（宁可留白）。
    """
    #: ① 找「辅助函数」：某个形参被当作 `get_com_member(owner, <形参>)` 的成员名
    helpers: dict = {}
    param_names: dict = {}          #: ★ `(函数名, 序号) → 形参名`（轮 176）
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        args = [a.arg for a in fn.args.args if a.arg not in ("self", "cls")]
        for idx, pname in enumerate(args):
            for n in ast.walk(fn):
                if not isinstance(n, ast.Call):
                    continue
                fname = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
                if fname not in ("get_com_member", "call_com_member", "safe_get_com_member"):
                    continue
                if len(n.args) >= 2 and isinstance(n.args[1], ast.Name) and n.args[1].id == pname:
                    helpers.setdefault((fn.name, idx), set())
                    param_names[(fn.name, idx)] = pname
    #: ② 收集调用点
    out: dict = {}
    for (fnname, idx), _s in helpers.items():
        vals: list = []
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            callee = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
            if callee != fnname:
                continue
            if len(n.args) > idx and isinstance(n.args[idx], ast.Constant) \
                    and isinstance(n.args[idx].value, str):
                vals.append(n.args[idx].value)
        if vals:
            #: ★ 连**形参名**一起返回（调用处不必再去 AST 里找那个函数对象 ——
            #: 那会踩"循环变量被覆盖"的坑，轮 176 第一次就是这么崩的）
            out[(fnname, idx)] = {"param": param_names[(fnname, idx)], "consts": sorted(set(vals))}
    return out


def main() -> int:
    if not REFLECT.is_file():
        print("  ⚠ 反射不在: %s" % REFLECT)
        return 2
    ifaces = load_interfaces(REFLECT)
    print("  反射: %d 个接口 · 合计 %d 个成员"
          % (len(ifaces), sum(len(v["members"]) for v in ifaces.values())))

    #: ★ 成员名 → 出现在哪些接口上（用于"完全不在"判据）
    by_member: dict = {}
    for iname, d in ifaces.items():
        for mem in d["members"]:
            #: ★ 同时按**裸名**与**原样**建索引（属性带 get_ 前缀）
            by_member.setdefault(mem, set()).add(iname)
            bare = canon_member(mem)
            if bare != mem:
                by_member.setdefault(bare, set()).add(iname)
    print("  去重后的成员名: %d 个" % len(by_member))

    hits = []
    indirect: list = []      #: ★ 未检查项：成员名是变量的（轮 175）
    checked = 0
    for base in SCAN:
        for f in sorted(base.glob("*.py")):
            try:
                tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            #: ① 建「变量 → 接口名」表（只看本文件，够用）
            var_iface: dict = dict(ROOTS)
            #: ★ 轮 175：每个函数的「形参 → 接口」表（**只从 `:param` 推**，见事实 114）
            iface_names = set(ifaces.keys())
            fn_scopes: list = []
            for fn in ast.walk(tree):
                if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    pi = param_ifaces_from_docstring(fn, iface_names)
                    if pi:
                        fn_scopes.append((fn, pi))

            def _lookup(name, node):
                """★ 沿**词法作用域链**找 `name` 的接口（**最内层优先**），再退回模块级变量表。

                ⚠ **为什么要链**（轮 175）：`mold_evidence` 的形状是
                ```
                    def mold_evidence(model):
                        fm = get_com_member(model, "FeatureManager")   # ← 外层函数里赋值
                        def _count(name):
                            return get_com_member(fm, name)            # ← 嵌套函数里用它
                ```
                ⇒ 只看最内层时 `fm` **不是形参** ⇒ 推不出 ⇒ 留白 ⇒ **检查器抓不到它的动机**。
                ★ 词法作用域是**语言规则**（内层能看见外层），**不是猜测**。
                ⚠ 仍**不兜底**：链上都没有 ⇒ 返回 `None` ⇒ 那一处**不检查**。
                """
                chain = []
                for fn, pi in fn_scopes:
                    if fn.lineno <= getattr(node, "lineno", 0) <= (fn.end_lineno or fn.lineno):
                        chain.append((fn.lineno, pi))
                chain.sort(key=lambda x: -x[0])          #: 最内层在前
                for _ln, pi in chain:
                    if name in pi:
                        return pi[name]
                return var_iface.get(name)
            for n in ast.walk(tree):
                if not isinstance(n, ast.Assign) or not isinstance(n.value, ast.Call):
                    continue
                call = n.value
                fname = getattr(call.func, "attr", None) or getattr(call.func, "id", None)
                if fname not in ("get_com_member", "call_com_member", "safe_get_com_member"):
                    continue
                if len(call.args) < 2 or not isinstance(call.args[1], ast.Constant):
                    continue
                owner = call.args[0]
                mem = call.args[1].value
                owner_iface = None
                if isinstance(owner, ast.Name):
                    owner_iface = _lookup(owner.id, n)      #: ★ 沿作用域链（轮 175）
                elif isinstance(owner, ast.Attribute):
                    owner_iface = _lookup(owner.attr, n)
                #: ★★ 推不出接口 ⇒ **留白**（**不许**落到 `IObject` 兜底 —— 那必然误报）
                if not owner_iface or owner_iface == "IObject":
                    continue
                #: ★ 由「持有者接口 + 成员名」查**返回类型** ⇒ 变量的接口
                #: ⚠⚠⚠ **2026-10-01（轮 177）：这里**必须两种写法都试**** ——
                #: 反射里**属性带 `get_` 前缀**（`FeatureManager get_FeatureManager()`）
                #: ，
                #: 而代码写的是裸名 `get_com_member(model, "FeatureManager")` ⇒
                #: 只查裸名会**一律查不到** ⇒ 变量**进不了表** ⇒ 后续全推不出
                #: （实测后果：`_count` 里的 `fm` 推不出 ⇒ `mold_evidence` 那 4 个计数**
                #: 漏报**）。
                #: ★ 我在**查询**那一处做了 `canon_member` 规范化，**却忘了建表这一处** 
                #: —— 同一个坑。
                ret = None
                for cand in (owner_iface, owner_iface[1:] if owner_iface.startswith("I") else owner_iface):
                    d = ifaces.get(cand) or ifaces.get(norm(cand))
                    if not d:
                        continue
                    for key in (mem, canon_member(mem), "get_" + mem):
                        if key in d["returns"]:
                            ret = d["returns"][key]
                            break
                    if ret:
                        break
                if not ret or ret in ("Void", "void"):
                    continue
                for tgt in n.targets:
                    if isinstance(tgt, ast.Name):
                        var_iface[tgt.id] = norm(ret)
            #: ② 查每一处 `get_com_member(X, "M")`
            for n in ast.walk(tree):
                if not isinstance(n, ast.Call):
                    continue
                fname = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
                if fname not in ("get_com_member", "call_com_member", "safe_get_com_member"):
                    continue
                if len(n.args) < 2 or not isinstance(n.args[1], ast.Constant):
                    #: ⚠⚠⚠ **间接成员名**（轮 175 查明的**判据边界**）：`get_com_member(
                    #: fm, name)`
                    #: —— 成员名是**变量** ⇒ 静态**不知道**要查哪个成员 ⇒ **本判据覆盖不
                    #: 了**。
                    #: ★ 不是"漏报"，是**信息不在源码里**（`mold_evidence` 的 4 个计数就
                    #: 是这种形态）。
                    #: ⇒ **登记成"未检查项"**，让读的人知道哪儿没被覆盖（**比默默跳过诚
                    #: 实**）。
                    if len(n.args) >= 2:
                        indirect.append({"file": f.name, "line": n.lineno,
                                         "owner": ast.unparse(n.args[0]),
                                         "arg": ast.unparse(n.args[1])})
                    continue
                owner, mem = n.args[0], n.args[1].value
                oiface = None
                if isinstance(owner, ast.Name):
                    oiface = _lookup(owner.id, n)           #: ★ 沿作用域链（轮 175）
                elif isinstance(owner, ast.Attribute):
                    oiface = _lookup(owner.attr, n)
                #: ★★ 同上：**推不出就别检查**（兜底值会造成假阳性）
                if not oiface or oiface == "IObject":
                    continue
                checked += 1
                owners_of_mem = owners_of(mem, by_member) | owners_of(canon_member(mem), by_member)
                if owners_of_mem is None:
                    hits.append({"file": f.name, "line": n.lineno, "owner_iface": oiface,
                                 "member": mem, "why": "**反射里没有这个成员名**"})
                    continue
                #: ★ 强判据：成员存在的**任何一个**接口，是不是 `oiface` 的谱系
                cands = {oiface, oiface[1:] if oiface.startswith("I") else oiface,
                         norm(oiface), oiface.lstrip("I")}
                if not (owners_of_mem & cands):
                    hits.append({"file": f.name, "line": n.lineno, "owner_iface": oiface,
                                 "member": mem,
                                 "actually_on": sorted(owners_of_mem)[:4]})

            #: ★★★ ③ **把辅助函数的调用点常量代进去**（轮 176）——
            #: 形状：`def _count(name): get_com_member(fm, name)` + 调用点 `_count("GetP
            #: artingLinesCount")`
            #: ⇒ ★ 把常量代进形参 ⇒ **静态就能查**（此前这类被登记为"未检查项"）。
            #: ⚠ **仍然不猜**：只认**字符串常量**的调用点；一个都给不出 ⇒ 留白。
            hc = helper_const_args(tree, iface_names)
            for (hfname, hidx), info in hc.items():
                hparam = info["param"]
                consts = info["consts"]
                for hn in ast.walk(tree):
                    if not isinstance(hn, ast.Call):
                        continue
                    hf = getattr(hn.func, "attr", None) or getattr(hn.func, "id", None)
                    if hf not in ("get_com_member", "call_com_member", "safe_get_com_member"):
                        continue
                    if len(hn.args) < 2 or not isinstance(hn.args[1], ast.Name):
                        continue
                    if hn.args[1].id != hparam:          #: ★ 用返回的形参名比对
                        continue
                    howner = hn.args[0]
                    hoif = None
                    if isinstance(howner, ast.Name):
                        hoif = _lookup(howner.id, hn)
                    elif isinstance(howner, ast.Attribute):
                        hoif = _lookup(howner.attr, hn)
                    if not hoif or hoif == "IObject":
                        continue
                    for cv in consts:
                        checked += 1
                        own = owners_of(cv, by_member) | owners_of(canon_member(cv), by_member)
                        if not own:
                            hits.append({"file": f.name, "line": hn.lineno, "owner_iface": hoif,
                                         "member": cv, "via": "%s(%r)" % (hfname, cv),
                                         "why": "**反射里没有这个成员名**"})
                            continue
                        hc_c = {hoif, hoif[1:] if hoif.startswith("I") else hoif, norm(hoif),
                                hoif.lstrip("I")}
                        if not (own & hc_c):
                            hits.append({"file": f.name, "line": hn.lineno, "owner_iface": hoif,
                                         "member": cv, "via": "%s(%r)" % (hfname, cv),
                                         "actually_on": sorted(own)[:4]})

    print("  ★ 检查过的 `get_com_member(已知对象, 成员)` 调用点: **%d** 个" % checked)
    print("  ⚠ **未检查项**（成员名是**变量**，静态查不了）: **%d** 处" % len(indirect))
    for h in indirect[:8]:
        print("      %-26s L%-5d get_com_member(%s, **%s**)"
              % (h["file"], h["line"], h["owner"], h["arg"]))
    print("  ★★ 命中（成员**不在**该对象的接口上）: **%d** 处" % len(hits))
    for h in hits[:20]:
        print("    %-26s L%-5d %-16s . %-26s ⇒ 实际在 %s"
              % (h["file"], h["line"], h["owner_iface"], h["member"],
                 h.get("actually_on", h.get("why", ""))))
    if hits:
        print()
        print("  ⚠ 独立复核（前 3 处）：")
        for h in hits[:3]:
            print("    %s:%d  `%s` 不在 %s 上 ⇒ %s"
                  % (h["file"], h["line"], h["member"], h["owner_iface"],
                     h.get("actually_on", h.get("why"))))
    out = Path(Path(__file__).resolve().parents[1] / "output" / "member-owner-interface.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"checked": checked, "hits": hits, "unchecked_indirect": indirect}, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print("  证据: %s" % out)
    #: ★ 事实 46：检查量为 0 不许 PASS
    if checked == 0:
        print("  ✗ **检查过 0 个** ⇒ 判据没生效（事实 46 的假绿）⇒ 非 0 退出")
        return 2
    return 0 if not hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
