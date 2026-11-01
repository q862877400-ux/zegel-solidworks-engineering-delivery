"""门禁：每个 MCP 工具都必须有**官方 API 页可回溯**的语义登记（禁止凭记忆）。

★ 业主 2026-11-01 原话（本门禁的唯一来源）：
  「修改的时候**不能根据记忆和印象，必须去 SolidWorks 官方 API 文档对照着自己的文档
    确认这个工具到底是干什么的**」＋「这个要求必须落成机械门禁」。

## 它到底在守什么

工具说明（`ToolSpec.doc` 首句）是模型**唯一看得见**的「这工具是干什么的」。它可能是：
  ① 从官方页抄来的 · ② 从实现读出来的 · ③ **凭印象编的**。
三者从文本上分不开 ⇒ 本门禁要求每条工具在台账里交出**可执行证据**：
  · 它调用的每个 COM 成员 → 一条官方页 `C:\\swapi\\types\\<接口>\\<成员>.md` + 页内**逐字锚点**；
  · 它的模型可见首句 → 一条 `claim_evidence`（官方页锚点 或 本仓实现锚点）。
锚点必须**逐字**出现在所指文件里（去掉 markdown 强调符后比较）⇒ 编不出来的引文过不去。

## 台账文件

`docs/tool-official-claims/<批次>.json`，每批一个文件、互不相交。★ 以 `_` 开头的文件
（如 `_draft-all.json`）是**生成器草稿**，门禁**不读** —— 否则机器抄来的锚点会被
当成「人核过的记录」，而这正是本门禁要治的那件事。

## 判据（每条都在 `judge_records()` 里，纯函数）

| 代号 | 判什么 |
|---|---|
| `no-record` | 工具在 `all_specs()` / `tools/list` 里，台账里没有它 |
| `impl-missing` | `impl` 指向的 `<文件>:<函数>` 不存在 |
| `member-uncited` | 实现里调用了成员，台账没登记（**漏查**） |
| `member-extra` | 台账登记了、本工具的**本层提取**没看到（**只进报表**：可能是更深一层的帮手函数，核验人确认后可保留） |
| `page-missing` | 登记的官方页不存在 |
| `page-mismatch` | 官方页 front-matter 的 `type` / `member` 与登记不符（**指错页**） |
| `anchor-not-found` | 锚点在所指文件里逐字找不到（**伪造引文**） |
| `claim-mismatch` | 台账 `claim` ≠ 工具 `doc` 首句（**台账说的 ≠ 模型看到的**） |
| `claim-unanchored` | `claim_evidence` 缺失或锚点找不到 |
| `member-undocumented` | 标了 `documented:false` 却没写 `gap`（★ 有 `gap` 的只进报表：官方页确实查不到时**不许编页**，铁律 5） |
| `unverified` | 没有 `verified`（谁、何时、用什么方法核的） |
| `unknown-tool` | 台账里有、注册表里没有（改名/删除后没同步） |

## 棘轮与它**不能**保证什么

* `docs/tool-official-claims-baseline.json` 只承载「**还没核到的工具**」（`pending` 名单）。
  已有台账的记录一律**硬判** —— 半成品记录不许借基线蒙混；核完一个工具就从 `pending`
  删掉一个 ⇒ **清单只降**。
* 本门禁保证的是**引用类正确**（页对、锚点真、覆盖全）。它**不能**保证语义正确：
  锚点存在 ≠ 你理解对了（同 `dsh-mcp-builder/references/claim-verification.md` §六）。
  ⇒ 语义那一关仍是「核验人真读了官方页」，落成台账的 `verified.notes` 供复核。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把「不许凭记忆改工具」接成硬门禁）
# 文件:   `tools/gen_tool_official_claims.py`（台账草稿生成器）
#         `docs/tool-official-claims/*.json`（台账，按批分文件、互不相交）
#         `docs/tool-official-claims-baseline.json`（棘轮基线，只许降）
#         `tests/test_tool_official_claims_gate.py`（双侧负例 + 反例自检）
#         `specs/353-mcp-tool-official-audit/spec.md`（判据与实测基线）
# 定位:   ★ 业主 2026-11-01：「不能根据记忆和印象…必须去官方 API 文档」⇒
#         把「查过官方页」从**自述**变成**可核对的文件+锚点**。
# 官方依据: ① SolidWorks API 离线文档树 `C:\\swapi\\types\\<接口>\\<成员>.md`
#             （front-matter 逐字含 `type:` / `member:` / `kind:`）
#           ② 成员名反查表 `C:\\swapi\\index\\by_member_name.md`
#             （`- \\`Member\\` [method] on **IInterface** …`）
#           ③ DSH `dsh-mcp-builder` 的断言台账机制
#             （`references/claim-verification.md` §二：`anchor` 必须逐字存在于 source）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   `scripts/` 下可解析的实现文件 + 台账目录；**不连 SolidWorks**
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
LEDGER_DIR = ROOT / "docs" / "tool-official-claims"
BASELINE = ROOT / "docs" / "tool-official-claims-baseline.json"

#: ★ 首句口径**只有一个家**：`scripts/check_tool_contract.py`（判据 K2 用的就是它）。
#:   本文件原先自带一份逐字相同的实现 ⇒ 被仓库统一化门禁的「跨文件同函数体」判据抓到
#:   （实测组数 76 → 77）⇒ 改成 import，不重写第二份 ✓
sys.path.insert(0, str(ROOT / "scripts"))
from check_tool_contract import counts_by_code, first_sentence  # noqa: E402

#: 官方文档树（可移植：读不到时**跳过判据并 exit 0**，与 `check_member_names` 同策）
SWAPI_TYPES = Path(r"C:\swapi\types")
SWAPI_INDEX = Path(r"C:\swapi\index\by_member_name.md")

#: ★ 第二个官方源：**Simulation（cosworks）add-in 的 interop 帮助解包**。
#:   实测 `C:\swapi\types` 里**没有任何 `ICW*` / `CW*` 接口**，而 Simulation/Topology
#:   的工具全挂在那些接口上 ⇒ 只查一棵树会把「有页」的成员误记成「查不到」。
CWORKS_API = Path(r"C:\cworks_en\api")

#: 包装函数形态：这三个是本仓全部「显式点名成员」的入口（`scripts/check_member_names.py` 同表）
WRAP_NAMES = {"get_com_member", "call_com_member", "safe_get_com_member", "get_com_member_raw"}

#: COM 基础设施成员 —— 不是 SolidWorks API，登记它们没有意义
COM_INFRA = {"QueryInterface", "AddRef", "Release", "GetTypeInfo", "GetIDsOfNames", "Invoke"}

#: 不可证明为 COM 的公共对象方法（Python 内置），不参与覆盖判据
PY_BUILTINS = {
    "items", "keys", "values", "get", "append", "extend", "pop", "update", "split",
    "strip", "lower", "upper", "format", "join", "read_text", "write_text", "exists",
    "is_file", "is_dir", "glob", "rglob", "resolve", "replace", "count", "index",
    "startswith", "endswith", "encode", "decode", "copy", "sort", "setdefault",
}

_INDEX_LINE = re.compile(r"^- `(?P<member>[^`]+)` \[\w+\] on \*\*(?P<iface>[A-Za-z_][\w]*)\*\*")


# ══════════════════════════════════════════════════════════════════════
# 文本归一化：**锚点比较的唯一口径**
#
# ★ 为什么必须归一化而不是裸 `in`：官方页把人名/参数写成 `**D1**`（markdown 强调），
#   而在 docstring 里照抄时会带着 `**`；裸比较会把**真引文**判成伪造（实测 244 条引文
#   裸命中 0 条、归一化后命中）⇒ 归一化只去掉**排版**，不去掉**词**。
# ══════════════════════════════════════════════════════════════════════
def normalize(text: str) -> str:
    """⇒ 去掉 markdown 排版与多余空白后的文本（比较锚点用）。

    :param text: 原文（官方页或台账里的锚点）。
    :returns: 小写、去强调符、空白压缩的文本。
    """
    s = str(text or "")
    #: ★ 只去 **markdown 排版**。HTML 的标签剥除在 `read_page()` 里做 ——
    #:   若在这里对**所有**文件跑 `<[^>]+>`，Python 源码里的 `list[str]`、`a < b`
    #:   会被当成标签整段吞掉（实测：31 KB 的 .py 归一化后只剩 25 KB，
    #:   于是 `def <函数名>(` 这种**实现锚点**永远判「找不到」）✓
    #: ★ HTML 实体是**排版**不是词：`&nbsp;` 与空格等价（台账里照抄页面时两种写法都有）。
    #:   不统一它们，同一句话会因为一个实体被判「找不到」——那是假红。
    s = (
        s.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
    )
    s = re.sub(r"[*`#>]+", "", s)
    s = re.sub(r"(?m)^\s*[-–—]\s*", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


from check_tool_contract import first_sentence  # noqa: E402 - 首句口径**只有一个家**（同文件判据 K2）


# ══════════════════════════════════════════════════════════════════════
# 官方页读取
# ══════════════════════════════════════════════════════════════════════
def read_page(path: Path) -> str | None:
    """⇒ 官方页正文；文件不存在返回 None。

    ★ HTML 页（`C:\\cworks_en\\api` 的 cosworks 帮助）在这里**剥标签/还原实体**，
      让锚点可以按纯文本逐字比对；markdown 页原样返回。

    :param path: 官方页路径（`.md` / `.html`）。
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if path.suffix.lower() in {".html", ".htm"}:
        text = re.sub(r"<script.*?</script>|<style.*?</style>|<xml.*?</xml>", " ", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", "\n", text)
        text = (
            text.replace("&nbsp;", " ")
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
        )
    return text


def page_front_matter(text: str) -> dict:
    """⇒ 官方页 front-matter 的 `key: value`（只取文件头 `---` 块内）。

    :param text: 官方页正文。
    """
    out: dict[str, str] = {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return out
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


_CWORKS_PAGE = re.compile(
    r"^SolidWorks\.Interop\.cosworks~SolidWorks\.Interop\.cosworks\.(?P<iface>[A-Za-z_]\w*)"
    r"~(?P<member>[A-Za-z_]\w*)\.html?$"
)


def cworks_member_index(root: Path = CWORKS_API) -> dict[str, list[tuple[str, str]]]:
    """⇒ `{成员名: [(接口, 页路径)]}`：Simulation add-in 帮助解包里的接口成员页。

    ★ 文件名就是身份：`SolidWorks.Interop.cosworks~SolidWorks.Interop.cosworks.ICWStudy~RunAnalysis.html`
      ⇒ 接口 `ICWStudy`、成员 `RunAnalysis`。`_members` / `~I` 开头的聚合页不算成员页。
    ★ 树不在（换机器）⇒ 返回空 dict，不抛。
    """
    out: dict[str, list[tuple[str, str]]] = {}
    if not root.is_dir():
        return out
    for path in root.iterdir():
        if path.suffix.lower() not in {".html", ".htm"}:
            continue
        m = _CWORKS_PAGE.match(path.name)
        if not m or m.group("member").endswith("_members") or m.group("member").startswith("I"):
            continue
        out.setdefault(m.group("member"), []).append((m.group("iface"), str(path)))
    return out


def member_index() -> dict[str, list[tuple[str, str]]] | None:
    """⇒ `{成员名: [(接口, 页路径)]}`；两棵树都读不到时返回 None（页/锚点判据跳过）。

    ★ 合并两个官方源：`C:\\swapi\\index\\by_member_name.md`（sldworks/swconst）
      与 `C:\\cworks_en\\api`（cosworks add-in）。
    """
    idx: dict[str, list[tuple[str, str]]] = {}
    if SWAPI_INDEX.is_file():
        for line in SWAPI_INDEX.read_text(encoding="utf-8", errors="replace").splitlines():
            m = _INDEX_LINE.match(line.strip())
            if not m:
                continue
            member, iface = m.group("member"), m.group("iface")
            idx.setdefault(member, []).append((iface, str(SWAPI_TYPES / iface / (member + ".md"))))
    for member, entries in cworks_member_index().items():
        idx.setdefault(member, []).extend(entries)
    return idx or None


# ══════════════════════════════════════════════════════════════════════
# 实现侧：这工具到底调了哪些 COM 成员
# ══════════════════════════════════════════════════════════════════════
def _base_name(node: ast.AST) -> str:
    """⇒ 属性链最左端的名字（`model.Extension.SelectByID2` ⇒ `model`）。

    :param node: `ast.Attribute` / `ast.Name` / 其它。
    """
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else ""


class FunctionIndex:
    """仓内 `scripts/*.py` + `mcp-server/server.py` 的函数索引（一层委托用）。

    ★ 为什么需要它：543 个工具里 **252 个**是「薄封装」—— 工具函数只调一句
      `sw_assembly.add_component(...)`，COM 成员在**被调函数**里。不跨这一层，
      台账对一半工具就是空的（实测），门禁也就守不住那一半。
    ★★ 只跨**一层**、且只跨**仓内有定义的函数**：再深就变成猜测调用图，
      而「猜」正是本门禁要治的病（覆盖边界写进 spec §五）。
    """

    def __init__(self) -> None:
        self._by_file: dict[Path, ast.AST | None] = {}
        self._index: dict[str, list[Path]] = {}

    def tree(self, path: Path) -> ast.AST | None:
        """⇒ 该文件的 AST（解析失败返回 None，**不抛**）。

        :param path: `.py` 路径。
        """
        if path not in self._by_file:
            try:
                self._by_file[path] = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except (OSError, SyntaxError):
                self._by_file[path] = None
        return self._by_file[path]

    def build(self, roots: list[Path]) -> FunctionIndex:
        """⇒ 自己（链式），扫描这些根下的 `.py`，登记 `函数名 → [文件]`。

        :param roots: 目录或文件列表。
        """
        for root in roots:
            files = sorted(root.glob("*.py")) if root.is_dir() else [root]
            for path in files:
                tree = self.tree(path)
                if tree is None:
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        self._index.setdefault(node.name, []).append(path)
        return self

    def node(self, path: Path, name: str) -> ast.AST | None:
        """⇒ `(文件, 函数名)` 的函数节点（同名取第一个）。

        :param path: 文件。
        :param name: 函数名。
        """
        tree = self.tree(path)
        if tree is None:
            return None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                return node
        return None

    def callees(self, node: ast.AST) -> list[tuple[Path, str]]:
        """⇒ 这个函数体里调用的、**仓内有定义**的函数（一层）。

        :param node: 函数 AST 节点。
        """
        out: list[tuple[Path, str]] = []
        seen: set[tuple[Path, str]] = set()
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Call):
                continue
            name = sub.func.id if isinstance(sub.func, ast.Name) else getattr(sub.func, "attr", "")
            if not name:
                continue
            for path in self._index.get(name, []):
                if (path, name) not in seen:
                    seen.add((path, name))
                    out.append((path, name))
        return out


def _members_of_fn(node: ast.AST, known: set[str]) -> tuple[dict[str, list[int]], dict[str, list[str]]]:
    """⇒ `(成员 → 行号, 成员 → 接收者提示)`：一个函数体**直接**调用的 COM 成员。

    ★ **接收者提示**（`model.SketchManager.InsertSketch` ⇒ `SketchManager`）用来把
      成员归到**正确的接口页**：`InsertSketch` 同时存在于 `IModelDoc2`（已废弃）与
      `ISketchManager`，只按名字取第一个会把「现在用的是哪个接口」指错。

    :param node: 函数 AST 节点。
    :param known: 官方成员名集合（直接属性调用只用它做保守过滤）。
    """
    members: dict[str, list[int]] = {}
    hints: dict[str, list[str]] = {}

    def add(name: str, line: int, hint: str = "") -> None:
        members.setdefault(name, []).append(int(line or 0))
        if hint:
            hints.setdefault(name, []).append(hint)

    for sub in ast.walk(node):
        if (
            isinstance(sub, ast.Call)
            and isinstance(sub.func, ast.Name)
            and sub.func.id in WRAP_NAMES
            and len(sub.args) >= 2
            and isinstance(sub.args[1], ast.Constant)
            and isinstance(sub.args[1].value, str)
        ):
            hint = _base_name(sub.args[0])
            receiver = sub.args[0]
            while isinstance(receiver, ast.Attribute):
                hint = receiver.attr
                break
            add(sub.args[1].value, getattr(sub, "lineno", 0), hint if hint else "")

    com_objs = {
        a.arg
        for a in list(getattr(node, "args", None).args if hasattr(node, "args") else [])
        + list(getattr(node, "args", None).kwonlyargs if hasattr(node, "args") else [])
        if a.arg not in {"self", "cls"}
    }
    for sub in ast.walk(node):
        if isinstance(sub, ast.Assign) and len(sub.targets) == 1 and isinstance(sub.targets[0], ast.Name):
            src = sub.value.func if isinstance(sub.value, ast.Call) else sub.value
            if _base_name(src) in com_objs or isinstance(sub.value, (ast.Call, ast.Attribute)):
                com_objs.add(sub.targets[0].id)
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            name = sub.func.attr
            if name in COM_INFRA or name in PY_BUILTINS:
                continue
            if _base_name(sub.func.value) in com_objs and name in known:
                hint = getattr(sub.func.value, "attr", "")
                add(name, getattr(sub, "lineno", 0), hint)
    return members, hints


def impl_members(impl_path: Path, func_name: str, known: set[str], index: FunctionIndex | None = None) -> dict:
    """⇒ 一个实现函数**实际驱动**的 COM 成员（直接 + **一层**仓内委托）。

    口径（三条，与 `scripts/check_member_names.py::find_direct_member_access` 同源）：
      ① 包装形态（`get_com_member` / `call_com_member` 的第二个实参是成员名字符串）这类**显式点名**；
      ② 直接属性调用 `obj.M(...)`，且 `M` **在官方成员索引里存在**（⇒ Python 内置方法
         天然不会进来）；`obj` 须是「本函数的形参」或「由属性/调用派生出来的名字」；
      ③ 被本函数调用、且**在本仓有定义**的函数，按同一口径再收一层（薄封装工具靠这条）。

    :param impl_path: 实现文件。
    :param func_name: 函数名。
    :param known: 官方成员名集合。
    :param index: 仓内函数索引（None = 不做第 ③ 条）。
    :returns: `{"found": bool, "members": {名字: [行号]}, "error": str}`。
    """
    tree = None
    try:
        tree = ast.parse(impl_path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError) as exc:
        return {"found": False, "members": {}, "error": "%s: %s" % (type(exc).__name__, exc)}
    fn = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            fn = node
            break
    if fn is None:
        return {"found": False, "members": {}, "error": "函数 %r 不在 %s" % (func_name, impl_path.name)}

    members, hints = _members_of_fn(fn, known)
    if index is not None:
        visited = {(impl_path, func_name)}
        for path, name in index.callees(fn):
            if (path, name) in visited:
                continue
            visited.add((path, name))
            node = index.node(path, name)
            if node is None:
                continue
            sub_members, sub_hints = _members_of_fn(node, known)
            for member, lines in sub_members.items():
                members.setdefault(member, lines)
            for member, hs in sub_hints.items():
                hints.setdefault(member, hs)
    return {"found": True, "members": members, "hints": hints, "error": ""}


# ══════════════════════════════════════════════════════════════════════
# 台账
# ══════════════════════════════════════════════════════════════════════
def load_ledger(ledger_dir: Path) -> tuple[dict[str, dict], list[str]]:
    """⇒ `({工具名: 记录}, [读不了的台账文件])`。

    :param ledger_dir: 台账目录（每个 `.json` 一个批次文件）。
    """
    records: dict[str, dict] = {}
    broken: list[str] = []
    if not ledger_dir.is_dir():
        return records, broken
    for path in sorted(ledger_dir.glob("*.json")):
        #: ★ 以 `_` 开头的是**草稿**（生成器产物），不进台账读音 ——
        #:   否则「机器抄来的锚点」会被当成「人核过的记录」（本门禁治的正是这件事）✓
        if path.name.startswith("_"):
            continue
        #: ★ `review-*.json` 是**复核暂存档**（由 `tools/merge_claim_reviews.py` 合并进
        #:   `B*.json`）。它不进台账读音 —— 否则一份写了一半的复核档会被当成已核记录 ✓
        #: ★ 只在**默认台账目录**里跳过复核暂存档；`--ledger <临时目录>` 时要读它们 ——
        #:   否则复核人没法用门禁自检自己写的那份（实测踩过：拷进临时目录被判「有台账 0」）✓
        if path.name.startswith("review-") and path.parent == LEDGER_DIR:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            broken.append("%s（%s）" % (path.name, exc))
            continue
        for rec in data.get("records") or []:
            name = str(rec.get("tool") or "").strip()
            if not name:
                broken.append("%s（有记录缺 tool 字段）" % path.name)
                continue
            records[name] = rec
    return records, broken


def resolve_impl(rel: str) -> Path:
    """⇒ 实现文件的真实路径（兼容 `scripts/engineering.catalog.py` 这种**点分模块名**）。

    ★ 为什么需要：`ToolSpec.module` 有 5 个工具是点分的（`engineering.catalog`），
      直接拼 `scripts/<module>.py` 会得到不存在的路径 ⇒ 那 5 条会被误判 `impl-missing`。

    :param rel: 台账里的 `相对路径:函数名` 的前半段。
    """
    direct = ROOT / rel
    if direct.is_file():
        return direct
    p = Path(rel)
    if "." in p.stem:
        alt = p.parent.joinpath(*p.stem.split(".")).with_suffix(".py")
        if (ROOT / alt).is_file():
            return ROOT / alt
    return direct


def judge_record(rec: dict, spec_doc: str, known: set[str] | None, index: "FunctionIndex | None" = None,
                 advisories: list[dict] | None = None) -> list[tuple[str, str]]:
    """⇒ 一条台账记录违反了哪些判据（空列表 = 合规）。

    ★ 纯函数：只看记录文本 + 官方页 + 实现文件，不碰注册表 ⇒ 负例可直接构造 ✓

    :param rec: 台账记录。
    :param spec_doc: 该工具当前的 `doc`（模型可见）。
    :param known: 官方成员名集合；None = 官方文档树不可用（跳过页/锚点判据）。
    :param index: 仓内函数索引（决定「实现调了哪些成员」的口径）。
    """
    out: list[tuple[str, str]] = []
    impl = str(rec.get("impl") or "")
    if not impl:
        out.append(("impl-missing", "记录没有 impl"))
        return out
    #: ★ 用 `rpartition` 而不是 `partition`：绝对路径自带盘符冒号（`C:\...`），
    #:   按第一个冒号切会把 `C` 当成文件名（本仓台账用相对路径，但测试与将来
    #:   的手工台账可能给绝对路径）✓
    rel, _, func = impl.rpartition(":")
    impl_path = resolve_impl(rel)
    if not impl_path.is_file():
        out.append(("impl-missing", "实现文件不存在：%s" % rel))
        return out

    # ── claim 必须等于模型看得见的那一句 ─────────────────────────────
    claim = str(rec.get("claim") or "").strip()
    visible = first_sentence(spec_doc)
    if not claim:
        out.append(("claim-mismatch", "记录没有 claim（应逐字等于 doc 首句）"))
    elif normalize(claim) != normalize(visible):
        out.append(
            ("claim-mismatch", "claim ≠ doc 首句（台账 %r / 模型可见 %r）" % (claim[:60], visible[:60]))
        )

    # ── claim 的证据 ────────────────────────────────────────────────
    ev = rec.get("claim_evidence") or {}
    ev_path, ev_anchor = str(ev.get("path") or ""), str(ev.get("anchor") or "")
    if not ev_path or not ev_anchor:
        out.append(("claim-unanchored", "claim_evidence 缺 path/anchor"))
    elif known is not None:
        text = read_page((ROOT / ev_path).resolve()) if not Path(ev_path).is_absolute() else read_page(Path(ev_path))
        if text is None:
            out.append(("claim-unanchored", "claim_evidence 指向的文件不存在：%s" % ev_path))
        elif normalize(ev_anchor) not in normalize(text):
            out.append(("claim-unanchored", "claim_evidence 锚点在所指出处里找不到：%r" % ev_anchor[:60]))

    # ── 成员覆盖：实现里调用的必须都登记 ────────────────────────────
    known_or_empty = known or set()
    used = impl_members(impl_path, func, known_or_empty, index) if func else {"found": False, "members": {}, "error": "impl 缺函数名"}
    if not used["found"]:
        out.append(("impl-missing", str(used["error"])))
    cited = {str(m.get("member") or "") for m in (rec.get("members") or [])}
    allowed = {str(a.get("name") or ""): str(a.get("why") or "") for a in (rec.get("allowed_non_com") or [])}
    for name in sorted(used["members"]):
        if name not in cited and name not in allowed:
            out.append(("member-uncited", "实现调用了 %s，台账没登记（第 %s 行）" % (name, used["members"][name][0])))
    for name, why in allowed.items():
        if not why.strip():
            out.append(("member-uncited", "allowed_non_com 里的 %s 没写理由" % name))
    if advisories is not None:
        for name in sorted(cited - set(used["members"])):
            advisories.append({"tool": str(rec.get("tool") or ""), "code": "member-extra",
                               "why": "登记了 %s，本层提取没看到（可能是更深一层的帮手）" % name})

    # ── 每条成员登记：页对、页在、锚点真 ───────────────────────────
    if known is not None:
        for m in rec.get("members") or []:
            iface = str(m.get("interface") or "")
            member = str(m.get("member") or "")
            path = str(m.get("path") or "")
            anchor = str(m.get("anchor") or "")
            #: ★ 铁律 5 的合法出口：官方页**确实查不到**时，必须显式写
            #:   `documented: false` + `gap`（查过哪些源/为什么没有页），
            #:   **不许编一个页**。这种条目进报表，不进违规（否则人会被逼着编）。
            if m.get("documented") is False:
                if not str(m.get("gap") or "").strip():
                    out.append(("member-undocumented", "%s 标了 documented:false 却没写 gap" % (member or "?")))
                elif advisories is not None:
                    advisories.append(
                        {"tool": str(rec.get("tool") or ""), "code": "member-undocumented",
                         "why": "%s 官方页查不到（已记账）：%s" % (member, str(m.get("gap"))[:80])}
                    )
                continue
            if not iface or not member:
                out.append(("page-mismatch", "成员登记缺 interface/member"))
                continue
            page_path = Path(path) if path else SWAPI_TYPES / iface / (member + ".md")
            text = read_page(page_path)
            if text is None:
                out.append(("page-missing", "官方页不存在：%s" % page_path))
                continue
            fm = page_front_matter(text)
            if fm.get("type") and fm.get("type") != iface:
                out.append(("page-mismatch", "%s 的 type 是 %s，不是 %s" % (page_path.name, fm.get("type"), iface)))
            if fm.get("member") and fm.get("member") != member:
                out.append(("page-mismatch", "%s 的 member 是 %s，不是 %s" % (page_path.name, fm.get("member"), member)))
            if not anchor.strip():
                out.append(("anchor-not-found", "%s 没写锚点" % member))
            elif normalize(anchor) not in normalize(text):
                out.append(("anchor-not-found", "%s 的锚点在官方页里找不到：%r" % (member, anchor[:60])))

    # ── 核验人 ──────────────────────────────────────────────────────
    ver = rec.get("verified") or {}
    if not (str(ver.get("by") or "").strip() and str(ver.get("at") or "").strip()):
        out.append(("unverified", "没有 verified.by / verified.at"))
    return out


def scan(ledger_dir: Path = LEDGER_DIR) -> tuple[list[dict], dict]:
    """⇒ `(rows, stats)`：每个违规一行；stats 给分母。

    :param ledger_dir: 台账目录。
    """
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "tools"))
    sys.path.insert(0, str(ROOT))
    import register_capabilities as rc  # noqa: PLC0415

    specs = {s.name: s for s in rc.all_specs()}
    #: ★ 45 个手写工具没有 ToolSpec —— 用真握手那份清单补上名字**与描述**
    #:   （否则它们的 `doc` 取到空串 ⇒ 全部误判 claim-mismatch）✓
    try:
        from mcp_tools_list import tools_list  # noqa: PLC0415

        wire = {t["name"]: str(t.get("description") or "") for t in tools_list()}
        wire_names = set(wire)
    except Exception:  # noqa: BLE001 - 握手失败不该让静态门禁崩，但必须显式说明
        wire = {}
        wire_names = set(specs)

    records, broken = load_ledger(ledger_dir)
    idx = member_index()
    known = set(idx) if idx is not None else None
    #: ★ 一层委托索引：只扫 `scripts/` 与 `server.py`（与实现落点一致）
    func_index = FunctionIndex().build([ROOT / "scripts", ROOT / "mcp-server" / "server.py"])

    rows: list[dict] = []
    adv: list[dict] = []
    for path in broken:
        rows.append({"tool": path, "code": "ledger-unreadable", "why": path})
    for name, rec in records.items():
        if name not in wire_names:
            rows.append({"tool": name, "code": "unknown-tool", "why": "台账有、注册表没有"})
    checked = 0
    for name in sorted(wire_names):
        checked += 1
        rec = records.get(name)
        if rec is None:
            rows.append({"tool": name, "code": "no-record", "why": "没有官方依据台账"})
            continue
        spec = specs.get(name)
        doc = str(getattr(spec, "doc", "") or "") if spec is not None else wire.get(name, "")
        for code, why in judge_record(rec, doc, known, func_index, adv):
            rows.append({"tool": name, "code": code, "why": why})
    stats = {
        "checked": checked,
        "records": len(records),
        "official_tree": known is not None,
        "members_indexed": len(known or ()),
        #: ★ 自动档与人读档分开计数：`verified.level="auto"` 是**机器核的**（成员提取 +
        #:   官方页原文抄取 + 词干重叠门槛），不能与「人读了页」混成一个数 ✓
        "auto_records": sum(
            1 for r in records.values() if str((r.get("verified") or {}).get("level") or "") == "auto"
        ),
        "advisories": adv,
    }
    return rows, stats


# ══════════════════════════════════════════════════════════════════════
# 基线（棘轮：只许降）+ CLI
# ══════════════════════════════════════════════════════════════════════


def main(argv=None) -> int:
    """门禁入口：退出 0 = 过（相对基线无新增）；1 = 有新增违规；2 = 无法判定。

    :param argv: 命令行参数（None = `sys.argv[1:]`）。
    """
    ap = argparse.ArgumentParser(description="MCP 工具官方依据台账门禁（规格 353）")
    ap.add_argument("--report", action="store_true", help="报表模式：退出码仍按判据给")
    ap.add_argument("--only", default="", help="只查这些工具（逗号分隔）")
    ap.add_argument("--json", default="", help="逐条读数写到这里")
    ap.add_argument("--baseline", default=str(BASELINE))
    ap.add_argument("--write-baseline", action="store_true", help="把当前违规写进基线（只许降）")
    ap.add_argument(
        "--reason",
        default="",
        help="★ 判据**收紧**导致的待核数上涨，必须写理由（写进基线文件，供复核）；判据放宽一律拒绝",
    )
    ap.add_argument("--strict", action="store_true", help="忽略基线：所有违规都算（验收用）")
    ap.add_argument("--ledger", default=str(LEDGER_DIR), help="台账目录")
    args = ap.parse_args(argv)

    ledger_dir = Path(args.ledger)
    rows, stats = scan(ledger_dir)
    only = {x.strip() for x in args.only.split(",") if x.strip()}
    if only:
        rows = [r for r in rows if r["tool"] in only]
        stats["checked"] = len(only)

    #: ★ 防假绿：一条都没看 = 没判（与 `check_tool_contract` 同型）
    if stats["checked"] < (1 if only else 300):
        print("★ 只看到 %d 个工具 ⇒ 注册表/握手可能没加载全，**这个绿不可信**" % stats["checked"])
        return 2

    baseline: dict = {}
    bp = Path(args.baseline)
    if bp.exists():
        try:
            baseline = json.loads(bp.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print("★ 基线读不出来（%s: %s）⇒ 本门禁无法判定" % (type(exc).__name__, exc))
            return 2

    if args.write_baseline:
        pending = sorted({r["tool"] for r in rows if r["code"] == "no-record"})
        prev = int(baseline.get("count", len(baseline.get("pending", []))))
        if bp.exists() and len(pending) > prev and not args.reason.strip():
            print(
                "✗ 拒绝写基线：待核工具 %d 个 > 既有基线 %d 个 —— **棘轮只许降不许升**；"
                "判据收紧导致上涨的，必须用 `--reason <为什么收紧>` 说明" % (len(pending), prev)
            )
            return 1
        bp.write_text(
            json.dumps(
                {"count": len(pending), "pending": pending,
                 "reason": args.reason.strip(), "previous_count": prev},
                ensure_ascii=False, indent=1,
            )
            + "\n",
            encoding="utf-8",
        )
        print("★ 已写基线：%s（待核 %d 个，上一版 %d 个）" % (bp.name, len(pending), prev))
        return 0

    base_keys = {
        r.get("tool", "")
        for r in (baseline.get("rows") or [])
    } | set(baseline.get("pending") or [])
    if args.strict:
        base_keys = set()
    #: ★ 棘轮**只承载「还没核到的工具」**（`no-record`）——
    #:   已有台账的记录一律硬判：半成品记录不许借基线蒙混 ✓
    new_rows = [r for r in rows if not (r["code"] == "no-record" and r["tool"] in base_keys)]

    if args.json:
        Path(args.json).write_text(
            json.dumps({"stats": stats, "counts": counts_by_code(rows), "rows": rows},
                       ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )

    done = stats["checked"] - sum(1 for r in rows if r["code"] == "no-record")
    if args.report:
        print(
            "★ 看了 %d 个工具 · 有台账 %d · **已核 %d/%d**（%.1f%%；其中人工 %d · 自动 %d）· "
            "违规合计 %d（基线 %d；本次新增 %d）"
            % (
                stats["checked"], stats["records"], done, stats["checked"],
                100.0 * done / max(1, stats["checked"]),
                stats["records"] - int(stats.get("auto_records", 0)), int(stats.get("auto_records", 0)),
                len(rows), int(baseline.get("count", 0)), len(new_rows),
            )
        )
        if not stats["official_tree"]:
            print("   ⚠ 官方文档树读不到（%s）⇒ 页/锚点判据本次**跳过**，这个绿只证明覆盖" % SWAPI_TYPES)
        for code, n in sorted(counts_by_code(rows).items(), key=lambda kv: -kv[1]):
            print("   %-22s %d" % (code, n))
        adv = stats.get("advisories") or []
        if adv:
            by_code: dict = {}
            for a in adv:
                by_code[a.get("code", "?")] = by_code.get(a.get("code", "?"), 0) + 1
            for code, n in sorted(by_code.items(), key=lambda kv: -kv[1]):
                print("   （建议，不进判据）%-20s %d 条" % (code, n))
        for r in new_rows[:40]:
            print("   [%s] %s —— %s" % (r["code"], r["tool"], r["why"][:110]))
        return 1 if new_rows else 0

    if new_rows:
        print("★ 官方依据台账门禁未通过（%d 条新违规）：" % len(new_rows))
        for r in new_rows:
            print("   [%s] %s —— %s" % (r["code"], r["tool"], r["why"][:110]))
        print("\n★ 修法：`python -B tools/gen_tool_official_claims.py --tools <名字>` 生成草稿，")
        print("   然后**真去读**官方页（C:\\swapi\\types\\<接口>\\<成员>.md），填 claim 与锚点。")
        print("   ★ 判据见 specs/353-mcp-tool-official-audit/spec.md §二")
        return 1

    print(
        "★ 官方依据台账门禁通过：%d 个工具 · 已核 %d · **相对基线没有新增违规**（基线 %d 条待收敛）"
        % (stats["checked"], done, int(baseline.get("count", 0)))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
