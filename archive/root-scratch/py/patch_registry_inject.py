"""给 tool_registry.py 加 `inject` 字段（注入语义建模）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁脚本，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_registry_inject.py
# 定位:   `docs/T-011-expose-capabilities-assessment.md` §8.4「注入语义建模」的落地。
# 官方签名依据: 不适用（纯 Python 文本补丁）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删（保留是为留下「怎么改的」的痕迹）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REG = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_registry.py")

OLD_DOC = "    :param needs_model: 该函数是否需要一个「活动文档」参数（注册器注入）。"
NEW_DOC = """    :param inject: **注入哪种宿主对象**（注册器负责造并把它作为实参传进去；空串 = 不注入）。
        取值由**调用方注册的解析器**决定 —— 本模块**不硬编码任何宿主 API**，
        因此可独立测试（见 `tests/test_tool_registry.py` 的假宿主）。
        约定俗成的四个：``""`` / ``"model"``（活动文档）/ ``"sw_app"``（ISldWorks）/
        ``"study"``（按 ``study_name`` 入参解析）。
        ⚠ 注入用的**关键字名**必须与目标函数的**真实形参名**一致
        （``model`` / ``sw_app`` / ``study``）。
    :param needs_model: **兼容别名**（等价于 ``inject="model"``）；新声明请直接用 ``inject``。"""

OLD_FIELDS = "    needs_model: bool = False\n    read_only: bool = False"
NEW_FIELDS = '    inject: str = ""\n    needs_model: bool = False\n    read_only: bool = False'

OLD_PROP = '''    @property
    def is_required(self) -> bool:
        return self.required if self.required is not None else self.default is ...
'''

NEW_PROP = '''    @property
    def is_required(self) -> bool:
        return self.required if self.required is not None else self.default is ...


def _effective_inject(spec: "ToolSpec") -> str:
    """把 ``inject`` 与兼容别名 ``needs_model`` 归一成一个字符串。

    ⚠ 两者都给且冲突 ⇒ 抛 :class:`GateError`（**不静默取其一**）。
    """
    if spec.inject and spec.needs_model:
        raise GateError(
            "工具 %r 同时给了 inject=%r 与 needs_model=True —— 二者等价，只留一个"
            % (spec.name, spec.inject)
        )
    if spec.inject:
        return spec.inject
    return "model" if spec.needs_model else ""
'''

OLD_BODY_CHECK = "    if not (spec.extra_op or (spec.module and spec.function)):"
NEW_BODY_CHECK = '''    inj = _effective_inject(spec)
    if inj and not inj.isidentifier():
        raise GateError("工具 %r 的 inject=%r 不是合法标识符" % (spec.name, inj))
    if inj and spec.extra_op is not None:
        raise GateError(
            "工具 %r 同时给了 inject=%r 与 extra_op —— extra_op 自己负责注入，二者互斥"
            % (spec.name, inj)
        )
    if not (spec.extra_op or (spec.module and spec.function)):'''

# make_tool_function：把 needs_model 分支换成通用注入
OLD_MAKE = '''    def _impl(params: Any) -> str:  # noqa: ANN401
        def op():
            kwargs = {p.name: getattr(params, p.name) for p in spec.params}
            if spec.needs_model:
                if resolve_model is None:
                    raise RuntimeError(
                        "工具 %r 声明了 needs_model 但注册时没给 resolve_model" % spec.name
                    )
                kwargs["model"] = resolve_model()
            if spec.extra_op is not None:
                return spec.extra_op(params)
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            return getattr(mod, spec.function)(**kwargs)

        return run_locked(op, params.response_format,
                          load_automation=spec.load_automation)
'''
NEW_MAKE = '''    def _impl(params: Any) -> str:  # noqa: ANN401
        def op():
            kwargs = {p.name: getattr(params, p.name) for p in spec.params}
            inj = _effective_inject(spec)
            if inj:
                resolver = (resolvers or {}).get(inj)
                if resolver is None:
                    raise RuntimeError(
                        "工具 %r 声明了 inject=%r，但注册时没给对应的解析器"
                        "（已给的：%r）" % (spec.name, inj, sorted((resolvers or {}).keys()))
                    )
                kwargs[inject_as or inj] = resolver(params)
            if spec.extra_op is not None:
                return spec.extra_op(params)
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            return getattr(mod, spec.function)(**kwargs)

        return run_locked(op, params.response_format,
                          load_automation=spec.load_automation)
'''

OLD_MAKE_SIG = '''def make_tool_function(spec: ToolSpec, input_model: type, run_locked: Callable[..., str],
                       resolve_model: Optional[Callable[[], Any]] = None) -> Callable[..., str]:'''
NEW_MAKE_SIG = '''def make_tool_function(spec: ToolSpec, input_model: type, run_locked: Callable[..., str],
                       resolve_model: Optional[Callable[[], Any]] = None,
                       resolvers: Optional[dict[str, Callable[[Any], Any]]] = None,
                       inject_as: Optional[str] = None) -> Callable[..., str]:'''

OLD_REG_SIG = '''def register(mcp: Any, specs: list[ToolSpec], base: type, response_enum: Any,
             run_locked: Callable[..., str],
             resolve_model: Optional[Callable[[], Any]] = None) -> list[str]:'''
NEW_REG_SIG = '''def register(mcp: Any, specs: list[ToolSpec], base: type, response_enum: Any,
             run_locked: Callable[..., str],
             resolve_model: Optional[Callable[[], Any]] = None,
             resolvers: Optional[dict[str, Callable[[Any], Any]]] = None) -> list[str]:'''

OLD_REG_CALL = "        fn = make_tool_function(spec, model, run_locked, resolve_model)"
NEW_REG_CALL = "        fn = make_tool_function(spec, model, run_locked, resolve_model, resolvers)"

OLD_REG_DOC = '''    先 `check_specs` 全量校验 —— **有任何问题就整体不注册**（不让半套工具进到运行期）。
    """'''
NEW_REG_DOC = '''    先 `check_specs` 全量校验 —— **有任何问题就整体不注册**（不让半套工具进到运行期）。

    :param resolvers: 注入解析器表：``{注入名: (params) -> 宿主对象}``。
        **由调用方提供** ⇒ 本模块保持宿主无关（其自测用假宿主）。
        典型：``{"model": lambda p: active_doc(), "sw_app": lambda p: sw(),
                 "study": lambda p: study_by_name(sw(), p.study_name)}``。
        兼容：只给 ``resolve_model`` 时等价于 ``{"model": lambda p: resolve_model()}``。
    """'''
NEW_REG_BODY = '''    if resolvers is None and resolve_model is not None:
        resolvers = {"model": lambda _p: resolve_model()}
'''

OLD_EXPORTS = '''__all__ = [
    "Param",
    "ToolSpec",
    "GateError",
    "check_spec",
    "check_specs",
    "build_input_model",
    "make_tool_function",
    "register",
    "SOLIDWORKS_NAME_RE",
    "CADSTUDIO_NAME_RE",
]'''
NEW_EXPORTS = '''__all__ = [
    "Param",
    "ToolSpec",
    "GateError",
    "check_spec",
    "check_specs",
    "build_input_model",
    "make_tool_function",
    "register",
    "effective_inject",
    "SOLIDWORKS_NAME_RE",
    "CADSTUDIO_NAME_RE",
]'''


def main() -> int:
    text = REG.read_text(encoding="utf-8")
    edits = [
        ("doc(needs_model→inject)", OLD_DOC, NEW_DOC),
        ("fields(+inject)", OLD_FIELDS, NEW_FIELDS),
        ("property(_effective_inject)", OLD_PROP, NEW_PROP),
        ("check_spec(inject 校验)", OLD_BODY_CHECK, NEW_BODY_CHECK),
        ("make_tool_function(签名)", OLD_MAKE_SIG, NEW_MAKE_SIG),
        ("make_tool_function(体)", OLD_MAKE, NEW_MAKE),
        ("register(签名)", OLD_REG_SIG, NEW_REG_SIG),
        ("register(doc)", OLD_REG_DOC, NEW_REG_DOC),
        ("register(体)", '    problems = check_specs(specs)',
         '    if resolvers is None and resolve_model is not None:\n'
         '        resolvers = {"model": lambda _p: resolve_model()}\n\n'
         '    problems = check_specs(specs)'),
        ("register(调用)", OLD_REG_CALL, NEW_REG_CALL),
        ("__all__(+effective_inject)", OLD_EXPORTS, NEW_EXPORTS),
    ]
    missed = []
    for label, old, new in edits:
        if old not in text:
            missed.append(label)
            continue
        text = text.replace(old, new, 1)
        print("  ✓ %s" % label)
    # 把 _effective_inject 暴露成公开名（测试要直接调）
    text = text.replace(
        "def _effective_inject(spec: \"ToolSpec\") -> str:",
        "def effective_inject(spec: \"ToolSpec\") -> str:", 1)
    text = text.replace("'\"effective_inject\",'", "'\"effective_inject\",'")
    # 内部引用同步
    text = text.replace("inj = _effective_inject(spec)", "inj = effective_inject(spec)")
    REG.write_text(text, encoding="utf-8")
    if missed:
        print("  ✗ 未匹配：%r" % missed)
        return 1
    print("  ⇒ 全部命中")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
