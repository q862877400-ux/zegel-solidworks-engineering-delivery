"""★ 探针：D 项（临时另存 → 展开 DXF）—— ★ 一个正例 + 两个负例。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · D 项的真机探针）
# 文件:   tools/probe_spec211_flatsave.py
# 定位:   ★ 用户 2026-10-07 指令：「★ **D 我允许你做**」✓ ——
#   ★★ D = 「平板型式 / 导出 DXF」那一项。★ 它此前判「不做」的唯一理由：
#     ★ 官方的真前置是「**已保存**的钣金件」（★ `docs/dead-ends.md` 轮 407 那条 ✓），
# ★★ 而本仓硬约束⑦原先是「**一律不保存文档**」⇒ ★ `export_flat_pattern_dxf` **显式拒绝**
#  ✓
#   ⇒ ★★★ **用户授权后，本批把它做成**受控例外**** ✓（★ 见 `scripts/sw_export.py` 的
#     `allow_temporary_save` / `temporary_save_dir` 两个新形参 ✓）
# 判据（★ 本批的验收 = **一正两负**，★ 事实 62：门禁只靠负例证明）：
# ★ **负例①**：★ 默认（`allow_temporary_save=False`）⇒ **必须拒绝** ✓（★ 行为与从前一致
# ✓）
#   ★★ **负例②**：★ 授权了、★ 但 `temporary_save_dir` **在仓库外** ⇒ **必须拒绝** ✓
#      （★ 那是「真机跑不许写到用户目录」那条硬约束的落点 ✓）
#   ★★★ **正例**：★ 授权 + 仓库内目录 ⇒ ★ **临时另存 + 导出 DXF 成功** ✓
#   ★★ 判据一律**回读**：★ **DXF 文件真的存在吗**（★ 不看返回值 —— 事实 8 ✓）；
#     ★ 并记**临时零件落在哪**（★ 必须**在仓库内** ✓）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

WORK = ROOT / "output" / "spec211-d-flatsave"
#: ★★ 负例②要用的"仓库外"路径（★ 用户目录 —— ★ **只声明、不写** ✓）
OUTSIDE = str(Path.home() / "Documents" / "dsh-should-be-refused")


def _sheet_metal_part(sw):
    """★ 建一个**未保存**的钣金件（★ 关键：★ 不调 `save_document` —— 那正是要触发的前置缺口 ✓）。"""
    import sw_connect
    import sw_part
    import sw_sheet_metal as sm

    model = sw_connect.new_document(sw, "part")
    sw_part.start_sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, 0.0, 0.0, 80.0, 60.0)
    sk = sw_part.current_sketch_name(model)
    sw_part.end_sketch(model)
    spec = sm.BaseFlangeSpec(
        thickness=float(sw_connect.mm(2.0)),
        bend_radius=float(sw_connect.mm(1.0)),
        depth=float(sw_connect.mm(40.0)),
    )
    sm.create_base_flange(model, sk, spec)
    return model


def main() -> int:
    import sw_connect
    import sw_export as e_

    out: dict = {"purpose": "★ D 项：临时另存 → 展开 DXF（★ 一正两负）", "cases": []}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    WORK.mkdir(parents=True, exist_ok=True)

    def _case(name: str, fn) -> dict:
        row = {"case": name}
        try:
            res = fn()
            row["raised"] = None
            row["result"] = str(res)
        except Exception as e:  # noqa: BLE001
            row["raised"] = "%s: %s" % (type(e).__name__, str(e)[:150])
        out["cases"].append(row)
        print(
            "★ %-34s ⇒ %s"
            % (
                name,
                ("拒绝 ✓（" + row["raised"][:70] + "）")
                if row["raised"]
                else ("完成 · " + row["result"][:50]),
            )
        )
        return row

    #: ★ **负例①**：默认 ⇒ 必须拒绝（★ 行为与从前一致 ✓）
    m1 = _sheet_metal_part(sw)
    dxf1 = WORK / "refused-default.dxf"
    r1 = _case(
        "负例① 默认（allow=False）", lambda: e_.export_flat_pattern_dxf(m1, str(dxf1))
    )
    r1["dxf_exists"] = dxf1.is_file()

    #: ★★ **负例②**：授权了、★ 而临时目录在**仓库外** ⇒ 必须拒绝
    m2 = _sheet_metal_part(sw)
    dxf2 = WORK / "refused-outside.dxf"
    r2 = _case(
        "负例② 授权但目录在仓库外",
        lambda: e_.export_flat_pattern_dxf(
            m2, str(dxf2), allow_temporary_save=True, temporary_save_dir=OUTSIDE
        ),
    )
    r2["dxf_exists"] = dxf2.is_file()
    r2["outside_dir_created"] = Path(OUTSIDE).exists()

    #: ★★★ **正例**：授权 + 仓库内目录 ⇒ 临时另存 + 导出成功
    m3 = _sheet_metal_part(sw)
    dxf3 = WORK / "flat.dxf"
    tempdir = WORK / "_temp_save"
    r3 = _case(
        "正例 授权 + 仓库内目录",
        lambda: e_.export_flat_pattern_dxf(
            m3, str(dxf3), allow_temporary_save=True, temporary_save_dir=str(tempdir)
        ),
    )
    #: ★★ 判据一律**回读**（★ 不看返回值 ✓）
    r3["dxf_exists"] = dxf3.is_file()
    r3["dxf_bytes"] = dxf3.stat().st_size if dxf3.is_file() else 0
    r3["temp_parts"] = (
        sorted(p.name for p in tempdir.glob("*.sldprt")) if tempdir.is_dir() else []
    )
    r3["temp_dir_inside_repo"] = str(tempdir).lower().startswith(str(ROOT).lower())
    print(
        "   ★★ 回读：DXF 存在=%r（%d 字节）· ★ 临时零件=%r · ★ 在仓库内=%r"
        % (
            r3["dxf_exists"],
            r3["dxf_bytes"],
            r3["temp_parts"],
            r3["temp_dir_inside_repo"],
        )
    )

    #: ★★★ **定案**
    neg1_ok = r1["raised"] is not None and not r1["dxf_exists"]
    neg2_ok = (
        r2["raised"] is not None
        and not r2["dxf_exists"]
        and not r2["outside_dir_created"]
    )
    pos_ok = r3["raised"] is None and r3["dxf_exists"] and r3["temp_dir_inside_repo"]
    out["verdicts"] = {
        "neg1_default_refused": neg1_ok,
        "neg2_outside_refused": neg2_ok,
        "pos_exported": pos_ok,
    }
    if neg1_ok and neg2_ok and pos_ok:
        out["verdict"] = (
            "★★★★★ **D 项成立** —— ★ 负例①（默认拒）✓ · ★★ 负例②（仓库外拒、★ 且**没在用户目录建任何东西**）✓ · "
            "★★★ 正例（仓库内临时另存 + 导出 DXF，★ 回读 **%d 字节** ✓）✓"
            % r3["dxf_bytes"]
        )
    else:
        out["verdict"] = (
            "★★ **未全过**：★ 负例①=%r · ★ 负例②=%r · ★ 正例=%r ⇒ ★ 如实记、★ 不硬说成功"
            % (neg1_ok, neg2_ok, pos_ok)
        )
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-d-flatsave.json"
    p.write_text(
        json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    import traceback

    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "spec211-d-flatsave-traceback.txt").write_text(
            tb, encoding="utf-8"
        )
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)
