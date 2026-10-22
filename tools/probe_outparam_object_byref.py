r"""@brief 裁决 A5 里那条悬案：**`Object&` 出参到底要不要传？**

## 悬案原文（`docs/signature-audit.md` 批次 7 的「一条未查证的遗留」）
`sw_hole_features.py` 的 4 处传了 `Object&` 出参，而 `audit_call_arity.py` 的**新**规则
把 `Object&` 排除（照 `GetErrorMessages(Object&, Object&, Object&)` = **0 参**那个例子）。
* ① `Object&` 与 `Int32&` 一样**必须传** ⇒ **规则对 `Object&` 也错，代码对**
* ② `Object&` **不必传** ⇒ 代码多传了无用参数（可能无害），**规则对**

**当时未做真机实验**（需要构造一个调用 `IHoleStandardsData` 的实测）⇒ 铁律 5 记「不猜」。

## 实验设计（照 `probe_outparam_convention.py` 的路子）
`ISldWorks.GetHoleStandardsData(HoleTypeID)` → `IHoleStandardsData`（null 仅当 HoleTypeID=5）。
然后对 `Boolean GetHoleStandards(Object& Standards, Object& Types)` 试三种形态：
```
A  不传任何出参      GetHoleStandards()
B  传两个 VARIANT(VT_BYREF|VT_DISPATCH, None)
C  传两个裸 None
```
**判读**：官方 arity = **2**。若 A 报 `DISP_E_PARAMNOTOPTIONAL`（「非选择性的参数」）
⇒ **出参是必填的** ⇒ **裁定 ①**（代码对、工具规则错）。
若 A 能跑通 ⇒ **裁定 ②**（规则对、代码多传）。

## 安全设计（轮 98 的模态框教训）
**只读**（`GetHoleStandardsData` / `GetHoleStandards` 都是查询），
不建几何、不碰用户文档 ⇒ 风险低；仍置 `CommandInProgress` 并在收尾查模态框。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/probe_outparam_object_byref.py
# 定位:   给 `docs/signature-audit.md` 批次 7 那条「未查证的遗留」取**真机**裁断。
# 官方依据: `C:\swapi\types\ISldWorks\GetHoleStandardsData.md` ·`C:\swapi\types\IHoleSta
#           ndardsData\GetHoleStandards.md` · 出厂反射
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as w
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "outparam-object-byref-evidence.json")
HOLE_TYPE_COUNTERBORE = 0      # swWzdCounterBore（官方：null 仅当 =5 swWzdLegacy）


def modal_dialogs() -> tuple:
    """★ 已改为**委托共享实现**（2026-10-01 轮 149）。"""
    try:
        from scripts.sw_connect import residual_dialogs
    except ImportError:
        from sw_connect import dismiss_residual_dialogs, residual_dialogs
    #: ★ 2026-10-01（轮 169）：**查到了就点掉**（兜底）——
    #: 只查不点的脚本在真发现弹窗时**什么也没处置**，弹窗还在 ⇒ 下一轮挂在这儿。
    _dialogs, _scanned = residual_dialogs()
    if _dialogs:
            dismiss_residual_dialogs()
    return _dialogs, _scanned
def main() -> int:
    import pywintypes
    from win32com.client import VARIANT      # ⚠ `pythoncom.VARIANT` **不存在**（第一版就栽在这）

    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
        print("   %s %-44s %s" % ("✓" if ok else "**✗**", name, str(detail)[:74]))

    sw = None
    try:
        import sw_connect
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass

        data = sw_connect.safe_get_com_member(sw, "GetHoleStandardsData", HOLE_TYPE_COUNTERBORE)
        chk("拿到 IHoleStandardsData（HoleTypeID=0 沉头孔）", data is not None,
            type(data).__name__ if data is not None else "**None**")
        ev["got_data"] = data is not None

        if data is not None:
            def attempt(label, args_factory):
                t0 = time.time()
                try:
                    args = args_factory()
                    r = sw_connect.safe_get_com_member(data, "GetHoleStandards", *args)
                    return label, "返回 %r" % (r,), False, time.time() - t0
                except pywintypes.com_error as exc:      # noqa: PERF203
                    code = exc.args[0] if exc.args else None
                    txt = exc.args[2][0] if len(exc.args) > 2 and exc.args[2] else str(exc)
                    return label, "com_error %s: %s" % (code, str(txt)[:60]), True, time.time() - t0
                except Exception as exc:      # noqa: BLE001
                    return label, "%s: %s" % (type(exc).__name__, str(exc)[:70]), True, time.time() - t0

            def mk_byref():
                #: ⚠ 用 `win32com.client.VARIANT`，不是 `pythoncom.VARIANT`（后者不存在
                #: ）
                import pythoncom as _pc
                return [VARIANT(_pc.VT_BYREF | _pc.VT_DISPATCH, None),
                        VARIANT(_pc.VT_BYREF | _pc.VT_DISPATCH, None)]

            def mk_byref_variant():
                #: ★ 照 `probe_outparam_convention.py` 对 `Int32&` 的**已知good形态**
                #: （`VARIANT(VT_BYREF|VT_I4, 0)` 通过）类推：容器出参用 `VT_BYREF|VT_VA
                #: RIANT`。
                import pythoncom as _pc
                return [VARIANT(_pc.VT_BYREF | _pc.VT_VARIANT, None),
                        VARIANT(_pc.VT_BYREF | _pc.VT_VARIANT, None)]

            forms = [
                ("A 不传出参", lambda: []),
                ("B 两个 VARIANT(VT_BYREF|VT_DISPATCH, None)", mk_byref),
                ("C 两个裸 None", lambda: [None, None]),
                ("D 两个 VARIANT(VT_BYREF|VT_VARIANT, None)", mk_byref_variant),
            ]
            results = []
            for label, fac in forms:
                lbl, detail, threw, _dt = attempt(label, fac)
                results.append({"form": lbl, "detail": detail, "threw": threw})
                print("      %-46s %s" % (lbl, detail))
            ev["forms"] = results

            # ★ 裁读：A 报「非选择性的参数」⇒ 出参**必填** ⇒ 裁定 ①
            a = results[0]
            not_optional = ("非选择性" in a["detail"]) or ("PARAMNOTOPTIONAL" in a["detail"].upper()) \
                or ("8002000E" in a["detail"].upper()) or ("-2147352578" in a["detail"])
            ev["verdict"] = ("out-required" if not_optional else
                             ("out-optional" if not a["threw"] else "inconclusive"))
            chk("★ 裁定：**A 形态报「非选择性的参数」** ⇒ Object& 出参是**必填**的",
                not_optional, "A: %s" % a["detail"])
    except Exception as exc:      # noqa: BLE001
        chk("整体探针", False, "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass

    modals, _win_scanned = modal_dialogs()
    chk("★ 收尾无残留模态框（已知事实 64 的检查）", (not modals) and _win_scanned > 0,
        "扫了 %d 个窗口 · %s" % (_win_scanned, "无模态框" if not modals else "有 %d 个: %s" % (len(modals), modals)))

    ev.update(passed=sum(1 for c in checks if c), total=len(checks),
              finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  ── %d/%d · 裁定：%s ──" % (ev["passed"], ev["total"], ev.get("verdict")))
    print("  ⚠ 只证 `GetHoleStandards` 这一个成员；**不证所有 Object& 出参都一样**。")
    return 0 if ev["verdict"] == "out-required" else 1


if __name__ == "__main__":
    raise SystemExit(main())
