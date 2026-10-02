r"""@brief **故意写错**的 arity 负例 —— 给 `scripts/audit_call_arity.py` 当"应该抓住"的输入。

⚠⚠ **本文件故意包含错误的 COM 调用，不要照抄，也不要修好它。**
它的唯一用途是**证明审计工具的判据仍然有效**（已知事实 62：「一个门禁『写了』
不等于它『有效』—— 负例测试是唯一的证明」）。

## 为什么要有这个文件
批次 6/7 的「判据有效性检验」用的是 `%TEMP%\arity_neg.py` ——
**住在临时目录里 ⇒ 不可复现**，下一轮想复验就得重写一份（而且容易写成"另一份"）。
⇒ 本轮（2026-10-01 轮 123）把它**固化进仓库**，并配一条测试。

## 三处故意错在哪
| 行 | 写法 | 官方 | 应报 |
|---|---|---|---|
| `CreateNewStudy3("n", 13, 0)` | 3 参 | 4 参（第 4 个是 `Int32&`，**必填**）| 「存疑 · 官方 arity=4」|
| `InsertWeldmentFeature(1)` | 1 参 | 0 参 | 「存疑 · 官方 arity=0」|
| `TotallyBogusMemberName()` | 成员名不存在 | — | 「查不到」|

# ── 来源 ──
# 仓库:   本项目自身（测试夹具，非第三方移植）
# 文件:   tools/arity_negative_case.py
# 定位:   固化 `docs/signature-audit.md` 的"判据有效性检验"输入。
# 官方依据: 出厂反射 `iface_*.txt`（ICWStudyManager / IFeatureManager）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sw_connect import get_com_member          # noqa: E402


def run(host):
    """@brief 对 `host` 发三个**故意错**的调用（仅供审计工具当负例）。"""
    # ① 少传一个：官方 4 参，这里只给 3 个
    get_com_member(host, "CreateNewStudy3", "n", 13, 0)

    # ② 多传一个：官方 0 参
    get_com_member(host, "InsertWeldmentFeature", 1)

    # ③ 成员名根本不存在
    get_com_member(host, "TotallyBogusMemberName")

    return None       # ⚠ 本函数**不该被真机调用** —— 只是给静态审计当输入
