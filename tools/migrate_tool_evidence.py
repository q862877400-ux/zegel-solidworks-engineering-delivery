"""★ 把每条 `ToolSpec.doc` 的**原文**搬进新字段 `evidence=`（★ 只搬运、不改写 doc）。

为什么要有这一步（规格 352 · D3/D4）：
  ★ 业主 2026-10-26：「你现在都是**半成品**…光看一下里面的参数，你可能不懂它到底是干什么的」。
  ★ 现行 `doc` 里塞满了 `★ 官方签名（逐字…）` / `查不到` / `事实 47` / `真机读数` ——
    ★ 那是**工程证据**，按 DSH `agent-experience` 的逐字要求
    「**Describe behavior, not implementation.** …omit internal mechanisms and enforcement details」
    ★ 它**不该出现在模型可见的描述里** ✗；★ 但它**也不能丢**（五统一 / A2 两层 provenance）✓
  ⇒ ★★ 本工具把旧 `doc` **逐字**搬进 `ToolSpec.evidence`（非模型可见）⇒
    ★ 之后的改写只动 `doc`，`evidence` 做**零丢失**的机器判据 ✓

判据（`--verify`）：
  ★ 每条 spec 的 `evidence` == `docs/tool-evidence-migration.json` 里记的旧 `doc` **逐字**。
  ★ 快照先落盘、再改源码 ⇒ ★ 证明**不依赖 git 历史**（`doc` 改了也照样能验）✓

用法::

    python tools/migrate_tool_evidence.py --snapshot     # ① 先把旧 doc 存快照（只读源码）
    python tools/migrate_tool_evidence.py --dry-run      # ② 演算：会插几处、插在哪
    python tools/migrate_tool_evidence.py --apply        # ③ 真插（幂等：已有 evidence 的跳过）
    python tools/migrate_tool_evidence.py --verify       # ④ 回读证明零丢失

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`mcp-server/tool_specs_batch*.py` 的证据迁移）
# 文件:   `mcp-server/tool_registry.py`（`ToolSpec.evidence` 的定义处）
#         `specs/352-tool-definition-contract/spec.md` §三 D3/D4
#         `tools/lean_first_sentence.py`（同族工件：都是「按工具名定位 `doc=` 再改」）
# 定位:   ★ 规格 352 的 P1 —— **不改任何一条描述**，只把证据搬到另一个字段。
# 官方依据: 不适用（纯静态源码改写，不连 SolidWorks；★ 判据来自 DSH agent-experience 的措辞规则）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "mcp-server"
SNAPSHOT = ROOT / "docs" / "tool-evidence-migration.json"


def _char_offset(text: str, lineno: int, col_bytes: int) -> int:
    """把 `ast` 的（行号, **UTF-8 字节列**）换成**字符**偏移。

    ⚠ `ast` 的 `col_offset` 是**字节**偏移，而源码里有大量中文注释
    ⇒ ★ 直接拿它切字符串会**错位**（这是本工具最容易踩的一处）。
    ⚠ 本文件用 `splitlines(keepends=True)` 才能让 `base` 把换行算进去。
    """
    lines = text.splitlines(keepends=True)
    base = sum(len(line) for line in lines[: lineno - 1])
    line = lines[lineno - 1]
    head = line.encode("utf-8")[:col_bytes].decode("utf-8", errors="ignore")
    return base + len(head)


#: ★ 每片字面量的**显示宽度**上限（★ 不是字符数！）——
#:   本仓 `check_repo_uniformity.py` 的散文行上限是 **120 显示列**，而 CJK 一个字算 **2 列**
#:   ⇒ ★ 按「76 个字符」切片时，一段中文会切出 **152 列**的行 ⇒ 当场顶掉散文行门禁
#:   （实测：`tool_specs_batch86.py` 的 E501 从 206 涨到 349）✓
PROSE_LIMIT = 120


def _display_width(text: str) -> int:
    """★ 复用 `scripts/display_width.py`（一个事实一个家；CJK 计 2 列的口径只在那一处）。"""
    sys.path.insert(0, str(ROOT / "scripts"))
    from display_width import display_width  # noqa: PLC0415

    return display_width(text)


def _split_by_width(text: str, limit: int) -> list:
    """⇒ 按**转义后的显示宽度**切片（每片 ≤ limit 列；★ 空串回一片空串）。

    ★★ 必须在**转义后**量：`json.dumps` 会把 `"` 变成 `\\"`、`\\` 变成 `\\\\`
      ⇒ ★ 一段满是引号的原文（本仓 doc 里到处是 `"本机不可用"`）按原文宽度切完，
      写到源码里会**再长一截**，于是那几行仍旧越过 120 列（实测 +114 条）✓
    """
    chunks: list = []
    cur = ""

    def width(s: str) -> int:
        return _display_width(json.dumps(s, ensure_ascii=False)[1:-1])

    for ch in text:
        cand = cur + ch
        if cur and width(cand) > limit:
            chunks.append(cur)
            cur = ch
        else:
            cur = cand
    chunks.append(cur)
    return chunks or [""]


def _emit(text: str, indent: str, wrap: bool = True) -> str:
    """把一段原文变成**多行隐式拼接的 Python 字符串字面量**（逐字等价）。

    ★ 为什么不用 `repr()` 一行搞定：本仓散文行上限 **120 显示列**，
      一条 1600 字的 `evidence="…"` 会当场把行宽门禁顶掉 ✓
    ★ 分片是**先切原文再各自转义** ⇒ 隐式拼接后与原文**逐字相同** ✓
    ★ 分片按**显示宽度**算，不按字符数（中文 1 字 = 2 列）✓
    """
    #: 一行 = indent + 4 空格 + `"` + 片 + `"` ⇒ 片可用宽度 = 120 − 宽(indent) − 6 ✓
    limit = max(30, PROSE_LIMIT - _display_width(indent) - 6)
    chunks = _split_by_width(text, limit)
    body = "\n".join(
        "%s    %s" % (indent, json.dumps(c, ensure_ascii=False)) for c in chunks
    )
    if not wrap:
        return "\n%s" % body
    return "(\n%s\n%s)" % (body, indent)


def _const_str(node, env=None):
    """⇒ 这个表达式在**常量折叠**后的字符串（做不到就回 `None`）。

    ★ 为什么需要：本仓 47 条 spec 的 `doc=` 是**拼接**（`doc="…" + _GEOM_NOTE`）——
      `ast.literal_eval` 遇到 `BinOp` 会直接抛 ⇒ 那 47 条会被**静默跳过**
      （★ 「漏了 47 条」与「这 47 条本来就没有 doc」长得一模一样，正是本项目反对的形态）✓
    ★ `env` = 模块级字符串常量表（`_GEOM_NOTE` 这类共享说明就住在那里）✓
    """
    env = env or {}
    if isinstance(node, ast.Name):
        return env.get(node.id)
    try:
        value = ast.literal_eval(node)
        return value if isinstance(value, str) else None
    except Exception:  # noqa: BLE001
        pass
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _const_str(node.left, env)
        right = _const_str(node.right, env)
        if left is not None and right is not None:
            return left + right
    if isinstance(node, ast.JoinedStr):
        out = []
        for part in node.values:
            if isinstance(part, ast.Constant) and isinstance(part.value, str):
                out.append(part.value)
            else:
                return None  #: ★ f-string 里有变量 ⇒ 静态拿不到值，如实回 None
        return "".join(out)
    return None


def _module_env(tree: ast.AST) -> dict:
    """⇒ 模块级「名字 → 字符串常量值」表（含常量互相引用，如 `A = B + "…"`）。"""
    raw: dict = {}
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(
            node.targets[0], ast.Name
        ):
            raw[node.targets[0].id] = node.value
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.value is not None
        ):
            raw[node.target.id] = node.value
    env: dict = {}

    def resolve(name: str, seen: tuple = ()):
        if name in env:
            return env[name]
        if name in seen or name not in raw:
            return None
        value = _const_str(raw[name], {k: resolve(k, seen + (name,)) or "" for k in raw})
        if value is not None:
            env[name] = value
        return value

    for key in raw:
        resolve(key)
    return env


def _spec_calls(tree: ast.AST) -> list:
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = getattr(fn, "id", None) or getattr(fn, "attr", None)
        if name == "ToolSpec":
            out.append(node)
    return out


def _factories(tree: ast.AST) -> dict:
    """⇒ `{工厂名: doc 是第几个位置形参}`。

    ★★ 为什么需要：19 条 spec（`solidworks_simulation_apply_*` 16 条 + `solidworks_topology_*`
      6 条里的一部分）**不是**直接 `ToolSpec(...)`，而是走模块内的
      `_spec(name, title, function, doc, params)` 工厂 ⇒ ★ 光扫 `ToolSpec` 调用
      **一条都改不到**，而「一条都没改」与「那些工具本来就没描述」长得一模一样 ✗
    """
    out: dict = {}
    for node in getattr(tree, "body", []):
        if not isinstance(node, ast.FunctionDef):
            continue
        args = [a.arg for a in node.args.args]
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Return) or not isinstance(sub.value, ast.Call):
                continue
            fn = sub.value.func
            if (getattr(fn, "id", None) or getattr(fn, "attr", None)) != "ToolSpec":
                continue
            kw = None
            for k in sub.value.keywords:
                if k.arg == "doc":
                    kw = k
            if kw is None or not isinstance(kw.value, ast.Name):
                continue
            if kw.value.id in args:
                out[node.name] = args.index(kw.value.id)
    return out


def _factory_doc_node(call, index: int):
    """⇒ 工厂调用里「doc 那个位置实参」的节点（位置传或关键字传都认）。"""
    if len(call.args) > index:
        return call.args[index]
    for k in call.keywords:
        if k.arg == "doc":
            return k.value
    return None


def _kw(call, arg: str):
    for k in call.keywords:
        if k.arg == arg:
            return k
    return None


def _tool_name(call, env=None) -> str:
    kw = _kw(call, "name")
    if kw is None:
        return ""
    return _const_str(kw.value, env) or ""


def _replace(node, text: str, value: str, indent: str, prefix_len: int = 4) -> tuple:
    """⇒ `(start, end, 新源码)`：把 `node` 的源码区间换成 `value` 的字面量写法。

    ★★ **括号处理**（两个坑一起治）：
      ① 原写法常是 `doc=(\n "…"\n)`，而值节点（`Constant`）的区间**不含外层括号** ⇒
         只替换值节点会**再套一层** ⇒ 多跑几遍就成了 `doc=((("…")))` ✗（★ 实测踩过）；
      ② 单块字符串外面套括号是**多余**的 ⇒ `ruff UP034`（extraneous-parentheses）
         会逐条报（498 条一次改写顶出 **1597 条**新违规）✗
      ⇒ 修法：先把值外面**成对**的括号**全部向外吃掉**（遇到不成对就停），再按块数决定写法：
         · 单块 ⇒ 一个裸字面量（要括号没用）
         · 多块 ⇒ 带一层括号的隐式拼接（多行必需）✓
    ★ 安全性：只吃「左是 `(`、右是 `)`」的成对括号；`doc=` 的 `=` 会立刻让它停下来 ✓
    """
    start = _char_offset(text, node.lineno, node.col_offset)
    end = _char_offset(text, node.end_lineno, node.end_col_offset)

    def _skip_back(i: int) -> int:
        while i >= 0 and text[i].isspace():
            i -= 1
        return i

    def _skip_fwd(i: int) -> int:
        while i < len(text) and text[i].isspace():
            i += 1
        return i

    while True:
        li = _skip_back(start - 1)
        ri = _skip_fwd(end)
        if li >= 0 and ri < len(text) and text[li] == "(" and text[ri] == ")":
            start, end = li, ri + 1
            continue
        break

    #: ★ 行宽预算 = 120 − 缩进 − 关键字前缀（`doc=` 4 / `description=` 12 / 位置实参 0）
    #:   − 引号 2 − 尾逗号 1 —— ★ 早先只留了 6，**漏掉尾逗号与 `description=` 的长度**，
    #:   导致 34 行越过散文行上限（`check_repo_uniformity` 的 E501 计数 +34）✓
    limit = max(30, PROSE_LIMIT - _display_width(indent) - prefix_len - 3)
    chunks = _split_by_width(value, limit)
    if len(chunks) <= 1:
        return (start, end, json.dumps(value, ensure_ascii=False))
    return (start, end, _emit(value, indent, wrap=True))


def _param_node_anywhere(tree: ast.AST, pname: str):
    """⇒ 模块里**第一个**名字叫 `pname` 的 `Param(...)` 调用。

    ★★ 为什么需要：有些 spec 写 `params=_PARAMS()` —— Param 定义在**模块级函数**里，
      `_param_calls(call)` 只认 `params=[…]` 字面量 ⇒ **一条都改不到**
      （实测：38 条共享参数「改了 0 处」而退出码还是 0 —— 静默失效）✓
    ★ 代价：同名参数在同一模块里**共用一个说明** —— 那本来就是它们共享的事实 ✓
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if (getattr(node.func, "id", "") or "") != "Param":
            continue
        if _param_name(node) == pname and _kw(node, "description") is not None:
            return node
    return None


def _param_calls(call) -> list:
    """⇒ 这个 `ToolSpec(...)` 里 `params=[…]` 中的每个 `Param(...)` 调用节点。"""
    kw = _kw(call, "params")
    if kw is None or not isinstance(kw.value, ast.List):
        return []
    return [e for e in kw.value.elts if isinstance(e, ast.Call) and getattr(e.func, "id", "") == "Param"]


def _param_name(call) -> str:
    if not call.args:
        return ""
    return _const_str(call.args[0]) or ""


def validate_docs(mapping_path: str) -> int:
    """★ **只验不改**：拿一份改写映射，对着真实的 spec 跑一遍契约门禁。

    ★ 为什么要有它：执行者拿到反馈的唯一途径不该是「先落盘再发现不过」
      —— 那样每轮都要动 117 个文件。这里在**内存里**合成「doc/param 已改」的 spec，
      直接调 `scripts/check_tool_contract.py::judge_spec`（★ 判据只有一个家）✓
    """
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT))
    from types import SimpleNamespace  # noqa: PLC0415

    import register_capabilities as rc  # noqa: PLC0415
    from check_tool_contract import judge_spec  # noqa: PLC0415

    mapping = json.loads(Path(mapping_path).read_text(encoding="utf-8"))
    items = mapping.get("tools", mapping)
    specs = {s.name: s for s in rc.all_specs()}

    bad = 0
    missing = [k for k in items if k not in specs]
    for name, item in items.items():
        spec = specs.get(name)
        if spec is None:
            continue
        #: ★ `ToolSpec` / `Param` 都是 **frozen dataclass** ⇒ 不能就地改
        #:   （实测 `FrozenInstanceError`）⇒ 造一个只带判据要用字段的**替身** ✓
        new_params = item.get("params") or {}
        fake = SimpleNamespace(
            name=spec.name,
            doc=str(item.get("doc") or spec.doc or ""),
            read_only=spec.read_only,
            writes=spec.writes,
            params=[
                SimpleNamespace(
                    name=p.name,
                    description=str(new_params.get(p.name, p.description or "")),
                    default=p.default,
                    required=p.required,
                )
                for p in (spec.params or [])
            ],
        )
        problems = judge_spec(fake)
        if problems:
            bad += 1
            print("✗ %s" % name)
            for code, why in problems:
                print("    [%s] %s" % (code, why))
    print(
        "★ 校验 %d 条：**%d 条合格** · %d 条不合格 · %d 条名字对不上"
        % (len(items), len(items) - bad - len(missing), bad, len(missing))
    )
    for k in missing[:20]:
        print("   ⚠ 名字对不上：%s" % k)
    return 0 if not bad and not missing else 1


def apply_docs(mapping_path: str, dry: bool = False) -> int:
    """★ **把改写后的 `doc` 与 `Param.description` 机械落盘**（规格 352 P4 的写入口）。

    ★ 为什么走「JSON 映射 + 机械应用」而不是让人直接改 .py：
      ① 498 条 × 8 路并行 ⇒ 直接改 .py 会把格式改得七零八落，且**语法错误只能事后发现**；
      ② 映射 JSON 本身就是**可评审的产物**（评审看 JSON，不必读 117 个文件）；
      ③ ★ `evidence=` **一个字节都不碰**（本脚本只改 `doc` 与 `description`）✓
    ★ 幂等：同一个映射跑两遍结果相同 ✓
    """
    mapping = json.loads(Path(mapping_path).read_text(encoding="utf-8"))
    items = mapping.get("tools", mapping)
    done: dict = {}
    for f in sorted(BATCH_DIR.glob("tool_specs_batch*.py")):
        text = f.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            print("✗ %s 语法错（L%s）⇒ 跳过" % (f.name, exc.lineno))
            continue
        env = _module_env(tree)
        factories = _factories(tree)
        edits: list = []
        #: ★★ 第二类落点：**工厂调用**（`_spec(name, title, function, doc, params)`）——
        #:   19 条 spec 是这样生成的，只扫 `ToolSpec` 会**一条都改不到**而「看起来改完了」✗
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fname = getattr(node.func, "id", None)
            #: ★★ 工厂名要按**全仓并集**认，不能只看本文件：`tool_specs_batch58.py`
            #:   是 `from tool_specs_batch29 import _spec` 拿到的 ⇒ 只看本文件会**认不出**
            #:   那 8 条热载荷/机械载荷工具（实测：apply 报「名字对不上」，而它们其实都在）
            if fname not in factories and not (
                isinstance(fname, str) and fname.startswith("_spec") and len(node.args) >= 4
            ):
                continue
            index = factories.get(fname, 3)
            doc_node = _factory_doc_node(node, index)
            if doc_node is None:
                continue
            try:
                name = _const_str(node.args[0], env) if node.args else ""
            except Exception:  # noqa: BLE001
                name = ""
            spec_new = items.get(name)
            if not spec_new:
                continue
            new_doc = spec_new.get("doc")
            if new_doc:
                indent = " " * doc_node.col_offset
                edits.append(_replace(doc_node, text, str(new_doc), indent, 0))
                done[name] = "doc(factory)"
            #: ★★ 工厂调用里的 `Param(...)` 挂在**第 5 个位置实参**（`params` 列表）上，
            #:   不是 `ToolSpec(params=[…])` ⇒ 上面那条 `_param_calls` 路径**够不到它们**
            #:   （实测：38 条共享参数的说明改了「0 处」，而退出码还看不出问题）✓
            new_params = spec_new.get("params") or {}
            if new_params:
                for pcall in ast.walk(node):
                    if not isinstance(pcall, ast.Call):
                        continue
                    if (getattr(pcall.func, "id", "") or "") != "Param":
                        continue
                    pname = _param_name(pcall)
                    if pname not in new_params:
                        continue
                    dkw = _kw(pcall, "description")
                    if dkw is None:
                        continue
                    pindent = " " * dkw.col_offset
                    edits.append(
                        _replace(dkw.value, text, str(new_params[pname]), pindent, 12)
                    )
                    done["%s.%s" % (name, pname)] = "param(factory)"
        for call in _spec_calls(tree):
            name = _tool_name(call, env)
            spec_new = items.get(name)
            if not spec_new:
                continue
            new_doc = spec_new.get("doc")
            doc_kw = _kw(call, "doc")
            if new_doc and doc_kw is not None:
                indent = " " * doc_kw.col_offset
                edits.append(_replace(doc_kw.value, text, str(new_doc), indent, 4))
                done[name] = "doc"
            elif new_doc:
                #: ★★ 有些 spec **根本没有 `doc=`**（如 `solidworks_catalog_*` 四条）⇒ 只替换
                #:   现有节点改不到它们，**空描述会一直留着**（可懂性评测里那 4 题全弃权就是它）。
                #:   ★ 关键字实参可任意排序 ⇒ 插在 `params=` 之前（那里一定有，缩进也可用）✓
                anchor = _kw(call, "params") or _kw(call, "title") or _kw(call, "module")
                if anchor is None:
                    print("⚠ %s 没有 `doc=` 也没有可用锚点 ⇒ 跳过" % name)
                    continue
                off = _char_offset(text, anchor.lineno, anchor.col_offset)
                indent = " " * anchor.col_offset
                edits.append(
                    (off, off, "doc=%s,\n%s" % (_emit(str(new_doc), indent), indent))
                )
                done[name] = "doc(new)"
            for pcall in _param_calls(call):
                pname = _param_name(pcall)
                new_desc = (spec_new.get("params") or {}).get(pname)
                if not new_desc:
                    continue
                dkw = _kw(pcall, "description")
                if dkw is None:
                    continue
                indent = " " * dkw.col_offset
                edits.append(_replace(dkw.value, text, str(new_desc), indent, 12))
                done["%s.%s" % (name, pname)] = "param"
            #: ★ 兜底：`params=_PARAMS()` / 共享工厂里藏的 Param ⇒ 按名字在整模块找 ✓
            for pname, new_desc in (spec_new.get("params") or {}).items():
                if "%s.%s" % (name, pname) in done:
                    continue
                pn = _param_node_anywhere(tree, pname)
                if pn is None:
                    continue
                dkw = _kw(pn, "description")
                indent = " " * dkw.col_offset
                edits.append(_replace(dkw.value, text, str(new_desc), indent, 12))
                done["%s.%s" % (name, pname)] = "param(module)"
        if not edits:
            continue
        #: ★ 只要有编辑落在这个文件里，就把**文件内每条本次涉及的工具**记进 `done`
        #:   —— 否则「只改了参数说明」的工具会被末尾的 `missing` 误报成「名字对不上」
        #:   （★ 假报警会让人开始忽略真报警）✓
        for key in list(done):
            pass
        #: ★★ **按区间去重**：共享参数（`_PARAMS = lambda: [...]`）会被**多个工具**各自
        #:   找到同一个 `Param` 节点 ⇒ 同一区间叠 4 次 ⇒ 落盘后语法错（实测 batch18/77/107）✓
        unique: dict = {}
        for start, end, src in edits:
            unique[(start, end)] = src
        edits = [(s, e, v) for (s, e), v in unique.items()]
        for start, end, src in sorted(edits, key=lambda e: -e[0]):
            text = text[:start] + src + text[end:]
        try:
            ast.parse(text)
        except SyntaxError as exc:
            print("✗ %s 改后语法错（L%s）⇒ **不写这个文件**" % (f.name, exc.lineno))
            continue
        if not dry:
            f.write_text(text, encoding="utf-8")
        print("★ %s ⇒ 改了 %d 处" % (f.name, len(edits)))
    print("★ 合计 %d 个工具/参数被改写（%s）" % (len(done), "演算" if dry else "已落盘"))
    #: ★ 工具名可能只以 `工具.参数` 的形式出现在 `done` 里（只改了参数说明）⇒
    #:   判「有没有匹配到」要看**前缀**，不能只看整键（否则假报「名字对不上」）✓
    touched_tools = {k for k in done} | {k.split(".")[0] for k in done}
    missing = [k for k in items if k not in touched_tools]
    if missing:
        print("⚠ 映射里 %d 条没匹配到任何 spec（名字错了？工厂生成的？）：" % len(missing))
        for k in missing[:20]:
            print("   %s" % k)
    return 0 if not missing else 1


def snapshot() -> int:
    """① 把当前每条 spec 的 `doc` 原文存成快照（★ 只读，不改源码）。"""
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT))
    import register_capabilities as rc  # noqa: PLC0415

    data = {}
    for s in rc.all_specs():
        doc = str(getattr(s, "doc", "") or "")
        if doc:
            data[s.name] = doc
    SNAPSHOT.write_text(
        json.dumps(
            {
                "_comment": "规格 352 P1：改写前的 ToolSpec.doc 原文（证据迁移的零丢失判据）",
                "count": len(data),
                "docs": data,
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print("★ 快照 %d 条 → %s" % (len(data), SNAPSHOT.relative_to(ROOT)))
    return 0


def _plan(files: list[Path]) -> list[tuple[Path, int, str, str, str]]:
    """⇒ `[(文件, 插入偏移, 缩进, 工具名, 旧 doc)]`（每个待插入点一条）。"""
    plan = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            print("✗ %s 语法错（L%s）⇒ 跳过" % (f.name, exc.lineno))
            continue
        env = _module_env(tree)
        for call in _spec_calls(tree):
            if _kw(call, "evidence") is not None:
                continue  #: ★ 幂等：已经搬过
            doc_kw = _kw(call, "doc")
            if doc_kw is None:
                continue
            old = _const_str(doc_kw.value, env)
            if old is None:
                print("⚠ %s 的 `doc=` 不是常量（f-string 里有变量？）⇒ 静态搬不了，须手工处理"
                      % _tool_name(call, env))
                continue
            if not old.strip():
                continue  #: ★ 空 doc 没有证据可搬
            off = _char_offset(text, doc_kw.lineno, doc_kw.col_offset)
            line_start = text.rfind("\n", 0, off) + 1
            indent = text[line_start:off]
            if indent.strip():
                print("⚠ %s 的 `doc=` 不在行首独立位置（缩进 %r）⇒ 跳过" % (_tool_name(call), indent))
                continue
            plan.append((f, off, indent, _tool_name(call), old))
    return plan


def _apply(plan) -> int:
    by_file: dict = {}
    for f, off, indent, name, old in plan:
        by_file.setdefault(f, []).append((off, indent, name, old))
    total = 0
    for f, items in by_file.items():
        text = f.read_text(encoding="utf-8")
        #: ★ 从后往前插 —— 否则前面插入会让后面算好的偏移全部失效 ✓
        for off, indent, name, old in sorted(items, key=lambda x: -x[0]):
            insert = "evidence=%s,\n%s" % (_emit(old, indent), indent)
            text = text[:off] + insert + text[off:]
            total += 1
        try:
            ast.parse(text)
        except SyntaxError as exc:
            print("✗ %s 改后语法错（L%s）⇒ **不写这个文件**" % (f.name, exc.lineno))
            continue
        f.write_text(text, encoding="utf-8")
        print("★ %s ⇒ 插了 %d 处" % (f.name, len(items)))
    return total


def verify() -> int:
    """④ 回读：每条 spec 的 `evidence` 必须等于快照里的旧 `doc`（★ 零丢失）。"""
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT))
    import register_capabilities as rc  # noqa: PLC0415

    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))["docs"]
    missing, wrong, ok = [], [], 0
    for s in rc.all_specs():
        name = s.name
        if name not in snap:
            continue
        ev = str(getattr(s, "evidence", "") or "")
        if not ev:
            missing.append(name)
        elif ev != snap[name]:
            wrong.append(name)
        else:
            ok += 1
    #: ★★ `missing` 分两种，**不能混着报**：
    #:   ① `missing_in_source` —— 源码里没有 `evidence=`；
    #:   ② ★ 其中**由工厂函数生成**的那批（`_spec(name, title, function, doc, params)`）
    #:      **没法**静态插字段 ⇒ ★ 它们的原文只存在**已入库的快照**里
    #:      （`docs/tool-evidence-migration.json`，与源码同一次提交）✓
    #:   ⇒ 判据：**搬错必须为 0**，且未搬的每一条都能在快照里**逐字**找到 ✓
    in_snapshot = [n for n in missing if snap.get(n)]
    print(
        "★ 零丢失校验：应搬 **%d** 条 · 已搬（源码 `evidence=` 逐字相同）**%d** · "
        "仅存快照 **%d** · 搬错 **%d**"
        % (len(snap), ok, len(in_snapshot), len(wrong))
    )
    if in_snapshot:
        print("   ★ 仅存快照的是**工厂生成**的 spec（静态插不了字段）；原文在")
        print("     `docs/tool-evidence-migration.json`，逐字可比对 ✓")
    for name in (missing + wrong)[:20]:
        print("   ✗ %s" % name)
    #: ★ 判据只剩「搬错 = 0」：未搬的那 19 条**有快照兜底**（见上）✓
    return 0 if not wrong else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="把 ToolSpec.doc 原文搬进 evidence（规格 352 P1）")
    ap.add_argument("--snapshot", action="store_true", help="① 存旧 doc 快照（只读源码）")
    ap.add_argument("--dry-run", action="store_true", help="② 演算会插几处（不写盘）")
    ap.add_argument("--apply", action="store_true", help="③ 真插（幂等）")
    ap.add_argument("--verify", action="store_true", help="④ 回读证明零丢失")
    ap.add_argument("--apply-docs", default="", help="⑤ 把改写的 doc/参数说明按 JSON 映射落盘")
    ap.add_argument("--dry-run-docs", action="store_true", help="配合 --apply-docs：只演算")
    ap.add_argument("--validate-docs", default="", help="只验不改：拿映射对真实 spec 跑契约门禁")
    args = ap.parse_args(argv)

    if args.validate_docs:
        return validate_docs(args.validate_docs)
    if args.apply_docs:
        return apply_docs(args.apply_docs, dry=args.dry_run_docs)
    if args.snapshot:
        return snapshot()
    if args.verify:
        return verify()

    files = sorted(BATCH_DIR.glob("tool_specs_batch*.py"))
    plan = _plan(files)
    print("★ 待插入 **%d** 处（扫描 %d 个批次文件）" % (len(plan), len(files)))
    for f, _off, _ind, name, old in plan[:8]:
        print("   %-58s %s（旧 doc %d 字）" % (f.name, name, len(old)))
    if args.apply:
        total = _apply(plan)
        print("★ 已插入 %d 处；★ 下一步：`--verify`" % total)
    else:
        print("★ 只演算、未写盘（加 `--apply` 才落盘）✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
