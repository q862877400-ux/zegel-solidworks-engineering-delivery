"""★ 把 `mech-design` 的 **22 个标准件数据表**接成可查服务。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/standard_parts.py
# 定位:   规格 `specs/333-standard-parts-tables` ——
#           ★★ 把 `~/.agents/skills/mech-design/标准件数据表/` 的 **22 个 CSV**
#             接成**可查服务**。
#           ★★★ 触发它的是 2026-10-14 全自动挖掘：`mech-design`（★ 业主早装好的）
#             里有 **O 型圈 349 规格 · 底孔 99 · 通孔 90 · 螺钉长度 29 种 ·
#             5 类轴承 102 型号** —— ★ 而本仓 `manufacturing_rules.yaml` **只有 5 个规格**。
# 官方依据: ① `~/.agents/skills/mech-design/标准件数据表/*.csv`（★ 只读）
#           ② 该 skill 自述「**直接查表，不要凭记忆写标准数值**」
# 许可:   本仓库 MIT。★ 外部数据表**只读**；★ 引用时标注来源路径。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（★ 纯查表，不碰 COM）。
# -----------------------------------------------------------------------------
from __future__ import annotations

import csv
import pathlib

#: ★★ **数据表目录**（★ 外部 skill · 只读）
#:   ⚠ 实测（2026-10-14）：表**不在** `mech-design/标准件数据表/`，
#:     ★ 而在 **`mech-design/知识库/标准件数据表/`** ✗ ——
#:     ★ 我第一版按索引里的写法猜了路径 ⇒ ★ 报 `no-tables`。
#:   ⇒ ★ 判据：**列候选路径**（★ 找到第一个存在的就是它）。
_SKILL = pathlib.Path.home() / ".agents" / "skills" / "mech-design"
TABLE_DIR_CANDIDATES = (
    _SKILL / "知识库" / "标准件数据表",
    _SKILL / "标准件数据表",
    _SKILL / "知识库" / "bearings",
)


def _tables_dir() -> pathlib.Path | None:
    """★ 找到**真的存在**的那个表目录（★ 不猜、不硬编码单一路径）。"""
    for d in TABLE_DIR_CANDIDATES:
        if d.is_dir() and any(d.glob("*.csv")):
            return d
    return None


TABLES_DIR = _tables_dir() or TABLE_DIR_CANDIDATES[0]

#: ★★ **22 个表**（★ 名称 → 语义）
TABLES: dict[str, str] = {
    "o-ring_parameters": "★ O 型圈规格（**349** 条）",
    "tap_hole_sizes": "★ 攻丝底孔（**99** 条）",
    "clearance_hole_sizes": "★ 通孔（**90** 条）",
    "nominal_screw_lengths": "★ 公称螺钉长度（**29** 种）",
    "single_row_deep_groove_ball_bearing_parameters": "★ 深沟球轴承",
    "single_row_cylindrical_roller_bearing_parameters": "★ 圆柱滚子轴承",
    "single_row_tapered_roller_bearing_parameters": "★ 圆锥滚子轴承",
    "single_row_angular_contact_ball_bearing_parameters": "★ 角接触球轴承",
    "single_row_capped_deep_groove_ball_bearing_parameters": "★ 带盖深沟球轴承",
    "hex_head_parameters": "★ 六角头螺钉",
    "socket_head_cap_parameters": "★ 内六角圆柱头螺钉",
    "countersunk_head_parameters": "★ 沉头螺钉",
    "button_head_parameters": "★ 圆头螺钉",
    "cheese_head_parameters": "★ 开槽圆柱头螺钉",
    "chamfered_washer_parameters": "★ 倒角垫圈",
    "heatset_nut_parameters": "★ 热熔螺母",
    "din471": "★ DIN 471 轴用挡圈",
    "din472": "★ DIN 472 孔用挡圈",
}


class TableError(Exception):
    """★ 数据表失败（★ 带封闭码）。"""

    CODES = ("no-tables", "unknown-table", "empty", "bad-row")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


def available() -> dict:
    """★ **有哪些表**（★ 名称 → 说明 + 行数）。"""
    if not TABLES_DIR.is_dir():
        raise TableError("no-tables", "★ 没有 %s" % TABLES_DIR)
    out = {}
    for f in sorted(TABLES_DIR.glob("*.csv")):
        name = f.stem
        try:
            with f.open(encoding="utf-8", errors="replace") as fh:
                n = max(0, sum(1 for _ in fh) - 1)   #: ★ 减表头
        except OSError:
            n = -1
        out[name] = {"rows": n,
                     "desc": TABLES.get(name, "★ 未登记语义"),
                     "source": str(f)}
    return out


def rows(table: str) -> list:
    """★ 读一张表的**全部行**（★ 返回 `list[dict]`）。"""
    p = TABLES_DIR / ("%s.csv" % table)
    if not p.is_file():
        raise TableError("unknown-table",
                         "★ 没有 `%s`（有：%s）" % (table, sorted(
                             f.stem for f in TABLES_DIR.glob("*.csv"))))
    with p.open(encoding="utf-8", errors="replace", newline="") as fh:
        rdr = csv.DictReader(fh)
        data = [dict(r) for r in rdr]
    if not data:
        raise TableError("empty", "★ `%s` 是空的" % table)
    return data


def find(table: str, **criteria) -> list:
    """★★ **按条件查表**（★ 逐字承 skill：「**直接查表，不要凭记忆写标准数值**」）。

    ★★ 判据：★ 条件是 `列名=值` 的**子串匹配**（★ 容错列名空格/大小写）。
    """
    data = rows(table)
    if not criteria:
        return data
    out = []
    for r in data:
        ok = True
        for k, v in criteria.items():
            #: ★ 容错：列名去空格、大小写不敏感
            hit = None
            for col in r:
                if col and col.strip().lower() == k.strip().lower():
                    hit = r[col]
                    break
            if hit is None or str(v).lower() not in str(hit).lower():
                ok = False
                break
        if ok:
            out.append(r)
    return out


def tap_drill(size: str, *, hard: bool = False) -> dict:
    """★★ **攻丝底孔**（★ 从 **99 条**表里查，★ 不凭记忆）。

    ★★★ **关键：表有两列 `Soft` / `Hard`** —— ★ 这正是 `mech-design` 说的
      「**软/硬材料差 0.1~0.2mm**：**脆性材料或硬铁用【小底孔】**，避免丝锥崩刃」。

    ★★ 判据：`hard=True` 取 `Hard` 列、否则取 `Soft` 列。
      ⚠ ★ 而实测发现**「硬材料用小底孔」与列名相反** ——
        ★ `M1.5-0.35`：`Soft=1.15` · `Hard=1.25` ⇒ ★ **Hard 列的值更大** ✗
        ⇒ ★ **不替它解释**（★ 铁律 5）—— ★ 两列**都回**，★ 由调用方定。
    """
    hits = find("tap_hole_sizes", **{"size": size})
    if not hits:
        raise TableError("unknown-table", "★ 底孔表里没有 `%s`" % size)
    row = hits[0]
    return {"size": row.get("Size"), "soft_mm": row.get("Soft"),
            "hard_mm": row.get("Hard"),
            "picked": row.get("Hard" if hard else "Soft"),
            "★": "★ 表里两列**都回**；★ 哪列对应哪种材料**表里没写** ⇒ 不替它解释"}


def clearance_hole(size: str, *, fit: str = "normal") -> dict:
    """★★ **通孔**（★ 从 **90 条**表里查）。

    ★★★ **表有三档 `Close` / `Normal` / `Loose`** ——
      ★ 正是 `mech-design` 说的「**通孔三档**」。

    ★★ 判据：`fit ∈ {close, normal, loose}` ⇒ ★ 取对应列。
    """
    hits = find("clearance_hole_sizes", **{"size": size})
    if not hits:
        raise TableError("unknown-table", "★ 通孔表里没有 `%s`" % size)
    row = hits[0]
    key = {"close": "Close", "normal": "Normal",
           "loose": "Loose"}.get(fit.lower(), "Normal")
    return {"size": row.get("Size"), "close_mm": row.get("Close"),
            "normal_mm": row.get("Normal"), "loose_mm": row.get("Loose"),
            "picked": row.get(key), "fit": fit}


def oring(size: str) -> list:
    """★★ **O 型圈**（★ 从 **349 条**表里查）。"""
    hits = find("o-ring_parameters", **{"size": size})
    if not hits:
        raise TableError("unknown-table", "★ O 型圈表里没有 `%s`" % size)
    return hits


def report() -> dict:
    """★ **总览**（★ 证明「业主早就给了」）。"""
    try:
        av = available()
    except TableError as exc:
        return {"ok": False, "error": str(exc)}
    total = sum(v["rows"] for v in av.values() if v["rows"] > 0)
    return {
        "source": str(TABLES_DIR),
        "tables": len(av),
        "rows_total": total,
        "★": "★ 全部来自 `mech-design`（★ 业主早装好的）—— "
             "★ 而本仓 `manufacturing_rules.yaml` 只有 5 个规格",
        "detail": av,
    }
