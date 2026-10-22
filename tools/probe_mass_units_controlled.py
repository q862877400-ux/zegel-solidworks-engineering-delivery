r"""@brief **D3 对照实验**：`IMassProperty2.Mass` 的物理单位 —— 用**已知密度材料**定死它。

## ★★★ 为什么需要它（24h 段 5「修地基 D3」）
```
★ 真机已测（`tools/probe_mass_property_reads.py`，轮 233）：
    盒 40×20×10 mm ⇒ `Volume = 8000` · `Density = 1000.0` · `Mass = 7999999.999999999`
  ⇒ ★ `Mass` 恰好 = `Volume(mm³) × Density`；★ 而 `Volume` 单位已确证是 **mm³**。
★★ 官方给了**一条关系式**（`C:\swapi\types\IMassProperty2\Density.md` 的 Remarks）：
    > **Density = ( Mass / Volume )**
  ⇒ ★ 实测 `7999999.999999999 / 8000 = 999.9999999999999 ≈ 1000.0` ⇒ ★ **关系式成立**
    ⇒ ★★ **三个读数互相自洽**，只是**单位系**是"mm-系"。
⇒ ★★★ **剩下的唯一未知：`Density` 用的到底是哪个单位制**（★ 这决定了 `Mass` 的单位）。
```

## ★★★★ 对照实验的设计（★ 一次定死）
```
★ **对照量**：★ **给它一个**已知密度**的材料**（★ 官方材料库里的值是我们**已知**的），
  然后读 `Density` 与 `Mass`，看读数**等于哪个单位制下的那个数**。
★ 判据（★ 事先规定，★ 事实 165 第 12 条）：
   ① ★ 记下 `set_material` 回读到的**材料名**（★ 确认真的赋上了）；
   ② ★ 读 `Density` ⇒ ★ **若它 ≈ 材料库给的 kg/m³ 数值** ⇒ **Density 以 kg/m³ 的数值表示**；
   ③ ★ 再用 `Mass / Volume` 与 `Density` 比 ⇒ ★ **验官方那条关系式在**这个**材料上也成立**；
   ④ ★ 最后：★ **用「体积(mm³) × Density」反算**，与 `Mass` 比 ⇒ ★ 定它与真实质量差多少个数量级。
⇒ ★★ **不做假设**：★ 三个读数**都记下来**，★ **结论从数里读出来**，不是我事先安一个。
```

## ⚠ 安全
只在新零件上跑 · `CommandInProgress` 抑制弹窗 · 关件不保存 · **不跑仿真** · **不保存文档**。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机对照实验）
# 文件:   tools/probe_mass_units_controlled.py
# 定位:   24h 计划 段 5「修地基 **D3**」；产物 `output/mass-units-controlled.json`。
# 官方依据: `C:\swapi\types\IMassProperty2\Density.md`（★ `Density = Mass / Volume` 那条
#            Remarks）·
#          `IMassProperty2\Mass.md` / `Volume.md` / `CenterOfMass.md`（★ 都在，但**都没写单位**）·
#          `IPartDoc\SetMaterialPropertyName2`（★ 赋材料）
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

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "mass-units-controlled.json"
)
#: ★ 对照材料（★ 选一个**密度有明确官方值**的；本机材料库的显示名见 `set_material` 的回
#: 读）
CANDIDATES = ("AISI 1020", "Plain Carbon Steel", "Alloy Steel", "AISI 304")


def main() -> int:
    ev: dict = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%s_"),
        "question": "IMassProperty2.Mass / Density 的物理单位（用已知密度材料对照）",
        "geometry": "40×20×10 mm 板（体积应 8000 mm³）",
        "steps": {},
    }
    sw = None
    doc = None
    try:
        import sw_connect

        from scripts import sw_part as p_
        from scripts import sw_simulation as s_

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        doc = sw_connect.new_document(sw, "part")
        p_.start_sketch(doc, plane_name="Front Plane")
        p_.sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk = p_.current_sketch_name(doc)
        p_.end_sketch(doc)
        p_.extrude_boss(doc, sk, 10.0)

        def _read():
            """★ 读三个量 + 官方关系式（★ 不假设单位，只记数）。

            ★★★ 2026-10-01（轮 263）**补上 `Recalculate()`** —— 这是第一版**漏掉的关键一步**：
              官方 `IMassProperty2.Density.md` 的 Remarks 写着
              「If `IncludeHiddenBodiesOrComponents` is reset, then **call `Recalculate`** before …」
              ⇒ ★★ **`IMassProperty2` 是**缓存**的** ⇒ 赋材料之后**不重算就读到旧值**
              ⇒ 这解释了第一版为什么"赋了 AISI 1020（≈7900 kg/m³）而 `Density` 仍是 1.0"。
              ⇒ ★★★ **而它同时说明**：★ 第一版那个"此路不通"的结论**是我漏了一步**，不是设计前提错。
            """
            ext = sw_connect.get_com_member(doc, "Extension")
            #: ★★★ 2026-10-01（轮 263）**改用后继入口** —— 第一版用 `CreateMassProperty`
            #: （**Obsolete**）
            #: 拿到的对象**没有** `Recalculate`（真机报 `<unknown>.Recalculate` ⇒ **事实
            #:  36 的形态**：
            #:   名字存在但**挂在别的接口上**）。★ 官方 `CreateMassProperty.md` 明写
            #:   「**Obsolete. Superseded by `IModelDocExtension::CreateMassProperty2`**」
            #: ⇒ ★ 而既有探针 L11 早就注着「`CreateMassProperty2` ← ⚠ **可能有后继**」，
            #: **当年没试**。
            #:   ★★ 两个都试，**记录哪个能用**（★ 不假设）。
            entry, mp, entry_errs = None, None, []
            for nm in ("CreateMassProperty2", "CreateMassProperty"):
                try:
                    cand = sw_connect.get_com_member(ext, nm)
                    if cand is not None:
                        entry, mp = nm, cand
                        break
                    entry_errs.append("%s ⇒ None" % nm)
                except Exception as exc:  # noqa: BLE001
                    entry_errs.append("%s ⇒ %s" % (nm, str(exc)[:60]))
            if mp is None:
                return {"entry_errors": entry_errs, "★": "两个入口都拿不到对象"}
            recalc_err = None
            try:
                #: ★ 官方 Remarks 要求：改过选择/材料之后要重算（★ 否则读的是缓存）
                sw_connect.get_com_member(mp, "Recalculate")()
            except Exception as exc:  # noqa: BLE001
                recalc_err = "%s: %s" % (type(exc).__name__, str(exc)[:120])
            vol = float(sw_connect.get_com_member(mp, "Volume"))
            den = float(sw_connect.get_com_member(mp, "Density"))
            mass = float(sw_connect.get_com_member(mp, "Mass"))
            com = sw_connect.get_com_member(mp, "CenterOfMass")
            return {
                "entry_used": entry,
                "entry_errors": entry_errs,
                "volume": vol,
                "density": den,
                "mass": mass,
                "center_of_mass": [float(x) for x in (com or [])][:3],
                "recalculate_error": recalc_err,
                #: ★ 官方关系式 Density = Mass / Volume ⇒ 用读数验它成不成立
                "density_from_readings": (mass / vol) if vol else None,
            }

        #: ① 赋材料前
        ev["steps"]["before_material"] = _read()
        print(
            "  [0] 未赋材料: %s"
            % json.dumps(ev["steps"]["before_material"], ensure_ascii=False)[:170]
        )

        #: ② 逐个试候选材料（★ 回读材料名 ⇒ 确认真的赋上了）
        got = None
        for name in CANDIDATES:
            try:
                r = s_.set_material(doc, material_name=name)
                got = (name, r)
                print("  [1] set_material(%r) ⇒ %s" % (name, str(r)[:110]))
                break
            except Exception as exc:  # noqa: BLE001
                print("  [1] set_material(%r) ✗ %s" % (name, str(exc)[:80]))
        ev["steps"]["material_assignment"] = {
            "tried": CANDIDATES,
            "used": got[0] if got else None,
            "readback": (str(got[1])[:400] if got else None),
        }
        #: ③ 赋材料后
        ev["steps"]["after_material"] = _read()
        print(
            "  [2] 赋材料后: %s"
            % json.dumps(ev["steps"]["after_material"], ensure_ascii=False)[:170]
        )

        #: ④ ★★ 从数里读结论（★ 不预设）
        a = ev["steps"]["after_material"]
        b = ev["steps"]["before_material"]
        ev["steps"]["judgement"] = {
            "volume_is_mm3": (
                abs(a["volume"] - 8000.0) < 1.0 or abs(b["volume"] - 8000.0) < 1.0
            ),
            "density_relation_holds_now": (
                abs(a["density_from_readings"] - a["density"]) < 1e-3
                if a["density_from_readings"]
                else None
            ),
            "density_relation_holds_before": (
                abs(b["density_from_readings"] - b["density"]) < 1e-3
                if b["density_from_readings"]
                else None
            ),
            "density_value_before": b["density"],
            "density_value_after": a["density"],
            "★": (
                "★ 判读：① `Volume≈8000` ⇒ 体积单位 **mm³** 确证；"
                "② `Density == Mass/Volume`（官方 Remarks 那条）⇒ 三个读数自洽；"
                "③ ★ **`Density` 的读数是多少，就说明它用的是哪个单位制的数值** —— "
                "★ 把它与材料库给的 kg/m³ 值比，即可定 `Mass` 的单位。"
                "⚠ **本脚本不替你下结论**：把两次数都留着。"
            ),
        }
        print("  ── 判读 ──")
        print(
            "     %s" % json.dumps(ev["steps"]["judgement"], ensure_ascii=False)[:300]
        )
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
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

    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if not ev.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
