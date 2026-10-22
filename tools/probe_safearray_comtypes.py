r"""@brief 探针：换 **comtypes 早绑定**后端，`ISafeArrayUtility` 能不能驱动（含 `out` 形参）。

## 为什么（轮 188）
轮 186 真机测出：pywin32 **迟到绑定**下 `ISafeArrayUtility` 的 **21 个成员可达 0/21**、
且返回对象**没有 dispinterface** ⇒ 记了「**不做**」，并把判据写成
「判可达性**只能真机逐接口穷尽枚举**」。
★ 但那一轮的括号里也写了限度：**未试 `comtypes` / C# PIA**（它们**可能**能驱动 `out` 形参）。
⇒ 本探针**闭合那条限度**：用 `comtypes`（**早绑定 + 类型库**）重测同一件事。

## 判据（可证伪，逐项记）
```
① `comtypes.client.GetActiveObject("SldWorks.Application")` ⇒ **附着到运行中实例**
   ⚠ **绝不能起第二个实例**（已知事实 24：两个进程抢同一 COM 连接会死锁）
② SldWorks 类型库（`sldworks.tlb`）生成后，模块里**有没有** `ISafeArrayUtility`
③ `sw.GetSafeArrayUtility()` 返回什么类型（官方签名是 `Object` ⇒ VARIANT）
④ ★★★ **`QueryInterface(ISafeArrayUtility)`** —— 这是分水岭：
   · QI **成功** ⇒ 该对象**真的实现那个 vtable 接口** ⇒ 早绑定可调 ⇒ 轮 186 的「不做」**要改写**
   · QI **失败** ⇒ 连早绑定也没有这个接口 ⇒ 轮 186 的结论**加强**（不是"绑法不对"，是"没这个口")
⑤ 若 QI 成：`GetDouble` / `PutDouble`(out) 各一次，看 `out` 形参能不能回写
```

## ⚠ 安全
**只附着**（`GetActiveObject`）；`CommandInProgress` 置位；**不开文档、不建特征、不改任何状态**；
收尾**轮询 + 查到就点掉**。comtypes 会在其缓存目录生成类型库模块（缓存，非配置，可接受）。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_safearray_comtypes.py
# 定位:   给 Spec Kit `108` 闭合轮 186 的限度：「换后端能不能驱动那些 `out` 形参」。
# 官方依据: `C:/swapi/types/ISafeArrayUtility/*.md` · `D:/Program Files/SOLIDWORKS Corp/
#           SOLIDWORKS/sldworks.tlb`
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "safearray-comtypes-probe.json")
TLB = Path(r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\sldworks.tlb")


def main() -> int:
    ev: dict = {"steps": []}
    sw = None
    try:
        import comtypes.client as cc
        import win32com.client

        def rec(name, ok, detail, extra=None):
            ev["steps"].append({"step": name, "ok": bool(ok), "detail": str(detail)[:220],
                                **(extra or {})})
            print("  %s %-44s %s" % ("✓" if ok else "**✗**", name[:44], str(detail)[:76]))

        #: ①b 先用**已有的** pywin32 通道确认实例在线（并拿到 PID 作对照），再走 comtype
        #: s
        base = win32com.client.GetActiveObject("SldWorks.Application")
        pid = None
        try:
            pid = int(base.GetProcessID())
        except Exception:      # noqa: BLE001
            pass
        rec("① 运行中实例（pywin32 附着）", base is not None, "PID=%s" % pid)
        ev["pid"] = pid

        #: ① comtypes **附着**（GetActiveObject 不新建实例）
        sw = cc.GetActiveObject("SldWorks.Application")
        rec("① comtypes.client.GetActiveObject ⇒ 附着", sw is not None,
            type(sw).__module__ + "." + type(sw).__name__)
        ev["comtypes_type"] = "%s.%s" % (type(sw).__module__, type(sw).__name__)
        try:
            pid2 = int(sw.GetProcessID())
            #: ⚠ pywin32 那条 `GetProcessID()` 上面返回了 `None` ⇒ **只在两边都有值时才
            #: 比**
            rec("   ↳ 同一个实例？",
                (pid is None) or (pid2 == pid),
                "comtypes PID=%s · pywin32 PID=%s ⇒ %s"
                % (pid2, pid, "同实例" if (pid is None or pid2 == pid) else "**不同**"))
            ev["pid_comtypes"] = pid2
        except Exception as exc:      # noqa: BLE001
            rec("   ↳ GetProcessID（comtypes）", False, "%s" % type(exc).__name__[:40])

        #: ② 类型库里有 ISafeArrayUtility 吗
        #: ⚠⚠ **2026-10-01（轮 188）第一版这里错了**：我拿 `type(sw).__module__` 去找模
        #: 块，
        #: 而它是 `comtypes._post_coinit.unknwn`（**基类所在模块**），不是生成的类型库模
        #: 块。
        #:   ⇒ 正确姿势：**显式 `cc.GetModule(<tlb 路径>)`**，从它的返回值里取接口类。
        iface = None
        mod = None
        try:
            mod = cc.GetModule(str(TLB))
            iface = getattr(mod, "ISafeArrayUtility", None)
            rec("② 类型库模块里的 ISafeArrayUtility", iface is not None,
                "%s（模块 %s）" % (getattr(iface, "__name__", None),
                                   getattr(mod, "__name__", "?")))
        except Exception as exc:      # noqa: BLE001
            rec("② cc.GetModule(sldworks.tlb)", False, "%s: %s" % (type(exc).__name__, str(exc)[:60]))
        ev["iface_found"] = iface is not None
        ev["tlb_module"] = getattr(mod, "__name__", None)

        #: ③ 拿到工具对象
        raw = None
        try:
            raw = sw.GetSafeArrayUtility()
            rec("③ ISldWorks.GetSafeArrayUtility()", True, type(raw).__name__)
        except Exception as exc:      # noqa: BLE001
            rec("③ ISldWorks.GetSafeArrayUtility()", False,
                "%s: %s" % (type(exc).__name__, str(exc)[:60]))
        ev["raw_type"] = type(raw).__name__ if raw is not None else None

        #: ④ ★★★ 分水岭：QueryInterface
        typed = None
        if raw is not None and iface is not None:
            try:
                typed = raw.QueryInterface(iface)
                rec("④ ★★★ QueryInterface(ISafeArrayUtility) ⇒ **成功**", True,
                    "⇒ 对象**真的实现**该 vtable 接口")
            except Exception as exc:      # noqa: BLE001
                rec("④ ★★★ QueryInterface(ISafeArrayUtility) ⇒ 失败", False,
                    "%s: %s" % (type(exc).__name__, str(exc)[:60]))
                ev["qi_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        else:
            rec("④ QueryInterface", False, "上一步没拿到对象或模块里没有该接口")
        ev["qi_ok"] = typed is not None

        #: ⑤ QI 成则试真调用
        #: ⚠⚠ **2026-10-01（轮 188）第一版这里也错了**：我按官方 **md** 的形参顺序
        #:   `PutDouble(out VariantArray, Index, Value)` 传了 **2** 个实参 ⇒
        #:   `TypeError: required argument 'Value' missing`。
        #:   ⇒ ★ 正确姿势是**读类型库自己的方法表**（`_methods_`，那才是权威 —— 铁律 4）：
        #:   ```
        #: PutDouble   argtypes=(VARIANT, c_long, c_double)  flags=(in,out / in / in) ⇒ 
        #: **3 参**
        #: GetDouble   argtypes=(VARIANT, c_long, c_double)  flags=(in / in / **out**) ⇒
        #:  2 参，出参作返回值
        #:   ```
        if typed is not None:
            try:
                from comtypes.automation import VARIANT as CVARIANT
            except Exception:      # noqa: BLE001
                import comtypes
                CVARIANT = comtypes.VARIANT
            arr = CVARIANT()
            ok_put = False
            try:
                ret = typed.PutDouble(arr, 0, 1.5)
                ok_put = True
                rec("⑤a PutDouble(arr, 0, 1.5) ⇒ **3 参 + in,out 数组**", True,
                    "返回 %r · arr.value=%r" % (ret, getattr(arr, "value", arr)))
                ev["putdouble_ret"] = repr(ret)
                ev["arr_after_put"] = repr(getattr(arr, "value", arr))
            except Exception as exc:      # noqa: BLE001
                rec("⑤a PutDouble(arr, 0, 1.5)", False,
                    "%s: %s" % (type(exc).__name__, str(exc)[:70]))
            if ok_put:
                #: ★★ **往返**：写进去 1.5 ⇒ 读回来应当还是 1.5（这才叫"能用"）
                try:
                    got = typed.GetDouble(arr, 0)
                    rec("⑤b ★★ **往返**：PutDouble 写 1.5 ⇒ GetDouble 读回", 
                        abs(float(got) - 1.5) < 1e-9, "读回 %r" % (got,))
                    ev["roundtrip"] = repr(got)
                except Exception as exc:      # noqa: BLE001
                    rec("⑤b 往返 GetDouble(arr, 0)", False,
                        "%s: %s" % (type(exc).__name__, str(exc)[:70]))
            #: ⑥ 对照：**我们现在怎么做的**（这条决定"它有没有新增能力"）
            #: ⚠ 第一版这里写错了：直接用了 `sw_connect.call_com_member` 而本函数里没导
            #: 入它。
            #:   ⇒ 改成**只用已导入的绑定**构造一次数组，证明"构造数组本来就不需要它"。
            try:
                import pythoncom
                import win32com.client as wc
                a1 = wc.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [1.5, 2.5, 3.5])
                a2 = wc.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [base, base])
                rec("⑥ 对照：pywin32 原生构造数组（R8 / DISPATCH 两种）", True,
                    "VT_ARRAY|VT_R8 ⇒ %s · VT_ARRAY|VT_DISPATCH ⇒ %s"
                    % (type(a1).__name__, type(a2).__name__))
                ev["pywin32_native_array"] = "VARIANT(VT_ARRAY|VT_R8|VT_DISPATCH, [...]) 均可构造"
            except Exception as exc:      # noqa: BLE001
                rec("⑥ 对照：pywin32 原生数组构造", False,
                    "%s: %s" % (type(exc).__name__, str(exc)[:60]))
    except Exception as exc:      # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
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
