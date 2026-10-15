"""★ 决定性实验：同文档、同会话、单变量 —— 把 COM 侧单位钉死。

★★ 为什么必须做（审计员 7/8 独立指出）：
   本仓有两套互相矛盾的真机记录：
     · 支持「COM 吃米」：`probe-unit-suspects`（dome +5000mm）· `sw_part.py:548-574`
     · 支持「随文档单位」：事实 517 · `extrude-depth-unit-evidence.json` · `chamfer-fillet-evidence.json`
   ★ 而审计员 8 已证：**旧证据的试件本身是错的**（它以为的 100mm 板实际是 100 米），
     且**判据尺度不变**（比值在两种单位下都成立）⇒ 定不了单位。

★★ 本实验的设计（★ 单变量、有基准、不可被尺度不变骗过）：
   同一个草图、同一个会话、只改**一个数**：
     臂 A：`extrude_boss(sk, 20.0)`     ← 原样传 20
     臂 B：`extrude_boss(sk, 0.02)`     ← 传 20mm 对应的米
   ⇒ 量两条的**包围盒 Z 跨度**：
     · 若 A 的 Z = 20000mm（20 米）、B 的 Z = 20mm ⇒ **COM 吃米**（A 错、B 对）
     · 若 A 的 Z = 20mm、B 的 Z = 0.02mm ⇒ **COM 吃毫米**（A 对、B 错）
   ★ 两个臂在**同一个文档**里做（用两个不同草图），排除跨文档差异。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/probe_unit_decisive.py
# 定位:   规格 315 的 ① 攻关 · 单位定案（★ 修之前必须先钉死）
# 官方依据: ① `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md`（官方 D1 的说明）
#           ② `C:\swapi\types\IModelDoc2\GetPartBox.md`（回读 6 个数）
#           ③ 本仓 `docs/known-facts.md` 事实 517（与本实验对立的旧结论）
#           ④ 审计员 7/8 的独立发现（`output/_unit_audit_verdicts.json` 那批）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import pathlib
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"), str(ROOT / "tools")]

DIR = ROOT / "output" / "probe-unit-decisive"
EV: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "arms": []}


def arm(name: str, **kw) -> None:
    EV["arms"].append({"arm": name, **kw})
    print("   %-38s %s" % (name, json.dumps(kw, ensure_ascii=False)[:120]))


def main() -> int:
    import sw_connect
    from scripts import sw_part

    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    try:
        sw.CommandInProgress = True
    except Exception:      # noqa: BLE001
        pass
    DIR.mkdir(parents=True, exist_ok=True)
    doc = None

    def size(d) -> list | None:
        """★ `GetPartBox(False)` 回 6 个数 [xmin..zmax]（毫米）⇒ 算 max−min。"""
        try:
            pd = list(sw_connect.safe_get_com_member(d, "GetPartBox", False))
            if len(pd) < 6:
                return None
            return [round(float(pd[3]) - float(pd[0]), 4),
                    round(float(pd[4]) - float(pd[1]), 4),
                    round(float(pd[5]) - float(pd[2]), 4)]
        except Exception:      # noqa: BLE001
            return None

    try:
        doc = sw_connect.new_document(sw, "part")

        #: ══ 臂 A：原样传 20.0 ═════════════════════════════════
        #: ★ 草图用「已换算」的路（sketch_corner_rectangle 内部乘 _MM_TO_M）
        #:   ⇒ 草图是 40×40 mm（正确），把变量隔离到「拉伸深度」这一个数上
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, 40.0, 40.0)
        sw_part.end_sketch(doc)
        arm("A0 草图已建（40×40 mm）", size=size(doc))
        sw_part.extrude_boss(doc, "草图1", 20.0)      #: ★ 原样传 20
        arm("A1 extrude_boss(20.0) 原样", size=size(doc),
            expect="吃米⇒[40,40,20000] · 吃毫米⇒[40,40,20]")

        #: ══ 臂 B：传 0.02（20mm 的米值）═══════════════════════
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 100.0, 0.0, 140.0, 40.0)
        sw_part.end_sketch(doc)
        #: ★ 第二块板的草图名可能是「草图2」
        names = []
        try:
            from scripts import sw_feature_readback
            names = sw_feature_readback.feature_names(doc) or []
        except Exception:      # noqa: BLE001
            pass
        sk2 = next((n for n in names if "草图" in str(n) or "Sketch" in str(n)), "草图2")
        arm("B0 草图2 已建（40×40 mm）", size=size(doc), sketch2=str(sk2))
        sw_part.extrude_boss(doc, str(sk2), 0.02)     #: ★ 传 0.02
        arm("B1 extrude_boss(0.02) 传米值", size=size(doc),
            expect="吃米⇒Z 增 20mm · 吃毫米⇒Z 几乎不变")

        #: ══ 臂 C：fillet 单变量（★ 用臂 A 那块 20mm 厚的板）════
        #: ★ 先确认当前尺寸，再对一条边做 R5
        before = size(doc)
        try:
            from scripts import sw_selection_spec
            ent = sw_selection_spec.resolve_entity(doc, "index:0", "EDGE")
            sw_selection_spec.select_object(doc, ent)
            sw_part.fillet(doc, 5.0)
            arm("C1 fillet(5.0) 原样", before=before, after=size(doc),
                expect="吃米⇒包围盒塌成 5 米级 · 吃毫米⇒只掉几毫米")
        except Exception as exc:      # noqa: BLE001
            arm("C1 fillet 异常", err="%s: %s" % (type(exc).__name__, str(exc)[:90]))

        EV["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        out = DIR / "decisive.json"
        out.write_text(json.dumps(EV, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\n★ 证据 → %s" % out)
        return 0
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        if doc is not None:
            try:
                t = sw_connect.safe_get_com_member(doc, "GetTitle")
                if callable(t):
                    t = t()
                if t:
                    sw.CloseDoc(str(t))
            except Exception:      # noqa: BLE001
                pass


if __name__ == "__main__":
    raise SystemExit(main())
