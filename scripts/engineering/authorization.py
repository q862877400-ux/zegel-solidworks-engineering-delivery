"""★ 阶段 1 · 公共授权（规格 316 的 C5）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/authorization.py
# 定位:   规格 `specs/316-stage1-parameter-plate` 的 C5（公共授权）。
#           ★★ 实测（2026-10-11）**全仓没有授权器** —— grep `TOOL_NOT_ADMITTED` /
#           `PATH_OUTSIDE_WORKSPACE` / `DOCUMENT_NOT_OWNED` 均 0 命中。
#           ★ 而外部方案的阶段 1 验收要求：
#             「未准入返回 TOOL_NOT_ADMITTED · 路径和文档越权分别返回
#               PATH_OUTSIDE_WORKSPACE、DOCUMENT_NOT_OWNED · **这些负例的 COM 写调用数全部为 0**」
# 官方依据: 不适用（本仓自研治理层）。
#           ★ 路径纪律依据：本仓 AGENTS.md 铁律 3（结构白名单）+ 「只写 output」
#           ★ 文档身份纪律依据：AGENTS.md §十九（回收自己开的资源 · 不删用户数据）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收见 `tools/run_stage1_plate.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import pathlib
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parents[2]

#: ══ 一、封闭码（★ 新增码必须同时加进 `AUTH_CODES`，否则 `assert` 拦下）══
TOOL_NOT_ADMITTED = "TOOL_NOT_ADMITTED"
PATH_OUTSIDE_WORKSPACE = "PATH_OUTSIDE_WORKSPACE"
DOCUMENT_NOT_OWNED = "DOCUMENT_NOT_OWNED"
EFFECT_UNKNOWN = "EFFECT_UNKNOWN"
PLAN_NOT_COMPILED = "PLAN_NOT_COMPILED"

AUTH_CODES = (TOOL_NOT_ADMITTED, PATH_OUTSIDE_WORKSPACE, DOCUMENT_NOT_OWNED,
              EFFECT_UNKNOWN, PLAN_NOT_COMPILED)


@dataclass(frozen=True)
class AuthorizationVerdict:
    ok: bool
    code: str = ""
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.ok:
            assert self.code in AUTH_CODES, "★ 非法授权码：%r" % self.code


#: ══ 二、工作区边界（★ 路径越权的唯一判据）═════════════════════════════
def workspace_root() -> pathlib.Path:
    """★ 允许写盘的范围 = 仓库根（`D:\\AI\\SW`）。"""
    return ROOT.resolve()


def _resolve_no_symlink(p: pathlib.Path) -> pathlib.Path:
    """★ 解析路径**并解开符号链接/junction**（★ 防「用链接绕过前缀检查」）。

    ★★ 为什么不能只判字符串前缀：`..` / 大小写 / UNC / junction / symlink
      都能让「看着在工作区内」的路径实际落在外面。
    """
    try:
        return p.resolve(strict=False)
    except Exception:                                                      # noqa: BLE001
        return p.absolute()


def check_path(path: str | pathlib.Path, *, root: pathlib.Path | None = None) -> AuthorizationVerdict:
    """★ 判一个写盘路径是否在**工作区内**（★ FR-006）。"""
    base = (root or workspace_root()).resolve()
    p = _resolve_no_symlink(pathlib.Path(str(path)))
    try:
        p.relative_to(base)
        return AuthorizationVerdict(True)
    except ValueError:
        return AuthorizationVerdict(
            False, PATH_OUTSIDE_WORKSPACE,
            "★ %s 不在工作区 %s 内（★ 解析后：%s）" % (path, base, p))


#: ══ 三、文档身份（★ 只操作**本任务创建**的文档）══════════════════════
class OwnedDocuments:
    """★ 记录**本任务创建**的文档（★ 判据 = 登记在册，不是看标题）。"""

    def __init__(self) -> None:
        self._owned: set[str] = set()

    def register(self, doc) -> None:
        t = self.title_of(doc)
        if t:
            self._owned.add(t)

    def is_owned(self, doc) -> bool:
        t = self.title_of(doc)
        return bool(t) and t in self._owned

    @staticmethod
    def title_of(doc) -> str:
        """★ 取标题（★ `GetTitle` 是**方法**，必须调用 —— 实测踩过：
        不调用会拿到 bound method，`CloseDoc` 静默失败）。"""
        try:
            t = doc.GetTitle
            return str(t() if callable(t) else t)
        except Exception:                                                  # noqa: BLE001
            return ""

    def check(self, doc) -> AuthorizationVerdict:
        if doc is None:
            return AuthorizationVerdict(False, DOCUMENT_NOT_OWNED, "★ 文档为 None")
        if not self.is_owned(doc):
            return AuthorizationVerdict(
                False, DOCUMENT_NOT_OWNED,
                "★ %r 不在本任务创建的文档清单里（★ 不碰别人的文档）"
                % self.title_of(doc))
        return AuthorizationVerdict(True)


#: ══ 四、工具准入（★ 未准入 ⇒ 拒绝）══════════════════════════════════
def check_tool(canonical_name: str, reg: dict) -> AuthorizationVerdict:
    """★ 判工具能否进入执行集（★ FR-005 + FR-013）。"""
    d = reg.get(canonical_name)
    if d is None:
        return AuthorizationVerdict(
            False, TOOL_NOT_ADMITTED, "★ %s 不在目录里" % canonical_name)
    if d.effect == "unknown":
        return AuthorizationVerdict(
            False, EFFECT_UNKNOWN,
            "★ %s 效应未知（★ I5：未知副作用不得自动执行）" % canonical_name)
    if not d.admitted:
        return AuthorizationVerdict(
            False, TOOL_NOT_ADMITTED,
            "★ %s 未准入：%s" % (canonical_name, d.reject_reason))
    return AuthorizationVerdict(True)


#: ══ 五、计划级授权（★ 一次把整条链查完）══════════════════════════════
def authorize_plan(plan, reg: dict, *, owned: OwnedDocuments | None = None,
                   doc=None, write_paths: tuple = ()) -> AuthorizationVerdict:
    """★ 整计划授权（★ 任一项不过 ⇒ **整计划拒绝**，★ 不执行前半段）。

    ★★ 顺序（★ 便宜的检查在前 —— 但**每一项都要过**）：
      ① 计划必须经编译器（`PLAN_NOT_COMPILED`）—— ★ 防绕过名字解析
      ② 每个步骤的工具准入（`TOOL_NOT_ADMITTED` / `EFFECT_UNKNOWN`）
      ③ 文档身份（`DOCUMENT_NOT_OWNED`）
      ④ 每个写盘路径（`PATH_OUTSIDE_WORKSPACE`）
    """
    #: ① 计划必须编译过（★ 每个 step 都填了 tool）
    steps = getattr(plan, "steps", ()) or ()
    if not steps:
        return AuthorizationVerdict(False, PLAN_NOT_COMPILED, "★ 计划没有步骤")
    for st in steps:
        if not getattr(st, "tool", ""):
            return AuthorizationVerdict(
                False, PLAN_NOT_COMPILED,
                "★ 步骤 %r 的 `tool` 为空 ⇒ 计划没经 `resolve_plan`（★ 防绕过）"
                % getattr(st, "step", "?"))

    #: ② 工具准入
    for st in steps:
        v = check_tool(st.tool, reg)
        if not v.ok:
            return v

    #: ③ 文档身份
    if owned is not None and doc is not None:
        v = owned.check(doc)
        if not v.ok:
            return v

    #: ④ 写盘路径
    for p in write_paths:
        v = check_path(p)
        if not v.ok:
            return v

    return AuthorizationVerdict(True)
