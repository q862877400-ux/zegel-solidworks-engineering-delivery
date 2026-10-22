"""★ **筛选器**：把 277 个工具映射到「它真正调的 COM 成员」⇒ 再投影到官方结构上。

★ 为什么需要它（★ 上一轮判据① = **100% 无处可放**，★ 根因已诊断清楚）：
  ★★ **工具名是**意图语言**（`fillet` / `part_shell`），★ 官方成员名是**实现语言**
    （`FeatureFillet3` / `InsertShellFeature`）** ⇒ ★★ **两套词汇不共享 token**
    ⇒ ★ **按名字分类必然 0 命中**。
  ⇒ ★★★ **但那条映射**已经存在于我们代码里**：★ 每个 ToolSpec 有 `module` + `function`，
    ★ 而那个函数体里就是真正的成员名 ⇒ **只是没被抽出来**。
★ 做法：★ 对每条 spec，★ 读 `scripts/<module>.py`，★ **AST 定位 `<function>`**，
  ★★ **跟一层调用图**（★ 事实 507：只看 spec 文档会漏，★ 要落到函数体），
  ★ 抽出 `get_com_member(x, "Member")` / `call_com_member(x, "Member")` 的**字符串字面量**。
★ 只读。产出 `output/tool-to-member-map.json`。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/map_tools_to_members.py
# 定位:   筛选器**：把 277 个工具映射到「它真正调的 COM 成员」⇒ 再投影到官方结构上。
# 官方依据: 官方源 `C:\swapi\types\**`（★ 逐条见文件内引用）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
SWAPI = Path(r"C:\swapi")
OUT = REPO / "output" / "tool-to-member-map.json"

#: ★ 取成员的两种调用形态（★ 本仓口径）
#: ★★★★ 2026-10-03（接手轮）**从"白名单枚举"改成"按形态认"** ——
#:   ★ 病灶：★ 原来写 `(?:get_com_member|call_com_member|set_com_member)` ⇒
#:     ★★ 而本仓**实际有 6 种写法**（★ 实测计数）：
#:     | ★ 名 | ★ 出现次数 | ★ 旧版认吗 |
#:     |---|---|---|
#:     | `get_com_member` | **1011** | ★ 认 |
#:     | `set_com_member` | 119 | ★ 认 |
#:     | `call_com_member` | 55 | ★ 认 |
#:     | ★★ `safe_get_com_member` | **39** | ✗ **不认** |
#:     | ★★ `_safe_com_member` | 14 | ✗ **不认** |
#:     | ★★ `_optional_com_member` | 10 | ✗ **不认** |
#:     ⇒ ★★★ **共 63 处被漏掉** ⇒ 直接后果：
#:       `sw_assembly.get_components` / `collect_mate_feature_summary` 被算成"抽不到成员"
#:       ⇒ ★★ 进了"无处可放"清单（★ 见阶段 3 的分类：那 3 个"真问题"里它就占 2 个）✓
#: ★★★ 修法（★ 不"再加两个名字"）：★ **按**形态**认** —— ★ **任何以 `_com_member` 结尾的
#: 函数名** ✓
#:     用 `\w*com_member` ⇒ ★ 6 种全覆盖，★ **且将来加第 7 种也不用改** ✓
#:   ★★ **可复用判据**：★★ **"按白名单枚举写法"必然漏掉新写法** ——
#:     ★ 凡"认若干种已知写法"的判据，★ 都要问"**有没有一个**形态**能覆盖全部**" ✓
CALL_PAT = re.compile(r'\b\w*com_member\s*\(\s*[^,]+,\s*"([A-Za-z_][A-Za-z0-9_]*)"')
#: ★ 取"点调用"形态：obj.Member(
DOT_PAT = re.compile(r"\.([A-Z][A-Za-z0-9_]{2,})\s*\(")


#: ★★★ 2026-10-03（第 4 版）**两个真错，一起修** —— 它们让**每个工具**都被污染：
#:   ★★ 错① **从原始源码抽成员名** ⇒ 把 **docstring 与注释里的示例**也算成了"用法"。
#:      ★ 实测：★ `sw_connect.get_com_member` 的**文档里有示例**
#:        （`InsertDome` / `InsertMoldShutOffSurface` / `RunAnalysis` / `Activate`）⇒
#:        ★★ 而它**被每个模块 import** ⇒ ★★★ **于是那批示例出现在了**每一个工具**上** ✓
#: ★★ 错② **跟图跟进 `sw_connect`** ⇒ ★ 它是 **COM 管道层**（`get_com_member` / `call_co
#: m_member`），
#:      ★ **不是功能实现** ⇒ ★★ 跟它等于把"全仓文档"引进来 ✓
#:   ⇒ ★ 修法：★ **① 抽成员名前先剥注释与 docstring（★ 但保留字符串字面量）**；
#:            ★ **② 跟图跳过"管道层"模块**。
#:   ⚠ 与 **事实 61 定则④**同族：★ **"剥注释"与"剥注释+字符串"是两件事** ——
#:     ★ 这里要**剥注释、留字符串**（★ 因为 `get_com_member(x, "M")` 的成员名是字符串）✓
_PIPE_MODULES = {"sw_connect", "sw_preflight", "sw_api_sldworks", "sw_selection_spec"}


def _strip_comments_and_docstrings(src: str) -> str:
    """★ 只剥 **注释与 docstring**，★ **保留普通字符串字面量**（★ 成员名就在里面）。"""
    try:
        import ast as _ast

        tree = _ast.parse(src)
        drop: list = []
        for node in _ast.walk(tree):
            if isinstance(
                node,
                (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef, _ast.Module),
            ):
                body = getattr(node, "body", [])
                if (
                    body
                    and isinstance(body[0], _ast.Expr)
                    and isinstance(body[0].value, _ast.Constant)
                    and isinstance(body[0].value.value, str)
                ):
                    drop.append((body[0].lineno, body[0].end_lineno))
        lines = src.splitlines()
        for a, b in drop:
            for i in range(a - 1, min(b, len(lines))):
                lines[i] = ""
        #: ★ 再砍行内 `#` 注释（★ 注意别砍进字符串里）
        out = []
        for line in lines:
            q, cut = None, None
            for i, c in enumerate(line):
                if q:
                    if c == q and line[i - 1] != "\\":
                        q = None
                elif c in "\"'":
                    q = c
                elif c == "#":
                    cut = i
                    break
            out.append(line[:cut] if cut is not None else line)
        return "\n".join(out)
    except Exception:  # noqa: BLE001
        return src


def _func_sources(mod_file: Path) -> dict:
    try:
        src = mod_file.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return {}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {}
    out = {}
    #: ★★★ 2026-10-03（第 4 版）**从"剥掉注释与 docstring"的源码里取函数体** ——
    #:   见文件头「错①」：★ 原始源码里，**docstring 的示例**会被当成"用法"抽出来
    #:   （★ 实测：`sw_connect.get_com_member` 的文档示例把 `InsertDome` /
    #:    `InsertMoldShutOffSurface` / `RunAnalysis` / `Activate` **拖进了每一个工具**）✓
    clean = _strip_comments_and_docstrings(src)
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[n.name] = ast.get_source_segment(clean, n) or ""
    return out


def _global_pool() -> dict:
    """★ 全仓函数池（★ 按 `模块名.函数名` 建键 ⇒ **不再按裸名字串**）。

    ★★★ 2026-10-03（接手轮）**两次修正的完整经过**（★ 这条本身是个教训）：
      ★ 第 1 版：★ **只在本模块内**跟调用图 ⇒ ★ 跨模块跟不到 ⇒
        ★★ `sw_topology` 9 个 + `sw_simulation*` 6 个被算成"无引用" ⇒ ★ 无处可放 30–59 个。
      ★★ 第 2 版：★ 改成**按裸函数名**建全仓池 ⇒ ★ 覆盖率从 76.9% 涨到 **91.3%**、
        判据① 从 21.30% 降到 **8.66%** ⇒ ★ 看着像大成功。
      ★★★ **但抽查证伪了它**：★ 随机抽 6 个工具，★ **每一个都含同一批成员**
        —— `Activate` / `InsertDome` / `InsertMoldShutOffSurface` / `RunAnalysis`
        ⇒ ★★ 它们来自某个**同名函数**，被裸名池**串到了每个工具上** ✓
        ⇒ ★★★ **所以 91.3% 是虚高、8.66% 是假象** —— ★ 与**事实 511**（按名字对必然误配）**同族** ✓
      ★ 本版（第 3 版）：★ **按 `模块.函数` 建键**，★ 跟图时**先在本模块找**、
        ★★ **找不到再按该模块的 `import` 解析到真正的来源模块** ⇒ ★ **精确、不串** ✓
    """
    pool = {}
    #: ★★★★ 2026-10-03（接手轮）**扫描范围要含 `subskills/`** ——
    #:   ★ 病灶：★ `scripts/sw_drawing.py` 逐字是一个**动态桥接**：
    #:     ```
    #:     _IMPLEMENTATION = … / "subskills" / "solidworks-engineering-drawing"
    #:                          / "scripts" / "drawing_workflow.py"
    #: _SPEC = importlib.util.spec_from_file_location(…); _SPEC.loader.exec_module(_MODU
    #: LE)
    #:     for _name in __all__: globals()[_name] = getattr(_MODULE, _name)
    #:     ```
    #: ★★ 即：★ **`sw_drawing` 里没有任何 `def`**（★ 实测 `^def` 匹配 **0 个**、★ 文件只
    #:  **29 行**），
    #:     ★★★ **真正的实现在 `subskills/` 下** ✓
    #:   ★★★★ 后果：★ **整个工程图族**（★ 30+ 个工具，★ 它们都委托到 `sw_drawing`）
    #:     抽到的成员**近 0** ⇒ ★ 矩阵把它们算成"低密度格"
    #:     ⇒ ★★ **补能力的排期因此被误导**（★ 见上一轮的记录）✓
    #:   ⇒ ★ 修法：★ **把 `subskills/**/scripts/*.py` 也收进池** ✓
    #:   ★★ 可复用判据：★★ **"扫描范围"本身是一个判据** ——
    #:     ★ 凡"扫某个目录"的工具，★ 都要问一句"**这个仓库还有没有别的地方放着实现**" ✓
    #:     （★ 与**事实 51**「分析范围要贴合组织单元」同族，★ 而本条是它的**目录版**）✓
    for d in ("scripts", "mcp-server"):
        for f in sorted((REPO / d).glob("*.py")):
            stem = f.stem
            for name, src in _func_sources(f).items():
                pool["%s.%s" % (stem, name)] = src
    #: ★★ 子技能里的实现（★ 与本仓 `scripts/` 里的模块**同名同辈**地进池）
    for f in sorted((REPO / "subskills").rglob("scripts/*.py")):
        stem = f.stem
        for name, src in _func_sources(f).items():
            pool.setdefault("%s.%s" % (stem, name), src)
    #: ★★★★★ 2026-10-03（接手轮）**桥接模块** —— ★ 本仓有一类文件**自己没有任何 `def`**
    #: ，
    #:   而是用 `importlib` 把另一个模块的名字转出来（★ `scripts/sw_drawing.py` 逐字）：
    #:     ```
    #:     _IMPLEMENTATION = … / "subskills" / … / "scripts" / "drawing_workflow.py"
    #: _SPEC = importlib.util.spec_from_file_location(…); _SPEC.loader.exec_module(_MODU
    #: LE)
    #:     for _name in __all__: globals()[_name] = getattr(_MODULE, _name)
    #:     ```
    #: ★★ **后果**：★ 池里只有 `drawing_workflow.add_view`，★ **而没有 `sw_drawing.add_v
    #: iew`**
    #:     ⇒ ★★★ 于是 `from scripts import sw_drawing as D` + `D.add_view(…)` **跟不下去**
    #:     ⇒ ★★★★ **整个工程图族（30+ 工具）抽到 0** ✓
    #: ⇒ ★ 修法：★ **认"桥接"这一形态** —— ★ 从文件里抽 `_IMPLEMENTATION` 指向的**目标模
    #: 块名**，
    #:     ★★ 并把 `目标模块.X` 的**键再挂一份到桥接模块名下** ✓
    #:   ★★ 可复用判据：★★ **"模块"不等于"文件"** ——
    #:     ★ 一个 `.py` 可能**只是转发**（★ 本仓有 `sw_drawing` 这种兼容入口）⇒
    #:     ★★★ **凡按"文件 → 函数"建索引的地方，都要处理"转发文件"** ✓
    _BRIDGE_PAT = re.compile(
        r"_IMPLEMENTATION\s*=\s*\(?(.{0,400}?)\)?\s*\n\s*_SPEC", re.S
    )
    _PYNAME_PAT = re.compile(r'"([A-Za-z_]\w*\.py)"')
    for d in ("scripts", "mcp-server"):
        for f in sorted((REPO / d).glob("*.py")):
            try:
                txt = f.read_text(encoding="utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                continue
            if "importlib" not in txt:
                continue
            m2 = _BRIDGE_PAT.search(txt)
            if not m2:
                continue
            inner = _PYNAME_PAT.search(m2.group(1))
            if not inner:
                continue
            target = inner.group(1)[:-3]
            for k, v in list(pool.items()):
                if k.startswith(target + "."):
                    pool.setdefault("%s.%s" % (f.stem, k.split(".", 1)[1]), v)
    return pool


#: ★★ 从源码里抽 `import` 映射：★ `from X import a, b as c` ⇒ `{a: X, c: X}`
_IMPORT_PAT = re.compile(r"^\s*from\s+([A-Za-z_][\w.]*)\s+import\s+(.+)$", re.M)
#: ★★★★ 2026-10-03（接手轮）**新增：模块别名** ——
#:   ★ 病灶：★ `scripts/sw_drawing_expose.py` 逐字有两行：
#:     ```
#:     from scripts import sw_drawing **as D**      ← ★ `from <包> import <模块> as <别名>`
#:     res = **D.add_view**(drawing_model, …)        ← ★★ 用**模块别名**调
#:     ```
#: ★★ 而 `_import_map` 原来只认「**名字 → 模块**」（★ `from X import a as b` 里的 `a` 是
#: **函数**）⇒
#:     ★★★ **不认「模块别名 → 模块」** ⇒ 于是 `D.add_view` **跟不下去** ✓
#:   ★★★★ 后果（★ 实测）：★ **整个工程图族**（★ `sw_drawing_expose` 里 30+ 个工具）
#:     抽到的成员**近 0**（★ `create_projected_view` 0 个 · `create_section_view` 1 个 ·
#:     `set_sheet_scale` 0 个）⇒ ★★★ **矩阵把它们算成"低密度格"** ✓
#: ⇒ ★ 修法：★ **同时抽 `import X as Y` 与 `from P import M as A`（★ 后者当"模块别名"）*
#: *，
#:     ★★ 并在跟图时**把 `A.foo` 解析成 `M.foo`** ✓
_IMPORT_ALIAS_PAT = re.compile(
    r"^\s*import\s+([A-Za-z_][\w.]*)(?:\s+as\s+([A-Za-z_]\w*))?\s*$", re.M
)


#: ★★ 函数池的键的**副本**（★ 由 `main` 在建池后填）—— ★ 供 `_import_map` 判断"这个名字
#: 是不是模块"
_POOL_KEYS: set = set()


def _import_map(mod_file: Path) -> dict:
    """★ 该模块的 `名字 → 来源模块` 映射（★ 用于精确跟跨模块调用）。

    ★★★ 两类都收（★ 见上面两段说明）：
      · ★ **函数名 → 模块**：`from X import f, g as h` ⇒ `{f: X, h: X}`
      · ★★ **模块别名 → 模块**：`from P import M as A` ⇒ `{A: M}` · `import M as A` ⇒ `{A: M}`
        （★ 而 `from P import M`（★ 无 `as`）⇒ `{M: M}` —— ★ 因为用法就是 `M.foo`）✓
    """
    out = {}
    try:
        src = mod_file.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return out
    for m in _IMPORT_PAT.finditer(src):
        srcmod = m.group(1).split(".")[-1]
        for part in m.group(2).split(","):
            part = part.strip().strip("()")
            if not part or part == "*":
                continue
            bits = part.split(" as ")
            name = (bits[1] if len(bits) > 1 else bits[0]).strip()
            if not name.isidentifier():
                continue
            if len(bits) > 1:
                #: ★ `from X import a as b` ⇒ ★ **`b` 指向 `X`**（★ `a` 通常是个**函数**
                #: ）
                out[name] = srcmod
            else:
                #: ★★★ 无 `as` 时**要分辨**：★ `from P import M` 里的 `M` 可能是
                #: ★ **函数**（⇒ 指向 `P`）★ 或 **模块**（⇒ 指向 `M` 自己，★ 用法 `M.foo
                #: `）
                #: ⇒ ★★ **用一个可核的判据**：★ **`M` 在函数池里吗**（★ 即 `M.<某函数>`
                #: 存在）✓
                is_module = any(k.startswith(name + ".") for k in _POOL_KEYS)
                out[name] = name if is_module else srcmod
    #: ★★ `import X as Y` / `import X`
    for m in _IMPORT_ALIAS_PAT.finditer(src):
        mod = m.group(1).split(".")[-1]
        alias = m.group(2) or mod
        if alias.isidentifier():
            out[alias] = mod
    return out


def main() -> int:
    started = time.time()
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "mcp-server"))
    sys.path.insert(0, str(REPO / "scripts"))
    import register_capabilities as rc

    specs = [s for s in rc.all_specs() if getattr(s, "name", None)]

    #: ★ 官方成员集合（★ 用来判"这个成员名是不是官方的"）
    official = set()
    for d in (SWAPI / "types").iterdir():
        if d.is_dir():
            official |= {p.stem for p in d.glob("*.md")}

    rows, cache = [], {}
    #: ★★★ 2026-10-03（第 3 版）：**按 `模块.函数` 键 + import 精确解析**（★ 见 `_global
    #: _pool` 的说明）
    pool = _global_pool()
    _POOL_KEYS.clear()
    _POOL_KEYS.update(pool.keys())  #: ★ 供 `_import_map` 判"这个名字是不是模块"
    imap_cache: dict = {}
    for s in specs:
        mod, fn = getattr(s, "module", "") or "", getattr(s, "function", "") or ""
        body = pool.get("%s.%s" % (mod, fn), "")
        if mod not in imap_cache:
            imap_cache[mod] = _import_map(REPO / "scripts" / ("%s.py" % mod))
        imap = imap_cache[mod]
        #: ★★ 跟**多层**调用图（★ 事实 507：只看 spec 文档会漏，★ 要落到函数体；
        #: ★★ 而"落脚"往往在**第二、三层** —— ★ 第一版只跟一层 ⇒ ★ `fillet` / `chamfer`
        #: /
        #: `extrude_boss` / `sketch_add_line` 这些**明明调 COM 的**被算成"无引用"（74 条
        #: ）。
        #:   ★ 现改为**广度优先跟 3 层**，★ 并把每一层抓到的函数体拼起来抽成员名。
        root = "%s.%s" % (mod, fn)
        seen, frontier, depth = {root}, [root], 0
        parts = [body]
        while frontier and depth < 3:
            nxt = []
            for cur in frontier:
                text_cur = pool.get(cur, "")
                cur_mod = cur.split(".", 1)[0]
                #: ★★★ 只在**候选**里找：① 本模块的函数 ② 该模块 `import` 进来的名字的来
                #: 源模块
                cands = [k for k in pool if k.startswith(cur_mod + ".")]
                for n, srcmod in (imap_cache.get(cur_mod) or {}).items():
                    #: ★★ 跳"管道层"（★ COM 水管，★ 不是功能实现）—— 见文件头的"错②"
                    if srcmod in _PIPE_MODULES:
                        continue
                    cands.append("%s.%s" % (srcmod, n))
                for key in cands:
                    if key in seen:
                        continue
                    short = key.split(".", 1)[1]
                    if re.search(r"\b%s\s*\(" % re.escape(short), text_cur):
                        seen.add(key)
                        nxt.append(key)
                        parts.append(pool.get(key, ""))
                #: ★★★★ 2026-10-03（接手轮）**新增：模块别名调用** `A.foo(` ⇒ `M.foo` ——
                #: ★ 病灶：★ `sw_drawing_expose` 逐字 `from scripts import sw_drawing **
                #: as D**`
                #: 然后 `**D.add_view**(…)` ⇒ ★★ 而上面那圈只找**裸函数名** ⇒ **跟不下去
                #: ** ✓
                #:   ★★★ 后果：★ 整个工程图族（30+ 工具）抽到的成员**近 0** ⇒
                #: 矩阵把它们算成"低密度格" ⇒ ★★ **补能力的排期因此被误导**（见上一轮的
                #: 记录）✓
                #: ★ 修法：★ 用 `_import_map` 里的**别名 → 模块**项，★ 把 `别名.函数` 也
                #: 当候选 ✓
                for alias, srcmod in (imap_cache.get(cur_mod) or {}).items():
                    if srcmod in _PIPE_MODULES or srcmod == alias:
                        continue
                    for member in re.findall(
                        r"\b%s\.([A-Za-z_]\w*)\s*\(" % re.escape(alias), text_cur
                    ):
                        key = "%s.%s" % (srcmod, member)
                        if key in seen or key not in pool:
                            continue
                        seen.add(key)
                        nxt.append(key)
                        parts.append(pool.get(key, ""))
            frontier = nxt
            depth += 1
        called = [n for n in seen if n != "%s.%s" % (mod, fn)]
        text = "\n".join(parts)
        members = sorted(set(CALL_PAT.findall(text)))
        #: ★★★ 2026-10-03 修：本仓**两种调用形态都有** ——
        #:   ① `get_com_member(x, "Member", …)`（★ 本仓新写法）
        #: ② ★★ **点调用** `model.FeatureManager.FeatureFillet(…)`（★ `sw_part.fillet`
        #: 就是这种）
        #: ★ 第一版**只统计 ①** ⇒ ★ `fillet` / `chamfer` / `sketch_add_line` 等**明明调
        #: COM 的**
        #:   被算成"无引用"（64–74 条）⇒ ★★ **判据漏了一整种调用形态**（★ 与事实 51 同族：
        #:   判据的**分析范围**与代码的**组织单元**不匹配）。
        dotted = sorted({m for m in DOT_PAT.findall(text) if m in official})[:60]
        all_members = sorted(set(members) | set(dotted))
        rows.append(
            {
                "tool": s.name,
                "module": mod,
                "function": fn,
                "com_members": all_members,
                "dot_members": dotted,
                "official_hits": [m for m in members if m in official],
                "non_official": [m for m in members if m not in official],
                "helpers_followed": called[:12],
            }
        )

    tot_m = sum(len(r["com_members"]) for r in rows)
    with_m = [r for r in rows if r["com_members"]]
    R = {
        "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "工具数": len(rows),
        "★_有成员的工具": len(with_m),
        "★_无成员的工具": len(rows) - len(with_m),
        "★_成员引用总数": tot_m,
        "★_官方成员命中": sum(len(r["official_hits"]) for r in rows),
        "★_非官方/自封装名": sum(len(r["non_official"]) for r in rows),
        "官方成员总数": len(official),
        "行": rows,
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")

    print(
        "★ 工具 **%d** 条 ⇒ ★★ **有 COM 成员引用的 %d 条（%.1f%%）** · 无的 %d 条"
        % (
            len(rows),
            len(with_m),
            100.0 * len(with_m) / max(1, len(rows)),
            len(rows) - len(with_m),
        )
    )
    print(
        "★ 成员引用合计 **%d** 处 · ★ 其中**是官方成员名**的 **%d** 处 · 其余 %d 处（★ 自封装/参数名）"
        % (tot_m, R["★_官方成员命中"], R["★_非官方/自封装名"])
    )
    print()
    print("★ 样例（前 12 条，★ 看意图 → 实现是否接上了）：")
    print("%-34s %-16s %s" % ("工具", "目标函数", "★ 抽到的 COM 成员"))
    print("-" * 116)
    for r in rows[:12]:
        print(
            "%-34s %-16s %s"
            % (
                r["tool"].replace("solidworks_", "")[:33],
                r["function"][:15],
                ", ".join(r["com_members"][:4])[:56],
            )
        )
    print()
    print("★ 无成员引用的工具（前 16，★ 这些是纯数据/纯读表的）：")
    print(
        "   "
        + ", ".join(
            r["tool"].replace("solidworks_", "") for r in rows if not r["com_members"]
        )[:400]
    )
    print()
    print("★ 产出:", OUT, "（%.1f s）" % (time.time() - started))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
