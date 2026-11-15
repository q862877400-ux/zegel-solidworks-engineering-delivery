"""跑通 SolidWorks 自带诊断接口（逐个验证能不能真用）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 业主 2026-11-07 指令：「把各种Debug工具能力全部跑通，然后做成一个整个项目通用的
#   Debug模块，遇到问题先到Debug模块里寻找Debug解法」
# 逐个验证的对象（官方页均在 `C:\swapi\types\`）：
#   · `IBody2::Check3`        属性，返回 `IFaultEntity`（实体是否有效）
#   · `IBody2::Diagnose()`    返回 `DiagnoseResult`（实体诊断）
#   · `IFeature::GetErrorCode2(out bool IsWarning)` → 特征错误码
#   · `ISketch::GetConstrainedStatus()` → 草图约束状态
#   · `ISketch::CheckFeatureUse(...)`   → 草图能否用于某特征（已做成模块）
#   · `ISldWorks::GetErrorMessages(out,out,out)` → 本会话最近 20 条消息
#   另：`IEdge::Check` / `IFace2::Check` → 边/面有效性
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

import pythoncom
import win32com.client

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts import sw_connect as c  # noqa: E402
from scripts import sw_sketch_check as sc  # noqa: E402
import scripts.sw_feature_readback as f_  # noqa: E402

TARGET = "零件46"


def byref_i4(v=0):
    return win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, v)


def byref_bool(v=False):
    return win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, v)


def byref_variant():
    return win32com.client.VARIANT(
        pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    sw, _ = c.connect_solidworks(wait_seconds=15)
    doc = None
    for d in list(c.get_com_member(sw, "GetDocuments") or []):
        if str(c.get_com_member(d, "GetTitle")) == TARGET:
            doc = d
            break
    if doc is None:
        print(f"✗ 找不到 {TARGET}")
        return 1
    print("文档 =", c.get_com_member(doc, "GetTitle"))

    # ── ① 实体有效性 ──
    print("\n=== ① 实体 Check3 / Diagnose ===")
    bodies = list(c.get_com_member(doc, "GetBodies2", 0, True) or [])
    print(f"实体数 = {len(bodies)}")
    for i, b in enumerate(bodies):
        try:
            fe = c.get_com_member(b, "Check3")
            n = -1
            try:
                n = len(list(fe or []))
            except Exception:  # noqa: BLE001
                pass
            print(f"  体{i} Check3 = {fe!r}  （故障实体数约 {n}）")
        except Exception as exc:  # noqa: BLE001
            print(f"  体{i} Check3 异常 {str(exc)[:90]}")
        try:
            dr = c.get_com_member(b, "Diagnose")
            print(f"  体{i} Diagnose = {dr!r}")
        except Exception as exc:  # noqa: BLE001
            print(f"  体{i} Diagnose 异常 {str(exc)[:90]}")

    # ── ② 特征错误码 ──
    print("\n=== ② 特征 GetErrorCode2 ===")
    for name in (f_.feature_names(doc) or []):
        feat = c.get_com_member(doc, "FeatureByName", name)
        if feat is None:
            continue
        iw = byref_bool(False)
        try:
            code = int(c.get_com_member(feat, "GetErrorCode2", iw))
            if code != 0:
                kind = "警告" if iw.value else "错误"
                print(f"  {name}: code={code} ({kind})")
        except Exception as exc:  # noqa: BLE001
            print(f"  {name}: 异常 {str(exc)[:70]}")
    print("  （只打印 code≠0 的特征）")

    # ── ③ 草图约束状态 + 合法性 ──
    print("\n=== ③ 草图 GetConstrainedStatus / CheckFeatureUse ===")
    for name in (f_.feature_names(doc) or []):
        if "草图" not in str(name):
            continue
        sk = sc.sketch_of(doc, name)
        if sk is None:
            continue
        try:
            cs = int(c.get_com_member(sk, "GetConstrainedStatus"))
            print(f"  {name}: 约束状态 = {cs}")
        except Exception as exc:  # noqa: BLE001
            print(f"  {name}: 约束状态异常 {str(exc)[:70]}")
        try:
            chk = sc.check_sketch(sk, sc.FEATURE_TYPES["BOSSEXTRUDE"])
            print(f"  {name}: {chk.report()}")
        except Exception as exc:  # noqa: BLE001
            print(f"  {name}: 合法性异常 {str(exc)[:70]}")

    # ── ④ 会话级错误消息 ──
    print("\n=== ④ ISldWorks::GetErrorMessages ===")
    try:
        m1, m2, m3 = byref_variant(), byref_variant(), byref_variant()
        cnt = int(c.get_com_member(sw, "GetErrorMessages", m1, m2, m3))
        print(f"  返回条数 = {cnt}")
        msgs = list(m1.value or []) if m1.value is not None else []
        types_ = list(m3.value or []) if m3.value is not None else []
        for i, msg in enumerate(msgs[-6:]):
            t = types_[i] if i < len(types_) else "?"
            print(f"    [{t}] {str(msg)[:110]}")
    except Exception as exc:  # noqa: BLE001
        print(f"  异常 {str(exc)[:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
