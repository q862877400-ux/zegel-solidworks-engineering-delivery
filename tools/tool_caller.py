"""★ 按 `ToolSpec` 契约调一个工具（★ 给 B2 的灵敏度标定与 B3 的存活普查共用）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具层）
# 文件:   tools/tool_caller.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B2（写操作那一格）/ B3**。★ 本仓纪律原话：
#   ★「写探针验能力时：**按 `ToolSpec` 的契约调，别手调内部实现**」——
#   ★★ 而我在 B2 第一版**正是手调的**（直接调 `sw_part` 的公开函数）⇒ ★ 形状不对、抛 `TypeError` ✗
#   ★ 契约（读 `mcp-server/tool_registry.py` 的 `make_tool_function` 得知）：
#     ① `kwargs[inject_as 或 spec.inject] = <宿主对象>`（★ 注册器负责解析，我们传现成的）
#     ② `kwargs[形参名] = <该形参的值>` ✓
# 判据:   ★★ `call(name, inject_objects={...}, **params)` ⇒ 回 `(ok, 说明)` ——
#   ★ **拿不到 spec / 缺注入对象 / 参数缺失** ⇒ ★ 回 `False` 并把原因写清楚（★ 不假装调过）✓
#   ★ 参数**没给且声明里有默认值** ⇒ 用默认值（★ 契约里就是这么填的）✓
# 官方依据: 无（本仓契约）—— ★ 如实标注 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_SPECS_CACHE: dict | None = None


def _specs() -> dict:
    """★ 惰性取全部 `ToolSpec`（★ 按名字建索引）✓"""
    global _SPECS_CACHE
    if _SPECS_CACHE is None:
        import register_capabilities as rc
        from tool_registry import effective_inject
        _SPECS_CACHE = {}
        for s in rc.all_specs():
            _SPECS_CACHE[s.name] = (s, effective_inject(s))
    return _SPECS_CACHE


def describe(tool_name: str) -> dict:
    """★ 一个工具的**契约摘要**（注入名 · 形参名与是否必需）—— ★ 不调它，只描述 ✓"""
    entry = _specs().get(tool_name)
    if not entry:
        return {"found": False}
    spec, inject = entry
    params = []
    for p in (spec.params or []):
        params.append({"name": p.name, "required": bool(getattr(p, "required", False)),
                       "default": getattr(p, "default", None)})
    return {"found": True, "inject": inject or "", "module": spec.module,
            "function": spec.function, "params": params}


def call(tool_name: str, *, inject_objects=None, **params):
    """★★ 按契约调一个工具 —— 回 `(ok, 说明)` ✓

    ★★ 首参刻意**不叫 `name`** —— ★ 真机踩过：★ 有的工具的形参**就叫 `name`** ⇒
      ★ 用 `call(name, **params)` 形式的调用会撞成 `got multiple values for argument 'name'` ✗
    :param inject_objects: `{注入名: 宿主对象}`（★ 如 `{"model": model, "sw": sw}`）
    :param params: 形参（★ 名字与声明一致）✓
    """
    entry = _specs().get(tool_name)
    if not entry:
        return False, "★ 工具名不在声明里：%s" % tool_name
    spec, inject = entry
    try:
        mod = None
        for cand in (spec.module, "scripts.%s" % spec.module):
            try:
                mod = importlib.import_module(cand)
                break
            except Exception:                                           # noqa: BLE001
                continue
        if mod is None:
            return False, "★ 模块导入失败：%s" % spec.module
        fn = getattr(mod, spec.function, None)
        if not callable(fn):
            return False, "★ 函数不存在：%s" % spec.function
        #: ★★★ 契约里有**两层映射**，`make_tool_function` 的注释写得很清楚
        #:   （★ 我第一版**没实现这两层**，所以调用形状不对 —— ★ 那是我的缺陷，不是声明的）✓
        #:   ① `param_alias`：**对外参数名 → 目标函数形参名**；★ 值为 `None` ⇒
        #:      **该参数由解析器消费、不传给目标函数** ✓
        #:   ② `derived_args`：`lambda params: {...}` —— ★ **从已声明的标量入参派生额外实参**，
        #:      返回的字典**并进**调用关键字实参里 ✓（★ 单位换算也在这里做）
        vals = {}
        for pp in (spec.params or ()):
            if pp.name in params:
                vals[pp.name] = params[pp.name]
            elif getattr(pp, "default", None) is not None and getattr(pp, "default", None) is not Ellipsis:
                vals[pp.name] = pp.default
        #: ★ 先按声明检查"必填且没给"（★ `Ellipsis` 是本仓约定的"必填"）✓
        for pp in (spec.params or ()):
            if getattr(pp, "default", None) is Ellipsis and pp.name not in vals:
                return False, "★ 缺必填形参：%s" % pp.name
        alias = getattr(spec, "param_alias", None) or {}
        kwargs = {}
        for name, value in vals.items():
            target = alias.get(name, name)
            if target is None:
                continue                       # ★ 解析器消费掉，不传给目标函数 ✓
            kwargs[target] = value
        derived = getattr(spec, "derived_args", None)
        if callable(derived):
            import types as _types
            try:
                extra = derived(_types.SimpleNamespace(**vals)) or {}
                kwargs.update(extra)
            except Exception as exc:                                    # noqa: BLE001
                return False, "★ derived_args 抛 %s: %s" % (type(exc).__name__, str(exc)[:80])
        if inject:
            obj = (inject_objects or {}).get(inject)
            if obj is None:
                return False, "★ 声明注入 %r 但没给对应对象" % inject
            kwargs[inject] = obj
        #: ★★★★ 2026-10-12 **补 `pre_call`**（★ 阶段 1 真机验收抓到的真缺陷）：
        #:   ★ 本仓有 **16 个**工具声明了 `pre_call=<fn>` —— 那是**声明式选择器**的解析钩子
        #:     （例：`solidworks_chamfer` 的 `pre_call=_select_edge` ⇒ 把 `selection="index:0"`
        #:      解析成真的把那条边选中，因为官方 API **不收边对象、只认当前选择**）。
        #:   ★★ 而本函数**从来没跑过它**（`'pre_call' in 源码` = **False**）⇒
        #:     ★ 真机后果：`chamfer` 收到 `selection="index:0"` 却**没有选中任何东西**
        #:     ⇒ `InsertFeatureChamfer` 回 `None` ⇒ **倒角没建出来**（体积 120000 = W×H×D，零损耗）。
        #:   ⇒ ★ 修法：**在注入宿主之后、调用目标函数之前**跑 `pre_call`；
        #:     ★ 它抛异常 ⇒ **不静默**，如实带回（★ 前置没上就报错，不装作"建不出来"）。
        pre = getattr(spec, "pre_call", None)
        if callable(pre):
            import types as _t2
            try:
                #: ★★ 实测（2026-10-12）：`pre_call` 的真实签名是 **`pre_call(params)`**，
                #:   收一个**命名空间**（不是 kwargs）—— 例：
                #:   `def _select_edge(params): return resolve_selection(_model(), params.selection, "EDGE")`
                #:   ⇒ ★ 必须传 `SimpleNamespace(**vals)`（★ 与 `derived_args` 同一形状）。
                pre(_t2.SimpleNamespace(**vals))
            except Exception as exc:                                    # noqa: BLE001
                return False, "★ pre_call（声明式选择器解析）抛 %s: %s" % (
                    type(exc).__name__, str(exc)[:120])
        #: ★★ 声明里的形参**未必都被底层函数接受** —— ★ 真机实测：`solidworks_extrude_boss`
        #:   ★ 抛 `TypeError: extrude_boss() got an unexpected keyword argument '...'` ⇒
        #:   ★★ 说明**注册器另有一套映射**（`param_alias` / `derived_args` / `omitted_params`）✓
        #:   ⇒ ★ 本函数只做**朴素投影**：★ 按底层函数的真实签名**过滤**掉它不接的那些，
        #:     ★★ 并把被丢掉的形参名**如实带回**（★ 那是一条「声明与实现不一致」的线索，不许吞掉）✓
        try:
            import inspect as _ins
            allowed = set(_ins.signature(fn).parameters)
            dropped = sorted(k for k in kwargs if k not in allowed)
            kwargs = {k: v for k, v in kwargs.items() if k in allowed}
        except (TypeError, ValueError):                                  # 内建/无签名
            dropped = []
        r = fn(**kwargs)
        #: ★ 工具层回的是 JSON 字符串（MCP 形状）⇒ ★ 不解释它，只**如实带回开头** ✓
        #: ★★★ 2026-10-06 **真机踩过（一定要记住）**：★ 工具层返回的是 **JSON 字符串**，
        #:   ★ 里面**自带成败** —— ★★ 而"调用没抛异常"**只说明它跑完了**，不说明它做成了 ✗
        #:   ★ 现场：★ 探针调 `extrude_boss` 时**没有先建草图**（`Sketch1` 不存在）⇒
        #:     ★ 工具返回**失败载荷**，★ 而我的 `call()` 报 **`写操作 成功`** ⇒
        #:     ★★ 于是**指纹没动**被记成 `not_detected`（= "这一类不可见"）✗✗
        #:   ★★ 那正是本规格**最不许**发生的假结论（★ 与「选不上当成能力不行」同族）✓
        #:   ⇒ ★ 修法：★ **解析返回体**，★ 只看**它自己说的成败** ✓
        text = str(r)
        payload_ok = None
        try:
            import json as _json
            obj = _json.loads(text)
            if isinstance(obj, dict):
                for key in ("ok", "success", "succeeded"):
                    if isinstance(obj.get(key), bool):
                        payload_ok = obj[key]
                        break
                if payload_ok is None and (obj.get("error") or obj.get("errors")):
                    payload_ok = False
        except Exception:                                               # noqa: BLE001
            payload_ok = None
        #: ★★★★ 2026-10-12 **修一个真缺陷**（★ 阶段 1 真机验收抓到的）：
        #:   ★ 原实现 `return True, note`，而 `note = text[:160]` ——
        #:   ⇒ ★★ **调用方永远拿不到完整返回体**（只拿到前 160 字符）！
        #:   ★ 真机后果：`solidworks_part_mass_properties` 回的 dict 有 ~200 字符
        #:     ⇒ 被截在 `'mass': 0.01600` 处 ⇒ `literal_eval` 报
        #:     `SyntaxError: unterminated string literal` ⇒ **体积永远读不到**。
        #:   ⇒ ★ 修法：**返回完整 `text`**；`note` 只用于**错误消息**（★ 那里截断是对的）。
        #:   ⚠ 这是「**返回体被截断**」这一类，★ 与「返回值不可信」（事实 8）**不同**：
        #:     那个说的是 bool 不可信，这个是**载荷被丢掉了**。
        note = text[:160]
        if dropped:
            note += "  ★（声明里有但底层不接的形参：%s）" % "、".join(dropped)
        if payload_ok is False:
            #: ★ 工具**跑完了但说自己没成** ⇒ ★ 这**不是**"这一类不可见"，★ 而是"没调成" ✓
            return False, "★ 工具返回体说失败：%s" % note[:140]
        return True, text
    except Exception as exc:                                            # noqa: BLE001
        return False, "★ 调用抛 %s: %s" % (type(exc).__name__, str(exc)[:120])
