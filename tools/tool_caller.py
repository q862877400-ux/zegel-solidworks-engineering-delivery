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


def describe(name: str) -> dict:
    """★ 一个工具的**契约摘要**（注入名 · 形参名与是否必需）—— ★ 不调它，只描述 ✓"""
    entry = _specs().get(name)
    if not entry:
        return {"found": False}
    spec, inject = entry
    params = []
    for p in (spec.params or []):
        params.append({"name": p.name, "required": bool(getattr(p, "required", False)),
                       "default": getattr(p, "default", None)})
    return {"found": True, "inject": inject or "", "module": spec.module,
            "function": spec.function, "params": params}


def call(name: str, *, inject_objects=None, **params):
    """★★ 按契约调一个工具 —— 回 `(ok, 说明)` ✓

    :param inject_objects: `{注入名: 宿主对象}`（★ 如 `{"model": model, "sw": sw}`）
    :param params: 形参（★ 名字与声明一致）✓
    """
    entry = _specs().get(name)
    if not entry:
        return False, "★ 工具名不在声明里：%s" % name
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
        kwargs = {}
        for p in (spec.params or []):
            if p.name in params:
                kwargs[p.name] = params[p.name]
            #: ★★ 声明的 `default` 可能是 **`Ellipsis`**（★ 那在本仓约定里表示**必填**，
            #:   ★ 真机实测：`extrude_boss` 的 `sketch_name`/`depth_mm` 就是 `Ellipsis`）⇒
            #:   ★ 把它当**值**传下去是错的 ⇒ ★ **视为未给**，★ 让底层自己的默认值生效，
            #:     ★ 或由底层报"缺参数"（★ 那也算一次**没调成**，记 `untested`）✓
            elif getattr(p, "default", None) is not None and getattr(p, "default", None) is not Ellipsis:
                kwargs[p.name] = p.default
            elif getattr(p, "required", False):
                return False, "★ 缺必需形参：%s" % p.name
        if inject:
            obj = (inject_objects or {}).get(inject)
            if obj is None:
                return False, "★ 声明注入 %r 但没给对应对象" % inject
            kwargs[inject] = obj
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
        note = str(r)[:160]
        if dropped:
            note += "  ★（声明里有但底层不接的形参：%s）" % "、".join(dropped)
        return True, note
    except Exception as exc:                                            # noqa: BLE001
        return False, "★ 调用抛 %s: %s" % (type(exc).__name__, str(exc)[:120])
