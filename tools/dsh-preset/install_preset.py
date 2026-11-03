"""把 DSH preset「Lean 模式（SW工程师）」装进当前 DSH profile —— 幂等、可回滚、路径自推算。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/dsh-preset/install_preset.py
# 定位:   ★ 业主 2026-11-03 指令：「把这个模式也放到项目里，相当于让这个项目自包含」。
#         ★★ 背景（实测）：preset 原建于 2026-10-07（见
#           `docs/history/HANDOFF-dsh-sw-engineer-preset.md`），落在
#           `~/.dsh/profiles/web/cordis.patch.yml`（853 → 1068 行）；**2026-10-17 该文件被
#           覆盖回 13 行**，插件也从 `node_modules/@local/` 消失 ⇒ 实战会话里**没有
#           `solidworks_*` 工具**，于是 544 个工具被绕过、改成手搓脚本直连 COM。
#         ⇒ 本安装器让**仓库自带**这个 preset 与插件，任何人 clone 后一条命令装好。
# 官方依据: `@deepseek-ai/dsh-agent-preset` README —— `plugins` 必填、**无继承机制**
#           ⇒ 只能把 `standard` 的插件逐行克隆（技能 `lean-preset-maintenance` §八亦警告：
#             上游改了插件组成要同步，否则被遮蔽）
#         `@deepseek-ai/dsh-mcp-client` 条目形状取自交接文档 §三（`serverName`/`transport`/
#           `failOnStartupError: false` —— 后者是硬教训：握手挂起会拖死 dsh boot）
# 许可:   本仓库 MIT。★ vendored 插件 `tools/dsh-preset/lean-mode/` 自带 LICENSE 与
#         THIRD-PARTY.md，随本目录一起分发。
# 覆盖:   单入口；`--dry-run` 只打印、`--apply` 才落盘
# ⚠ 只改 `cordis.patch.yml` 里**哨兵注释包住的区段**；改前写备份并打印一行回滚命令。
# -----------------------------------------------------------------------------
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

PRESET_ID = "sw-engineer"
PRESET_NAME = "Lean 模式（SW工程师）"
PRESET_ORDER = 9
BEGIN = "# >>> dsh-preset-sw-engineer（由 tools/dsh-preset/install_preset.py 管理，请勿手改）>>>"
END = "# <<< dsh-preset-sw-engineer <<<"
PLUGIN_NAME = "@local/dsh-lean-mode"


def _candidates_standard() -> list[Path]:
    """⇒ 候选的官方 `standard.patch.yml`（活配置优先，仓库快照兜底）。"""
    out: list[Path] = []
    home = Path(os.environ.get("DSH_HOME") or (Path.home() / ".dsh"))
    roots = [
        home.parent / "DSH-Portable" / "app" / "production",
        Path(r"D:\Agent-Studio\Deepseek-Harness\DSH-Portable\app\production"),
        Path(r"D:\Agent-Studio\Deepseek-Harness\DSH-Portable\app"),
    ]
    for root in roots:
        if root.is_dir():
            out.extend(sorted(root.glob("node_modules/@deepseek-ai/dsh-web-app/presets/standard.patch.yml")))
    out.append(HERE / "standard.snapshot.patch.yml")
    return out


def _pick_standard(explicit: str | None) -> tuple[Path | None, str]:
    """⇒ (路径, 来源说明)。"""
    if explicit:
        p = Path(explicit)
        return (p, "命令行指定") if p.is_file() else (None, f"命令行给的路径不存在: {p}")
    for p in _candidates_standard():
        if p.is_file():
            kind = "仓库快照（兜底）" if p.parent == HERE else "DSH 活配置"
            return p, kind
    return None, "找不到 standard.patch.yml"


def _plugins_block(standard: Path) -> tuple[list[str], int]:
    """⇒ (插件项各行, 计数)。★ 逐行原样搬运，保留 `!!js` 标签与缩进。"""
    lines = standard.read_text(encoding="utf-8").splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "plugins:":
            start = i + 1
            break
    if start is None:
        raise SystemExit("★ standard.patch.yml 里找不到 `plugins:` 行")
    block = lines[start:]
    #: ★ 只保留插件项（10 空格 `- id:` 起头）及其后缩进更深的属性行
    kept: list[str] = []
    n = 0
    for ln in block:
        if ln.startswith("          - id:"):
            n += 1
            kept.append(ln)
        elif ln.strip() == "":
            kept.append(ln)
        elif ln.startswith("           "):  #: 11+ 空格 ⇒ 属于上一个插件项
            kept.append(ln)
        else:
            break
    return kept, n


def _mcp_block(python_exe: str, repo: Path) -> list[str]:
    """⇒ `mcp-solidworks` 插件项（★ 路径按**本仓库实际位置**推算，不写死）。"""
    server = (repo / "mcp-server" / "server.py").as_posix()
    return [
        "          - id: mcp-solidworks",
        "            name: '@deepseek-ai/dsh-mcp-client'",
        "            config:",
        "              serverName: solidworks",
        "              transport: stdio",
        f"              command: '{python_exe}'",
        "              args:",
        f"                - '{server}'",
        f"              cwd: '{repo.as_posix()}'",
        "              toolCallTimeoutMs: 120000",
        "              failOnStartupError: false",
        "              reconnect: { enabled: true, initialDelayMs: 2000, maxDelayMs: 30000, maxAttempts: 20 }",
    ]


def build_section(standard: Path, python_exe: str, repo: Path) -> tuple[str, dict]:
    """⇒ (要追加的 YAML 文本, 统计)。"""
    plugins, n = _plugins_block(standard)
    mcp = _mcp_block(python_exe, repo)
    lines = [
        BEGIN,
        "# ① 第二个 lean-mode 实例：**只**对 preset 名 sw-engineer 生效（不碰 lean）",
        "- insert:",
        "    - id: lean-mode-sw",
        f"      name: '{PLUGIN_NAME}'",
        "      config:",
        "        presets:",
        f"          - {PRESET_ID}",
        "        maxChars: 300",
        "        descriptions: true",
        "        table: descriptions.json",
        "        pending: descriptions.pending.json",
        "",
        "# ② preset 本体：组成 = 官方 standard 逐行克隆 + mcp-solidworks",
        "- insert:",
        "    - id: preset-sw-engineer",
        "      name: '@deepseek-ai/dsh-agent-preset'",
        "      config:",
        f"        id: {PRESET_ID}",
        f"        name: {PRESET_NAME}",
        "        description: 与标准模式同组成，额外挂 SolidWorks MCP；呈现由 lean-mode-sw 接管。",
        f"        order: {PRESET_ORDER}",
        "        plugins:",
        *plugins,
        *mcp,
        END,
        "",
    ]
    return "\n".join(lines), {"standard_plugins": n, "with_mcp": n + 1, "standard": str(standard)}


def _strip_section(text: str) -> tuple[str, bool]:
    """⇒ (去掉哨兵区段后的文本, 是否曾经存在)。"""
    i = text.find(BEGIN)
    if i < 0:
        return text, False
    j = text.find(END, i)
    if j < 0:
        return text[:i], True
    j += len(END)
    #: 连同其后一个换行一起去掉
    while j < len(text) and text[j] in "\r\n":
        j += 1
    return text[:i] + text[j:], True


def main(argv: list[str] | None = None) -> int:
    """命令行入口。"""
    ap = argparse.ArgumentParser(description="安装/卸载 DSH preset「Lean 模式（SW工程师）」")
    ap.add_argument("--profile", default="web", help="目标 profile 名（默认 web）")
    ap.add_argument("--dsh-home", default=None, help="DSH home（默认 $DSH_HOME 或 ~/.dsh）")
    ap.add_argument("--standard", default=None, help="指定 standard.patch.yml（默认自动找）")
    ap.add_argument("--python-exe", default=sys.executable, help="MCP server 用的 python（默认当前解释器）")
    ap.add_argument("--apply", action="store_true", help="真的写入（否则只打印计划）")
    ap.add_argument("--uninstall", action="store_true", help="移除本 preset 与插件")
    ap.add_argument("--no-plugin", action="store_true", help="只改 cordis.patch.yml，不装插件")
    ap.add_argument(
        "--force-replace",
        action="store_true",
        help="★ 目标里已有**手写**的 preset-sw-engineer 时也覆盖（默认拒绝）",
    )
    ap.add_argument("--verify", action="store_true", help="装完做真 MCP 握手，报工具数")
    a = ap.parse_args(argv)

    home = Path(a.dsh_home) if a.dsh_home else Path(os.environ.get("DSH_HOME") or (Path.home() / ".dsh"))
    profile_dir = home / "profiles" / a.profile
    target = profile_dir / "cordis.patch.yml"
    report: dict = {"repo": str(REPO), "dsh_home": str(home), "profile": a.profile,
                    "target": str(target), "apply": bool(a.apply)}

    if not target.is_file():
        print(json.dumps({**report, "error": "目标 cordis.patch.yml 不存在"}, ensure_ascii=False, indent=1))
        return 2

    text = target.read_text(encoding="utf-8")
    stripped, existed = _strip_section(text)

    #: ★★ 安全闸（2026-11-03）：目标里已经有**手写**的 `preset-sw-engineer`
    #:   （不在我们的哨兵区段内）时**默认拒绝覆盖** —— 实测本机那份 1789 行活配置里有大量
    #:   手写注释（542 工具对账、GitHub MCP 槽位、REA preset 说明），覆盖就是销毁信息。
    #:   ⇒ 这种机器应当**继续用手写版**；本安装器面向**新机器**（干净 profile）。
    if not existed and not a.uninstall and not a.force_replace:
        if "id: sw-engineer" in stripped:
            report["refused"] = (
                "目标 cordis.patch.yml 里已有**手写**的 preset-sw-engineer（不在本安装器的"
                "哨兵区段内）⇒ 拒绝覆盖。★ 这份机器继续用手写版即可；"
                "确要换成生成版，加 --force-replace。"
            )
            print(json.dumps(report, ensure_ascii=False, indent=1))
            return 4

    if a.uninstall:
        report["had_section"] = existed
        if a.apply:
            if existed:
                bak = target.with_name(target.name + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-before-uninstall-sw-preset")
                shutil.copy2(target, bak)
                target.write_text(stripped, encoding="utf-8", newline="\n")
                report["backup"] = str(bak)
            plug = profile_dir / "node_modules" / "@local" / "dsh-lean-mode"
            if plug.is_dir():
                shutil.rmtree(plug)
                report["plugin_removed"] = str(plug)
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 0

    std, why = _pick_standard(a.standard)
    report["standard_source"] = why
    if std is None:
        print(json.dumps({**report, "error": why}, ensure_ascii=False, indent=1))
        return 3

    section, stats = build_section(std, a.python_exe, REPO)
    report.update(stats)
    report["replaced_existing"] = existed
    report["mcp_server"] = str(REPO / "mcp-server" / "server.py")

    if not a.apply:
        report["plan_lines"] = len(section.splitlines())
        print(json.dumps(report, ensure_ascii=False, indent=1))
        print("\n--- 将追加的区段（前 14 行）---")
        for ln in section.splitlines()[:14]:
            print("  " + ln)
        print("  ...")
        print("\n★ 这是 dry-run。加 --apply 才落盘。")
        return 0

    bak = target.with_name(target.name + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-before-apply-sw-preset")
    shutil.copy2(target, bak)
    new_text = stripped.rstrip("\n") + "\n\n" + section
    target.write_text(new_text, encoding="utf-8", newline="\n")
    report["backup"] = str(bak)

    if not a.no_plugin:
        src = HERE / "lean-mode"
        dst = profile_dir / "node_modules" / "@local" / "dsh-lean-mode"
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst)
            report["plugin_installed"] = str(dst)
            report["plugin_files"] = sum(1 for _ in dst.rglob("*") if _.is_file())
        else:
            report["plugin_error"] = f"仓库里找不到 vendored 插件: {src}"

    report["rollback"] = f'copy "{bak}" "{target}"'
    print(json.dumps(report, ensure_ascii=False, indent=1))
    print("\n★ 装好了。**要生效必须重启 dsh**，然后在新建会话里选 preset「%s」。" % PRESET_NAME)
    print("★ 一行回滚：copy \"%s\" \"%s\"" % (bak, target))

    if a.verify:
        import subprocess  # noqa: PLC0415 - 仅此处需要
        probe = REPO / "tools" / "probe_mcp_stdio_handshake.py"
        if probe.is_file():
            r = subprocess.run((sys.executable, "-B", str(probe)), cwd=str(REPO),
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding="utf-8", errors="replace")
            tail = [ln for ln in (r.stdout or "").splitlines() if "tools/list" in ln or "initialize" in ln]
            print("★ 真 MCP 握手复核（判据：tools/list 有数才算装好）：")
            for ln in tail[-4:]:
                print("   " + ln.strip())
            if r.returncode != 0:
                print("⚠ 握手探针非零退出，需人工看输出")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
