"""★ 门禁：不许再挂「要求调用方先选、却没有任何入口能选」的工具（注册 ≠ 能跑）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁）
# 文件:   scripts/check_preselect_family.py
# 定位:   ★ 本道闸是 **`specs/202-user-coverage-gaps/recon/preselect-family-merged.md`
#           **（277 条
#         总表，2026-10-03 三路并集复核）**§四 通用建议 3** 点名要建的那一条 ✓ ——
#         原文逐字：「★ **补一条静态门禁**：现状是『只有 `batch4`/`batch23`/`batch26`/
#         `batch29`/`batch58`/`batch60`/`batch74` 记得写 `pre_call`』… ★ 这条门禁一次就会
#         抓住本表 **30 条**」✓
#         ★★ 也是 `docs/ROADMAP.md` §一 游标「下一步候选 ①」的落点（按该 recon 继续扫同族）✓
# 机制前提（★ 复核者逐字核过，不是转述）：
#   `mcp-server/tool_registry.py` 的调用序是 **注入解析器 → `extra_op` → `pre_call` →
#   `derived_args` → 目标函数** ⇒ ★ **「建立选区」只有 `pre_call`（第 2 步）与
#   `derived_args`（第 3 步）两个落点** ✓
#   ★★ 而 **事实 503**：`RESOLVERS[inj]` 会**清空选区**（真机证据
#   `output/selection-lifetime-evidence.json`：调过 `RESOLVERS['model']` 之后 `mark1 = 2 → 0`）
#   ⇒ ★★★ **「调用方先选好、我再调工具」这条路经 MCP 表面不可能成立** ——
#     选区**必须**由 `pre_call` 在注入**之后**重建 ✓
# 判据:   ★ **三条同时成立**才算命中（★ 三条缺一都会把好工具报成坏的）：
#     ① **文档在要求先选**：spec 的 `doc` 命中「调用前必须由调用方选中某物」的关键词表；
#     ② **没有建选区的落点**：`pre_call is None` **且** `derived_args is None`；
#     ③ **没有表达选区的入参**：spec 的 `params` 里**没有** `selection` 这种形态的入参。
#   ★★ 为什么必须三条：①保证「它自己说要先选」是**原文**不是推测；②③合起来保证
#     「模型**没有任何办法**满足那个要求」—— 那才是「注册 ≠ 能跑」 ✓
#   ⚠ **本道闸不判「选区建得对不对」**（那要真机，见 recon §三 的分档与 41 条逐条复核）✓
# 输出:   ★ 逐模块列出命中（★ 每行给出**命中的那句原文片段**，★ 便于人工复核是否假阳性）
#   ★★ 存量走**棘轮基线** `docs/preselect-family-baseline.json`（★ 每条带理由）——
#     理由为空不算登记；基线与实况**双向判**（新增 ⇒ 拦；基线腐坏 ⇒ 也报）✓
# 官方依据: 不适用（本项目内部口径；机制见 `tool_registry.py` 与事实 503）。
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import warnings
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★ 中文 Windows 上打印 `⇒` 会 `UnicodeEncodeError: 'gbk' codec`（**事实 58** 那一族）
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")            # type: ignore[attr-defined]
except Exception:                                                         # noqa: BLE001
    pass

BASELINE = ROOT / "docs" / "preselect-family-baseline.json"

#: ★★ ① 的**关键词表**：只收「**调用方必须先选**」这一个语义的表述（中英双份）✓
#:   ⚠ 刻意**不**收裸 `selected` / `selection` —— ★ 那会把「文档在解释自己怎么取选区」的
#:     （比如自建选区的 `hole_wizard`）也报进来（★ 外部清单第 6 类的关键词假阳性，已见一次）✗
PRESELECT_PATTERNS = (
    r"调用前.{0,12}(先选|选中|选择)",
    r"(先|预先|须先|必须先|需要先).{0,8}(选|选中|选择)",
    r"(在|再).{0,6}调用(前|之前).{0,10}选",
    r"caller\s+must\s+(first\s+)?select",
    r"must\s+first\s+select",
    r"before\s+calling\s+this\s+method[^.]{0,80}select",
    r"make\s+the\s+selections?\s+(using|before)",
    r"(pre-?select|preselect)",
    r"select\s+the\s+(required\s+)?(entities|faces?|edges?|profiles?|points?)\s+(first|before)",
    r"the\s+selected\s+(entities|faces?|edges?|profiles?|sketch\s+segments?)",
    r"requires?\s+(a\s+)?(pre-?)?selection",
)
PRESELECT = [re.compile(p, re.I) for p in PRESELECT_PATTERNS]

#: ★★ **否定 / 自建选区** 的排除表（★ 实测必须要有，否则假阳性一眼可见）——
#:   ★ 起因：第一版纯关键词，27 条里当场就有反例：★ `feature_cosmetic_thread` 的自述逐字是
#:     「调用方**不必**先选」、`thicken` 是「★ 本工具**自己**把第一张面按 mark=1 选上」、
#:     `drawing_add_note` 是「**没有选中时**……自由放置」（★ 那两条 recon §三-3.2 已**逐字复核过**
#:     并降级为「无关」）⇒ ★★ **关键词命中 ≠ 它在要求先选** ✓
#:   ★ 这与我核外部清单第 6 类时抓到的假阳性**同型**（`NOT deprecated` 被 `deprecated` 命中）✓
NEGATION = re.compile(
    r"不必先选|不用先选|毋须先选|无需先选|不需要先选|无须先选"
    r"|不必由调用方|不需要调用方"
    r"|自己(选|把|建|代)|自行(选|建)|自动选|会自动选|不代选|代选"
    r"|没有选中时|未选中时|无选中时"
    r"|does\s+not\s+need\s+to\s+select|no\s+selection\s+is\s+needed"
    r"|selects?\s+(it|them)\s+(itself|automatically)|auto-?select",
    re.I)
#: 否定词要在这个窗口内出现才算「它其实不要求先选」（★ 太窄会漏、太宽会误吞，取 ±160 字）
NEGATION_WINDOW = 160


def _normalize(text: str) -> str:
    """★ 去掉 Markdown 强调符再匹配 —— ★ 否则**关键词会被 `**` 劈开** ✗

    ★★ 实测（本文件第一版的第二个假阳性）：★ `feature_cosmetic_thread` 的自述逐字是
      「调用方`**不必**先选`」⇒ ★ **字面上根本没有 `不必先选` 这个连续子串** ⇒
      ★ 否定过滤**看不见它**、于是照报 ✗ —— ★ 与「`NOT deprecated` 被 `deprecated` 命中」同型 ✓
      ⇒ ★ 修法：匹配前统一 `text.replace("*", "")`（★ 只影响匹配与片段展示，★ 不动任何源文件）✓
    """
    return text.replace("*", "")


def _match_snippet(text: str) -> str:
    """⇒ 命中的**那句原文片段**（★ 便于人工复核是不是假阳性）✓

    ★★ 命中后又做一道**否定过滤**：若命中处 ±`NEGATION_WINDOW` 字里出现
      「不必先选 / 自己选 / 没有选中时…」这类表述 ⇒ ★ **不算命中** ✓
    ★ 口径：**逐个命中看**，只有**存在一处「非否定的」要求**才算命中 ✓
    """
    text = _normalize(text)
    for rx in PRESELECT:
        for m in rx.finditer(text):
            lo = max(0, m.start() - NEGATION_WINDOW)
            hi = min(len(text), m.end() + NEGATION_WINDOW)
            if NEGATION.search(text[lo:hi]):
                continue                                # ★ 这一处是否定句 ⇒ 看下一处
            lo2 = max(0, m.start() - 24)
            return text[lo2:m.end() + 40].replace("\n", " ")
    return ""


def _has_selection_param(spec) -> bool:
    """⇒ spec 是否已有「表达选区」的入参（★ `selection` / `*_selection` 形态）✓"""
    for p in (spec.params or []):
        name = getattr(p, "name", "") or ""
        if name == "selection" or name.endswith("_selection"):
            return True
    return False


#: ★★ ④ **函数侧**：「自己能建选区」的信号（★ 有它 ⇒ 它不依赖调用方预选 ⇒ **不是缺陷**）✓
#:   ★ 这一条是照 recon §3.1 的原方法加的：它逐条读过 41 条目标函数体，
#:     把「24 条函数体**零选区 token**」当作「靠官方 API 隐式吃选区」的判据 ✓
#:   ★★ 实测（未加它之前）：21 条里有 3 条是**自建选区**（`create_fold` / `insert_replace_face` /
#:     `create_revolved_surface`）—— 它们**不是缺陷**，却因为文档里提过「先选」被报进来 ✗
SELF_SELECT = re.compile(
    r"SelectByID2|Select4\(|SelectByRay|\bresolve_selection\b|resolve_entity|"
    r"clear_selection|ClearSelection|"
    #: ★★ 2026-10-07（接手轮 · 规格 216 · T-216-05）**补上本仓自己的选择助手名** ——
    #:   ★ 起因：把 14 条逐条读函数体时，实测出 **2 条假阳性**：
    #:     · `sw_assembly.suppress_component` 逐字 `_select_by_id(asm_model.Extension, component_name, "COMPONENT")`
    #:     · `sw_sheet_metal.insert_form_tool_report` 逐字 `SS.select_entity_by_index(model, "FACE", face_int)`
    #:   ★★ 这两条**自己就会选**，★ 却因为 token 集不含这两个名字，被报成「没人能选」✗
    #:   ⚠ 与 `audit_byref_args.BYREF_OK`（只认**裸名**、不认 `sw_connect.out_i4()`）·
    #:     `check_probe_reuse`（判据过宽）**同型** ⇒ ★★ **判据必须覆盖"本仓自己常用的写法"** ✓
    #:   ⚠ 边界（★ 刻意写清）：★ 这里**只加名字**、不加语义 —— ★ 若某函数**调用了**助手却仍
    #:     **没选够**（例如只选了 1 个而需要 2 个），★ 本道**看不见** ⇒ ★ 那一类要靠**真机验证** ✓
    r"_select_by_id|_select_faces_for|_select_com_object|select_component_by_name|"
    #: ★★ 2026-10-07（接手轮 · 规格 216 T-216-06b）**改成「命名约定」而不是逐个点名** ——
    #:   ★ 起因：★ 我给圆顶新写的自选助手叫 `sw_part.select_face_by_index_mark1` ⇒
    #:     ★ 逐个点名的名单**必然漏**（★ 本仓 `sw_selection_spec` 里就有 `select_object` /
    #:     `select_entity_by_index` / `select_by_selector_report` / `select_face_at` … 一族）✗
    #:   ★★ 而本仓的约定是：**凡 `select_*` 函数，就是"把选择交给一个具名助手"** ⇒
    #:     ★ 目标函数里出现 `select_xxx(` ⇒ ★ **它自己会选** ✓
    #:   ⚠ 仍然**不是**放宽到任意调用：★ 必须真的叫 `select_…(`（★ 带左括号 = 是**调用**、不是提及）✓
    r"select_[a-z0-9_]+\s*\(",
    re.I)

_MODULE_CACHE: dict = {}


def _function_source(module: str, func: str) -> str:
    """⇒ 目标函数的源码（★ 找不到就回空串 ⇒ **不回空串当"自建选区"**，宁可按命中处理）✓

    ⚠ 解析时静音 `SyntaxWarning`：★ 本仓有些模块正文里有非 raw 字符串的 `\\s`（★ 与我无关），
      ★ `ast.parse` 会往 stderr 打警告、把我这道闸的输出搅浑（★ 与 `check_probe_reuse` 同型）✓
    """
    if module in _MODULE_CACHE:
        tree, text = _MODULE_CACHE[module]
    else:
        path = ROOT / "scripts" / (module + ".py")
        if not path.is_file():
            _MODULE_CACHE[module] = (None, "")
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", SyntaxWarning)
                    tree = ast.parse(text)
            except SyntaxError:
                tree = None
            _MODULE_CACHE[module] = (tree, text)
        tree, text = _MODULE_CACHE[module]
    if tree is None:
        return ""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func:
            return ast.get_source_segment(text, node) or ""
    return ""


def judge(doc: str, has_pre_call: bool, has_derived_args: bool,
          has_selection_param: bool, function_source: str) -> str:
    """★ **纯函数**：判一条 spec 是不是「要求先选却无法选」。⇒ 命中则回**原文片段**，否则回 `""` ✓

    ★★ 做成纯函数是**为了能被负例测试直接喂样本**（事实 62：门禁只靠负例证明）——
      ★ 否则测试只能改真仓（★ 而改仓会污染工作树）✓
      四条判据全部在这一处，★ 顺序即文档里的 ① ② ③ ④ ✓
    """
    if has_pre_call or has_derived_args:
        return ""                                       # ★ ② 有建选区的落点
    if has_selection_param:
        return ""                                       # ★ ③ 模型有办法表达选区
    snip = _match_snippet(doc)
    if not snip:
        return ""                                       # ★ ① 它自己没说要先选
    if SELF_SELECT.search(function_source or ""):
        return ""                                       # ★ ④ 它自己会选 ⇒ 不是缺陷
    return snip


def scan() -> list:
    """⇒ `[{tool, module, function, snippet}]` —— ★ **四条同时成立**才算命中 ✓"""
    import register_capabilities as rc
    hits = []
    for spec in rc.all_specs():
        snip = judge(spec.doc or "",
                     spec.pre_call is not None,
                     spec.derived_args is not None,
                     _has_selection_param(spec),
                     _function_source(spec.module, spec.function))
        if snip:
            hits.append({"tool": spec.name, "module": spec.module,
                         "function": spec.function, "snippet": snip})
    return sorted(hits, key=lambda h: (h["module"], h["tool"]))


def load_baseline() -> dict:
    if not BASELINE.is_file():
        return {"entries": []}
    try:
        return json.loads(BASELINE.read_text(encoding="utf-8"))
    except Exception as exc:                                              # noqa: BLE001
        raise SystemExit("★ 基线 %s 解析失败：%s" % (BASELINE, exc))


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="「要求先选却无法选」门禁")
    ap.add_argument("--report", action="store_true", help="★ 只打印命中全表（不判基线）")
    args = ap.parse_args(argv[1:])

    hits = scan()

    if args.report:
        print("★ 预选族门禁 · 命中 **%d** 条（判据：文档要求先选 ∧ 无 pre_call/derived_args ∧ 无 selection 入参）"
              % len(hits))
        by_mod: dict = defaultdict(list)
        for h in hits:
            by_mod[h["module"]].append(h)
        for mod in sorted(by_mod):
            print("── %s（%d 条）" % (mod, len(by_mod[mod])))
            for h in by_mod[mod]:
                print("   %-52s %s" % (h["tool"], h["snippet"][:96]))
        return 0

    base = load_baseline()
    entries = base.get("entries") or []
    for e in entries:
        for f in ("tool", "reason"):
            if not str(e.get(f) or "").strip():
                print("★ 基线条目缺字段 `%s`（★ 一个没有理由的豁免等于没写）：%r" % (f, e))
                return 1
    known = {e["tool"] for e in entries}
    got = {h["tool"] for h in hits}

    new = sorted(got - known)
    stale = sorted(known - got)

    print("★ 预选族门禁 —— 命中 %d 条 · 基线认可 %d 条" % (len(got), len(known)))
    if new:
        print()
        print("  ★★ **新增命中 %d 条** ⇒ ★ 这些工具**要求调用方先选、而模型没有任何办法选**" % len(new))
        print("     （★ 事实 503：`RESOLVERS` 会清空选区 ⇒ 选区**必须**由 `pre_call` 在注入之后重建）")
        for tool in new:
            h = next(x for x in hits if x["tool"] == tool)
            print("      %-52s %s" % (tool, h["snippet"][:100]))
        print()
        print("  ★ 修法两条：① 给它加 `pre_call`（照 `tool_specs_batch74.py::_select_faces_for` 的形状）；")
        print("    ② 或若它**根本不需要**调用方先选（自建选区／官方明示可降级）⇒ 登记进")
        print("       docs/preselect-family-baseline.json 并**写明理由**。")
    if stale:
        print()
        print("  ★ **基线腐坏 %d 条** ⇒ ★ 名单里认了、实际已不存在（★ 名单要跟着改）：" % len(stale))
        for tool in stale:
            print("      %s" % tool)
    if not new and not stale:
        print("  ✓ 无新增命中、基线无腐坏")
    return 1 if (new or stale) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
