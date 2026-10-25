"""★ S2 首件需求冻结：把「必须由人确认的五项」变成机器可判的缺项。

## 判据（`docs/ENGINEERING-PATH.md` 第六节 S2）

1. 与工程负责人冻结首件功能、接口、主参数及可修改域、材料、工艺、必要图样和交付目的。
2. 从这些要求倒推最小规范/规则集合，不先批量搬整个标准库。
3. 完成结构化需求到方法计划的单一映射，**去掉关键参数的静默默认值**。
4. 换材料/工艺/规则版本、移除引用或未确认参数，均**不得继续旧批准**。

## ★★ 为什么以 `engineering_contract.LEGACY_ALWAYS_MISSING` 为基准

那五项 `('material', 'load_case', 'safety_level', 'process', 'datums')`
是本仓早已认定的「**旧版永远缺**」字段 —— 也就是当年那些「悄悄填默认值」的地方。

S2 不新造一套字段，直接在既有的 `EngineeringContract` 上判：
**这五项任一为空 ⇒ 不得冻结**。

## ★ 缺项必须提问，不得填默认值

`EngineeringContract.clarifications` 是提问的唯一落点。
本模块的 `missing()` 只报「缺什么」，**不提供任何默认值** ——
给默认值就是替工程负责人拍板。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/acceptance/s2_requirements.py
# 定位:   docs/ENGINEERING-PATH.md 第六节 S2 的落地 —— 首件需求冻结。
#          ★ 以既有的 engineering_contract.LEGACY_ALWAYS_MISSING 为基准，
#            不新造字段：那五项 material/load_case/safety_level/process/datums
#            是本仓早已认定的「旧版永远缺」项。
#          ★ 缺项只**报出**、**不给默认值** —— 给默认值就是替工程负责人拍板。
# 官方依据: 不适用（纯 Python 层，不调 SolidWorks API）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import engineering_contract as ec  # noqa: E402

#: ★ 首件必须由人确认的五项（复用既有定义，不新造）
REQUIRED_CONFIRMATIONS = ec.LEGACY_ALWAYS_MISSING

#: ★ 首件额外要求的可判项（S2 补，见 `docs/ENGINEERING-PATH.md` 第五节）
ADDITIONAL_REQUIRED = (
    "interface",       #: 接口（孔型/孔位/配合面）
    "drawing_scope",   #: 必要图样范围
    "delivery_purpose",  #: 交付目的
)


def missing_confirmations(contract: object) -> list:
    """★ 报出**未确认**的必填项 —— 只报缺什么，**不给默认值**。

    判据：字段值「为空或未设置」即算缺。具体形态：
      · `material`      —— `None` 或 `MaterialRef` 的牌号为空
      · `load_case`     —— `load_cases` 列表为空
      · `safety_level`  —— 空串或 `None`
      · `process`       —— `None` 或 `ProcessIntent.kind` 为空
      · `datums`        —— `datums` 列表为空
    """
    out: list = []

    material = getattr(contract, "material", None)
    if material is None or not str(getattr(material, "name", "") or "").strip():
        out.append("material")

    if not list(getattr(contract, "load_cases", ()) or ()):
        out.append("load_case")

    if not str(getattr(contract, "safety_level", "") or "").strip():
        out.append("safety_level")

    process = getattr(contract, "process", None)
    if process is None or not str(getattr(process, "kind", "") or "").strip():
        out.append("process")

    if not list(getattr(contract, "datums", ()) or ()):
        out.append("datums")

    #: ★ 附加项：从 `clarifications` 里查是否已确认
    confirmed = {
        str(c.get("field", "")) for c in (getattr(contract, "clarifications", ()) or ())
        if c.get("confirmed")
    }
    for name in ADDITIONAL_REQUIRED:
        if name not in confirmed:
            out.append(name)

    return out


#: ★ 标准号形态（与 E7 的 locator 判据同一族：只判「像不像依据」，不判真伪）
#: ★ 允许编号前有一个字母（`ASTM A36`），但机构前缀必须≥2 个字母（所以 `Q235` 不算）
_STANDARD_NO = re.compile(r"\b[A-Z]{2,}(?:/[A-Z]{1,2})?\s*[A-Z]?\d")
#: ★ 数值 + 量纲（如 `500 N` · `12.5 kN` · `2 MPa` · `0.03 mm`）
_MAGNITUDE = re.compile(r"\d+(?:\.\d+)?\s*[A-Za-z%\u00b0/]+")


def shape_problems(contract: object) -> list[dict]:
    """★ 报出**形状不合格**的必填项 —— 只报「能不能作为依据」，**不判值对不对**。

    返回 `[{"field": ..., "problem": ..., "hint": ...}, ...]`，空列表表示形状都合格。

    ## 判据（每条都只要求「可核对」，不要求「正确」）

    | 字段 | 要求 |
    |---|---|
    | `material` | `name` 非空 **且** ≥1 个标准号形态（`GB/T 700-2006` / `ASTM A36` …） |
    | `load_case` | 每个 `LoadCase` 都有**数值 + 量纲**（`500 N` / `2 MPa`） |
    | `datums` | 每个基准都有**非空语义角色** |
    | `process` | `kind` 非空（首件路线限定为机加工，但本函数不替人填） |
    | `safety_level` | 非空（取值口径由工程负责人定，本函数**不预设枚举**） |

    ⚠ **不含**的判据：材料是否合适、载荷是否合理、安全等级取几级 ——
      那些是工程判断，本函数一律不做。
    """
    out: list[dict] = []

    material = getattr(contract, "material", None)
    if material is not None:
        name = str(getattr(material, "name", "") or "").strip()
        std = str(getattr(material, "standard", "") or "").strip()
        if name and not _STANDARD_NO.search(name) and not _STANDARD_NO.search(std):
            out.append(
                {
                    "field": "material",
                    "problem": "材料没有标准号形态 ⇒ 无法核对",
                    "hint": "牌号要能追到标准（如 `Q235B / GB/T 700-2006`），"
                    "只写「钢」「45 钢」不可判",
                }
            )

    for lc in list(getattr(contract, "load_cases", ()) or ()):
        mag = getattr(lc, "magnitude", None)
        text = str(mag or "").strip()
        #: ★ **空也要报** —— 「有载荷项但没填数值」就是不可判，
        #:   不能因为它为空就当作「还没填」丢给缺项检查
        #:   （缺项检查只看列表是否为空，看不到单个项里的值）。
        if not text or not _MAGNITUDE.search(text):
            out.append(
                {
                    "field": "load_case",
                    "problem": "载荷 %r 没有「数值 + 量纲」形态" % (getattr(lc, "name", ""),),
                    "hint": "写成 `500 N` / `2 MPa` / `0.03 mm`，量纲要明写",
                }
            )

    for dt in list(getattr(contract, "datums", ()) or ()):
        #: ★ 字段名是 semantic_role（engineering_contract.Datum 实测），不是 role
        role = str(getattr(dt, "semantic_role", "") or "").strip()
        if not role:
            out.append(
                {
                    "field": "datums",
                    "problem": "基准没有语义角色",
                    "hint": "写清它是主基准/导向/测量基准，后续图样与装配都要绑它",
                }
            )

    return out


def can_freeze(contract: object) -> tuple:
    """⇒ `(能否冻结, 缺项清单)`。

    ★ 有任一缺项 ⇒ **不得冻结**（不是「警告后继续」）。
    """
    miss = missing_confirmations(contract)
    return (not miss, miss)


def freeze(contract: object) -> object:
    """★ 冻结契约；缺项时抛错并**指名缺什么**。

    ⚠ 不提供任何自动填充 —— 缺项是工程负责人要回答的问题，
      不是程序可以替他决定的事。
    """
    ok, miss = can_freeze(contract)
    if not ok:
        raise ValueError(
            "★ 首件需求不能冻结：还缺 %d 项未确认 —— %s。"
            "★ 这些必须由工程负责人确认，不得填默认值。"
            % (len(miss), ", ".join(miss))
        )
    contract.freeze()
    return contract


def require_sheet(contract: object) -> dict:
    """★ 生成「要求 → 承担者 → 验收者」三列对照表。

    ★ `docs/ENGINEERING-PATH.md` S2 完成标准：
      「首件每条硬要求有执行承担者和验收者」—— 缺一即不成立。
    """
    rows: list = []

    def add(req_id: str, what: str, owner: str, checker: str) -> None:
        rows.append(
            {
                "requirement_id": req_id,
                "what": what,
                "executor": owner,
                "acceptor": checker,
                "complete": bool(owner) and bool(checker),
            }
        )

    add("R-01", "板外形与厚度（主参数）", "method:plate", "accept:e2_rebuild")
    add("R-02", "孔数 / 孔型 / 孔位", "method:hole_group", "accept:e5_drawing")
    add("R-03", "材料牌号", "requirement:material", "check:e6_process")
    add("R-04", "工艺路线", "requirement:process", "check:e6_process")
    add("R-05", "定位基准与配合", "method:assembly", "accept:e4_assembly")
    add("R-06", "必要图样标注", "method:drawing", "accept:e5_drawing")
    add("R-07", "关键判据的溯源", "rule:rule_service", "accept:e7_provenance")

    incomplete = [r for r in rows if not r["complete"]]
    return {
        "rows": rows,
        "total": len(rows),
        "incomplete": [r["requirement_id"] for r in incomplete],
        "ok": not incomplete,
    }
