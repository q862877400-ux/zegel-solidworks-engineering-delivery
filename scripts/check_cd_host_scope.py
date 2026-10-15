"""★ 门禁：`CreateDefinition` 站点的常量必须落在**官方宿主页**的域内，且映射必须与官方点名一致。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_cd_host_scope.py
# 定位:   `check_interface_member_ownership.py` 的 `CONST → 接口` 映射表**只**从
#         `C:\swapi\types\IFeatureManager\CreateDefinition.md` 造 ⇒ 它隐含一个**从未被写出**的
#         前提：「每个 `CreateDefinition` 调用的宿主都是 `IFeatureManager`」。
#         ★★ 而官方有**两个**宿主页（`IFeatureManager` / `IMotionStudy`），各自有**自己的**
#         `Type` 常量域。`sw_motion.py` 的站点宿主是 `IMotionStudy`，却被拿去查 `IFeatureManager`
#         的表 ⇒ 判成 `unmapped`。**「宿主没被表达」= 一个数里混了两种东西**（spec 237 同族）。
# 官方依据: ① `C:\swapi\types\IFeatureManager\CreateDefinition.md` 的 `## Parameters`
#              （35 条，括注是**散文标签**）
#           ② `C:\swapi\types\IMotionStudy\CreateDefinition.md` 的 `## Parameters`
#              （11 条，括注是 **`[[接口]]` 逐条点名**）
#           ★ 读取器**全部 import** `check_interface_member_ownership`，不重写。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
#
# ## 为什么需要它（**先量推翻待办**）
# 上一轮交接单的待办是「给 3 个未映射常量（`swFmDraft` / `swFmAEMRotationalMotor` /
# `swFmMateProfileCenter`）逐条读候选接口的 `## Description` 补 `MANUAL_MAP`」。
# ★★ 先量当场推翻它：**这 3 个常量一个都不属于 `IFeatureManager::CreateDefinition`**：
#   · `swFmAEMRotationalMotor` —— 官方宿主是 **`IMotionStudy::CreateDefinition`**，
#     且官方**逐条点名**返回 `ISimulationMotorFeatureData`（最强证据）；
#   · `swFmDraft` —— 官方 `Type` 清单里**没有**；本仓另有**真机证据**：`CreateDefinition(3)`
#     返回 `None`（`sw_sheet_metal.create_draft` 的来源块已记）；
#   · `swFmMateProfileCenter` —— **只有枚举页**收录，没有任何官方文档把它绑到 `CreateDefinition`。
# ⇒ ★ 照字面「补 `MANUAL_MAP`」会**污染一张本来正确的表**（把「别的宿主的常量」或
#   「官方不支持的常量」写成「本宿主返回的接口」）—— 与「照错前提改会把正确的登记改错」同族。
#
# ## 判据（四条，全部以**官方页**为事实源）
# | 违规 | 条件 |
# |---|---|
# | `should-map` | 站点 `unmapped` 的常量**出现在任一官方宿主页** ⇒ 必须补映射，**不许**用 `unmapped` 逃避 |
# | `host-mismatch` | 站点 `checked` 的常量被官方**点名**接口 ⇒ 映射值必须 **==** 点名值（人工表/文本匹配不得覆盖官方断言） |
# | `ambiguous-host` | 同一常量在多个宿主页被点名成**不同**接口 ⇒ 不猜，红 |
# | `unsupported-path` | ★ spec 239 新增：站点 `unmapped` 的常量**没有任何**官方宿主页收录 ⇒ 代码走了**官方不支持**的路径 ⇒ 必须表态官方替代入口 |
#
# ## 为什么要有 `unsupported-path`（**先量**才发现的盲区）
# 前三条**都只在「常量被官方收录」时才生效** ⇒ 「代码用了官方**根本不在** `CreateDefinition`
# 域里的常量」**三条全都不管**（读数上与「一切正常」同形）。★ 这正是 238 那条核心事实的
# **反面**：238 治「该映射却用 `unmapped` 逃避」，本码治「官方不支持却照旧调用」。
# 真树现状（先量）：`sw_sheet_metal.py` 的 `swFmDraft`（★ 本仓另有**真机证据**：
# `CreateDefinition(3)` 返回 `None`）与 `sw_weldment.py` 的 `swFmMateProfileCenter`。
#
# ## 契约（`unsupported-path` 专用，由人写死；门禁只「按你写的查」）
# 该站点上方**连续 `#:` 声明块**里必须有：
# ```
# #: create-entry: alt <官方成员名|unknown>  <理由>
# ```
# ★ `alt` 的三条**自证**（写错即红）：
#   ① `<官方成员名>` 必须在官方文档树里**有成员页**（`types/<接口>/<名>.md`）；
#   ② 该页**不得**带 `Obsolete` 标注 —— ★ 官方正是用 `Obsolete. Superseded by X`
#      表达「该换 X 了」⇒ 把代码换成**已废弃的前代入口** = 没解决问题（★ 本码的主要价值）；
#   ③ `unknown` 是**有界逃生门**（必须写理由）：表示「官方替代入口**尚未查明**」——
#      ★ 它是**表态**，不是「通过」；不许用它代替查证。
# ★ 读取方式是**向上连续扫描 `#:` 块**（不是只看第一行）：因为 237 的 `cd-site:` 声明
#   **必须紧贴调用行**（它只看第一行非空行）⇒ 两种声明需要**并存**，各读各的。
#
# ## 只增不减（下界冻结）
# `sites`（站点数）· `named`（常量被官方点名的站点数）· `no-host`（常量**无**官方宿主页的
# 站点数）都只允许**增**：减少 = 取点或读取器漏了。
# ★★ `no-host` 的下界是**本码不空转**的守卫：真树 1（`swFmMateProfileCenter`）——
#    `swFmDraft` 那个站点由 spec 239 改走官方入口 `IFeatureManager::InsertMultiFaceDraft` 后
#    **正当消失** ⇒ 237/238 的 `sites` 下界随之 10 → 9（**已记录在案**）；
#    ★★ spec 240：`swFmMateProfileCenter` 那个站点也改走官方入口
#    （`IAssemblyDoc::CreateMateData` + `CreateMate`）⇒ `sites` 9 → **8**、`no-host` 1 → **0**
#    （★ 三个「官方不支持」的靶子**全部处置完毕**）。
#    ★★★ **`no-host` 降到 0 ≠ 本码失效**：`unsupported-path` 的触发条件是
#    「**站点存在** + 常量无宿主页 + 未表态」⇒ 有人写回 `CreateDefinition(swFmMateProfileCenter)`
#    时它照样红；而「有人重新写回 `CreateDefinition(swFmDraft)`」这件事同样由**本码**接住
#    （它会红），不靠计数棘轮 ⇒ 这是「降低棘轮时必须补一条内容断言」的落地
#    （★ spec 240 补的内容断言在 `tests/test_mate_official_entry.py`）。
#
# ## 假绿守卫
# ★ `站点 == 0` 或 `named == 0` ⇒ FAIL（事实 46）。
#
# ## 便携性
# 官方文档树不在 ⇒ `[SKIP]` + `exit 0`（缺数据源 ≠ 检查失败）。
# 源开关：`DSH_CD_HOST_ROOT` · `DSH_CD_HOST_TYPES` · `DSH_CD_HOST_DUMPS` ·
# `DSH_CD_HOST_BASELINE_MIN`（`sites,named,no-host`）。
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

#: ★ 扫描根可被覆盖 ⇒ 负例能在**合成树**上端到端跑。
ROOT = Path(os.environ.get("DSH_CD_HOST_ROOT") or Path(__file__).resolve().parents[1])
#: 官方文档树 / 反射转储（未设 ⇒ 用被复用工具自己的默认路径）。
TYPES_ENV = os.environ.get("DSH_CD_HOST_TYPES", "")
DUMPS_ENV = os.environ.get("DSH_CD_HOST_DUMPS", "")
#: 明细打印上限。
DETAIL_LIMIT = 25
#: ★ `unsupported-path` 的声明形态（封闭词表：只有 `alt`）。
CREATE_ENTRY = re.compile(r"^#:\s*create-entry:\s*(?P<head>[a-z-]+)(?:\s+(?P<rest>\S.*?))?\s*$")
CREATE_ENTRY_CODES = ("alt",)
#: `#:` 声明行的形状（向上连续扫描声明块用）。
DECL_LINE = re.compile(r"^#:")
#: ★ 下界（真树实测 · 2026-10-09 · spec 238 / 239）—— 只增不减。
#: ⚠ **刻意写成独立常量而不是一张整数表**：整数表会进
#: `check_enum_values_vs_reflection` 的盲区清单、要额外表态（spec 237 当场踩过）。
BASELINE_SITES = 8             # `CreateDefinition` 站点总数（★ spec 239：10 → 9 ——
#:                              `sw_sheet_metal.create_draft` 改走官方入口后该站点**正当消失**；
#:                              ★ spec 240：9 → **8** —— `sw_weldment.create_profile_center_mate`
#:                              改走官方入口 `IAssemblyDoc::CreateMateData` + `CreateMate` 后，
#:                              它唯一的 `CreateDefinition` 站点**正当消失**）
BASELINE_NAMED = 1             # 常量被官方**逐条点名**接口的站点数
BASELINE_NO_HOST = 0           # ★ 常量**无**任何官方宿主页收录的站点数（本码的靶子数）
#:                             ★ spec 239：真树 1（`swFmMateProfileCenter`）；spec 240 改走官方入口后
#:                              真树 **0** —— ★★ 注意：**下界降到 0 ≠ 本码空转**：
#:                              ① `unsupported-path` 的**触发条件是「站点存在 + 无宿主 + 未表态」**，
#:                                 只要有人写回 `CreateDefinition(swFmMateProfileCenter)` 它就**会红**
#:                                 （与计数棘轮无关）；② 该码的 `alt` 三自证由 `judge_unsupported()`
#:                                 纯函数 + `tests/test_cd_host_scope.py` 的合成树/单测接住；
#:                              ③ 计数棘轮的替代品 = `tests/test_mate_official_entry.py` 的
#:                                 **内容断言**（按名字定位 `create_profile_center_mate`）。


def _baseline() -> dict:
    """⇒ 下界字典；`DSH_CD_HOST_BASELINE_MIN` 可整体覆盖（仅测试用）。"""
    spec = os.environ.get("DSH_CD_HOST_BASELINE_MIN", "")
    if spec.strip():
        parts = [int(x) for x in spec.split(",")]
        if len(parts) == 3:
            return dict(zip(("sites", "named", "no-host"), parts))
    return {"sites": BASELINE_SITES, "named": BASELINE_NAMED,
            "no-host": BASELINE_NO_HOST}


def _cimo():
    """★ 复用被检查工具的读取器；只用本门禁自己的环境变量覆盖它的路径。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_interface_member_ownership as cimo  # noqa: PLC0415

    if TYPES_ENV:
        cimo.TYPES = Path(TYPES_ENV)
        cimo.CD_DOC = cimo.TYPES / "IFeatureManager" / "CreateDefinition.md"
        cimo.CD_DOCS = {h: cimo.TYPES / h / "CreateDefinition.md" for h in cimo.CD_HOSTS}
    if DUMPS_ENV:
        cimo.RAW = Path(DUMPS_ENV)
    return cimo


def declaration_block(lines: list, lineno: int) -> list:
    """⇒ 调用行上方**连续** `#:` 声明块（自下而上收集）。

    ★ 确定性：向上跳过空行，遇到第一个**不以 `#:` 开头**的行即停
    （与 227/228/234/235/236/237 同一方式，**不用行窗口启发式**）。
    ★ 与 237 的 `declaration_above()` **并存**：那个只看**第一行**，本函数看**整块** ——
      因为 237 的 `cd-site:` 必须紧贴调用行，本码的 `create-entry:` 只能排在它上面。
    """
    out: list = []
    i = lineno - 2
    while i >= 0:
        t = lines[i].strip()
        if not t:
            i -= 1
            continue
        if not DECL_LINE.match(t):
            break
        out.append(t)
        i -= 1
    return out


def judge_unsupported(block: list, const: str, member_exists, member_obsolete):
    """⇒ 违规说明或 `None`。**`unsupported-path` 的全部判罪集中在这一处**（spec 235 纪律）。

    `member_exists(name)` / `member_obsolete(name)` 由调用方注入（真树 = 官方文档树；
    单测 = 直接喂 lambda）⇒ 本函数是**纯函数**，两个自证分支**都可被直接喂靶子**。
    """
    decl = None
    for t in block:
        m = CREATE_ENTRY.match(t)
        if m:
            decl = m
            break
    if decl is None:
        return ("常量 `%s` **没有任何官方 `CreateDefinition` 宿主页收录** ⇒ 代码走了"
                "**官方不支持**的路径 ⇒ 请在调用行上方声明 `#: create-entry: alt "
                "<官方成员名|unknown> <理由>`" % const)
    head = decl.group("head")
    if head not in CREATE_ENTRY_CODES:
        return "未知 code `%s`（封闭词表：%s）" % (head, " / ".join(CREATE_ENTRY_CODES))
    toks = (decl.group("rest") or "").split()
    if not toks:
        return "`alt` 缺替代入口与理由"
    entry, reason = toks[0], " ".join(toks[1:]).strip()
    if not reason:
        return "`alt` 缺理由（只写了替代入口）"
    if entry == "unknown":
        return None                       # ★ 有界逃生门：已**表态**「官方替代入口尚未查明」
    if not member_exists(entry):
        return ("`alt %s` —— 官方文档树里**查不到**该成员页 ⇒ 自证失败"
                "（不许写一个官方没有的入口）" % entry)
    if member_obsolete(entry):
        return ("`alt %s` —— 该成员页带 **`Obsolete`** 标注 ⇒ 自证失败："
                "★ 官方用 `Obsolete. Superseded by X` 表达「该换 X 了」⇒ "
                "换回已废弃的前代入口 = 没解决问题" % entry)
    return None


def make_unsupported_judge(blocks: dict, types_dir: Path):
    """⇒ `(site) -> 违规说明|None`。把「读声明块 + 查官方页」绑定进去，判罪仍在 `judge_unsupported`。"""
    def _exists(name: str) -> bool:
        return bool(list(types_dir.glob("*/%s.md" % name))) if types_dir.is_dir() else False

    def _obsolete(name: str) -> bool:
        for p in sorted(types_dir.glob("*/%s.md" % name)):
            try:
                if "Obsolete" in p.read_text(encoding="utf-8", errors="replace"):
                    return True
            except OSError:
                continue
        return False

    def _judge(site: dict):
        key = (site["path"].name, site["line"])
        return judge_unsupported(blocks.get(key, []), site.get("const") or "",
                                 _exists, _obsolete)

    return _judge


def judge_sites(sites: list, pages: dict, owned: dict, mapped: dict, members_of,
                unsupported=None) -> tuple:
    """⇒ ``(violations, gaps, named_sites, no_host)``。**所有判罪集中在这一处**（spec 235 的纪律）。

    ★ 抽成纯函数是为了让 `host-mismatch` / `ambiguous-host` 这两个码**有靶子**：
    正常跑时映射表**先**由官方点名播种 ⇒ 它们不会自然触发；只有把输入直接喂进来才可测
    （**没有靶子的守卫不写** —— spec 232/236 的教训）。
    ★ `unsupported`（spec 239）是**注入的** `(site) -> 说明|None`：本函数保持纯的，
      官方页查询与声明块读取都在调用方（真树 = 官方文档树；单测 = lambda）。
    """
    violations: list = []
    gaps: list = []
    named_sites = 0
    no_host = 0
    for s in sites:
        const = s.get("const") or ""
        if not const:
            continue
        hosts = owned.get(const, [])
        if s["code"] == "unmapped":
            if const in pages:
                #: ★ 官方**点名**了返回接口 ⇒ 必须映射；但**接口文档缺失**属**缺数据源**
                #:   （事实 46 同族：缺数据源 ≠ 检查失败）⇒ 只登记，不拦发布。
                vals = sorted(set(pages[const].values()))
                if len(vals) == 1 and members_of(vals[0]):
                    violations.append({"kind": "should-map", "file": s["path"].name,
                                       "line": s["line"],
                                       "detail": "常量 `%s` 被官方宿主页 `%s` **逐条点名**为 `%s` "
                                                 "⇒ 必须映射，**不许**用 `unmapped` 逃避"
                                                 % (const, " / ".join(sorted(pages[const])),
                                                    vals[0])})
                else:
                    gaps.append("`%s`（%s:%d）官方点名 `%s` 但**接口文档缺失** ⇒ 缺数据源"
                                % (const, s["path"].name, s["line"], " / ".join(vals)))
            elif hosts:
                violations.append({"kind": "should-map", "file": s["path"].name,
                                   "line": s["line"],
                                   "detail": "常量 `%s` **在官方宿主页 `%s` 的 `Type` 清单里** ⇒ "
                                             "必须补进映射表，**不许**用 `unmapped` 逃避"
                                             % (const, " / ".join(hosts))})
            else:
                #: ★ spec 239：常量**没有任何**官方宿主页收录 ⇒ 代码走了官方不支持的路径。
                no_host += 1
                bad = unsupported(s) if unsupported else None
                if bad:
                    violations.append({"kind": "unsupported-path", "file": s["path"].name,
                                       "line": s["line"], "detail": bad})
            continue
        if const in pages:
            named_sites += 1
            vals = sorted(set(pages[const].values()))
            if len(vals) > 1:
                violations.append({"kind": "ambiguous-host", "file": s["path"].name,
                                   "line": s["line"],
                                   "detail": "常量 `%s` 在多个宿主页被点名成**不同**接口：%s ⇒ 不猜"
                                             % (const, " / ".join("%s=%s" % kv for kv in
                                                                  sorted(pages[const].items())))})
                continue
            got = mapped.get(const)
            if got != vals[0]:
                violations.append({"kind": "host-mismatch", "file": s["path"].name,
                                   "line": s["line"],
                                   "detail": "常量 `%s` 官方点名 `%s`，而映射表给的是 `%s` ⇒ "
                                             "**官方断言不得被人工表/文本匹配覆盖**"
                                             % (const, vals[0], got or "（无）")})
    return violations, gaps, named_sites, no_host


def main() -> int:
    cimo = _cimo()
    if not cimo.TYPES.is_dir():
        print("[SKIP] 官方文档树不在（`%s`）—— **缺数据源不算违规**" % cimo.TYPES)
        print("站点 0 · [SKIP] · exit 0")
        return 0

    pages = cimo.host_pages()          # {常量: {宿主: 官方点名的接口}}
    owned = cimo.host_consts()         # {常量: [收录它的宿主页]}
    paths = sorted((ROOT / "scripts").glob("*.py"))
    sites = cimo.scan_sites(paths)
    mapped, _amb, _unm = cimo.build_map()
    minb = _baseline()

    #: ★ spec 239：`unsupported-path` 的声明块（按 `(文件名, 调用行)` 取）。
    blocks: dict = {}
    for s in sites:
        key = (s["path"].name, s["line"])
        if key in blocks:
            continue
        try:
            blocks[key] = declaration_block(
                s["path"].read_text(encoding="utf-8").splitlines(), s["line"])
        except OSError:
            blocks[key] = []
    unsupported = make_unsupported_judge(blocks, cimo.TYPES)

    violations, gaps, named_sites, no_host = judge_sites(
        sites, pages, owned, mapped, cimo.members_of, unsupported)

    #: ★ 只增不减（下界冻结）。
    facts = {"sites": len(sites), "named": named_sites, "no-host": no_host}
    for key in ("sites", "named", "no-host"):
        if facts[key] < minb.get(key, 0):
            violations.append({"kind": "baseline-shrunk", "file": "-", "line": 0,
                               "detail": "%s %d < 下界 %d（只增不减：先查取点/读取器）"
                                         % (key, facts[key], minb.get(key, 0))})
    #: ★ 假绿守卫（事实 46）。
    if not sites:
        violations.append({"kind": "zero-checked", "file": "-", "line": 0,
                           "detail": "`CreateDefinition` 站点 == 0"})
    elif named_sites == 0:
        violations.append({"kind": "zero-checked", "file": "-", "line": 0,
                           "detail": "被官方**逐条点名**接口的站点 == 0 ⇒ 官方点名这条判据空转"})

    print("== `CreateDefinition` 站点的**宿主域** ==")
    print("官方宿主页 %d 个：%s" % (len(cimo.CD_DOCS),
                                   " / ".join(sorted(cimo.CD_DOCS))))
    print("扫描 `%s/scripts/*.py` · 站点 %d · 常量被官方点名 %d · 收录常量 %d · 无宿主常量站点 %d"
          % (ROOT.as_posix(), len(sites), named_sites, len(owned), no_host))
    for g in gaps[:DETAIL_LIMIT]:
        print("  [SKIP] %s" % g)

    if violations:
        print("[FAIL] 违规 %d 处：" % len(violations))
        for v in violations[:DETAIL_LIMIT]:
            print("  [%s] %s:%s —— %s" % (v["kind"], v["file"], v["line"], v["detail"]))
        if len(violations) > DETAIL_LIMIT:
            print("  …另有 %d 处" % (len(violations) - DETAIL_LIMIT))
    ok = not violations
    print("[PASS]" if ok else "[FAIL]")
    print("站点 %d · 点名 %d · 无宿主 %d · 违规 %d · [%s] · exit %d"
          % (len(sites), named_sites, no_host, len(violations),
             "PASS" if ok else "FAIL", 0 if ok else 1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
