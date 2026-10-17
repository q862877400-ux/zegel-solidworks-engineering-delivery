r"""@brief 探针：`ISldWorks.GetSafeArrayUtility()` 在 pywin32 上**可达吗**，`out` 形参能不能驱动。

## 为什么（轮 186）
一份外部评审把 `ISafeArrayUtility`（21 成员，台账 `used=0`）列为本项目**唯一高杠杆**的缺口：
```
「项目的已知事实里有一长串 BYREF / 数组 / VARIANT 的坑」——
  事实 12  空 Dispatch 参数包 VARIANT(VT_DISPATCH, None)
  事实 33  SelectByID2 / Select4 的 Callout 必须传 VARIANT(VT_DISPATCH, None)
  事实 68  Object& 出参必须填（VT_BYREF | VT_VARIANT）
  事实 123 CreateSpline 的数组实参必须包 VARIANT(VT_ARRAY | VT_R8)
  事实 167 AddRelation 必须包 VARIANT(VT_ARRAY | VT_DISPATCH)
⇒ 「官方给了工具集，我们在手搓」
```
★ 但**评审没验证可达性**（它自己 §十三 就写了「未连 SolidWorks」）。
⇒ 本探针只回答一件事：**它到底能不能用**（不能就按铁律 5 记"查不到/到不了"，别当缺口挂在报告里）。

## 判据（可证伪，逐项记）
```
① `sw.GetSafeArrayUtility()` ⇒ 返回什么（None / 一个 dispatch）
② `GetDouble(<普通 list>, 0)` ⇒ 能不能读（**不需要 out 形参**的那一半）
③ `PutDouble(<VT_BYREF|VT_VARIANT>, 0, 1.5)` ⇒ **out 形参回写了吗**（读 byref 的 .value）
④ `GetInfo` 的两个 `Int32&` ⇒ 同③的 byref 回写问题（事实 68 同族）
⑤ `PackVariant` 的 `ref Int32 Data` ⇒ 形态不明，如实记
★ 每项都记 **返回/异常原文**，不写"大概能/大概不能"。
```

## ⚠ 安全
`GetSafeArrayUtility` 在 `ISldWorks` 上 ⇒ **不需要文档**；`CommandInProgress` 置位；
全程不开文档、不建特征、不改任何东西；收尾**轮询 + 查到就点掉**。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_safearray_utility.py
# 定位:   给 Spec Kit `106` 判定 `ISafeArrayUtility` 是**可用工具**还是**又一条到不了的路**。
# 官方依据: `C:/swapi/types/ISafeArrayUtility/{_overview,PackVariant,PutDouble,GetDouble}.md` ·
#          反射 `ISldWorks.GetSafeArrayUtility() -> Object` · 出厂类型库
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "safearray-utility-probe.json")


def main() -> int:
    import pythoncom
    import win32com.client
    ev: dict = {"steps": []}
    sw = None
    try:
        import sw_connect
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass

        def rec(name, ok, detail, extra=None):
            ev["steps"].append({"step": name, "ok": bool(ok), "detail": str(detail)[:200],
                                **(extra or {})})
            print("  %s %-46s %s" % ("✓" if ok else "**✗**", name[:46], str(detail)[:74]))

        #: ① 拿到工具对象
        util = None
        try:
            util = sw_connect.call_com_member(sw, "GetSafeArrayUtility")
            rec("① ISldWorks.GetSafeArrayUtility()", util is not None, type(util).__name__)
            ev["util_type"] = type(util).__name__
        except Exception as exc:      # noqa: BLE001
            rec("① ISldWorks.GetSafeArrayUtility()", False,
                "%s: %s" % (type(exc).__name__, str(exc)[:60]))
            ev["util_type"] = "EXC:%s" % type(exc).__name__

        if util is None:
            print("\n  ⇒ **拿不到工具对象** ⇒ 后面不必试（按铁律 5：记「到不了」）")
        else:
            #: ② Get* 半边（不需要 out 形参）
            try:
                v = sw_connect.call_com_member(util, "GetDouble", [1.5, 2.5, 3.5], 1)
                rec("② GetDouble([1.5,2.5,3.5], 1) ⇒ 期望 2.5", abs(float(v) - 2.5) < 1e-9,
                    "拿到 %r" % (v,))
            except Exception as exc:      # noqa: BLE001
                rec("② GetDouble(<普通 list>, 1)", False,
                    "%s: %s" % (type(exc).__name__, str(exc)[:60]))

            #: ③ out 形参：PutDouble(out Object VariantArray, Index, Value)
            #:    ⚠ pywin32 迟到绑定下只能靠**显式 byref VARIANT** 拿回写（事实 68 同族）
            for label, holder in (
                ("③a byref VARIANT(None)", win32com.client.VARIANT(
                    pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)),
                ("③b 裸 None", None),
            ):
                try:
                    r = sw_connect.call_com_member(util, "PutDouble", holder, 0, 1.5)
                    val = getattr(holder, "value", holder)
                    rec("%s ⇒ PutDouble 回写" % label, val is not None,
                        "返回 %r · holder.value=%r" % (r, val))
                    if val is not None:
                        try:
                            got = sw_connect.call_com_member(util, "GetDouble", val, 0)
                            rec("    ↳ GetDouble(回写值, 0) ⇒ 期望 1.5",
                                abs(float(got) - 1.5) < 1e-9, "拿到 %r" % (got,))
                        except Exception as exc:      # noqa: BLE001
                            rec("    ↳ GetDouble(回写值, 0)", False,
                                "%s: %s" % (type(exc).__name__, str(exc)[:50]))
                except Exception as exc:      # noqa: BLE001
                    rec("%s ⇒ PutDouble" % label, False,
                        "%s: %s" % (type(exc).__name__, str(exc)[:60]))

            #: ④ Int32& 两个（GetInfo）
            try:
                a = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
                b = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
                sw_connect.call_com_member(util, "GetInfo", [1.0, 2.0], a, b)
                rec("④ GetInfo 的 Int32& ×2 回写", True, "a=%r b=%r" % (a.value, b.value))
            except Exception as exc:      # noqa: BLE001
                rec("④ GetInfo 的 Int32& ×2 回写", False,
                    "%s: %s" % (type(exc).__name__, str(exc)[:60]))

            #: ⑤ PackVariant 的 `ref Int32 Data` 形态不明 ⇒ 如实记一次尝试
            try:
                arr = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
                d = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
                r = sw_connect.call_com_member(util, "PackVariant", arr, 1, 0, d)
                rec("⑤ PackVariant(out,1,0,ref) ⇒ 形态试探", False,
                    "没抛错但形态未定：arr=%r d=%r" % (getattr(arr, "value", arr), d.value))
            except Exception as exc:      # noqa: BLE001
                rec("⑤ PackVariant(out,1,0,ref) ⇒ 形态试探", False,
                    "%s: %s" % (type(exc).__name__, str(exc)[:70]))
                ev["packvariant_tb"] = traceback.format_exc().strip().splitlines()[-2:]

            #: ⑥ ★★★ **定论扫描**：官方登记的**全部 21 个成员**逐个试（只试 5 个不下结论）
            #:    —— 轮 185 的教训：判据要**穷尽**、要锚在权威源（这里就是那份反射签名表）。
            ALL = ["GetBoolean", "GetBstr", "GetByte", "GetDispatch", "GetDouble", "GetInfo",
                   "GetLong", "GetLongLong", "GetShort", "GetUNKNOWN", "PackVariant",
                   "PutBoolean", "PutBstr", "PutByte", "PutDispatch", "PutDouble", "PutLong",
                   "PutLongLong", "PutShort", "PutUNKNOWN", "UnPackVariant"]
            reachable = []
            for nm in ALL:
                try:
                    m = getattr(util, nm)
                    reachable.append(nm)
                except Exception:      # noqa: BLE001
                    pass
            ev["members_total"] = len(ALL)
            ev["members_reachable"] = reachable
            rec("⑥ 官方 21 个成员里**迟到绑定可达**的", len(reachable) == len(ALL),
                "%d/%d ⇒ %s" % (len(reachable), len(ALL), reachable or "**一个都没有**"))

            #: ⑦ 内省：这个 dispatch 到底带不带类型信息（区分「接口不对」与「没有 dispinterface」）
            try:
                ti = util._oleobj_.GetTypeInfo()
                ta = ti.GetTypeAttr()
                names = [ti.GetDocumentation(i)[0] for i in range(ta.cFuncs)]
                ev["typeinfo_funcs"] = names
                rec("⑦ 类型信息里的方法名", bool(names),
                    "%d 个：%s" % (len(names), names[:8]))
            except Exception as exc:      # noqa: BLE001
                ev["typeinfo_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:80])
                rec("⑦ 类型信息内省", False,
                    "%s: %s ⇒ **没有可用的 dispinterface**" % (type(exc).__name__, str(exc)[:50]))
    except Exception as exc:      # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass

    import sw_connect as _sc
    found, dismissed, scanned = _sc.settle_residual_dialogs(settle_seconds=1.0)
    print("  收尾：发现 %d · 点掉 %d · 扫了 %d 个窗口" % (found, dismissed, scanned))
    ev["cleanup"] = {"found": found, "scanned": scanned}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
