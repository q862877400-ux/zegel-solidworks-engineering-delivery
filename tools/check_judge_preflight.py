"""★ 判据前置检查：凡"用某个回读去判某条能力"的判据，必须**先在已知成功场景上被验过**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/check_judge_preflight.py
# 定位:   ★ 2026-10-03（轮 420）24h 计划 v2 收敛报告 §五「下一步」与
#   `specs/150-judge-first-rollout/spec.md` 的 **T0.2** 的落地。
#   ★★ **为什么有它**（★ 而这是上一轮**用五次事故换来的**）：★ 五次出现同一形态 ——
#     ★ **能力好好的，而它看起来坏了**，而**每一次的错都在"判据"**：
#     ```
#     ① 轮 400 判据（**选区**）不干净          ② 轮 402 判据的前提（**算例类型**）错
#     ③ 轮 414 判据的前提（**算例名**）错       ④ 轮 415 判据的**名单本身**不全
#     ⑤ 轮 417–419 判据**在这条路上间歇性不稳**
#     ```
#     ⇒ ★★ **命题：判据本身也是被测对象** —— ★ 它必须**先被验过**，★ 才能拿去判别人。
#   ★★★ 而"先找后搓"（作业单 §五）已核：★ **本仓与四家 MIT 克隆都没有**现成实现
#     ⇒ ★ 本工具是**自己搓的**（★ 也因此是**我们自己的**一块）。
#   ★★ 判据的形态（★ 本工具定义的）：★ **`docs/judge-registry.json` 是一张显式登记表** ——
# 每条记「判据是什么 / 它实现在哪 / 它的**已知成功场景** / 那份 evidence / 它在哪条路上*
# *不可用**」。
# 官方依据: 不适用（本仓自有的判据纪律 —— 事实 320 / 323 / 329 / 330 / 332 / 333 / 334）
#           。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 登记表**每条都完整**（id / what / where / 已知成功场景 / evidence 存在且 ver
# dict=pass /
#   usable_on 或 unusable_on 至少一项）★ 且**已知成功场景的文件真的存在**。
# ⚠ 便携性：★ 拿不到工作区（`DSL_WORKSPACE` / 默认 `D:\\AI\\SW`）⇒ **[SKIP] 并 exit 0**
# 。

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

#: ★★★ 2026-10-03（接手轮）**必须强制 stdout 为 UTF-8** —— ★ 本工具会 `print` 中文，
#: 而默认走 `locale.getpreferredencoding()`（★ 本机是 **GBK**）⇒ ★ 被父进程按 UTF-8 解时
#: **全是乱码**。
#:   ★★ 实测后果：`tests/test_judge_preflight_gate.py` 的 **5 条**全失败 ——
#:     `assert "缺字段" in proc.stdout` 拿到的是 `'\ufffd\u043e\u0775\u01fc…'`
#: （★ 而那个测试**自己的** `subprocess.run` **是**带 `encoding="utf-8"` 的 ⇒ 错不在它）
#: 。
#:   ★ 这正是 **known-facts 58** 那一族的**第三个实例**（前两个：测试里的 subprocess、
#:     以及本仓 11 处缺 `encoding=`），★ 而这次的病灶在**子进程的输出侧**，不是解码侧。
sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]
#: ★ 登记表路径可覆盖（`DSL_JUDGE_REGISTRY`）—— ★ 那是**负例自证**的前提：
#:   ★ 测试要能拿一张“**故意坏的**”表去跑（事实 62：一个门禁“写了”不等于它“有效”，
#:   **负例测试是唯一的证明**）。
REGISTRY = Path(
    os.environ.get("DSL_JUDGE_REGISTRY") or (REPO_ROOT / "docs" / "judge-registry.json")
)
WORKSPACE = Path(os.environ.get("DSL_WORKSPACE", Path(__file__).resolve().parents[1]))

#: ★ 每条登记项**必须**有的字段（★ 缺一个就是"没登记清楚"）
#: ★ `judge` 要求有“已知成功场景”；★ `refuted`（**被否掉的假设**）**不**要求它
REQUIRED = ("id", "kind", "what", "where")
REQUIRED_JUDGE = ("known_good_scenario",)


def main(argv: list) -> int:
    if not REGISTRY.is_file():
        print("  [SKIP] 找不到登记表：%s" % REGISTRY)
        return 2
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    judges = data.get("judges") or []
    print("  判据登记表：%d 条（%s）" % (len(judges), REGISTRY.name))
    if not WORKSPACE.is_dir():
        print(
            "  [SKIP] 工作区不可达（%s）⇒ 无法核对 evidence（便携性约定）" % WORKSPACE
        )
        return 0

    bad: list = []
    for j in judges:
        jid = str(j.get("id") or "<无 id>")
        for field in REQUIRED:
            if not str(j.get(field) or "").strip():
                bad.append((jid, "缺字段", field))
        #: ★ 至少要说明"它在哪条路上可用或不可用"—— ★ 否则这条登记没有信息量
        if not (j.get("usable_on") or j.get("unusable_on")):
            bad.append((jid, "缺说明", "usable_on 与 unusable_on 都空"))
        #: ★ evidence **必须真的存在且 verdict=pass**（★ 否则"已知成功"是空话）
        ev_name = str(j.get("evidence") or "")
        if ev_name:
            ev = (
                WORKSPACE / ev_name
                if not Path(ev_name).is_absolute()
                else Path(ev_name)
            )
            if not ev.is_file():
                bad.append((jid, "evidence 不存在", ev_name))
            else:
                try:
                    v = json.loads(ev.read_text(encoding="utf-8")).get("verdict")
                except Exception as exc:  # noqa: BLE001
                    bad.append(
                        (
                            jid,
                            "evidence 读不了",
                            "%s: %s" % (type(exc).__name__, str(exc)[:60]),
                        )
                    )
                else:
                    kind = str(j.get("kind") or "judge")
                    if kind == "judge" and v != "pass":
                        #: ★ `judge` 的 evidence **必须** pass —— 那才叫“已知成功”
                        bad.append(
                            (
                                jid,
                                "judge 的 evidence 不是 pass",
                                "%s ⇒ %r" % (ev_name, v),
                            )
                        )
                    elif kind == "refuted" and v == "pass":
                        #: ★ `refuted`（被否的假设）的 evidence **不能** pass
                        #:   —— ★ 因为它证的就是“**没成**”
                        bad.append(
                            (
                                jid,
                                "refuted 的 evidence 不该是 pass",
                                "%s ⇒ %r" % (ev_name, v),
                            )
                        )
        #: ★ "已知成功场景"那个**脚本**也要真的在
        scen = str(j.get("known_good_scenario") or "")
        if scen and "/" in scen and not (REPO_ROOT / scen).is_file():
            bad.append((jid, "已知成功场景的脚本不存在", scen))
        #: ★ 只有 **`judge`** 才要求有“已知成功场景”
        #:   （★ `refuted` 记的是**被否掉的假设** —— 它本来就没有）
        if str(j.get("kind") or "judge") == "judge":
            for field in REQUIRED_JUDGE:
                if not str(j.get(field) or "").strip():
                    bad.append((jid, "judge 缺字段", field))

    if bad:
        print("  不合格 **%d** 处：" % len(bad))
        for jid, kind, item in bad[:30]:
            print("    %-38s %-22s %s" % (jid, kind, item))
        print("  ── 判据 ──")
        print(
            "  ★ 凡「用某个回读去判某条能力」的判据，**必须先在已知成功场景上被验过** ——"
        )
        print(
            "  ★ 而「**验过**」的证据就是那条登记的 `evidence`（且它得是 `verdict: pass`）。"
        )
        print(
            "  ★ 依据：上一轮**五次**事故全是「**能力好好的、而它看起来坏了**」，错的都在判据。"
        )
        return 1
    print(
        "  [OK] 登记的 %d 条都完整：★ **judge** 各自的“已知成功场景”证据存在且 `verdict: pass`；★ **refuted**（被否的假设）的证据**如实不是** pass。"
        % len(judges)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
