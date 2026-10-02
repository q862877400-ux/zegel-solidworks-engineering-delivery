

# ── 24h 计划 段 6 续（Spec Kit `165`）：**给 `inject` 与 `Param.kind` 加**形态**校验** ──────
# ★★★★★ 2026-10-01（轮 302→303）**这条门禁**本来就查了 `inject`，★ 而它漏了形态**：
#   · 旧代码 `inj = getattr(spec, "inject", "") or ""` ⇒ ★ **元组 `("model",)` 是真值** ⇒ `inj` 就是那个元组
#     ⇒ 然后判 `inj not in RESOLVERS` ⇒ 元组**永远不等于**字符串键 ⇒ 报
#       「inject=('model',) 不是 RESOLVERS 的键（有：['asm_model', 'manager', 'model', …]）」
#     ⇒ ★★★ **而那条报错**字面上自相矛盾****：`'model'` **明明在**列出的那个集合里！
#   · 真因是**形态**（元组 vs 字符串），★ 而**报错指向名字** ⇒ ★★ 与事实 232 同一条。
#   ★ 同时加上 `Param.kind` 的形态校验：★ **必须是**类型对象**（`str`/`int`/`float`/`bool`/`dict`/`list`）——
#     写 `"string"` 这类**字符串**在 `Param` 的签名里是一个**值**、不是类型，★ 会让下游生成模型时炸
#     （★ 本会话实测：`server.py` 报 `cadstudio_resolve_backendArguments is not fully defined`，
#      ★ 而真因离它很远）。
#
# ★ 判据：★ **两条都做成"报错里带上正确形态"**（★ 与事实 197「报错要会列合法值」同族）。
# ⚠ **本段只加校验，不改既有判定**（★ 原来那两条判据原样保留）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁实现）
# 文件:   scripts/check_param_binding.py —— 本段
# 定位:   门禁③（注入名）与门禁②（参数归属）都保留，★ **新增两条形态判据**。
# 官方签名依据: 不适用（本文件是本仓库的门禁，判据来自 `tool_registry.RESOLVERS` 与 `Param` 的签名）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def check_forms() -> list:
    """★ **查"形态对"**：`spec.inject` 必须是 `str` · `Param.kind` 必须是**类型对象**。

    ★ 为什么单列一条：★ 事实 232 —— 参数的错有**三层**（名字对 / 类型对 / **形态对**），
    ★ 而**第三层只有"跑一次"能抓**，★ 且它的报错**指向名字、不指向形态**。
    ⇒ 本函数把那层**变成静态可抓**的（★ 而它抓的两处，本会话各踩过一次）。
    """
    import inspect as _inspect
    from tool_registry import RESOLVERS as _RES
    problems: list = []
    for spec in _specs():
        inj = getattr(spec, "inject", None)
        if inj:
            if not isinstance(inj, str):
                problems.append(
                    "%s: inject=%r 是 %s —— ★ **必须是字符串**（如 inject=\"model\"）；"
                    "★ 元组/列表会让 `in` 判断永远失败，而报错会误导成\"名字不在 RESOLVERS 里\""
                    "（★ 事实 232）。合法值：%s"
                    % (spec.name, inj, type(inj).__name__, sorted(_RES)))
            elif inj not in _RES:
                problems.append("%s: inject=%r 不是 RESOLVERS 的键（有：%s）"
                                % (spec.name, inj, sorted(_RES)))
        for p in (getattr(spec, "params", None) or []):
            k = getattr(p, "kind", None)
            if isinstance(k, str):
                problems.append(
                    "%s: 参数 %r 的 kind=%r 是**字符串** —— ★ **必须传类型对象**"
                    "（str / int / float / bool / dict / list）；★ 传字符串会让下游生成模型时炸，"
                    "而报错离这里很远（★ 事实 232）。"
                    % (spec.name, getattr(p, "name", "?"), k))
            elif not (isinstance(k, type) or k is None):
                problems.append("%s: 参数 %r 的 kind=%r 既不是类型也不是 None"
                                % (spec.name, getattr(p, "name", "?"), k))
    _ = _inspect            # ★ 保留 import（★ 便于后续扩展成"查签名"）
    return problems
