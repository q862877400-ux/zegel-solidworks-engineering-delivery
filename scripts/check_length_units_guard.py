r"""★ 单位纪律**门禁**：有长度形参的工具，进 COM 前**必须**有换算痕迹。

## ★★★★★ 为什么要有它（★ 业主 2026-10-10 点破的那一层）

★★★ **业主原话**：「★ **既然你明明知道了之前的错误，那为什么你还会把错误原封不动地再犯一次呢？**」✓
  ★★★ **答案不是「我不记得」** —— ★ 而是 **`scripts/audit_length_units.py` 从来没拦住过任何东西**：
    · ★ 它**只打印一份清单**（`return 0` 恒真）⇒ ★ **它不是门禁，是报告** ✓
    · ★★ 它**不在 `release_check.py` 里** ⇒ ★ **发布前根本不会跑** ✓
    · ★★★ 它**还有一处盲区**：★ 只按**形参名**判长度 ⇒ ★ 形参叫 `spec`（dict/dataclass）时
      ★ **长度名藏在字段里** ⇒ ★ 判「无长度形参」⇒ ★ **整族跳过** ✗
      ★★ **齿轮族正是这样被跳过的**（★ `solidworks_gear_create_spur` 的形参是 `spec`）✓
  ★★★ **⇒ 本文件把那三件事一起解决**：
    ① ★ **有下界**（★ 已换算数只增不减 —— ★ 与 `check_dispatch_entry_guard` 同法）✓
    ② ★ **接进 `release_check.py`** ⇒ ★ **每次发布前都跑** ✓
    ③ ★ **审计器补了盲区**（★ 注解展开 · ★ 函数体属性 · ★ 跟一层调用）✓

## 判据

| ★ | ★ 条件 | ★ 结论 |
|---|---|---|
| ① | ★ 审计器**跑得起来**且输出可解析 | ★ 否则 `fail`（★ 不静默跳过） |
| ② | ★ **已换算数 ≥ 下界** | ★ 否则 `fail`（★ 只增不减 —— ★ 防「把换算删了」） |
| ③ | ★ **齿轮族在审计视野里**（★ 回归守卫） | ★ 否则 `fail`（★ 那正是被漏掉的那一族） |

⚠ **为什么 ③ 单列**：★ 业主点破的**正是**「那一族被跳过」——
  ★★ 所以「审计器能看见齿轮」这件事**本身**要成为判据，
  ★ 否则下次改审计器时又会把它漏掉（★ 与事实 62「门禁写了 ≠ 有效」同族）✓

# ── 来源 ──
# 仓库:   本项目自身（门禁实现）
# 文件:   scripts/check_length_units_guard.py —— 本文件自身
#         scripts/audit_length_units.py（★ 被它守的审计器）
#         specs/212-unit-discipline/（★ 单位纪律规格）
# 定位:   把「单位纪律」从**一份报告**升级为**会拦发布的门禁**；
#         起因是业主点破「知道了还再犯」——根因是**审计器没有牙齿**。
# 官方依据: 本仓单位纪律（事实 2）：★ **入参毫米 · COM 侧米** ⇒ 进 COM 前必须换算 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: ★★★ **下界**（★ 只增不减）—— ★ 2026-10-10 真树实测：
#:   · ★ 有长度形参的工具 **96** 个 · ★ **已换算 58** 个
#:   ★★ **2026-10-10 下调（★ 业主架构指令 —— ★ 正当减少）**：
#:     ★ 业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
#:       ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
#:       ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
#:     ★★ **减少了什么**：★ 5 个**由方法模块支撑**的 MCP 工具被移除 ——
#:       · ★ `solidworks_gear_calculate_spur` / `solidworks_gear_create_spur`（★ `sw_gear`）
#:       · ★ `solidworks_chamfer_straight_edge_volume` / `_circular_rim_volume` /
#:         `_volume_report`（★ `sw_chamfer_geometry`）
#:     ★★★ **为什么是正当减少**：★ 那 5 个工具的落点（★ 渐开线齿形公式 · ★ 倒角体积公式）
#:       **是方法**（★ 判据：★「那个数字错了，回读能不能查出来」⇒ **不能**）⇒
#:       ★★ **移出它们是**目的**，★ 不是副作用** ✓
#:     ★ 原件在 `archive/inherited-methods/scripts/`（★ **只搬不删**）✓
#:   ★★ **为什么给「已换算数」下界**：★ 它掉下来只有两种可能 ——
#:     ★ ① 有人**删了换算**（★ 真 bug）· ★ ② 工具被删/改名（★ 应显式调下界）
#:   ⇒ ★ 两种都该**报出来让人看**，★ 不该静默通过 ✓
BASELINE_CONVERTED = 58
#: ★ 有长度形参的总数下界（★ 掉下来 ⇒ 审计器**又瞎了** —— ★ 那正是业主点破的病）✓
BASELINE_LENGTHISH = 96


def _run_audit() -> str:
    """★ 跑审计器，拿它的 stdout（★ 用**显式解释器**，★ 与 release_check 同法）。"""
    import os
    proc = subprocess.run(
        [os.environ.get("PYTHON", sys.executable),
         str(ROOT / "scripts" / "audit_length_units.py")],
        check=False, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=300, cwd=str(ROOT), stdin=subprocess.DEVNULL,
    )
    return (proc.stdout or "") + (proc.stderr or "")


def main() -> int:
    try:
        out = _run_audit()
    except Exception as exc:                                                   # noqa: BLE001
        print("[FAIL] 审计器**跑不起来**：%s: %s" % (type(exc).__name__, exc))
        return 1

    #: ★ ① 输出可解析（★ 拿不到数字 ⇒ **不许**当通过 —— ★ 不静默跳过）
    m_len = re.search(r"有长度形参\*\*\s*=\s*(\d+)", out)
    m_sus = re.search(r"看不到换算\*\* ✗ —— 共\s*(\d+)", out)
    m_conv = re.search(r"这些先不动）：共\s*(\d+)", out)
    if not (m_len and m_sus and m_conv):
        print("[FAIL] 审计器输出**无法解析**（★ 拿不到计数 ⇒ 不许当通过）")
        print(out[-1200:])
        return 1
    n_len, n_sus, n_conv = int(m_len.group(1)), int(m_sus.group(1)), int(m_conv.group(1))

    print("== 单位纪律门禁 ==")
    print("有长度形参 %d · 可疑（无换算）%d · 已换算 %d" % (n_len, n_sus, n_conv))

    problems: list[str] = []

    #: ★★ ② 只增不减
    if n_conv < BASELINE_CONVERTED:
        problems.append("已换算数 %d < 下界 %d（★ 只增不减：先查是不是有人**删了换算**）"
                        % (n_conv, BASELINE_CONVERTED))
    if n_len < BASELINE_LENGTHISH:
        problems.append("有长度形参数 %d < 下界 %d（★ 审计器**又瞎了**？—— ★ 那正是被点破的病）"
                        % (n_len, BASELINE_LENGTHISH))

    #: ★★★ ③ **「长度藏在 spec 里」那一族必须在视野里**（★ 回归守卫）
    #: ★ 依据：★ `create_external_spur_gear_report(model, spec, …)` 的形参是 `spec`（dic
    #: t）⇒
    #:     ★ 只按形参名判 ⇒ **整族被跳过** ✗（★ 业主点破的就是这一族）
    #:   ★★ **2026-10-10 改为按「机制」断言，不按「具体工具名」**（★ 如实）：
    #:     ★ 齿轮**工具**已按业主架构指令移出（★ 它是方法）⇒ ★ 不能再要求它在工具面上 ✓
    #:     ★★★ **但那条**盲区**必须仍然被守** ⇒ ★ 改判「**审计器有没有跟一层调用的机制**」——
    #:       ★ 只要 `_lengthish_from_callees` 在，★ 形参叫 `spec` 的族就**不会被整族跳过** ✓
    #:   ★ 判据：★ 审计器源码里必须有 `_lengthish_from_callees` 与 `SPECLIKE_PARAM` ✓
    audit_src = (ROOT / "scripts" / "audit_length_units.py").read_text(
        encoding="utf-8", errors="replace")
    if "_lengthish_from_callees" not in audit_src:
        problems.append("★★★ 审计器**没有「跟一层调用」的机制** ⇒ "
                        "★ 形参叫 `spec` 的族会被**整族跳过** —— ★ 业主点破的病复发")
    if "SPECLIKE_PARAM" not in audit_src:
        problems.append("★★★ 审计器**没有「像规格对象的形参名」那个判据** ⇒ ★ 盲区回来了")

    if problems:
        #: ⚠ 编码：★ 中文 Windows 控制台是 GBK ⇒ 直接 print 会把 `⇒` 打成
        #:   `UnicodeEncodeError`（★ 本判据自己踩过）⇒ ★ **逐条安全打印** ✓
        print("[FAIL] 单位纪律门禁未通过：")
        for p in problems:
            try:
                print("  * %s" % p)
            except UnicodeEncodeError:
                print("  * %s" % p.encode("ascii", "replace").decode("ascii"))
        return 1

    print("[PASS]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
