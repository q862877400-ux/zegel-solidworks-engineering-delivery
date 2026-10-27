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


def _emit(text: str, indent: str) -> str:
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


def _replace(node, text: str, new_source: str) -> tuple:
    """⇒ `(start, end)` 字符区间 + 替换文本（把 `node` 的源码区间换成 `new_source`）。"""
    start = _char_offset(text, node.lineno, node.col_offset)
    end = _char_offset(text, node.end_lineno, node.end_col_offset)
    return (start, end, new_source)


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
        edits: list = []
        for call in _spec_calls(tree):
            name = _tool_name(call, env)
            spec_new = items.get(name)
            if not spec_new:
                continue
            new_doc = spec_new.get("doc")
            doc_kw = _kw(call, "doc")
            if new_doc and doc_kw is not None:
                indent = " " * doc_kw.col_offset
                edits.append(_replace(doc_kw.value, text, _emit(str(new_doc), indent)))
                done[name] = "doc"
            for pcall in _param_calls(call):
                pname = _param_name(pcall)
                new_desc = (spec_new.get("params") or {}).get(pname)
                if not new_desc:
                    continue
                dkw = _kw(pcall, "description")
                if dkw is None:
                    continue
                indent = " " * dkw.col_offset
                edits.append(_replace(dkw.value, text, _emit(str(new_desc), indent)))
                done["%s.%s" % (name, pname)] = "param"
        if not edits:
            continue
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
    missing = [k for k in items if k not in done]
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
    print(
        "★ 零丢失校验：应搬 **%d** 条 · 已搬且**逐字相同** **%d** · 未搬 **%d** · 搬错 **%d**"
        % (len(snap), ok, len(missing), len(wrong))
    )
    for name in (missing + wrong)[:20]:
        print("   ✗ %s" % name)
    return 0 if not missing and not wrong else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="把 ToolSpec.doc 原文搬进 evidence（规格 352 P1）")
    ap.add_argument("--snapshot", action="store_true", help="① 存旧 doc 快照（只读源码）")
    ap.add_argument("--dry-run", action="store_true", help="② 演算会插几处（不写盘）")
    ap.add_argument("--apply", action="store_true", help="③ 真插（幂等）")
    ap.add_argument("--verify", action="store_true", help="④ 回读证明零丢失")
    ap.add_argument("--apply-docs", default="", help="⑤ 把改写的 doc/参数说明按 JSON 映射落盘")
    ap.add_argument("--dry-run-docs", action="store_true", help="配合 --apply-docs：只演算")
    args = ap.parse_args(argv)

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
