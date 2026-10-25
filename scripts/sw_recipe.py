"""L2 · 配方（recipe）：从捕获的模型语义提炼「意图 + 判据」，可读可校验可执行。

## 为什么不是「动作序列」

业主 2026-10-26：「我可能会有反复检查，可能会有错误了之后再删除，然后再重新做。」
⇒ 动作里含废动作；同一结果有多条动作路径；UI 动作还绑死版本与语言。

⇒ 配方只记 **intent（意图）+ assertions（判据）**，`hints` 只作提示。

## 数据形状（`recipe.yaml`）

```yaml
id: hole-4x-m6-gb
title: 一块板上 4 个 M6 间隙孔（一个孔特征 + 关系 + 尺寸）
version: 1
provenance: {demonstrated_by: owner, demonstrated_at: 2026-10-26, capture: ...}
intent: |
  4 个孔位放进**一个**孔特征；用水平/竖直关系把 4 个点组成矩形；标准用 GB。
inputs:
  plate: {width_mm: 100, height_mm: 60, thickness_mm: 20}
  hole:  {standard: GB, fastener: 螺钉间隙, size: M6, through: true,
          diameter_mm: 6.6}
  positions_mm: [[10,10],[90,10],[10,50],[90,50]]
hints:
  relations: [HORIZPOINTS, VERPOINTS, HORIZPOINTS, VERPOINTS]
  dimension_style: to_edge     # to_edge | points_plus_fixed
assertions:
  feature_count_hole: 1
  hole_sketch_constrained: 3
  hole_standard: GB
  cylinder_count: 4
```

★ 校验只认 `assertions` 里的键（见 `ALLOWED_ASSERTIONS`），写错键**直接报错**，
  免得「以为在验、其实没验」。
"""
from __future__ import annotations

import json
from pathlib import Path

#: 允许的 assertion 键 ⇒ 说明（写错键要立刻红，不许静默忽略）
ALLOWED_ASSERTIONS = {
    "feature_count_hole": "孔特征（HoleWzd）的个数",
    "hole_sketch_constrained": "孔位（定位）草图的求解状态：3 = 完全定义",
    "hole_standard": "孔特征的标准名需包含的子串（如 GB）",
    "hole_size": "孔规格（如 M6），非空即可",
    "hole_fastener": "孔紧固类型（如 螺钉间隙），非空即可",
    "cylinder_count": "圆柱面个数 = 孔数（独立于特征树的几何核对）",
}

#: 配方版本（结构不兼容时升）
RECIPE_VERSION = 1


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（示教器 L2 · 配方数据模型与校验）
# 文件:   scripts/sw_recipe.py
# 定位:   recipe 的读写与校验；把 L1 捕获的模型语义（model.json）提炼成可执行配方。
#          示教器的中间层，让「人示范一次」变成「机器可复现」。
# 官方依据: 不适用（本仓自身数据格式）；语义来源为业主 2026-10-26 的示范模型，
#          经 scripts/sw_model_snapshot.py 读出（关系 25/26 + 距离尺寸 + GB 孔）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


class RecipeError(ValueError):
    """配方不合法（键写错、缺必需字段等）—— 一律**抛**，不静默。"""


def _mini_yaml_dump(data, indent: int = 0) -> str:
    """极简 YAML 输出（只覆盖本配方用到的结构：dict/list/str/num/bool）。

    ★ 不引入 PyYAML 依赖：配方结构固定，自己写足够；读回时也用本模块的解析器。
    """
    pad = "  " * indent
    out = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                out.append("%s%s:" % (pad, k))
                out.append(_mini_yaml_dump(v, indent + 1))
            elif isinstance(v, list) and v and isinstance(v[0], (list, dict)):
                out.append("%s%s:" % (pad, k))
                for item in v:
                    out.append("%s  - %s" % (pad, json.dumps(item, ensure_ascii=False)))
            elif isinstance(v, list):
                out.append("%s%s: [%s]" % (
                    pad, k, ", ".join(_scalar(x) for x in v)))
            else:
                out.append("%s%s: %s" % (pad, k, _scalar(v)))
    return "\n".join(out)


def _scalar(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if v is None:
        return "null"
    s = str(v)
    if any(c in s for c in ":#[]{}\n") or s.strip() != s:
        return json.dumps(s, ensure_ascii=False)
    return s


def _mini_yaml_load(text: str) -> dict:
    """解析本模块自己写出的 YAML 子集（缩进 + `- ` 列表 + 行内 JSON 列表）。

    ★ `pending` 记「值为空、后面可能跟 `- ` 列表」的父容器 —— 第一版没有它，
      于是 `positions_mm:\n  - [10,-10]` 被读成 `{}`，配方静默丢孔位。
    """
    root: dict = {}
    stack = [(0, root)]
    pending: list = []
    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        while len(stack) > 1 and indent < stack[-1][0]:
            stack.pop()
        cur = stack[-1][1]
        if line.startswith("- "):
            item = line[2:].strip()
            while pending and pending[-1][2] > indent:
                pending.pop()
            if pending:
                cont, key, _k = pending[-1]
                if not isinstance(cont.get(key), list):
                    cont[key] = []
                try:
                    cont[key].append(json.loads(item))
                except Exception:  # noqa: BLE001
                    cont[key].append(item)
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            child: dict = {}
            cur[key] = child
            stack.append((indent + 2, child))
            pending.append((cur, key, indent + 1))
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            cur[key] = [_coerce(x.strip()) for x in inner.split(",")] if inner else []
        else:
            cur[key] = _coerce(val)
    return root


def _coerce(v: str):
    if v.startswith('"') and v.endswith('"'):
        try:
            return json.loads(v)
        except Exception:  # noqa: BLE001
            return v.strip('"')
    if v in ("true", "false"):
        return v == "true"
    if v == "null":
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        return v


def validate(recipe: dict) -> list:
    """校验配方，回**问题清单**（空 = 合法）。"""
    p: list = []
    if not isinstance(recipe, dict):
        return ["配方必须是映射（dict）"]
    for key in ("id", "title", "assertions"):
        if not recipe.get(key):
            p.append("缺必需字段：%s" % key)
    a = recipe.get("assertions") or {}
    if not isinstance(a, dict) or not a:
        p.append("assertions 必须是非空映射")
    else:
        unknown = [k for k in a if k not in ALLOWED_ASSERTIONS]
        if unknown:
            p.append("assertions 里有未知键（写错就等于没验）：%s；允许的键：%s"
                     % (unknown, sorted(ALLOWED_ASSERTIONS)))
    inp = recipe.get("inputs") or {}
    if not isinstance(inp, dict):
        p.append("inputs 必须是映射")
    else:
        pos = inp.get("positions_mm")
        if pos is not None:
            if not isinstance(pos, list) or not pos:
                p.append("inputs.positions_mm 必须是非空列表")
            else:
                for item in pos:
                    if not (isinstance(item, (list, tuple)) and len(item) == 2):
                        p.append("positions_mm 每项必须是 [x_mm, y_mm]：%r" % (item,))
                        break
    return p


def dump(recipe: dict) -> str:
    """配方 → YAML 文本（稳定输出，便于 diff）。"""
    data = dict(recipe)
    data.setdefault("version", RECIPE_VERSION)
    return "# 示教器配方（L2）：意图 + 判据。由 tools/teach.py 读写。\n" + \
        _mini_yaml_dump(data) + "\n"


def load(path) -> dict:
    """读配方并校验；不合法就抛 `RecipeError`（不静默）。"""
    p = Path(path)
    if not p.is_file():
        raise RecipeError("配方不存在：%s" % p)
    data = _mini_yaml_load(p.read_text(encoding="utf-8"))
    problems = validate(data)
    if problems:
        raise RecipeError("配方不合法：\n  - " + "\n  - ".join(problems))
    return data


def save(recipe: dict, path) -> Path:
    """校验后落盘；不合法就抛。"""
    problems = validate(recipe)
    if problems:
        raise RecipeError("配方不合法：\n  - " + "\n  - ".join(problems))
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dump(recipe), encoding="utf-8", newline="\n")
    return p


def derive_from_snapshot(snap: dict, *, capture: str = "", by: str = "owner") -> dict:
    """L2：`model.json`（L1 的语义快照）→ recipe。

    只提炼**能确证的**东西；确证不了的留空并写在 `notes` 里，不编。
    """
    feats = snap.get("features") or []
    holes = snap.get("holes") or []
    plate = {}
    #: 板草图的最小角（用来把孔位**归一化**到板自身坐标系）
    plate_lo = None
    #: 板尺寸：取顶层草图（非孔内）的点包络
    for sk in snap.get("sketches") or []:
        pts = sk.get("points") or []
        if len(pts) >= 4:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            plate = {"width_mm": round(max(xs) - min(xs), 3),
                     "height_mm": round(max(ys) - min(ys), 3)}
            plate_lo = (min(xs), min(ys))
            break
    #: 板厚：优先用包围盒的 Z 跨度（几何事实），读不到才留空
    bb = snap.get("bbox_mm") or []
    if len(bb) >= 6:
        try:
            #: ★ bbox 的 raw 是**米**（实测 0.02 = 20mm）⇒ 必须 ×1000，
            #:   否则板厚被写成 0.02「毫米」，L3 建出一张纸片。
            plate["thickness_mm"] = round(
                abs(float(bb[5]) - float(bb[2])) * 1000.0, 3)
        except (TypeError, ValueError):
            plate.setdefault("thickness_mm", None)
    else:
        plate.setdefault("thickness_mm", None)
    for f in feats:
        if f.get("type") == "Extrusion":
            break

    hole_in = {}
    positions = []
    relations = []
    n_hole = len(holes)
    if holes:
        h0 = holes[0]
        hole_in = {"standard": h0.get("standard"), "fastener": h0.get("fastener"),
                   "size": h0.get("size"), "through": True}
        for sk in h0.get("sketches") or []:
            pts = sk.get("points") or []
            rels = sk.get("relations") or []
            #: 定位草图 = 有距离尺寸的那张
            if any(r.get("type") == "DISTANCE" for r in rels):
                #: ★ 归一化：示范件的孔位可能是负坐标（它的草图原点在别处），
                #:   而执行时板从 (0,0) 建起 ⇒ 不减掉板的最小角，射线会打空。
                ox, oy = plate_lo if plate_lo else (0.0, 0.0)
                positions = [[round(p[0] - ox, 3), round(p[1] - oy, 3)]
                             for p in pts]
                relations = [r.get("type") for r in rels
                             if r.get("type") not in ("DISTANCE",)]
                diameters = [r.get("value_mm") for r in rels
                             if r.get("type") in ("DIAMETER", "DOUBLEDISTANCE")]
                if diameters:
                    hole_in["diameter_mm"] = diameters[0]
                break

    notes = []
    if plate.get("thickness_mm") is None:
        notes.append("拉伸深度读不到 ⇒ 留空，执行时用 habits 或显式参数")
    if not positions:
        notes.append("没找到带距离尺寸的孔位草图 ⇒ positions_mm 留空")

    return {
        "id": "derived-%s" % (snap.get("document") or "part").replace(" ", "-"),
        "title": "由示范自动提炼：%s" % (snap.get("document") or "未命名"),
        "version": RECIPE_VERSION,
        "provenance": {
            "demonstrated_by": by,
            "capture": capture or "",
            "document": snap.get("document") or "",
        },
        "intent": "照示范复现：孔位的相对关系 + 到参照的距离尺寸做到全定义。",
        "inputs": {"plate": plate, "hole": hole_in, "positions_mm": positions},
        "hints": {"relations": relations, "dimension_style": "to_edge"},
        "assertions": {
            "feature_count_hole": n_hole,
            "hole_sketch_constrained": 3,
            "hole_standard": hole_in.get("standard") or "GB",
            "cylinder_count": len(positions) or 4,
        },
        "notes": notes,
    }
