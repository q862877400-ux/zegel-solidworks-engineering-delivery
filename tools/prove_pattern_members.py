"""★ 真机：`IFeatureManager` 上那几个**阵列成员**取得取不到 —— ★ 拿 `CircularPattern4`（已验能用）当对照。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_pattern_members.py
# 定位:   ★ 2026-10-03（轮 453）—— ★ 承**事实 315**（`linear_pattern` 三次尝试后**没抛
#           错而特征树 9→9**）。
#   ★★★ **为什么现在值得重看**：★ 事实 315 那时我**没有**那把"问真机成员可用性"的镜子
#     （★ 它是**事实 362** 才建的）⇒ ★★ 而现在可以直接问：
#     ```
#     ★★ `FeatureLinearPattern3` 在这台真机的 `FeatureManager` 上**取得取不到**？
#     ```
#   ★ 而**对照**是现成的：★ 同族的 `circular_pattern` **已挂且能用**
#     （★ 而它用的 `FeatureCircularPattern4` 与 `linear_pattern` 用的是**同一套选区** ——
#      ★ 都是 `_select_by_id(..., "BODYFEATURE", mark=4)`）⇒ ★★ **故两者只差那一个成员** ✓
# ★★ 判据（★ 与事实 362 同一口径）：★ `getattr(obj, 名, None)` 三态（可调 / 属性 / 取不
# 到）。
#     ⚠ 而 `get_*` / `set_*` 是属性访问器（★ 迟到绑定下叫 `X`）⇒ 本探针**只查非访问器**。
# 官方依据: `IFeatureManager` 的 330 个成员（★ 出厂程序集反射）· 本仓 `scripts/sw_part.p
#           y` 的
#   `linear_pattern` / `circular_pattern` · 事实 315 / 362
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 报**每一个**候选的三态（★ 含对照项 —— ★ 因为"对照组能用"才使结论有意义）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "pattern-members-evidence.json"
)

#: ★ 要问的（★ 前 5 个是 `LinearPattern` 那族；★ 而后面几个是**对照**）
NAMES = [
    "FeatureLinearPattern",
    "FeatureLinearPattern2",
    "FeatureLinearPattern3",
    "FeatureLinearPattern4",
    "FeatureLinearPattern5",
    "FeatureCircularPattern4",
    "FeatureCircularPattern5",
    "InsertProtrusionBlend2",
    "FeatureExtrusion3",
]


def main() -> int:
    import sw_connect
    from com_member_probe import probe_members
    from sw_connect import get_com_member, safe_get_com_member

    ev: dict = {"at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        fm = get_com_member(doc, "FeatureManager")
        got = probe_members(fm, NAMES)
        ev["probed"] = len(NAMES)  # ★ 先报查了多少（事实 357）
        ev["states"] = got
        #: ★ 对照：★ CircularPattern4 **已验能用** ⇒ 它必须是 callable（★ 否则本探针的判
        #: 据有问题）
        ev["control_ok"] = got.get("FeatureCircularPattern4") == "callable"
        lp = {n: got.get(n) for n in NAMES if n.startswith("FeatureLinearPattern")}
        ev["linear_pattern_states"] = lp
        ev["any_linear_available"] = sorted(n for n, v in lp.items() if v == "callable")
        ev["verdict"] = "pass" if ev["control_ok"] else "invalid"
        ev["note"] = (
            "★ 问真机：那几个阵列成员取得取不到。★ **对照**是 `FeatureCircularPattern4` —— "
            "★ 它**已挂且能用**，★ 故它必须回 callable（★ 否则说明本探针的判据本身不对）。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        if doc is not None:
            try:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:  # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
