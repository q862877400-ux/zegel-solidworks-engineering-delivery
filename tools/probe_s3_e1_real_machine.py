"""★ S3 第 3 条：先验证**检查器能看见真实坏样件**。

## 为什么需要这个探针

`docs/ENGINEERING-PATH.md` 第六节 S3 第 3 条逐字：

> 先核官方签名、Remarks、示例和死路限制，再做限定真机试验。
> **先验证检查器能看见真实坏样件，再验证生成方法。**

⇒ 顺序不能反。先证明「判据能抓住真机的欠约束草图」，
  才谈得上「生成方法做对了」。否则做出来的东西没有任何东西能验它。

## 做什么

① 新建零件，在 Front Plane 画一个矩形 ⇒ **真机的欠约束草图**（真实坏样件）
② 读 `ISketch.GetConstrainedStatus()` ⇒ 期望 2（`swUnderConstrained`）
③ 把读数喂给 `judge_sketch_constraint` ⇒ **必须判 fail**
④ 对全部草图段加 `sgFIXED` ⇒ **真机的全约束草图**（真实好样件）
⑤ 再读 ⇒ 期望 3（`swFullyConstrained`）
⑥ 再喂给判据 ⇒ **必须判 pass**

## 为什么这是「真实」坏样件

不是构造一个假输入让判据说 fail，而是让 SolidWorks **自己**产生一个
欠约束草图，读它的真实状态枚举，再让判据判。这样验证的是：
**判据与真机信号之间的接合是对的**。

## 只读

创建的是临时文档，收尾关闭；不改仓库文件（除 `--out` 指定的 JSON）。
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from engineering.acceptance.e1_sketch import (  # noqa: E402
    collect_sketch_constraint,
    judge_sketch_constraint,
)

from scripts import sw_connect as c_  # noqa: E402
from scripts import sw_part as p_  # noqa: E402

#: ★ 复用既有共用帮手（`scripts/sw_sketch.py:585`）——
#:   同一件事不在两个地方各写一份（统一化体检⑤）
from scripts.sw_sketch import active_sketch as _active_sketch  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_s3_e1_real_machine.py
# 定位:   `docs/ENGINEERING-PATH.md` 第六节 S3 第 3 条 ——
#           先验证检查器能看见真实坏样件，再验证生成方法。
#          ★ 本探针验证「E1 判据 vs 真机 GetConstrainedStatus」的接合。
# 官方依据: `C:\swapi\types\ISketch\GetConstrainedStatus.md`
#             `System.int GetConstrainedStatus()`
#           `C:\swapi\enums\swConstrainedStatus_e.md`（7 个成员）
#           ★ 三源互证：反射 `Int32 GetConstrainedStatus()` 一致
#             （`_raw/reflect/iface_sldworks.txt`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

REQ = "S3-E1-real"


def _get(obj, name, *args):
    """★ 取 COM 成员并调用（容错：成员不存在时回 None）。"""
    fn = getattr(obj, name, None)
    if fn is None:
        return None
    return fn(*args) if args else fn




def _status(sk) -> int:
    return int(_get(sk, "GetConstrainedStatus"))


def main() -> int:
    out: dict = {"probe": "s3-e1-real-machine", "cases": []}
    #: ★ connect_solidworks() 返回 (sw, model) 元组，model 可能为 None
    conn = c_.connect_solidworks()
    sw = conn[0] if isinstance(conn, tuple) else conn
    if sw is None:
        print("★ 连不上 SolidWorks ⇒ 无法做真机验证")
        return 2

    doc = None
    try:
        doc = c_.new_document(sw, "part")
        if doc is None:
            print("★ 新建零件失败")
            return 2

        # ── ① 真机的欠约束草图（真实坏样件）──
        p_.start_sketch(doc, plane_name="Front Plane")
        #: 矩形：x/y 各 ±20 mm（米制 → 米）
        _get(
            doc.SketchManager,
            "CreateCornerRectangle",
            -0.02,
            -0.01,
            0.0,
            0.02,
            0.01,
            0.0,
        )
        sk = _active_sketch(doc)
        if sk is None:
            print("★ 取不到活动草图对象 ⇒ 真机验证无法继续")
            return 2

        st_under = _status(sk)
        print("① 欠约束草图：GetConstrainedStatus = %d" % st_under)
        obs_bad = collect_sketch_constraint(
            target="real-machine-under-constrained",
            entities=0,
            relations=(),
            dimensions=(),
            solver_state="from_api",
            solver_status_int=st_under,
        )
        res_bad = judge_sketch_constraint(obs_bad, requirement_id=REQ)
        print(
            "   → 判据结论：%s（%s）"
            % (res_bad.status.value, res_bad.reason[:70])
        )
        out["cases"].append(
            {
                "case": "under_constrained",
                "status_int": st_under,
                "expected_int": 2,
                "judge": res_bad.status.value,
                "judge_reason": res_bad.reason,
                "expect_judge": "fail",
            }
        )

        # ── ② 加 sgFIXED 成全约束（真实好样件）──
        segs = list(_get(sk, "GetSketchSegments") or [])
        print("② 草图段数 = %d" % len(segs))
        doc.ClearSelection2(True)
        n_sel = 0
        for s in segs:
            try:
                if p_._select_com_object(s, append=True, mark=0):
                    n_sel += 1
            except Exception:  # noqa: BLE001
                pass
        print("   选中段数 = %d" % n_sel)
        if n_sel:
            p_.add_sketch_relation(doc, "sgFIXED")

        st_full = _status(sk)
        print("③ 全固定后：GetConstrainedStatus = %d" % st_full)
        obs_good = collect_sketch_constraint(
            target="real-machine-fully-defined",
            entities=0,
            relations=(),
            dimensions=(),
            solver_state="from_api",
            solver_status_int=st_full,
        )
        res_good = judge_sketch_constraint(obs_good, requirement_id=REQ)
        print(
            "   → 判据结论：%s（%s）"
            % (res_good.status.value, res_good.reason[:70])
        )
        out["cases"].append(
            {
                "case": "fully_defined",
                "status_int": st_full,
                "expected_int": 3,
                "segments": len(segs),
                "segments_selected": n_sel,
                "judge": res_good.status.value,
                "judge_reason": res_good.reason,
                "expect_judge": "pass",
            }
        )

        # ── ④ 总判 ──
        ok_int = st_under == 2 and st_full == 3
        ok_judge = res_bad.status.value == "fail" and res_good.status.value == "pass"
        out["status_int_matches_official"] = ok_int
        out["judge_sees_both"] = ok_judge
        out["ok"] = bool(ok_int and ok_judge and st_under != st_full)
        out["conclusion"] = (
            "★ 真机两个状态读数分别为 %d / %d，与官方表 2=欠定义、3=完全定义吻合；"
            "判据对两者分别给出 fail / pass ⇒ 判据能看见真实坏样件"
            % (st_under, st_full)
            if out["ok"]
            else "★ 未达预期：读数 %d / %d，判据 %s / %s"
            % (st_under, st_full, res_bad.status.value, res_good.status.value)
        )
        print()
        print(out["conclusion"])
        return 0 if out["ok"] else 1
    finally:
        if doc is not None:
            try:
                sw.CloseDoc(doc.GetTitle())
            except Exception:  # noqa: BLE001
                pass
        out["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s3-e1-real-machine-evidence.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("\n证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
