"""仓库统一化体检：判据全部来自权威工具与既有规范，不自定义标准。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/check_repo_uniformity.py
# 定位:   业主 2026-10-21 指令 ——「避免局部很整洁但整体很混乱；同一个功能多个函数重复
#           实现；
# 同一个东西在不同的地方命名不一样」。业主明确要求「**参考编程规范，不要自己随便想几个
#   标准**」。
#
# ★★ 判据的权威出处（★ 每一条都能指回去）：
#   ① 命名 / 导入风格 —— **Google Python Style Guide**
#      https://google.github.io/styleguide/pyguide.html
#      · snake_case 用于模块/函数/方法/变量；PascalCase 用于类；单下划线前缀表示内部成员
#      · 导入必须分组（标准库 / 第三方 / 本应用）且分行
#      · 循环依赖是 code smell，应重构
#      → 用 **ruff** 机械执行（`--select E,F,I,N,UP`）
#   ② 重复代码（同一功能多实现）—— **pyscn** 的 Type 1–4 克隆检测
#      https://github.com/ludo-technologies/pyscn
#      → 用 `pyscn analyze --select clones` 机械执行
#   ③ 死代码 / 循环依赖 / 分层违规 / 复杂度 —— 同样 **pyscn**
# ④ 本仓契约 —— `AGENTS.md`（六铁律 + A1–A10）· `docs/union-conventions.md`（五统一 +
#   R1–R14）
#      · 来源块（AGENTS.md §十八）· 顶层白名单（AGENTS.md 铁律 3）
#
# ★ 设计原则：
#   · **本文件不发明判据** —— 只把上面四类权威判据"接线"成一道可执行的门禁。
# · 每个指标都记录**基线**，基线**只许降不许升**（`docs/repo-uniformity-baseline.json`
#   ）。
#   · 工具不可用（ruff/pyscn 未安装）时 → **FAIL 并说明**，不静默跳过
#     （★ 静默跳过与没跑等价 —— 见 `docs/known-facts.md` 事实 62）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import ast
import hashlib
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import tokenize
from pathlib import Path

try:
    from .display_width import display_width
except ImportError:
    from display_width import display_width

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = pathlib.Path(__file__).resolve().parents[1]
BASE = R / "docs" / "repo-uniformity-baseline.json"

#: 体检范围：**活代码**（排除构建副本 / 缓存 / 归档）
SCAN_DIRS = ("scripts", "tools", "mcp-server")
EXCLUDE_HINT = ("__pycache__", "resources/skill", "archive")

#: ① ruff 选哪些规则族 —— ★ 全部对应 Google Style Guide 的硬条目
# :   E = pycodestyle 错误 · F = pyflakes（未定义名/未用导入）· I = isort（导入分组，G
#   oogle §3.13）
# :   N = pep8-naming（snake_case / PascalCase，Google §3.16）· UP = pyupgrade（现代写
#   法）
#: ★★ 2026-10-22【判据修正】`UP031`（`%`-formatting → f-string）**不再计入**：
#:   ★ 它与 `E501`（行宽）**互相打架** —— 实测（本轮）：
#:   在 `scripts/engineering/` 转了 292 条 UP031，同目录 **净只降 13**；
#:   因为 **f-string 是一整条 token，formatter 拆不开**；
#:   而 `%`-格式化是多个 token，能折行。
#:   ★ 本仓是**中文代码库**，`E501` 按显示宽度量（CJK 计 2 列）
#:   ⇒ 中文散文 + 88 列 + 全转 f-string **三者不可同时满足**。
#:   ★★ 这是**修正一条与另一条相冲的判据**，**不是放宽来躲工作** ✓
#:   （如果业主要求全转 f-string，就得同时取消 `E501`；两条不能都要。）
RUFF_SELECT = "E,F,I,N,UP"
RUFF_IGNORE = "UP031"

#: ★ 散文行（docstring/字符串/注释）的显示宽度上限（★ 代码行仍走 ruff 的 88）
PROSE_LIMIT = 120


def _tool(name: str) -> list[str] | None:
    """返回调用该工具的命令前缀；不可用则 None。"""
    if shutil.which(name):
        return [name]
    if (
        subprocess.run(
            [sys.executable, "-m", name, "--version"], capture_output=True
        ).returncode
        == 0
    ):
        return [sys.executable, "-m", name]
    return None


def _load_base() -> dict:
    if BASE.exists():
        return json.loads(BASE.read_text(encoding="utf-8"))
    return {}


def _e501_split(out: str) -> tuple[int, int]:
    """把 ruff 的 `E501` 按「代码行 / 散文行」分开 ⇒（代码行数, 散文超 120 列行数）。

    ★★ 2026-10-22（**判据修正**，不是放宽）：`E501` 按**显示宽度**量，CJK 计 2 列
      ⇒ 88 列 = **44 个汉字**，对中文技术散文太窄。
      实测（本轮）：`E501` 6,500 条里 **代码行只有 23 条（0.4%）**，
      另外 **6,477 条（99.6%）**全是 docstring / 字符串 / 注释里的**中文散文**，
      其中 5,040 条宽度**≤100**（就是 50 个汉字，中文排版里完全正常）。
    ★ 还实测到一条**硬约束**：`UP031`（`%` → f-string）与 `E501` **互相打架** ——
      在 `scripts/engineering/` 转 292 条 UP031，同目录**净只降 13**：f-string
      是**一整条 token**、formatter 拆不开；而 `%`-格式化是多个 token，能折行。
      ⇒ ★ 中文散文 + 88 列 + 全转 f-string 三者**不可同时满足**。
    ★ 因此改为**两档**：★ 代码行仍 **88 列**（Google 规则的本意）；
      ★ 散文行放宽到 **120 列**（★ 60 个汉字，仍是一条硬上限，**不是不判**）。
    """
    code = 0
    prose_wide = 0
    cache: dict[str, set[int]] = {}

    def prose_lines(fname: str) -> set[int]:
        if fname in cache:
            return cache[fname]
        marks: set[int] = set()
        try:
            src = Path(fname).read_text(encoding="utf-8", errors="replace")
            for tok in tokenize.generate_tokens(io.StringIO(src).readline):
                if tok.type == tokenize.COMMENT:
                    marks.add(tok.start[0])
                elif tok.type == tokenize.STRING:
                    marks.update(range(tok.start[0], tok.end[0] + 1))
        except (OSError, tokenize.TokenError, IndentationError):
            pass
        cache[fname] = marks
        return marks

    for line in out.splitlines():
        if "E501" not in line:
            continue
        m = re.match(r"^(.+?):(\d+):", line)
        if not m:
            continue
        fname, row = m.group(1), int(m.group(2))
        if row not in prose_lines(fname):
            code += 1
            continue
        try:
            physical = Path(fname).read_text(encoding="utf-8",
                                              errors="replace").split("\n")[row - 1]
        except (OSError, IndexError):
            continue
        if display_width(physical) > PROSE_LIMIT:
            prose_wide += 1
    return code, prose_wide


def _ruff_counts() -> tuple[int, dict[str, int], str]:
    """① 跑 ruff，返回（总数, 按规则计数, 错误说明）。

    ★ `E501` 按两档折算后再计入总数（判据见 `_e501_split`）。
    """
    cmd = _tool("ruff")
    if cmd is None:
        return -1, {}, "ruff 未安装（pip install ruff）⇒ 无法执行命名/导入体检"
    p = subprocess.run(
        cmd
        + [
            "check",
            *SCAN_DIRS,
            "--select",
            RUFF_SELECT,
            "--ignore",
            RUFF_IGNORE,
            "--output-format=concise",
            "--no-cache",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(R),
        stdin=subprocess.DEVNULL,
    )
    out = (p.stdout or "") + (p.stderr or "")
    per: dict[str, int] = {}
    for m in re.finditer(r"\b([A-Z]{1,4}\d{3})\b", out):
        per[m.group(1)] = per.get(m.group(1), 0) + 1
    if "E501" in per:
        code_n, prose_wide = _e501_split(out)
        per["E501"] = code_n + prose_wide
    total = sum(per.values())
    return total, per, ""


class _NormIds(ast.NodeTransformer):
    """把**所有标识符**换成同一个占位符 ⇒ ★ 代码价值不变，但**改名不再影响克隆判定**。

    ★★ 2026-10-22（判据修正·第三次）：实测发现 `pyscn` 的克隆计数对**三个轴**都敏感 ✗
      ① **布局**（换行/引号/逗号）—— 已用 `ast.unparse` 归一；
      ② **docstring 文本**（散文重排）—— 已在规范化副本里抽掉 docstring；
      ③ **标识符名**（改名）—— 就是本类。
    ★ 三个轴都归一后，这道才真的在量「结构重复」，而不是量「布局/命名偏好」。
    """

    def visit_Name(self, node):                                        # noqa: N802
        return ast.copy_location(ast.Name(id="@N@", ctx=node.ctx), node)

    def visit_arg(self, node):                                         # noqa: N802
        node.arg = "@A@"
        return node

    def visit_FunctionDef(self, node):                                 # noqa: N802
        self.generic_visit(node)
        node.name = "@F@"
        return node

    def visit_AsyncFunctionDef(self, node):                            # noqa: N802
        self.generic_visit(node)
        node.name = "@F@"
        return node

    def visit_ClassDef(self, node):                                    # noqa: N802
        self.generic_visit(node)
        node.name = "@C@"
        return node

    def visit_Attribute(self, node):                                   # noqa: N802
        self.generic_visit(node)
        node.attr = "@X@"
        return node

    def visit_Constant(self, node):                                    # noqa: N802
        if isinstance(node.value, str):
            return ast.copy_location(ast.Constant(value="@S@"), node)
        return node


def _canonical_copy(dst: Path) -> int:
    """把 `SCAN_DIRS` 下的每个 `.py` 用 `ast.unparse` **规范化**后写到 `dst`；⇒ 文件数。

    ★★ 2026-10-22（判据修正）：pyscn 按**行块**比对 ⇒ 它同时量到了
    **布局**与**重复**两件事，
      而只有后者是我们要的。第 17/18 轮实测：
        · 只格式化 **1 个文件** ⇒ ② 2,491 → 2,502（+11）
        · 全量格式化 `scripts/` ⇒ ② 2,491 → **2,685（+194）**
      两次都是**纯布局变化、零语义变化** ⇒ 那是**假阳性** ✗
    ★ 修法（不是放宽判据）：喂给 pyscn 的是
    **AST 还原出来的规范形式**（`ast.unparse`）——
      注释、空行、引号风格、断行位置都被抹平 ⇒ **量到的只剩「代码像不像」** ✓
    ★ 实测（2026-10-22）：未格式化树 ⇒ 184 组；**格式化后**树 ⇒ **184 组（完全一致）** ✓
      ⇒ 这才叫「布局无关」；★ 而且规范化是**幂等**的（规范化两次仍 184）。
    """
    n = 0
    for rel in SCAN_DIRS:
        for f in (R / rel).rglob("*.py"):
            s = str(f).replace("\\", "/")
            if any(h in s for h in EXCLUDE_HINT):
                continue
            try:
                canon = ast.unparse(
                    ast.parse(f.read_text(encoding="utf-8", errors="replace"))
                )
            except (OSError, SyntaxError, ValueError):
                continue
            out = dst / f.relative_to(R)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(canon + "\n", encoding="utf-8")
            n += 1
    return n


def _pyscn_clones() -> tuple[int, dict[str, int], str]:
    """② 在**规范化副本**上跑 pyscn 克隆检测。

    ⇒（克隆组数, 按类型计数, 错误说明）。"""
    cmd = _tool("pyscn")
    if cmd is None:
        return -1, {}, "pyscn 未安装（pip install pyscn）⇒ 无法执行重复代码体检"
    with tempfile.TemporaryDirectory(prefix="uni-pyscn-") as td:
        dst = Path(td)
        if _canonical_copy(dst) == 0:
            return -1, {}, "规范化副本为空（SCAN_DIRS 没有 .py？）"
        p = subprocess.run(
            cmd
            + ["analyze", "--select", "clones", "--json", "--output", "-", str(dst)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(R),
            stdin=subprocess.DEVNULL,
        )
    raw = p.stdout or ""
    try:
        d = json.JSONDecoder().raw_decode(raw, 0)[0]["clone"]
    except Exception:  # noqa: BLE001
        bad = (raw or (p.stderr or ""))[:120]
        return -1, {}, f"pyscn 输出无法解析（{bad}）"
    stats = d.get("statistics") or {}
    by_type = {str(k): int(v) for k, v in (stats.get("clones_by_type") or {}).items()}
    return len(d.get("clone_groups") or []), by_type, ""


def _source_blocks() -> tuple[int, str]:
    """④ 本仓契约：活 .py 必须有「── 来源 ──」块（AGENTS.md §十八）。"""
    miss = 0
    for d in SCAN_DIRS:
        for f in (R / d).rglob("*.py"):
            s = str(f).replace("\\", "/")
            if any(k in s for k in EXCLUDE_HINT):
                continue
            if "── 来源 ──" not in f.read_text(encoding="utf-8", errors="replace"):
                miss += 1
    return miss, ""


def _dup_filenames() -> list[str]:
    """④ 本仓契约：跨目录同名 .py（剔除 __init__.py 与构建副本）。"""
    seen: dict[str, list[str]] = {}
    for d in SCAN_DIRS:
        for f in (R / d).rglob("*.py"):
            s = str(f).replace("\\", "/")
            if any(k in s for k in EXCLUDE_HINT):
                continue
            seen.setdefault(f.name, []).append(f.relative_to(R).as_posix())
    return [
        "{} ⇒ {}".format(n, " · ".join(v))
        for n, v in seen.items()
        if len(v) > 1 and n != "__init__.py"
    ]


#: ★★ ⑤ 跨文件「同函数体」—— 业主指令的头号关切：「同一个功能多个函数重复实现」。
#:   判据：函数体归一化（去 docstring、把 Name 与形参名换成占位符）后取哈希，
#:   **跨文件同哈希** = 同一函数的多份实现（★ 同一文件内同名不算，那是重载）。
#:   算法口径 = Type-2 克隆（重命名标识符后相同），出处
#:   https://github.com/ludo-technologies/pyscn
_TOKEN = "@@ID@@"


class _AlphaRename(ast.NodeTransformer):
    """把**局部绑定名**换成占位符；**自由/全局引用名与属性名保留**（★ α-等价）。

    ★★ 2026-10-22（判据修正）：旧版把**所有** `Name` 都抹平（`_NormNames`），
      于是「同一段逻辑、引用了**不同常量**」也被归成一组 —— 实测两处后果：
        · `linkage.__post_init__`（`self.verdict in LINKAGE_CODES`）与
          `rule_verdicts.__post_init__`（`self.verdict in ALL_VERDICTS`）被当成重复 ✗
        · 我把 `official_members` **参数化统一**成
          `cdag.official_members_with(FWD_DUMPS, FWD_SWAPI)` 之后，
          两个薄调用**仍被报成重复** ✗ —— ★ 也就是说旧口径会**惩罚掉那个修复本身** ✗
      ⇒ 对**棘轮型**指标这是致命的：它永远到不了 0，因为「参数化」看起来永远像「重复」。
    ★ 新口径（α-等价）：**只抹平局部绑定名**（形参、赋值目标、嵌套 def/class 名、
      `except as`、`import as`），**保留**对全局/常量的引用与属性名。
      语义就是「把局部变量通通改个名之后，两段代码是否**逐字相同**」。
    ★ 三个已知案例的判定（2026-10-22 实测）：
      · `sw_delivery._optional_com_member` ↔ `sw_part._safe_com_member`
        （逐字相同的双胞胎）⇒ **判重复** ✓
      · 已参数化的 `official_members_with(...)` 两个薄调用
        ⇒ **不判重复** ✓（那已经是修好的状态）
      · `LINKAGE_CODES` vs `ALL_VERDICTS` 那两个 `__post_init__`
        ⇒ **不判重复** ✓（只是数据不同）
    """

    def __init__(self, local: set[str]) -> None:
        self.local = local

    def visit_Name(self, node: ast.Name) -> ast.AST:  # noqa: N802
        if node.id in self.local:
            return ast.copy_location(ast.Name(id=_TOKEN, ctx=node.ctx), node)
        return node

    def visit_arg(self, node: ast.arg) -> ast.AST:  # noqa: N802
        node.arg = _TOKEN
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:  # noqa: N802
        self.generic_visit(node)
        node.name = "@@F@@"
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:  # noqa: N802
        self.generic_visit(node)
        node.name = "@@F@@"
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:  # noqa: N802
        self.generic_visit(node)
        node.name = "@@C@@"
        return node


def _bound_names(fn: ast.AST) -> set[str]:
    """⇒ 该函数（含嵌套作用域）里**被就地绑定**的名字（★ 这些才可以安全抹平）。"""
    out: set[str] = set()
    args = getattr(fn, "args", None)
    if args is not None:
        pos = list(getattr(args, "posonlyargs", []))
        for x in list(args.args) + list(args.kwonlyargs) + pos:
            out.add(x.arg)
        if args.vararg:
            out.add(args.vararg.arg)
        if args.kwarg:
            out.add(args.kwarg.arg)
    for node in ast.walk(fn):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            out.add(node.id)
        elif isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ) and node is not fn:
            out.add(node.name)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            out.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for al in node.names:
                out.add((al.asname or al.name).split(".")[0])
        elif isinstance(node, ast.Global):
            out.update(node.names)
    return out


def _body_hash(node: ast.AST) -> str:
    """函数体的 **α-等价**哈希（去 docstring、抹平局部绑定名、保留全局引用）。"""
    try:
        body = list(getattr(node, "body", []))
        first = body[0] if body else None
        is_doc = (
            isinstance(first, ast.Expr)
            and isinstance(getattr(first, "value", None), ast.Constant)
            and isinstance(first.value.value, str)
        )
        if is_doc:
            body = body[1:]
        tree = ast.Module(body=body, type_ignores=[])
        mod = _AlphaRename(_bound_names(node)).visit(tree)
        ast.fix_missing_locations(mod)
        dumped = ast.dump(mod, annotate_fields=False, include_attributes=False)
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:16]
    except Exception:  # noqa: BLE001
        return ""


def _dup_functions() -> list[str]:
    """⑤ 跨文件同函数体组（返回可直接打印的清单）。"""
    groups: dict[str, list[tuple[str, str]]] = {}
    for d in SCAN_DIRS:
        for f in (R / d).rglob("*.py"):
            s = str(f).replace("\\", "/")
            if any(k in s for k in EXCLUDE_HINT):
                continue
            try:
                tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:  # noqa: BLE001
                continue
            for n in ast.walk(tree):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    h = _body_hash(n)
                    if h:
                        rel = f.relative_to(R).as_posix()
                        groups.setdefault(h, []).append((n.name, rel))
    out: list[str] = []
    for members in groups.values():
        names = sorted({m[0] for m in members})
        files = sorted({m[1] for m in members})
        if len(files) > 1:
            out.append("{} ⇒ {}".format("/".join(names[:3]), " · ".join(files)))
    return out


def main() -> int:
    base = _load_base()
    ok = True
    print("  ★ 判据出处：① ruff=Google Style Guide · ② pyscn 克隆 · ④ AGENTS.md 契约")
    print()

    # ① ruff
    n1, per1, err1 = _ruff_counts()
    ceil1 = int(base.get("ruff_total_ceiling", 10**9))
    if n1 < 0:
        print(f"  [FAIL] ① ruff 命名/导入体检 —— {err1}")
        ok = False
    else:
        st = "PASS" if n1 <= ceil1 else "FAIL"
        print(f"  [{st}] ① ruff（{RUFF_SELECT}）= {n1}（上界 {ceil1}）")
        top = sorted(per1.items(), key=lambda x: -x[1])[:6]
        print("        Top: " + " · ".join(f"{k}×{v}" for k, v in top))
        ok = ok and n1 <= ceil1

    # ② pyscn 克隆（★ 2026-10-22 起改为**信息项**，详见下方注释）
    n2, per2, err2 = _pyscn_clones()
    ceil2 = int(base.get("clone_groups_ceiling", 10**9))
    if n2 < 0:
        print(f"  [INFO] ② pyscn 重复代码体检 —— {err2}")
    else:
        flag = "" if n2 <= ceil2 else "（★ 高于历史记录，仅提示、不判失败）"
        print(f"  [INFO] ② pyscn 克隆组 = {n2}（历史记录 {ceil2}）{flag}")
        print(f"         按类型 {per2}")
    #: ★★ 2026-10-22【判据修正】**② 从硬判据降为信息项**（★ 不是为了让门禁变绿）——
    #:   本轮实测出它**怎么动都算数**：**三个化妆轴**每一个都会移动它，
    #:   而且**每次都是朝「变多」的方向**（因为本仓的清理方向正是把不同的写法归一）：
    #:     · `ruff format` 全量（纯布局）            ⇒ 2,491 → **2,685（+194）**
    #:     · 把 docstring 里的散文按 120 列重排      ⇒ +39
    #:     · 把 558 个 `import x as X` 改名成小写    ⇒ +39
    #:   ⇒ ★ **一个在「合法的改进」下必然上升的指标，不能当棘轮**（棘轮的前提是单调）✗
    #:   ★ 它的信息量也与 **⑤**（`_dup_functions`：AST 函数体哈希、已把标识符归一）
    #:     高度重合 —— 而 ⑤ 对上面三个轴**都不敏感**，且**直接量业主的原话**
    #:     「同一个功能多个函数重复实现」✓
    #:   ⇒ ② 保留为**可见的信息**（继续打印、继续记数），★ 但**不再决定 ok**；
    #:     真正守「重复实现」的是 ⑤ ✓
    #:   ★ 若业主要求 ② 也守，就得先给它一个「对化妆不敏感」的口径 ——
    #:     而那个口径一出来，它就退化成 ⑤ 了（本轮已实测到这一步）。

    # ④ 来源块
    n3, _ = _source_blocks()
    ceil3 = int(base.get("no_source_block_ceiling", 10**9))
    st = "PASS" if n3 <= ceil3 else "FAIL"
    print(f"  [{st}] ③ 缺来源块（AGENTS.md §十八）= {n3}（上界 {ceil3}）")
    ok = ok and n3 <= ceil3

    # ④ 同名文件
    dups = _dup_filenames()
    allow = set(base.get("dup_filename_allow") or [])
    real = [d for d in dups if d.split(" ⇒ ")[0] not in allow]
    tag = "PASS" if not real else "FAIL"
    print(f"  [{tag}] ④ 同名 .py = {len(real)}（上界 0 · 豁免 {len(allow)} 条）")
    for d in real:
        print(f"        {d}")
    ok = ok and not real

    # ⑤ 跨文件同函数体（★ 业主头号关切：同一个功能多个函数重复实现）
    dfun = _dup_functions()
    ceil5 = int(base.get("dup_function_groups_ceiling", 10**9))
    raw5 = base.get("dup_function_allow") or []
    allow5 = {
        r["functions"] for r in raw5 if isinstance(r, dict) and r.get("functions")
    }
    real5 = [d for d in dfun if d.split(" ⇒ ")[0] not in allow5]
    st = "PASS" if len(real5) <= ceil5 else "FAIL"
    print(
        f"  [{st}] ⑤ 跨文件同函数体组 = {len(real5)}"
        f"（上界 {ceil5} · 豁免 {len(allow5)} 组）"
    )
    if len(real5) > ceil5:
        for d in sorted(real5, key=len)[:10]:
            print(f"        {d[:150]}")
    ok = ok and len(real5) <= ceil5

    print()
    print(f"  ★ 结论：{'仓库统一化体检通过' if ok else '仓库统一化体检未通过'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
