"""★ 用户偏好守卫：**改 SolidWorks 全局用户偏好之前先记旧值，用完在 `finally` 里还原**。

（★ 交付纪律：别人的 SolidWorks 设置不该被我们留下痕迹 —— 事实 525）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\`）
# 文件:   `C:\swapi\types\ISldWorks\GetUserPreferenceStringValue.md` ·
#         `…/GetUserPreferenceIntegerValue.md` · `…/GetUserPreferenceToggle.md` ·
#         `…/SetUserPreferenceStringValue.md` · `…/SetUserPreferenceIntegerValue.md` ·
#         `…/SetUserPreferenceToggle.md`   （★ 每个都是 1 参 get / 2 参 set）
#         `scripts/sw_connect.py`（`get_com_member` —— ★ 本项目「取或调」的统一入口）
# 定位:   ★★★ **为什么需要它**（★ 2026-10-04 业主体检出的交付问题）：
#   业主问「我们这个项目别人装上，是不是也要改他的 SolidWorks？」——
# ★ 核查结论：**本体零改动**（注册表写入 0 处、不写安装目录、不打补丁、不注入，全走官方
# COM API）；
#   ★★ 而**有一处真落点**：全仓 **8 处 `SetUserPreference*`** 会改用户的**全局用户偏好**
#     （默认模板路径 / 新建提示 / STL 导出质量 / STL-VRML 导入选项 / 原点与三轴显示），
#     且**多数不还原** ⇒ ★ 那等于"装一次我们的工具，用户的 SolidWorks 设置被改掉且回不去" ✓
#   ⇒ ★ 本模块提供**唯一的**写入姿势：**读旧值 → 设 → `finally` 还原**（★ 默认还原）。
#
# ★★★ 三条设计约束（★ 与仓内既有纪律一致，★ 每条都有反面教训）：
#   ① **默认还原**；★ 想"留下设置"必须**显式**用 `keep=`，且**在调用处写明理由**
#      （★ 事实 40：一个存在但默认关掉的守卫，与没有守卫等价 —— ★ 故本模块把"写"这条路
#       做成**只有经过 guard 才安全**，并另配门禁 `check_user_preference_writes.py`）✓
#   ② **还原失败要可见**：★ 不吞异常 —— 报告里带 `restore_errors`，
#      且★ **一次都没改过的偏好不写回**（★ 免得把"本来就没动"变成"动了一下"）✓
#   ③ **只碰声明的偏好号**：★ 不做"整表快照回写"（★ 那会覆盖用户在别处刚做的改动）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO / "scripts"))

#: ★ 官方偏好号的取值集合见 `C:\swapi\enums\swUserPreference*_e.md`；
#: ★ 本模块**不硬编码任何偏好号** —— 号由调用方给（★ 号写错 = 改错设置，故要显式、要可 g
#: rep）✓
KINDS = ("string", "integer", "toggle", "double")
_GET = {
    "string": "GetUserPreferenceStringValue",
    "integer": "GetUserPreferenceIntegerValue",
    "toggle": "GetUserPreferenceToggle",
    "double": "GetUserPreferenceDoubleValue",
}
_SET = {
    "string": "SetUserPreferenceStringValue",
    "integer": "SetUserPreferenceIntegerValue",
    "toggle": "SetUserPreferenceToggle",
    "double": "SetUserPreferenceDoubleValue",
}


@dataclass(frozen=True)
class Preference:
    """★ 一条"我们想临时设成这个值"的偏好。`why` 要写清**为什么这条要改**。"""

    kind: str
    pref_id: int
    value: Any
    why: str = ""

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(
                "kind 必须是 %s 之一（收到 %r）" % ("/".join(KINDS), self.kind)
            )


@dataclass
class GuardReport:
    """★ 守卫的完整交代：改了什么、还回去了没有、有没有出错。"""

    changed: list[dict] = field(default_factory=list)
    restored: list[dict] = field(default_factory=list)
    kept: list[dict] = field(default_factory=list)
    read_errors: list[dict] = field(default_factory=list)
    set_errors: list[dict] = field(default_factory=list)
    restore_errors: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        out = {
            "ok": not (self.restore_errors or self.read_errors or self.set_errors),
            "changed_count": len(self.changed),
            "restored_count": len(self.restored),
            "kept_count": len(self.kept),
            "changed": self.changed,
            "restored": self.restored,
            "kept": self.kept,
            "read_errors": self.read_errors,
            "set_errors": self.set_errors,
            "restore_errors": self.restore_errors,
            "★": "★ 默认**全部还原**；`kept` 非空 ⇒ 调用方**显式**要求留下（须有理由）",
        }
        return out


#: dispatch-guard: exempt internal-helper
def _member(obj, name: str, *args):
    """★ 走本仓统一的 `get_com_member`（★ 有实参 ⇒ 一定**调用**）。"""
    from sw_connect import get_com_member

    return get_com_member(obj, name, *args)


def read_preference(sw_app, kind: str, pref_id: int) -> Any:
    """读一条偏好（★ 读不到 ⇒ 抛，由调用方决定是否只记不判）。"""
    if kind not in KINDS:
        raise ValueError("kind 必须是 %s 之一（收到 %r）" % ("/".join(KINDS), kind))
    return _member(sw_app, _GET[kind], int(pref_id))


def write_preference(sw_app, kind: str, pref_id: int, value: Any):
    """写一条偏好（★ 只在 guard 内使用；★ 门禁会扫"有没有人绕过 guard 直接写"）。"""
    if kind not in KINDS:
        raise ValueError("kind 必须是 %s 之一（收到 %r）" % ("/".join(KINDS), kind))
    return _member(sw_app, _SET[kind], int(pref_id), value)


def _same(kind: str, a: Any, b: Any) -> bool:
    """★ 比较时**按 kind 归一**（★ 字符串路径**大小写不敏感**、toggle 归 bool）。"""
    if kind == "string":
        return str(a or "").lower() == str(b or "").lower()
    if kind == "toggle":
        return bool(a) == bool(b)
    try:
        return float(a) == float(b)
    except (TypeError, ValueError):
        return a == b


@contextmanager
def preference_guard(
    sw_app,
    preferences: Iterable[Preference],
    *,
    restore: bool = True,
    keep: Iterable[int] = (),
):
    """★ **改全局用户偏好的唯一安全姿势**：读旧值 → 设 → `finally` 还原。

    :param preferences: 想临时设成哪些值（每次现给，★ 不做整表快照）。
    :param restore: ★ **默认 True**（用完还原）；`False` 会被门禁要求写明理由。
    :param keep: 故意**留下**的偏好号（★ 只有传了它们才不还原；`report.kept` 会记下来）。
    :yields: `GuardReport` —— ★ 退出上下文后可以用它核对（★ 调用方**不要**吞掉 `restore_errors`）。
    """
    keep_set = {int(k) for k in keep}
    rep = GuardReport()
    old: dict[int, tuple[str, Any]] = {}

    #: ① 记旧值 —— ★★ **连 `keep` 的那些也要读**（★ 报告要能说出"留下了什么"），
    #: 这正是本模块**第一版**的 bug：`keep` 跳过读 ⇒ `kept` 分支永不触发、报告里旧值是 `
    #: None`。
    for pref in preferences:
        try:
            old[int(pref.pref_id)] = (
                pref.kind,
                read_preference(sw_app, pref.kind, pref.pref_id),
            )
        except Exception as exc:  # noqa: BLE001
            rep.read_errors.append(
                {
                    "pref_id": int(pref.pref_id),
                    "kind": pref.kind,
                    "error": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
                }
            )
    #: ② 设新值
    #:   ★★ **读不到旧值的，一律不写** —— ★ 否则那条设置**永远回不去**
    #:   （★ 这是本模块**第二版**补的：第一版会照写，而"读不到"恰恰是最需要保守的情形）✓
    for pref in preferences:
        pid = int(pref.pref_id)
        if pid not in old:
            continue
        if _same(pref.kind, old[pid][1], pref.value):
            continue  # ★ 值没变 ⇒ 不写（不制造历史）
        try:
            write_preference(sw_app, pref.kind, pid, pref.value)
            rep.changed.append(
                {
                    "pref_id": pid,
                    "kind": pref.kind,
                    "value": pref.value,
                    "old": old[pid][1],
                    "why": pref.why,
                }
            )
        except Exception as exc:  # noqa: BLE001
            rep.set_errors.append(
                {
                    "pref_id": pid,
                    "kind": pref.kind,
                    "value": pref.value,
                    "error": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
                }
            )
    try:
        yield rep
    finally:
        #: ③ 还原（★ `finally` ⇒ 连异常路径也还原）
        changed_ids = {int(c["pref_id"]) for c in rep.changed}
        for pid, (kind, value) in old.items():
            if pid in keep_set:
                rep.kept.append(
                    {
                        "pref_id": pid,
                        "kind": kind,
                        "value": value,
                        "note": "★ 调用方显式 keep ⇒ 故意不还",
                    }
                )
                continue
            if pid not in changed_ids:
                continue  # ★ 没改过就不写回
            if not restore:
                rep.kept.append(
                    {
                        "pref_id": pid,
                        "kind": kind,
                        "value": value,
                        "note": "★ restore=False ⇒ 故意不还",
                    }
                )
                continue
            try:
                write_preference(sw_app, kind, pid, value)
                back = read_preference(sw_app, kind, pid)
                rep.restored.append(
                    {
                        "pref_id": pid,
                        "kind": kind,
                        "value": value,
                        "readback": back,
                        "match": _same(kind, back, value),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                rep.restore_errors.append(
                    {
                        "pref_id": pid,
                        "kind": kind,
                        "value": value,
                        "error": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
                    }
                )


__all__ = [
    "KINDS",
    "Preference",
    "GuardReport",
    "preference_guard",
    "read_preference",
    "write_preference",
]
