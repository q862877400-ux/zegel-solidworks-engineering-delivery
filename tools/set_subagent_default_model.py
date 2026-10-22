"""★ 把子代理的默认模型改成 bunny（写活配置 `profiles/web/cordis.patch.yml`，先备份）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   DSH 用户配置（不是 SW 仓库）
# 文件:   C:\Users\Zegel\.dsh\profiles\web\cordis.patch.yml
# 定位:   ★ 业主指令：「把默认模型直接改掉」（★ 起因：我两次用 `workflow` 的 `agent()`
# 派活**没传
#           `model`** ⇒ **默认继承我自己的模型（DeepSeek）** ⇒ 烧掉当天约 50% 花费）✓✗
#         ★★ 机制（**逐字读出来的，不是猜的**）：
#           · `packages/core/agent/src/runtime-types.ts` 的 `AgentOptions` =
#             `{ provider?, model?, reasoningEffort?, maxTokens? }` ✓
# · `packages/subagent/tool-subagent/src/index.ts:73-76` 的 `Config.agentOptions` 注释逐
# 字：
#             「Agent options applied to **every child**; omitted fields use child-loop defaults.」✓
# · `packages/subagent/subagent-spawn-in-process/src/index.ts:31` 的 provider 配置**只有
# **
#             `providerName` ⇒ ★ **provider 层没有默认模型可改** ✓
# · `packages/workflow/workflow-ptc/src/host.ts:205-210` ⇒ workflow 的子代理**只在脚本显
# 式
#             传 provider/model 时才带 `agentOptions`**，否则**继承父级**；而 `workflow-ptc` 的
#             `Config`（`src/index.ts:32-36`）**只有 `maxConcurrentAgents`** ⇒ ★ **workflow 这层没有
#             配置默认值可改**（★ 本条如实记下，不假装改到了）✓
#         ★★★ 所以本脚本只改**能改且是业主说的那个**：`tool-subagent` 的 `agentOptions` ⇒ 让
#           `subagent` 的每个子代理**默认走 bunny**（opencode-zen / space-bunny-free）✓
# 官方依据: 上述 harness 源码行（★ 本机 checkout，非官方 API 文档）
# 许可:   本机配置，无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

CFG = Path(r"C:\Users\Zegel\.dsh\profiles\web\cordis.patch.yml")
BUNNY = {"provider": "opencode-zen", "model": "space-bunny-free"}


def main() -> int:
    if not CFG.is_file():
        print("★ 找不到活配置：%s" % CFG)
        return 1
    raw = CFG.read_text(encoding="utf-8")
    lines = raw.splitlines(keepends=True)

    #: ★ 备份（沿用该目录既有的命名惯例 `*.bak-<ts>-before-<原因>`）
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = CFG.with_name(CFG.name + ".bak-%s-before-subagent-default-model" % ts)
    shutil.copy2(CFG, bak)
    print("★ 已备份 → %s" % bak.name)

    out: list[str] = []
    inserted = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        #: 命中 `- id: tool-subagent`（★ 只改非 fork 那个：`toolName: subagent`）
        if re.match(r"^\s*- id: tool-subagent\s*$", line):
            #: 往后找这个块的 `name:` / `toolName:` / `modelSelectionSettings:` 与缩进
            j = i + 1
            name = toolname = ""
            indent = None
            while j < len(lines) and j < i + 14:
                out.append(lines[j])
                s = lines[j]
                if re.search(r"name:\s*'@deepseek-ai/dsh-tool-subagent'\s*$", s):
                    name = "subagent"
                m = re.search(r"^(\s*)toolName:\s*(\S+)", s)
                if m:
                    toolname = m.group(2)
                m2 = re.search(r"^(\s*)provider:\s*", s)
                if m2 and indent is None:
                    indent = m2.group(1)  #: ★ 用同块 `provider:` 的缩进
                if re.search(r"^\s*modelSelectionSettings:", s) and indent is not None:
                    #: ★ 紧跟在 modelSelectionSettings 之后插入 agentOptions
                    out.append("%sagentOptions:\n" % indent)
                    out.append("%s  provider: %s\n" % (indent, BUNNY["provider"]))
                    out.append("%s  model: %s\n" % (indent, BUNNY["model"]))
                    inserted += 1
                    j += 1
                    break
                j += 1
            i = j
            continue
        i += 1

    if inserted == 0:
        print("★ 一处也没插进去 ⇒ **不改**（避免半改状态）")
        return 2

    CFG.write_text("".join(out), encoding="utf-8")
    print("★ 已插入 agentOptions：**%d** 处" % inserted)

    #: ★ 回读确认（铁律：判据是文件，不是"我以为改了"）
    back = CFG.read_text(encoding="utf-8").splitlines()
    for k, s in enumerate(back, 1):
        if re.match(r"^\s*- id: tool-subagent\s*$", s):
            print("   L%d 起：" % k)
            for t in back[k - 1 : k + 10]:
                print("      " + t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
