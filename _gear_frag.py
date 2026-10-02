

# ── 24h 计划 段 5/6 续（Spec Kit `158`）：**dict → SpurGearSpec 的包装** ─────────────
# ★★★★ 为什么包一层：★ 真机实测（轮 281）`calculate_external_spur_gear(spec)` 传 **dict** 时
#   报 **`'dict' object has no attribute 'module_mm'`** ⇒ ★★ **它要一个 `SpurGearSpec` 对象**。
# ★ 而**工具层的入参只能是 JSON**（★ dict）⇒ ★★ 所以正解是**在能力层做转换**
#    （★ 与孔族的 `*_at_selection`、求解器设置的 `*_report` **同一手法** —— 这是第三次）。
#
# ★ 判据：★ **转换失败要如实报**（★ 缺哪个键、非法值）—— ★ 不静默用默认值。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_gear.py —— 本段
# 定位:   段 5/6 续：让齿轮几何能从**工具层**（JSON 入参）表达。
# 官方依据: 渐开线直齿轮几何（★ 见 `scripts/sw_gear.py` 既有来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 2 个包装
# ─────────────────────────────────────────────────────────────────────────────


def _gear_spec_from_dict(spec):
    """★ 把 dict 变成 `SpurGearSpec`（★ **缺键/非法就抛**，不静默补默认）。"""
    if isinstance(spec, SpurGearSpec):
        return spec
    if not isinstance(spec, dict):
        raise TypeError("spec 必须是 dict 或 SpurGearSpec，收到 %s" % type(spec).__name__)
    import inspect as _inspect
    fields = {}
    try:
        params = _inspect.signature(SpurGearSpec).parameters
    except Exception:                                          # noqa: BLE001
        params = {}
    for name, p in params.items():
        if name in ("self",) or p.kind in (p.VAR_KEYWORD, p.VAR_POSITIONAL):
            continue
        if name in spec:
            fields[name] = spec[name]
        elif p.default is _inspect.Parameter.empty:
            raise KeyError("spec 缺少必填字段 %r（★ 合法字段：%s）"
                           % (name, ", ".join(k for k in params if k != "self")))
    #: ★ 多余键也报出来（★ 否则调用方会以为它生效了）
    extra = [k for k in spec if k not in params]
    if extra:
        raise KeyError("spec 含未登记字段 %s（★ 合法字段：%s）"
                       % (extra, ", ".join(k for k in params if k != "self")))
    return SpurGearSpec(**fields)


def calculate_external_spur_gear_report(spec) -> dict:
    """★ **算外啮合直齿轮几何**（★ 吃 dict；★ 判据对**解析式**）。"""
    try:
        s = _gear_spec_from_dict(spec)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "spec", "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    try:
        g = calculate_external_spur_gear(s)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "calculate",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    out = {}
    for name in ("pitch_diameter_mm", "base_diameter_mm", "outer_diameter_mm",
                 "root_diameter_mm", "teeth", "module_mm"):
        try:
            out[name] = getattr(g, name, None)
        except Exception:                                      # noqa: BLE001
            out[name] = None
    #: ★ 解析式核对：★ pitch = module × teeth（★ 事实 204/§5.0：期望值用几何推出的公式）
    try:
        pd, mm_, z = float(out.get("pitch_diameter_mm")), float(s.module_mm), float(s.teeth)
        out["_check_pitch_equals_module_times_teeth"] = abs(pd - mm_ * z) < 1e-6
    except Exception:                                          # noqa: BLE001
        out["_check_pitch_equals_module_times_teeth"] = None
    return {"ok": True, "readback": out}


def create_external_spur_gear_report(model, spec, plane_name: str = "Front Plane") -> dict:
    """★ **建外啮合直齿轮实体**（★ 吃 dict；★ 判据是**特征树变化** —— 规则 6）。"""
    try:
        s = _gear_spec_from_dict(spec)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "spec", "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    try:
        from sw_feature_readback import feature_names as _fn
        before = _fn(model)
    except Exception:                                          # noqa: BLE001
        before = None
    try:
        r = create_external_spur_gear(model, s, plane_name=plane_name)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "create",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    try:
        after = _fn(model)
    except Exception:                                          # noqa: BLE001
        after = None
    new = [x for x in (after or []) if x not in (before or [])] if before is not None and after is not None else []
    return {"ok": bool(new), "plane_name": plane_name, "new_features": new[:6],
            "returned": str(r)[:80]}
