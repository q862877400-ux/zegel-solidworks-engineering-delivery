"""门禁：**工具声明的参数必须"有归属"** —— 让「漏写 `param_alias`」这一类**不可能再发生**。

## 为什么要有这道门禁（**两次真实事故**逼出来的）
```
★ 事故一（Spec Kit `140` / W7）：`solidworks_simulation_apply_normal_force` 对外声明
  `magnitude_n`，而能力层形参是 `magnitude` ⇒ **漏写 `param_alias`**
  ⇒ 真机报 `TypeError: apply_normal_force() got an unexpected keyword argument 'magnitude_n'`。
★ 事故二（Spec Kit `141` / 段 1.1）：`create_study_report` / `find_study` 对外声明 `study_name`，
  而能力层形参是 `name` ⇒ **又漏写** ⇒ 真机报同一族的 `TypeError`。
⇒ ★★ 两次都是"**走工具真实路径**"的证据脚本当场抓住的（★ 那条纪律有效）。
★★★ 但"记下来"**不等于**"下次不犯" —— ★ 所以本门禁把这条**变成机器检查**：
    声明的每个参数名，要么**能在目标函数的形参表里找到**，
    要么**在 `param_alias` 里出现**（`None` = 由解析器消费；`"x"` = 改名为 x）。
★ 反面也查：`param_alias` 指向的目标名**必须真的存在于形参表**（否则就是改了名却改错了）。
★ 还查注入名：`spec.inject` 必须是 `RESOLVERS` 的键（★ 事实 169 的教训）。
```

## 判据（三条，都是"静态可判"的）
```
① 每个 `Param.name`：∈ 目标函数形参 **或** ∈ `param_alias`
② 每个 `param_alias[src] = dst`（`dst` 非 `None`）：`dst` ∈ 目标函数形参
③ `spec.inject`（非空时）：∈ `RESOLVERS` 的键
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁脚本）
# 文件:   scripts/check_param_binding.py
# 定位:   接进 `release_check.py`；★ 事故一/二 的**机器化修复**（不靠"记住"）。
# 官方依据: 不适用（查的是本项目的声明与能力层形参是否对得上）
# 许可:   本仓库 MIT。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for _p in (str(REPO), str(REPO / "mcp-server"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _target(spec):
    mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
    return getattr(mod, spec.function, None)


def check() -> list[str]:
    """回**问题清单**（空 = 通过）。"""
    import register_capabilities as rc

    problems: list[str] = []
    resolver_keys = set(rc.RESOLVERS)
    for spec in rc.all_specs():
        fn = _target(spec)
        if fn is None:
            problems.append("%s: 目标函数 scripts.%s.%s 不存在" % (spec.name, spec.module,
                                                              spec.function))
            continue
        try:
            formals = set(inspect.signature(fn).parameters)
        except (TypeError, ValueError) as exc:
            problems.append("%s: 取不到签名（%s）" % (spec.name, str(exc)[:50]))
            continue
        alias = dict(spec.param_alias or {})

        #: ① 声明的参数必须"有归属"
        for p in spec.params:
            if p.name in alias:
                continue
            if p.name not in formals:
                problems.append(
                    "%s: 参数 %r 既不在 %s 的形参表里、也没在 param_alias 里 "
                    "⇒ 调用时会 TypeError（★ 事故一/二 的同一族）"
                    % (spec.name, p.name, spec.function))

        #: ② `param_alias` 的目标名必须真的存在
        for src, dst in alias.items():
            if dst is None:
                continue
            if dst not in formals:
                problems.append(
                    "%s: param_alias 把 %r 改名成 %r，但 %s 的形参里没有 %r"
                    % (spec.name, src, dst, spec.function, dst))

        #: ③ 注入名必须是解析器的键
        inj = getattr(spec, "inject", "") or ""
        if inj and inj not in resolver_keys:
            problems.append("%s: inject=%r 不是 RESOLVERS 的键（有：%s）"
                            % (spec.name, inj, sorted(resolver_keys)))
    return problems


def check_forms() -> list:
    """★ **查"形态对"**（事实 232 的第三层）：

    ★ `spec.inject` 必须是 **str**（不是元组/列表）·
    ★ `Param.kind` 必须是**类型对象**（不是 "string" 这种字符串）。

    ★ 为什么单列：★ 这两处的错**只有"跑一次"能抓**，★ 而报错**指向名字**。
    """
    import register_capabilities as rc
    _RES = set(rc.RESOLVERS)
    problems: list = []
    for spec in rc.all_specs():
        inj = getattr(spec, "inject", None)
        if inj and not isinstance(inj, str):
            problems.append(
                "%s: inject=%r 是 %s —— ★ **必须是字符串**（如 inject=\"model\"）；"
                "★ 元组/列表会让 `in` 判断永远失败，而报错会误导成"
                "名字不在 RESOLVERS 里（★ 事实 232）。合法值：%s"
                % (spec.name, inj, type(inj).__name__, sorted(_RES)))
        for _p in (getattr(spec, "params", None) or []):
            _k = getattr(_p, "kind", None)
            if isinstance(_k, str):
                problems.append(
                    "%s: 参数 %r 的 kind=%r 是**字符串** —— ★ **必须传类型对象**"
                    "（str / int / float / bool / dict / list）；★ 传字符串会让下游生成模型时炸，"
                    "而报错离这里很远（★ 事实 232）。"
                    % (spec.name, getattr(_p, "name", "?"), _k))
    return problems


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


def main() -> int:
    #: ★★★ 2026-10-01（轮 305）**形态检查必须排在语义检查**之前****——
    #:   ★ 真机实测：把 `inject` 改成 **list** 时，旧的 `check()` **先炸**：
    #:     `TypeError: cannot use 'list' as a set element (unhashable type: 'list')`
    #:     ⇒ ★★ **形态错会让语义检查崩掉**，而下游的诊断（报形态的那两条）在后面等着
    #:     ⇒ ★ **先查形态、再查语义**（★ 而它们都属于同一条门禁，★ 所以只是**顺序**问题）。
    _form = check_forms() + check_field_forms()
    #: ★★ **形态有问题就**不跑语义检查****（★ 否则得到的是
    #:   `TypeError: unhashable type`，而不是"你的 inject 是个 list"——
    #:   ★ 诊断就在手里却被掩住了）。
    problems = _form if _form else check()
    total = 0
    try:
        import register_capabilities as rc

        total = len(rc.all_specs())
    except Exception:                                          # noqa: BLE001
        pass
    print("参数绑定门禁 · 扫 %d 个工具（判据：声明名 ∈ 形参 或 ∈ param_alias）" % total)
    if problems:
        print("\n  [FAIL] %d 处：" % len(problems))
        for x in problems[:40]:
            print("    · %s" % x)
        return 1
    print("  [PASS] 0 处 —— 每个声明参数都有归属，param_alias 目标都存在，注入名都是解析器的键")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
