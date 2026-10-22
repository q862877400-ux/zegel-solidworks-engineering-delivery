"""★ 门禁：写 SolidWorks **全局用户偏好**的每一处都必须是"可还原"的（★ 事实 525）。

（★ 交付纪律：别人的 SolidWorks 设置不该被我们留下痕迹）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（`C:\swapi\types\ISldWorks\SetUserPreference*
# .md`）
# 文件:   `scripts/sw_preference_guard.py`（★ **唯一被认可的写入姿势**：读旧值 → 设 → `f
# inally` 还原）
#         `scripts/check_unreachable_members.py`（★ **带理由豁免**的写法照它 —— 本仓既有模式）
# 定位:   ★★★ **为什么需要它**（★ 2026-10-04 业主体检出的交付问题）：
#   业主问「我们这个项目别人装上，是不是也要改他的 SolidWorks？」—— 核查结论是：
# ★ **本体零改动**（注册表写入 0 处、不写安装目录、不打补丁、不注入，全走官方 COM API）
# ；
# ★★ 而**有一处真落点**：全仓曾有 **8 处 `SetUserPreference*`** 直接改用户的**全局用户偏
# 好**
# （默认模板路径 ×3 / 新建提示 / STL 导出质量 / STL-VRML 导入选项 ×6 / 原点与三轴显示 ×2
# ），
#     ★ 且**多数不还原** ⇒ 装一次我们的工具 = 用户的设置被永久改掉 ✓
#   ⇒ ★ 本门禁把那条纪律**变成可执行的**：★ 每一处裸写都必须满足以下之一 ——
#     ① **落在 `preference_guard` 的 `with` 里**（★ 首选：那是被 10 条负例证明过的姿势）；
#     ② **所在函数的源码里带确认标记** `preference-guard:` **且其后有非空理由**
#        （★ 用于"设"与"还原"分居两个函数的情形，如 `ensure_default_templates` /
#          `restore_default_templates` —— ★ 标记本身就是那条还原链路的说明）；
# ③ **进豁免名单** `docs/preference-write-exemptions.json`（★ 每条带**非空 `reason` + `e
# vidence`**，
#        照 `check_unreachable_members` 的既有模式）。
#
# ⚠ **本门禁的边界（★ 如实写）**：★ 它保证"**写过理由/走过守卫**"，**不证明"还原真的生效
# "**
# —— ★ 后者由 `sw_preference_guard` 的 **10 条负例**（`tests/test_preference_guard.py`）
# 在做 ✓
# ★ 另：它只认 `SetUserPreference*` 这个**名字** ⇒ ★ 走 `sw_preference_guard.write_prefe
# rence`
#     的路径**天然不被拦**（★ 那是被认可的通道，且**只在 guard 内部被调用**）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXEMPTIONS = ROOT / "docs" / "preference-write-exemptions.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★ 扫描根（★ 与 `check_member_names` 的分工不同：本道要覆盖 **`subskills/`**，
#:   因为真有两处偏好写在焊件/圆角那两个验证脚本里）
SCAN_ROOTS = ("scripts", "mcp-server", "subskills", "tools", "tests", "apps")
SKIP_PARTS = ("node_modules", ".venv", "resources", "solidpilot-salvage")
#: ★ 被认可的守卫途径（★ `with` 表达式里出现这些名字即算）
GUARD_NAMES = ("preference_guard", "write_preference")
#: ★ 确认标记：★ 必须**带非空理由**（★ 光是标记不算 —— 那会退化成"盖个章"）。
#: ⚠★ **理由必须与标记在**同一行**：第一版用的是 `\s*`，而 ★ `\s` **含换行**
#:   ⇒ 于是 `# preference-guard:` 后面**空着**时，`\S` 会去匹配**下一行的第一个字符**
#:   ⇒ ★★ "空理由"被判成"有理由"（★ 由负例当场抓出）⇒ ★ 改用 `[ \t]*` ✓
MARKER = re.compile(r"preference-guard[ \t]*[:：][ \t]*(\S.{0,200})")


def _call_name(node: ast.AST) -> str:
    fn = getattr(node, "func", None)
    if isinstance(fn, ast.Attribute):
        return fn.attr
    if isinstance(fn, ast.Name):
        return fn.id
    return ""


def _is_guarded(node: ast.AST, guards: set[int]) -> bool:
    """★ 这个调用是否落在某个 `with <guard>(...)` 的**体内**（★ 用行号区间判）。"""
    return any(lo <= getattr(node, "lineno", -1) <= hi for lo, hi in guards)


def _guard_spans(tree: ast.AST) -> set[tuple[int, int]]:
    """★ 收集所有 `with preference_guard(...):` 的**行号区间**。"""
    spans: set[tuple[int, int]] = set()
    for n in ast.walk(tree):
        if not isinstance(n, ast.With):
            continue
        names = {
            _call_name(item.context_expr)
            for item in n.items
            if isinstance(item.context_expr, ast.Call)
        }
        if names & set(GUARD_NAMES):
            lo = min(getattr(b, "lineno", 0) for b in n.body) if n.body else n.lineno
            hi = (
                max(getattr(b, "end_lineno", lo) or lo for b in n.body)
                if n.body
                else lo
            )
            spans.add((lo, hi))
    return spans


def _enclosing_function(tree: ast.AST, lineno: int):
    """★ 取包住这一行的最内层函数（★ 用于读"那个函数的源码里有没有标记"）。"""
    best = None
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            lo, hi = n.lineno, getattr(n, "end_lineno", n.lineno) or n.lineno
            if lo <= lineno <= hi and (best is None or lo > best.lineno):
                best = n
    return best


def load_exemptions() -> tuple[dict, list[str]]:
    """★ 读豁免名单；★ 条目缺 `reason`/`evidence` 视作**无效**（★ 与事实 62 同口径）。"""
    if not EXEMPTIONS.is_file():
        return {}, []
    try:
        data = json.loads(EXEMPTIONS.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {}, ["★ 豁免名单不是合法 JSON：%s" % exc]
    bad = []
    for item in data.get("exemptions") or []:
        if (
            not str(item.get("reason") or "").strip()
            or not str(item.get("evidence") or "").strip()
        ):
            bad.append("★ 豁免条目缺 reason/evidence：%r" % (item.get("file"),))
    return data, bad


def scan_one(rel: str, src: str, exempt_files: set[str] | None = None) -> list[dict]:
    """★ **判据本体**（可对任意源码字符串调用 —— ★ 负例测试就靠它喂"修复前的原文"）。

    :param rel: 相对路径（★ 只用于豁免名单匹配与报告）。
    :param src: 源码文本。
    :param exempt_files: 豁免文件名集合（★ `None` ⇒ 现读名单）。
    :returns: 违规列表（★ 空 = 这一份源码合规）。
    """
    if exempt_files is None:
        exemptions, _ = load_exemptions()
        exempt_files = {
            str(e.get("file") or "").replace("\\", "/")
            for e in (exemptions.get("exemptions") or [])
        }
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    violations: list[dict] = []
    lines = src.splitlines()
    spans = _guard_spans(tree)
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call) or not _call_name(n).startswith(
            "SetUserPreference"
        ):
            continue
        line = getattr(n, "lineno", 0)
        if _is_guarded(n, spans):
            continue
        fn = _enclosing_function(tree, line)
        body = (
            lines[fn.lineno - 1 : (getattr(fn, "end_lineno", fn.lineno) or fn.lineno)]
            if fn
            else lines
        )
        marker = MARKER.search("\n".join(body))
        if marker and marker.group(1).strip():
            continue
        if rel in exempt_files:
            continue
        violations.append(
            {
                "file": rel,
                "line": line,
                "func": _call_name(n),
                "enclosing": fn.name if fn else "<模块级>",
                "why": (
                    "★ 既不在 `preference_guard` 的 with 里、所在函数也没有带理由的"
                    " `preference-guard:` 标记、也不在豁免名单里"
                ),
            }
        )
    return violations


def scan() -> tuple[list[dict], list[str], int]:
    """扫全仓，回 `(违规, 无效豁免, 看过的文件数)`。"""
    exemptions, bad_exempt = load_exemptions()
    exempt_files = {
        str(e.get("file") or "").replace("\\", "/")
        for e in (exemptions.get("exemptions") or [])
    }
    violations: list[dict] = []
    seen = 0
    for root in SCAN_ROOTS:
        base = ROOT / root
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.py")):
            if any(x in p.parts for x in SKIP_PARTS):
                continue
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            src = p.read_text(encoding="utf-8", errors="replace")
            try:
                ast.parse(src)
            except SyntaxError:
                continue
            seen += 1
            violations.extend(scan_one(rel, src, exempt_files))
    return violations, bad_exempt, seen


def main() -> int:
    violations, bad_exempt, seen = scan()
    exemptions, _ = load_exemptions()
    print(
        "★ 用户偏好写入门禁（★ 事实 525）—— 判据：每一处 `SetUserPreference*` 必须可还原"
    )
    print("   扫了 %d 个 .py（★ 扫描根：%s）" % (seen, " ".join(SCAN_ROOTS)))
    print(
        "   豁免名单：%d 条（%s）"
        % (len(exemptions.get("exemptions") or []), EXEMPTIONS.name)
    )
    for e in exemptions.get("exemptions") or []:
        print("      · %s ⇒ %s" % (e.get("file"), str(e.get("reason"))[:70]))
    for b in bad_exempt:
        print("   [BAD] %s" % b)
    for v in violations:
        print(
            "   [HIT] %s:%d  %s（在 %s 里）"
            % (v["file"], v["line"], v["func"], v["enclosing"])
        )
        print("         %s" % v["why"])
    if violations or bad_exempt:
        print(
            "\n[FAIL] ★ 有 %d 处不可还原的偏好写入 / %d 条无效豁免 —— "
            "★ 正解：① 用 `with preference_guard(...)`；② 或把「设」与「还原」成对写好"
            "并在函数里留 `preference-guard: <理由>`；③ 或进豁免名单（带 reason + evidence）"
            % (len(violations), len(bad_exempt))
        )
        return 1
    print("\n[PASS] 每一处 `SetUserPreference*` 都是可还原的（或已带理由豁免）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
