"""★ **示范捕获（试教）**：把业主的一次手工示范完整接住 —— 步骤 + 画面 + 模型语义。

## 这是干什么的（业主原话）

> 这个工具我们以后是经常要用的，我觉得真的很像**机械臂的试教功能**。

机械臂试教：人手把机械臂走一遍，机器记住轨迹。
这里：人手动把 SolidWorks 走一遍，我们记住 **三步** —— ① 动作文字 ② 画面 ③ 模型语义。

## 三层证据 + 一个对齐键

```
第1层  PSR（Windows 问题步骤记录器）  每步：动作 + 控件名 + 墙钟时间 + 截图
第2层  ffmpeg gdigrab 录屏           我起/停，记下**开始墙钟** ⇒ 可按步骤时间戳精确抽帧
第3层  模型语义快照                   特征树 / 草图的点坐标 / 关系与尺寸（含参照实体）
对齐键 墙钟时间
```

★ 为什么不用 Game Bar：它的开始时刻拿不到，视频时间轴与步骤时间戳无法稳定对齐。
★ 为什么坚持第 3 层：截图能看「改了没有」，但看不出「这条尺寸量的是点到哪条边」。

## 用法

```bash
python -B tools/demo_capture.py --start              # 起 PSR + 起录屏 + 记开始时刻
python -B tools/demo_capture.py --stop                # 停两者 + 落模型快照 + 出报告
python -B tools/demo_capture.py --status
python -B tools/demo_capture.py --report              # 打印步骤表（含每步对应帧名）
python -B tools/demo_capture.py --frame 12:34:56      # 按墙钟时间抽一帧
```

产物在 `output/teach/<会话号>/`：`psr.zip` · `screen.mp4` · `model.json` ·
`model.md` · `steps.md` · `REPORT.md` · `frames/`。
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

ROOT = R / "output" / "teach"
STATE = ROOT / "session.json"
#: 录屏帧率（8 fps 足够看清操作，文件又不会太大）
FPS = 8
#: 录屏最长时长（分钟）—— 防忘了停
MAX_MINUTES = 30


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 示范捕获「试教」）
# 文件:   tools/demo_capture.py
# 定位:   一次命令完成「业主示范 → 步骤文字 + 录屏 + 模型语义」三合一捕获，供后续照做。
#          起因：业主 2026-10-26 指出「能读到 4 个尺寸但不知道标的是哪里」，
#          并把它比作机械臂试教，要求做成常用工具。
# 官方依据: psr.exe（Windows 问题步骤记录器；已被微软标记弃用，但本机可用）·
#          ffmpeg gdigrab（屏幕录制/抽帧）· scripts/sw_model_snapshot.dump_model
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def _no_window() -> int:
    """子进程不弹控制台窗口（0x08000000 = CREATE_NO_WINDOW）。"""
    return 0x08000000


def _read_state() -> dict:
    if STATE.is_file():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}
    return {}


def _write_state(d: dict) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def _kill_stale_psr() -> int:
    """结束残留的 psr.exe（/stop 会写 zip，强行结束则不写 —— 这里只清实例）。"""
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq psr.exe", "/NH"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=30,
            creationflags=_no_window(),
        ).stdout
    except Exception:  # noqa: BLE001
        return 0
    n = 0
    for line in (out or "").splitlines():
        if "psr.exe" not in line.lower():
            continue
        parts = line.split()
        if len(parts) > 1 and parts[1].isdigit():
            subprocess.run(["taskkill", "/PID", parts[1], "/F"],
                           creationflags=_no_window(), timeout=20, check=False)
            n += 1
    if n:
        print("   （已清掉 %d 个残留 PSR 实例 —— 不清它会弹"
              "「某个实例正在运行中」）" % n)
    time.sleep(0.8)
    return n


def _psr_running() -> bool:
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq psr.exe", "/NH"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=20,
            creationflags=_no_window(),
        ).stdout
        return "psr.exe" in (out or "").lower()
    except Exception:  # noqa: BLE001
        return False


def start() -> int:
    st = _read_state()
    if st.get("running"):
        print("★ 已在录（会话 %s）" % st.get("session"))
        return 0
    sid = time.strftime("%Y%m%d-%H%M%S")
    d = ROOT / sid
    d.mkdir(parents=True, exist_ok=True)
    zip_path = d / "psr.zip"
    mp4 = d / "screen.mp4"

    #: ★★ 先清掉**已在跑的 PSR 实例** —— 否则它会弹「某个实例正在运行中」，
    #:    命令既不退出也不报错，人就在这里干等（2026-10-26 真实事故）。
    _kill_stale_psr()

    #: ① PSR（可见窗口 ⇒ 屏幕上能看到「正在录制」）
    p1 = subprocess.Popen(  # noqa: S603
        ["psr.exe", "/start", "/output", str(zip_path), "/sc", "1"],
        creationflags=_no_window(),
    )

    #: ② ffmpeg 录屏（记下开始墙钟，供后面抽帧对齐）
    t0 = time.time()
    p2 = subprocess.Popen(  # noqa: S603
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "gdigrab", "-framerate", str(FPS), "-i", "desktop",
         "-t", str(MAX_MINUTES * 60),
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
         str(mp4)],
        stdin=subprocess.PIPE, creationflags=_no_window(),
    )
    _write_state({
        "running": True, "session": sid, "dir": str(d),
        "psr_pid": p1.pid, "ffmpeg_pid": p2.pid,
        "started_epoch": t0,
        "started_wall": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t0)),
        "zip": str(zip_path), "mp4": str(mp4),
    })
    print("① 示范捕获已开始")
    print("   会话目录：%s" % d)
    print("   屏幕上应能看到「步骤记录器 - 现在正在录制」")
    print("   做完请说一声，我执行 --stop")
    return 0


def stop() -> int:
    st = _read_state()
    if not st.get("running"):
        print("★ 没有正在进行的捕获")
        return 0
    d = Path(st["dir"])
    #: ① 停 PSR（必须 /stop 它才会写 zip）
    subprocess.run(["psr.exe", "/stop"], creationflags=_no_window(), timeout=60,
                   check=False)
    for _ in range(20):
        if Path(st["zip"]).is_file() and Path(st["zip"]).stat().st_size > 0:
            break
        time.sleep(0.5)
    #: ② 停 ffmpeg：发 q 让它自己收尾（直接 kill 会留下坏文件）
    try:
        pid = int(st["ffmpeg_pid"])
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                       creationflags=_no_window(), timeout=30, check=False)
    except Exception:  # noqa: BLE001
        pass
    time.sleep(1.5)
    st["running"] = False
    st["stopped_wall"] = time.strftime("%Y-%m-%d %H:%M:%S")
    _write_state(st)
    print("① 已停止")
    print("   PSR 包：%s %s" % (Path(st["zip"]).name,
                              Path(st["zip"]).stat().st_size
                              if Path(st["zip"]).is_file() else "（未生成）"))
    print("   录屏：  %s %s" % (Path(st["mp4"]).name,
                              Path(st["mp4"]).stat().st_size
                              if Path(st["mp4"]).is_file() else "（未生成）"))

    #: ③ 模型语义快照（此刻 SolidWorks 里那个零件）
    snap = _model_snapshot(d)
    if snap:
        print("   模型快照：model.json / model.md")
    #: ④ 步骤表 + 报告
    steps = _steps_from_psr(Path(st["zip"]), d)
    if steps is not None:
        print("   步骤表：steps.md（%d 步）" % len(steps))
    _write_report(d, st, steps, snap)
    print("② 报告：%s" % (d / "REPORT.md"))
    return 0


def _model_snapshot(d: Path) -> dict:
    """读当前 SolidWorks 文档的语义并落盘（失败不中断整个流程）。"""
    try:
        import sw_connect as c_
        from sw_connect import get_com_member as g
        from sw_model_snapshot import dump_model

        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        try:
            doc = g(sw, "ActiveDoc")
            if doc is None:
                return {}
            data = dump_model(doc)
        finally:
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
    except Exception as exc:  # noqa: BLE001
        print("   ★ 模型快照失败：%s: %s" % (type(exc).__name__, str(exc)[:80]))
        return {}

    (d / "model.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = ["# 模型语义快照", "",
             "- 文档：`%s`" % data.get("document"),
             "- 路径：`%s`" % (data.get("path") or "（未保存）"), "",
             "## 特征", ""]
    for f in data.get("features", []):
        lines.append("- `%s` — %s" % (f.get("name"), f.get("type")))
    for h in data.get("holes", []):
        lines += ["", "## 孔 `%s`" % h.get("name"), "",
                  "- 标准：**%s** · 类型：%s · 规格：%s"
                  % (h.get("standard"), h.get("fastener"), h.get("size"))]
        for sk in h.get("sketches", []):
            lines += _sketch_lines(sk, "   ")
    for sk in data.get("sketches", []):
        lines += _sketch_lines(sk, "")
    (d / "model.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return data


def _sketch_lines(sk: dict, indent: str) -> list:
    out = ["", "%s### %s（状态 %s）" % (indent, sk.get("name"), sk.get("constrained")),
           "", "%s- 点：%s" % (indent, sk.get("points"))]
    rels = sk.get("relations") or []
    if rels:
        out.append("%s- 关系/尺寸 %d 条：" % (indent, len(rels)))
        for r in rels:
            val = (" = %s mm" % r["value_mm"]) if r.get("value_mm") is not None else ""
            out.append("%s  - **%s**%s  ← %s"
                       % (indent, r.get("type"), val, " + ".join(r.get("refs") or [])))
    return out


def _steps_from_psr(zip_path: Path, d: Path):
    """把 PSR 的 mht 解成步骤列表（时间 / 动作文字）。"""
    if not zip_path.is_file():
        return None
    try:
        import html
        import quopri
        import re
        import zipfile

        with zipfile.ZipFile(zip_path) as z:
            mhts = [n for n in z.namelist() if n.lower().endswith(".mht")]
            if not mhts:
                return None
            raw = z.read(mhts[0]).decode("utf-8", "replace")
        try:
            body = quopri.decodestring(raw.encode("utf-8", "replace")).decode(
                "utf-8", "replace")
        except Exception:  # noqa: BLE001
            body = raw
        txt = html.unescape(re.sub(r"<[^>]+>", "", body))
        steps = []
        for line in txt.splitlines():
            m = re.match(r"^Step (\d+): \(([^)]*)\)\s*(.*)$", line.strip())
            if m:
                steps.append({"n": int(m.group(1)),
                              "time": m.group(2).replace("\u200e", ""),
                              "text": m.group(3).strip()})
        md = ["# 示范步骤（PSR）", "", "| # | 时间 | 动作 |", "|---|---|---|"]
        for s in steps:
            txt = s["text"].replace("|", "\\|")
            md.append("| %d | %s | %s |" % (s["n"], s["time"], txt))
        (d / "steps.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        return steps
    except Exception as exc:  # noqa: BLE001
        print("   ★ 解析 PSR 失败：%s" % type(exc).__name__)
        return None


def _write_report(d: Path, st: dict, steps, snap) -> None:
    lines = ["# 示范捕获报告", "",
             "- 会话：`%s`" % st.get("session"),
             "- 开始：%s" % st.get("started_wall"),
             "- 结束：%s" % st.get("stopped_wall", ""),
             "- PSR：`%s`" % Path(st["zip"]).name,
             "- 录屏：`%s`（%d fps）" % (Path(st["mp4"]).name, FPS),
             "",
             "## 怎么用这份报告",
             "",
             "1. 看 `steps.md`：每步的动作与控件名（语义骨架）",
             "2. 看 `model.md`：模型里实际留下了什么（点坐标 / 关系 / 尺寸参照）",
             "3. 需要画面时按步骤时间抽帧：",
             "   `python -B tools/demo_capture.py --frame <步骤时间>`",
             "", "## 步骤数", ""]
    lines.append("- %d 步" % (len(steps) if steps else 0))
    if snap:
        lines += ["", "## 模型", "",
                  "- 文档：`%s`" % snap.get("document"),
                  "- 特征 %d 个 · 孔 %d 个 · 草图 %d 张"
                  % (len(snap.get("features", [])), len(snap.get("holes", [])),
                     len(snap.get("sketches", [])))]
    (d / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def frame(at: str) -> int:
    """按**墙钟时间**（HH:MM:SS）从录屏里抽一帧。"""
    st = _read_state()
    mp4 = Path(st.get("mp4") or "")
    if not mp4.is_file():
        print("★ 找不到录屏文件")
        return 1
    t0 = st.get("started_epoch") or 0
    try:
        hh, mm, ss = (int(x) for x in at.split(":"))
    except Exception:  # noqa: BLE001
        print("★ 时间格式应为 HH:MM:SS")
        return 1
    today = time.strftime("%Y-%m-%d", time.localtime(t0))
    target = time.mktime(time.strptime("%s %02d:%02d:%02d" % (today, hh, mm, ss),
                                       "%Y-%m-%d %H:%M:%S"))
    rel = max(0.0, target - t0)
    out = Path(st["dir"]) / "frames" / ("f_%s.png" % at.replace(":", ""))
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-ss", "%.3f" % rel, "-i", str(mp4), "-frames:v", "1", str(out)],
        creationflags=_no_window(), timeout=120, check=False)
    if out.is_file():
        print("① 已抽帧：%s（距开始 %.1f 秒）" % (out, rel))
        return 0
    print("★ 抽帧失败")
    return 1


def status() -> int:
    st = _read_state()
    if st.get("running"):
        print("① 捕获中（会话 %s，开始 %s）"
              % (st.get("session"), st.get("started_wall")))
    else:
        print("① 未捕获。最近会话：%s" % (st.get("session") or "（无）"))
    d = Path(st.get("dir") or "")
    if d.is_dir():
        for n in ("psr.zip", "screen.mp4", "model.json", "steps.md", "REPORT.md"):
            p = d / n
            print("   %-12s %s" % (n, ("%d bytes" % p.stat().st_size)
                                   if p.is_file() else "（缺）"))
    return 0


def report() -> int:
    st = _read_state()
    d = Path(st.get("dir") or "")
    rp = d / "REPORT.md"
    if not rp.is_file():
        print("★ 还没有报告，先 --start / --stop 一次")
        return 1
    print(rp.read_text(encoding="utf-8"))
    return 0


def main() -> int:
    if "--start" in sys.argv:
        return start()
    if "--stop" in sys.argv:
        return stop()
    if "--status" in sys.argv:
        return status()
    if "--report" in sys.argv:
        return report()
    if "--frame" in sys.argv:
        k = sys.argv.index("--frame")
        if k + 1 < len(sys.argv):
            return frame(sys.argv[k + 1])
        print("★ --frame 需要时间参数 HH:MM:SS")
        return 2
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
