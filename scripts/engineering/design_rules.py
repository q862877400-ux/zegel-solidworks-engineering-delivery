"""★ `mech-design` 的**设计规则库**（3 个 YAML）接成可查服务。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/design_rules.py
# 定位:   规格 `specs/335-design-rules-lib` ——★★ 把 `~/.agents/skills/mech-design/知识
#           库/` 的 **3 个 YAML**  接成**可查服务**：  · `design_rules.yaml`（**225 行**
#            通用设计规则）  · `material_db.yaml`（**材料库** —— 含 **SolidWorks 牌号映
#           射**）  · `fits_iso286.yaml`（**孔/轴极限偏差** + 计算公式）★★★ 触发它的是 2
#           026-10-14 全自动挖掘。
# 官方依据: ① `~/.agents/skills/mech-design/知识库/*.yaml`（★ 只读）② `design_rules.yaml
#           ` 自述：「**先查此库推导缺失参数，再执行建模**   （原则：**先确认参数，不猜*
#           *）」—— ★ 与本仓「该问就问」同源
# 许可:   本仓库 MIT。★ 外部数据**只读**；★ 引用标注来源路径。
#           ⚠ `design_rules.yaml` 自述来源含 `SHY-563/solidworks-draw`
#             ⇒ ★ 本模块**只读它已汇总的规则**，★ 不引入第三方代码。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 纯查表（★ 不碰 COM）。
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib

#: ★★ **三个 YAML**（★ 外部 skill · 只读）
KB = pathlib.Path.home() / ".agents" / "skills" / "mech-design" / "知识库"
FILES = {
    "rules": "design_rules.yaml",
    "materials": "material_db.yaml",
    "fits": "fits_iso286.yaml",
}


try:
    from ._coded_error import CodedError
except ImportError:
    from _coded_error import CodedError


class RuleError(CodedError):
    """★ 规则库失败（★ 带封闭码）。"""

    CODES = ("no-lib", "unknown-key", "unknown-material", "unknown-fit")


def _load(which: str) -> dict:
    """★ 读**其中一个** YAML（★ 单一源 —— ★ 不复制内容）。

    ⚠⚠⚠ 实测（2026-10-14）：**两个外部 YAML 各有多处语法错** ✗ ——
      我**连着修了 4 类**，★ 第 4 类时**按本仓事实 53 停手**
      （★ 「同一个启发式连续修补 ≥3 次还没稳定，就该停下回退」）。

      | 类 | 形态 | 例 |
      |---|---|---|
      | ① | 块下**裸标量**（缺 `-`） | `design_rules.yaml` L222 `sealing:` |
      | ② | `key:{` 的 `:` 后**缺空格** | `fits_iso286.yaml` L41 |
      | ③ | `key:"v"` 的 `:` 后**缺空格** | `fits_iso286.yaml` L90 |
      | ④ | ★ **两个键挤在一行** | `fits_iso286.yaml` L52 `shaft_limits: "0_3": {…}` |

    ★★★ **判据（★ 本仓事实 53 的直接应用）**：
      ★ **①②③ 修**（★ 已实证有效）；★ **④ 不修** ——
      ★ 而是**如实报「这个文件读不全」**，★ 并**只回能读的部分**。
      ★★ 理由：★ 继续加正则就是「**同一个启发式连续修补**」⇒
        ★ 而且**我改的是别人的资产**，★ **越修越可能改错意思**。

    ★★ 返回值：★ 读得到 ⇒ 用（★ 带 `_yaml_repair` 标注）；
      ★ 读不全 ⇒ ★ **如实带 `_yaml_unreadable`**（★ 不假装读到）。
    """
    p = KB / FILES[which]
    if not p.is_file():
        raise RuleError("no-lib", "★ 没有 %s" % p)
    import yaml                                                         # noqa: PLC0415
    text = p.read_text(encoding="utf-8")
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        fixed = _repair_bare_scalars(text)
        try:
            d = yaml.safe_load(fixed) or {}
        except yaml.YAMLError as exc2:
            #: ★★★ **第 4 类：不修** —— ★ 如实报（★ 事实 53）
            return {"_yaml_unreadable": (
                "⚠⚠ **该文件有多处 YAML 语法错，本模块修不全** —— "
                "★ 已修 ①②③（裸标量 / `:{` 缺空格 / `:\"` 缺空格），"
                "★ 仍剩**第 4 类**（两个键挤在一行）⇒ "
                "★ **按事实 53 停手**（★ 不再加正则）\n"
                "  首错：%s\n  修复后仍错：%s"
                % (str(exc)[:160], str(exc2)[:160])),
                "_yaml_source": str(p)}
        if isinstance(d, dict):
            d["_yaml_repair"] = (
                "⚠ **原文件有 YAML 语法错**（★ ①②③ 类之一）⇒ "
                "★ 本模块**只读时修**、★ **未改原文件**（★ 那是用户的资产）")
        return d


def _repair_bare_scalars(text: str) -> str:
    """★ 修两类**YAML 语法错**（★ **只在内存里** —— ★ 不改原文件）。

    ⚠⚠ 实测（2026-10-14）：这两个外部 YAML **各有各的语法错**：
      ```
      design_rules.yaml  L222  sealing:
                               "金属垫片…"        ← ★ 少了 `-`
      fits_iso286.yaml   L41   "100_120":{H6: …}   ← ★ `:` 后**少了空格**
      ```
      ⇒ ★ `yaml.safe_load` 抛 `ParserError`（★ 两者都是
        「expected <block end>, but found '<scalar>'」）。
      ★★ 而**两种错的报错文本一样** ⇒ ★ 得**分别试**。

    ★★ 判据：★ **不静默改用户文件** —— ★ 只在**读的时候**补，
      ★ 并在返回值里**如实标注**（★ `_yaml_repair` 字段）。
    """
    #: ★ 修 ①：块下**裸标量** ⇒ 补 `-`
    out = []
    for line in text.splitlines():
        s = line.strip()
        if (s.startswith('"') and s.endswith('"')
                and ':' not in s[:-1].replace('：', '')):
            indent = len(line) - len(line.lstrip())
            out.append(" " * indent + "- " + s)
        else:
            out.append(line)
    text = "\n".join(out) + "\n"
    #: ★ 修 ②：`key:{` / `key:[` 的 `:` 后**缺空格** ⇒ 补一个
    import re                                                           # noqa: PLC0415
    text = re.sub(r'^(\s*"[^"]+")\s*:\s*(\{|\[)', r'\1: \2', text,
                  flags=re.M)
    #: ★ 修 ③：`key:"value"` 的 `:` 后**缺空格**（★ 第三类 —— 实测
    #:   `fits_iso286.yaml` L90 的 `H11/c11:"间隙 非常松…"`）
    #:   ⚠ 这一类的报错文本**又不一样**（「could not find expected ':'」）⇒
    #:   ★ 判据：**三类一起修**（★ 幂等、互不干扰）。
    return re.sub(r'^(\s*[A-Za-z0-9_./\-]+)\s*:\s*(")', r'\1: \2', text,
                  flags=re.M)


def _get(d: dict, path: str):
    """★ 按**点分路径**取值（★ 如 `general.bolt.min_spacing`）。"""
    cur = d
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            raise RuleError("unknown-key", "★ 没有 `%s`（★ 在 `%s` 处断了）"
                            % (path, k))
        cur = cur[k]
    return cur


#: ══════════════════════════════════════════════════════════════════════
# 一、设计规则（★ `design_rules.yaml`）
#: ══════════════════════════════════════════════════════════════════════

def rule(path: str):
    """★★ **按路径查规则**（★ 如 `general.bolt.min_spacing`）。

    ★★★ 判据（★ 逐字承该 YAML 的头）：
      「**先查此库推导缺失参数，再执行建模**（原则：**先确认参数，不猜**）」

    ⚠ 实测（2026-10-14）：`design_rules.yaml` **读不全**（★ 见 `_load` 的四类语法错）
      ⇒ ★ 本函数会**如实报**「读不全」，★ **不假装查到**。
    """
    d = _load("rules")
    if "_yaml_unreadable" in d:
        raise RuleError("no-lib",
                        "★ `design_rules.yaml` **读不全**（★ 见 `_load`）"
                        "⇒ ★ **不假装查到**（★ 本仓事实 53：不继续加正则硬修）")
    return _get(d, path)


def rules_tree() -> dict:
    """★ 规则的**顶层分组**（★ 供浏览）。"""
    d = _load("rules")
    if "_yaml_unreadable" in d:
        return {"_yaml_unreadable": d["_yaml_unreadable"][:200]}
    return {k: (sorted(v) if isinstance(v, dict) else v) for k, v in d.items()}


#: ══════════════════════════════════════════════════════════════════════
# 二、材料库（★ `material_db.yaml` —— ★ 含 SolidWorks 牌号映射）
#: ══════════════════════════════════════════════════════════════════════

def _materials_table() -> dict:
    """★ 找到**真的材料表**（★ 结构实测：`steels` / `aluminum` … 是**分组**）。

    ⚠ 实测（2026-10-14）：`material_db.yaml` 的结构是
      ```
      steels:
        "45钢": {name: …, sw_material: …, yield_strength: …}
        "40Cr": {…}
      aluminum: {…}
      ```
      ⇒ ★ **两层**（★ 分组 → 材料），★ 不是我第一版猜的一层 ✗。
    ⇒ ★ 判据：★ **拍平成「材料名 → 属性」**（★ 名字唯一）。
    """
    d = _load("materials")
    flat: dict = {}
    for group, v in d.items():
        if group.startswith("_"):
            continue
        if not isinstance(v, dict):
            continue
        for k, m in v.items():
            #: ★ 只收**看起来像材料**的项（★ 有 `name` 或 `sw_material` 或密度）
            if isinstance(m, dict) and (
                    "name" in m or "sw_material" in m or "density" in m):
                flat[k] = m
    return flat


def materials() -> list:
    """★ **有哪些材料**（★ 如 `45钢` / `40Cr` / `20钢` …）。"""
    return sorted(_materials_table())


def material(name: str) -> dict:
    """★★ **材料属性**（★ 含 **SolidWorks 近似牌号** `sw_material`）。

    ★★ 判据：★ 这是「**设计要选材、建模要填牌号**」的桥 ——
      ★ 中文名（`45钢`）↔ ★ SolidWorks 牌号（`AISI 1020`）。
    """
    tbl = _materials_table()
    if name not in tbl:
        raise RuleError("unknown-material",
                        "★ 材料库里没有 `%s`（有：%s）" % (name, sorted(tbl)))
    return dict(tbl[name])


def sw_material_of(name: str) -> str:
    """★ 中文材料名 → **SolidWorks 近似牌号**（★ 建模时填这个）。"""
    m = material(name)
    return str(m.get("sw_material") or "")


#: ══════════════════════════════════════════════════════════════════════
# 三、公差配合（★ `fits_iso286.yaml`）
#: ══════════════════════════════════════════════════════════════════════

def fits_meta() -> dict:
    """★ 公差库的**元信息**（★ 有哪些键）。"""
    d = _load("fits")
    return {k: (sorted(v) if isinstance(v, dict) else type(v).__name__)
            for k, v in d.items()}


def fit(name: str) -> dict:
    """★★ **查一个配合**（★ 如 `H7/k6`）。

    ★★ 判据：★ 表里有**孔/轴极限偏差**（0~500mm）+ **计算公式** ⇒
      ★ 可以算**间隙/过盈**。
    """
    d = _load("fits")
    for key in ("fits", "fits_table", "holes", "shafts"):
        tbl = d.get(key)
        if isinstance(tbl, dict) and name in tbl:
            return {"fit": name, "data": tbl[name]}
    #: ★ 兜底：**全库搜**
    for k, v in d.items():
        if isinstance(v, dict) and name in v:
            return {"fit": name, "data": v[name], "found_in": k}
    raise RuleError("unknown-fit", "★ 公差库里没有 `%s`" % name)


def fits_raw() -> dict:
    """★ 公差库的**原文**（★ 供上层自己算 —— ★ 本模块不替它算）。"""
    return _load("fits")


#: ══════════════════════════════════════════════════════════════════════
# 四、总览
#: ══════════════════════════════════════════════════════════════════════

def report() -> dict:
    """★ **总览**（★ 证明「业主早就给了」）。"""
    out = {"source": str(KB)}
    for which, fname in FILES.items():
        p = KB / fname
        out[which] = {"file": fname, "exists": p.is_file(),
                      "bytes": p.stat().st_size if p.is_file() else 0}
    try:
        out["material_count"] = len(materials())
        out["rule_groups"] = sorted(rules_tree())
    except RuleError as exc:
        out["error"] = str(exc)
    out["★"] = ("★ 三个 YAML 全部来自 `mech-design`（★ 业主早装好的）—— "
                "★ `design_rules.yaml` 自述「**先确认参数，不猜**」")
    return out
