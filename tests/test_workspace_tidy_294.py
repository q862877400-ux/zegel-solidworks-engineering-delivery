"""★ 规格 294 判据：仓库根只留白名单 · 归档不删文件 · `archive/` 已登记 · 真因（Param 默认值）已修。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/294-workspace-tidy/`（四件套）· `mcp-server/tool_specs_batch81.py`（真因现场）
#         `mcp-server/tool_registry.py:294-312`（`Param` 契约：`default is ...` ⇒ 必填）
#         `AGENTS.md` 铁律 3（白名单外顶层目录要先登记）
# 定位:   ① 根文件必须 ⊆ 白名单（整理前 2843 ⇒ 整理后 29）；
#         ② 归档**不删任何文件**（红线）；
#         ③ `archive/` 已在 `AGENTS.md` 铁律 3 登记；
#         ④ ★★ 真因：`Param` 的 `default` 不得是**中文提示语**（否则会建出同名目录）；
#         ⑤ `run_review` 的 `output_dir` 必须**必填**；
#         ⑥ 边界冻结：本轮只改了**那 1 处** `default`。
# 官方依据: 不适用（纯静态：读文件 + 读 AST，**不连 SolidWorks**）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: ★ 白名单：打包器顶层文件 + 仓库门面 + 被活代码 import 的（★ 见 spec §二）
ALLOWED_ROOT_FILES = {
    # ── 打包器 TOP_LEVEL_FILES（打包器已随桌面端删除） ──
    "README.md", "SKILL.md", "SUBSKILLS.md", "capabilities.yaml", "golden-workflows.yaml",
    "requirements.txt", "requirements-mesh.txt", "requirements-occt.txt", "requirements-pdf.txt",
    # ── 仓库门面 / 许可 / 贡献 / 构建 ──
    "AGENTS.md", "CONTRIBUTING.md", "SECURITY.md", "THIRD-PARTY-NOTICES.md", "LICENSE",
    "README-workspace.md", "RESTART-HANDOFF.md", "REPORTING-STYLE-PROPOSAL.md",
    "INPUT-ANOMALY-INVESTIGATION.md", "toolbox-research.md",
    "package.json", "install.js", "manifest.json", "project.yaml", "uv.lock",
    "pyproject.toml", ".gitignore", ".mcpbignore",
    # ── ★ 被活代码 import（`scripts/sw_jlcfa_*.py` 的 `import shot` / `import ctl`）──
    "shot.py", "ctl.py",
}

ARCHIVE = ROOT / "archive" / "root-scratch"

#: ★ 整理前的根文件数（★ 实测；★ 与归档数一起做**守恒断言**）
ROOT_FILES_BEFORE = 2843
#: ★ 另外单独搬走的**一个目录**（畸形目录 `（必填，无默认值）`，★ 6 个文件）——
#:   ★ 它**不是根文件**，故不计入上面的 2843；★ 这里显式记下，免得守恒式看着对不上。
MALFORMED_DIR_FILES = 6


def test_root_holds_only_the_allowlist():
    """★ FR-001：仓库根只留白名单里的文件（整理前 2843 个）。"""
    actual = {p.name for p in ROOT.iterdir() if p.is_file()}
    extra = sorted(actual - ALLOWED_ROOT_FILES)
    assert not extra, "仓库根出现白名单外的文件（%d 个）：%s" % (len(extra), extra[:12])


def test_nothing_was_deleted():
    """★★ FR-002：归档**不删文件** —— 归档数 + 根保留数 == 整理前总数（守恒）。

    ★ 守恒式：`归档文件数 == 根文件数(2843) - 根保留数(29) + 畸形目录文件数(6)`。
    """
    archived = sum(1 for _ in ARCHIVE.rglob("*") if _.is_file())
    kept = sum(1 for p in ROOT.iterdir() if p.is_file())
    expected = (ROOT_FILES_BEFORE - kept) + MALFORMED_DIR_FILES
    assert archived == expected, (
        "文件数不守恒：归档 %d，按「根 %d → 留 %d」+ 畸形目录 %d 应是 %d ⇒ **有文件被删或漏搬**"
        % (archived, ROOT_FILES_BEFORE, kept, MALFORMED_DIR_FILES, expected)
    )


def test_archive_dir_is_registered_in_agents_md():
    """★ FR-004：`archive/` 是白名单外的新顶层目录 ⇒ 按铁律 3 必须先登记。"""
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8", errors="replace")
    assert "archive/" in text, "AGENTS.md 里没有登记 `archive/`（铁律 3 要求先登记再动手）"
    assert "root-scratch" in text, "AGENTS.md 的登记段没写清 `archive/` 里装的是什么"


#: ★ 中文提示语的形状：一句**给人看的**话被当成值（含中文标点或「必填」这类词）
PLACEHOLDER = re.compile(r"[（(][^）)]*[）)]|必填|无默认值|待填|请填")


def _param_defaults(path: Path):
    """⇒ `[(行号, 参数名, default 的源码文本)]`（★ 只取 `Param(...)` 调用）。"""
    out = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else "")
        if name != "Param":
            continue
        pname = ""
        if node.args and isinstance(node.args[0], ast.Constant):
            pname = str(node.args[0].value)
        for kw in node.keywords:
            if kw.arg == "default":
                out.append((node.lineno, pname, ast.unparse(kw.value)))
    return out


def test_no_param_default_is_a_chinese_placeholder():
    """★★★ FR-005：`Param(default=...)` **不得**是中文提示语。

    ★ 真因：`tool_specs_batch81.py` 曾写 `default="（必填，无默认值）"` ⇒
      `tool_registry.Param.is_required` 逐字是 `self.default is ...`
      ⇒ ★ 那句提示**被判成默认值** ⇒ `run_review` 真机在仓库根建出
      **同名目录**（18.3 MB / 6 文件，★ 见 `specs/294-workspace-tidy/spec.md` §三）。
    """
    bad = []
    for path in sorted((ROOT / "mcp-server").glob("tool_specs_batch*.py")):
        for lineno, pname, src in _param_defaults(path):
            if PLACEHOLDER.search(src):
                bad.append("%s:%d Param(%r, default=%s)" % (path.name, lineno, pname, src))
    assert not bad, "有 `Param` 把**中文提示语**当默认值（会建出同名目录）：\n  " + "\n  ".join(bad)


def test_review_run_output_dir_is_required():
    """★★★ FR-005 的**内容断言**：`run_review` 的 `output_dir` 必须**必填**。

    ★ 铁律 22：棘轮/计数下调必须补「按名字定位」的断言 —— 否则「有人写回去」接不住。
    """
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(ROOT / "scripts"))
    import register_capabilities as rc  # noqa: PLC0415

    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    spec = specs.get("solidworks_review_run")
    assert spec is not None, "`solidworks_review_run` 不在注册表里"
    param = next((p for p in spec.params if p.name == "output_dir"), None)
    assert param is not None, "`solidworks_review_run` 没有 `output_dir` 参数"
    assert param.is_required, (
        "`output_dir` 被判成**可选**（默认值 %r）⇒ 调用方不传时会把那句提示当路径用"
        % (param.default,)
    )


def test_only_the_one_param_default_changed():
    """★ FR-006：边界冻结 —— 全仓 `Param` 里**没有**其它中文提示语默认值（改的是**那一处**）。"""
    hits = []
    for path in sorted((ROOT / "mcp-server").rglob("*.py")):
        for lineno, pname, src in _param_defaults(path):
            if PLACEHOLDER.search(src):
                hits.append("%s:%d" % (path.name, lineno))
    assert hits == [], "除已修的那一处外，又出现了中文提示语默认值：%s" % hits


def test_archive_manifest_is_machine_readable():
    """★ 归档留一份机器可读清单（★ 便于日后按名找回，★ 也是「搬了什么」的证据）。"""
    manifest = ROOT / "output" / "_tidy_result.json"
    assert manifest.is_file(), "缺 `output/_tidy_result.json`（整理结果清单）"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data.get("moved", 0) >= 2800, "归档数异常：%r" % data.get("moved")
    assert len(data.get("keep") or []) >= 25, "保留清单异常"
