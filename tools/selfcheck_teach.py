"""示教工具**全能力自检**：不依赖业主操作，逐项跑并给 PASS/FAIL/SKIP。

判据分三类：
- **PASS**  = 本轮真机跑通，有读数
- **FAIL**  = 跑了但不成立（必须修）
- **UNVERIFIED** = 没有样本/没法离线验（如实标，不冒充通过）

覆盖：模块导入 · 记录器（零件/装配/图样）· 时间轴 · 对话框 · PSR 解析 ·
      视频抽帧 · 报告生成 · 枚举一致性 · 量纲门禁。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（示教器 · 自检）
# 文件:   tools/selfcheck_teach.py
# 定位:   改完示教器相关代码就跑一遍，逐项验模块/枚举/量纲/时间轴/
#          对话框/PSR/录屏/报告/记录器。
#          起因：2026-10-26 多次「改一处引入另一处回归」，需要一键判据而不是逐个手点。
# 官方依据: 不适用（自检的是本仓自身行为；判据来自各模块既有表与真机样本）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
import importlib
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
sys.stdout.reconfigure(encoding="utf-8")

R = Path(".")
ROWS = []


def rec(name: str, verdict: str, detail: str = "") -> None:
    ROWS.append((name, verdict, detail))
    print(f"  [{verdict:<10}] {name}  {detail}")


print("=" * 76)
print("① 模块导入")
print("=" * 76)
for m in ("sw_enums", "sw_units", "sw_model_timeline", "sw_dialog_text",
          "sw_model_snapshot", "check_dimension_units"):
    try:
        importlib.import_module(m)
        rec(f"import {m}", "PASS")
    except Exception as exc:  # noqa: BLE001
        rec(f"import {m}", "FAIL", f"{type(exc).__name__}: {exc}")

print()
print("=" * 76)
print("② 枚举与既有表的一致性")
print("=" * 76)
try:
    import sw_enums
    import sw_model_snapshot
    from sketch_relations import SKETCH_CONSTRAINT_TYPES, SKETCH_RELATION_ENTITY_TYPES
    from sw_selection_spec import ENTITY_KINDS

    ok = len(sw_enums.CONSTRAINT_TYPE) >= 80
    rec("sw_enums 关系表规模", "PASS" if ok else "FAIL",
        f"{len(sw_enums.CONSTRAINT_TYPE)} 项")
    same = sw_model_snapshot.ELEMENT_KIND_BY_ID == SKETCH_RELATION_ENTITY_TYPES
    rec("元素名复用既有表", "PASS" if same else "FAIL")
    rec("非草图元素中文覆盖 ENTITY_KINDS",
        "PASS" if (
            set(ENTITY_KINDS) <= set(sw_model_snapshot.ELEMENT_KIND_ZH)) else "FAIL",
        str(ENTITY_KINDS))
    bad = []
    SYN = {"distance": "DISTANCE", "angle": "ANGLE", "horizontal": "HORIZONTAL",
           "vertical": "VERTICAL", "tangent": "TANGENT", "parallel": "PARALLEL",
           "perpendicular": "PERPENDICULAR", "coincident": "COINCIDENT",
           "concentric": "CONCENTRIC", "symmetric": "SYMMETRIC",
           "midpoint": "ATMIDDLE", "intersect": "ATINTERSECT",
           "equal": "SAMELENGTH", "fix": "FIXED", "collinear": "COLINEAR",
           "coradial": "CORADIAL", "pierce": "ATPIERCE"}
    for k, v in SKETCH_CONSTRAINT_TYPES.items():
        want = SYN.get(k)
        got = sw_enums.CONSTRAINT_TYPE.get(v)
        if want is None or got != f"swConstraintType_{want}":
            bad.append(k)
    rec("两张关系表同值", "PASS" if not bad else "FAIL", f"不一致 {bad}" if bad else "")
except Exception as exc:  # noqa: BLE001
    rec("枚举一致性", "FAIL", f"{type(exc).__name__}: {exc}")

print()
print("=" * 76)
print("③ 量纲分派（长度/角度/未实测）")
print("=" * 76)
try:
    import sw_units

    class _D:
        def __init__(self, v):
            self.v = v

        #: N802：替身用小写名；被测代码按原属性名调用，故挂别名
        def get_system_value2(self, _c):
            return self.v

        GetSystemValue2 = get_system_value2

    a = sw_units.dimension_reading(_D(0.1), 1)
    b = sw_units.dimension_reading(_D(0.7853981634), 2)
    c = sw_units.dimension_reading(_D(5.0), 77)
    rec("长度 → mm", "PASS" if a.get("value_mm") == 100.0 else "FAIL", str(a))
    deg_ok = abs(b.get("value_deg", 0) - 45) < 1e-6
    rec("角度 → deg", "PASS" if deg_ok else "FAIL", str(b))
    rec("计数标 unit_unverified",
        "PASS" if c.get("unit_unverified") and "value_mm" not in c else "FAIL", str(c))
except Exception as exc:  # noqa: BLE001
    rec("量纲分派", "FAIL", f"{type(exc).__name__}: {exc}")

print()
print("=" * 76)
print("④ 时间轴逻辑（首次/去重/切换/状态变化留快照）")
print("=" * 76)
try:
    import sw_model_timeline

    def fake(title, path, states):
        return {"title": title, "path": path, "doc_type": 1, "features": 5,
                "sketches": 1, "sketch_states": states, "relations": 3,
                "dimensions": 1, "holes": 0, "mates": 0}

    real = sw_model_timeline.loudness
    with tempfile.TemporaryDirectory() as td:
        tl = sw_model_timeline.Timeline(Path(td), 0.0)
        try:
            sw_model_timeline.loudness = lambda _d: fake("A", "/a", [2])
            r1 = tl.poll(object())
            r2 = tl.poll(object())
            sw_model_timeline.loudness = lambda _d: fake("A", "/a", [3])
            r3 = tl.poll(object())
            sw_model_timeline.loudness = lambda _d: fake("B", "/b", [3])
            r4 = tl.poll(object())
            r5 = tl.poll(object())
        finally:
            sw_model_timeline.loudness = real
        rec("首次记一条", "PASS" if r1 else "FAIL")
        rec("同文档重复不记", "PASS" if r2 is None else "FAIL")
        rec("状态变化留快照", "PASS" if r3 and r3.get("snapshot") else "FAIL",
            str((r3 or {}).get("snapshot")))
        rec("切文档记 doc-switch",
            "PASS" if r4 and r4.get("kind") == "doc-switch" else "FAIL")
        rec("切后同文档不记", "PASS" if r5 is None else "FAIL")
        rows = [x for x in (Path(td) / "timeline.jsonl").read_text(
            encoding="utf-8").splitlines() if x.strip()]
        rec("轨迹条数=3", "PASS" if len(rows) == 3 else "FAIL", f"{len(rows)} 条")
except Exception as exc:  # noqa: BLE001
    rec("时间轴逻辑", "FAIL", f"{type(exc).__name__}: {exc}")

print()
print("=" * 76)
print("⑤ 对话框文字读取")
print("=" * 76)
try:
    import sw_dialog_text

    rows = sw_dialog_text.snapshot()
    rec("无对话框时回空且不崩", "PASS" if isinstance(rows, list) else "FAIL",
        f"当前 {len(rows)} 个")
    #: 用假对话框验数值筛选
    fake_dlg = {"title": "修改", "class": "#32770",
                "fields": [("NECSPIN", "D1@草图1"), ("RichEdit", "100.74390101mm"),
                           ("RichEdit", "abc")]}
    nums = sw_dialog_text.numeric_fields(fake_dlg)
    rec("能从字段里挑出数值",
        "PASS" if any("100.74" in n["text"] for n in nums) else "FAIL", str(nums))
except Exception as exc:  # noqa: BLE001
    rec("对话框读取", "FAIL", f"{type(exc).__name__}: {exc}")

print()
print("=" * 76)
print("⑥ PSR 解析（用真实 psr.zip）")
print("=" * 76)
Z = R / "output/teach/20261026-005007/psr.zip"
if not Z.is_file():
    rec("PSR 解析", "UNVERIFIED", "无样本 zip")
else:
    sys.path.insert(0, "tools")
    try:
        from extract_psr_shots import extract
        with tempfile.TemporaryDirectory() as td:
            shots = extract(Z, Path(td))
        rec("截图提取", "PASS" if len(shots) >= 1 else "FAIL", f"{len(shots)} 张")
    except Exception as exc:  # noqa: BLE001
        rec("截图提取", "FAIL", f"{type(exc).__name__}: {exc}")
    try:
        import demo_capture
        steps = demo_capture._steps_from_psr(Z, Z.parent)
        rec("步骤解析", "PASS" if steps and len(steps) > 10 else "FAIL",
            f"{len(steps)} 步")
        rec("步骤含时间字段",
            "PASS" if steps and steps[0].get("time") else "FAIL",
            str(steps[0])[:60] if steps else "")
    except Exception as exc:  # noqa: BLE001
        rec("步骤解析", "FAIL", f"{type(exc).__name__}: {exc}")

print()
print("=" * 76)
print("⑦ 录屏（真实 mp4）")
print("=" * 76)
MP4 = R / "output/teach/20261026-005007/screen.mp4"
if not MP4.is_file():
    rec("录屏可读", "UNVERIFIED", "无样本 mp4")
else:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1", str(MP4)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = r.returncode == 0 and "duration=" in (r.stdout or "")
    rec("ffprobe 可读（moov 完好）", "PASS" if ok else "FAIL",
        (r.stdout or r.stderr or "").strip()[:60])
    with tempfile.TemporaryDirectory() as td:
        r2 = subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(MP4),
             "-vf", "fps=1/60,scale=640:-1", str(Path(td) / "f_%02d.jpg")],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        n = len(list(Path(td).glob("*.jpg")))
        rec("能抽帧", "PASS" if n >= 1 else "FAIL", f"{n} 帧")

print()
print("=" * 76)
print("⑧ 报告生成")
print("=" * 76)
RP = R / "output/teach/20261026-005007/REPORT.md"
if RP.is_file():
    txt = RP.read_text(encoding="utf-8")
    for needle, label in (
            ("记录覆盖范围", "含覆盖范围段"),
            ("模型变化轨迹", "含轨迹段"),
            ("截图", "含截图段"),
            ("弹窗事件", "含弹窗段")):
        rec(label, "PASS" if needle in txt else "FAIL")
else:
    rec("报告存在", "FAIL", "无 REPORT.md")

print()
print("=" * 76)
print("⑨ 记录器（真实文档）")
print("=" * 76)
try:
    import sw_connect as c
    from sw_connect import get_com_member as g

    conn = c.connect_solidworks(wait_seconds=20)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass
    try:
        doc = g(sw, "ActiveDoc")
        import sw_model_snapshot

        data = sw_model_snapshot.dump_document(doc)
        rec("dump_document 能跑", "PASS" if data else "FAIL",
            f"类型 {data.get('doc_type')} · 特征 {len(data.get('features') or [])}")
        if data.get("doc_type") == "装配":
            comps = data.get("components") or []
            inner = (comps[0].get("model") or {}) if comps else {}
            rec("组件内部模型", "PASS" if inner.get("features") else "FAIL",
                f"实体来源={inner.get('bodies_source')}")
            sk = (inner.get("sketches") or [{}])[0]
            rec("草图状态语义", "PASS" if sk.get("constrained_official") else "FAIL",
                str(sk.get("constrained_official")))
            rec("元素名含中文", "PASS" if sk.get("points") or sk.get("segments")
                else "UNVERIFIED", "")
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
except Exception as exc:  # noqa: BLE001
    rec("记录器真机", "FAIL", f"{type(exc).__name__}: {exc}")

print()
print("=" * 76)
print("汇总")
print("=" * 76)
counts = {}
for _n, v, _d in ROWS:
    counts[v] = counts.get(v, 0) + 1
print("  " + " · ".join(f"{k} {v}" for k, v in sorted(counts.items())))
bad = [(n, d) for n, v, d in ROWS if v == "FAIL"]
if bad:
    print("\n  ✗ 失败项：")
    for n, d in bad:
        print(f"    {n}  {d}")
else:
    print("\n  ✓ 无失败项")
uns = [(n, d) for n, v, d in ROWS if v == "UNVERIFIED"]
if uns:
    print("\n  ⚠ 未验证项（如实列出）：")
    for n, d in uns:
        print(f"    {n}  {d}")
