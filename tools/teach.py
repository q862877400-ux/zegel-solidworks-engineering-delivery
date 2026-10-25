"""示教器统一入口：L1 捕获 / L2 提炼 / L3 执行 / L4 个人化。

```bash
# L1 捕获（业主示范一次）
python -B tools/teach.py capture --start
python -B tools/teach.py capture --stop          # 落 model.json / steps.md / 录屏
# L2 提炼（语义快照 → 配方）
python -B tools/teach.py derive --snapshot output/teach/<会话>/model.json \
                                --out teach/recipes/hole-4x.yaml
# L4 个人化
python -B tools/teach.py profile --id owner --set hole_standard=ISO
python -B tools/teach.py profile --id owner            # 看当前生效值
# L3 执行（配方 → 纯 API 建模 + 按 assertions 核对）
python -B tools/teach.py run --recipe teach/recipes/hole-4x.yaml --profile owner
```
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（示教器统一入口）
# 文件:   tools/teach.py
# 定位:   把 L1 捕获 / L2 提炼 / L3 执行 / L4 个人化收成一个命令，
#          让「业主示范一次 → agent 照做」成为常规流程（业主比作机械臂试教）。
# 官方依据: 复用本仓 demo_capture（PSR+ffmpeg+模型快照）· sw_recipe（L2）·
#          sw_recipe_exec（L3）· sw_habits（L4）；实机调用走 HoleWizard5 等既有封装
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def _capture(argv: list) -> int:
    """L1：转给 `demo_capture`。"""
    import demo_capture

    saved = sys.argv
    try:
        sys.argv = ["demo_capture"] + argv
        return demo_capture.main()
    finally:
        sys.argv = saved


def _derive(argv: list) -> int:
    """L2：语义快照 → 配方。"""
    import sw_recipe

    snap_p = _arg(argv, "--snapshot")
    out_p = _arg(argv, "--out")
    if not snap_p or not out_p:
        print("用法：teach.py derive --snapshot <model.json> --out <recipe.yaml>")
        return 2
    snap = json.loads(Path(snap_p).read_text(encoding="utf-8"))
    recipe = sw_recipe.derive_from_snapshot(snap, capture=str(Path(snap_p).parent))
    p = sw_recipe.save(recipe, out_p)
    print("① 配方已生成：%s" % p)
    print("   id=%s · 孔位 %d 个 · assertions %d 条"
          % (recipe["id"], len(recipe["inputs"].get("positions_mm") or []),
             len(recipe["assertions"])))
    for note in recipe.get("notes") or []:
        print("   ⚠ %s" % note)
    return 0


def _profile(argv: list) -> int:
    """L4：读写个人化档案。"""
    import sw_habits

    pid = _arg(argv, "--id")
    if not pid:
        print("用法：teach.py profile --id <profile> [--set k=v ...]")
        return 2
    sets = [a for a in argv if "=" in a and not a.startswith("--")]
    if sets:
        cur = {}
        p = sw_habits.habits_path(pid)
        if p.is_file():
            from sw_recipe import _mini_yaml_load

            cur = _mini_yaml_load(p.read_text(encoding="utf-8"))
        for item in sets:
            k, _, v = item.partition("=")
            k, v = k.strip(), v.strip()
            ref = sw_habits.DEFAULT_HABITS.get(k)
            if isinstance(ref, bool):
                cur[k] = v.lower() in ("1", "true", "yes", "on")
            elif isinstance(ref, float):
                cur[k] = float(v)
            elif isinstance(ref, int):
                cur[k] = int(v)
            else:
                cur[k] = v
        path = sw_habits.save(pid, cur)
        print("① 已写：%s" % path)
    eff = sw_habits.load(pid)
    print("② %s 当前生效：" % pid)
    for k in sorted(eff):
        mark = "" if eff[k] == sw_habits.DEFAULT_HABITS[k] else "  ← 已改"
        print("   %-28s %s%s" % (k, eff[k], mark))
    return 0


def _run(argv: list) -> int:
    """L3：配方 → 纯 API 建模 + 核对 assertions。"""
    import sw_connect as c_
    import sw_habits
    import sw_recipe
    import sw_recipe_exec
    from sw_connect import get_com_member as g

    rp = _arg(argv, "--recipe")
    if not rp:
        print("用法：teach.py run --recipe <recipe.yaml> [--profile <id>]")
        return 2
    recipe = sw_recipe.load(rp)
    pid = _arg(argv, "--profile")
    if pid:
        recipe = sw_habits.apply_to_recipe(recipe, sw_habits.load(pid))
        print("① 已套用档案：%s" % pid)

    inp = recipe.get("inputs") or {}
    plate = inp.get("plate") or {}
    hole = inp.get("hole") or {}
    pos = inp.get("positions_mm") or []
    miss = [k for k in ("width_mm", "height_mm", "thickness_mm") if not plate.get(k)]
    if miss or not pos:
        print("★ 配方缺参数，执行不了：plate 缺 %s · 孔位 %d 个" % (miss, len(pos)))
        print("  ⇒ 用 `teach.py profile --id <id> --set ...` 补默认值，或手改配方")
        return 1

    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass
    try:
        for d in list(g(sw, "GetDocuments") or ()):
            c_.try_call(sw.CloseDoc, str(g(d, "GetTitle") or ""))
        #: ★ 不用 or 6.6 兜底：环境坑门禁把它当「隐式默认值」回归（实测抓到）。
        #:   显式判空，缺就报错，别静默塞一个数。
        diam = hole.get("diameter_mm")
        if diam is None:
            print("★ 配方缺 inputs.hole.diameter_mm ⇒ 不猜，请补上")
            return 1
        doc, rep = sw_recipe_exec.build_plate_with_holes(
            sw,
            width_mm=float(plate["width_mm"]),
            height_mm=float(plate["height_mm"]),
            thickness_mm=float(plate["thickness_mm"]),
            holes_mm=tuple(tuple(p) for p in pos),
            size=str(hole.get("size") or "M6"),
            diameter_mm=float(diam),
        )
        if doc is None:
            print("★ 建模失败：%s" % rep.get("error"))
            return 1
        print("② 建模完成，逐步读数：")
        for s in rep["steps"]:
            step = s.pop("step")
            print("   %-12s %s" % (step, s))
        res = sw_recipe_exec.assert_recipe(doc)
        print("③ assertions：")
        bad = []
        for k, v in res.items():
            if k == "all_ok":
                continue
            print("   %-26s %s  实测=%s 期望=%s"
                  % (k, "PASS" if v["ok"] else "FAIL", v["observed"],
                     v["expected"]))
            if not v["ok"]:
                bad.append(k)
        print("★ 结论：%s" % ("全部通过" if not bad else "未通过：%s" % bad))
        return 0 if not bad else 1
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass


def _arg(argv: list, flag: str) -> str:
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
    return ""


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        return 0
    sub, rest = argv[0], argv[1:]
    if sub in ("capture", "--start", "--stop", "--status", "--report", "--frame"):
        return _capture(argv if sub == "capture" else argv)
    if sub == "derive":
        return _derive(rest)
    if sub == "profile":
        return _profile(rest)
    if sub == "run":
        return _run(rest)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
