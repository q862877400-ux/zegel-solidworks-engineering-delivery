"""★ 探针：那三个"从没查过"的参数式成员**到底存不存在** —— ★ 真机反射直调。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · 收口后**加做**：外部覆盖侦察的决定性实验）
# 文件:   tools/probe_spec211_external_members.py
# 定位:   ★ 用户 2026-10-07 指令：「★ **其他的找找别的项目有无覆盖，多想想别的办法**」✓
#   ⇒ ★ 扫四家克隆（`C:\swprojects\{Eduardof0nt,andrewbartels1,SolidworksMCP-TS,Slacker-LLC}`）
#     ★★★ **发现三家用了本仓从没查过的成员** ✓：
#       · ★ `scripts/...`（Eduardof0nt `sw_client.py:2580`）：`FeatureManager.InsertBoundaryBoss(False, False, 0, 0, 0.0, 0.0, False, False)` —— ★ **8 参** ✓
#       · ★ 同文件 `:2603`：`InsertCurveDrivenPattern(count, spacing, equal, False×5, False, 0, 0, 0)` —— ★ **12 参** ✓
#       · ★ 同文件 `:1577`：`InsertTrimSurface2(0, False, False, False, False, 0.0, 0.0)` —— ★ **7 参** ✓
#       · ★ 同文件 `:1528`：`InsertKnitSurface(True, False, 0.0, True)` —— ★ **4 参** ✓
#       · ★ 另（vespo92 `vba-part.ts:308/447/626`）：`InsertBoundaryBoss2` · `InsertCurveDrivenPattern` · `InsertKnitSurface2` ✓
#   ★★★★ **而本规格全程只查了 `swapi` 一源** ✗：
#     · `C:\swapi\types\IFeatureManager\` 里**这四个成员都查不到** ✗
#     · ★ 而**铁律 4 要求三源互证、并以出厂类型库反射为裁决者** ✓
#     · ★★ 且我第一次查 CHM 只 match 了**文件名**（★ 而 CHM 页名可能是别名 ✗）
#   ⇒ ★★★★★ **所以本探针做的是最便宜、也最决定性的一步：**
#     ★★ **在真机上反射直调** —— ★ **成员存在 ⇒ 它响应**（★ 参数不对会是**另一种**错 ✓）；
#        ★ **成员不存在 ⇒ `get_com_member` 报"名字不在这个接口上"** ✓
#     ⇒ ★★★ **两者分得很清**，★ 而那是**唯一能裁决**的读法 ✓
# 判据:   ★★ 每条**独立落三类读数**：★ ① 成员能否取到（★ `exists` ✓）· ★② 抛什么（★ 若取不到，
#     错里会带 `InsertBoundaryBoss` 那样的名字 ✓）· ★③ **建成吗**（★ 特征树增量 ✓）
#   ★★ 前置逐条落布尔字段（★ 「读数无效」与「真的不建」长得一模一样 —— ★ 已六次 ✓）
#   ★⚠ **参数是**抄自外部项目**的**（★ 不是官方签名 ✗）—— ★★ **那本身就是待验证的东西** ✓：
#     ★ 若成员存在而参数不对 ⇒ ★ **官方签名要去 CHM/反射补** ✓
# 许可:   本仓库 MIT。★ 外部项目的实现**只读**（★ 用于对照成员名与参数个数，
#          ★ 不抄代码、★ 不抄文本 —— ★ 铁律 6 与铁律 1 ✓）。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

WORK = ROOT / "output" / "spec211-external-members"

#: ★ 要试的四个成员 + 它们**抄自外部项目**的实参（★ 参数个数取自 Eduardof0nt 的调用原文 ✓）
CANDIDATES = (
    ("InsertBoundaryBoss", (False, False, 0, 0, 0.0, 0.0, False, False)),
    ("InsertBoundaryBoss2", (False, False, 0, 0, 0.0, 0.0, False, False)),
    ("InsertCurveDrivenPattern", (3, 0.03, True, False, False, False, False, False, False, 0, 0, 0)),
    ("InsertTrimSurface2", (0, False, False, False, False, 0.0, 0.0)),
    ("InsertKnitSurface", (True, False, 0.0, True)),
    ("InsertKnitSurface2", (0.0001, True, False, True)),
)


def _fnames(model):
    import sw_surface_features as SF
    return SF.feature_names(model)


def main() -> int:
    import sw_connect
    import sw_part
    import sw_selection_spec as SS

    out: dict = {"purpose": "★ 反射直调：那三个成员到底存不存在（★ 四家外部项目的对照）",
                 "params_source": "★ 实参个数抄自 Eduardof0nt 的调用原文（★ 不是官方签名）",
                 "runs": []}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    WORK.mkdir(parents=True, exist_ok=True)

    #: ★ 建零件 + 两张草图轮廓（★ 边界凸台要 2+ 轮廓 ✓）
    model = sw_connect.new_document(sw, "part")
    for (x1, y1, x2, y2) in ((0.0, 0.0, 40.0, 30.0), (60.0, 0.0, 100.0, 30.0)):
        sw_part.start_sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, x1, y1, x2, y2)
        sw_part.end_sketch(model)
    sketches = [n for n in _fnames(model) if n.startswith("草图")]
    out["sketches"] = sketches
    print("★ 轮廓草图 ⇒ %r" % sketches)

    fm = sw_connect.get_com_member(model, "FeatureManager")
    print("★ FeatureManager ⇒ %s" % ("取到" if fm is not None else "拿不到 ✗"))

    for name, args in CANDIDATES:
        row: dict = {"member": name, "arity_tried": len(args)}
        #: ① **成员能不能取到**（★ 取不到 ⇒ `get_com_member` 会报"名字不在这个接口上" ✓）
        exists = False
        probe_exc = None
        try:
            sw_connect.get_com_member(fm, name)
            exists = True
        except Exception as e:                                          # noqa: BLE001
            probe_exc = "%s: %s" % (type(e).__name__, str(e)[:120])
        row["member_exists"] = exists
        row["probe_exception"] = probe_exc

        #: ② **选两张草图**（★ 边界凸台的前置 ✓）
        sel_ok = False
        try:
            SS.clear_selection(model)
            ext = sw_connect.get_com_member(model, "Extension")
            ok1 = bool(sw_part._select_by_id(ext, sketches[0], "SKETCH", append=False, mark=0)) if sketches else False
            ok2 = bool(sw_part._select_by_id(ext, sketches[1], "SKETCH", append=True, mark=0)) if len(sketches) > 1 else False
            sel_ok = SS.get_selection_count(model) > 0
            row["sel"] = {"s1": ok1, "s2": ok2}
        except Exception as e:                                          # noqa: BLE001
            row["sel_error"] = "%s: %s" % (type(e).__name__, str(e)[:100])
        row["selection_count"] = SS.get_selection_count(model)

        #: ③ **真调**（★ 判据 = 特征树增量 ✓）
        before = _fnames(model)
        exc = None
        feat = None
        if exists:
            try:
                feat = sw_connect.get_com_member(fm, name, *args)
            except Exception as e:                                      # noqa: BLE001
                exc = e
        after = _fnames(model)
        added = [n for n in after if n not in before]
        row.update({"called": exists, "added": added,
                    "returned_is_none": (feat is None) if exists else None,
                    "call_exception": None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:140])})
        out["runs"].append(row)
        print("★ %-26s 存在=%-5s 选区=%-2s ⇒ 新增 %-22r %s"
              % (name, exists, row["selection_count"], added,
                 ("· 抛：" + row["call_exception"][:70]) if row.get("call_exception") else ""))

    existed = [r["member"] for r in out["runs"] if r["member_exists"]]
    built = [r["member"] for r in out["runs"] if r.get("added")]
    out["members_that_exist"] = existed
    out["members_that_built"] = built
    if built:
        out["verdict"] = ("★★★★★ **有成员真的建成了**：%r ⇒ ★★ **这几项要重开**（★ 事实 47 封的是属性式 "
                          "`AccessSelections` 族、★ **不是参数式入口** ✓）" % built)
    elif existed:
        out["verdict"] = ("★★★★ **成员存在（%r）、★ 而没建成** ⇒ ★ 下一步：★ 按铁律 4 去 **CHM/反射**"
                          "补**官方签名**（★ 本次实参抄自外部项目、★ 个数可能不对 ✓）" % existed)
    else:
        out["verdict"] = ("★★ **这四个成员在真机上**取不到**** ⇒ ★ 与 `swapi` 的读数一致 ✓ —— "
                          "★★ 但★ **仍要补 CHM/反射两源**才能定案（★ 铁律 4：★ 三源互证 ✓）")
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-external-members.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "spec211-external-members-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)
