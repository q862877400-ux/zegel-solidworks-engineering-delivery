"""★ 门禁：`CreateDefinition` 站点的**逐站点处置**必须表态，且处置必须与事实相符。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_create_definition_site_disposition.py
# 定位:   `check_interface_member_ownership.py`（**诊断**）末尾只报
#         「检查过 5 个站点；跳过 5」—— **四种语义完全不同的处置被合成一个数**：
#         `dynamic`（可能只是读取器太窄）/ `unmapped`（该审却漏审）/
#         `empty-members`（数据源缺）/ `no-members-used`（确实无事可查）。
#         ⇒ 合成之后，**一次把 `checked` 退化成 `unmapped` 的回归完全不可见**
#         （读数仍是「跳过 5→6」）。本门禁把每个站点**摊开并要求表态**。
# 官方依据: ① `C:\\swapi\\types\\<接口>\\<成员>.md`（官方文档镜像 · 成员集）
#           ② `C:\\swapi\\types\\IFeatureManager\\CreateDefinition.md`（`CONST → 接口` 映射表）
#           ③ `_raw/**/enum_values_sldworks.txt`（模块常量 → `swFm*` 名反查）
#           ★ 读取器**全部 import** `check_interface_member_ownership`，不重写。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
#
# ## 为什么需要它
# 「一句话不是守卫」（spec 229/236）：诊断**报了**「跳过 5」，但**没人查这 5 个是什么**。
# ★★ 而本规格「先量」当场量出真缺陷：`module_consts()` 的正则要求常量行**以数字结尾**
#   ⇒ `SW_FM_MATE_PROFILE_CENTER = 101  # swFmMateProfileCenter` **读不到**
#   ⇒ `scripts/sw_weldment.py` 的常量表成 `{}` ⇒ 它唯一的站点被静默判成 `dynamic`
#   （真处置是 `unmapped`）。⇒ 「**窄读取器读出 0 也会骗人**」第七次。
#
# ## 契约（由人写死；门禁只负责「按你写的查」）
# 非 `checked` 站点，其 **`CreateDefinition(...)` 调用行的正上方第一行非空行**必须是：
# ```
# #: cd-site: unmapped <const>…       <理由>
# #: cd-site: empty-members           <理由>
# #: cd-site: no-members-used         <理由>
# #: cd-site: dynamic                 <理由>
# ```
# ★ 关联方式是**确定性**的（向上跳过空行取第一行非空行，与 227/228/234/235/236 同一方式），
#   **不用行窗口启发式**。
# ★ `checked` 是**隐式默认**、**不需要**声明；在 `checked` 站点上写声明 ⇒ 红 `redundant-decl`
#   （多余声明是噪声，且会掩盖真回归）。
#
# ## 每个 code 的自证条件（**写错即红**）
# | code | 自证 |
# |---|---|
# | `unmapped` | 列出的常量集合 **==** 该站点**实际**未映射常量集合（漏列 / 多列 ⇒ 红 `集合不符`） |
# | `empty-members` | 该站点**确实**没有任何未映射常量，且期望接口成员集为空 |
# | `no-members-used` | 该站点**确实** 0 个 `data.X` |
# | `dynamic` | ★★ **读取器太窄的守卫**：`arg_texts` 里**每一个**实参文本必须 ① 不含 `swFm\\w+` ② 不是纯数字 ③ 其标识符**都不在**同文件模块常量表 —— 任一不满足 ⇒ 红 `reader-too-narrow` |
#
# ## 只增不减（下界冻结）
# 站点数 / `checked` 数 / 各 code 计数都只允许**增**：减少 = 取点或读取器漏了
# （**不是**「问题解决了」）⇒ 判 FAIL，先查清再改常量。
#
# ## 假绿守卫
# ★ `站点 == 0` 或 `checked == 0` ⇒ FAIL（事实 46）。
#
# ## 便携性
# 官方文档树不在 ⇒ `[SKIP]` + `exit 0`（缺数据源 ≠ 检查失败）。
# 源开关：`DSH_CD_SITE_ROOT` · `DSH_CD_SITE_TYPES` · `DSH_CD_SITE_DUMPS` ·
# `DSH_CD_SITE_BASELINE_MIN`（`sites,checked,unmapped,empty-members,no-members-used,dynamic`）。
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

#: ★ 扫描根可被覆盖 ⇒ 负例能在**合成树**上端到端跑。
ROOT = Path(os.environ.get("DSH_CD_SITE_ROOT") or Path(__file__).resolve().parents[1])
#: 官方文档树 / 反射转储（未设 ⇒ 用被复用工具自己的默认路径）。
TYPES_ENV = os.environ.get("DSH_CD_SITE_TYPES", "")
DUMPS_ENV = os.environ.get("DSH_CD_SITE_DUMPS", "")
#: 声明（**`CreateDefinition` 调用行**上方第一行非空行）。
DECL = re.compile(r"^#:\s*cd-site:\s*(?P<head>[a-z-]+)(?:\s+(?P<rest>\S.*?))?\s*$")
#: ★ 封闭词表（`checked` 是隐式默认，不在此表 —— 写它就是多余声明）。
CODES = ("unmapped", "empty-members", "no-members-used", "dynamic")
#: 明细打印上限。
DETAIL_LIMIT = 25
#: ★ 下界（真树实测 · 2026-10-09 · spec 237）—— 只增不减。
#: ⚠ **刻意写成 6 个独立常量而不是一张整数表**：① 与姊妹门禁（235 `BASELINE_SITES` /
#:   `BASELINE_ENUM` / `BASELINE_VALUES`、236 `BASELINE_DECLS` …）同一形状；
#:   ② 整数表会进 `check_enum_values_vs_reflection` 的盲区清单、要额外表态 ——
#:   而这张表**不是**任何官方枚举的取值，本就不该走那条路（首跑 `release_check` 当场报了它）。
BASELINE_SITES = 8             # 站点总数（★ spec 239：10 → 9 —— `sw_sheet_metal.create_draft`
#:                              改走官方入口 `IFeatureManager::InsertMultiFaceDraft` 后，
#:                              它那个 `CreateDefinition(swFmDraft)` 站点**正当消失**；
#:                              ★ spec 240：9 → **8** —— `sw_weldment.create_profile_center_mate`
#:                              改走官方入口 `IAssemblyDoc::CreateMateData` + `CreateMate` 后，
#:                              它唯一的 `CreateDefinition` 站点（连同**无调用方**的共用骨架
#:                              `_create_from_definition`）**整体消失**。
#:                              ★★ **棘轮下调必须补内容断言**（spec 240）：由
#:                                `tests/test_mate_official_entry.py` 按**名字**定位该函数，
#:                                断言它不直接 / 不经共用骨架到达 `CreateDefinition`、
#:                                且逐字调 `call_assembly_doc(…, "CreateMateData"/"CreateMate")`
#:                                ⇒ 「有人写回 `CreateDefinition(swFmMateProfileCenter)`」
#:                                  会被**那条判据**接住，**不靠计数棘轮**）
BASELINE_CHECKED = 6           # `checked` 站点数（★ spec 238：5 → 6，`sw_motion.py` 那个站点
#:                              的常量被官方 `IMotionStudy::CreateDefinition` 页点名 ⇒ 进了映射表）
BASELINE_UNMAPPED = 0          # 常量未进 `CONST → 接口` 映射表（★ spec 238：3 → 2 ·
#:                              ★ spec 239：2 → 1（`swFmDraft` 改走官方入口）·
#:                              ★ spec 240：1 → **0**（`swFmMateProfileCenter` 改走官方入口）
#:                              —— ★ 三个「该审却漏审」的常量**全部处置完毕**，
#:                              **不是**取点/读取器漏了）
BASELINE_EMPTY_MEMBERS = 0     # 期望接口的成员集为空
BASELINE_NO_MEMBERS_USED = 2   # 建了 data 但不设成员
BASELINE_DYNAMIC = 0           # 常量静态解析不出


def _baseline() -> dict:
    """⇒ 下界字典；`DSH_CD_SITE_BASELINE_MIN` 可整体覆盖（仅测试用）。"""
    spec = os.environ.get("DSH_CD_SITE_BASELINE_MIN", "")
    if spec.strip():
        parts = [int(x) for x in spec.split(",")]
        if len(parts) == 6:
            return dict(zip(("sites", "checked", "unmapped", "empty-members",
                             "no-members-used", "dynamic"), parts))
    return {"sites": BASELINE_SITES, "checked": BASELINE_CHECKED,
            "unmapped": BASELINE_UNMAPPED, "empty-members": BASELINE_EMPTY_MEMBERS,
            "no-members-used": BASELINE_NO_MEMBERS_USED, "dynamic": BASELINE_DYNAMIC}


def _cimo():
    """★ 复用被检查工具的读取器；只用本门禁自己的环境变量覆盖它的路径。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_interface_member_ownership as cimo  # noqa: PLC0415

    if TYPES_ENV:
        cimo.TYPES = Path(TYPES_ENV)
        cimo.CD_DOC = cimo.TYPES / "IFeatureManager" / "CreateDefinition.md"
    if DUMPS_ENV:
        cimo.RAW = Path(DUMPS_ENV)
    return cimo


def declaration_above(lines: list, lineno: int):
    """⇒ `(head, rest)` 或 `None`（未表态）。★ 确定性：向上跳过空行取第一行非空行。"""
    i = lineno - 2
    while i >= 0 and not lines[i].strip():
        i -= 1
    if i < 0:
        return None
    m = DECL.match(lines[i].strip())
    if not m:
        return None
    return m.group("head"), (m.group("rest") or "").strip()


def _arg_is_dynamic(text: str, consts: dict) -> bool:
    """★ `dynamic` 的自证：实参文本**确实**解析不出常量（读取器太窄则返回 False）。"""
    t = (text or "").strip()
    if re.search(r"\bswFm\w+\b", t):
        return False                                   # ① 字面 `swFm*` 名
    if re.fullmatch(r"-?\d+", t):
        return False                                   # ② 纯数字
    for ident in re.findall(r"\b([A-Za-z_]\w*)\b", t):
        if ident in consts:
            return False                               # ③ 同文件模块常量（★ 旧正则读不到带注释的）
    return True


def judge(decl, group: list, consts: dict):
    """⇒ 违规说明，或 `None`。**所有判罪集中在这一处**（spec 235 的纪律）。"""
    head, rest = decl
    codes_present = sorted({s["code"] for s in group if s["code"] != "checked"})
    if head not in CODES:
        return "未知 code `%s`（封闭词表：%s；`checked` 是隐式默认，不需要声明）" % (
            head, " / ".join(CODES))
    if len(codes_present) > 1:
        return "同一站点混有多个非 checked 处置（%s）⇒ 请拆分或逐条声明" % " / ".join(codes_present)
    if not rest:
        return "`%s` 缺理由" % head
    toks = rest.split()
    named = [t for t in toks if re.fullmatch(r"swFm\w+", t)]
    reason = " ".join(t for t in toks if t not in named).strip()
    if not reason:
        return "`%s` 缺理由（只写了常量名）" % head
    if head == "unmapped":
        actual = {s["const"] for s in group if s["code"] == "unmapped"}
        if not actual:
            return ("`unmapped` 但该站点**没有**未映射常量（实际处置：%s）"
                    % " / ".join(codes_present))
        if set(named) != actual:
            return ("`unmapped` 列出的常量与**实际**未映射常量**集合不符**："
                    "声明 %s · 实际 %s（漏列/多列都算错）"
                    % (sorted(named) or "无", sorted(actual) or "无"))
        return None
    if head == "empty-members":
        actual = {s["const"] for s in group if s["code"] == "unmapped"}
        if actual:
            return "`empty-members` 但该站点有未映射常量 %s（该用 `unmapped`）" % sorted(actual)
        if any(s["code"] != "empty-members" for s in group if s["code"] != "checked"):
            return "`empty-members` 与实际处置不符（实际：%s）" % " / ".join(codes_present)
        return None
    if head == "no-members-used":
        if any(s["used"] for s in group):
            return ("`no-members-used` 但该站点**确实设了成员**（%s）⇒ 自证失败"
                    % ", ".join(str(s["used"]) + " 个" for s in group if s["used"]))
        if any(s["code"] != "no-members-used" for s in group if s["code"] != "checked"):
            return "`no-members-used` 与实际处置不符（实际：%s）" % " / ".join(codes_present)
        return None
    #: `dynamic` —— ★★ 读取器太窄的守卫。
    texts = sorted({t for s in group for t in s["arg_texts"] if t})
    bad = [t for t in texts if not _arg_is_dynamic(t, consts)]
    if bad or codes_present != ["dynamic"]:
        return ("[reader-too-narrow] `dynamic` 但该站点**其实可解析**"
                "（实际处置 %s；可解析实参 %s）⇒ "
                "**不许把「读取器读不出」写成「它就是动态的」**（先修读取器）"
                % (" / ".join(codes_present), ", ".join("`%s`" % t for t in bad[:4]) or "-"))
    return None


def main() -> int:
    cimo = _cimo()
    if not cimo.TYPES.is_dir():
        print("[SKIP] 官方文档树不在（`%s`）—— **缺数据源不算违规**" % cimo.TYPES)
        print("站点 0 · [SKIP] · exit 0")
        return 0

    paths = sorted((ROOT / "scripts").glob("*.py"))
    sites = cimo.scan_sites(paths)
    minb = _baseline()

    #: 按 (文件, `CreateDefinition` 调用行) 分组 —— 一行可产生多个计划。
    groups: dict = {}
    for s in sites:
        groups.setdefault((s["path"], s["line"]), []).append(s)

    lines_cache: dict = {}
    violations: list = []
    claimed: dict = {}
    for (path, line), group in sorted(groups.items(), key=lambda kv: (kv[0][0].as_posix(),
                                                                     kv[0][1])):
        if path not in lines_cache:
            try:
                lines_cache[path] = path.read_text(encoding="utf-8").splitlines()
            except OSError:
                lines_cache[path] = []
        lines = lines_cache[path]
        shown = path.name
        decl = declaration_above(lines, line)
        non_checked = [s for s in group if s["code"] != "checked"]
        if not non_checked:
            if decl is not None:
                violations.append({"kind": "redundant-decl", "file": shown, "line": line,
                                   "detail": "该站点是 `checked`（隐式默认）⇒ 不需要声明；"
                                             "多余声明会掩盖真回归"})
            continue
        if decl is None:
            violations.append({"kind": "undeclared", "file": shown, "line": line,
                               "detail": "处置 %s **未表态** ⇒ 请在调用行上方补 "
                                         "`#: cd-site: <code> <理由>`（const=%s）"
                                         % (" / ".join(sorted({s["code"] for s in non_checked})),
                                            ", ".join(str(s["const"]) for s in non_checked))})
            continue
        bad = judge(decl, group, cimo.module_consts(path))
        if bad:
            violations.append({"kind": "invalid-claim", "file": shown, "line": line,
                               "detail": bad})
        else:
            claimed[decl[0]] = claimed.get(decl[0], 0) + len(non_checked)

    codes: dict = {}
    for s in sites:
        codes[s["code"]] = codes.get(s["code"], 0) + 1
    checked = codes.get("checked", 0)

    print("== `CreateDefinition` 站点的**逐站点处置** ==")
    print("扫描 `%s/scripts/*.py` · 站点 %d · checked %d · %s"
          % (ROOT.as_posix(), len(sites), checked,
             " · ".join("%s %d" % (c, codes.get(c, 0)) for c in CODES)))
    print("表态：%s" % (" / ".join("%s %d" % (c, claimed.get(c, 0)) for c in CODES) or "无"))

    #: ★ 只增不减（下界冻结）。
    facts = dict(codes)
    facts["sites"] = len(sites)
    facts["checked"] = checked
    for key in ("sites", "checked") + CODES:
        if facts.get(key, 0) < minb.get(key, 0):
            violations.append({"kind": "baseline-shrunk", "file": "-", "line": 0,
                               "detail": "%s %d < 下界 %d（只增不减：先查取点/读取器）"
                                         % (key, facts.get(key, 0), minb.get(key, 0))})
    #: ★ 假绿守卫（事实 46）。
    if not sites:
        violations.append({"kind": "zero-checked", "file": "-", "line": 0,
                           "detail": "检查过的 `CreateDefinition` 站点 == 0"})
    elif checked == 0:
        violations.append({"kind": "zero-checked", "file": "-", "line": 0,
                           "detail": "`checked` 站点 == 0（全部被跳过 ⇒ 结论不可信）"})

    if violations:
        print("[FAIL] 违规 %d 处：" % len(violations))
        for v in violations[:DETAIL_LIMIT]:
            print("  [%s] %s:%s —— %s" % (v["kind"], v["file"], v["line"], v["detail"]))
        if len(violations) > DETAIL_LIMIT:
            print("  …另有 %d 处" % (len(violations) - DETAIL_LIMIT))
    ok = not violations
    print("[PASS]" if ok else "[FAIL]")
    print("站点 %d · checked %d · %s · 违规 %d · [%s] · exit %d"
          % (len(sites), checked,
             " · ".join("%s %d" % (c, codes.get(c, 0)) for c in CODES),
             len(violations), "PASS" if ok else "FAIL", 0 if ok else 1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
