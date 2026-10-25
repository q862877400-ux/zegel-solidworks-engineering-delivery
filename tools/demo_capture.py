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

⚠ 用法注意：本命令是**长驻录制**（会拉起 ffmpeg 子进程），
  **不要**把它套在 tools/guard_run.py 里跑 —— 子进程会继承护栏的输出管道，
  护栏会一直等管道关闭而挂住（2026-10-26 实测踩过）。直接跑即可。
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
import os
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

#: 轨迹采样间隔（秒）—— 录制期轮询模型摘要的节奏（根因 C）
MIN_INTERVAL_S = 2.0
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


def _psr_alive() -> bool:
    """`psr.exe` 是否还在跑。

    ★ 2026-10-26 实操暴露：业主在 PSR 窗口点「停止记录」后，`psr.zip` 就在那一刻
      定稿，之后的操作**没有任何步骤文字**，而系统照旧以为在录。
      ⇒ 轮询进程必须能察觉这件事，并把它记进时间轴 + 报告。
    """
    try:
        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq psr.exe", "/NH"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=10, creationflags=_no_window(), check=False,
            stdin=subprocess.DEVNULL,
        )
        return "psr.exe" in (r.stdout or "")
    except Exception:  # noqa: BLE001
        return False


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
        print("★ 已在录（会话 {}）".format(st.get("session")))
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
         #: ★★★ 抗中断分片 MP4（2026-10-26 实操暴露）：原来用默认 MP4，
         #:   `stop()` 强杀 ffmpeg ⇒ `moov atom` 没写 ⇒ **整段录屏播不了**
         #:   （37MB 白录，`ffprobe` 报 "moov atom not found"）。
         #:   ★ 只加 `-movflags` **不够**：`frag_keyframe` 要等关键帧才写分片，
         #:   而 libx264 默认 GOP ≈31 秒 ⇒ 实测 12 秒后强杀只得到 **28 字节**。
         #:   必须配 `-g <小>`。实测（`output/test_frag_mp4.py`）：
         #:     无 movflags        → 播不了
         #:     分片但无 -g        → 28 字节（等于没录）
         #:     **分片 + -g 8**    → 能读 duration=6.0 · 能抽帧 ✓
         "-g", str(FPS),          #: 每秒一个关键帧 ⇒ 分片才写得出去
         "-movflags", "+frag_keyframe+empty_moov+default_base_moof",
         str(mp4)],
        stdin=subprocess.PIPE, creationflags=_no_window(),
    )
    #: ③ 拉起**轨迹轮询进程**（根因 C：录制期持续采样，不只拍终态）
    p3 = subprocess.Popen(  # noqa: S603
        [sys.executable, "-B", str(Path(__file__).resolve()), "--run"],
        creationflags=_no_window(),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    _write_state({
        "running": True, "session": sid, "dir": str(d),
        "timeline_pid": p3.pid,
        "psr_pid": p1.pid, "ffmpeg_pid": p2.pid,
        "started_epoch": t0,
        "started_wall": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t0)),
        "zip": str(zip_path), "mp4": str(mp4),
    })
    print("① 示范捕获已开始")
    print(f"   会话目录：{d}")
    print("   屏幕上应能看到「步骤记录器 - 现在正在录制」")
    print("   做完请说一声，我执行 --stop")
    return 0


def run() -> int:
    """**常驻录制进程**：轮询模型摘要，变化就落一条轨迹（由 --start 拉起）。

    ★ 为什么要有它（根因 C：录制是「录音」不是「拍照」）
      原来只在 --stop 时抓**一次**终态快照。业主实操暴露：步骤 66 草图还是**欠定义**
      （蓝色、没有 45° 尺寸），收工时是**完全定义** —— 中间怎么调出来的全丢了。
      ⇒ 录制期必须持续采样，形成时间轴。

    ★ COM 纪律：本进程是唯一的读取客户端；只读，且 CommandInProgress=False
      （否则会抑制用户的模态交互）。摘要很轻（只读计数与状态），高频安全。
    """
    st = _read_state()
    if not st.get("running"):
        print("★ 没有进行中的会话")
        return 0
    d = Path(st["dir"])
    pid_file = d / "running.pid"
    pid_file.write_text(str(os.getpid()), encoding="utf-8")
    t0 = float(st.get("started_epoch") or time.time())
    import sw_connect
    from sw_connect import get_com_member as g
    from sw_model_timeline import Timeline, summary_line

    tl = Timeline(d, t0)
    doc = None
    sw = None
    print(f"▶ 轨迹轮询已启动（每 {MIN_INTERVAL_S:.1f} 秒采样一次）")
    try:
        while pid_file.is_file():
            try:
                if sw is None:
                    conn = sw_connect.connect_solidworks(wait_seconds=10)
                    sw = conn[0] if isinstance(conn, tuple) else conn
                    try:
                        sw.CommandInProgress = False
                    except Exception:  # noqa: BLE001
                        pass
                doc = g(sw, "ActiveDoc") if sw is not None else None
                rec = tl.poll(doc)
                if rec:
                    print("   " + summary_line(rec))
                #: ★ 缺陷 2：PSR 被人手动停掉时，必须察觉并留证
                if not getattr(run, "_psr_gone", False) and not _psr_alive():
                    run._psr_gone = True
                    ev = tl.note_event(
                        "psr-stopped",
                        "psr.exe 已退出（可能被手动点了「停止记录」）；"
                        "此后的动作**没有步骤文字**，只有模型轨迹与录屏",
                    )
                    if ev:
                        print(f"   ⚠ #{ev['i']:03d} PSR 已停止 —— 之后的动作只有轨迹没有步骤")

                #: ★ 根因 D：顺带读「修改」框里的**实际数值**（PSR 记不到这些）
                try:
                    from sw_dialog_text import snapshot as _dlg_snapshot

                    drec = tl.note_dialog(_dlg_snapshot())
                    if drec:
                        nums = [n["text"] for dlg in drec["dialogs"]
                                for n in dlg.get("numbers") or []]
                        print("   #%03d %s 对话框 %s：%s" % (
                            drec["i"], drec["t"],
                            drec["dialogs"][0].get("title"),
                            ", ".join(nums[:4]) or "（无数值）"))
                except Exception:  # noqa: BLE001
                    pass
            except Exception as exc:  # noqa: BLE001
                #: 掉线就丢引用重连；不因为一次读失败就退出录制
                sw = None
                print(f"   （采样失败，重连：{type(exc).__name__}）")
            time.sleep(MIN_INTERVAL_S)
    except KeyboardInterrupt:
        pass
    print("■ 轨迹轮询结束，共 %d 条" % tl.n)
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
    print("   PSR 包：{} {}".format(Path(st["zip"]).name,
                              Path(st["zip"]).stat().st_size
                              if Path(st["zip"]).is_file() else "（未生成）"))
    print("   录屏：  {} {}".format(Path(st["mp4"]).name,
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
    #: ★ 让轨迹轮询进程收尾（删 pid 文件 → 它退出），并等它把 jsonl 写完
    pid_file = d / "running.pid"
    try:
        pid_file.unlink(missing_ok=True)
    except Exception:  # noqa: BLE001
        pass
    #: ★★★ 缺陷 1（质检 2026-10-26 发现）：pid 文件刚被自己删掉，
    #:   原来 `if not pid_file.exists(): break` **第一次就成立** ⇒ 等于没等，
    #:   可能读到 `run()` 还没写完的 timeline.jsonl。
    #:   现在按 **timeline_pid** 等进程真正退出（最多 10 秒）。
    tl_pid = st.get("timeline_pid")
    if tl_pid:
        for _ in range(50):
            if not _pid_alive(int(tl_pid)):
                break
            time.sleep(0.2)
    tl = _timeline_rows(d)
    st["timeline_rows"] = len(tl)
    if tl:
        print("   轨迹：%d 条（timeline.jsonl）" % len(tl))
    #: ★ 自动把 PSR 里的截图抽出来（根因 H：以前手写解析两次提取 0 张，
    #:   于是「看图核对」从来没做成）——现在用标准库 email 解析，一次就成。
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from extract_psr_shots import extract as _extract

        shots = _extract(Path(st["zip"]), d / "shots")
        st["shot_count"] = len(shots)
        if shots:
            print("   截图：%d 张（shots/，含步号索引）" % len(shots))
    except Exception as exc:  # noqa: BLE001
        st["shot_count"] = 0
        print(f"   （截图提取失败：{type(exc).__name__}）")

    st["dialog_events"] = _dialog_events(float(st.get("started_epoch") or 0))
    if st["dialog_events"]:
        print("   弹窗事件：%d 条" % len(st["dialog_events"]))
    _write_report(d, st, steps, snap)
    print("② 报告：%s" % (d / "REPORT.md"))
    return 0


def _pid_alive(pid: int) -> bool:
    """进程是否还活着（用 `tasklist` 查，不依赖 psutil）。"""
    try:
        r = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=15, creationflags=_no_window(), check=False,
            stdin=subprocess.DEVNULL,
        )
        out = (r.stdout or "").strip()
        #: 找不到时 tasklist 回「信息: 没有运行的任务…」或空 ⇒ 判死
        return str(pid) in out
    except Exception:  # noqa: BLE001
        return False


def _timeline_rows(d: Path) -> list:
    """读 timeline.jsonl（录制期的模型变化轨迹）。"""
    f = Path(d) / "timeline.jsonl"
    if not f.is_file():
        return []
    rows = []
    for line in open(f, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:  # noqa: BLE001
            continue
    return rows


def _dialog_events(started_epoch: float) -> list:
    """本次录制期间**护栏抓到的弹窗事件**（output/dialogs/events.jsonl）。

    ★ 业主 2026-10-26 要求「记录得特别全」⇒ 弹窗也是操作环境的一部分：
      它常常是「命令为什么没生效」的唯一线索，必须进同一份报告。
    """
    import json as _json

    log = R / "output" / "dialogs" / "events.jsonl"
    if not log.is_file():
        return []
    out = []
    cutoff = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(started_epoch - 5))
    try:
        for line in log.open(encoding="utf-8"):
            try:
                rec = _json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if str(rec.get("t") or "") >= cutoff:
                out.append(rec)
    except Exception:  # noqa: BLE001
        return out
    return out


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
        print(f"   ★ 模型快照失败：{type(exc).__name__}: {str(exc)[:80]}")
        return {}

    (d / "model.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = ["# 模型语义快照", "",
             "- 文档：`{}`".format(data.get("document")),
             "- 路径：`%s`" % (data.get("path") or "（未保存）"), "",
             "## 特征", ""]
    for f in data.get("features", []):
        lines.append("- `{}` — {}".format(f.get("name"), f.get("type")))
    for h in data.get("holes", []):
        lines += ["", "## 孔 `{}`".format(h.get("name")), "",
                  "- 标准：**{}** · 类型：{} · 规格：{}".format(h.get("standard"), h.get("fastener"), h.get("size"))]
        for sk in h.get("sketches", []):
            lines += _sketch_lines(sk, "   ")
    for sk in data.get("sketches", []):
        lines += _sketch_lines(sk, "")
    (d / "model.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return data


def _sketch_lines(sk: dict, indent: str) -> list:
    out = ["", "{}### {}（状态 {}）".format(indent, sk.get("name"), sk.get("constrained")),
           "", "{}- 点：{}".format(indent, sk.get("points"))]
    rels = sk.get("relations") or []
    if rels:
        out.append("%s- 关系/尺寸 %d 条：" % (indent, len(rels)))
        for r in rels:
            val = (" = {} mm".format(r["value_mm"])) if r.get("value_mm") is not None else ""
            out.append("{}  - **{}**{}  ← {}".format(indent, r.get("type"), val, " + ".join(r.get("refs") or [])))
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
        print(f"   ★ 解析 PSR 失败：{type(exc).__name__}")
        return None


def _coverage_gaps(d: Path, steps: list, st: dict) -> list:
    """回「覆盖缺口」的文字说明列表（供报告显著位置展示）。

    ★ 判据全基于**文件事实**，不看运行时状态 ⇒ 对已经录完的会话也成立。
    """
    out = []
    started = st.get("started_wall") or ""
    zip_p = Path(st.get("zip") or "")
    psr_stop = ""
    if zip_p.is_file():
        import datetime as _dt

        psr_stop = _dt.datetime.fromtimestamp(zip_p.stat().st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S")
    last_step = ""
    if steps:
        #: ★ `_steps_from_psr` 回的是 `{"n","time","text"}` 的 dict
        #:   （不是 `when`）。原来只认 `when`，于是"步骤覆盖到几点"永远算不出来，
        #:   连带「缺口多少秒」也判不出 —— 实测踩过。
        try:
            last = steps[-1]
            if isinstance(last, dict):
                last_step = str(
                    last.get("time") or last.get("when") or "")
            else:
                last_step = str(last[1])
        except Exception:  # noqa: BLE001
            last_step = ""
    tl_rows = _timeline_rows(d)
    last_tl = ""
    if tl_rows:
        last_tl = f"{tl_rows[-1].get('t')}（+{tl_rows[-1].get('elapsed_s')}s）"

    if started and last_step:
        out.append(
            f"步骤文字（PSR）覆盖：**{started} → {last_step}**，共 {len(steps)} 步。")
    if psr_stop:
        out.append(f"PSR 包定稿时刻：**{psr_stop}**（此后 PSR 不再记录任何动作）。")
    if last_tl:
        out.append(f"模型轨迹覆盖到：**{last_tl}**，共 {len(tl_rows)} 条。")
    #: 缺口判定：轨迹比步骤晚得多，就说明步骤丢了
    if last_step and tl_rows:
        try:
            import datetime as _dt

            fmt = "%Y/%m/%d %H:%M:%S"
            try:
                t_step = _dt.datetime.strptime(last_step, fmt)
            except ValueError:
                t_step = _dt.datetime.strptime(last_step, "%Y-%m-%d %H:%M:%S")
            t_tl = _dt.datetime.strptime(
                f"{st.get('started_wall', '')[:10].replace('-', '/')} "
                f"{tl_rows[-1].get('t')}", fmt)
            gap = (t_tl - t_step).total_seconds()
            if gap > 30:
                out.append(
                    f"⚠ **缺口 {gap:.0f} 秒**：这段时间**只有模型轨迹和录屏，"
                    "没有步骤文字** —— 通常是因为在 PSR 窗口点了「停止记录」。")
        except Exception:  # noqa: BLE001
            pass
    return out


def _write_report(d: Path, st: dict, steps, snap) -> None:
    lines = ["# 示范捕获报告", "",
             "- 会话：`{}`".format(st.get("session")),
             "- 开始：{}".format(st.get("started_wall")),
             "- 结束：{}".format(st.get("stopped_wall", "")),
             "- PSR：`{}`".format(Path(st["zip"]).name),
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
    #: ★ 覆盖缺口（2026-10-26 实操教训）：必须在**开头**就说清"哪段没有步骤"
    gaps = _coverage_gaps(d, steps or [], st)
    if gaps:
        lines += ["", "## ⚠ 记录覆盖范围（先看这个）", ""]
        lines += [f"- {x}" for x in gaps]
        lines.append("")

    #: ★★★ 模型变化**轨迹**（根因 C）：这是「怎么一步步做出来的」，不是终态
    tl = _timeline_rows(d)
    lines += ["", "## 模型变化轨迹（录制期采样）", ""]
    if tl:
        lines.append("共 **%d** 条变化记录（timeline.jsonl）；" % len(tl))
        if (d / "snaps").is_dir():
            lines.append("snaps/ 下是对应的完整快照。")
        lines.append("")
        lines.append("| # | 时刻 | 相对秒 | 变化 | 完整快照 |")
        lines.append("|---|---|---|---|---|")
        for rec in tl:
            ch = rec.get("changed") or {}
            bits = []
            for k, label in (("sketch_states", "草图状态"),
                             ("dimensions", "尺寸数"),
                             ("relations", "关系数"),
                             ("features", "特征数"),
                             ("sketches", "草图数"),
                             ("holes", "孔数"),
                             ("mates", "配合数")):
                if k in ch:
                    bits.append(f"{label} {ch[k][0]}→{ch[k][1]}")
            if rec.get("kind") == "dialog":
                #: ★ 对话框文字（尤其「修改」框里的数值）—— PSR 记不到这些
                dl = rec.get("dialogs") or []
                shown = []
                for dg in dl:
                    nums = [n["text"] for n in dg.get("numbers") or []]
                    shown.append("**{}**：{}".format(
                        dg.get("title"), " / ".join(nums) or
                        " / ".join(dg.get("fields") or [])[:1]))
                lines.append("| {} | {} | +{:.0f}s | 🗔 {} | — |".format(
                    rec.get("i"), rec.get("t"), rec.get("elapsed_s") or 0,
                    "；".join(shown)[:120]))
                continue
            lines.append("| {} | {} | +{:.0f}s | {} | {} |".format(
                rec.get("i"), rec.get("t"), rec.get("elapsed_s") or 0,
                " · ".join(bits) or "（首次）", rec.get("snapshot") or ""))
    else:
        lines.append("- 无（录制期间模型没变化，或未采到）")

    dialogs = st.get("dialog_events") or []
    if st.get("shot_count"):
        lines += ["", "## 截图", "",
                  "共 **%d** 张，在 shots/；"
                  "shots/index.tsv 给出「步号 → 文件」对照。" % st["shot_count"]]

    lines += ["", "## 弹窗事件（本次录制期间）", ""]
    if dialogs:
        for dg in dialogs:
            lines.append("- {} 「{}」：{}".format(dg.get("t"), dg.get("title"),
                            " / ".join(dg.get("kids") or [])[:120]))
    else:
        lines.append("- 无（或护栏日志里没有该时段记录）")
    if snap:
        lines += ["", "## 模型", "",
                  "- 文档：`{}`".format(snap.get("document")),
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
    out = Path(st["dir"]) / "frames" / ("f_{}.png".format(at.replace(":", "")))
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-ss", f"{rel:.3f}", "-i", str(mp4), "-frames:v", "1", str(out)],
        creationflags=_no_window(), timeout=120, check=False)
    if out.is_file():
        print(f"① 已抽帧：{out}（距开始 {rel:.1f} 秒）")
        return 0
    print("★ 抽帧失败")
    return 1


def status() -> int:
    st = _read_state()
    if st.get("running"):
        print("① 捕获中（会话 {}，开始 {}）".format(st.get("session"), st.get("started_wall")))
    else:
        print("① 未捕获。最近会话：%s" % (st.get("session") or "（无）"))
    d = Path(st.get("dir") or "")
    if d.is_dir():
        for n in ("psr.zip", "screen.mp4", "model.json", "steps.md", "REPORT.md"):
            p = d / n
            print("   %-12s %s" % (n, ("%d bytes" % p.stat().st_size)
                                   if p.is_file() else "（缺）"))
    return 0


def rebuild() -> int:
    """用当前代码**重新生成**报告（不改动原始证据，只重排 REPORT.md）。

    参数：`--rebuild [会话目录]`；省略则用 `session.json` 指向的会话。
    """
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        d = Path(args[0])
        st = _read_state()
    else:
        st = _read_state()
        d = Path(st.get("dir") or "")
    if not d.is_dir():
        print("★ 会话目录不存在：", d)
        return 1
    #: 补全会话级字段（老会话可能缺）
    st = dict(st)
    st.setdefault("session", d.name)
    st.setdefault("dir", str(d))
    for key, name in (("zip", "psr.zip"), ("mp4", "screen.mp4")):
        if not st.get(key):
            cand = d / name
            if cand.is_file():
                st[key] = str(cand)
    zip_p = Path(st.get("zip") or d / "psr.zip")
    steps = _steps_from_psr(zip_p, d) if zip_p.is_file() else []
    snap = {}
    snap_file = d / "model.json"
    if snap_file.is_file():
        try:
            import json as _json

            snap = _json.loads(snap_file.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            snap = {}
    _write_report(d, st, steps, snap)
    print("已重生成：", d / "REPORT.md")
    print("  步骤 %d · 轨迹 %d 条" % (len(steps or []), len(_timeline_rows(d))))
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
    if "--run" in sys.argv:
        return run()
    if "--start" in sys.argv:
        return start()
    if "--stop" in sys.argv:
        return stop()
    if "--status" in sys.argv:
        return status()
    if "--rebuild" in sys.argv:
        return rebuild()
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
