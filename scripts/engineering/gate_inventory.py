"""★ Q16 · 把门禁分类表扩到四类 + 补环境/责任人（规格 324 的 P1/P2）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/gate_inventory.py
# 定位:   规格 `specs/324-gate-inventory-and-meta-coverage` 的 P1（四类枚举）/
#           P2（类别+理由+环境+责任人）/ P4（真机单独编排 · NOT_RUN）/
#           P6（retired 带 replaced_by）。
#           ★★ 实测（2026-10-12）起点：`docs/gate-classification.json` 有 **50 条**，
#           而 `kind` 只有 `{'hard': 47, 'diagnostic': 3}`、字段只有
#           `['gate','kind','reason','runner']` ⇒ ★ **缺三类**、★ **缺环境与责任人**。
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q16（L329-347）逐字：
#           「类别只能是：`release_static / release_hardware / diagnostic /
#             retired`。每个文件必须有**类别、理由、环境与责任人**。」
#           + 「真机门禁**单独编排并明确 `NOT_RUN`**，不能跳过仍报全部通过」
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收入口 `tools/run_s324_gates.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLASSIFICATION = ROOT / "docs" / "gate-classification.json"
INVENTORY = ROOT / "metadata" / "gate-inventory.json"
#: ★★ **豁免名单**（★ Q16：诊断工具**保留但明确不是门禁**）
#:   ★ 判据：**被豁免 ≠ 漏登记** —— 豁免是**有理由的已知状态**
#:     （★ 元门禁 `check_gate_wiring.py` 要求每条豁免带 `reason` + 非空 `evidence`）。
EXEMPTIONS = ROOT / "docs" / "gate-wiring-exemptions.json"

#: ★★ **Q16 逐字给的四个类别**（★ 封闭枚举）
RELEASE_STATIC = "release_static"
RELEASE_HARDWARE = "release_hardware"
DIAGNOSTIC = "diagnostic"
RETIRED = "retired"
KINDS = (RELEASE_STATIC, RELEASE_HARDWARE, DIAGNOSTIC, RETIRED)

#: ★★ **旧名 → 新名**（★ FR-003：`hard` **映射到** `release_static`，★ 不丢语义）
#:   ★ 依据：`hard` 门禁全是**静态**检查（语法/单位/接线/约定），★ 不需要真机。
LEGACY_KIND_MAP = {"hard": RELEASE_STATIC, "diagnostic": DIAGNOSTIC}

#: ★★ **真机门禁的识别**（★ FR-004）。
#: ⚠ 实测（2026-10-12）：第一版只做**子串命中** ⇒ ★ **17 条假阳性** ✗ ——
#:   因为很多静态门禁的**理由里会"提到"真机**（如「★ 这条**不需要真机**」
#:   「与真机实测互为印证」）⇒ ★ 一提真机就被判成真机门禁。
#: ⇒ ★★ 判据改成**三条都要**（★ 缺一不算真机）：
#:   ```
#:   ① 名字像真机（`hardware`/`real_machine`/`sw_guard`/`live`）
#:      或 理由里出现**必须真机**的正向措辞
#:   ② ★ **且**不是"不需要真机"这种**否定句**
#:   ③ ★ **且** `runs_in` 确实不是 `release_check`
#:   ```
#: ★ 为什么③必须：「接进 release 的静态门禁」与「要真机才能跑」**是两件事** ——
#:   ★ Q16 要的正是**把真机门禁从 release 里拿出去单独编排**。
HARDWARE_NAME_PAT = re.compile(
    r"hardware|real_machine|realmachine|sw_guard|\blive\b|真机", re.I)
#: ★ 正向措辞（★ 「必须/需要/要在真机上跑」）
HARDWARE_POSITIVE = ("必须真机", "需要真机", "要在真机", "真机才能", "真机运行",
                     "requires solidworks", "requires sw")
#: ★★ **否定措辞**（★ 提到真机但**不是**真机门禁）
HARDWARE_NEGATIVE = ("不需要真机", "无需真机", "不用真机", "不跑真机",
                     "与真机实测互为印证", "真机实测互为印证", "静态")
HARDWARE_HINTS = ("真机", "COM", "SolidWorks", "sw_guard", "外部求解器",
                  "calculix", "elmer", "需要 SW")


class GateInventoryError(Exception):
    """★ 门禁清单失败（★ 带封闭码）。"""

    CODES = ("bad-kind", "missing-field", "bad-legacy", "no-replaced-by",
             "not-run-mismatch", "missing-file")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法门禁清单拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


@dataclass
class GateEntry:
    """★ 一条门禁登记（★ Q16：**类别 / 理由 / 环境 / 责任人** 四者都要）。"""

    gate: str = ""
    runner: str = ""
    kind: str = ""
    reason: str = ""
    environment: str = ""
    owner: str = ""
    replaced_by: str = ""
    not_run: bool = False
    runs_in: str = "release_check"

    def missing(self) -> list:
        """★ 缺哪几项（★ P2 的判据）。"""
        out = []
        if not self.kind:
            out.append("kind")
        if not str(self.reason).strip():
            out.append("reason")
        if not str(self.environment).strip():
            out.append("environment")
        if not str(self.owner).strip():
            out.append("owner")
        return out

    def validate(self) -> None:
        if self.kind and self.kind not in KINDS:
            raise GateInventoryError(
                "bad-kind", "★ %s 的 kind=%r 不在四类里" % (self.gate, self.kind))
        miss = self.missing()
        if miss:
            raise GateInventoryError(
                "missing-field", "★ %s 缺 %s" % (self.gate, miss))
        #: ★ P6：`retired` **必须**带替代关系（★ Q16 逐字「不删除，先标明替代关系」）
        if self.kind == RETIRED and not self.replaced_by:
            raise GateInventoryError(
                "no-replaced-by", "★ %s 是 retired 却没有 `replaced_by`" % self.gate)

    def to_dict(self) -> dict:
        d = {"gate": self.gate, "runner": self.runner, "kind": self.kind,
             "reason": self.reason, "environment": self.environment,
             "owner": self.owner, "runs_in": self.runs_in}
        if self.replaced_by:
            d["replaced_by"] = self.replaced_by
        if self.not_run:
            d["not_run"] = True
        return d


#: ★★ **责任人**（★ Q16 要「责任人」—— ★ 本仓的责任人是**执行代理**与**业主**）
OWNER_AGENT = "executing-agent"
OWNER_OWNER = "owner"

#: ★★ **环境**（★ Q16 要「环境」）
ENV_STATIC = "offline-static"           #: ★ 纯静态（不需要 SW）
ENV_SW = "solidworks-required"          #: ★ 要真机
ENV_SOLVER = "external-solver-required"  #: ★ 要外部求解器


def classify_hardware(entry: dict) -> bool:
    """★★ **判一条门禁要不要真机**（★ P4 —— ★ FR-004）。

    ★★ 判据（★ 三条都要，★ 见 `HARDWARE_NAME_PAT` 的说明）：
      ```
      ① 名字像真机 或 理由里有**正向**真机措辞
      ② **且**理由里**没有否定措辞**（「不需要真机」）
      ③ **且** `runs_in` 不是 `release_check`（★ 接进 release 的就是静态的）
      ```
    """
    name = str(entry.get("gate", ""))
    reason = str(entry.get("reason", ""))
    runs_in = str(entry.get("runs_in") or "release_check")
    low = reason.lower()

    #: ② 否定句 ⇒ 不是真机门禁
    if any(neg.lower() in low for neg in HARDWARE_NEGATIVE):
        return False
    #: ③ 接进 release 的 ⇒ 静态（★ Q16 的"单独编排"才叫真机门禁）
    if runs_in == "release_check" and not entry.get("force_hardware"):
        return False
    #: ① 名字像真机 或 正向措辞
    if HARDWARE_NAME_PAT.search(name):
        return True
    return any(p in low for p in HARDWARE_POSITIVE)


def migrate_entry(entry: dict) -> GateEntry:
    """★★ **把一条旧登记升成新形状**（★ P1/P2 —— ★ 不丢语义）。

    ★★ 判据（★ 三条）：
      ```
      ① `kind`：旧名按 `LEGACY_KIND_MAP` 映射；★ 命中真机特征 ⇒ release_hardware
      ② `environment`：★ 按真机/求解器判定
      ③ `owner`：★ 默认执行代理（★ 静态门禁不需要业主）
      ```
    """
    old = str(entry.get("kind") or "")
    if old in LEGACY_KIND_MAP:
        kind = LEGACY_KIND_MAP[old]
    elif old in KINDS:
        kind = old
    else:
        raise GateInventoryError("bad-legacy", "★ 未知旧 kind=%r" % old)

    hw = classify_hardware(entry)
    if hw and kind == RELEASE_STATIC:
        #: ★★ FR-004：**要真机的不能标成静态**（★ 否则"跳过仍报全过"）
        kind = RELEASE_HARDWARE
    env = ENV_SW if hw else ENV_STATIC
    if re.search(r"calculix|elmer", "%s %s" % (entry.get("reason", ""),
                                               entry.get("gate", "")), re.I):
        env = ENV_SOLVER

    return GateEntry(
        gate=str(entry.get("gate") or ""),
        runner=str(entry.get("runner") or ""),
        kind=kind,
        reason=str(entry.get("reason") or ""),
        environment=str(entry.get("environment") or env),
        owner=str(entry.get("owner") or OWNER_AGENT),
        replaced_by=str(entry.get("replaced_by") or ""),
        not_run=bool(entry.get("not_run") or hw),
        runs_in=str(entry.get("runs_in") or
                    ("sw_guard" if hw else "release_check")))


def load_classification() -> dict:
    return json.loads(CLASSIFICATION.read_text(encoding="utf-8"))


def _load_exemptions() -> dict:
    """★ 读豁免名单（★ 只取**条目** —— ★ `_comment` 是说明不是条目）。

    ⚠ 实测（2026-10-12）：`docs/gate-wiring-exemptions.json` 的形状是
      `{"_comment": ..., "exemptions": [{gate, reason, evidence}, ...]}`
      —— ★ **列表嵌在 `exemptions` 键下**，★ 而第一版按**顶层字典**读
      ⇒ ★ 把 `exemptions` 这个**键名**当成了"一条豁免"（★ 它的"理由"是个 list）
      ⇒ `test_exemptions_are_accounted_for` 失败。
    ⇒ ★ 判据：**两种形状都要吃**（★ 顶层字典 或 `exemptions` 列表）。
    """
    if not EXEMPTIONS.is_file():
        return {}
    try:
        d = json.loads(EXEMPTIONS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    out: dict = {}
    #: ★ 形状 A：`{"exemptions": [{gate, ...}, ...]}`
    if isinstance(d.get("exemptions"), list):
        for item in d["exemptions"]:
            if isinstance(item, dict) and item.get("gate"):
                out[str(item["gate"])] = item
        return out
    #: ★ 形状 B：顶层就是 `{gate: {...}}`
    for k, v in d.items():
        if not k.startswith("_"):
            out[k] = v
    return out


def migrate_all() -> dict:
    """★ 升整张表（★ 返回新表 + 计数）。"""
    d = load_classification()
    rows = d.get("classification") or []
    out = []
    for r in rows:
        e = migrate_entry(r)
        e.validate()
        out.append(e.to_dict())
    return {"_comment": d.get("_comment", ""), "classification": out}


def kind_counts(entries: list) -> dict:
    """★★ **四类计数**（★ SC-009 —— ★ **0 条也要报**）。"""
    counts = {k: 0 for k in KINDS}
    for e in entries:
        counts[e.get("kind", "")] = counts.get(e.get("kind", ""), 0) + 1
    return counts


def validate_all(entries: list) -> dict:
    """★★ **整表校验**（★ P1/P2/P6 —— ★ 逐条 `validate()`）。"""
    bad = []
    for r in entries:
        e = GateEntry(**{k: v for k, v in r.items()
                         if k in GateEntry.__dataclass_fields__})
        try:
            e.validate()
        except GateInventoryError as exc:
            bad.append({"gate": e.gate, "code": exc.code, "detail": exc.detail})
    return {"ok": not bad, "n": len(entries), "bad": bad,
            "counts": kind_counts(entries)}


#: ══════════════════════════════════════════════════════════════════════
# 清点 tools/（★ P7/P9 —— ★ Q16 逐字「元门禁同时覆盖 scripts/、tools/」）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **哪些文件算「检查文件」**（★ P7/P9）。
#: ⚠ 实测（2026-10-12）：第一版用 `check|verify|validate|audit|run_*` 的**宽**模式
#:   ⇒ `scripts/` 扫出 **52** 个，而元门禁自己的口径（`glob("check_*.py")`）
#:   只有 **50** 个 ⇒ ★ **报出 7 个"应执行却没登记"** ✗
#:   —— ★ 而那 7 个里 `audit_*`/`validate_*` **从来就不是门禁**
#:     （★ 元门禁的口径是 `check_*.py`）。
#: ⇒ ★★ 判据：**沿用元门禁自己的口径**（`check_*.py`）——
#:   ★ 「应执行集合」必须与**既有判据同口径**，否则报的是**假缺口**。
#:   ★ 另加 `tools/` 侧的 `check_*` 与 `verify_*`（★ Q16 要覆盖 `tools/`）。
SCRIPTS_CHECK_PAT = re.compile(r"^check_.*\.py$", re.I)
TOOLS_CHECK_PAT = re.compile(r"^(check_|verify_|run_s\d)", re.I)


def scan_check_files(dirname: str) -> list:
    """★ 扫一个目录里的**检查文件**（★ P7 的判据）。

    ★★ 判据：**`scripts/` 用 `check_*.py`**（★ 与元门禁同口径）；
      ★ **`tools/` 用 `check_*`/`verify_*`/`run_s*`**（★ Q16 要覆盖 `tools/`）。
    """
    d = ROOT / dirname
    if not d.is_dir():
        return []
    pat = SCRIPTS_CHECK_PAT if dirname == "scripts" else TOOLS_CHECK_PAT
    return sorted(p.name for p in d.glob("*.py") if pat.search(p.name))


def build_inventory() -> dict:
    """★★ **门禁清点**（★ P7/P9 —— ★ `scripts/` + `tools/` **两边都扫**）。"""
    cls = load_classification()
    entries = cls.get("classification") or []
    scripts_checks = scan_check_files("scripts")
    tools_checks = scan_check_files("tools")
    declared = {e.get("gate", "") for e in entries}

    #: ★★ **应执行集合 vs 实际执行结果**（★ P8 —— ★ Q16 逐字
    #:   「不只检查文件被发现」）
    #: ⚠ 实测（2026-10-12）：第一版把「**被豁免**」也算成「应执行却没登记」 ✗
    #:   ⇒ ★ 而豁免是**有理由的已知状态**（★ 元门禁要求带 `reason` + `evidence`）
    #:     ⇒ ★ 判据：**应执行 = 有文件 且 未豁免**。
    exempt = {k for k in _load_exemptions()}
    should = set(scripts_checks) - exempt
    actually = {e.get("gate", "") for e in entries
                if e.get("runs_in") == "release_check"}
    not_run = sorted(e.get("gate", "") for e in entries
                     if e.get("kind") == RELEASE_HARDWARE)

    #: ⚠ 实测（2026-10-12）：第一版判「登记了却没文件」时**只在 `scripts/` 与
    #:   `tools/` 里找** ⇒ ★ 把 `tests/test_inout_array_audit_contract.py`
    #:   （★ 那是个**真实存在**的门禁——它验 `tools/audit_inout_array_params.py`
    #:   的产物）**误报成"名单腐坏"** ✗。
    #: ⇒ ★ 判据：**先按路径整体找，找不到再按目录名找**（★ 门禁可以在 `tests/`）。
    def _exists(name: str) -> bool:
        if not name:
            return False
        p = ROOT / name
        if p.is_file():
            return True
        return ((ROOT / "scripts" / name).is_file()
                or (ROOT / "tools" / name).is_file())

    return {
        "scripts": {"checks": scripts_checks, "n": len(scripts_checks)},
        "tools": {"checks": tools_checks, "n": len(tools_checks)},
        "declared": sorted(declared),
        "declared_n": len(declared),
        "counts": kind_counts(entries),
        #: ★★ **豁免**（★ 有理由的已知未接线 —— ★ 不算漏）
        "exempted": sorted(exempt),
        "exempted_n": len(exempt),
        #: ★★ **应执行 vs 实际**（★ 核心判据）
        "should_run_in_release": sorted(should),
        "actually_run_in_release": sorted(actually),
        "should_but_not_declared": sorted(should - declared),
        "declared_but_no_file": sorted(
            d for d in declared if not _exists(d)),
        #: ★★ **真机门禁单独编排**（★ P4 —— ★ 明确 `NOT_RUN`）
        "not_run": not_run,
        "not_run_n": len(not_run),
        "★": ("★ `scripts/` 与 `tools/` **两边都扫**；★ 且核对"
              "「应执行集合」与「实际执行结果」"),
    }


def write_inventory(path: pathlib.Path | None = None) -> pathlib.Path:
    p = path or INVENTORY
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(build_inventory(), ensure_ascii=False, indent=1),
                 encoding="utf-8")
    return p
