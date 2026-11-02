"""★ 逐文件诊断台账生成器：给出每个入库文件的机械事实，并保留既有审阅裁决。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/gen_file_audit.py
# 定位:   业主 2026-11-02 指令「一个文件一个文件地诊断……多轮带机械门禁地自动进行，
#           不然你就容易骗我说看完了一起，实际上根本就没看」的落地。★ 本脚本只产
#           **机械事实**（行数 / 语法能否编译 / AST 结构 / 空壳函数 / JSON 能否解析），
#           不产判断；判断由 `scripts/check_file_audit.py` 按枚举强制。
# 官方依据: docs/state/INDEX.md 的记录纪律（不凭记忆报数 / 口径要说出来）；
#           AGENTS.md §铁律 3（archive/ 与 output/ 是归档与产物，不被门禁扫描）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   `git ls-files` 全部入库文件；产物 docs/state/file-audit.jsonl
# ⚠ 幂等：文件内容 sha 未变时，保留既有 verdict/evidence/round，不覆盖人工裁决。
# -----------------------------------------------------------------------------
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import subprocess
import sys
import warnings

sys.stdout.reconfigure(encoding="utf-8")  # 事实 58：管道下 GBK 会崩
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "state" / "file-audit.jsonl"

#: 出册范围（每条给出理由；理由写在 judge 里，不靠记忆）
OUT_OF_SCOPE_PREFIX = {
    "archive/": ("frozen", "AGENTS.md 铁律 3：归档目录只搬不删，不被任何门禁扫描"),
    "output/": ("generated", "构建/运行产物，非源码"),
    "commit-messages/": ("frozen", "提交信息存档，非可执行内容"),
    "solidpilot-salvage": ("excluded", "第三方 salvage，许可受限只读，不参与自研诊断"),
    '.solidpilot-salvage': ("excluded", "第三方 salvage（引号转义目录名），许可受限只读"),
}

#: 无法按内容审阅的二进制
BINARY_EXT = {".png", ".bmp", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".pdf",
              ".sldprt", ".sldasm", ".slddrw", ".stl", ".step", ".stp", ".iges",
              ".zip", ".7z", ".gz", ".dll", ".exe", ".so", ".pyd", ".whl",
              }

#: 入册文件的功能域（决定审阅方式）
CATEGORY_RULES = [
    ("product-code:scripts", "scripts/"),
    ("product-code:mcp", "mcp-server/"),
    ("product-code:apps", "apps/"),
    ("product-code:subskills", "subskills/"),
    ("gate:tools", "tools/"),
    ("test", "tests/"),
    ("spec", "specs/"),
    ("doc", "docs/"),
    ("speckit-config", ".specify/"),
    ("reference", "references/"),
    ("example", "examples/"),
    ("metadata", "metadata/"),
    ("evidence", "_proof/"),
    ("evidence", "evidence/"),
    ("evidence", "batch_evidence/"),
    ("root-config", ""),
]


def category_of(path: str) -> str:
    """按前缀把文件归到功能域。"""
    for name, prefix in CATEGORY_RULES:
        if prefix and path.startswith(prefix):
            return name
        if not prefix and "/" not in path:
            return name
    return "other"


def is_binary(ext: str) -> bool:
    """扩展名是否属于无法按文本审阅的资产。"""
    return ext.lower() in BINARY_EXT


def py_facts(text: str) -> dict:
    """Python 文件的机械事实：能否编译、AST 结构、空壳函数。"""
    facts: dict = {}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            compile(text, "<audit>", "exec")
            facts["compiles"] = True
        except SyntaxError as exc:
            facts["compiles"] = False
            facts["compile_error"] = f"{exc.msg} @ line {exc.lineno}"
            return facts
        facts["compile_warnings"] = len(caught)
    if False:  # pragma: no cover - 保持原结构可读
        exc = None
    try:
        tree = ast.parse(text)
    except SyntaxError:
        facts["parses"] = False
        return facts
    facts["parses"] = True
    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    facts["functions"] = len(funcs)
    facts["classes"] = len(classes)
    facts["undocumented"] = sum(1 for f in funcs if ast.get_docstring(f) is None)
    stubs = []
    for f in funcs:
        body = [b for b in f.body if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))]
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            stubs.append(f.name)
        elif len(body) == 1 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                and body[0].value.value is Ellipsis:
            stubs.append(f.name)
        elif len(body) == 1 and isinstance(body[0], ast.Raise) and body[0].exc is not None:
            src = ast.unparse(body[0].exc)
            if "NotImplementedError" in src:
                stubs.append(f.name)
    facts["stubs"] = len(stubs)
    if stubs:
        facts["stub_names"] = stubs[:12]
    return facts


def purpose_of(path: str, ext: str, text: str, tree: ast.AST | None = None) -> str:
    """取文件的自述用途：py 取模块 docstring 首行，md 取首个标题，其它取首个非空行。"""
    if ext == ".py" and tree is not None:
        doc = ast.get_docstring(tree) or ""
        first = doc.strip().splitlines()[0] if doc.strip() else ""
        if first:
            return first[:160]
    for line in text.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped[:160]
    return ""


def json_facts(text: str) -> dict:
    """JSON 文件能否解析。"""
    try:
        json.loads(text)
        return {"parses": True}
    except Exception as exc:  # noqa: BLE001 - 任何解析失败都记为事实
        return {"parses": False, "parse_error": str(exc)[:120]}


def md_facts(text: str) -> dict:
    """Markdown 的标题数与是否含量化断言（粗判）。"""
    headings = sum(1 for line in text.splitlines() if line.startswith("#"))
    return {"headings": headings, "chars": len(text)}


def load_previous() -> dict:
    """读回既有台账，按 path 建索引，用于保留人工裁决。"""
    if not OUT.exists():
        return {}
    prev = {}
    for line in OUT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        prev[row["path"]] = row
    return prev


def main() -> int:
    """枚举全部入库文件，写台账。"""
    files = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
    paths = [p for p in files.stdout.decode("utf-8", "replace").split("\0") if p]
    prev = load_previous()
    rows = []
    kept = 0
    for path in sorted(paths):
        abs_path = ROOT / path
        ext = pathlib.Path(path).suffix
        try:
            raw = abs_path.read_bytes()
        except OSError:
            raw = b""
        sha = hashlib.sha256(raw).hexdigest()[:16]
        scope, verdict, evidence = "in", "pending", ""
        for prefix, (v, why) in OUT_OF_SCOPE_PREFIX.items():
            if path.startswith(prefix):
                scope, verdict, evidence = "out", v, why
                break
        if scope == "in" and is_binary(ext):
            scope, verdict, evidence = "out", "binary-asset", f"{ext} 为二进制/不可读文本资产"

        facts: dict = {"bytes": len(raw)}
        text = ""
        if not is_binary(ext) and len(raw) < 4_000_000:
            text = raw.decode("utf-8", "replace")
            facts["lines"] = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
            if ext == ".py":
                facts.update(py_facts(text))
                try:
                    facts["purpose"] = purpose_of(path, ext, text, ast.parse(text))
                except SyntaxError:
                    facts["purpose"] = purpose_of(path, ext, text)
            elif ext in (".md", ".markdown"):
                facts["purpose"] = purpose_of(path, ext, text)
            elif ext == ".json":
                facts.update(json_facts(text))
                facts.update(md_facts(text))
        row = {
            "path": path,
            "scope": scope,
            "category": category_of(path),
            "ext": ext,
            "sha": sha,
            "facts": facts,
            "verdict": verdict,
            "evidence": evidence,
            "round": prev.get(path, {}).get("round", 0),
            "checked_by": prev.get(path, {}).get("checked_by", ""),
        }
        old = prev.get(path)
        if old and old.get("sha") == sha and old.get("verdict") not in (None, "", "pending"):
            row["verdict"] = old["verdict"]
            row["evidence"] = old.get("evidence", "")
            row["round"] = old.get("round", 0)
            row["checked_by"] = old.get("checked_by", "")
            kept += 1
        rows.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    pending = sum(1 for r in rows if r["verdict"] == "pending")
    print(f"台账已写：{OUT.relative_to(ROOT)}")
    print(f"  文件总数 {len(rows)} · 入册 {sum(1 for r in rows if r['scope']=='in')} · 出册 {sum(1 for r in rows if r['scope']=='out')}")
    print(f"  pending {pending} · 保留既有裁决 {kept}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
