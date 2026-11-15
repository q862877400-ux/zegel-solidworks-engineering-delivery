"""探针：`ISketch.CheckFeatureUse` 在 pywin32 下的**返回形态**（out 参数怎么给）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 业主 2026-11-07 指令：暂停主线，先把 SolidWorks 自带的评估/检测能力用 API 跑通。
#   业主手工用的「检查草图合法性」= 官方 `ISketch::CheckFeatureUse`：
#     签名 `int CheckFeatureUse(int FeatureType, out int OpenCount, out int ClosedCount)`
#     官方 Remarks 逐字：「This method is equivalent to the SOLIDWORKS interactive tool
#       **Check Sketch for Feature Usage**.」
#   枚举：`C:\\swapi\\enums\\swSketchCheckFeatureProfileUsage_e.md`（24 个特征类型）
#         `C:\\swapi\\enums\\swSketchCheckFeatureStatus_e.md`（24 个状态码）
# 本探针只回答一件事：pywin32 迟到绑定下，两个 `out` 参数怎么回来
#   （可能是 (retval, open, closed) 元组，也可能要 VARIANT byref）。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts import sw_connect as c  # noqa: E402
import scripts.sw_feature_readback as f_  # noqa: E402


def find_doc(sw, title):
    for d in list(c.get_com_member(sw, "GetDocuments") or []):
        if str(c.get_com_member(d, "GetTitle")) == title:
            return d
    return None


def get_sketch(doc):
    for n in (f_.feature_names(doc) or []):
        if "草图" in n:
            feat = c.get_com_member(doc, "FeatureByName", n)
            for meth in ("GetSpecificFeature2", "GetSketch"):
                try:
                    sk = c.get_com_member(feat, meth)
                    if sk is not None:
                        return n, sk
                except Exception:  # noqa: BLE001
                    continue
    return None, None


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    sw, _ = c.connect_solidworks(wait_seconds=10)
    for title in ("零件46", "零件56"):
        doc = find_doc(sw, title)
        if doc is None:
            print(f"✗ 找不到 {title}")
            continue
        print("=== ", title, " ===")
        sk_name, sk = get_sketch(doc)
        print("草图 =", sk_name, " 对象 =", type(sk).__name__ if sk else None)
        if sk is None:
            continue
        for ft, label in ((3, "BOSSEXTRUDE(拉伸凸台)"),
                          (1, "BASEEXTRUDE(基体拉伸)"),
                          (0, "UNSET(任意特征通用检查)")):
            #: ★ 官方签名是 `int CheckFeatureUse(int, out int, out int)` ——
            #:   pywin32 迟到绑定下 `out` **必须**显式传 `VARIANT(VT_BYREF|VT_I4)`，
            #:   少传就报「非选择性的参数」（实测三次）。
            import pythoncom
            import win32com.client
            open_cnt = win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            closed_cnt = win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            try:
                r = c.get_com_member(sk, "CheckFeatureUse",
                                     ft, open_cnt, closed_cnt)
                print(f"  FeatureType={ft} {label}: 返回={r!r}  "
                      f"开放轮廓={open_cnt.value} 闭合轮廓={closed_cnt.value}")
            except Exception as exc:  # noqa: BLE001
                print(f"  FeatureType={ft} {label}: 异常 {str(exc)[:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
