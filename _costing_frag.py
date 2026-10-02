

# ── 24h 计划 段 4 续（Spec Kit `155`）：**Costing 的"注入 manager + 内部取下游"包装** ──────
# ★★★★ 为什么（★ 而这一片有真价值）：
#   · **Costing 是 AGENTS.md §〇 点名的三个「真正全网空白域」之一**（拓扑优化 · 动画导出 AVI · Costing）；
#   · `sw_costing` 有 **25 个公开函数**，★ 而**只挂了 1 个**（`get_costing_manager`）；
#   · 其余 24 个的入参都是**宿主对象**（`cost_manager` / `cost_part` / `cost_analysis` /
#     `cost_body` / `defaults`）⇒ ★★ **所以要点是"怎么拿到它们"**；
#   ⇒ ★★★ **正解与轮 272 完全同一手法**：★ **注入 `manager`（已有 resolver）+ 包装内部取下游**
#     （`CostingModel` / `CostingDefaults` / `GetCostAnalysis()` / `GetBodies()`）。
#   ★ `get_costing_manager` 的 docstring 记着两条**重要实测**：★
#     「Costing 加载项**未「加载」也能拿到**」·「4 个 ProgID **全返 None** ⇒ **不要在入口上再试探**」。
#
# ★ 判据（★ 三层，与 `configure_*_solver_report` 一致）：
#   ① ★ **取下游对象成功**（★ 取不到就如实报，★ 含"卡在哪一环"）；
#   ② ★ **底层返回值如实回传**；
#   ③ ★ 把**读了什么/设了什么**记在返回里（★ 便于下一步核对）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_costing.py —— 本段
# 定位:   段 4 续：把 Costing 的读数族挂上柜台（★ 护城河域）。
# 官方依据: `IModelDocExtension.GetCostingManager` · `ICostManager` / `ICostPart` /
#          `ICostAnalysis` / `ICostingDefaults`（★ 见 `scripts/sw_costing.py` 的来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 8 个包装 + 1 个助手
# ─────────────────────────────────────────────────────────────────────────────


def _costing_chain(cost_manager):
    """★ 从 `cost_manager` 往下取 `(model, defaults, err)`（★ 取不到就**如实报哪一环**）。"""
    if cost_manager is None:
        return None, None, "cost_manager 为 None（★ 先用 solidworks_get_costing_manager 取它）"
    try:
        m = get_costing_model(cost_manager)
    except Exception as exc:                                   # noqa: BLE001
        return None, None, "取 CostingModel 失败：%s" % str(exc)[:160]
    if m is None:
        return None, None, "CostingModel 为 None ⇒ ★ Costing 可能没在这个文档上初始化"
    try:
        d = get_costing_defaults(cost_manager)
    except Exception:                                          # noqa: BLE001
        d = None                                               #: ★ 默认值取不到不算致命
    return m, d, None


def collect_costing_evidence_report(cost_manager) -> dict:
    """★ **成本状态概览**（★ 实体数 + 有没有成本分析）。"""
    m, _d, err = _costing_chain(cost_manager)
    if err:
        return {"ok": False, "error": err}
    try:
        r = collect_costing_evidence(m)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}
    return {"ok": isinstance(r, dict), "readback": r}


def read_cost_analysis_report(cost_manager) -> dict:
    """★ **读成本分析的全部可读项**（★ 那是最有价值的一项读数）。"""
    m, _d, err = _costing_chain(cost_manager)
    if err:
        return {"ok": False, "error": err}
    try:
        ca = get_cost_analysis(m)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "get_cost_analysis",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}
    if ca is None:
        return {"ok": False, "stage": "get_cost_analysis",
                "error": "成本分析为 None ⇒ ★ 该零件可能还没做过成本分析（★ 先 create_cost_analysis）"}
    try:
        r = read_cost_analysis(ca)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "read_cost_analysis",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}
    return {"ok": isinstance(r, dict), "readback": r}


def get_body_count_report(cost_manager) -> dict:
    """★ **实体数**（★ 成本是按实体算的）。"""
    m, _d, err = _costing_chain(cost_manager)
    if err:
        return {"ok": False, "error": err}
    try:
        n = get_body_count(m)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}
    return {"ok": n is not None, "body_count": n}


def list_cost_bodies_report(cost_manager) -> dict:
    """★ **列出实体**（★ 回它们的名字 —— ★ 供 `read_cost_body_report` 用）。"""
    m, _d, err = _costing_chain(cost_manager)
    if err:
        return {"ok": False, "error": err}
    try:
        b = get_bodies(m)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}
    names = []
    for x in (b or []):
        try:
            nm = get_com_member(x, "Name")
        except Exception:                                      # noqa: BLE001
            nm = None
        names.append(str(nm) if nm else "?")
    return {"ok": b is not None, "count": len(names), "names": names[:20]}


def read_cost_body_report(cost_manager, body_name: str) -> dict:
    """★ **按名字读一个实体的成本**（★ `body_name` 从 `list_cost_bodies_report` 来）。"""
    m, _d, err = _costing_chain(cost_manager)
    if err:
        return {"ok": False, "error": err}
    try:
        bodies = get_bodies(m) or []
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "get_bodies",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}
    target = None
    for x in bodies:
        try:
            nm = str(get_com_member(x, "Name") or "")
        except Exception:                                      # noqa: BLE001
            nm = ""
        if nm == str(body_name):
            target = x
            break
    if target is None:
        got = []
        for x in bodies:
            try: got.append(str(get_com_member(x, "Name") or "?"))
            except Exception: got.append("?")
        return {"ok": False, "stage": "find_body",
                "error": "没有名为 %r 的实体。★ 合法值：%s" % (body_name, got[:20])}
    try:
        r = read_cost_body(target)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "read_cost_body",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}
    return {"ok": isinstance(r, dict), "body_name": str(body_name), "readback": r}


def list_costing_templates_report(cost_manager, category: int = 0) -> dict:
    """★ **成本模板清单**（★ 回清单 ⇒ ★ 于是调用方能看出合法值）。"""
    _m, d, err = _costing_chain(cost_manager)
    if err:
        return {"ok": False, "error": err}
    if d is None:
        return {"ok": False, "stage": "CostingDefaults", "error": "取不到 CostingDefaults"}
    try:
        t = list_templates(d, category)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}
    return {"ok": t is not None, "category": int(category),
            "count": len(t) if hasattr(t, "__len__") else None,
            "templates": [str(x) for x in (t or [])][:20]}


def get_default_template_report(cost_manager, category: int) -> dict:
    """★ **某类别的默认模板名**。"""
    _m, d, err = _costing_chain(cost_manager)
    if err:
        return {"ok": False, "error": err}
    if d is None:
        return {"ok": False, "stage": "CostingDefaults", "error": "取不到 CostingDefaults"}
    try:
        t = get_default_template(d, int(category))
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}
    return {"ok": t is not None, "category": int(category), "template": str(t) if t else None}


def get_costing_method_report(cost_manager, method_name: str) -> dict:
    """★ **某个成本方法的取值**（★ `method_name` 见 `read_cost_analysis` 的方法清单）。"""
    m, _d, err = _costing_chain(cost_manager)
    if err:
        return {"ok": False, "error": err}
    try:
        v = get_costing_method(m, str(method_name))
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "method_name": str(method_name),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}
    return {"ok": v is not None, "method_name": str(method_name), "value": v}
