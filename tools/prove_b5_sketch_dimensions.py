"""★ 真机：B5 批草图尺寸与关系（★ 判据 = 草图特征上的**尺寸计数** + **关系计数**）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_b5_sketch_dimensions.py
# 定位:   ★ 2026-10-03（轮 466）★ `specs/201-toolbar-gaps` **B5 批**的真机探针。
#   ★★★ **判据怎么定的（★ 这一步花了几次试错）**：
#     ```
#     ★ 一开始想用「文档级的草图尺寸计数」—— ★ **官方没有那个成员**
#       （`GetDimensionCount*` 只在 `IView` / `IMacroFeatureData` / `ISketchBlockDefinition` 上）。
#     ★★ 换判据：**`IFeature.GetFirstDisplayDimension` + `IAnnotation.GetNext2`** ——
#        ★ 从**草图特征**出发遍历它挂着的尺寸 ⇒ 数出来的就是这张草图的尺寸 ✓
#     ★ 关系用 **`ISketchRelationManager.GetRelationsCount(-1)`**（`-1` = 全部）✓
#     ```
#   ⚠ 每个操作**单独开一张新草图**（★ 免副作用污染）✓
#   ⚠ `FullyDefineSketch` 的**枚举取值表两套源都没查到** ⇒ 只如实记录它**回了什么数**，
#     ★ 不拿"回了 0"当"全定义成功"（★ 那正是"看到数字就定性"的坑）。
# 官方依据: `C:\swapi\types\` 的 `IModelDoc2` / `IModelDocExtension` / `ISketchManager` /
#   `ISketchRelationManager` / `IFeature` / `IAnnotation`（见 `sw_sketch_dimensions.py` 来源块）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（草图特征上的尺寸计数 / 关系计数）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "b5-sketch-dimensions-evidence.json"
#: ★ 单跑开关：`--only <名字片段>` ⇒ 只跑匹配的那个操作（★ 隔离用，见 `run()` 的注释）
_ONLY = ""
for _i, _a in enumerate(sys.argv):
    if _a == "--only" and _i + 1 < len(sys.argv):
        _ONLY = sys.argv[_i + 1]


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import sw_part as P
    import sw_sketch as SK
    import sw_sketch_dimensions as D

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "B5 批：草图尺寸与关系（specs/201-toolbar-gaps）",
          "judge": "草图特征上的 DisplayDimension 计数 / ISketchRelationManager 关系计数",
          "items": []}

    def dim_count(model):
        """★ 遍历**草图特征**上的显示尺寸（`IFeature.GetFirstDisplayDimension` + `GetNext2`）。"""
        n = 0
        for nm in P.feature_names(model):
            if not (nm.startswith("\u8349\u56fe") or nm.lower().startswith("sketch")):
                continue
            try:
                feat = get_com_member(model, "FeatureByName", nm)
                dd = get_com_member(feat, "GetFirstDisplayDimension") if feat is not None else None
                while dd is not None:
                    n += 1
                    dd = get_com_member(dd, "GetNext2")
            except Exception:
                continue
        return n

    def rel_count(model):
        try:
            return int(D.count_sketch_relations(model, -1))
        except Exception:
            return -1

    def with_sketch(setup, act, *, judge="dim_up"):
        row = {"judge": judge}
        doc = None
        try:
            doc = sw_connect.new_document(sw, "part")
            P.start_sketch(doc, plane_name="Front Plane")
            setup(doc)
            d0, r0 = dim_count(doc), rel_count(doc)
            ret = act(doc)
            d1, r1 = dim_count(doc), rel_count(doc)
            row.update({"dim": [d0, d1], "rel": [r0, r1],
                        "ret": (str(ret)[:28] if ret is not None else "None")})
            if judge == "dim_up":
                row["built"] = d1 > d0
            elif judge == "rel_up":
                row["built"] = r1 > r0
            elif judge == "rel_down":
                row["built"] = (r1 < r0) or (r1 == 0 and r0 > 0)
            elif judge == "readable":
                row["built"] = r1 >= 0
            elif judge == "any_change":
                row["built"] = (d1 != d0) or (r1 != r0)
            else:
                row["built"] = (d1 != d0) or (r1 != r0)
            row["verdict"] = "能" if row["built"] else "不能"
        except Exception as e:
            row["err"] = "%s: %s" % (type(e).__name__, str(e)[:130])
            #: ★★★ 2026-10-03（轮 491）**补这一行** ——
            #:   ⚠ 原来的异常分支**只写 `err`、没写 `verdict`**，而 `run()` 里
            #:     `row["verdict"]` 是**无条件读**的 ⇒ ★★ 一旦 `act` 抛异常，
            #:     **探针自己就 `KeyError: 'verdict'` 崩掉** ⚠
            #:   ★★ 而它**看起来像"这条能力不行"**（★ 真机：`--only 4` 尺寸链，
            #:     rc=1 · Traceback 落在 `run()` 里 · ★ 而 evidence 里**那条根本没进**）⚠
            #:   ⇒ ★ 这正是本仓反复出现的那一类（★ 轮 473/479/486/487 都是）：
            #:     **「失败」看着像能力问题，实际是我这边的判据 / 前置 / 探针** ✓
            row["verdict"] = "不能"
        finally:
            if doc is not None:
                try:
                    P.end_sketch(doc)
                except Exception:
                    pass
                try:
                    t = str(safe_get_com_member(doc, "GetTitle") or "")
                    if t:
                        sw.CloseDoc(t)
                except Exception:
                    pass
        return row

    def run(zh, setup, act, judge="dim_up", note=""):
        #: ★ 2026-10-03（轮 466）★ **加单跑开关**（`python … --only 3` 跑第 3 个）。
        #:   两个原因叠在一起：
        #:   ① 整批跑时**挂住并弹出「SOLIDWORKS Design 错误报告」**，而 stdout 是空的
        #:      （看不到跑到哪一步）⇒ ★ **隔离**必须能一次只跑一个 ✓
        #:   ② ⚠ **第一版按中文名匹配 ⇒ 一次都没匹配上** —— 真因是 **PowerShell 传中文参数时
        #:      编码坏了**（`_ONLY` 收到乱码）⇒ ★ 改用**序号**（ASCII）绕开它 ✓
        run.n += 1
        if _ONLY and int(_ONLY) != run.n:
            return None
        row = with_sketch(setup, act, judge=judge)
        row["zh"] = zh
        if note:
            row["note"] = note
        ev["items"].append(row)
        print("  %-16s %-3s  \u5c3a\u5bf8%s \u5173\u7cfb%s  %s" % (
            zh, row["verdict"], row.get("dim"), row.get("rel"),
            str(row.get("err") or "")[:52]))
        return row

    #: ★ 计数器（★ 必须在 def run **之后** —— 否则 Python 把 run 当局部变量 ⇒ UnboundLocalError）
    run.n = 0

    def box(d):
        P.sketch_corner_rectangle(d, -25.0, -20.0, 25.0, 20.0)

    #: \u2460 \u6c34\u5e73\u5c3a\u5bf8\uff08\u2605 \u9700\u5148\u9009\u4e2d\u4e00\u6761\u7ebf\u6bb5\uff09
    def s_h(d):
        box(d)
        D_sel = __import__("sw_sketch_edit_ops").select_sketch_segment
        D_sel(d, 0)
    run("\u6c34\u5e73\u5c3a\u5bf8", s_h, lambda d: D.add_horizontal_dimension(d, 0.0, 30.0), "dim_up")
    #: \u2461 \u7ad6\u76f4\u5c3a\u5bf8
    def s_v(d):
        box(d)
        __import__("sw_sketch_edit_ops").select_sketch_segment(d, 1)
    run("\u7ad6\u76f4\u5c3a\u5bf8", s_v, lambda d: D.add_vertical_dimension(d, 35.0, 0.0), "dim_up")
    #: \u2462 \u8def\u5f84\u957f\u5ea6\u5c3a\u5bf8
    def s_p(d):
        box(d)
        __import__("sw_sketch_edit_ops").select_sketch_segment(d, 0)
    run("\u8def\u5f84\u957f\u5ea6\u5c3a\u5bf8", s_p, lambda d: D.add_path_length_dimension(d, 0.0, 30.0), "dim_up")
    #: \u2463 \u5c3a\u5bf8\u94fe
    def s_c(d):
        box(d)
        __import__("sw_sketch_edit_ops").select_sketch_segment(d, 0)
        __import__("sw_sketch_edit_ops").select_sketch_segment(d, 1, append=True)
    run("\u5c3a\u5bf8\u94fe", s_c, lambda d: D.insert_chain_dimensions(d, "__current_selection__"), "dim_up")
    #: \u2464 \u5b8c\u5168\u5b9a\u4e49\u8349\u56fe
    run("\u5b8c\u5168\u5b9a\u4e49\u8349\u56fe", box, lambda d: D.fully_define_sketch(d), "any_change",
        note="\u2605 \u679a\u4e3e\u53d6\u503c\u8868\u4e24\u5957\u6e90\u90fd\u6ca1\u67e5\u5230 \u21d2 \u53ea\u5982\u5b9e\u8bb0\u5b83\u56de\u4e86\u4ec0\u4e48\u6570")
    #: \u2465 \u6dfb\u52a0\u51e0\u4f55\u5173\u7cfb\uff08\u2605 \u4ed3\u91cc\u5df2\u6709\uff0c\u672c\u8f6e\u9a8c\u5b83\u56de\u8bfb\u5f97\u5230\uff09
    def s_r(d):
        P.sketch_line(d, -20.0, 0.0, 20.0, 0.0)
        __import__("sw_sketch_edit_ops").select_sketch_segment(d, 0)
    run("\u6dfb\u52a0\u51e0\u4f55\u5173\u7cfb", s_r, lambda d: P.add_sketch_relation(d, "sgHORIZONTAL"), "rel_up")
    #: \u2466 \u5173\u7cfb\u8ba1\u6570\uff08\u2605 \u53ea\u8bfb\uff09
    run("\u5173\u7cfb\u8ba1\u6570", s_r, lambda d: D.count_sketch_relations(d, -1), "readable")
    #: \u2467 \u5220\u9664\u5168\u90e8\u51e0\u4f55\u5173\u7cfb
    def s_del(d):
        P.sketch_line(d, -20.0, 0.0, 20.0, 0.0)
        __import__("sw_sketch_edit_ops").select_sketch_segment(d, 0)
        P.add_sketch_relation(d, "sgHORIZONTAL")
    run("\u5220\u9664\u5168\u90e8\u5173\u7cfb", s_del, lambda d: D.delete_all_sketch_relations(d), "rel_down")

    ok = sum(1 for i in ev["items"] if i["verdict"] == "能")
    ev["can"], ev["total"] = ok, len(ev["items"])
    ev["verdict"] = "pass" if ok == ev["total"] else "partial"
    #: ★ 单跑模式（`--only`）⇒ **累积**到既有产物里，而不是覆盖 ——
    #:   因为整批连跑会在某处**挂住并弹「SOLIDWORKS Design 错误报告」**
    #:   （★ 8 个**单独**跑全 ok ⇒ 故改成逐条单跑、结果累积）✓
    if _ONLY and OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
            merged = [x for x in (old.get("items") or []) if x.get("zh") != ev["items"][0].get("zh")]
            merged += ev["items"]
            ev["items"] = merged
            ev["can"] = sum(1 for i in merged if i["verdict"] == "能")
            ev["total"] = len(merged)
            ev["verdict"] = "pass" if ev["can"] == ev["total"] else "partial"
            ev["_mode"] = "逐条单跑 + 累积（整批连跑会挂住）"
        except Exception:
            pass
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u2500\u2500 **\u80fd %d / \u5171 %d** \u21d2 %s" % (ev["can"], ev["total"], str(ev["verdict"]).upper()))
    print("  \u4ea7\u7269\uff1a%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
