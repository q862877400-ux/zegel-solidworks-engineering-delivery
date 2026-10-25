"""★ 真机验证单位纪律：按**米**放组件，回读变换矩阵必须是对应的**毫米**数。

## 为什么是独立工具而不是 pytest 内的测试

第 60 轮实测：常驻弹窗监控（`sw_dialog_watch`）自己会连 SolidWorks ⇒
pytest 进程内再连就是**两个 COM 客户端** ⇒ 后连的被断连（事实 569）。

⇒ 真机验证必须**自己一个进程**跑。pytest 里那条只做结构断言（形参带 `_m`）。

## 用法

```
python -B tools/verify_component_units.py            # 默认 3 组偏移全跑
python -B tools/verify_component_units.py --offset 0.030,0.050
```

## 判据（独立读数，不看返回值）

对每组 `(x_m, z_m)`：
- 组件数必须 **+1**（数条数，不信返回值）
- 变换矩阵平移分量（mm）的**量级**必须与给定米数一致：`|x_read - x_m*1000|` 与零件自身
  坐标系偏移一致（板件原点在角上，实测约 -50 / -30 / +10 mm）
- ★ **最关键的判据是数量级**：传 0.030 米就该读到几十毫米；读到几万毫米就是
  又「把毫米喂给收米的函数」了（第 60 轮的 bug 正是 30 米）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 单位纪律真机验证）
# 文件:   tools/verify_component_units.py
# 定位:   按米放组件并回读变换矩阵，证明「米/毫米」在真机上不再混。
#          独立进程跑（常驻弹窗监控也持 COM ⇒ 同进程两个客户端会断连，事实 569）。
# 官方依据: IAssemblyDoc::AddComponent5（文件必须已在内存）· IAssemblyDoc::GetComponents ·
#          IComponent2::Transform2 → IMathTransform::ArrayData（平移在 [9..11]，单位米）·
#          ISldWorks::ActivateDoc3
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "verify-component-units.json"

#: (x_m, z_m) 三组：覆盖「非零两轴」「只一轴」「原点」
CASES = ((0.030, 0.050), (0.060, 0.0), (0.0, 0.0))

import sw_assembly as asm_  # noqa: E402
import sw_connect as c_  # noqa: E402
from sw_connect import get_com_member  # noqa: E402


def _open_fresh(sw):
    """清场 → 开零件 → 建装配 → 激活 → 返回装配文档。"""
    try:
        for d in list(get_com_member(sw, "GetDocuments") or ()):
            sw.CloseDoc(str(get_com_member(d, "GetTitle") or ""))
    except Exception:  # noqa: BLE001
        pass
    c_.open_document(sw, str(PART))
    ok, raw = c_.try_call(c_.new_document, sw, "assembly")
    if not ok or raw is None:
        return None
    try:
        sw.ActivateDoc3(str(get_com_member(raw, "GetTitle") or ""), 0, False)
    except Exception:  # noqa: BLE001
        pass
    #: ★★ 只接受**装配体**（GetType()==2）—— 无条件用 ActiveDoc 会拿到**零件**，
    #:   那样 dd_component 就是对零件操作，必然 0 → 0（第 60 轮实测踩到）。
    cand = get_com_member(sw, "ActiveDoc")
    if cand is not None and int(get_com_member(cand, "GetType") or 0) == 2:
        return cand
    if raw is not None and int(get_com_member(raw, "GetType") or 0) == 2:
        return raw
    return None


def main() -> int:
    cases = CASES
    if "--offset" in sys.argv:
        k = sys.argv.index("--offset")
        x, z = sys.argv[k + 1].split(",")
        cases = ((float(x), float(z)),)

    ev: dict = {"probe": "verify-component-units", "cases": []}
    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass

    bad = 0
    try:
        for (x_m, z_m) in cases:
            rec: dict = {"x_m": x_m, "z_m": z_m}
            asm_doc = _open_fresh(sw)
            if asm_doc is None:
                rec["err"] = "建不了装配"
                ev["cases"].append(rec)
                bad += 1
                continue
            before = len(list(get_com_member(asm_doc, "GetComponents", False) or ()))
            try:
                asm_.add_component(asm_doc, str(PART), x_m=x_m, y_m=0.0, z_m=z_m, sw=sw)
            except Exception as exc:  # noqa: BLE001
                rec["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
            comps = list(get_com_member(asm_doc, "GetComponents", False) or ())
            rec["components"] = "%s → %s" % (before, len(comps))
            rec["added"] = len(comps) == before + 1

            if rec["added"]:
                tr = get_com_member(comps[-1], "Transform2")
                data = list(get_com_member(tr, "ArrayData") or ())
                if len(data) >= 12:
                    rec["read_mm"] = [
                        round(data[9] * 1000.0, 3),
                        round(data[10] * 1000.0, 3),
                        round(data[11] * 1000.0, 3),
                    ]
                    #: ★ 最关键的判据：**数量级**
                    rec["magnitude_ok"] = all(
                        abs(v) < 1000.0 for v in rec["read_mm"]
                    )
                    #: 平移量应≈给定米数×1000 + 零件自身原点偏移
                    rec["delta_x_mm"] = round(rec["read_mm"][0] - x_m * 1000.0, 3)
                    rec["delta_z_mm"] = round(rec["read_mm"][2] - z_m * 1000.0, 3)
                else:
                    rec["err"] = "变换矩阵读不到"
            rec["ok"] = bool(rec.get("added") and rec.get("magnitude_ok"))
            if not rec["ok"]:
                bad += 1
            ev["cases"].append(rec)
            print(
                "  (%s, %s) m → 读数 %s mm · 组件 %s · %s"
                % (x_m, z_m, rec.get("read_mm"), rec.get("components"),
                   "通过" if rec["ok"] else "★ 不过")
            )
    finally:
        try:
            for d in list(get_com_member(sw, "GetDocuments") or ()):
                sw.CloseDoc(str(get_com_member(d, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        ev["ok"] = bad == 0
        ev["failed"] = bad
        DEST.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("★ 结论：%s（%d/%d 通过）" % ("全部通过" if bad == 0 else "有失败",
                                          len(cases) - bad, len(cases)))
        print("   证据已写：%s" % DEST)

    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
