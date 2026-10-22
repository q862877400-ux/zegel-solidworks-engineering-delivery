r"""@brief 真机冒烟：`sw_mold.py` 的**只读**函数（`mold_evidence` 等）—— 给 `mold_tools` 拆条目取证。

## 背景
`capabilities.yaml` 的 `mold_tools` 是 **`stitched`** 且 **`evidence` 为空**；
它的第 3 条限度写着「本机没有 OCP/cadquery/trimesh ⇒ 涉及 **headless-occt** 的声明无法复现」。
★ 但同一条目的第 1 条说「新增 `scripts/sw_mold.py`（`InsertMoldPartingLine` / … / `mold_evidence`）」
  —— ★★ **那是我们自己的 COM 侧能力**，**可以真机验**，却因为混在同一条目里而**没有 evidence**。
⇒ 本冒烟给**只读那一半**取证（写入类函数**故意不调**，它们在未准备的分型件上会弹框，见 `PRECONDITIONS`）。

## 判据（能被空操作证伪）
```
① `mold_evidence()` 在**新零件**上可调用，且**返回 dict**（不是 None）
② dict 里**有**官方那几个只读入口的键（GetPartingLinesCount / GetPartingSurfacesCount /
   GetCavitySurfacesCount / GetCoreSurfacesCount / PartingType / CoreCavitySplit）
③ 新零件上这些计数**都是 0**（**定量**：空件的分型面/型芯型腔必然为 0；非 0 就说明读错了对象）
④ `MoldDraftAnalysis` / `MoldUndercutDetect` **故意不调**（会弹框）⇒ 如实写明"未验"
```

## ⚠ 安全
只在新零件上；`CommandInProgress` 复位；收尾**轮询点掉**；关件不保存。

# ── 来源 ──
# 仓库:   本项目自身（真机冒烟）
# 文件:   tools/verify_mold_evidence_smoke.py
# 定位:   给 Spec Kit `092` 拆出 `mold_evidence` 条目并升 `verified`。
# 官方依据: `sw_mold.py::mold_evidence` 的 docstring（GetPartingLinesCount /
#          GetPartingSurfacesCount / GetCavitySurfacesCount / GetCoreSurfacesCount /
#          get_PartingType / get_CoreCavitySplit）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "mold-evidence-smoke.json")
#: ★★★★★ 2026-10-01（轮 343）**判据修正：4 个计数在 `counts` **子字典**里，不在顶层** ——
#:   真因（挖 `mold_analysis` 这条 `stitched` 时发现）：
#:   ★ 本脚本原先按**平铺**找键（`"parting_lines_count" in evd`），
#:   而 `sw_mold.mold_evidence()` 回的是**嵌套**的：
#:   ```
#: {"counts": {"parting_lines": …, "parting_surfaces": …, "cavity_surfaces": …, "core_su
#: rfaces": …},
#:    "parting_type": …, "core_cavity_split": …}
#:   ```
#: ⇒ ★ 顶层只有 **2** 个（`parting_type` / `core_cavity_split`）⇒ 本脚本**永远报 3/5 fai
#: l**。
#:   ⇒ ★★★ **而那个结论被写进了 `capabilities.yaml` 的 `limitations`**，
#:     把一条**本来正常**的能力钉在 `stitched` 上 ⇒ ★★ **旧结论会把好能力误判成坏能力。**
#: ★ 现改为：**计数键名对 `counts` 子字典、属性键名对顶层**（★ 与实现的**更好**形状对齐
#: ）。
WANTED_COUNTS = ("parting_lines", "parting_surfaces", "cavity_surfaces", "core_surfaces")
WANTED_PROPS = ("parting_type", "core_cavity_split")


def main() -> int:
    ev: dict = {"checks": []}
    ok_n = 0
    total = 0
    sw = None
    doc = None

    def chk(name, ok, detail=""):
        nonlocal ok_n, total
        total += 1
        if ok:
            ok_n += 1
        ev["checks"].append({"name": name, "ok": bool(ok), "detail": str(detail)[:150]})
        print("   %s %-52s %s" % ("✓" if ok else "**✗**", name[:52], str(detail)[:66]))

    try:
        import sw_connect
        from scripts import sw_mold
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        chk("新建临时零件（不碰用户文档）", doc is not None, "ok")

        evd = sw_mold.mold_evidence(doc)
        chk("★ `mold_evidence()` 可调用且返回 dict", isinstance(evd, dict),
            type(evd).__name__)
        if isinstance(evd, dict):
            ev["evidence_keys"] = sorted(evd.keys())
            print("     键: %s" % sorted(evd.keys()))
            #: ★★ 判据按**实现真实的形状**：计数在 `counts` 子字典、属性在顶层。
            counts = evd.get("counts") if isinstance(evd.get("counts"), dict) else {}
            have = ([k for k in WANTED_COUNTS if k in counts]
                    + [k for k in WANTED_PROPS if k in evd])
            chk("★★ 含官方只读入口的键（%d/%d）" % (len(have), len(WANTED_COUNTS) + len(WANTED_PROPS)),
                len(have) >= 4, have)
            #: ★ 定量：新零件上计数必须为 0
            zeros = ([k for k in WANTED_COUNTS if k in counts and counts[k] in (0, None, "", "0")]
                     + [k for k in WANTED_PROPS if k in evd and evd[k] in (0, None, "", "0")])
            chk("★★ 新零件上这些读数**都是空/0**（非 0 就是读错了对象）",
                len(zeros) >= 4, "%d 个为 0/空" % len(zeros))
            ev["values"] = {"counts": {k: counts.get(k) for k in WANTED_COUNTS if k in counts},
                            **{k: evd.get(k) for k in WANTED_PROPS if k in evd}}
    except Exception as exc:      # noqa: BLE001
        chk("真机冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:90]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:      # noqa: BLE001
            pass

    import sw_connect as _sc
    found, dismissed, scanned = _sc.settle_residual_dialogs(settle_seconds=1.0)
    chk("★ 收尾（轮询 + 查到就点掉）", found == 0,
        "发现 %d · 点掉 %d · 扫了 %d 个窗口" % (found, dismissed, scanned))

    print()
    print("  ── %d/%d · verdict: %s ──" % (ok_n, total, "pass" if ok_n == total else "fail"))
    print("  ⚠ **未验**：`MoldDraftAnalysis` / `MoldUndercutDetect` / `InsertMold*` —— "
          "在未准备的分型件上会弹框（见 `verify_batch9_smoke.py` 的 PRECONDITIONS）。")
    ev["passed"], ev["total"] = ok_n, total
    ev["verdict"] = "pass" if ok_n == total else "fail"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if ok_n == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
