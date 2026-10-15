r"""并入规范门禁 —— 校验 docs/union-conventions.md 定义的五条硬规则。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本工具为原创
# 文件:   scripts/check_union_conventions.py —— 本文件自身
# 定位:   docs/union-conventions.md §四「违规怎么办」的实现 ——
#         把命名/单位/选择/验证等级/出处五条规则变成**会执行的门禁**，
#         而不是文档里的建议。
# 官方依据: 无（本工具只读本仓库文件，不涉及 SolidWorks API）
# 许可:   本仓库 MIT
# ⚠ 本工具为**静态文本校验**，不连 SolidWorks、不运行被扫描项目，
#   未在本机实测（见 AGENTS.md 铁律 2）。
# 覆盖:   后续同级定义
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent

#: ⚑ **R 编号登记表**（轮 193 加）：`docs/union-conventions.md` 的「二之补」一节是
#: **R1–R14 的唯一登记处**（此前 R1–R11 的权威定义在**另一个仓库**的提案里、
#: 而 R12–R14 提案里根本没有 ⇒ ★ 读代码的人无法核验这些编号）。
#: ⚠ 本节是**手写**的（含判断与出处），但**编号集合**由 `check_rule_registry()` 守。
CONVENTIONS_DOC = ROOT / "docs" / "union-conventions.md"
#: 登记表里的一行形如 `| **R7** | … |`
REGISTRY_ROW = re.compile(r"^\|\s*\*\*R(\d{1,2})\*\*\s*\|", re.M)
#: 段名 / 说明里引用的编号（含 `R1-R3` 这种区间写法）
RULE_REF = re.compile(r"\bR(\d{1,2})\b")
RULE_RANGE = re.compile(r"\bR(\d{1,2})\s*[-–]\s*R?(\d{1,2})\b")


#: 规则 5：许可白名单 —— 只有这两个能抄（见 union-conventions.md 表格）
COPYABLE_LICENSES = {"MIT", "Apache-2.0"}

#: 规则 4：验证等级枚举
LEVELS = {"verified", "source_verified", "stitched", "indexed", "not_implemented"}

#: ⚑ **R12（轮 58 加）：能力清单的 `source` 标记枚举** —— 回答「这条是**并入来的**还是**本项目自研的**」。
#: ⚠ 与 `level` **不是一回事**：`level: verified` 说的是「**有我们自己的运行证据**」，
#: **不是**「代码是我们写的」（`AGENTS.md §一 A2` 明写这条）。
#: ⚠ `undetermined` 是**合法且被鼓励**的值：
#: `THIRD-PARTY-NOTICES.md` 写着「把**未并入**的东西写成**已并入**，是**归属造假**，
#: 比遗漏更严重」⇒ **没有依据就留 `undetermined`，不猜**。
SOURCES = {"original", "merged", "upstream", "mixed", "undetermined"}

#: R11：执行模式的值域（`unattended` 是无人值守授权，只有 verified 才能带）
VALID_MODES = {"interactive", "reviewed", "unattended"}

#: R1：五级枚举与 provenance 必填性挂在这个 schema 版本上
SCHEMA_VERSION = "2.0"

#: R3：能力 id 必须是稳定 slug（改 id 会断掉 operation_routes 的引用与既有 provenance 指向）
ID_SLUG = re.compile(r"^[a-z][a-z0-9_]*$")

#: R6：provenance.repo 必须是 owner/repo 全名，不是克隆目录名
REPO_FULLNAME = re.compile(r"^[\w.-]+/[\w.-]+$")

#: R10：该来源仓的 References/ 是达索财产（MIT 仓里被点名的唯一例外）
ANGELSIX_REPO = "angelsix/solidworks-api"

#: R11 第二半：**把 level 比较当作授权来源**才算违规（判据刻意收窄）。
#: 只扫「赋值给授权语义词、且右侧是 level 比较」——即从等级*推断*出授权。
#: 不扫「读某个授权信号」（如编排器读 `ready_for_unattended_use` 来降级，
#: 那是消费授权结论，不是制造第二个真源），也不扫纯注释与 docstring。
AUTHORIZATION_ASSIGN = re.compile(
    r"""^\s*[\"']?[\w]*(?:unattended|authorized|无人值守)[\w]*[\"']?\s*[:=].*"""
    r"""(?:level[\"'\]]*\s*==|==\s*(?:CapabilityLevel\.VERIFIED|[\"']verified[\"']))""",
    re.IGNORECASE,
)

#: 授权词（函数名与变量名共用）
AUTHORIZATION_WORD = re.compile(r"unattended|authoriz|无人值守", re.IGNORECASE)

#: 一行里出现 level 比较（形状②用；形状①的赋值模式已含此意）
LEVEL_IN_LINE = re.compile(
    r"""level[\"'\]]*\s*==|==\s*(?:CapabilityLevel\.VERIFIED|[\"']verified[\"'])"""
)

#: 规则 1：工具命名
TOOL_NAME = re.compile(r"^(solidworks|cadstudio)_[a-z0-9_]+$")


def normalize_license(lic: str) -> str:
    """把许可字符串归一化到白名单比对用的基名。

    与 `check_sources()` 里 L70 那处用的是同一手法（去掉全角括号里的附注）——
    来源表里的许可写作 `"Apache-2.0（见 NOTICE）"` 这类带注形式，
    归一化后才能与 `COPYABLE_LICENSES` 比对。
    """
    return lic.split("（")[0].strip()


def check_sources() -> list[str]:
    """规则 5：每个并入来源必须有 repo / license / 验证状态。"""
    bad: list[str] = []
    f = ROOT / "tools" / "union-sources.json"
    if not f.is_file():
        return ["缺少 tools/union-sources.json（先跑 tools/build_union_sources.py）"]
    data = json.loads(f.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        bad.append("union-sources.json 的 schema_version 不是 1.0")
    for s in data.get("sources", []):
        repo = s.get("repo", "")
        if not re.match(r"^[\w.-]+/[\w.-]+$", repo):
            bad.append("来源 repo 不是 owner/repo 形式: %r" % repo)
        lic = s.get("license", "")
        base = lic.split("（")[0].strip()
        if base not in COPYABLE_LICENSES:
            bad.append("来源 %s 的许可 %r 不在可抄白名单内 —— 只能读思想" % (repo, lic))
        if "declared_verified" not in s:
            bad.append("来源 %s 缺 declared_verified 字段（必须显式，可为空串）" % repo)
        if not s.get("note"):
            bad.append("来源 %s 缺 note（必须写明验证口径的真相）" % repo)
    return bad


def normalize_generated_text(text: str) -> str:
    """★ 把**非数据字段**（生成日期/时间戳）换成占位，再用于比对生成物。

    ## 为什么必须有它（★ 2026-10-10 实测 · 规格 295）

    R8 做的是**逐字节比对**（「重生成出来的」vs「盘上那份」），而
    `scripts/gen_level_audit.py:81` **把 `date.today()` 写进正文**：

        > 生成日期：2026-10-10 ｜ 数据源：`capabilities.yaml`（`schema_version` = `2.0`）

    ⇒ ★★ **跨过午夜 ⇒ 即便数据零变化，两份也必然不同** ⇒ **每天一次假红**。
    ★ 实测：只改那一个日期字段（数据一字不改）⇒ `[FAIL] … 与最新数据**不一致**`；
    ★ 而 `git diff` 只有 **2 行**、只差那个日期。

    ⇒ ★★★ **定则：比生成物时先剥掉时间戳/日期** ——
      否则「日期变了」被误判成「数据变了」，而**假红会淹没真红**。

    ⚠ **不是静默吞掉**：只有**已知的非数据字段**被替换成占位（字段名保留），
      其余一字不动 ⇒ ★ **真数据变化照样报红**（判据 `test_real_data_difference_is_still_red` 守着）。

    ★ 与 `docs/AUTO_HANDOFF.md` ③ 第 **74** 条同源（上一轮记下的坑，本轮修）。
    """
    #: ★ 只认「字段名 + 值」的形状；★ 字段名保留、只把值换成占位
    #:   · 生成日期：2026-10-10
    #:   · 生成时间：2026-10-10 12:34:56
    text = re.sub(r"(生成日期\s*[:：]\s*)\d{4}-\d{2}-\d{2}", r"\g<1><DATE>", text)
    text = re.sub(r"(生成时间\s*[:：]\s*)\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}",
                  r"\g<1><TIMESTAMP>", text)
    return text


def check_docs() -> list[str]:
    """规范与地图必须存在，且地图是生成物；**R8 的等级审计也要在且是最新的**。"""
    bad: list[str] = []
    for rel in ("docs/union-conventions.md", "docs/union-coverage-matrix.md",
                "docs/union-level-audit.md"):
        if not (ROOT / rel).is_file():
            bad.append("缺少 %s" % rel)
    mp = ROOT / "docs" / "union-coverage-matrix.md"
    if mp.is_file() and "本文件是生成物" not in mp.read_text(encoding="utf-8")[:600]:
        bad.append("union-coverage-matrix.md 顶部缺少「本文件是生成物」声明")
    # ⚑ **R8 的新鲜度（轮 60 加）**：`docs/union-level-audit.md` 必须是**能重生成出来的那份**。
    #   ★ 这条是**实测逼出来的**：此前 R8 只在那句 docstring 里承诺过，
    #     **既没有生成器、也没有读者**，而文件**不存在** ⇒ 读文档的人会以为
    #     「等级已经审计过了」，**而审计根本没发生**（「文档串与代码不符比没有文档更糟」）。
    #   ⚠ 判据是**内容一致**（不是存在）：把当下数据重新生成一遍，逐字节比对
    #     ⇒ 「忘记重生成」当场变成红灯，而不是等评审时才发现。
    #   ★★ **2026-10-10（规格 295）订正**：比对前**先剥掉非数据字段**（生成日期/时间戳）——
    #     ★ 生成器**应当**记录生成时间，而「日期变了」**不是**「数据变了」
    #     ⇒ 不剥的话**每天一次假红**（★ 假红会淹没真红）。
    #     ★ 归一化在 `normalize_generated_text()`，★ 只替换**已知的**非数据字段。
    audit = ROOT / "docs" / "union-level-audit.md"
    if audit.is_file():
        gen = ROOT / "scripts" / "gen_level_audit.py"
        if gen.is_file():
            import importlib.util as _ilu
            try:
                _spec = _ilu.spec_from_file_location("_gen_level_audit", gen)
                _mod = _ilu.module_from_spec(_spec)
                _spec.loader.exec_module(_mod)
                want = _mod.build(json.loads(
                    (ROOT / "capabilities.yaml").read_text(encoding="utf-8")), sys.modules[__name__])
                #: ★★ 两侧都归一化（★ 生成器写「今天」、盘上那份写「昨天」⇒ 都换成占位）
                if normalize_generated_text(want) != normalize_generated_text(
                        audit.read_text(encoding="utf-8")):
                    bad.append("docs/union-level-audit.md 与最新数据**不一致** —— "
                               "跑 `python scripts/gen_level_audit.py` 重生成（R8）"
                               "（★ 已忽略**非数据字段**：生成日期/时间戳）")
            except Exception as exc:  # noqa: BLE001 —— 生成器自身坏了要说出来，不能吞
                bad.append("R8 新鲜度检查无法执行（生成器报错）：%s: %s"
                           % (type(exc).__name__, exc))
    return bad


def check_map_fresh() -> list[str]:
    """地图必须与来源数据同步（防止手改或忘记重生成）。"""
    import subprocess
    mp = ROOT / "docs" / "union-coverage-matrix.md"
    gen = ROOT / "tools" / "build_union_map.py"
    if not (mp.is_file() and gen.is_file()):
        return []
    before = mp.read_text(encoding="utf-8")
    proc = subprocess.run([sys.executable, str(gen)], capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=180, cwd=str(ROOT), stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        return ["build_union_map.py 执行失败: %s" % (proc.stderr or "")[-200:]]
    after = mp.read_text(encoding="utf-8")
    if before != after:
        # ⚑ 说清**为什么**不同步（2026-10-01 加）。
        # 本会话亲身踩过：往 `scripts/` 加了两个函数 ⇒ 地图「本仓库能力面」列计数变了
        # ⇒ 地图过期。当时先怀疑「门禁抖动」，浪费一轮 —— 这条诊断就是为了避免重演。
        return [
            "union-coverage-matrix.md 与来源数据不同步 ⇒ 重跑 "
            "`python tools/build_union_map.py` 并提交。\n"
            "        常见原因（按概率）：\n"
            "          ① **增删了 `scripts/sw_*.py` 里的公开函数** ⇒ 地图的"
            "「本仓库能力面」列计数变了；\n"
            "          ② 改了 `tools/union-sources.json`（四家的域/许可/验证口径）；\n"
            "          ③ 有人手改了地图。\n"
            "        诊断：`python tools/build_union_map.py` 后看 `git diff "
            "docs/union-coverage-matrix.md` —— 差异在哪一列，就是哪一类原因。\n"
            "        ⚠ 这三类里只有 ② 需要人工判断；① 是**纯机械**的（跑一遍再提交即可）。"
        ]
    return []


def check_capabilities_schema() -> list[str]:
    """R1–R3、R6、R9、R10：能力清单的形状（docs/capabilities-schema-proposal.md §五）。

    R4（条数 ≥10）留在 `release_check.py` 的现有断言；R5/R7/R11 在
    `check_capabilities_levels()`；R8 读生成物 `docs/union-level-audit.md`。

    ⚑ **`provenance` 的触发条件只有 `source_verified`**（裁断修正 B2）：
    自研但未运行的 `stitched` 没有来源仓，填一个指向本仓库的值属于给字段安它没有的
    含义 —— 它们允许为空。`indexed` 的出处是官方接口族，记在 `evidence`，
    也不是来源仓的 `provenance`。
    """
    bad: list[str] = []
    f = ROOT / "capabilities.yaml"
    if not f.is_file():
        return ["缺少 capabilities.yaml"]
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ["capabilities.yaml 不是合法 JSON: %s" % exc]

    # R1：schema_version 必须挂在 2.0（五级枚举与 provenance 必填性挂在它上面）
    sv = data.get("schema_version")
    if sv != SCHEMA_VERSION:
        bad.append('capabilities.yaml 的 schema_version 不是 "%s"（读到 %r）—— '
                   "五级枚举与 provenance 必填性挂在 %s 上" % (SCHEMA_VERSION, sv, SCHEMA_VERSION))

    # R3：id 全局唯一且是稳定 slug
    seen: set[str] = set()
    for c in data.get("capabilities", []):
        cid = c.get("id", "")
        if cid in seen:
            bad.append("能力 id 重复：%s" % cid)
        seen.add(cid)
        if not ID_SLUG.match(str(cid)):
            bad.append("能力 id 不是稳定 slug：%s" % cid)

    for c in data.get("capabilities", []):
        cid = c.get("id", "?")
        lv = c.get("level")
        # ⚑ **R12（2026-10-01 轮 58 加）：`source` 标记** ——
        #   把「并入来的」与「本项目自研的」分开。此前 schema **没有**这个字段 ⇒
        #   29 条里**无法区分**（例：`requirements_planning` 的 backend 是 `local-agent`，
        #   显然是自研，却**没有地方这么说**）。见 `AGENTS.md §一 A2` 的「两层 provenance」。
        #   ⚠ **`undetermined` 是合法值**（`THIRD-PARTY-NOTICES.md`：「把未并入的东西写成已并入，
        #     是**归属造假**，比遗漏更严重」）⇒ 宁可留 `undetermined`，不猜。
        #   ⚠ `source_evidence` **必须非空** —— 一个没有依据的分类等于没分类。
        src = c.get("source")
        if src not in SOURCES:
            bad.append("能力 %s 的 source=%r 不在枚举 %s 内" % (cid, src, sorted(SOURCES)))
        if not str(c.get("source_evidence") or "").strip():
            bad.append("能力 %s 缺 source_evidence（分类必须有依据；没有依据就写 undetermined 并说明）" % cid)
        # ⚑ **R13（轮 59 加）：`source` 与 `provenance` 必须**自洽**** ——
        #   `provenance` 非空 ⇒ 该能力**有第三方来源** ⇒ `source` **不能**是 `original`。
        #   ★ 这条是**实测逼出来的**：`mold_tools` 曾同时有
        #     `source: "original"` 与一条指向 `Eduardof0nt/Solidworks-MCP-Server` 的 `provenance`
        #     —— **字段之间互相打架**，而 R12（只查枚举与依据非空）**看不见**。
        #     ⇒ 「原创」与「有来源」是互斥的陈述，机器能判。
        prov = c.get("provenance")
        if src == "original" and prov:
            repos = ", ".join(str(p.get("repo")) for p in prov if isinstance(p, dict))
            bad.append("能力 %s 的 source='original' 与 provenance（%s）**自相矛盾** —— "
                       "有第三方来源就不能叫原创（应改 mixed 或 upstream）" % (cid, repos))
        # ⚑ **R13b：反向** —— `provenance` 非空却写 `upstream` 也**不一定**对，但**无法机器判**
        #   （「来源是上游还是四家」需要看 repo 名）⇒ 只在 repo 明确**不是**上游时提示。
        if src == "upstream" and prov:
            for p in prov:
                if isinstance(p, dict) and "wzyn20051216" not in str(p.get("repo", "")):
                    bad.append("能力 %s 的 source='upstream' 而 provenance 指向 %s —— "
                               "「上游」特指 `wzyn20051216/solidworks-automation-skill`，"
                               "别家来源请用 mixed" % (cid, p.get("repo")))
        entries = c.get("provenance")
        # R6：只有来源派生的 source_verified 强制要 provenance
        if lv == "source_verified" and not entries:
            bad.append("能力 %s 是 source_verified 却没有 provenance —— 外部来源派生必须有出处" % cid)
        if not entries:
            continue
        if not isinstance(entries, list):
            bad.append("能力 %s 的 provenance 必须是数组（一条能力可由多个来源并入）" % cid)
            continue
        for i, item in enumerate(entries):
            if not isinstance(item, dict):
                bad.append("能力 %s 的 provenance[%d] 必须是对象" % (cid, i))
                continue
            repo = str(item.get("repo", ""))
            # R6：repo 是 owner/repo 全名，不写克隆目录名
            if not REPO_FULLNAME.match(repo):
                bad.append("能力 %s 的 provenance.repo 不是 owner/repo 形式：%r" % (cid, repo))
            # R6：license 归一化后必须在白名单内
            lic = normalize_license(str(item.get("license", "")))
            if lic not in COPYABLE_LICENSES:
                bad.append("能力 %s 的 provenance.license 不在白名单：%r" % (cid, item.get("license")))
            # R6：upstream_verified 字段必须**存在**（可为空串，表示来源没声明跑过）
            if "upstream_verified" not in item:
                bad.append("能力 %s 的 provenance 缺 upstream_verified 字段"
                           "（来源没声明跑过就写空串，但不能没有）" % cid)
            # R9：files 为非空数组，路径相对来源仓根
            files = item.get("files")
            if not isinstance(files, list) or not files:
                bad.append("能力 %s 的 provenance.files 是空数组或不是数组" % cid)
            # R9：commit / tag 可省略，出现必须是字符串
            for opt in ("commit", "tag"):
                if opt in item and not isinstance(item[opt], str):
                    bad.append("能力 %s 的 provenance.%s 不是字符串：%r" % (cid, opt, item[opt]))
            # R10：angelsix/solidworks-api 的 References/ 是达索财产，只能原样配 SolidDNA 用
            if isinstance(files, list) and repo == ANGELSIX_REPO:
                if any(str(p).replace("\\", "/").startswith("References/") for p in files):
                    bad.append("能力 %s 的 provenance 引用了 angelsix 的 References/ —— "
                               "那是达索财产，只能原样配 SolidDNA 用" % cid)
    return bad


def _docstring_lines(src: str) -> set[int]:
    """所有模块/类/函数 docstring 占的行号（含其内部行）。

    不排除它们会误报 —— 说明「这处判据为什么改成 allowed_modes」的 docstring
    里天然会写出 `level == "verified"` 这个旧口径，那不是违规，是解释。
    """
    import ast

    out: set[int] = set()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if not body:
                continue
            first = body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) \
                    and isinstance(first.value.value, str):
                out.update(range(first.lineno, (first.end_lineno or first.lineno) + 1))
    return out


def _authorization_functions(src: str) -> dict[int, str]:
    """授权语义词命名的函数 → 其函数体的行号范围（1-based，含签名行）。

    用于抓第二种违规形状：**函数名叫 `*unattended*` / `*authoriz*`，函数体却直接
    `return ... level == "verified"`**。只扫赋值行抓不到这种 —— 而那正是
    `unattended_allowed()` 被改回旧实现的形状。
    """
    import ast

    out: dict[int, str] = {}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if AUTHORIZATION_WORD.search(node.name):
                for ln in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                    out[ln] = node.name
    return out


def check_authorization_source() -> list[str]:
    """R11 第二半：授权真源是 `allowed_modes`，静态扫描「用 level 推断授权」的写法。

    2026-10-01 迁移时实测该判据在代码里有 **4 条**路径，其中两条不在
    `unattended_allowed()` 里（`queue_worker` 的任务门禁、`sw_capability_probe` 的
    `ready_for_unattended_use`）—— **只改那个函数是抓不全的**，是既有测试红了才暴露。
    本检查把这一条变成事前的静态门禁。

    抓两种形状（`tools/prove_authorization_check.py` 对两者都喂了真实反例）：
    ① **赋值**给授权语义词、右侧是 level 比较 —— 从等级*推断*出授权；
    ② **授权语义词命名的函数**，函数体里出现 level 比较 —— 例如把
       `unattended_allowed()` 改回 `return ... level == "verified"`。

    刻意放过：**消费**授权结论的代码（编排器读 `ready_for_unattended_use` 来降级 ——
    那是对的，不是第二个真源）、纯注释、以及所有 docstring
    （说明「为什么改成 allowed_modes」的 docstring 天然会写出旧口径）。
    """
    bad: list[str] = []
    for p in sorted(ROOT.rglob("*.py")):
        rel = p.relative_to(ROOT).as_posix()
        if any(part in rel for part in (".git/", "__pycache__/", "node_modules/")):
            continue
        if rel == "scripts/check_union_conventions.py":
            continue  # 本文件里的模式字符串不是判据本身
        try:
            src = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        skip = _docstring_lines(src)
        auth_funcs = _authorization_functions(src)
        for n, line in enumerate(src.splitlines(), 1):
            if n in skip or line.lstrip().startswith("#"):
                continue
            if AUTHORIZATION_ASSIGN.match(line):
                bad.append("%s:%d 用 level 推断无人值守授权（真源应是 allowed_modes）: %s"
                           % (rel, n, line.strip()[:80]))
                continue
            if n in auth_funcs and LEVEL_IN_LINE.search(line):
                bad.append("%s:%d 授权函数 %s() 的函数体里按 level 判授权"
                           "（真源应是 allowed_modes）: %s"
                           % (rel, n, auth_funcs[n], line.strip()[:80]))
    return bad


def check_capabilities_levels() -> list[str]:
    """规则 4 + R5 + R7 + R11：level 在五级枚举内、verified 有证据、授权与等级自洽。

    ⚑ `verified_versions` **只对 CAD 后端**要求（SolidWorks / AutoCAD）。
    首次跑本门禁时它误报了 `requirements_planning`（backend `local-agent`）和
    `geometry_and_delivery_review`（`local-python`）—— 这两条是**代理层与本地
    Python 层**能力，本来就没有「SolidWorks 版本」可言。
    ⇒ 规则收紧为：**只在 backends 含 CAD 后端时**要求版本证据。

    ⚑ 2026-10-01 `pilot`→五级迁移完成后，`pilot` / `reference_only` 的迁移期豁免已删 ——
    留着它们等于枚举实际是六七个值，是双写换一种形式
    （docs/capabilities-schema-proposal.md §1.1）。

    ⚑ R11（同提案 §五）：`allowed_modes` 的值域是三个；且 `level != verified` 不得带
    `unattended` —— 没到「我们真机跑过」就不许放开无人值守。
    """
    bad: list[str] = []
    f = ROOT / "capabilities.yaml"
    if not f.is_file():
        return ["缺少 capabilities.yaml"]
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ["capabilities.yaml 不是合法 JSON: %s" % exc]
    for c in data.get("capabilities", []):
        cid = c.get("id", "?")
        lv = c.get("level")
        backends = c.get("backends") or []
        modes = set(c.get("allowed_modes") or [])
        is_cad = any(b.startswith(("solidworks", "autocad")) for b in backends)
        if lv not in LEVELS:
            bad.append("能力 %s 的 level=%r 不在枚举 %s 内" % (cid, lv, sorted(LEVELS)))
        if lv == "verified" and not c.get("evidence"):
            bad.append("能力 %s 标 verified 但 evidence 为空 —— 「跑过」必须有证据" % cid)
        if lv == "verified" and is_cad and not c.get("verified_versions"):
            bad.append("能力 %s 是 CAD 能力且标 verified，但 verified_versions 为空 —— "
                       "「跑过」必须有版本证据" % cid)
        if lv == "not_implemented" and not c.get("limitations"):
            bad.append("能力 %s 标 not_implemented 但没写原因" % cid)
        invalid_modes = modes - VALID_MODES
        if invalid_modes:
            bad.append("能力 %s 的 allowed_modes 含非法值: %s" % (cid, sorted(invalid_modes)))
        if "unattended" in modes and lv != "verified":
            bad.append("能力 %s 的 level=%r 却带了无人值守授权 —— R11 禁止" % (cid, lv))
    return bad


#: ⚑ **R14（2026-10-01 轮 67 加）：`docs/union-not-doing.json` 的形状** ——
#: 承载 `AGENTS.md §一 A1` 的**另一半**：「域覆盖矩阵里本仓库每一格**都有来源，
#: 或写明「不做 + 原因」」。
#: ⚠ 此前**只有「有来源」那一半有机制**（`capabilities.yaml` 的 `source`/`source_evidence`，
#:   由 R12 守），而「不做 + 原因」**一格机制都没有** —— 矩阵里只有「缺 N」，
#:   读者**无从知道哪些是「我们不做」、哪些是「还没做」**（轮 67 实测确认）。
#: ⚠ 三条判据（每条都必须**非空**）：`subject` / `reason` / `evidence`。
#:   一个没有依据的「不做」等于**用一个词掩盖一个缺口**，比不写更糟。
#: ⚠ **文件可以不存在**（= 一个都没登记）—— 那**不是错误**，但生成器会在矩阵里
#:   打一行「本清单为空」的提醒（见 `tools/build_union_map.py`）。
NOT_DOING_PATH = ROOT / "docs" / "union-not-doing.json"


def rule_registry() -> set:
    """从 `docs/union-conventions.md` 的「二之补 R 编号登记表」读出**已登记的编号集合**。

    :returns: 形如 `{1, 2, …, 14}` 的集合；文档或该节缺失时返回**空集**
        （空集会让 `check_rule_registry` 报错，而不是静默通过 —— 见那里的说明）。
    """
    if not CONVENTIONS_DOC.is_file():
        return set()
    return {int(m.group(1)) for m in REGISTRY_ROW.finditer(
        CONVENTIONS_DOC.read_text(encoding="utf-8", errors="replace"))}


def referenced_rules(titles) -> set:
    """从一个可迭代的**段名**里收集被引用的编号（含 `R1-R3` 这类区间写法）。

    :param titles: 段名（或任何文本）的可迭代对象。
    :returns: 形如 `{1, 2, 3, 6, …}` 的集合。
    """
    out: set = set()
    for t in titles:
        s = str(t)
        for m in RULE_REF.finditer(s):
            out.add(int(m.group(1)))
        for m in RULE_RANGE.finditer(s):          #: `R1-R3` ⇒ 展开成 1,2,3
            out.update(range(int(m.group(1)), int(m.group(2)) + 1))
    return out


#: ⚑ **执行侧**的扫描范围（轮 194 扩）：只 `scripts/*.py` ——
#: ⚠ **`tests/` 与 `docs/` 故意不在内**，理由见 `check_rule_registry` 的 docstring
#:   （负例测试要能写出未登记的编号；docs 是历史记录）。
RULE_SCAN_GLOB = "*.py"


def unregistered_refs(glob_pat: str, registry: set, base: Path | None = None) -> dict:
    """扫 `scripts/` 下匹配 `glob_pat` 的文件，回报**引用了未登记编号**的那些。

    :param glob_pat: 文件通配（如 `"*.py"`）。
    :param registry: 已登记的编号集合。
    :param base: 扫描目录；缺省为 `<repo>/scripts`（**测试可传临时目录**，于是不必动真文件）。
    :returns: `{文件名: [未登记的编号,…]}`；**全部在册时返回空 dict**。
    """
    d = base if base is not None else (ROOT / "scripts")
    out: dict = {}
    if not d.is_dir():
        return out
    for p in sorted(Path(d).glob(glob_pat)):
        refs = referenced_rules([p.read_text(encoding="utf-8", errors="replace")])
        un = sorted(refs - registry)
        if un:
            out[p.name] = un
    return out


def check_rule_registry(titles) -> list:
    """R 编号登记表：**引用的编号必须都已登记，且登记表本身无缺号**。

    :param titles: 本门禁各段的**段名**（运行时传入 `groups` 的标题）。

    ⚠ **为什么需要它**（轮 193 实测）：
    ```
    · 本门禁引用 **R1–R14**，而**代码仓库里此前没有任何一处**说明 R1–R11 是什么 ——
      它们的权威定义在**另一个仓库**的 `capabilities-schema-proposal.md`
    · 反过来 **R12/R13/R14** 是后来（轮 58/59/67）加的，**那份提案里没有它们**
    ⇒ ★★ 读代码的人**无法核验这些编号代表什么**；而对不上号时也**没有任何门禁会响**。
    ```
    ⇒ 本检查把「编号的**登记**」变成**结构上可核验**的事：
      ① 引用了未登记的编号 ⇒ 报；
      ② 登记表有缺号（如登记了 R1,R3 而没 R2）⇒ 报。
    ⚠ **已知的分工**：`R4` 由 `release_check.py` 的既有断言守，**不在本门禁的段名里出现**
      ⇒ 本检查覆盖不到它的**执行**，只保证它**被登记**。
    """
    bad: list = []
    reg = rule_registry()
    if not reg:
        bad.append("读不出 R 编号登记表 ⇒ `docs/union-conventions.md` 的「二之补 R 编号登记表」"
                   "缺失或形态变了（**这不等于没问题**）")
        return bad
    ref = referenced_rules(titles)
    for n in sorted(ref - reg):
        bad.append("段名引用了 **R%d**，但登记表里没有它 ⇒ 读代码的人查不到它代表什么" % n)
    #: ⚑⚑ **轮 194：覆盖面从「段名」扩到「**执行侧**」** ——
    #:   ★ 轮 193 只查段名，而实测「引用 R 编号的文件」有 **17 个**（3 个门禁 + 4 个其它 scripts +
    #:     5 个 tests + 5 个 docs）⇒ 段名只覆盖了其中**极小一块**。
    #:   ★★ **范围为什么是 `scripts/*.py`（不含 `tests/`、不含 `docs/`）** —— 如实声明覆盖面：
    #:     · `scripts/` = **执行侧**（谁在**执行**这些规则）⇒ 引错编号就是**执行错规则**
    #:     · `tests/` **故意排除**：**负例测试必须能写出未登记的编号**（如 `R<n>` 那种**不存在的**编号）
    #:       来证明判据有牙 —— 把 tests 纳进来会**把负例判成违规**
    #:       ⚠⚠ **这一行本身踩过一次（轮 194）**：第一版我在这里写了一个**具体的**未登记编号当例子，
    #:       ★ 而新判据**立刻把它抓出来了**（"执行侧引用了未登记编号"）。
    #:       ⇒ ★ **定则**：**在本文件里举例，请用 `` R<n> `` 这种占位写法，不要写具体编号** ——
    #:         判据分不出「举例」与「引用」，所以**要让举例本身不构成引用**（比去剥注释更稳）。
    #:       —— 把 tests 纳进来会**把负例判成违规**
    #:     · `docs/`（含 ROADMAP / known-facts / specs）**故意排除**：那是**历史记录**，
    #:       记的是"当时引用过什么"，**不该被后来的登记表追着改**
    #:   ⚠ 实测（轮 194）：执行侧 `scripts/*.py` 里引用 R 编号的共 **7 个文件**，**全部已在册** ⇒
    #:     本扩展**当前不报任何东西**（★ 这是"扩了覆盖面而结论不变"，不是"没生效"）。
    for name, refs in sorted(unregistered_refs(RULE_SCAN_GLOB, reg).items()):
        bad.append("`scripts/%s` 引用了未登记的 %s ⇒ 执行侧引错编号 = **执行错规则**"
                   % (name, "、".join("R%d" % n for n in refs)))
    lo, hi = min(reg), max(reg)
    missing = sorted(set(range(lo, hi + 1)) - reg)
    if missing:
        bad.append("登记表缺号：%s（登记区间是 R%d–R%d）"
                   % ("、".join("R%d" % m for m in missing), lo, hi))
    return bad


def check_not_doing() -> list:
    """R14：`union-not-doing.json` 的每条都必须有 `subject` / `reason` / `evidence`。"""
    import json
    bad: list = []
    if not NOT_DOING_PATH.is_file():
        return bad                      # 不存在 = 空清单，合法（生成器会提醒）
    try:
        data = json.loads(NOT_DOING_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ["%s 不是合法 JSON：%s" % (NOT_DOING_PATH.name, exc)]
    items = data.get("not_doing")
    if not isinstance(items, list):
        return ["%s 的 `not_doing` 必须是数组" % NOT_DOING_PATH.name]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            bad.append("not_doing[%d] 不是对象" % i)
            continue
        subj = str(item.get("subject") or "").strip()
        if not subj:
            bad.append("not_doing[%d] 缺 `subject`（不做什么）" % i)
        if not str(item.get("reason") or "").strip():
            bad.append("not_doing[%d]（%s）缺 `reason` —— 一条没有原因的「不做」"
                       "等于用一个词掩盖一个缺口" % (i, subj or "?"))
        ev = item.get("evidence")
        if not isinstance(ev, list) or not [e for e in ev if str(e).strip()]:
            bad.append("not_doing[%d]（%s）缺**非空** `evidence` —— "
                       "凭什么这么判定？没有依据的「不做」比不写更糟" % (i, subj or "?"))
    return bad


def main() -> int:
    #: ⚑ **轮 193：段名先单独列出来**，因为 `check_rule_registry` 要读它们
    #:   （「段名引用的编号必须在登记表里」）—— 这样检查**不需要解析自己的源码**。
    _TITLES = (
        "规则 5 · 出处与许可",
        "规范与地图存在性",
        "地图与来源同步",
        "R1-R3/R6/R9/R10/**R12**/**R13** · 清单形状",
        "规则 4 + R5/R7/R11 · 验证等级与授权",
        "R11 · 授权真源",
        "**R14** · A1 的另一半「不做 + 原因」",
        "R 编号登记表（引用的编号必须都已登记）",
    )
    groups = (
        (_TITLES[0], check_sources()),
        (_TITLES[1], check_docs()),
        (_TITLES[2], check_map_fresh()),
        (_TITLES[3], check_capabilities_schema()),
        (_TITLES[4], check_capabilities_levels()),
        (_TITLES[5], check_authorization_source()),
        (_TITLES[6], check_not_doing()),
        (_TITLES[7], check_rule_registry(_TITLES)),
    )
    #: ⚑ **首行汇总**（轮 192）：本门禁实际有 **7 段**检查，而此前首行只显示**第一段**
    #:   （`[PASS] 规则 5 · 出处与许可`）⇒ ★ 只看首行的人会以为它只查了"规则 5"。
    #:   ⚠⚠ 而且**这一处的教训值得留**：我先用「首行里有没有数字」当"有没有分母"的判据，
    #:   那一段首行里的 `5` **是规则编号、不是分母** ⇒ ★ **`\d` 区分不了这两件事**。
    #:   ⇒ 所以这行汇总要**明写"段"**，不能只丢一个数字。
    print("并入规范门禁 · **%d** 段检查（%s）"
          % (len(groups), "、".join(t.split(" · ")[0] for t, _ in groups)))
    failed = 0
    for title, bad in groups:
        if bad:
            failed += len(bad)
            print("[FAIL] %s" % title)
            for b in bad:
                print("   - %s" % b)
        else:
            print("[PASS] %s" % title)
    print()
    if failed:
        print("并入规范门禁未通过：%d 项。见 docs/union-conventions.md" % failed)
        return 1
    print("并入规范门禁通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
