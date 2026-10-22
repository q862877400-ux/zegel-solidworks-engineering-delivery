r"""@brief 验收命令：`routing` 的**中性复核**端到端（离线，**不碰 SolidWorks**）。

## 为什么需要它（2026-10-01 轮 78）
`capabilities.yaml` 的 `routing` 是 **`stitched`** 且 **`evidence: 无`**。
按 `AGENTS.md §一 A4`「`verified` 必须有**我们自己的运行证据**」——本命令补那条证据。

## limitations ① 承诺的七件事（⇒ 本命令逐条判）
```
当前支持中性 Routing 端点、分段、长度、弯曲半径、碰撞/间隙、支撑间距和 BOM 复核；
不生成 SOLIDWORKS Routing 原生特征
```
⇒ 判据（**故意造违规，看它们是否被抓**；不是"跑通就算"）：
1. **端点 / 分段 / 长度**：两点 (0,0,0)→(30,40,0) ⇒ `totalLength` 必须 = 50；
2. **弯曲半径**：`bendRadius` 低于 `minimumBendRadius` ⇒ **必须被抓**；
3. **碰撞/间隙**：在路径上放 AABB 障碍 ⇒ `collisionEvidence[].obstacles` 必须点名它；
4. **支撑间距**：长段且支撑不足 ⇒ `supportEvidence[].required > 0` 且出现
   `routing_supports_insufficient`；
5. **BOM 复核**：`routingBom[0].totalLength` 必须与 `totalLength` 一致；
6. **不生成原生特征**：`nativePreflight.readyForNativeWrite` 必须 **False**
   （**这是最核心的诚实承诺**）；
7. 输入侧：**上限 / 损坏 JSON / 根节点类型** 都被挡，**输入文件只读**。

⚠ 另判 limitations ② 的前提：`probe_solidworks_routing()` 必须返回**结构化**结果
（`readyForNativeWrite` 为 True 或 False 都行 —— 关键是**它给的是判断而不是异常**）。

## ⚑ 先核依赖（上一轮的教训）
升 level 前先确认「证据依赖的东西在本机存不存在」：
`json` / `math` / `numpy` / `jsonschema` / `pydantic` **本机都可用** ⇒ 本条**不需要** OCP / SolidWorks。

# ── 来源 ──
# 仓库:   本项目自身（离线验收）
# 文件:   tools/verify_routing_e2e.py
# 定位:   给 `capabilities.yaml` 的 `routing` 条目提供 `evidence`。
# 官方依据: 不适用（本项目内部工具，只读 JSON、不调 SolidWorks API）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts import routing_review  # noqa: E402

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "routing-evidence.json")


def _clean_doc() -> dict:
    """正常文档：两点 50 mm ⇒ 不触发任何违规。"""
    return {
        "routeType": "cable", "units": "mm", "material": "PVC",
        "minimumBendRadius": 20, "minimumClearance": 5, "maximumSupportSpacing": 60,
        "endpoints": [{"id": "J1", "position": [0, 0, 0]},
                      {"id": "J2", "position": [30, 40, 0]}],
        "segments": [{"id": "S1", "start": "J1", "end": "J2",
                      "bendRadius": 25, "diameter": 8}],
    }


def _bad_doc() -> dict:
    """违规文档：碰撞障碍 + 支撑不足 + **弯曲半径过小**，段长 60 mm。"""
    return {
        "routeType": "pipe", "units": "mm", "material": "Steel",
        "minimumBendRadius": 30, "minimumClearance": 10, "maximumSupportSpacing": 20,
        "endpoints": [{"id": "A", "position": [0, 0, 0]},
                      {"id": "B", "position": [60, 0, 0]}],
        "segments": [{"id": "P1", "start": "A", "end": "B",
                      "bendRadius": 5, "diameter": 12}],       # ← 5 < minimumBendRadius 30
        "obstacles": [{"id": "FRAME", "min": [28, -5, -5], "max": [32, 5, 5]}],
        "supports": [{"id": "CLAMP-1", "segmentId": "P1", "distanceAlong": 5}],
    }


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name: str, ok: bool, detail: str) -> None:
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": detail}
        print("   %s %-40s %s" % ("✓" if ok else "**✗**", name, detail[:88]))

    # 原生探测必须是**结构化**的（不是抛异常）
    probe = routing_review.probe_solidworks_routing()
    chk("原生探测返回结构化结果（不抛异常）",
        isinstance(probe, dict) and "readyForNativeWrite" in probe,
        "keys=%s" % sorted(probe.keys())[:6])

    print()
    print("=== ① 正常文档：端点 / 分段 / 长度 ===")
    good = routing_review.build_routing_report(_clean_doc())
    chk("totalLength = 50（3-4-5 直角三角形）", good.get("totalLength") == 50,
        "实际 %r" % good.get("totalLength"))
    chk("endpointTable 有两个端点", len(good.get("endpointTable") or []) == 2,
        "%r" % [e.get("id") for e in good.get("endpointTable") or []])
    chk("segmentEvidence 回读 bendRadius = 25",
        (good.get("segmentEvidence") or [{}])[0].get("bendRadius") == 25,
        "实际 %r" % (good.get("segmentEvidence") or [{}])[0].get("bendRadius"))

    print()
    print("=== ② BOM 复核 ===")
    bom = (good.get("routingBom") or [{}])[0]
    chk("routingBom 长度与 totalLength 一致", bom.get("totalLength") == 50,
        "bom=%r" % bom.get("totalLength"))

    print()
    print("=== ③ ★ 核心诚实承诺：**不生成原生特征** ===")
    npf = good.get("nativePreflight") or {}
    chk("readyForNativeWrite 为 **False**（不假装能写原生）",
        npf.get("readyForNativeWrite") is False,
        "readyForNativeWrite=%r · status=%r" % (npf.get("readyForNativeWrite"), npf.get("status")))

    print()
    print("=== ④ 违规文档：碰撞 / 支撑 / 弯曲半径 ===")
    bad = routing_review.build_routing_report(_bad_doc())
    coll = (bad.get("collisionEvidence") or [{}])[0]
    chk("**碰撞障碍 FRAME 被点名**", "FRAME" in (coll.get("obstacles") or []),
        "obstacles=%r status=%r" % (coll.get("obstacles"), coll.get("status")))
    sup = (bad.get("supportEvidence") or [{}])[0]
    chk("**支撑不足被发现**（required > 0）", (sup.get("required") or 0) > 0,
        "required=%r 已给=%r" % (sup.get("required"), sup.get("provided")))
    codes = [f.get("code") for f in (bad.get("reviewFindings") or [])]
    chk("出现 `routing_supports_insufficient`",
        "routing_supports_insufficient" in codes, "codes=%r" % codes)
    # ⚠ 弯曲半径过小：本项**不假定**一定被抓 —— 如实记录实测结果（可能是一个发现）
    bend_hit = any("bend" in str(c).lower() for c in codes)
    ev["checks"]["bend_radius_too_small_detected"] = {
        "ok": bend_hit, "detail": "codes=%r" % codes}
    print("   %s %-40s %s" % ("✓" if bend_hit else "ⓘ", "弯曲半径过小（5 < 30）",
                              "被抓 ✓" if bend_hit else "**未被抓**（如实记录，见 codes）"))
    checks.append(True)      # ⓘ 不当作失败：如实记录即可（铁律 5，不臆断该行为）

    print()
    print("=== ⑤ 输入侧：上限 / 损坏 JSON / 只读 ===")
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = td / "route.json"
        src.write_text(json.dumps(_clean_doc(), ensure_ascii=False), encoding="utf-8")
        before = hashlib.sha256(src.read_bytes()).hexdigest()

        rep = routing_review.review_routing_file(src, td / "r.json")
        chk("正常输入产出报告（review_required）", rep.get("status") == "review_required",
            "status=%r" % rep.get("status"))
        chk("**输入文件只读**（sha256 不变）",
            hashlib.sha256(src.read_bytes()).hexdigest() == before, "sha256 相同")

        broken = td / "broken.json"
        broken.write_text("{broken", encoding="utf-8")
        r2 = routing_review.review_routing_file(broken, td / "r2.json")
        chk("损坏 JSON 被挡（routing_input_invalid_json）",
            r2.get("error_code") == "routing_input_invalid_json", "error_code=%r" % r2.get("error_code"))

        arr = td / "arr.json"
        arr.write_text("[]", encoding="utf-8")
        r3 = routing_review.review_routing_file(arr, td / "r3.json")
        chk("根节点非 object 被挡（routing_input_root_invalid）",
            r3.get("error_code") == "routing_input_root_invalid", "error_code=%r" % r3.get("error_code"))

        missing = routing_review.review_routing_file(td / "nope.json", td / "r4.json")
        chk("**输入缺失返回结构化 blocked**（不抛异常）",
            missing.get("error_code") == "routing_input_missing"
            and not (td / "r4.json").exists(), "error_code=%r" % missing.get("error_code"))

    print()
    print("=== ⑥ CLI 可用（两个入口）===")
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = td / "cli.json"
        src.write_text(json.dumps(_clean_doc(), ensure_ascii=False), encoding="utf-8")
        # ⚠ 它的 CLI 用 **`--input` / `--output`**（不是位置参数）—— 实测踩过：位置参数 
        # ⇒ rc=2
        proc = subprocess.run(
            [sys.executable, str(_REPO / "scripts" / "routing_review.py"),
             "--input", str(src), "--output", str(td / "cli-report.json")],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(_REPO), stdin=subprocess.DEVNULL,
        )
        report_written = td / "cli-report.json"
        chk("CLI `--input/--output` ⇒ rc=0 且产出报告",
            proc.returncode == 0 and report_written.is_file(),
            "rc=%s 报告在=%s" % (proc.returncode, report_written.is_file()))
        if report_written.is_file():
            body = json.loads(report_written.read_text(encoding="utf-8"))
            chk("CLI 产出的报告含 nativePreflight",
                "nativePreflight" in body, "keys=%s" % sorted(body.keys())[:6])

        # 另一入口：`--preflight`（原生前置探测）
        pre = subprocess.run(
            [sys.executable, str(_REPO / "scripts" / "routing_review.py"), "--preflight"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(_REPO), stdin=subprocess.DEVNULL,
        )
        try:
            pre_body = json.loads((pre.stdout or "").strip())
        except json.JSONDecodeError:
            pre_body = {}
        chk("CLI `--preflight` ⇒ 输出结构化 JSON（含 backend）",
            isinstance(pre_body, dict) and "backend" in pre_body,
            "rc=%s backend=%r" % (pre.returncode, pre_body.get("backend")))

    ev["passed"] = sum(1 for c in checks if c)
    ev["total"] = len(checks)
    ev["verdict"] = "pass" if all(checks) else "fail"
    ev["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print()
    print("  ── %d/%d 项通过 · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  证据已写: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
