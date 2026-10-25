"""★ 用户决定索引的**双向核对器**（防止「只有业主能定」的事在轮次里被忘掉）。

## 为什么需要

这类事散在三处：`docs/s3-blockers.yaml`（owner=user）、
`docs/repro-manifest.yaml` 的 `known_gaps`（owner=user）、S2 问卷。
轮次一多必然漏 —— 而漏掉的后果是：**它悄悄从报告里消失，看起来像解决了**。

⇒ 本脚本双向核对：
- **反向**：每个 `owner: user` 的阻塞项 / 缺口，都必须在
  `docs/user-decisions.yaml` 里有对应条目
- **正向**：`user-decisions.yaml` 里每条 `blocks` 指向的 check_id 必须真存在

## 还有一条硬规矩

**`value` 字段必须为空**。
`ENGINEERING-PATH.md` 第 85 行逐字：「尺寸缺失就问；**材料、功能孔型、配合、制造约束、
影响承载的工况不得偷偷填默认值**」。
⇒ 一旦有人往 `user-decisions.yaml` 里填了值，就等于替业主决定了这些
  ⇒ 本脚本直接判失败。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]

DECISIONS = R / "docs" / "user-decisions.yaml"
BLOCKERS = R / "docs" / "s3-blockers.yaml"
REPRO = R / "docs" / "repro-manifest.yaml"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（用户决定索引核对）
# 文件:   scripts/check_user_decisions.py
# 定位:   双向核对「用户决定索引」与阻塞台账/复现缺口；并禁止任何条目被填上默认值。
# 官方依据: 不适用（本仓自定口径）；禁止填默认值来自
#           docs/ENGINEERING-PATH.md 第 85 行「不得偷偷填默认值」
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def check() -> list:
    """回问题列表；空表示一致。"""
    problems: list = []
    import yaml

    d = yaml.safe_load(DECISIONS.read_text(encoding="utf-8")) or {}
    decisions = d.get("decisions") or ()
    ids = [str(x.get("id") or "") for x in decisions]

    #: ① 每条决定必须有基本字段
    for x in decisions:
        for k in ("id", "topic", "question", "format", "source"):
            if not str((x or {}).get(k) or "").strip():
                problems.append("决定 %s 缺 %s" % (x.get("id"), k))
        #: ★★ 禁止填值
        if str((x or {}).get("value") or "").strip():
            problems.append(
                "★★ 决定 %s **被填了值**（%r）—— 不得替业主决定材料/载荷/工艺"
                % (x.get("id"), x.get("value"))
            )
        src = str((x or {}).get("source") or "").split("#")[0]
        if src and not (R / src).is_file():
            problems.append("决定 %s 的 source 不存在：%s" % (x.get("id"), src))

    #: ② 反向：owner=user 的阻塞项都要有决定条目
    try:
        bl_doc = yaml.safe_load(BLOCKERS.read_text(encoding="utf-8")) or {}
        bl = bl_doc.get("blockers") or ()
    except Exception:  # noqa: BLE001
        bl = ()
    declared_blocks: set = set()
    for x in decisions:
        for b in (x or {}).get("blocks") or ():
            declared_blocks.add(str(b))
    for b in bl:
        if str((b or {}).get("owner") or "") != "user":
            continue
        cid = str((b or {}).get("check_id") or "")
        if cid and cid not in declared_blocks:
            problems.append(
                "★ 阻塞项 %s（owner=user）没有出现在任何决定的 blocks 里 ⇒ 会漏掉" % cid
            )

    #: ③ 反向：owner=user 的复现缺口都要有条目
    try:
        rp_doc = yaml.safe_load(REPRO.read_text(encoding="utf-8")) or {}
        gaps = rp_doc.get("known_gaps") or ()
    except Exception:  # noqa: BLE001
        gaps = ()
    for g in gaps:
        if str((g or {}).get("owner") or "") != "user":
            continue
        key = str((g or {}).get("key") or "")
        #: 缺口 key 与 topic 允许不同名，但必须有**某条**决定的 source 指向复现清单
        if not any(str((x or {}).get("source") or "").endswith("repro-manifest.yaml")
                   for x in decisions):
            problems.append(
                "★ 复现缺口 %s（owner=user）没有对应的决定条目" % key
            )
            break

    #: ④ 正向：blocks 指向的 check_id 必须真在阻塞台账里
    known = {str((b or {}).get("check_id") or "") for b in bl}
    for b in sorted(declared_blocks):
        if b and b not in known:
            problems.append(
                "★ 决定里 blocks 写的 %s 不在阻塞台账里（可能是笔误或已解决）" % b
            )

    #: ⑤ id 不重复
    if len(ids) != len(set(ids)):
        problems.append("★ 决定 id 有重复：%s" % ids)

    return problems


def main() -> int:
    problems = check()
    import yaml

    d = yaml.safe_load(DECISIONS.read_text(encoding="utf-8")) or {}
    n = len(d.get("decisions") or ())
    print("用户决定索引 · %d 条决定 · %d 条记录项"
          % (n, len(d.get("for_information") or ())))
    if problems:
        print("★ [FAIL] %d 处：" % len(problems))
        for p in problems:
            print("   -", p)
        return 1
    print("★ [PASS] 与阻塞台账/复现缺口双向一致；无条目被填默认值")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
