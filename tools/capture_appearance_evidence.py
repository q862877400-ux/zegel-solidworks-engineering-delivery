r"""@brief 真机证据：**渲染材质与外观域**（24h 段 5 的「方程 / 渲染材质」那一半）。

## ★★★ 为什么这一批（★ 逐域判断的产出，不是数函数）
```
★ 对照**仓库自己的 14 个域**（`docs/capability-matrix.md` §一）核 `capabilities.yaml` 的 57 条 ⇒
  发现 ★ **`appearance` / `render` 各出现 0 次** ⇒ ★★ **"渲染材质"这个域**有工具、没条目****：
     · `solidworks_list_render_materials` / `solidworks_collect_appearance_evidence` /
       `solidworks_refresh_scene_graph`（★ **三个工具早就在**，`module=sw_render_material`）
     · `scripts/sw_appearance.py` + `scripts/sw_render_material.py`
⇒ ★★★ **所以缺口在「域级能力条目」，不在工具** ⇒ ★★ **本批补的是条目 + 它的真机证据**。
★★ 而 §5.0 先找了：★ **这个域**没有**既有证据脚本**（`tools/` 里搜 `appearance`/`render`/`material` ⇒ 无）
  ⇒ ★ **自己搓，并说明"找过"**。
```

## 判据（★ 用**既有的**读写配对，不新搓）
```
★ `sw_appearance.set_document_appearance(model, color)` ⇒ 设置
★★ `sw_appearance.verify_appearance(target, color, tolerance)` ⇒ ★ **回读核对**（★ 本项目"读写配对"的既有手法）
★ `sw_render_material.collect_appearance_evidence(model)` ⇒ ★ **读数**（★ 是不是 dict、有没有关键键）
⇒ ★★ **判据 = 设一个颜色 → 回读核对通过**（★ 而不是"函数没报错"）。
```

## ⚠ 安全
只在新零件上跑 · `CommandInProgress` 抑制弹窗 · 关件不保存 · **不跑仿真**。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本）
# 文件:   tools/capture_appearance_evidence.py
# 定位:   给「渲染材质与外观」能力条目取真机证据；产物 `output/appearance-evidence.jso
#           n`。
# 官方依据: `IModelDocExtension.SetMaterialPropertyValues2` 族 / `IRenderMaterial`
#          （见 `scripts/sw_appearance.py` 与 `scripts/sw_render_material.py` 的来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 真机脚本：跑之前确认只有一个 SolidWorks 实例（已知事实 24）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "appearance-evidence.json")
#: ★ 一个明确的测试色（★ 用 RGB 分量表示，★ 与 `set_document_appearance` 的口径一致）
TEST_COLOR = (0.2, 0.6, 0.9)


def main() -> int:
    ev: dict = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%m_:%S"),
        "capability": "render_materials_and_appearance",
        "steps": {},
    }
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect

        from scripts import sw_appearance as a
        from scripts import sw_part as p_
        from scripts import sw_render_material as m_

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        doc = sw_connect.new_document(sw, "part")
        p_.start_sketch(doc, plane_name="Front Plane")
        p_.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = p_.current_sketch_name(doc)
        p_.end_sketch(doc)
        p_.extrude_boss(doc, sk, 20.0)

        #: ① 读数：外观证据（★ 判"是 dict 且有关键键"）
        try:
            r = m_.collect_appearance_evidence(doc)
            ev["steps"]["collect_appearance_evidence"] = {
                "ok": isinstance(r, dict) and bool(r),
                "keys": sorted(r.keys())[:8] if isinstance(r, dict) else None,
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["collect_appearance_evidence"] = {
                "ok": False,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }
        print(
            "  [1] collect_appearance_evidence: %s"
            % json.dumps(
                ev["steps"]["collect_appearance_evidence"], ensure_ascii=False
            )[:140]
        )

        #: ② 渲染材质清单（★ 判"是 list"）
        try:
            mats = m_.list_render_materials(doc)
            ev["steps"]["list_render_materials"] = {
                "ok": isinstance(mats, (list, tuple)),
                "count": len(mats) if mats is not None else None,
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["list_render_materials"] = {
                "ok": False,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }
        print(
            "  [2] list_render_materials: %s"
            % json.dumps(ev["steps"]["list_render_materials"], ensure_ascii=False)[:120]
        )

        #: ③ ★★ 读写配对：设文档外观 → 回读核对
        try:
            a.set_document_appearance(doc, TEST_COLOR)
            v = a.verify_appearance(doc, TEST_COLOR, 0.05)
            ev["steps"]["set_and_verify_document_appearance"] = {
                "ok": bool(v),
                "set_color": list(TEST_COLOR),
                "verified": bool(v),
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["set_and_verify_document_appearance"] = {
                "ok": False,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }
        print(
            "  [3] 设+验文档外观: %s"
            % json.dumps(
                ev["steps"]["set_and_verify_document_appearance"], ensure_ascii=False
            )[:140]
        )

        #: ④ 推进场景图（★ 判"不抛异常"）
        try:
            m_.refresh_scene_graph(doc, update=True)
            ev["steps"]["refresh_scene_graph"] = {"ok": True}
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["refresh_scene_graph"] = {
                "ok": False,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }
        print(
            "  [4] refresh_scene_graph: %s"
            % json.dumps(ev["steps"]["refresh_scene_graph"], ensure_ascii=False)[:100]
        )

        #: ⑤ 综合
        checks = {k: bool(v.get("ok")) for k, v in ev["steps"].items()}
        ev["steps"]["judgement"] = {
            "checks": checks,
            "passed": sum(1 for x in checks.values() if x),
            "of": len(checks),
            "★": "★ 四项：读数两项 + **读写配对**一项（核心）+ 场景图一项",
        }
        ok = all(checks.values())
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ok = False
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)  #: ★ 关件不保存
        except Exception:  # noqa: BLE001
            pass

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 渲染材质与外观真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-36s %s" % (k, json.dumps(v, ensure_ascii=False)[:200]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
