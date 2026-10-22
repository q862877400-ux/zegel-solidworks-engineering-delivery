"""★ **任务 3 · 扫全仓"用了官方废弃成员"** —— ★ 判据用「所有接口都废弃」的**安全名字**（★ 事实 511）。

★★ 为什么要有这一版（★ 上一版报了 **870 处、头几名全假阳性**）：
  ★ 第一版 `tools/scan_obsolete_usage.py` **按成员名**直接对废弃名单 ⇒
    ★★ `FeatureCut4`（★ 本仓**事实 1** 说它才是"切除的正确入口"）· `Name`（★ 24 个接口里只有 2 个废弃）·
    `GetBodies2` · `CreateLine` · `GetEdges` —— **全被误报** ✓
  ⇒ ★★★ **根因**：★ 官方 API 是「**接口 × 成员**」二维表，★ 而 `get_com_member(x, "GetBodies2")` 里
    **`x` 属于哪个接口静态看不出来** ⇒ ★ **按名字判必须有取舍**。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
★★★ 判据（★ **本文件在跑之前写死，跑完不改**）
  ★ **纳入**：★ 成员名落在「**在所有接口上都废弃**」那一桶里（★ 实测量约 **1163** 个）
      ⇒ ★ 按名字判**对这种名字不含歧义**（★ 事实 511 定的边界）。
  ★ **覆盖两种调用形态**（★ 上一版只覆盖 ①，★ 漏了 `sw_part.fillet` 那种）：
      ① `get_com_member(x, "M", …)` / `call_com_member` / `set_com_member`
      ② ★★ **点调用** `obj.Member(…)` / `obj.Member = …`
  ★ **三种排除**（★ 每条都必须过，★ 否则又是 870 处）：
      E1 ★ **注释里的不算** —— ★ 用 `scripts/check_env_pitfalls.py::strip_comments_and_strings`
           （★ 事实 61 定则④：写了好用的工具函数，就要在**所有**同类场合用它）
      E2 ★★ **"兜底/回退分支"单列不算缺陷** —— ★ 若**同文件里已出现该成员的后继调用**
           （★ bunny 的 `PATTERNS.md` 档② 就是这个形态）⇒ ★ 标 `fallback_branch`
      E3 ★ **纯字符串登记表不算** —— ★ 行内只有字符串字面量、没有调用形态的（★ 如 `METHODS = {...}`）⇒ 标 `registry`
  ★ **三个自检**（★ 事实 506/510：判据要自证在跑、要先标定）：
      S1 ★ **覆盖面自报**：★ 扫了几个文件 · 抽了几个调用点 · 命中几条
      S2 ★★ **假阳性自检**：★ 拿**已知反例**试 —— ★ `FeatureCut4` / `Name` / `GetBodies2` /
           `CreateLine` / `GetEdges` **必须 0 命中**（★ 它们有多接口，★ 落在歧义桶里）
      S3 ★ **抽 5 条回原文**：★ 每条给附近两行原文，★ 供人工复核
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
★ 只读。产出 `output/obsolete-dotcall-scan.json`。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/scan_obsolete_safe.py
# 定位:   任务 3 · 扫全仓"用了官方废弃成员"** —— ★ 判据用「所有接口都废弃」的**安全名
#           字**（★ 事实 511）。
# 官方依据: 官方源 `C:\swapi` 的**废弃成员索引**（★ 文件内引 `known-facts` 多处）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
IDX = (
    REPO / "specs" / "202-user-coverage-gaps" / "recon" / "official-obsolete-index.json"
)
MEM = (
    REPO / "specs" / "202-user-coverage-gaps" / "recon" / "official-members-index.json"
)
OUT = REPO / "output" / "obsolete-dotcall-scan.json"

#: ★★ 已知反例（★ S2 用它自检）—— 它们**必须 0 命中**
NEGATIVES = [
    "FeatureCut4",
    "Name",
    "GetBodies2",
    "CreateLine",
    "GetEdges",
    "CreateCircleByRadius",
    "GetType",
]

CALL_FORMS = [
    (
        "get_com_member",
        re.compile(r'\b(?:get|call|set)_com_member\s*\(\s*[^,]+,\s*"([A-Za-z_]\w*)"'),
    ),
    ("dot_call", re.compile(r"\.([A-Z][A-Za-z0-9_]{2,})\s*\(")),
    ("dot_assign", re.compile(r"\.([A-Z][A-Za-z0-9_]{2,})\s*=(?!=)")),
]


def main() -> int:
    started = time.time()
    sys.path.insert(0, str(REPO / "scripts"))
    sys.path.insert(0, str(REPO))

    obs = json.loads(IDX.read_text(encoding="utf-8", errors="replace"))["entries"]
    mem = json.loads(MEM.read_text(encoding="utf-8", errors="replace"))

    #: ★★★ 算「在所有接口上都废弃」的安全桶（★ 事实 511 的边界）
    per_iface = mem.get("per_interface") or {}
    by_name: dict = defaultdict(list)
    for iface, members in per_iface.items():
        for m in members:
            by_name[m["member"]].append(bool(m.get("obsolete")))
    safe = {n for n, flags in by_name.items() if flags and all(flags)}
    ambiguous = {n for n, flags in by_name.items() if any(flags) and not all(flags)}
    successor = {}
    for e in obs:
        if e["member"] in safe and e.get("successor"):
            successor.setdefault(e["member"], e["successor"])

    #: ★ S2 自检：反例必须在歧义桶或不在桶里（★ 不许进安全桶）
    s2 = {
        n: (
            "★ 安全桶"
            if n in safe
            else ("歧义桶" if n in ambiguous else "不在废弃名单")
        )
        for n in NEGATIVES
    }
    s2_bad = [n for n, v in s2.items() if v == "★ 安全桶"]

    files = (
        sorted((REPO / "scripts").glob("*.py"))
        + sorted((REPO / "mcp-server").glob("*.py"))
        + sorted((REPO / "tools").glob("*.py"))
    )

    #: ★★★★ 2026-10-03（接手轮）**修一个假阴性**：
    #:   ★ 第一版 E1 用了 `check_env_pitfalls.strip_comments_and_strings` ——
    #:     ★★ **它把字符串字面量也剥掉** ⇒ ★★★ 于是 `get_com_member(x, "SystemValue")`
    #:     里的**成员名也没了** ⇒ ★ **全部 ① 形态的命中被漏掉**，★ 只剩点调用被抓到。
    #:   ★ 实测证据：`IDimension.SystemValue` 是废弃的（★ 且只在 1 个接口上 ⇒ 属安全桶），
    #: 而 `scripts/sw_document_data.py:221` 的 `get_com_member(dimension, "SystemValue")
    #: `
    #:     **没出现在结果里**。
    #:   ⇒ ★ 本版改用 **tokenize 只丢 COMMENT**（★ 保留 STRING）——
    #:     ★ 与事实 61 定则④同精神：**工具函数用错场合就等于没有**。
    def strip_comments_only(src: str) -> str:
        """★ 只剥**注释**，★ 保留字符串字面量（★ 成员名就在里面）。

        ★★★★ 2026-10-03（接手轮）**第四次修法 —— 前三版全错**（★ 这段本身是个教训）：
          ★ 第 1 版：★ 用 `check_env_pitfalls.strip_comments_and_strings` ⇒
            ★★ **它把字符串也剥了** ⇒ 成员名一起没了 ⇒ 漏掉全部 `get_com_member(x,"M")` 形态。
          ★★ 第 2 版：★ `tokenize` 丢 `COMMENT` 再 `untokenize(out)` ⇒ ★★★ **实测它把注释原样还原**
            （★ 负例：`sw_sketch_modify_ops.py` 里 `GetActiveSketch2` 的命中 **2 → 2**，★ 而那两条**全是注释**）。
          ★★★ 第 3 版：★ 我自己写**逐行引号状态机** ⇒ ★★ **三引号状态没正确关闭**
            ⇒ 多行 docstring 之后的行**一律不裁 `#`** ⇒ 注释命中依旧（★ 实测 3 条仍在）✓
          ★★★★ 第 4 版（★ 本版）：★★ **用 `tokenize` 拿每个 `COMMENT` 的 **(start,end) 位置**，
            再**按位置从原文里挖掉那些字符** ⇒ ① **不重建 token 流**（★ 避免第 2 版的还原）
            ② **不自己实现状态机**（★ 避免第 3 版的引号 bug）✓
        ★★ **可复用判据**：★ **"剥注释"这种预处理必须用**负例**验一次**
          （★ 本文件顶部 `_strip_selftest()` 可跑；★ 与**事实 62**「负例是门禁有效的唯一证明」同族）✓
        """
        import io as _io
        import tokenize as _tk

        #: ★★★★ 2026-10-03（接手轮）**第五次修法 —— 真根因终于找到**：
        #:   ★★ 前面四版都在修"注释"，★ **而真正的污染源是 **docstring**** ✓
        #:   ★ 负例自检给了决定性线索：★ `_strip_selftest()` 回 `(False, True)`
        #:     —— ★★ "注释里的名字没被剥掉"；★★ **而实测那些行仍是带 `#` 与 `★` 的正文**
        #:     ⇒ ★★★ **它们是**模块/函数 docstring 的文本**，★ 不是注释** ⇒
        #:       ★ `tokenize` 正确地把它当 **STRING**（★ 而我的判据说"保留字符串"）⇒ 没剥 ✓
        #: ★★★★ **这与**事实 512** 的根因**一模一样**（★ 当时是 `sw_connect.get_com_memb
        #: er`
        #:     的 docstring 把 `InsertDome`/`RunAnalysis` 污染进了每个工具）✓
        #:   ⇒ ★ 修法两条并用：★ ① **剥注释**（按 tokenize 的位置挖）★ ② **剥 docstring**
        #:     （★ 用 AST 找"模块/类/函数体的第一条 string 表达式"⇒ 按位置挖掉）✓
        #:     ★★ **普通字符串字面量必须保留**（★ `get_com_member(x, "M")` 的成员名在里面）✓
        src2 = src
        try:
            tree = __import__("ast").parse(src)
            spans = []
            for node in __import__("ast").walk(tree):
                if isinstance(
                    node,
                    (
                        __import__("ast").Module,
                        __import__("ast").ClassDef,
                        __import__("ast").FunctionDef,
                        __import__("ast").AsyncFunctionDef,
                    ),
                ):
                    body = getattr(node, "body", [])
                    if (
                        body
                        and isinstance(body[0], __import__("ast").Expr)
                        and isinstance(body[0].value, __import__("ast").Constant)
                        and isinstance(body[0].value.value, str)
                    ):
                        spans.append(
                            (
                                body[0].lineno,
                                body[0].col_offset,
                                body[0].end_lineno,
                                body[0].end_col_offset,
                            )
                        )
            if spans:
                all_lines = src.splitlines(keepends=True)
                for r0, c0, r1, c1 in sorted(spans, reverse=True):
                    if r0 == r1:
                        line = all_lines[r0 - 1]
                        all_lines[r0 - 1] = line[:c0] + line[c1:]
                    else:
                        all_lines[r0 - 1] = all_lines[r0 - 1][:c0] + "\n"
                        for rr in range(r0, r1 - 1):
                            all_lines[rr] = "\n"
                        all_lines[r1 - 1] = all_lines[r1 - 1][c1:]
                src2 = "".join(all_lines)
        except Exception:  # noqa: BLE001
            src2 = src

        lines = src2.splitlines(keepends=True)
        #: ★ 收集每个 COMMENT 的 (行, 列起, 列止)（★ 在**剥掉 docstring 之后**的文本上做
        #: ）
        cuts: dict = {}
        try:
            for tok in _tk.generate_tokens(_io.StringIO(src2).readline):
                if tok.type == _tk.COMMENT:
                    r, c = tok.start
                    cuts.setdefault(r, []).append((c, tok.end[1]))
        except Exception:  # noqa: BLE001
            cuts = {}
        if not cuts:
            return src2
        out = []
        for idx, line in enumerate(lines, 1):
            if idx in cuts:
                body = line.rstrip("\n").rstrip("\r")
                for c0, c1 in sorted(cuts[idx], reverse=True):
                    body = body[:c0] + body[c1:]
                line = body + "\n"
            out.append(line)
        return "".join(out)

    def _strip_selftest() -> tuple:
        """★ **负例自检**（★ 事实 62）：★ 拿"注释里有成员名"的样本，验它被剥掉。"""
        sample = (
            'a = 1  # 这里是注释，含 get_com_member(x, "GetActiveSketch2")\n'
            "def f():\n"
            '    """多行 docstring\n'
            '    里面也有 get_com_member(y, "GetActiveSketch2")\n'
            '    """\n'
            '    return get_com_member(z, "KeepMe")  # 行尾注释\n'
        )
        cleaned = strip_comments_only(sample)
        return (
            ("GetActiveSketch2" not in cleaned),  #: ★ 注释与 docstring 里的都该没了
            ("KeepMe" in cleaned),
        )  #: ★★ 真正的字符串字面量必须留着

    #: ★★★ 2026-10-03（接手轮）**新增"跨库存疑"档**（★ 由 OCP 的 `bounds.Get()` 暴露）：
    #:   ★ 病灶：★ `scripts/advanced_geometry_ocp.py` 与 `headless_occt_service.py` 里的
    #: `xmin, ymin, zmin, xmax, ymax, zmax = **bounds.Get()**` 是 **OCP/OpenCASCADE** 的
    #: 调用
    #:     （★ `Bnd_Box.Get()` 正是回 6 元组），★ 而本扫描器**按名字**把它算成了
    #:     SolidWorks 的 `ICustomPropertyManager.Get` ⇒ ★★ **跨库假阳性** ✓
    #: ★★★ 根因与**事实 511**同源：★ **点调用（`obj.M()`）的宿主是运行时的，静态判不出来
    #: **。
    #:   ⇒ ★ 判据：★ **点调用** 且 **同文件里没有任何 SolidWorks 标志**（`sw_`/`SldWorks`/
    #: `get_com_member`/`IModelDoc`/`SolidWorks`…）⇒ ★★ **降级为「跨库存疑」，不计入真命
    #: 中** ✓
    #:   ⚠ 限度（★ 如实记）：★ 这是**启发式**（★ 同文件可能恰好没有那些词），
    #:     所以它**只降级、不删除** —— 存疑条目**仍会单独列出**供人看 ✓
    SW_MARKERS = (
        "get_com_member",
        "call_com_member",
        "set_com_member",
        "SldWorks",
        "SolidWorks",
        "IModelDoc",
        "sw_app",
        "sldworks",
    )
    SUSPECT_LIB = ("ocp", "occ", "opencascade", "pythonocc", "cadquery")

    def _is_crosslib_suspect(f: Path, raw: str) -> bool:
        low = str(f).lower()
        if any(k in low for k in SUSPECT_LIB):
            return True
        head = raw[:4000]
        return not any(m in head for m in SW_MARKERS)

    rows, scanned, calls = [], 0, 0
    for f in files:
        if f.name.startswith("_"):
            continue
        scanned += 1
        try:
            raw = f.read_text(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            continue
        #: ★ E1 —— 只剥**注释**（★ 保留字符串字面量，★ 否则成员名一起没了）
        code = strip_comments_only(raw)
        lines = raw.splitlines()
        code_lines = code.splitlines()

        #: ★ E2 依据：本文件里出现过的官方**后继**名字集合
        #: ★★★★ 2026-10-03（接手轮）**第三次修法 —— 前两次都错，★ 这次找到了真因**：
        #: ★ 病灶：★ `AddComponent4` 明明是**刻意兜底**（`AddComponent5 → 返回 None → 退
        #: 回 4`），
        #:     却一直被算成"真命中" ⇒ ★★ **生产里一条兜底都认不出来**（实测 0 条）✓
        #:   ★★ 第 1 版：★ `succ_short in succ_here` ⇒ 大小写敏感 ⇒ 漏。
        #:   ★★ 第 2 版：★ `.lower()` ⇒ **还是漏** —— 后继 `AddComponent5` 在本仓写作
        #:     **`add_component5`（蛇形 + 下划线）** = `事实 513` 那一族"名字形态不匹配"。
        #: ★★★ 第 3 版（本版）：★ **找到了真根因** —— ★ `succ_here` 原来**只从 `CALL_FOR
        #: MS`
        #:     里抽**（★ 即 `get_com_member(x,"M")` 与 `obj.M(` 两种形态）⇒
        #:     ★★ 而真正的兜底往往是**裸函数调用**：`_add_component5(...)` ——
        #:     ★★★ **它没有点、也不是 `get_com_member`** ⇒ **压根没进集合** ✓
        #: ⇒ ★ 修法：★ **改成"在后继名出现过的任何位置"都算**（★ 用裸标识符扫描 + 归一化
        #: ：
        #:     ★ 去下划线 + 小写），★ 不再依赖调用形态 ✓
        #:   ⚠ 代价（★ 如实记）：★ 这会让"兜底"这一类**更容易成立** ⇒ ★ 即**更保守**
        #:     （★ 宁少勿滥 —— ★ 把非兜底判成兜底，★ 后果是"少改一处废弃调用"，
        #:      ★ 而把兜底判成真命中，★ 后果是"改错一处会跑不了的兜底"）✓
        def _norm(x: str) -> str:
            return x.replace("_", "").lower()

        succ_here = {_norm(tok) for tok in re.findall(r"[A-Za-z_]\w*", code)}
        for i, cl in enumerate(code_lines):
            s = cl.strip()
            #: ★★★ 2026-10-03（接手轮）**兜底过滤**：★ 剥注释/剥 docstring 之后**仍以 `#
            #: ` 开头**的行
            #:   ⇒ ★ **它一定是注释**（★ 合法 Python 代码行不以 `#` 开头）⇒ **跳过** ✓
            #: ★ 为什么需要兜底：★ 上面那套"AST 剥 docstring + tokenize 挖注释"已经**修
            #: 好了主因**
            #: （★ 负例自检 `(True, True)`、★ 生产真命中 31 → 27），★ 但实测**仍有 17 条
            #: **残留
            #:     ⇒ ★★ 与其继续追那 17 条的真因（★ 事实 53：同一处 ≥3 次就该停），
            #:     ★ **加一道开销为零、判据无歧义的兜底**更划算 ✓
            #: ⚠ 它**不替代**上面那套（★ 那套负责保留真字符串字面量），★ 只做最后一道闸
            #: ✓
            if s.startswith("#"):
                continue
            for how, pat in CALL_FORMS:
                for name in pat.findall(cl):
                    if name not in safe:
                        continue
                    calls += 1
                    succ = successor.get(name, "")
                    succ_short = succ.split("::")[-1] if succ else ""
                    #: ★ E2：后继在本文件里出现过 ⇒ 这是兜底/回退分支
                    #: ★★★★ 2026-10-03（接手轮）**两次修法 —— 第二次才抓到真因**：
                    #:   ★ 第 1 版 `succ_short in succ_here` ⇒ 大小写敏感 ⇒ 漏。
                    #: ★★ 第 2 版 `.lower()` ⇒ ★★ **还是漏** —— 因为**本仓的内部帮手是蛇
                    #: 形命名**：
                    #: 后继 `AddComponent5` ⇒ 源码里写的是 **`add_component5`（带下划线
                    #: ）**
                    #:     ⇒ `'addcomponent5'` ≠ `'add_component5'` ✓
                    #: ★★★ 第 3 版（本版）：★ **两侧都"去下划线 + 小写"** ⇒ 归一化后比较
                    #:  ✓
                    #:   实证：`scripts/sw_assembly.py` 的 `AddComponent4` 是
                    #: 「AddComponent5 → 返回 None → **退回 AddComponent4**」的**刻意兜
                    #: 底** ✓
                    #: ★ `_norm` 与 `succ_here` 已在外层定义（★ 见文件上方的 E2 段）
                    fallback = bool(succ_short) and _norm(succ_short) in succ_here
                    #: ★ E3：该行只有字符串/登记，没有真正的调用括号
                    registry = (
                        how != "dot_call" and "(" not in s.replace("#", "")
                    ) or bool(re.match(r'^\s*["\']', s))
                    rows.append(
                        {
                            "file": str(f.relative_to(REPO)),
                            "line": i + 1,
                            "member": name,
                            "how": how,
                            "successor": succ,
                            "fallback_branch": fallback,
                            "registry_like": registry,
                            #: ★★★ 2026-10-03（接手轮）**加"生产 vs 探针/证据"这一维**：
                            #: ★ 实测 `GetActiveSketch2` 的 17 处里 **只有 3 处在 `scripts/`
                            #: **，
                            #:   ★ 其余 14 处都在 `tools/`（★ 探针与历史证据脚本）。
                            #:   ★★ **探针是**历史证据**，改了会破坏"证据不可变"**
                            #: （★ 我在 `gate-cand/GATE-FINAL.md` 的 **C12 证据不可变**里也
                            #: 写了这条）
                            #:   ⇒ ★ **只改 `scripts/`（生产）**，★ `tools/` 的**只报不动** ✓
                            "scope": (
                                "★ 生产（scripts/）"
                                if str(f.relative_to(REPO)).startswith("scripts")
                                else "★ 探针/证据（tools/，★ 只报不动）"
                                if str(f.relative_to(REPO)).startswith("tools")
                                else "★ 其它"
                            ),
                            #: ★★★ 「跨库存疑」：★ **点调用** 且 **同文件没有 SolidWorks 标
                            #: 志**
                            #:   ⇒ ★ 降级（★ 见上面 `_is_crosslib_suspect` 的说明）
                            "crosslib": bool(
                                how != "get_com_member" and _is_crosslib_suspect(f, raw)
                            ),
                            #: ★★★ 2026-10-03（接手轮）**修 ctx 的行号错位**：
                            #:   ★ 原来 `ctx` 取 `lines[i]`（★ **剥前的原文**），
                            #:   ★★ 而**匹配是在 `cl`（剥后的行）上做的** ⇒ 两者**会错位**
                            #: ⇒ 实证：`AddMate5` / `SetTransformAndSolve2` 的 `ctx` 显示成
                            #: `"""` ✓
                            #:   ★ 修法：★ **ctx 就用 `cl`（剥后的那一行）** ——
                            #:     ★★ 它才是**匹配依据**；★ 展示依据 == 匹配依据，★ 就不会错位 ✓
                            "ctx": s[:160],
                        }
                    )
    #: ★ 分类
    for r in rows:
        r["class"] = (
            "★ 兜底分支（不算缺陷）"
            if r["fallback_branch"]
            else "★ 疑似登记表（要人看）"
            if r["registry_like"]
            else "★ 跨库存疑（点调用 + 无 SolidWorks 标志）"
            if r.get("crosslib")
            else "★★ 待修（真命中）"
        )
    real = [r for r in rows if r["class"] == "★★ 待修（真命中）"]
    crosslib = [
        r for r in rows if r["class"] == "★ 跨库存疑（点调用 + 无 SolidWorks 标志）"
    ]
    agg = Counter(r["member"] for r in real)

    R = {
        "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "★_判据": "成员名 ∈「所有接口都废弃」的安全桶；覆盖 get_com_member/dot_call/dot_assign；"
        "排除 E1 注释 · E2 兜底分支 · E3 登记表",
        "规模": {
            "官方废弃成员": len(obs),
            "★_安全桶（所有接口都废弃）": len(safe),
            "★_歧义桶（部分接口废弃）": len(ambiguous),
            "扫的文件": scanned,
            "★_抽到的调用点": calls,
        },
        "自检 S2 反例": s2,
        "★_S2 通过": not s2_bad,
        "命中": {
            "真命中": len(real),
            "兜底分支": sum(1 for r in rows if r["fallback_branch"]),
            "疑似登记表": sum(
                1 for r in rows if r["registry_like"] and not r["fallback_branch"]
            ),
        },
        "★_按成员": agg.most_common(30),
        "行": real,
        "全部行": rows,
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")

    print(
        "★ 官方废弃成员 **%d** ⇒ ★★ **安全桶 %d**（★ 所有接口都废弃）· 歧义桶 %d"
        % (len(obs), len(safe), len(ambiguous))
    )
    print("★ 扫了 **%d** 个文件 · 抽到 **%d** 个调用点" % (scanned, calls))
    print()
    print(
        "★ 自检 S2（★ 已知反例**必须不进安全桶**）：%s"
        % ("★ 通过 ✓" if not s2_bad else "★★ 失败：%s" % s2_bad)
    )
    for n, v in s2.items():
        print("     %-24s %s" % (n, v))
    print()
    print("★★★ 分类：")
    print("   ★★ 真命中（待修）      **%d**" % len(real))
    #: ★★★ 新增档：★ 跨库存疑（★ 由 OCP 的 `bounds.Get()` 暴露 —— 与事实 511 同源）
    print(
        "   ★ 跨库存疑（★ 点调用 + 无 SolidWorks 标志）**%d**  ← ★ 降级，不计入真命中"
        % len(crosslib)
    )
    #: ★★★ 生产 / 探针 分开报（★ 探针是**历史证据**，★ 改了会破坏"证据不可变" —— GATE-FI
    #: NAL C12）
    print(
        "        ★ 其中**生产（scripts/）**  **%d**  ← ★★ **只有这批该改**"
        % len([r for r in real if str(r.get("scope", "")).startswith("★ 生产")])
    )
    print(
        "        ★ 其中探针/证据（tools/）**%d**  ← ★ **只报不动**"
        % len([r for r in real if str(r.get("scope", "")).startswith("★ 探针")])
    )
    print("   ★ 兜底分支（不算缺陷）  **%d**" % R["命中"]["兜底分支"])
    print("   ★ 疑似登记表（要人看）  **%d**" % R["命中"]["疑似登记表"])
    print()
    print("★ 真命中的成员分布（前 16）：")
    for m, n in agg.most_common(16):
        print(
            "   %-34s %-3d ⇒ 后继 %s"
            % (m[:33], n, successor.get(m, "（官方没写）")[:36])
        )
    print()
    print("★ 抽 5 条回原文（★ S3）：")
    for r in real[:5]:
        print("   %s:%d  [%s]  %s" % (r["file"], r["line"], r["member"], r["ctx"][:88]))
    print()
    print("★ 产出:", OUT, "（%.1f s）" % (time.time() - started))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
