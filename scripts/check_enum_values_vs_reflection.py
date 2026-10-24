r"""@brief 门禁：代码里写的**官方枚举值**，必须与**出厂反射**对得上。

## 为什么（2026-10-01 轮 106，Spec Kit `025`）
连着两轮的错**都在「值」上，不在「名字」上**：
```
023：螺旋线枚举凭记忆写反  (height_and_pitch 1↔2)
024：swSketchChamfer_DistanceDistance 两源冲突 (-1 vs 1)
```
⚠ 而**当时所有的门禁都查不到** —— 它们查的是「名字在不在官方清单里」
（`check_member_names` / `interface_member_ownership` / `audit_call_arity`），
**没有一个查「值对不对」**。

⇒ 本门禁补这个缺口：**把「值」也变成机器判据**。

## 判据
1. 在 `scripts/**/*.py` 里找形如 `"<key>": <整数>,   # <swMember>` 的行
   （这是本仓库广泛使用的写法：**值 + 官方成员名**；★ 键**大小写不限**）；
   ★★ 2026-10-08（spec 223 / FR-012）：扫描面从 `scripts/sw_*.py` **扩到全部** `scripts/**/*.py`
     —— 原先 `scripts/sketch_relations.py` 的 **38 条**合格行**一条都没被检查过**（文件名不以 `sw_` 开头）✗
     且键的字符集从 `[a-z0-9_]+` 放宽到 `[A-Za-z0-9_]+` —— 原先**驼峰键**一律匹配不到 ✗
2. 从**出厂反射转储** `enum_values_sldworks.txt` 解析出 `{成员名: 值}`；
3. 逐条比对：
   * **对不上** ⇒ `[FAIL]`（这就是 023 那类错）；
   * **转储里查不到该成员** ⇒ 单独列「查不到」（铁律 5：不猜），**不算失败**
     （可能来自别的枚举源，由人核）；
4. 若 `C:\swapi\enums\<枚举>.md` 也在、且值与反射**不同** ⇒ 报 **CONFLICT**
   （这就是 024 那类；⚠ **冲突本身不判失败**，因为铁律 4 已规定取反射 ——
   但要**显式列出来**，让人知道"这里两源不一致、我们取了反射的"）。
5. ★★ 2026-10-08（spec 223 / FR-011）**覆盖清单**：打印「扫描文件数 · 模块级整数表数 ·
   已覆盖 · 未覆盖」，并把**自称官方却无 `# swXxx` 标注**（⇒ 门禁看不见）的表**逐个列出**
   （上限 `INVENTORY_LIMIT`，超出给「另有 N 张未列出」）。
   ★ **退出码不变** —— 未覆盖的表未必是枚举，把它判红是**噪音**；要的是**可见**。
   ★★ 2026-10-09（spec 225）**修探测器自己**：`CLAIM` 从 `官方|swapi|sw[A-Z]\w+` 放宽到
     `官方|swapi|sws?[A-Z]\w+|反射|转储|CHM|_raw` —— 原先**`sws*` 全族**（`sw[A-Z]` 要求
     `sw` 后紧跟大写）与**「反射/转储/CHM」三种出处自称**一律不命中 ⇒ 10 张表**从没进过盲区**
     ⇒ 224 的「未表态即红」对它们失效 ✗ ★ 放宽后盲区 44 → 54，逐张补声明后未表态仍为 0。

⚠ **便携性**：反射转储在**工作区**（不在本仓库）⇒ 拿不到就 **SKIP 并 exit 0**。
可用 `DSH_ENUM_DUMP` / `DSH_SWAPI_ENUMS` 覆盖路径。

# ── 来源 ──
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_enum_values_vs_reflection.py
# 定位:   补「值级」覆盖缺口 —— 名字有人查，**值此前没人查**。
# 官方依据: `D:\AI\SW\_raw\enum_values_sldworks.txt`（由 `SolidWorks.Interop.swconst.dll
#           ` 的**纯元数据读取**生成，非实测）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(os.environ.get("DSH_ENUM_GATE_ROOT") or Path(__file__).resolve().parents[1])
#: ★★ 2026-10-09（spec 224）：`DSH_ENUM_GATE_ROOT` 可把**扫描根**指向别处。
#: 目的是让 FR-003 的**负例**能在一棵**合成树**上端到端跑（「自称官方却没表态」⇒ 必须 ex
#: it 1），
#:   而不是只在单元层断言 —— ★ 与既有的 `DSH_ENUM_DUMP` / `DSH_SWAPI_ENUMS` 同一风格。
#:   ★ 默认仍是本仓库根 ⇒ 日常行为**不变**。

#: ⚠ **转储不止一个**（轮 107 补）：`sldworks` 与 `cosworks` 是两个程序集，
#:   各自一份枚举清单，格式相同。
#: ★ 第一版只读 `enum_values_sldworks.txt` ⇒ **75 条 `sws*`（Simulation）全归"查不到"**
#: 。
#:     实测那些成员在 **`SolidWorks.Interop.cosworks.dll`** 里，
#:     而 `_raw\reflect\enum_cosworks.txt` 已有对应转储（363 个枚举节）。
DEFAULT_DUMPS = (
    Path(__file__).resolve().parents[1] / "_raw" / "enum_values_sldworks.txt",
    Path(__file__).resolve().parents[1] / "_raw" / "reflect" / "enum_cosworks.txt",
)
#: 可用 `DSH_ENUM_DUMP` 覆盖（多个用 `;` 分隔）。
DUMP_SPEC = os.environ.get("DSH_ENUM_DUMP", "")
DUMPS = tuple(p for p in DUMP_SPEC.split(";") if p.strip()) or DEFAULT_DUMPS
#: 兼容旧名（单个转储）。
DUMP = Path(DUMPS[0])
SWAPI_ENUMS = Path(os.environ.get("DSH_SWAPI_ENUMS", r"C:\swapi\enums"))

#: `"<key>": <int>,   # <swMember>[后面可有注释文字]`
#: ⚠ **第一版要求成员名后即行尾** ⇒ 漏掉了 `sw_sketch_edit.py` 那行
#:   （它写成 `# swSketchChamfer_DistanceDistance（⚠ md 写 -1…）`）
#:   ⇒ **门禁会漏掉 024 那个冲突本身**（轮 106 当场抓到并修）。
#: ★★ 2026-10-08（spec 223 / FR-012）：键的字符集从 `[a-z0-9_]+` **放宽到 `[A-Za-z0-9_]+
#: `**
#:   —— ★ 原先**驼峰键**（如 `sw_ref_geometry.py` 的 `"Parallel": 1, # swRefPlane…`）
#: **一律匹配不到** ⇒ 那又是一处**静默边界**（★ 实测：放宽后正好多出 `REF_PLANE_CONSTRAI
#: NTS`
#:   的 **10 行**，而**新值全部与反射一致、0 处新冲突**）✓
CODE_ROW = re.compile(
    r'^\s*"(?P<key>[A-Za-z0-9_]+)"\s*:\s*(?P<value>-?\d+)\s*,\s*#\s*'
    r"(?P<enum>[A-Za-z_]\w*)?\.?(?P<member>sw\w+)\b.*$"
)
#: 转储里的一行：`    swFmChamfer = 0`（缩进 4 空格，在 `## <Enum>` 之下）
#: ★★ 2026-10-09（spec 224 / FR-001）：成员名的字符集从 `sw\w+` **放宽到** `[A-Za-z_]\w*
#: `。
#: ★ 为什么：`## <Enum>` 节里的 `名字 = 整数` **就是**成员定义，`sw` 前缀是**命名习惯、
#: 不是语法**。
#:   实测反例（`_raw/reflect/enum_cosworks.txt` 第 2707–2721 行）：
#:   ```
#:   ## swsTopologyIterationOption_e
#:     IterationOption_Auto = 0        ← 不带 `sw` 前缀
#:   ## swsTopologyPreservedRegionOption_e
#:     PreservedRegion_LoadsOnly = 0   ← 同上
#:   ```
#:   ⇒ 旧正则把**整节读成空** ⇒ 门禁对这两条枚举一律回「查不到」✗
#:   ★（与 223 的「边界外的表静默不报」同族：这次漏在**转储解析**侧。）
#:   ★★ 实测影响（已先量后改）：成员 **10588 → 10664（+76）**，而
#: `ok` 175 不变 · 值不符 0 不变 · 查不到 2 不变 · 两源冲突 3 不变 ⇒ **不制造任何新红**
#: ✓
DUMP_ROW = re.compile(r"^\s{2,}(?P<member>[A-Za-z_]\w*)\s*=\s*(?P<value>-?\d+)\s*$")
DUMP_HEAD = re.compile(r"^##\s+(?P<enum>\w+)\s*$")


def parse_dumps(paths) -> tuple:
    """把**多个**转储合并 ⇒ `({成员名: 值}, {成员名: 枚举名}, {成员名: 来源转储名})`。

    ⚠ 合并顺序即优先级：先来的 `setdefault` 生效（`sw*` 与 `sws*` 前缀不重叠，
    实测无冲突；真有冲突时**先出现的那个转储**赢，且下面会把它打出来）。
    """
    values: dict = {}
    owner: dict = {}
    origin: dict = {}
    for p in paths:
        p = Path(p)
        if not p.is_file():
            continue
        v, o = parse_dump(p)
        for k, val in v.items():
            if k not in values:
                values[k] = val
                owner[k] = o.get(k, "")
                origin[k] = p.name
    return values, owner, origin


def parse_dump(path: Path) -> tuple:
    """⇒ `({成员名: 值}, {成员名: 枚举名})`。"""
    values: dict = {}
    owner: dict = {}
    cur = ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        h = DUMP_HEAD.match(line)
        if h:
            cur = h.group("enum")
            continue
        m = DUMP_ROW.match(line)
        if m:
            values.setdefault(m.group("member"), int(m.group("value")))
            owner.setdefault(m.group("member"), cur)
    return values, owner


def parse_code() -> list:
    """⇒ `[(文件, 行号, key, 值, 成员名, 枚举名或None)]`。

    ★★ 2026-10-08（spec 223 / FR-012）：扫描面从 `scripts/sw_*.py` **扩到 `scripts/**/*.py`**
      —— 原先是 `glob("sw_*.py")`，而 `scripts/sketch_relations.py` 有 **38 条**完全符合
      `CODE_ROW` 的行**一条都没被检查过**（文件名不以 `sw_` 开头 ⇒ 静默落在边界外）✗
    ★ 覆盖判据**不变**（仍是「值 + `# swXxx`」）—— ★ 扩的是**可见性**，不是放宽判定 ✓
    """
    out: list = []
    for p in sorted((ROOT / "scripts").rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        for i, line in enumerate(
            p.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            m = CODE_ROW.match(line)
            if m:
                out.append(
                    (
                        #: ★ 用**相对 `scripts/` 的路径**，不是 basename ——
                        #:   子目录（`engineering/acceptance/` 等）里的同名文件
                        #:   会互相覆盖 `covered` 字典，且下游 `ROOT/"scripts"/fname`
                        #:   读不到。
                        str(p.relative_to(ROOT / "scripts")).replace("\\", "/"),
                        i,
                        m.group("key"),
                        int(m.group("value")),
                        m.group("member"),
                        m.group("enum"),
                    )
                )
    return out


#: ★★ spec 223 / FR-011：**覆盖清单** —— 整数枚举表的「已覆盖 / 未覆盖」清点。
#:   为什么要有它：FR-012 之前只知道「122 行被覆盖」，**不知道谁没被覆盖** ✗
#: ⇒ ★ 判据是「**静默漏过 = 看不见的豁免**」（与 `check_undefined_names.py` 的跳过同族）
#: 。
#:
#: ★★ 2026-10-09（spec 225 / FR-001）：**`sw[A-Z]` 要求 `sw` 后紧跟大写 ⇒ `sws*` 全族不
#: 命中**。
#: 实测：`CLAIM.search("swsSolverType_e")` → `False`，而 `CLAIM.search("swSolverType_e")
#: ` → `True`。
#:   `sws*` 是 **Simulation/Cosworks 程序集的整族枚举名**（转储里 **300+ 个**）⇒
#: 那些表「自称官方/反射」却**从没进过盲区清单** ⇒ 224 的「未表态即红」对它们**完全失效*
#: * ✗
#:   ★ 同族反例（本轮当场量到）：`sw_topology.py` 里 `SWS_TOPOLOGY_DEMOLD_DIRECTIONS`
#:     注释写着「反射：swsTopologyDemoldDirectionOption_e」却没表态，而**紧邻**的
#:     `SWS_TOPOLOGY_ITERATION_OPTIONS` 有 `#: enum-gate:` —— 差别只在**探测器看不看得见**。
#:
#: ★★ 2026-10-09（spec 225 / FR-002）：**出处自称不止「官方」一种写法**。
#: 本仓同一件事还会写成「反射」「转储」「CHM」「`_raw`」（★ 见 `AGENTS.md` §十四 的三源
#: ）。
#:   只认「官方/swapi」⇒ 那几种写法下的表同样**静默落在盲区外** ✗
#:
#: ⚠ **诚实边界**：`CLAIM` 是**启发式**，不是证明 —— 窗口里出现这些词**不等于**该表真有
#: 出处，
#:   只等于「旁边的人**声称**有」⇒ 于是要求**表态**（把声称变成一句可核的话）。
#: ★ 用**散文**（不含上述词）声称出处的表**仍看不见** ⇒ 登记为未过门（spec 225 §二 FR-00
#: 2）。
#:   ★★ 实测影响（已先量后改）：盲区 **44 → 54**，新暴露 10 张**全部未表态**
#:     （3 张 `sws*` 枚举 + 6 张 `*_ARITY` + 1 张 `_REFGEOM_POSITIONS`）
#:     ⇒ 本轮逐张补声明后 `未表态 = 0`，**不制造任何新红** ✓
#:
#: ★★ 2026-10-09（spec 226 / FR-001）：**收口 225 登记的那条未过门 —— 散文式出处自称**。
#:   ★ 先量后改：一次性探针（`output/_probe_prose_claim.py`，不进仓库代码）量到
#:     非盲区 14 张里**只有 1 张**是真散文自称 ——
#:     `sw_import_mesh_reference.py:69 SW_LENGTH_UNITS`，注释写着
#: `# 本机 SolidWorks 2024 swconst.dll 验证值`；而 `本机`/`swconst`/`.dll` **一个都不在*
#: * 旧 `CLAIM` 里
#:     （★ `swconst.dll` 也**不**命中 `sws?[A-Z]\w+`：那条要求 `sw` 后是 `s` 或**大写**）
#: ⇒ 它「自称有出处」却**从没进过盲区清单** ⇒ 224 的判红对它**完全无效**（与 225 修掉的
#: 那族同型）。
#:   ★★ 加词前**先量爆炸半径**（225 的教训：放宽后新暴露 10 张要逐张表态）：
#:     定稿词集实测**只新增 1 张**（就是上面那张）⇒ 安全，不制造未预期的新红。
#:   ★ 按**语义**分四类（每类都是本仓**真实存在**的出处来源，不是凑词）：
#:     ① 真机/运行观测 `本机|本地|实测|真机|观测`（对应 `not-enum observed` 子类）
#:     ② 程序集/反射 `\.dll|swconst`（本仓 `_raw` 反射转储的机制）
#:     ③ 离线文档 `手册|帮助|文档`（与 `CHM` 同族）
#:     ④ 摘录动词 `摘自|取自`（显式声明从别处摘录）
#: ★★ **有意排除**（歧义太大，加进去只制造噪声，判据 `test_claim_does_not_match_ambiguou
#: s_prose` 冻结此边界）：
#:     `参考`（「仅供参考」**不是**出处自称）· `据`/`按`（单字过宽：「按需」「按名」）。
#:   ★ 实测影响：盲区 **54 → 55**，新暴露 1 张 ⇒ 补 1 行声明后 `未表态 = 0`；
#:     `ok 175` · 查不到 2 · 两源冲突 3 · 覆盖清单 189/101/33/68 **四读数全不变** ✓
CLAIM = re.compile(
    r"官方|swapi|sws?[A-Z]\w+|反射|转储|CHM|_raw"
    r"|本机|本地|实测|真机|观测|\.dll|swconst|手册|帮助|文档|摘自|取自"
)
#: 未覆盖明细的**打印上限**（超出给「另有 N 张未列出」，免得刷屏）。
INVENTORY_LIMIT = 20


def _int_dict_len(node) -> int | None:
    """★ 节点是「全 `str` 键 + 全 `int` 值」的字典 ⇒ 返回条目数；否则 `None`。"""
    if not isinstance(node, ast.Dict):
        return None
    n = 0
    for k, v in zip(node.keys, node.values):
        if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
            return None
        if not (isinstance(v, ast.Constant) and isinstance(v.value, int)):
            return None
        n += 1
    return n


def find_int_tables() -> list:
    """扫 `scripts/**/*.py` 的**模块级**整数表 ⇒ `[(文件, 起始行, 结束行, 表名, 条目数), …]`。

    ★ 只认 `tree.body` 顶层（缩进 0）的 `Assign` / `AnnAssign` ⇒ 函数内的局部表不算。
    ★ 空表（0 项）不算 —— 它不是枚举表。
    """
    out: list = []
    for p in sorted((ROOT / "scripts").rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in tree.body:
            names: list = []
            if isinstance(node, ast.Assign):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names = [node.target.id]
            if not names:
                continue
            n = _int_dict_len(node.value)
            if n:
                lo = node.lineno
                hi = max(getattr(node, "end_lineno", lo) or lo, lo)
                #: ★ 同 `parse_code`：相对路径，子目录文件才读得到
                out.append(
                    (
                        str(p.relative_to(ROOT / "scripts")).replace("\\", "/"),
                        lo,
                        hi,
                        names[0],
                        n,
                    )
                )
    return out


def find_uncovered_claimed_tables() -> list:
    """⇒ **未覆盖**且**紧邻注释自称官方**的整数表 ⇒ `[(文件, 行, 表名, 条目数), …]`。

    ★ 这是 F1（spec 223）那一类表的**探测器**：来源块写着「照录官方页」，
      而表里一行 `# swXxx` 都没有 ⇒ 门禁**看不见**它。
      （真例：`sw_pattern.py` 的两张伪造表在订正前正落在这里。）
    """
    covered: dict = {}
    for fname, lineno, *_rest in parse_code():
        covered.setdefault(fname, []).append(lineno)
    out: list = []
    for fname, lo, hi, name, n in find_int_tables():
        if any(lo <= x <= hi for x in covered.get(fname, [])):
            continue
        src = (ROOT / "scripts" / fname).read_text(encoding="utf-8", errors="replace")
        lines = src.splitlines()
        window = "\n".join(lines[max(0, lo - 15) : hi])
        if CLAIM.search(window):
            out.append((fname, lo, name, n))
    return out


#: ★★ 2026-10-09（spec 224 / FR-002）：**表级出处声明**。
#:
#: 为什么需要它（本轮实测，这是设计的**事实依据**）：44 张「自称官方却无 `# swXxx` 标注
#: 」的
#: 模块级整数表共 **409 条**，其中**键就是官方成员名**的只有 **27 条**
#: （26 条在 `ANNOTATION_TYPE_BITS` + 1 条在 `DIALOG_SUPPRESSORS`）⇒
#: ★ **「逐行补 `# swXxx`」对 42 张表是错的解法** —— 它们的键是**本地语义键**（`"edge":
#: 1`），
#: 官方成员名**不在键里**；硬补只能靠人把「本地键 ↔ 官方成员」一一对上，
#: 成本极高且极易写错（★ 223 抓的「冒官方名」正是这类）。
#: ⇒ 它们真正的出处是**表级**的：表上方那行注释写着 `#: ★ 官方 swViewEntityType_e`。
#: ★ 本声明形态就是**把那行注释形式化**，不是发明新概念。
DISPOSITION = re.compile(
    r"#:\s*enum-gate:\s*(?P<code>[a-z][a-z-]*)(?:\s+(?P<arg>\S.*?))?\s*$"
)
#: 封闭词表。**认不出的 code 一律判红** —— 否则声明就是装饰品（223 判过的「空判据」同族
#: ）。
DISPOSITION_CODES = ("enum", "member", "not-enum")
#: `not-enum` 的封闭子类。
NOT_ENUM_SUBS = ("arity", "index", "mark", "derived", "observed")
#: `member` 声明的官方页根（可用 `DSH_SWAPI_TYPES` 覆盖）。
SWAPI_TYPES = Path(os.environ.get("DSH_SWAPI_TYPES", r"C:\swapi\types"))


def table_values(fname: str, lineno: int) -> list:
    """⇒ 该文件里**起始行 == `lineno`** 的模块级整数表的**值列表**（取不到 ⇒ `[]`）。"""
    p = ROOT / "scripts" / fname
    if not p.is_file():
        return []
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.lineno != lineno:
            continue
        if _int_dict_len(node.value) is None:
            continue
        return [v.value for v in node.value.values]
    return []


def enum_value_sets(paths=None) -> dict:
    """⇒ `{枚举名: {取值集}}`（来自出厂反射转储）。★ `enum` 声明的**值集来源**。"""
    ref, owner, _origin = parse_dumps(paths or DUMPS)
    out: dict = {}
    for member, enum_name in owner.items():
        if enum_name:
            out.setdefault(enum_name, set()).add(ref[member])
    return out


def member_page_exists(name: str):
    """⇒ `True/False`；★ **拿不到 `C:\\swapi\\types` 时回 `None`（= SKIP，不判罪）**。"""
    if not SWAPI_TYPES.is_dir():
        return None
    return bool(list(SWAPI_TYPES.glob("*/%s.md" % name)))


def _find_declaration(lines: list, lo: int, hi: int):
    """⇒ `(code, arg, 声明行号)` 或 `None`。归属规则见 docstring 下方。

    ★ 归属规则（**必须无歧义**）：声明只属于**紧邻其下**的那张表 ——
      从表起始行的**上一行**向上扫**连续的注释/空行块**，取该块里**最后一条**
      （= 最靠近表的那条）`#: enum-gate:`；块里没有再看**表体行内**（`[lo, hi]`）的第一条。
    ★ 为什么取「最后一条」而不是「第一条」：`scripts/sw_ref_geometry.py` 里相邻表的注释块
      **会连成一片**（`REF_POINT_ALONG_CURVE_TYPES` 的注释块与 `GLOBAL_BBOX_FIT_OPTIONS` 的相邻）
      ⇒ 取「块里第一条」会把声明**错配给上一张表**。
    """
    i = lo - 2
    while i >= 0:
        stripped = lines[i].strip()
        if stripped and not stripped.startswith("#"):
            break
        m = DISPOSITION.search(lines[i])
        if m:
            return (m.group("code"), (m.group("arg") or "").strip(), i + 1)
        i -= 1
    for j in range(lo - 1, min(hi, len(lines))):
        m = DISPOSITION.search(lines[j])
        if m:
            return (m.group("code"), (m.group("arg") or "").strip(), j + 1)
    return None


def parse_dispositions() -> dict:
    """⇒ `{(文件名, 表起始行): (code, arg, 声明行号)}`（只含**已表态**的表）。"""
    out: dict = {}
    for fname, lo, hi, _name, _n in find_int_tables():
        p = ROOT / "scripts" / fname
        if not p.is_file():
            continue
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        decl = _find_declaration(lines, lo, hi)
        if decl:
            out[(fname, lo)] = decl
    return out


def check_dispositions(dispositions: dict, sets=None) -> list:
    """校验每条表态**能不能被核**。⇒ `[(文件, 行, 表名/空, 原因), …]`（空 = 全过）。

    ★ 判据是「**表态必须可核**」：`enum` 要能解析 + 值集包含；`member` 要有官方页；
      `not-enum` 的子类要在封闭词表内；code 本身要在词表内。
      **认不出/核不了 ⇒ 报问题**（否则表态退化成装饰品）。
    """
    problems: list = []
    table_names = {(f, lo): n for f, lo, _hi, n, _c in find_int_tables()}
    for (fname, lo), (code, arg, line) in sorted(dispositions.items()):
        name = table_names.get((fname, lo), "?")
        if code not in DISPOSITION_CODES:
            problems.append(
                (
                    fname,
                    line,
                    name,
                    "认不出的 code %r（词表 %s）" % (code, list(DISPOSITION_CODES)),
                )
            )
            continue
        if not arg:
            problems.append((fname, line, name, "`%s` 缺参数" % code))
            continue
        if code == "not-enum":
            if arg not in NOT_ENUM_SUBS:
                problems.append(
                    (
                        fname,
                        line,
                        name,
                        "`not-enum %s` 的子类不在封闭词表 %s 里"
                        % (arg, list(NOT_ENUM_SUBS)),
                    )
                )
            continue
        if code == "member":
            ok = member_page_exists(arg)
            if ok is False:
                problems.append(
                    (
                        fname,
                        line,
                        name,
                        "`member %s` 在 %s\\*\\ 下**没有官方页**" % (arg, SWAPI_TYPES),
                    )
                )
            continue
        #: code == "enum"
        table_sets = sets if sets is not None else enum_value_sets()
        if arg not in table_sets:
            problems.append(
                (
                    fname,
                    line,
                    name,
                    "`enum %s` 在出厂反射转储里**解析不到**（枚举名错，或转储解析漏了）"
                    % arg,
                )
            )
            continue
        bad = sorted({v for v in table_values(fname, lo) if v not in table_sets[arg]})
        if bad:
            problems.append(
                (
                    fname,
                    line,
                    name,
                    "`enum %s` 但值 %s 不在该枚举取值集 %s 里"
                    % (arg, bad, sorted(table_sets[arg])),
                )
            )
    return problems


def parse_swapi(enum_name: str) -> dict:
    """从 `C:\\swapi\\enums\\<enum>.md` 的表格里取值（拿不到就回空）。"""
    p = SWAPI_ENUMS / ("%s.md" % enum_name)
    if not p.is_file():
        return {}
    out: dict = {}
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\|\s*(sw\w+)\s*\|\s*(-?\d+)\s*\|", line)
        if m:
            out[m.group(1)] = int(m.group(2))
    return out


def compare(rows, ref, owner, swapi_loader=None):
    """把 `parse_code()` 的行与反射值比对。

    ⇒ `(ok 数, 值不符列表, 查不到列表, 两源冲突列表)`

    ⚠ **抽出来是为了可测**：`main()` 只做 IO 与打印，判定逻辑在这里
    （**负例测试需要能直接喂一批行进去看它报不报**）。
    """
    load = swapi_loader or parse_swapi
    mismatched, unknown, conflicts = [], [], []
    ok = 0
    for fname, lineno, key, value, member, enum_name in rows:
        if member not in ref:
            unknown.append((fname, lineno, key, value, member))
            continue
        if ref[member] != value:
            mismatched.append((fname, lineno, key, value, member, ref[member]))
            continue
        ok += 1
        en = enum_name or owner.get(member, "")
        if en:
            sw = load(en)
            if member in sw and sw[member] != ref[member]:
                conflicts.append((fname, lineno, member, ref[member], sw[member], en))
    return ok, mismatched, unknown, conflicts


def main() -> int:
    present = [p for p in DUMPS if Path(p).is_file()]
    if not present:
        print("枚举值门禁 · **SKIP** —— 拿不到任何出厂反射转储（%s）" % (DUMPS,))
        print("  （**便携性守卫**：转储在工作区，别的机器上不应无条件红）")
        return 0

    ref, owner, origin = parse_dumps(DUMPS)
    rows = parse_code()
    print(
        "枚举值门禁 · 出厂反射转储 **%d** 份：%s"
        % (len(present), ", ".join(Path(p).name for p in present))
    )
    print("  合并后共 **%d** 个成员" % len(ref))
    print("  代码里「值 + 官方成员名」的行：**%d** 条" % len(rows))

    #: ★★ spec 223 / FR-011：**覆盖清单** —— 让「没被覆盖的表」**看得见**。
    #:   原先只知道「多少行被覆盖」，**不知道谁没被覆盖** ⇒ 边界外的表静默漏过 ✗
    tables = find_int_tables()
    covered_by_file: dict = {}
    for fname, lineno, *_rest in rows:
        covered_by_file.setdefault(fname, []).append(lineno)
    covered_n = sum(
        1
        for fname, lo, hi, _n, _c in tables
        if any(lo <= x <= hi for x in covered_by_file.get(fname, []))
    )
    blind = find_uncovered_claimed_tables()
    scanned_files = len(
        [p for p in (ROOT / "scripts").rglob("*.py") if "__pycache__" not in p.parts]
    )
    print(
        "  覆盖清单 · 扫描 **%d** 个文件 · 模块级整数表 **%d** 张 · 已覆盖 **%d** · 未覆盖 **%d**"
        % (scanned_files, len(tables), covered_n, len(tables) - covered_n)
    )

    #: ★★ spec 224 / FR-003：把「盲区」拆成**已表态 / 未表态**，并让**未表态判红**。
    #:   ★ 223 的定位是「要的是可见，不是判罪」—— 那个定位在 223 已经**消费完**：
    #:     44 张全部表态后，剩下的「未表态」只可能是**新写的表**，而新表自称官方却不表态
    #:     正是 223 那张伪造表的**复发形态** ⇒ 这时**静默通过才是错的**。
    #:   ★ 兼容性：`门禁盲区）：**N** 张` 这一行**保留**（223 的判据按它做正则），
    #:     但 **N 的语义改为「未表态」** ⇒ 44 张表态后 N=0，223 的
    #:     `len(details) == min(blind, 20)` 仍自洽 ✓
    dispositions = parse_dispositions()
    declared = [t for t in blind if (t[0], t[1]) in dispositions]
    undeclared = [t for t in blind if (t[0], t[1]) not in dispositions]
    print(
        "  其中**自称官方却无 `# swXxx` 标注**（★ 门禁盲区）：**%d** 张"
        % len(undeclared)
    )
    for fname, lo, name, n in undeclared[:INVENTORY_LIMIT]:
        print("     未覆盖：%s:%d %s（%d 项）" % (fname, lo, name, n))
    if len(undeclared) > INVENTORY_LIMIT:
        print("     …（另有 %d 张未列出）" % (len(undeclared) - INVENTORY_LIMIT))
    print("  表级出处声明（`#: enum-gate: …`）· 已表态 **%d** 张" % len(declared))
    for fname, lo, name, _n in declared[:INVENTORY_LIMIT]:
        code, arg, line = dispositions[(fname, lo)]
        print(
            "     已表态：%s:%d %s → %s %s（声明在第 %d 行）"
            % (fname, lo, name, code, arg, line)
        )
    if len(declared) > INVENTORY_LIMIT:
        print("     …（另有 %d 张未列出）" % (len(declared) - INVENTORY_LIMIT))
    print()

    mismatched, unknown, ok = [], [], 0
    conflicts: list = []
    ok, mismatched, unknown, conflicts = compare(rows, ref, owner)

    bad = 0
    if mismatched:
        bad += 1
        print("[FAIL] **%d 条的值与出厂反射对不上**：" % len(mismatched))
        for fname, lineno, key, value, member, want in mismatched:
            print(
                "         %s:%d  %r = %d  ✗  反射里 %s = %d"
                % (fname, lineno, key, value, member, want)
            )
        print()
        print("  修法：**按反射改值**（铁律 4：冲突/不一致以出厂类型库为准）。")
        print("        ★ 这类错**所有旧门禁都抓不到**（它们只查名字，不查值）——")
        print("          这正是 023 / 024 连着踩的那个缺口。")
    if unknown:
        print(
            "[INFO] **%d 条在转储里查不到**（铁律 5：不猜，列出待人工核）："
            % len(unknown)
        )
        for fname, lineno, key, value, member in unknown[:12]:
            print(
                "         %s:%d  %r = %d  → %s（转储里没有）"
                % (fname, lineno, key, value, member)
            )
        if len(unknown) > 12:
            print("         …（还有 %d 条）" % (len(unknown) - 12))
        print()
    if conflicts:
        print(
            "[INFO] **%d 处两源冲突**（我们按铁律 4 取了反射的值）：" % len(conflicts)
        )
        for fname, lineno, member, rv, sv, en in conflicts:
            print(
                "         %s:%d  %s —— 反射 %d · swapi 的 md %d（枚举 %s）"
                % (fname, lineno, member, rv, sv, en)
            )
        print("         ⚠ 冲突**不判失败**（铁律 4 已定：取反射），但要让人看得见。")
        print()

    #: ★★ spec 224 / FR-002：**表态必须可核**（核不过 ⇒ 声明是装饰品，等于 223 判过的「
    #: 空判据」）。
    problems = check_dispositions(dispositions)
    if problems:
        bad += 1
        print("[FAIL] **%d 条表级出处声明核不过**：" % len(problems))
        for fname, line, name, why in problems:
            print("         %s:%d  %s —— %s" % (fname, line, name, why))
        print()

    #: ★★ spec 224 / FR-003：**未表态即红**（本轮新增的判罪 —— 见 main() 上方的理由）。
    if undeclared:
        bad += 1
        print(
            "[FAIL] **%d 张未表态**（自称官方却无 `# swXxx` 覆盖、也无表级出处声明）："
            % len(undeclared)
        )
        for fname, lo, name, n in undeclared[:INVENTORY_LIMIT]:
            print("         %s:%d %s（%d 项）" % (fname, lo, name, n))
        if len(undeclared) > INVENTORY_LIMIT:
            print(
                "         …（另有 %d 张未列出）" % (len(undeclared) - INVENTORY_LIMIT)
            )
        print(
            "  修法：在该表**起始行正上方**补一行 `#: enum-gate: <code> <arg>`（spec 224 FR-002）："
        )
        print(
            "        · `enum <swXxx_e>`      —— 值是命名官方枚举的取值（门禁校验值集 ⊆ 该枚举）"
        )
        print(
            "        · `member <MemberName>` —— 值来自该官方成员的页内文档（门禁校验该成员有官方页）"
        )
        print("        · `not-enum <%s>` —— 不是官方枚举值" % "|".join(NOT_ENUM_SUBS))
        print()

    if bad:
        return 1
    print(
        "[PASS] **%d** 条有据可查的值**全部与出厂反射一致**"
        "（另有 %d 条查不到、%d 处两源冲突，均已列出）"
        % (ok, len(unknown), len(conflicts))
    )
    print(
        "[PASS] 表级出处声明 **%d** 张**全部可核**，盲区**未表态 = 0**"
        % len(dispositions)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
