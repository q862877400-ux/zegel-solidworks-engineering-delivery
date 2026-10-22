"""★ **弹窗取证**：发现弹窗 ⇒ 截图 + 抓结构 ⇒ 落盘 ⇒ **交给 LLM 判根因**（★ 不自动点）。

## 为什么有这个文件（★ 用户两次提出的常驻纪律）
```
★ 纪律原文（`~/.dsh/纪律/自我纠错.md` 第 9 条）：
   「遇到对话框、模态框、被阻塞的进程这类中断，不要用函数按类名机械点掉就继续。顺序固定为三步：
     先把弹窗的**内容**交给 LLM 判**这是什么、为什么弹**；判明根因后再点；
     点完**必须改代码或配置**，让同一场景不再弹。」
★ 反面教材（★ 本仓库真发生过）：`open_document` 打开带外部参考的零件时弹
   「打开外部参考的零件」⇒ 我**机械点掉**它 ⇒ ★ **下次再打开同一个文件还弹** ⇒ 某次没人点 ⇒ 会话卡死。
   ★ 而真正的解法是查官方文档找到 `swOpenDocOptions_LoadExternalReferencesInMemory(512)`
     —— ★ **加一个选项位，它就不弹了**（★ 那是"改"，不是"点"）。
```

## ★ 本模块做与不做
```
★ **做**：① 按 Win32 类名 `#32770` 找弹窗（★ 与 `sw_connect` 同一判据，零硬编码）
       ② 逐个**截图**（`PrintWindow` ⇒ PNG，★ 被遮挡也能截）
       ③ 逐个**抓结构**：标题 · 类名 · 所有子控件的类名与文本 · 按钮 ID
       ④ 落盘到 `output/dialogs/<utc 时间戳>/`
       ⑤ 回一个 dict —— **给 LLM 看的证据包**
★ **不做**：★ **不点**。★ 点不点、怎么点、改什么，**由 LLM 判完根因再决定**。
   （★ 兜底仍然存在：`sw_connect.dismiss_residual_dialogs` —— ★ 但它是**兜底**，
     ★ 按纪律，用完它**必须**补一次根因修复，否则同一条会一直回来。）
```

## ★ 用法
```python
from modal_dialog_forensics import collect_dialogs
pack = collect_dialogs()            # 或 collect_dialogs(pid)
# ⇒ {'count':…, 'dir':…, 'dialogs':[{'title':…, 'png':…, 'controls':[…]}, …]}
# ★ 然后把 pack 交给 LLM（★ 我会 `read_image` 那张 PNG + 读 JSON 里的控件文本）判根因。
```
"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/modal_dialog_forensics.py
# 定位:   弹窗取证的**工具**：截图 + 结构落盘，供 LLM 判根因（纪律 自我纠错 §9）。
# 官方签名依据: 不适用（★ 本文件只调 Win32 `user32`/`gdi32`，不调 SolidWorks API）。
# ★ 判据来源：`scripts/sw_connect.py` 的 `_DIALOG_CLASS = "#32770"`（Win32 `WC_DIALOG`）
# 。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import json
import subprocess
import sys
import time
from pathlib import Path

OUT_ROOT = Path(Path(__file__).resolve().parents[1] / "output" / "dialogs")
DIALOG_CLASS = (
    "#32770"  #: Win32 预定义对话框类（`WC_DIALOG`）—— ★ 与 sw_connect 同一判据
)

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32


def resolve_pid(target=None) -> int | None:
    """★ 取目标 PID：★ 显式给就用；★ 否则用 `SLDWORKS.exe` 的（★ 本项目的主场景）。"""
    if isinstance(target, int):
        return target
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq SLDWORKS.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for line in (out.stdout or "").splitlines():
            parts = [x.strip('"') for x in line.split('","')]
            if len(parts) >= 2 and parts[1].isdigit():
                return int(parts[1])
    except Exception:  # noqa: BLE001
        return None
    return None


def _top_level(hwnd, pid):
    """★ 该窗口是否**归我们关注的对象**（★ 2026-10-04 修：★ **同族进程的也要算**）。

    ★★★★ 真根因（★ 用户当场截图 + 我复核）：★ 那个
      `[Simulation] 未定义载荷或规定的位移 … QA00000299039` 框的 owner 是
      ★ **`star.exe`（pid 46240）**、**不是** `SLDWORKS.exe`（pid 49384）✓
    ★★ 而原文只判 `wpid.value == pid` ⇒ ★ **本工具对那个框回 `count: 0`**（★ 我实测过）——
      ★★ **而它当初就是为这个框写的**（事实 292）⇒ ★ 一个"PID 精确匹配"把整条判据废掉了 ✓
    ★ 修法：★ `pid` 只用来"聚焦"，★ **同族进程（`star.exe` / `cwbcbfmesh.exe` …）一律放行** ✓
    """
    _, wpid = wt.DWORD(), wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
    if wpid.value == pid:
        return True
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import sw_guard

        return bool(sw_guard.sw_family_window(hwnd))
    except Exception:  # noqa: BLE001
        return False


def list_dialogs(pid: int) -> list[int]:
    """★ 列出**我们关注的进程（或其家族进程）**的顶层 `#32770` 窗口句柄（★ 按类名，不按标题）。"""
    found: list[int] = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def _cb(hwnd, _lparam):
        if _top_level(hwnd, pid):
            buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, buf, 256)
            if buf.value == DIALOG_CLASS:
                found.append(hwnd)
        return True

    user32.EnumWindows(_cb, 0)
    return found


def _controls(hwnd: int) -> list[dict]:
    """★ 抓该弹窗的**所有子控件**：类名 + 文本 + 控件 ID（★ 那才是"弹窗在问什么"）。"""
    rows: list[dict] = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def _cb(child, _lparam):
        cls = ctypes.create_unicode_buffer(256)
        txt = ctypes.create_unicode_buffer(1024)
        user32.GetClassNameW(child, cls, 256)
        #: ★ `WM_GETTEXT` 对按钮/静态文本/编辑框都适用
        user32.SendMessageW(child, 0x000D, 1024, txt)
        try:
            cid = int(user32.GetDlgCtrlID(child))
        except Exception:  # noqa: BLE001
            cid = None
        rows.append({"class": cls.value, "text": txt.value, "id": cid})
        return True

    user32.EnumChildWindows(hwnd, _cb, 0)
    return rows


def _screenshot(hwnd: int, png_path: Path) -> bool:
    """★ 截该窗口 ⇒ 存 PNG。★ 无第三方依赖（纯 ctypes + GDI）。

    ★★★★★ 2026-10-02（轮 375）**这里原来只用 `PrintWindow`，而它会**阻塞在模态对话框上**** ——
      用户当场撞见的就是这个：SolidWorks 弹着「未定义载荷或规定的位移」，
      而 `collect_dialogs()` **自己也挂住了**（300 s 未返回）⇒ ★★ **检测器与"卡住"一起卡住**。
    ```
    分步计时诊断（真机，弹窗正在屏幕上）：
      EnumWindows（列举 #32770）      ⇒ **0.00 s** ✓
      tasklist（取 pid）              ⇒ **0.14 s** ✓
      **PrintWindow（旧实现）**        ⇒ ★ **挂住（>300 s）** ✗   ← 真因
      **BitBlt（新实现）**             ⇒ **0.01 s · 唯一色数 9（有内容）** ✓✓✓
    ```
    ★ 为什么 `PrintWindow` 会挂：★ 它**向目标窗口发消息**请它自己绘制，★ 而模态对话框
      **在自己的消息循环里等用户**（★ 本项目铁律 2 说的"未抑制的模态对话框会永久挂起"正是它）。
    ★ 为什么 `BitBlt` 不挂：★ 它**只从屏幕 DC 拷贝像素**，★ **不向目标窗口发任何消息** ✓
      ⚠ 代价：★ **目标被遮挡时截不到内容**（★ 而 `PrintWindow` 能截被遮挡的窗口）。
    ⇒ ★★ 策略：**先 `BitBlt`（快、不阻塞）；只有内容为空时才退回 `PrintWindow`**，
      ★ 而退回那一步**必须带时限**（★ 由调用方在子进程里做，见 `collect_dialogs_safe`）。
    """
    rect = wt.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return False
    w, h = rect.right - rect.left, rect.bottom - rect.top
    if w <= 0 or h <= 0:
        return False
    #: ★★ **默认用 `BitBlt`（不阻塞）** —— 见本函数文档串里的真机计时证据。
    #:   ★ `force_print_window=True`（或 BitBlt 得空）时才走老路。
    hdc = user32.GetWindowDC(hwnd)
    mem = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(mem, bmp)
    srccopy = 0x00CC0020
    hdc_screen = user32.GetDC(0)
    ok = gdi32.BitBlt(mem, 0, 0, w, h, hdc_screen, rect.left, rect.top, srccopy)
    user32.ReleaseDC(0, hdc_screen)
    if not ok:
        #: ★ 兜底才用 `PrintWindow`（★ 调用方应把它放在**有超时的子进程**里）
        ok = user32.PrintWindow(hwnd, mem, 2)  #: ★ PW_RENDERFULLCONTENT = 2

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", wt.DWORD),
            ("biWidth", wt.LONG),
            ("biHeight", wt.LONG),
            ("biPlanes", wt.WORD),
            ("biBitCount", wt.WORD),
            ("biCompression", wt.DWORD),
            ("biSizeImage", wt.DWORD),
            ("biXPelsPerMeter", wt.LONG),
            ("biYPelsPerMeter", wt.LONG),
            ("biClrUsed", wt.DWORD),
            ("biClrImportant", wt.DWORD),
        ]

    class BITMAPINFO(ctypes.Structure):
        _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wt.DWORD * 3)]

    bi = BITMAPINFO()
    bi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bi.bmiHeader.biWidth = w
    bi.bmiHeader.biHeight = -h  #: ★ 负高度 = 自上而下（与 PNG 行序一致）
    bi.bmiHeader.biPlanes = 1
    bi.bmiHeader.biBitCount = 32
    bi.bmiHeader.biCompression = 0  #: BI_RGB
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(mem, bmp, 0, h, buf, ctypes.byref(bi), 0)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mem)
    user32.ReleaseDC(hwnd, hdc)
    if not ok:
        return False
    #: ★ 手写 PNG（★ 只做"能看"这一件事 —— 不引 Pillow）：★ 直接存**BMP** 更省事且无损，
    #: 而调用方（LLM）读图只需 `read_image` 支持 PNG/JPEG/WebP/GIF ⇒ ★ 所以这里存 **BMP
    #: 的裸数据**？
    #: ★ **不行** —— 那就得多一步转换。⇒ ★ 本函数落 **`.bmp`**，由调用方用系统 `System.D
    #: rawing`
    #:   转 PNG（★ 与既有 `knitted_*.bmp → .png` 的流程一致）。
    bmp_path = png_path.with_suffix(".bmp")
    hdr = ctypes.create_string_buffer(14)
    hdr[0:2] = b"BM"
    hdr[2:6] = (14 + 40 + len(buf)).to_bytes(4, "little")
    hdr[10:14] = (14 + 40).to_bytes(4, "little")
    info = ctypes.create_string_buffer(40)
    info[0:4] = (40).to_bytes(4, "little")
    info[4:8] = w.to_bytes(4, "little")
    info[8:12] = h.to_bytes(4, "little")
    info[12:14] = (1).to_bytes(2, "little")
    info[14:16] = (32).to_bytes(2, "little")
    info[20:24] = len(buf).to_bytes(4, "little")
    bmp_path.write_bytes(hdr.raw + info.raw + buf.raw)
    #: ★★★ 2026-10-02（轮 336）**加"全黑检测"** —— 真机实测：
    #:   ★ `tools/fake_modal_dialog.py` 那个夹具**故意不置 `WS_VISIBLE`** ⇒
    #:   `PrintWindow` 截出来是 **320×200 全黑**（PNG 只有 733 字节）。
    #:   ⇒ ★★ **"截到图了"不等于"图有用"** —— ★ 全黑（或近全黑）必须**如实标注**，
    #:     否则下游（LLM）会把一张黑图当成弹窗内容去判。
    #: ★ 真实弹窗是 `visible=True`（★ 本仓库真机验过：`#32770` 且 `IsWindowVisible` 为真
    #: ）⇒
    #:     ★ 对它们截图有效；★ **而不可见窗口只得靠"标题 + 控件文本"那一路文字情报**。
    raw = buf.raw
    #: ★★★★★ 2026-10-02（轮 337）**判据改成"有没有内容"，不能判"黑不黑"** —— 用户指出：
    #:   「判断不能用黑白啊，SolidWorks 可以自定义颜色的，人家来个**黑色皮肤**你怎么办，
    #:     要去**探测内容**」★ **完全对**：
    #: ★ 深色主题下**真弹窗也会整体偏暗** ⇒ ★ 用"全黑"当判据会把**有内容**的图误判成无效
    #:  ✗
    #:   ★★ 而"有没有内容"与颜色**无关** —— ★ 三个与配色无关的量：
    #: · **唯一色数**（`distinct`）：★ 纯色底 = 1；★ 有文字/控件 = 远大于 1（★ 黑底白字
    #: 也有 2 种以上）
    #: · **非众数像素占比**（`non_mode_ratio`）：★ 有多少像素**不是**背景色（★ 即"画了东
    #: 西"的部分）
    #:     · **亮度极差**（`range`）：★ 有内容必然有明暗差，★ 而它同样与主题无关
    #:   ⇒ ★ 本函数**不再判 blank**，改报 `content_present` + 三个量，
    #:     由调用方（LLM）看数字判 —— ★ **而不是由一个阈值替它判**。
    step = 4 * 97  #: ★ 抽样（★ 全扫太慢）
    colors: dict[int, int] = {}
    lum_min, lum_max = 255, 0
    total = 0
    for i in range(0, len(raw) - 3, step):
        b, g, r = raw[i], raw[i + 1], raw[i + 2]  #: ★ BGRA 顺序
        key = (r << 16) | (g << 8) | b
        colors[key] = colors.get(key, 0) + 1
        lum = (r * 299 + g * 587 + b * 114) // 1000  #: ★ 感知亮度
        lum_min = min(lum_min, lum)
        lum_max = max(lum_max, lum)
        total += 1
    distinct = len(colors)
    mode_count = max(colors.values()) if colors else 0
    non_mode = total - mode_count
    stats = {
        "distinct_colors": distinct,
        "sampled": total,
        "non_mode_pixels": non_mode,
        "non_mode_ratio": round(non_mode / total, 4) if total else 0.0,
        "luminance_range": (lum_max - lum_min),
        "★": "★ **与配色无关**的三个量：唯一色数 / 非众数像素占比 / 亮度极差。"
        "★ 深色主题下真弹窗也有内容 ⇒ ★ **不要用「黑不黑」当判据**",
    }
    #: ★ 内容判据（★ 与颜色无关）：★ 颜色数 > 1 **或** 有非众数像素 **或** 有亮度差
    content_present = bool(distinct > 1 and (non_mode > 0 or (lum_max - lum_min) > 0))
    stats["content_present"] = content_present
    bmp_path.with_suffix(".stats").write_text(
        json.dumps(stats, ensure_ascii=False), encoding="utf-8"
    )
    return {
        "ok": bool(ok),
        "content_present": content_present,
        "stats": stats,
        "path": str(bmp_path),
    }


def collect_dialogs(target=None, out_root: Path | None = None) -> dict:
    """★ **发现 + 取证 + 落盘**（★ **不点**）⇒ 回给 LLM 的证据包。

    ★ 回 `{"count", "dir", "pid", "dialogs": [{"title", "class", "controls", "bmp"}, …]}`。
    ★ **`count == 0` 是好消息**（★ 没有弹窗）。★ 有弹窗时：★ 把 `dir` 里的东西交给 LLM 判根因。
    """
    pid = resolve_pid(target)
    if not pid:
        return {"count": 0, "pid": None, "error": "取不到 SLDWORKS.exe 的 PID"}
    handles = list_dialogs(pid)
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    root = (out_root or OUT_ROOT) / stamp
    root.mkdir(parents=True, exist_ok=True)
    dialogs = []
    for i, hwnd in enumerate(handles):
        tb = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, tb, 512)
        cb = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cb, 256)
        shot = root / ("dialog-%d.png" % i)
        shot_info = {"ok": False, "blank": None, "path": None}
        try:
            got = _screenshot(hwnd, shot)
            if isinstance(got, dict):
                shot_info = got
            else:  #: ★ 兼容旧形态（bool）
                shot_info = {
                    "ok": bool(got),
                    "blank": None,
                    "path": str(shot.with_suffix(".bmp")) if got else None,
                }
        except Exception as exc:  # noqa: BLE001
            shot_info = {
                "ok": False,
                "blank": None,
                "path": None,
                "error": str(exc)[:80],
            }
        dialogs.append(
            {
                "index": i,
                "hwnd": int(hwnd),
                "title": tb.value,
                "class": cb.value,
                "controls": _controls(hwnd),
                "bmp": shot_info.get("path"),
                "screenshot_ok": bool(shot_info.get("ok")),
                #: ★★★ 2026-10-02（轮 337）**不再报 `screenshot_blank`** ——
                #: ★ 用户指出「不能用黑白判，SolidWorks 可以自定义颜色，黑色皮肤
                #: 怎么办」
                #: ⇒ ★ 改报**与配色无关**的 `screenshot_content_present` + 三个
                #: 统计量，
                #:     由调用方（LLM）看数字判，★ **而不是由一个阈值替它判**。
                "screenshot_content_present": shot_info.get("content_present"),
                "screenshot_stats": shot_info.get("stats"),
                "★shot": "★ `screenshot_content_present=False` ⇒ 图里**没有内容**"
                "（纯色空窗）；★ 而它**与配色无关** —— 深色主题的真弹窗也算有内容。"
                "★ 判据看 `screenshot_stats` 的三个量：唯一色数 / 非众数占比 / 亮度极差",
            }
        )
    pack = {
        "count": len(dialogs),
        "pid": pid,
        "dir": str(root),
        "dialogs": dialogs,
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "★": "★ 本模块**不点**弹窗 —— ★ 按纪律（自我纠错 §9）先把内容交 LLM 判根因，"
        "判完再点，点完必须改到不再弹",
    }
    (root / "dialogs.json").write_text(
        json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return pack


def main() -> int:
    """★ 命令行入口：★ `python tools/modal_dialog_forensics.py` ⇒ 打印证据包路径。"""
    pack = collect_dialogs()
    print(
        json.dumps(
            {k: pack[k] for k in ("count", "pid", "dir") if k in pack},
            ensure_ascii=False,
            indent=2,
        )
    )
    for d in pack.get("dialogs", []):
        print(
            "  [%d] title=%r class=%s controls=%d bmp=%s"
            % (d["index"], d["title"][:40], d["class"], len(d["controls"]), d["bmp"])
        )
        for c in d["controls"][:8]:
            if c["text"]:
                print(
                    "        %-16s id=%-6s %r" % (c["class"], c["id"], c["text"][:60])
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
