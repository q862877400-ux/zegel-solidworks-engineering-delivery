

# ── 24h 计划 段 1 续（Spec Kit `154`）：**从 study 取 options 的求解器设置包装** ──────────
# ★★★★ 为什么包一层（★ 而不是加新的注入键）：
#   · 底层 `configure_static_solver(options, …)` / `set_option(options, family, name, value)` 等
#     **要一个 `options` 宿主对象**；★ 而那个对象**从 study 取**：
#       `study_options_of(study, family)` → `get_com_member(study, accessor)`
#   · ★★ 而 **`inject="study"` 早就存在**（`resolve_study`）⇒ ★★★ **所以包一层就够了**：
#       工具层**注入 `study`** ⇒ 包装内部**先取 options** ⇒ 再调底层
#     ⇒ ★★★★ **不需要新增 `RESOLVERS` 键**（★ 加了要同步解析器，★ 而这里没必要）。
#   ★ 与孔族（`*_at_selection`）**同一手法**：★ **用已有的 resolver + 包装**表达新工具。
#
# ★ 判据（★ 三层）：
#   ① ★ 取 options **成功**（★ 取不到就如实报 —— `study_options_of` 对**未确认的族名**会抛
#      `KeyError` 并**列出已确认的那些** ⇒ ★ 那正是"会列合法值的好报错"，见事实 204）；
#   ② ★ 底层返回的 **`bool` / dict 如实回传**；
#   ③ ★ 把**用了哪个族**与**改了什么**记在返回里（★ 便于下一步回读核对）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_simulation_study_options.py —— 本段
# 定位:   段 1 续：让"求解器设置"能被工具层表达（★ 不要注入键）。
# 官方依据: `ICWStaticStudyOptions` / `ICWFrequencyStudyOptions` / `ICWBucklingStudyOptions`
#          （★ 见 `STUDY_OPTIONS_ACCESSORS` 的反射清单）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 5 个包装
# ─────────────────────────────────────────────────────────────────────────────


def _options_from_study(study, family: str):
    """★ 从 study 取某个设置族对象；★ 取不到就**如实报**（★ 不静默）。"""
    if study is None:
        return None, "study 为 None（★ 需要先建/找到研究）"
    try:
        opts = study_options_of(study, family)
    except Exception as exc:                                   # noqa: BLE001
        return None, "取 options 失败（family=%s）：%s" % (family, str(exc)[:200])
    if opts is None:
        return None, ("study 上取不到 family=%s 的设置对象 ⇒ "
                      "★ 该研究类型可能不是这一族（★ 见 list_setter_summary 的族清单）" % family)
    return opts, None


def configure_static_solver_report(study, family: str = "ICWStaticStudyOptions", **kwargs) -> dict:
    """★ **静力求解器设置**：★ 从 `study` 取 options ⇒ 调 `configure_static_solver`。

    ★ kwargs 里**只传非 None 的**（★ 底层用 `None` 表示"不改"，★ 所以过滤掉 None 是**保持语义**）。
    """
    opts, err = _options_from_study(study, family)
    if err:
        return {"ok": False, "family": family, "error": err}
    kw = {k: v for k, v in kwargs.items() if v is not None}
    try:
        r = configure_static_solver(opts, **kw)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "family": family, "changed": sorted(kw),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    return {"ok": bool(r), "family": family, "changed": sorted(kw), "returned": r}


def configure_frequency_solver_report(study, family: str = "ICWFrequencyStudyOptions", **kwargs) -> dict:
    """★ **频率求解器设置**（★ 同族手法）。"""
    opts, err = _options_from_study(study, family)
    if err:
        return {"ok": False, "family": family, "error": err}
    kw = {k: v for k, v in kwargs.items() if v is not None}
    try:
        r = configure_frequency_solver(opts, **kw)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "family": family, "changed": sorted(kw),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    return {"ok": bool(r), "family": family, "changed": sorted(kw), "returned": r}


def configure_buckling_solver_report(study, family: str = "ICWBucklingStudyOptions", **kwargs) -> dict:
    """★ **屈曲求解器设置**（★ 同族手法）。"""
    opts, err = _options_from_study(study, family)
    if err:
        return {"ok": False, "family": family, "error": err}
    kw = {k: v for k, v in kwargs.items() if v is not None}
    try:
        r = configure_buckling_solver(opts, **kw)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "family": family, "changed": sorted(kw),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    return {"ok": bool(r), "family": family, "changed": sorted(kw), "returned": r}


def set_study_option_report(study, family: str, name: str, value) -> dict:
    """★ **按登记表设一个求解器选项**（★ 从 `study` 取 options）。

    ⚠ `set_option` 对**未登记的族名/选项名**抛 `KeyError`（★ **不静默忽略**）——
      ★ 包装里如实回传（★ 于是调用方能看出"名字写错了"而不是"设了但没生效"）。
    """
    opts, err = _options_from_study(study, family)
    if err:
        return {"ok": False, "family": family, "name": name, "error": err}
    try:
        r = set_option(opts, family, name, value)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "family": family, "name": name,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    return {"ok": bool(r), "family": family, "name": name, "value": value, "returned": r}


def set_study_options_report(study, family: str, values: dict) -> dict:
    """★ **一次设一组求解器选项**（★ 从 `study` 取 options）。"""
    opts, err = _options_from_study(study, family)
    if err:
        return {"ok": False, "family": family, "error": err}
    try:
        r = set_options(opts, family, values)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "family": family,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    return {"ok": bool(r) if isinstance(r, bool) else True, "family": family,
            "asked": sorted(values), "readback": r}
