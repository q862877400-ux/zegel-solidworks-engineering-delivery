"""★ 规格 328 验收入口：云政策 + 离线承诺 + 降级顺序（Q7 的 U1~U7）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_s328_cloud.py
# 定位:   规格 `specs/328-cloud-whitelist-and-degradation` 的**验收入口**
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q7（L114-161）逐字② `metada
#           ta/cloud-policy.json`③ ★★ 业主 2026-10-12 三条拍板
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "scripts"),
    str(ROOT / "mcp-server"),
    str(ROOT / "tools"),
]

from scripts.engineering import cloud_policy as cp  # noqa: E402

OUT = ROOT / "output" / "s328"


def run_u() -> dict:
    """★ **U1~U7 逐条**。"""
    rows = []
    cp.load_policy()

    #: U1 离线承诺
    c = cp.offline_commitment()
    rows.append(
        {
            "u": "U1",
            "what": "五类离线 + 规划可关闭",
            "ok": c["offline_count"] == 5
            and c["online_can_be_disabled"]
            and c["offline_claim_narrowed"],
            "got": "%d 类 · 可关闭=%s"
            % (c["offline_count"], c["online_can_be_disabled"]),
        }
    )

    #: U2 不声称断网能自主
    v_off = cp.offline_verdict(online=False)
    rows.append(
        {
            "u": "U2",
            "what": "断网不声称能自主",
            "ok": v_off["autonomous_new_requirement"] is False
            and v_off["new_requirement"] == "manual_or_wait",
            "got": "新需求=%s · 自主=%s"
            % (v_off["new_requirement"], v_off["autonomous_new_requirement"]),
        }
    )

    #: U3 关闭能力
    d = cp.disabled_capabilities()
    rows.append(
        {
            "u": "U3",
            "what": "五项云端能力全关",
            "ok": d["all_disabled"] and d["n"] == 5,
            "got": "%d 项 · 全关=%s" % (d["n"], d["all_disabled"]),
        }
    )

    #: U4 固定快照
    pin = cp.check_model_pinning()
    rows.append(
        {
            "u": "U4",
            "what": "模型固定快照",
            "ok": pin["ok"] and not pin["follow_latest"],
            "got": "%s · follow_latest=%s" % (pin["snapshot"], pin["follow_latest"]),
        }
    )

    #: U5 降级顺序
    deg = cp.degradation_order()
    rows.append(
        {
            "u": "U5",
            "what": "三级降级顺序",
            "ok": deg["n"] == 3 and tuple(deg["steps"]) == cp.DEGRADATION_STEPS,
            "got": "%d 级" % deg["n"],
        }
    )

    #: U6 三条禁止
    rows.append(
        {
            "u": "U6",
            "what": "三条禁止",
            "ok": not any(deg["forbidden"].values())
            and len(cp.DEGRADATION_FORBIDDEN) == 3,
            "got": "三条都没犯",
        }
    )

    #: U7 业主三条拍板
    od = cp.owner_decisions()
    rows.append(
        {
            "u": "U7",
            "what": "业主三条拍板被尊重",
            "ok": od["respected"],
            "got": "本地模型=%s · 预算=%s · 客户端认证=%s"
            % (
                not od["decisions"]["no_local_model"],
                not od["decisions"]["no_budget"],
                not od["decisions"]["no_client_auth"],
            ),
        }
    )

    return {"rows": rows, "ok": all(r["ok"] for r in rows)}


def run_w() -> dict:
    """★ **W1~W6 反向验证**。"""
    rows = []

    #: W1 说过头
    w1 = cp.check_offline_claim("断网仍能自主处理新需求")
    rows.append(
        {
            "w": "W1",
            "what": "声称断网仍能自主",
            "ok": w1["ok"] is False,
            "got": w1["code"],
        }
    )

    #: W2 开一项云端能力
    p2 = cp.load_policy()
    p2["disabled_cloud_capabilities"]["cloud_execution"] = True
    w2 = cp.disabled_capabilities(p2)
    rows.append(
        {
            "w": "W2",
            "what": "开一项云端能力",
            "ok": w2["all_disabled"] is False,
            "got": w2["code"],
        }
    )

    #: W3 跟随 latest
    p3 = cp.load_policy()
    p3["cloud_whitelist"]["follow_latest"] = True
    w3 = cp.check_model_pinning(p3)
    rows.append(
        {
            "w": "W3",
            "what": "跟随 latest 升级",
            "ok": w3["ok"] is False,
            "got": w3["code"],
        }
    )

    #: W4 跳过降级顺序
    w4 = cp.check_degradation(used_steps=["fall_back_to_manual_or_deterministic"])
    rows.append(
        {"w": "W4", "what": "跳过降级顺序", "ok": w4["ok"] is False, "got": w4["code"]}
    )

    #: W5 抢显存
    p5 = cp.load_policy()
    p5["degradation_order"]["forbidden"]["compete_with_solidworks_for_vram"] = True
    w5 = cp.check_degradation(used_steps=[], policy=p5)
    rows.append(
        {
            "w": "W5",
            "what": "与 SolidWorks 抢显存",
            "ok": w5["ok"] is False,
            "got": w5["code"],
        }
    )

    #: W6 偷建本地模型服务
    w6 = cp.check_no_local_service(builds=["local_model_server"])
    rows.append(
        {
            "w": "W6",
            "what": "偷偷建本地模型服务",
            "ok": w6["ok"] is False,
            "got": w6["code"],
        }
    )

    return {"rows": rows, "ok": all(r["ok"] for r in rows)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    u = run_u()
    w = run_w()

    print("★ U1~U7：")
    for r in u["rows"]:
        print(
            "   %s %-4s %-24s ⇒ %s"
            % ("✓" if r["ok"] else "✗", r["u"], r["what"], str(r["got"])[:50])
        )
    print()
    print("★ W1~W6 反向验证：")
    for r in w["rows"]:
        print(
            "   %s %-4s %-24s ⇒ %s"
            % ("✓" if r["ok"] else "✗", r["w"], r["what"], str(r["got"])[:46])
        )

    print()
    print("★★ 业主三条拍板（★ 原话）：")
    for k, q in cp.owner_decisions()["owner_quotes"].items():
        print("   %-18s 「%s」" % (k, q))

    ev = {"u": u, "w": w, "finished": time.strftime("%H:%M:%S")}
    p = OUT / "cloud.json"
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print(
        "★ U：%s · W：%s" % ("过" if u["ok"] else "不过", "过" if w["ok"] else "不过")
    )
    print("★ 证据 → %s" % p)
    return 0 if (u["ok"] and w["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
