r"""@brief 探针：`Thickness` 是「**读得到、写不进**」吗？（pywin32 迟到绑定类问题）

## 为什么要问这个
上一轮把「mark」假设否证了。而报错里有个可疑词：
```
Property '<unknown>.Thickness' can not be set
         ^^^^^^^^^^^ dispatch 没有类型信息
```
**⇒ 这与 AGENTS.md 已知事实 11（makepy 强类型代理的 `[out] long` 要绕）、
28（`IModeler` 的成员运行期取不到）**同一类**：**类型层与运行层不一致**。**
**⇒ 若「读得到、写不进」，那这就**不是建模错误**，而是**绑定层问题** —— 修法完全不同。**

## 本探针查三件事
1. `Thickness` **读**得到吗？（`getattr` / `get_com_member`）
2. **写**的几条路各是什么结果？属性赋值 / `SetThickness` / `_oleobj_.Invoke`
3. 对象是什么类型？（`CDispatch`？有没有 typelib 信息？）
   **⇒ 若换用 `win32com.client.gencache`（makepy 强类型）能写进去，那真因就定了。**

# ── 来源 ──
# 仓库:   本项目自身（真机判定）+ AGENTS.md 已知事实 11 / 28 / 30
# 文件:   `IGussetFeatureData.Thickness`（`C:\swapi\types\IGussetFeatureData\Thickness.md`）
# 定位:   `scripts/sw_sheet_metal.py` 的 `create_gusset` 「属性设不上」的**绑定层**候选真因。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只造参照几何、不保存。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part  # noqa: E402
from scripts import sw_sheet_metal as SM  # noqa: E402


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        SM.create_base_flange(model, "Sketch1",
                              SM.BaseFlangeSpec(thickness=0.002, bend_radius=0.002, depth=0.05))
        mgr = get_com_member(model, "FeatureManager")

        print("=== ① 对每个 fm 拿到的 FeatureData：类型与可读性 ===")
        for fm, label in ((118, "Gusset"), (37, "EdgeFlange"), (34, "BaseFlange")):
            d = get_com_member(mgr, "CreateDefinition", fm)
            if d is None:
                print("  [%-10s] CreateDefinition(%d) → None" % (label, fm))
                continue
            print("  [%-10s] type=%s  repr=%s" % (label, type(d).__name__, str(d)[:44]))
            # 读几个属性
            for prop in ("Thickness", "BendRadius", "ProfileDistance1", "UseDefaultBendRadius"):
                try:
                    v = getattr(d, prop)
                    print("      read  %-22s → %r" % (prop, v))
                except Exception as exc:  # noqa: BLE001
                    print("      read  %-22s → ✗ %s" % (prop, str(exc)[:50]))
            # 写
            for prop, val in (("Thickness", 0.002), ("BendRadius", 0.002)):
                try:
                    setattr(d, prop, val)
                    print("      write %-22s → ✓" % prop)
                except Exception as exc:  # noqa: BLE001
                    print("      write %-22s → ✗ %s" % (prop, str(exc)[:50]))
            # 有没有 Set 前缀的方法
            cands = [n for n in dir(d) if n.lower().startswith(("set", "put"))][:8]
            print("      set*/put* 候选: %r" % cands)

        print()
        print("=== ② 换 makepy 强类型代理再试（若成功，真因就是绑定层）===")
        try:
            import win32com.client.gencache as gencache
            from win32com.client import Dispatch
            # 用 EnsureDispatch 拿强类型
            typed = gencache.EnsureDispatch("SldWorks.Application")
            tmgr = get_com_member(typed.ActiveDoc, "FeatureManager") \
                if typed.ActiveDoc is not None else None
            if tmgr is not None:
                td = tmgr.CreateDefinition(SM.SW_FM_SM_GUSSET)
                print("  强类型 CreateDefinition(118) → %s" % (type(td).__name__ if td else "None"))
                if td is not None:
                    try:
                        td.Thickness = 0.002
                        print("      ✓ **强类型代理下 Thickness 写成功** ⇒ 真因是绑定层！")
                    except Exception as exc:  # noqa: BLE001
                        print("      ✗ 强类型下也失败: %s" % str(exc)[:70])
            else:
                print("  ⚠ 拿不到强类型的 ActiveDoc")
        except Exception as exc:  # noqa: BLE001
            print("  ⚠ makepy 路径失败: %s" % str(exc)[:90])

        print()
        print("=== ③ 反射里 `Thickness` 到底是不是**可写**的 ===")
        print("  （官方文档的 Thickness.md 会写 Read/Write 权限）")
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
