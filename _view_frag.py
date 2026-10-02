

# ── 24h 计划 段 6 续（Spec Kit `160`）：**工程图视图读数的包装** ─────────────────────
# ★★★★ 为什么包一层（★ 第四次同法）：`sw_drawing_view` 的 12 个函数**全部吃一个 `view` 对象**
#   ⇒ ★★ 而工具层的入参只能是 `model`（★ 文档）⇒ ★ **所以要注入 `model` + 内部往下取 view**。
#   ★ 入口链：`model` → `get_first_view(drawing)` → `get_next_view(view)` → 逐个读。
#
# ★ 判据：★ ① **取视图链成功**（★ 一个视图都没有 ⇒ 如实报"这不是工程图 / 图里没视图"）；
#   ② ★ 每个视图的读数**如实回传**；③ ★ **按视图名查找失败时报出**已有的名字（★ 会列合法值）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_drawing_view.py —— 本段
# 定位:   段 6 续：让"工程图视图"从工具层可表达（★ 此前 12 个函数一个工具都没挂）。
# 官方依据: `IView` 族（★ Name / ScaleDecimal / GetAnnotationCount / GetVisibleComponentCount /
#          SetScale）—— ★ 见 `scripts/sw_drawing_view.py` 的既有来源块
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 4 个包装
# ─────────────────────────────────────────────────────────────────────────────


def _iter_views(model):
    """★ 遍历图纸上的视图（★ 取不到就回 `([], 原因)`）。"""
    try:
        require = getattr(__import__("scripts.sw_drawing_query", fromlist=["x"]), "require_drawing")
        require(model)                                          #: ★ 非工程图 ⇒ 它自己会抛（★ 不静默）
    except Exception as exc:                                   # noqa: BLE001
        return [], "不是工程图文档：%s" % str(exc)[:160]
    try:
        v = get_first_view(model)
    except Exception as exc:                                   # noqa: BLE001
        return [], "取第一个视图失败：%s: %s" % (type(exc).__name__, str(exc)[:160])
    out, seen = [], 0
    while v is not None and seen < 200:                        #: ★ 上限防死循环
        out.append(v); seen += 1
        try:
            v = get_next_view(v)
        except Exception:                                      # noqa: BLE001
            break
    if not out:
        return [], "图里没有视图（★ 图纸可能是空的）"
    return out, None


def list_drawing_views_report(model) -> dict:
    """★ **列出工程图的所有视图**（★ 名字 / 比例 / 注释数 / 可见件数）。"""
    views, err = _iter_views(model)
    if err:
        return {"ok": False, "error": err}
    rows = []
    for v in views:
        row = {}
        for key, fn in (("name", get_view_name), ("scale", get_view_scale),
                        ("scale_decimal", get_scale_decimal),
                        ("annotation_count", get_annotation_count),
                        ("visible_component_count", get_visible_component_count)):
            try:
                row[key] = fn(v)
            except Exception:                                  # noqa: BLE001
                row[key] = None
        rows.append(row)
    return {"ok": True, "count": len(rows), "views": rows}


def _find_view(model, view_name: str):
    views, err = _iter_views(model)
    if err:
        return None, err
    for v in views:
        try:
            if str(get_view_name(v)) == str(view_name):
                return v, None
        except Exception:                                      # noqa: BLE001
            continue
    names = []
    for v in views:
        try: names.append(str(get_view_name(v)))
        except Exception: names.append("?")
    return None, "没有名为 %r 的视图。★ 合法值：%s" % (view_name, names[:20])


def get_view_scale_report(model, view_name: str) -> dict:
    """★ **按视图名取比例**（★ 找不到就**列出合法值**）。"""
    v, err = _find_view(model, view_name)
    if err:
        return {"ok": False, "error": err}
    try:
        return {"ok": True, "view_name": str(view_name), "scale": get_view_scale(v),
                "scale_decimal": get_scale_decimal(v)}
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "view_name": str(view_name),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}


def set_view_scale_report(model, view_name: str, scale: float) -> dict:
    """★ **按视图名设比例并回读**（★ 规则 6：不静默成功）。"""
    v, err = _find_view(model, view_name)
    if err:
        return {"ok": False, "error": err}
    try:
        before = get_view_scale(v)
    except Exception:                                          # noqa: BLE001
        before = None
    try:
        r = set_view_scale(v, float(scale))
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "view_name": str(view_name),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}
    try:
        after = get_view_scale(v)
    except Exception:                                          # noqa: BLE001
        after = None
    #: ★ 判据：★ **回读值真的变了**（★ 而不是"没报错"）
    changed = (before is not None and after is not None and abs(float(after) - float(before)) > 1e-9)
    return {"ok": bool(r) and changed, "view_name": str(view_name),
            "asked": float(scale), "before": before, "after": after, "returned": bool(r)}


def collect_view_evidence_report(model) -> dict:
    """★ **每个视图的完整证据**（★ 走 `collect_view_evidence`）。"""
    views, err = _iter_views(model)
    if err:
        return {"ok": False, "error": err}
    out = []
    for v in views:
        try:
            out.append(collect_view_evidence(v))
        except Exception as exc:                               # noqa: BLE001
            out.append({"error": "%s: %s" % (type(exc).__name__, str(exc)[:140])})
    return {"ok": True, "count": len(out), "evidence": out}
