

def check_field_forms() -> list:
    """★ **字段形态白名单**（事实 232/233 的推广）：每个 `ToolSpec` 字段**允许的形态**是固定的。

    ★ 白名单是**从 180 个既有工具实测出来的**（★ 不是猜的）：
    ```
    inject        : str | None      （168 str / 12 None）
    module        : str
    function      : str
    title         : str
    doc           : str
    omitted_params: tuple
    param_alias   : dict           （★ 值是 str | None —— 两种都合法）
    derived_args  : callable | None（161 None / 19 function）
    pre_call      : callable | None（169 None / 11 function）
    extra_op      : callable | None（180 None）
    ```
    ★ 判据：★ **实际形态 ∈ 白名单** ⇒ 违反时报**期望形态**与**实际形态**（★ 而不是只说"不对"）。
    ★ 为什么单列一条：★ 事实 232 —— 参数的错有**三层**（名字 / 类型 / **形态**），
      ★ 而**第三层只有"跑一次"能抓**、★ 且**它的报错指向名字**。
    """
    import register_capabilities as rc
    whitelist = {
        "inject": ("str", "NoneType"),
        "module": ("str",),
        "function": ("str",),
        "title": ("str",),
        "doc": ("str", "NoneType"),
        "omitted_params": ("tuple", "NoneType"),
        "param_alias": ("dict", "NoneType"),
        "derived_args": ("function", "NoneType", "method"),
        "pre_call": ("function", "NoneType", "method"),
        "extra_op": ("function", "NoneType", "method"),
    }
    problems: list = []
    for spec in rc.all_specs():
        for field, allowed in whitelist.items():
            v = getattr(spec, field, None)
            got = type(v).__name__
            if got not in allowed:
                problems.append(
                    "%s: 字段 %s 的形态是 **%s** —— ★ **期望 %s**（★ 白名单据 180 个既有工具实测："
                    "事实 233）。★ 形态错时下游的**报错会指向名字而不是形态**，很难查。"
                    % (spec.name, field, got, " / ".join(allowed)))
        #: \u2605 `param_alias` \u7684**\u503c**\u4e5f\u67e5\uff08\u2605 \u4e24\u79cd\u5408\u6cd5\uff1astr | None\uff09
        pa = getattr(spec, "param_alias", None)
        if isinstance(pa, dict):
            for k, v in pa.items():
                if v is not None and not isinstance(v, str):
                    problems.append(
                        "%s: param_alias[%r] 的值是 **%s** —— ★ **期望 str 或 None**"
                        "（★ 180 个既有工具只有这两种；事实 233）。"
                        % (spec.name, k, type(v).__name__))
    return problems
