"""L4 · 个人化档案：把「某个人的习惯」变成数据，生成器读它来决定**默认值**。

## 业主的要求（2026-10-26）

> 不同的人建模画图或者做装配，有不同的习惯……这个示教器就可以让他把一些习惯变成数据，
> 然后给他的 agent 用，让他的 agent 去调整。我们这个项目的实现方式就可以更加私人化。

## 边界（写死在代码里）

- 档案只写**默认值/偏好**，**不写能力**（能力在 `capabilities.yaml`，两者不许混）。
- 缺省值来自 `DEFAULT_HABITS`；档案**只覆盖**自己写的键。
- 未知键 ⇒ **报错**，不静默忽略（否则用户以为设了、其实没生效）。
- 单位一律写进键名（`*_mm`），与本仓 §十四之二 一致。

## 目录

```
profiles/
  <profile-id>/
    habits.yaml
```
其中 `<profile-id>` 只能是 `[a-z0-9_-]+`（防路径穿越）。
"""
from __future__ import annotations

import os
import re
from pathlib import Path

#: 允许的键 ⇒ 默认值（**唯一权威**；未知键一律报错）
DEFAULT_HABITS = {
    #: 孔标准：国内出图用 GB
    "hole_standard": "GB",
    #: 孔紧固类型
    "hole_fastener": "螺钉间隙",
    #: 默认孔规格
    "hole_size": "M6",
    #: M6 中等装配通孔直径（GB/T 5277-1985 ≡ ISO 273:1979）
    "hole_diameter_mm": 6.6,
    #: 孔位约束风格：to_edge（点到边，示范的做法）| points_plus_fixed
    "dimension_style": "to_edge",
    #: 优先用阵列而不是多点（若实现支持）
    "prefer_pattern_over_points": False,
    #: 保存时是否顺带存一份 step
    "export_step": False,
}

#: profile id 白名单（防穿越）
_ID_RE = re.compile(r"^[a-z0-9_-]{1,64}$")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（示教器 L4 · 个人化档案）
# 文件:   scripts/sw_habits.py
# 定位:   读写 `profiles/<id>/habits.yaml`，把个人习惯变成**默认值**注入生成器。
#          业主 2026-10-26：让每个人的习惯成为数据，agent 按它调整。
# 官方依据: 不适用（本仓自身数据格式）；默认值中 GB/螺钉间隙/M6/6.6mm 有出处 ——
#          `GB/T 5277-1985`（等同采用 ISO 273:1979）M6 中等装配通孔 6.6 mm；
#          SolidWorks 标准索引 13=GB / 紧固 356=螺钉间隙（真机扫描命中，见已知事实 585）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


class HabitsError(ValueError):
    """档案不合法（未知键、id 非法等）—— 一律**抛**。"""


def profiles_root() -> Path:
    """档案根目录（可用环境变量覆盖，便于测试）。"""
    env = os.environ.get("SW_PROFILES_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[1] / "profiles"


def check_id(profile_id: str) -> str:
    if not _ID_RE.match(str(profile_id or "")):
        raise HabitsError(
            "profile id 只允许 [a-z0-9_-]，1~64 字：%r" % (profile_id,))
    return profile_id


def habits_path(profile_id: str) -> Path:
    return profiles_root() / check_id(profile_id) / "habits.yaml"


def validate(habits: dict) -> list:
    """校验，回问题清单（空 = 合法）。"""
    if not isinstance(habits, dict):
        return ["档案必须是映射（dict）"]
    unknown = [k for k in habits if k not in DEFAULT_HABITS]
    if unknown:
        return ["未知键（写错就等于没设）：%s；允许的键：%s"
                % (unknown, sorted(DEFAULT_HABITS))]
    bad_type = []
    for k, v in habits.items():
        ref = DEFAULT_HABITS[k]
        if isinstance(ref, bool) and not isinstance(v, bool):
            bad_type.append("%s 应为 bool，给的是 %r" % (k, v))
        elif isinstance(ref, float) and not isinstance(v, (int, float)):
            bad_type.append("%s 应为数字，给的是 %r" % (k, v))
    return bad_type


def load(profile_id: str) -> dict:
    """读某人的档案（不存在 ⇒ 全默认）。未知键/类型错 ⇒ 抛。"""
    p = habits_path(profile_id)
    if not p.is_file():
        return dict(DEFAULT_HABITS)
    from sw_recipe import _mini_yaml_load

    data = _mini_yaml_load(p.read_text(encoding="utf-8"))
    problems = validate(data)
    if problems:
        raise HabitsError("档案不合法（%s）：\n  - %s"
                          % (p, "\n  - ".join(problems)))
    merged = dict(DEFAULT_HABITS)
    merged.update(data)
    return merged


def save(profile_id: str, habits: dict) -> Path:
    """写档案（先校验）。"""
    problems = validate(habits)
    if problems:
        raise HabitsError("档案不合法：\n  - " + "\n  - ".join(problems))
    from sw_recipe import _mini_yaml_dump

    p = habits_path(profile_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    body = ("# 个人化档案（L4）：只写默认值/偏好，不写能力。\n"
            + _mini_yaml_dump(habits) + "\n")
    p.write_text(body, encoding="utf-8", newline="\n")
    return p


def apply_to_recipe(recipe: dict, habits: dict) -> dict:
    """把档案的默认值**填进配方里空着的**字段（不覆盖配方已写的值）。"""
    out = dict(recipe)
    inputs = dict(out.get("inputs") or {})
    hole = dict(inputs.get("hole") or {})
    mapping = {
        "standard": habits.get("hole_standard"),
        "fastener": habits.get("hole_fastener"),
        "size": habits.get("hole_size"),
        "diameter_mm": habits.get("hole_diameter_mm"),
    }
    for key, val in mapping.items():
        if hole.get(key) in (None, "") and val is not None:
            hole[key] = val
    inputs["hole"] = hole
    out["inputs"] = inputs
    hints = dict(out.get("hints") or {})
    if not hints.get("dimension_style"):
        hints["dimension_style"] = habits.get("dimension_style")
    out["hints"] = hints
    return out
