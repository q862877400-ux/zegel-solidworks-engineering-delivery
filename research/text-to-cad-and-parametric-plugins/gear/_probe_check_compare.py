"""对比：方形草图（确定可拉伸）vs 齿轮草图（拉伸失败）的 CheckFeatureUse 结果。

# ── 来源 ─────────────────────────────────────────────────────────────
# 目的：判定 `swSketchCheckFeatureStatus_e = 15`（ClosedWantOpen）到底是不是「有问题」。
#   做法：同一个 SolidWorks 会话里建一个肯定能拉伸的正方形，跑同一个检查。
#       · 方形返回 0（OK）     ⇒ 15 是真问题码，齿轮草图确实不合法
#       · 方形也返回 15        ⇒ 15 是常态，这个检查判不了齿轮的问题
# 官方：`ISketch::CheckFeatureUse(int FeatureType, out int OpenCount, out int ClosedCount)`
#   等价于工具「检查草图合法性」；`swSketchCheckFeature_BOSSEXTRUDE = 3`
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
from scripts import sw_part as P  # noqa: E402
import scripts.sw_feature_readback as f_  # noqa: E402

STATUS = {
    0: "OK 可用", 1: "轮廓自相交", 2: "实体自相交", 3: "实体自相交(未指明)",
    4: "某端点被多个实体错误共享", 5: "空草图", 6: "含开放轮廓",
    7: "轮廓多于一个", 8: "含零长度实体", 9: "开放轮廓多于一个",
    10: "已无开放轮廓", 11: "同时有开放与闭合轮廓", 12: "轮廓相互相交",
    13: "轮廓互不相连", 14: "轮廓是开放的", 15: "轮廓是闭合的(却要求开放)",
    16: "轮廓双重嵌套", 17: "轮廓多于一个", 18: "应只含一条开放轮廓",
    19: "应只含一条闭合轮廓", 20: "应为单开放或多互不相连闭合",
    21: "应含中心线", 22: "所选轮廓开放或不明确",
    23: "旋转轮廓不能穿过/点触中心线", -1: "未知错误",
}


def check_feature_use(sk, feature_type: int):
    """跑 CheckFeatureUse，返回 (status, open_count, closed_count)。"""
    oc = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    cc = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    r = c.get_com_member(sk, "CheckFeatureUse", int(feature_type), oc, cc)
    return int(r), int(oc.value), int(cc.value)


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

    sw, _ = c.connect_solidworks(wait_seconds=15)

    # ① 方形对照
    sq = c.new_document(sw, "part")
    with P.sketch(sq, "Front Plane") as skn:
        P.sketch_line(sq, 0.0, 0.0, 10.0, 0.0)
        P.sketch_line(sq, 10.0, 0.0, 10.0, 10.0)
        P.sketch_line(sq, 10.0, 10.0, 0.0, 10.0)
        P.sketch_line(sq, 0.0, 10.0, 0.0, 0.0)
    _, sk_sq = get_sketch(sq)
    st, oc, cc = check_feature_use(sk_sq, 3)
    print(f"方形（10×10，4 条直线）：status={st} {STATUS.get(st,'?')}  "
          f"开放={oc} 闭合={cc}")

    # ② 齿轮草图
    gear = None
    for d in list(c.get_com_member(sw, "GetDocuments") or []):
        if str(c.get_com_member(d, "GetTitle")) == "零件46":
            gear = d
            break
    if gear is not None:
        gn, sk_g = get_sketch(gear)
        st2, oc2, cc2 = check_feature_use(sk_g, 3)
        print(f"齿轮（120 段样条+圆弧）：status={st2} {STATUS.get(st2,'?')}  "
              f"开放={oc2} 闭合={cc2}")
        print()
        if st == 0 and st2 != 0:
            print("⇒ 判定：**15 是真问题码**，方形通过、齿轮不通过 "
                  "⇒ 该检查能判出齿轮草图的缺陷")
        elif st == st2:
            print(f"⇒ 判定：两者同为 {st} ⇒ 该检查**判不出**齿轮的问题")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
