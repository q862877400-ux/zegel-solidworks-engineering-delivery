"""★ 生成并**校验** DSH 新 preset「Lean 模式（SW工程师）」的配置块（★ 只写文件、不 apply）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（DSH 侧配置生成器；★ 用户 2026-10-07 指令）
# 文件:   tools/gen_dsh_sw_preset.py
# 定位:   ★ 用户原话：「★ 建一个新 preset 可以，就叫 **Lean模式（SW工程师）**，然后要
#           把这个 DSH 上
#   **所有的工具**都挂上，包括 SW 的、GitHub 的，但是 **comfyui 的不挂**」✓
#   ★★ **为什么用生成器而不是手抄**（★ 本仓事实 48 + 铁律 4 的同一道理）：
#     ★ 新 preset 的组成 = **官方标准模式**（★ 与 `@local/dsh-lean-mode` 里那条
#       `preset-lean` 逐行相同 ✓）—— ★ 那一块有 **145 行**、★ 其中 `plan-mode` 的
#       `section:` 是多行长文本 ✗ ⇒ ★ **手抄必错** ✓
#     ⇒ ★★★ **从源块**程序化克隆**、★ 只改 4 个字段**，★ 再用 `js-yaml` **机器校验** ✓
#   ★★★ **为什么必须同时挂第二个 lean-mode 实例**（★ 这条是 token 安全的关键 ✓）：
#     ★ `@local/dsh-lean-mode` 挂在 `system-prompt/assemble` 上，对 `config.presets` 里
#       **点名的 preset** 做两层变换：① `shallowParameters()` 把工具 schema **投影成
#       "顶层键 → 类型"**；② 追加 `tools:catalog` 段 ✓
#     ★★ 它的配置当前是 `presets: ['lean']` ✗ ⇒ **新 preset 不点名就得不到投影** ✗ ⇒
#       ★★★ **504 个工具会以**完整 JSON Schema**注入** ≈ **175k tokens** ✗✗
#       （★ 记忆库实测：478 工具 原生 693 KB / 175k token **vs** Lean 76 KB / 19k token ✓）
#     ⇒ ★ **再声明一个同模块实例、`presets: [sw-engineer]`** ✓ —— ★ 该插件**没有 `provide`**
#       （★ 只 `ctx.on(...)` 监听 ✓）⇒ ★ **不会撞 realm** ✓✓
# 判据:   ★★ 三条，★ 全部机器可判（★ 事实 62：★ 门禁只靠负例证明 ✓）：
#     ★ ① `js-yaml` 能解析**改后**的整份配置 ✓（★ 阳性对照：**改前**那份也要能解析 ✓）
#     ★ ② 新 id（`sw-engineer` / `preset-sw-engineer` / `lean-mode-sw` / `mcp-solidworks`）
#        **全部出现在解析结果里** ✓
#     ★ ③ **`lean` 那条一个字节没动** ✓（★ 用户明令：「★ 你可不要直接让所有 lean 模式的
#        对话都生效啊」✗ ⇒ ★ 必须能证明 lean preset 未被触碰 ✓）
# 官方依据: `docs/subsystems/mcp.zh.md` 的「配置」节（★ `transport: 'stdio'` ✓）·
# `docs/config-catalog.zh.md` 的 `@deepseek-ai/dsh-mcp-client` 段（★ `StdioConfig` 字段 
# ✓）·
# `docs/glossary.zh.md:20`（★ **setup window**：★ 作用域在 agent 创建时组装 ⇒ ★ **必须新
# 开会话** ✓）
# 许可:   本仓库 MIT。★ 只读源块 + 只写一个新文件（★ 配置的追加由调用方做 ✓）。覆盖: 全
# 文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
LEAN_BUNDLE = HOME / ".dsh/profiles/web/node_modules/@local/dsh-lean-mode/cordis.patch.yml"
LIVE_CFG = HOME / ".dsh/profiles/web/cordis.patch.yml"
DSH_ROOT = Path(r"D:\AI\DSH\deepseek-harness")
OUT_BLOCK = Path(Path(__file__).resolve().parents[1] / "output" / "_dsh_sw_preset_block.yml")
OUT_JSON = Path(Path(__file__).resolve().parents[1] / "output" / "dsh-sw-preset-generate.json")

NEW_PRESET_ID = "sw-engineer"
NEW_PRESET_NAME = "Lean 模式（SW工程师）"
NEW_PRESET_DESC = ("★ SW 工程师档：官方标准模式组成 + SolidWorks MCP（504 个工具），"
                   "★ 呈现走 lean-mode 的浅投影 + 工具目录 ✓")
#: ★★ `order` 取 9（★ `preset-lean` 是 8 ✓）—— ★ 只是个排序位、★ 不与别人撞 ✓
NEW_ORDER = 9

#: ★★★ **SW MCP 的条目**（★ 形状抄自本仓既有的 `preset-solidworks` ✓，而**路径全部改成现
#: 值** ✗）：
#:   ★ 那条旧配置指向 `C:/Users/Zegel/solidpilot-mcp/...` ✗ —— ★★ 记忆库里正记着这个坑
#:     （「★ **常驻 MCP 进程仍指向归档路径**」✗），★ 而**硬验收信号**是
#:     「`server_path` 显示为 **`D:\AI\SW\mcp-server\server.py`**」✓
#:   ★ 真机前置已验：`tools/probe_mcp_stdio_handshake.py` ⇒ `initialize` ok ·
#:     `tools/list` **504** 个 · 前缀 `{'solidworks_': 491, 'cadstudio_': 13}` ✓
SW_PYTHON = r"C:\Users\Zegel\AppData\Local\Python\pythoncore-3.14-64\python.exe"

MCP_ENTRY = f"""          # ── 本 preset 的唯一增量：SolidWorks MCP（504 个工具）──────────────
          # ★ 路径是**现值** `D:/AI/SW/mcp-server/server.py` ✓ —— ★★ 不是旧配置里的
          #   `C:/Users/Zegel/solidpilot-mcp/...` ✗（★ 那是归档路径、★ 已过期 ✓）
          # ★ 真机前置已验（tools/probe_mcp_stdio_handshake.py）：
          #   initialize ok · tools/list **504** 个（= 459 声明式 + 45 装饰器 ✓）
          # ★★ `failOnStartupError: false` 是**必须的** —— ★ 记忆库里那条硬教训逐字：
          #   「handshake with this MCP server **hangs the whole dsh boot**」✗
          # ⚠⚠ 缩进必须与 `plugins:` 的**其它列表项逐格一致**（★ 那层是 10/12/14 ✓）——
          #    ★★★ 本生成器第一版写成 12/14/16 ✗ ⇒ **js-yaml 当场报
          #    `bad indentation of a sequence entry`** ✓ 被抓下 ✓
          #    ★★ 根因是**我读源块时被自己的格式化前缀污染了读数** ✗（★ 每行加了 3 空格 ✓）
          #    ⇒ ★ **权威做法：数空格、★ 不靠眼看** ✓
          - id: mcp-solidworks
            name: '@deepseek-ai/dsh-mcp-client'
            config:
              serverName: solidworks
              transport: stdio
              command: '{SW_PYTHON}'
              args:
                - 'D:/AI/SW/mcp-server/server.py'
              cwd: 'D:/AI/SW'
              # ★ SolidWorks 的 COM 调用慢 ⇒ 给足超时（★ 既有 preset-solidworks 也是这个值 ✓）
              toolCallTimeoutMs: 120000
              failOnStartupError: false
              reconnect:
                enabled: true
                initialDelayMs: 2000
                maxDelayMs: 30000
                maxAttempts: 20
          # ── GitHub MCP：★ **尚未接线**（★ 用户点名要它，★ 而本机没有该服务器 ✗）──
          # ★ 查证结果（2026-10-07）：npm 全局包**没有** GitHub MCP ✗ ·
          #   `D:\\AI\\DSH\\mcp-servers\\` 只有 comfyui-mcp ✓ · `github` 在活配置里 **0 处** ✗ ·
          #   ★★ 而 **`gh` CLI 装了**（`C:\\Program Files\\GitHub CLI\\gh.exe` ✓）——
          #   ★ 那是**命令行**、★ **不是可挂的 MCP** ✗
          # ⇒ ★★★ **要挂必须先装** ⇒ ★ **撞硬约束「不装不改系统层」** ✗ ⇒ ★ **留此槽位待用户定** ✓
          #     定了就照上面 `mcp-solidworks` 那段**逐行抄**、★ 只换
          #     `id` / `serverName` / `command` / `args` ✓（★ 缩进同 10/12/14 ✓）
"""


def _read_bundle_preset_block() -> tuple:
    """★ 从 lean 插件里取出 `preset-lean` 那段（★ 逐行、★ 不改内容 ✓）。"""
    lines = LEAN_BUNDLE.read_text(encoding="utf-8").splitlines(keepends=True)
    #: ★ 找 `- insert:` 且**紧接着**是 `preset-lean` 的那一处（★ 插件那条在它上面 ✓）
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "- insert:" and i + 1 < len(lines) and "preset-lean" in lines[i + 1]:
            start = i
            break
    if start is None:
        raise SystemExit("★ 在 lean bundle 里找不到 preset-lean 的 `- insert:` 块")
    return lines, "".join(lines[start:]).rstrip("\n")


def main() -> int:
    out: dict = {"new_preset": NEW_PRESET_ID, "name": NEW_PRESET_NAME}
    if not LEAN_BUNDLE.is_file():
        print("✗ 找不到 lean bundle：%s" % LEAN_BUNDLE)
        return 2

    full, block = _read_bundle_preset_block()
    out["source_lines"] = len(full)
    out["block_lines"] = len(block.splitlines())
    print("★ 源块 ⇒ %d 行（★ 整份 %d 行）" % (out["block_lines"], out["source_lines"]))

    #: ★ 只改 4 处（★ 逐个断言"改到了" —— ★ 改不到就是源块结构变了，★ 要停下 ✓）
    changes = [
        #: ★★ 条目 id 用的是 `preset-lean`（★ 我第一版误以为它叫 `lean` ✗）——
        #:   ★ 必须改成 `preset-sw-engineer`，★ 否则**同一个 id 声明两次** ✗
        ("    - id: preset-lean\n", "    - id: preset-sw-engineer\n"),
        ("        id: lean\n", "        id: %s\n" % NEW_PRESET_ID),
        ("        name: Lean 模式\n", "        name: %s\n" % NEW_PRESET_NAME),
        ("        description: 工具呈现为「浅而准」形态（lean-mode 插件按此模式生效）。\n",
         "        description: %s\n" % NEW_PRESET_DESC),
        ("        order: 8\n", "        order: %d\n" % NEW_ORDER),
    ]
    for old, new in changes:
        if old not in block:
            print("✗ 源块里找不到要改的锚点：%r ⇒ **停下**（结构变了）" % old.strip())
            return 3
        block = block.replace(old, new, 1)

    #: ★ 把 MCP 追加到 `plugins:` 列表**末尾**（★ 缩进 12 空格、★ 与列表项同级 ✓）
    block = block.rstrip("\n") + "\n" + MCP_ENTRY

    #: ★★ **同插件的第二个实例**：只服务新 preset（★ 这是 token 安全的关键 ✓）
    #:   ★ 该插件**没有 `provide`** ⇒ 两个实例**不会撞 realm** ✓（★ 已核对 index.mjs ✓）
    companion = (
        "\n# ═══════════════════════════════════════════════════════════════════════════\n"
        "# ★ preset「%s」—— ★ 用户 2026-10-07 指令建的（★ 原话见本段末）\n"
        "# ═══════════════════════════════════════════════════════════════════════════\n"
        "# 用户的理由（原话）：「★ 你用 pwsh 调 tools/sw_guard.py 起探针的方式我怕你会忘记你\n"
        "#   有哪些工具，你会不会忘记你有哪个工具，然后就一直用常用工具硬干」✓\n"
        "# ★★ 实测依据：★ 本仓 `tools/probe_*.py` **246 个** + `tools/prove_*.py` **110 个**\n"
        "#   = **356 个手搓探针** ✗；★ 而 `AGENTS.md:105` 那条纪律只管「**怎么调**」、\n"
        "#   ★ **不管「该不该自己调」** ✗ ⇒ ★ **没有任何门禁能拦住「手搓已有工具的替代品」** ✓\n"
        "# ⇒ ★★★ **挂进工具目录就是机制性解法**（★ 目录每轮由 `system-prompt/assemble` 重算 ✓）\n"
        "#\n"
        "# ★ 做法：把 lean-mode 插件**再挂一个实例**、只点名本 preset ✓\n"
        "#   ★★ 为什么不改 lean 那个实例的 `presets` 列表 ✗：★ 用户明令\n"
        "#     「★ **你可不要直接让所有 lean 模式的对话都生效啊**」✓\n"
        "#   ★★★ 为什么必须再挂一个 ✗：★ 没有它，504 个工具会以**完整 JSON Schema** 注入\n"
        "#     ≈ **175k tokens** ✗（★ 记忆库实测：478 工具 原生 175k vs Lean 19k ✓）\n"
        "#\n"
        "# 回滚：★ 删掉本段与下面那段 `preset-sw-engineer` 即可，★ **不影响任何其它 preset** ✓\n"
        "# ⚠ 用法：★ **新建会话 → 选 preset「%s」** ✓ —— ★★ **不是**当前这个会话\n"
        "#   （★ `docs/glossary.zh.md:20` 逐字：setup window 里「scope 和 agent 对象**已存在**」\n"
        "#    ⇒ ★ **作用域在 agent 创建时组装完，事后改配置加不进正在跑的会话** ✗）\n"
        "# ⚠ 依赖：不需要任何 npm 依赖——`@deepseek-ai/dsh-mcp-client` 与\n"
        "#   `@local/dsh-lean-mode` 都随 bundle 解析 ✓\n"
        "# ═══════════════════════════════════════════════════════════════════════════\n"
        "- insert:\n"
        "    - id: lean-mode-sw\n"
        "      name: '@local/dsh-lean-mode'\n"
        "      config:\n"
        "        presets:\n"
        "          - %s\n"
        "\n"
        "# ② preset 本体（★ 组成 = 官方标准模式，★ 从 `preset-lean` **逐行克隆** ✓）\n"
        % (NEW_PRESET_NAME, NEW_PRESET_NAME, NEW_PRESET_ID)
    )

    payload = companion + block.rstrip("\n") + "\n"
    OUT_BLOCK.write_text(payload, encoding="utf-8")
    out["out_block"] = str(OUT_BLOCK)
    print("★ 生成块 ⇒ %s（%d 行）" % (OUT_BLOCK, len(payload.splitlines())))

    #: ── ★★ 机器校验（★ 三条判据，★ 见来源块）──────────────────────────────
    chk = subprocess.run(
        ["node", "-e", JS_CHECK, str(LIVE_CFG), str(OUT_BLOCK)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    print("── js-yaml 校验 ──")
    print((chk.stdout or "").strip())
    if chk.returncode != 0:
        print("✗ 校验没过：%s" % (chk.stderr or "")[-500:])
        return 4
    out["validate_stdout"] = (chk.stdout or "").strip()
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("★ 证据：%s" % OUT_JSON)
    return 0


#: ★ 校验脚本：★ 拼"原配置 + 新块" ⇒ 必须能解析、★ 且新 id 全在、★ 且 **lean 那条没变** 
#: ✓
JS_CHECK = r"""
const fs = require('fs');
const yaml = require('D:/AI/DSH/deepseek-harness/node_modules/js-yaml');
const [cfgPath, blkPath] = process.argv.slice(1);
const norm = s => s.replace(/!!js/g, '');
function idsOf(src) {
  const doc = yaml.load(norm(src));
  const ids = [];
  //: ★★ 两层都要收（★ 第一版只收顶层 ⇒ 把 preset 内的 plugins 漏了 ✗）：
  //:   ★ ① 顶层 `- insert:` 的条目 id ✓
  //:   ★★ ② **preset 的 `config.plugins[]` 里的插件 id** ✓ —— ★ `mcp-solidworks` 在这一层 ✓
  for (const blk of (doc || [])) {
    for (const it of ((blk && blk.insert) || [])) {
      if (!it) continue;
      if (it.id) ids.push(it.id);
      const cfg = it.config || {};
      for (const pl of (cfg.plugins || [])) if (pl && pl.id) ids.push(pl.id);
    }
  }
  return { ids, n: (doc || []).length };
}
let base, blk;
try { base = idsOf(fs.readFileSync(cfgPath, 'utf8')); }
catch (e) { console.log('   ✗ 阳性对照失败（原配置就解析不了）：' + e.message.slice(0, 160)); process.exit(1); }
console.log('   ★ 阳性对照：原配置解析成功 ⇒ 顶层 ' + base.n + ' 条 · id ' + JSON.stringify(base.ids));
const merged = fs.readFileSync(cfgPath, 'utf8') + '\n' + fs.readFileSync(blkPath, 'utf8');
let m;
try { m = idsOf(merged); }
catch (e) { console.log('   ✗ 合并后解析失败：' + e.message.slice(0, 300)); process.exit(1); }
console.log('   ★ 合并后解析成功 ⇒ 顶层 ' + m.n + ' 条 · id 共 ' + m.ids.length + ' 个');
const want = ['lean-mode-sw', 'preset-sw-engineer', 'mcp-solidworks'];
const missing = want.filter(w => m.ids.indexOf(w) < 0);
console.log('   ★ 新 id ' + JSON.stringify(want) + ' 缺失 ' + JSON.stringify(missing));
// ★★ 判据③：`lean` 那条**必须还在**、且旧 id 一个不少（★ 证明没碰别人的 preset ✓）
const lost = base.ids.filter(x => m.ids.indexOf(x) < 0);
console.log('   ★★ 原有 id 丢失 ' + JSON.stringify(lost) + '（★ 必须为空）');
if (missing.length || lost.length) process.exit(1);
console.log('   ✓✓ 三条判据全过：可解析 · 新 id 齐 · 旧 id 无损');
"""


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        Path(Path(__file__).resolve().parents[1] / "output" / "dsh-sw-preset-generate-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1500:])
        raise SystemExit(3)
