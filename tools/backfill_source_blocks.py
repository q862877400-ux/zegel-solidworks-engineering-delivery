"""给早于 §十八 的 .py 补来源块（dry-run 先看，--write 才落盘）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/backfill_source_blocks.py
# 定位:   AGENTS.md §十八 要求新建 .py 带「── 来源 ──」块，但本仓有一批早于该规矩的文件
#         没有。本工具**按可核实的证据**分类生成来源块，★ 不编造「官方依据」：
#           ① 兼容转发壳（importlib 加载真源 / docstring 自称"兼容入口"）⇒ 官方依据「不适用」
#           ② 不调 COM 的纯工具 ⇒ 官方依据「不适用（本仓工具，不调 COM）」
#           ③ 读 C:\\swapi 官方源的分析脚本 ⇒ 官方依据「官方源 C:\\swapi\\types（见文件内引用）」
# ④ 声明式 ToolSpec 批次 ⇒ 官方依据「= 被包装函数的来源（见各 ToolSpec 的 module/functio
# n）」
#           ⑤ 其余调 COM 的 ⇒ 如实写「★ 待逐条回填（本文件早于 §十八）」—— ★ 不假装有依据
# 官方依据: AGENTS.md §十八「新建 .py 的模板：docstring 一行 + 来源块紧随其后」
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = pathlib.Path(__file__).resolve().parents[1]
SKIP = ("__pycache__", "resources/skill", "archive")
COM = re.compile(
    r"get_com_member|SelectByID2|Select4\(|IModelDoc|ISldWorks|ActiveDoc"
    r"|FeatureManager|SketchManager|Dispatch\(|EnsureDispatch"
)
#: ★★ 间接碰 COM：不直接写成员名，但 import 了本仓 COM 封装或 COM 库 ⇒ **不能**写成「不
#: 调 COM」
COM_IMPORT = re.compile(
    r"from\s+\.?sw_connect\b|from\s+\.?sw_preflight\s+import\s+import_com_dependencies"
    r"|import\s+win32com|import\s+comtypes|import\s+pythoncom|from\s+win32com"
    r"|from\s+comtypes"
)
SHIM = re.compile(r"importlib\.util\.spec_from_file_location|兼容入口|兼容转发")
SWAPI = re.compile(r"C:\\\\?swapi|C:/swapi|swapi[\\/]types")
SPEC_BATCH = re.compile(r"ToolSpec\(")
MARK = "# ── 来源 ─────────────────────────────────────────────────────────────"


def first_doc(path: pathlib.Path) -> str:
    try:
        doc = (
            ast.get_docstring(
                ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            )
            or ""
        )
    except Exception:  # noqa: BLE001
        return ""
    line = doc.strip().split("\n")[0].strip()
    return re.sub(r"^[@*★\s]+", "", line)[:80]


#: ★★ 逐条人工确证的「官方依据」—— **只依赖各文件自己的 docstring 与既有台账**，不编造。
#: 出这个表的原因：这些文件的性质是「判本仓自己的运行时行为」，而不是「照官方签名调 COM
#: 」，
#: 所以机械分类只能给出「待回填」；人工读一遍就能给出**如实且具体**的依据。
MANUAL: dict[str, str] = {
    "scripts/sw_macro_guard.py": "本仓防护层（VBA 宏生成护栏）；判据来自 AGENTS.md 铁律 2 的弹窗/超时纪律，"
    "★ 本文件未逐条标注官方页号",
    "tools/_sweep_our_docs.py": "不适用（本仓一次性清场工具：只关**我方**打开的文档，不调官方 API 做建模）",
    "tools/probe_resolver_mark_matrix.py": "★ 判的是**本仓** `register_capabilities.RESOLVERS` 的运行时行为（事实 503 一族），"
    "★ 不涉官方签名",
    "tools/probe_result_serializer.py": "★ 判的是**本仓** `_result` 的 `json.dumps` 兼容性，★ 不涉官方签名",
    "tools/scan_nondict_returns.py": "★ 扫**本仓**工具的目标函数返回类型一致性，★ 不涉官方签名",
    "tools/scan_obsolete_safe.py": "官方源 `C:\\swapi` 的**废弃成员索引**（★ 文件内引 `known-facts` 多处）",
    "tools/scan_obsolete_usage.py": "官方源 `C:\\swapi` 的**废弃成员索引**（★ 拿官方索引去比，不靠人读）",
    "tools/scan_preselect_requiring_tools.py": "★ 扫**本仓**工具族的预选依赖（事实 503 一族），★ 不涉官方签名",
}


def _code_lines(text: str) -> str:
    """只留**非注释**行（★ 避免「注释里提到别的文件」被误判成该文件的性质）。"""
    return "\n".join(ln for ln in text.split("\n") if not ln.lstrip().startswith("#"))


def classify(path: pathlib.Path, text: str) -> tuple[str, str]:
    """返回（类别, 官方依据文本）。"""
    rel = path.relative_to(R).as_posix()
    if rel in MANUAL:
        return "manual", MANUAL[rel]
    code = _code_lines(text)
    if re.search(r"importlib\.util\.spec_from_file_location", code):
        return "shim", "不适用（兼容转发壳：真源见文件内 `_IMPLEMENTATION` 指向的模块）"
    if SPEC_BATCH.search(code):
        return (
            "spec",
            "= 各条 ToolSpec 所包装函数的来源（见同文件内 `module=` / `function=`）",
        )
    touches_com = bool(COM.search(code) or COM_IMPORT.search(code))
    if not touches_com:
        return "pure", "不适用（本仓工具，不调 COM）"
    if SWAPI.search(text) or re.search(r"官方废弃索引|官方源|known-facts", text):
        return "swapi", "官方源 `C:\\swapi\\types\\**`（★ 逐条见文件内引用）"
    if COM_IMPORT.search(code):
        #: ★ 经由本仓 COM 封装 ⇒ 依据在**被调模块**的来源块里，可追溯
        return "deleg", (
            "经由本仓 COM 封装（`sw_connect` / `sw_preflight` / win32com / comtypes）；"
            "★ 各成员签名见被调模块的来源块，本文件为上层封装"
        )
    return (
        "todo",
        "★ 待逐条回填（本文件早于 §十八；★ 不假装有依据 —— 见 `docs/repo-uniformity-report.md`）",
    )


def main() -> int:
    write = "--write" in sys.argv
    rows = []
    for d in ("scripts", "tools", "mcp-server"):
        for f in sorted((R / d).rglob("*.py")):
            s = str(f).replace("\\", "/")
            if any(k in s for k in SKIP):
                continue
            t = f.read_text(encoding="utf-8", errors="replace")
            if "── 来源 ──" in t:
                continue
            rows.append((f, classify(f, t)[0], classify(f, t)[1], first_doc(f)))

    import collections

    print("  ★ 待补 %d 个 · 分类:" % len(rows))
    for k, v in collections.Counter(r[1] for r in rows).most_common():
        print("     %-8s %d" % (k, v))
    print()
    for f, kind, basis, doc in rows:
        rel = f.relative_to(R).as_posix()
        print("  [%-5s] %-46s | %s" % (kind, rel[:46], basis[:64]))

    if not write:
        print("\n  （dry-run：未写盘。加 `--write` 才落盘）")
        return 0

    n = 0
    for f, kind, basis, doc in rows:
        t = f.read_text(encoding="utf-8", errors="replace")
        rel = f.relative_to(R).as_posix()
        block = (
            f"{MARK}\n"
            f"# 仓库:   本项目自身\n"
            f"# 文件:   {rel}\n"
            f"# 定位:   {doc or '（本文件无模块 docstring）'}\n"
            f"# 官方依据: {basis}\n"
            f"# 许可:   本仓库 MIT。无第三方代码引入。\n"
            f"# 覆盖:   全文件\n"
            f"# ─────────────────────────────────────────────────────────────────────\n"
        )
        # 插在首个 import / from 之前；找不到就插在首个非注释非 docstring 行之前
        lines = t.split("\n")
        anchor = None
        for i, ln in enumerate(lines):
            if re.match(r"^(from|import)\s", ln):
                anchor = i
                break
        if anchor is None:
            for i, ln in enumerate(lines):
                if (
                    ln.strip()
                    and not ln.lstrip().startswith("#")
                    and not ln.lstrip().startswith('"""')
                ):
                    anchor = i
                    break
        if anchor is None:
            continue
        new = "\n".join(lines[:anchor] + [block] + lines[anchor:])
        f.write_text(new, encoding="utf-8")
        n += 1
    print(f"\n  ✓ 已补 {n} 个文件的来源块")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
