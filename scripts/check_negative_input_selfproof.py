r"""@brief 审计：`tools/` 下探针里「**负例输入**」是否**自证**。

## 为什么（2026-10-01 轮 85，Spec Kit `009`）
轮 84 撞见一个**假用例**：`probe_skip_semantics.py` 里用一条正则把「逐模块表」删掉来造"坏文档"，
⚠ **那条正则根本没匹配上** ⇒ 产出的"坏文档"**仍带完整的表** ⇒ 门禁照常 `[PASS]`，
**而我把它当成了"修好了"的证据**。

★ **教训：假用例比没有用例更糟** —— 它给出一份**看起来验过的**证据。

## 本审计判的**一类**（不是全部）
> **凡「用变换（`re.sub` / `replace`）造出来的负例输入」，必须自证变换确实生效**
> —— 即：比对变换前后**不相等**，或**打印前后差异/字节数**。

那正是轮 84 那个 bug 的**可直接机器判**的特征：**变换没生效 ⇒ "坏输入" 等于真输入 ⇒ 用例空转**。

## ⚠ 本审计**抓不到**的（如实声明，不夸大覆盖面）
* **类型 2 · 坏的理由不对**：输入确实"坏"了，但**不是**该用例声称的那一点
  （轮 83 的 DFM 用例就是这类：我造的文档缺的是表，却声称在测"篡改 sha256"）；
* **类型 3 · 负例与正例结果相同**：用例跑了，但**没区分出任何东西**；
* **类型 4 · 断言打在了恒定字段上**。
⇒ 这三类需要**语义**判断，本审计**明确不假装**能判 —— 只把类型 1 钉住。

# ── 来源 ──
# 仓库:   本项目自身（只读审计）
# 文件:   scripts/check_negative_input_selfproof.py
# 定位:   **硬门禁** —— 把「假用例」中**可机器判的那一类**（变换没生效）钉住。
# ⚠ 它扫的是 `tools/` 下的探针（不是本目录）—— 因为假用例的危害正是发生在**探针**里。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.stdout.reconfigure(encoding="utf-8")

#: 「负例输入」的文件名特征
NEG_NAME = re.compile(r"(bad|broken|tamper|invalid|wrong|corrupt|no_?table|missing)", re.I)
#: 变换调用
TRANSFORM = re.compile(r"\bre\.sub\(|\.replace\(|\bre\.subn\(")
#: 「自证」的证据：比对不等 / 打印字节数或长度 / 打印前后
SELF_PROOF = re.compile(
    r"!=\s*\w+|\w+\s*!=\s*\w+"          # 比对不等
    r"|len\([^)]*\)\s*-\s*len\("        # 前后长度差
    r"|->\s*%d|%d\s*->\s*%d"            # 「A -> B 字节」
    r"|assert\s+.*!="                   # 断言
)

WINDOW = 10          # 在「变换」前后多少行内找自证

#: ★★ **显式豁免**：必须是**带非空理由**的标记 `negproof-exempt: <理由>` ✓
#: 起因（2026-10-07 接手轮实测）：本道闸对 `tools/verify_union_349.py:112` 报了**假阳性*
#: * ✗ ——
#:   那一句 `d = base / name.replace("：", "_")` ★ **不是造负例输入**，
#:   ★ 而是把负例**目录名**里的全角「：」换成「_」；★ 真正的坏输入由**下一行**
#:   `write_all(d, **kw)` 的实参（`skip` / `extra` / `broken`）造出来 ✓ ——
#: ★ 而它落在 `NEG_NAME` 的 10 行窗口里（窗口里恰好有 `"broken": True`）⇒ ★ 被判「变换没
#: 有自证」✗
#: ★★ 处置**不是**删掉本道闸（它抓的是轮 84 那件真事），★ 而是照本仓既有模式给一个**可核
#: 的豁免**：
#:   ★ 同型先例 —— `preference-guard:` 标记（`check_user_preference_writes`）·
#:   `MANUAL_MAP` 的「**没有依据的不许进来**」✓ ⇒ ★ **理由为空 ⇒ 不生效** ✓
EXEMPT = re.compile(r"negproof-exempt:\s*(\S[^\n]*)")
#: ⚠ 豁免标记必须**紧贴那一句变换**：★ 只在**紧邻变换的那一段连续注释块**里找 ✓
#: ★ 为什么是「连续注释块」而不是「上面 N 行」：★ 理由常常要写**好几行**（本项目就这样）
#: ，
#:     而固定行窗口要么太窄（漏掉多行理由）要么太宽（**一处标记豁免掉窗口里好几处变换**）✗
#:   ⇒ ★ 判据的范围必须贴合它要判的**那一个**组织单元（**已知事实 51**）✓
def _comment_block_above(lines: list, i: int) -> str:
    """⇒ 紧邻第 `i` 行**上面**的那一段连续注释（★ 遇到第一行非注释就停）✓"""
    block = []
    j = i - 1
    while j >= 0 and lines[j].lstrip().startswith("#"):
        block.append(lines[j])
        j -= 1
    return "\n".join(reversed(block))


def scan(path: Path) -> list:
    """⇒ `[(行号, 说明, 是否自证, 豁免理由或 None)]`。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for i, line in enumerate(lines):
        if not TRANSFORM.search(line):
            continue
        # 这个变换是否服务于一个「负例输入」？
        window = lines[max(0, i - 4): i + WINDOW]
        blob = "\n".join(window)
        if not NEG_NAME.search(blob):
            continue
        proved = bool(SELF_PROOF.search(blob))
        m = EXEMPT.search(_comment_block_above(lines, i))
        out.append((i + 1, line.strip()[:74], proved, m.group(1).strip() if m else None))
    return out


def main() -> int:
    files = sorted(TOOLS.glob("*.py"))
    total = bad = exempt = 0
    #: ⚑ **首行必须自带分母**（轮 192）：读者（与人写的 review 脚本）**只看首行** ——
    #:   本项目实测过一次：因为只看首行，我把"分母在第二行"误判成"这道门禁没分母"。
    print("负例输入自证审计 · 扫 %s（**%d** 个 .py）" % (TOOLS, len(files)))
    print("  判据：凡「用变换造负例输入」的地方，必须在前后 %d 行内**自证变换生效**" % WINDOW)
    print("  （比对不等 / 打印前后字节数 / 断言）")
    print("  ★ 另：紧贴变换的**连续注释块**里写 `negproof-exempt: <理由>` 可**显式豁免**"
          "（★ 理由为空 ⇒ 不生效）")
    print()
    for f in files:
        hits = scan(f)
        if not hits:
            continue
        print("── %s" % f.name)
        for ln, txt, proved, why in hits:
            total += 1
            if proved:
                mark = "自证✓"
            elif why:
                mark, exempt = "豁免✓", exempt + 1
            else:
                mark, bad = "**未自证**", bad + 1
            print("   L%-4d %-76s [%s]" % (ln, txt, mark))
            if why:
                print("        ↳ 豁免理由：%s" % why)
    print()
    if bad:
        print("[FAIL] **%d/%d** 处「造负例输入」的变换**没有自证**：" % (bad, total))
        print("  ⚠ 变换可能**根本没生效** ⇒ 那个负例输入**等于真输入** ⇒ **用例空转却显示通过**")
        print("     （2026-10-01 轮 84 就是这么撞见的：删表的正则没匹配上）")
        print("  修法：在变换后加一句**自证** ——")
        print("        `assert new != old` 或 `print('坏输入: %d -> %d 字节' % (len(old), len(new)))`")
        print("  ★ 或者：若该变换**根本不参与造负例输入** ⇒ 在它（或上面 2 行内）写一句")
        print("        `# negproof-exempt: <为什么它不是造负例输入>`（★ **理由不能为空**）")
        return 1
    print("[PASS] %d 处「造负例输入」的变换**全部自证**（比对/字节数/断言）"
          "%s" % (total, "，另 %d 处走带理由的显式豁免" % exempt if exempt else ""))
    print("  ⚠ **覆盖面声明**：本审计只判「**变换没生效**」这一类（类型 1）；")
    print("     类型 2/3/4（坏的理由不对 / 负例与正例同结果 / 断言打在恒定字段）**需要语义判断，未判**。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
