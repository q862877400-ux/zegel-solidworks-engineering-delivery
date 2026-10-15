"""★ 一次性：把 B2 的进展与真机发现写进 goal-bar 与 tasks。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")

t = ROOT / "specs/210-declarative-effects/tasks.md"
lines = t.read_text(encoding="utf-8").splitlines()
out, done, i = [], False, 0
while i < len(lines):
    if lines[i].startswith("- [ ] **B2-1**"):
        out += [
            "- [x] **B2-1** 定义**状态指纹**（**已交付** `scripts/sw_fingerprint.py`）：九类都有读数、",
            "      每类**标明官方成员**（铁律 4）· 拿不到 ⇒ **记 `None` + 原因**（★ 不假装读到）·",
            "      ★★ **失效判据**：九类全 `None` ⇒ 标 `usable=False`（★ 别当成「什么都没变」）✓",
            "      ⚠ **待补**：`bodies`/`faces` 的 `GetBodies2` **要两个实参**（BodyType/BVisibleOnly）——",
            "      ★ 官方签名已查到，★ 下一轮按签名补 ✓",
            "- [~] **B2-2** 灵敏度测试（★ **半程**）：`tools/probe_fingerprint_sensitivity.py` 已交付，",
            "      ★★ **真机已验**：`selection` 与 `edit_mode` **= sensitive** ✓；",
            "      ★ 其余记 **`untested`**（★ 不许说成「看不见」）—— ★ 写操作要**按 ToolSpec 契约**接（下一轮）✓",
            "- [x] **第 0 格（读数只读）**：★ 连读两次、中间什么都不做 ⇒ ★ **真机首轮**「完全相等」✓",
            "      ★★ **但它单独不足以证明量具好** —— ★ 首轮九类**全 None 时它照样通过** ✗",
            "      ⇒ ★ 已补 `usable` 判据把它堵住 ✓；★ 且发现「文档还在自行稳定」会让两次读数不等 ⇒",
            "      ★ 下一轮改成**连读三次、比第 2 与第 3 次**（★ 先让它稳定下来）✓",
        ]
        done = True
        i += 1
        while i < len(lines) and not lines[i].startswith("- [ ] "):
            i += 1
        continue
    out.append(lines[i]); i += 1
assert done, 「没找到 B2-1 那一格」
t.write_text("\n".join(out) + "\n", encoding="utf-8")
print(「tasks B2 已更新:」, done)

g = ROOT / "specs/210-declarative-effects/goal-bar.md"
s = g.read_text(encoding="utf-8")
s = s.replace("阶段：★★ **B5 全部收口**（B5-1..B5-5）· **B1 收口**；下一步 = **B2 指纹与灵敏度校准**",
              "阶段：**B2 半程**（指纹模块已交付 · 两类已验 sensitive）· B1/B5 已收口；"
              "下一步 = **修三个真机查出的缺陷 + 补写操作契约**")

NEW = [
    "## 下一个动作（只写一条，免得没人知道该恢复哪个）",
    "",
    "★★★ **真机查出三个真问题**（★ 这一轮最值钱的就是它们 —— ★ **都不是读代码能发现的**）：",
    "",
    "**① `get_com_member` 的 `default=` 被当成了位置实参** ⇒ ★★ **九类读数全 None** ✗",
    "   ★ 本仓的签名是 `get_com_member(obj, attr, *args)`，**没有 `default=`** ⇒",
    "   ★ 传 `default=None` = **用 `None` 去调那个成员** ⇒ 绝大多数成员当场抛异常 ✓",
    "   ★★ 而**「两次读数相等」照样通过**（两次都一样地全 None）⇒ ★ 光靠第 0 格发现不了 ✗",
    "   ⇒ ★ 已修；★ 并加 `usable` 判据：**九类全 None ⇒ 标「指纹失效」** ✓",
    "",
    "**② ★★ B5 的门禁曾是「瞎着放行」**（★ 比 ①更严重，因为它是**安全**件）：",
    "   ★ 现场：SolidWorks **明明开着文档**，而 COM 路的 `GetDocuments` 返回**空** ⇒",
    "   ★ 裁决读出 `count=None · 文档数=0`，★ **照样放行** ✗ —— ★ 「存在但没人用的守卫」同类 ✓",
    "   ⇒ ★ 已修：★ **降级到标题路**并**记明 `path_used`** + 记下降级过的路 ✓",
    "   ★（标题路**看得见**打开的文档 —— 真机上它报出过「1 个文档 · 未保存 1 个」✓）",
    "",
    「**③ ★ 而我随后的」过度纠正"又把它变成了路障**（★ 同一个坑这轮踩了两次）：",
    「   ★ 我先改成」读不出 ⇒ **拒绝**" ⇒ ★★ **会话干净时也拒绝** ⇒ 门禁**拒绝一切** ✗",
    "   ★ 与上一轮 `sandbox_before` 那次同族：★ **「保守」不等于「一律拒绝」** ✓",
    "   ⇒ ★ 已改成**降级**（既不瞎、也不堵）；★ 真机验证：会话干净 ⇒ 放行 · `ok: true` · 退出码 0 ✓",
    "   ★ 另加：★ **两次点名不一致 ⇒ 拒绝**（★ 真机现场就是 1 对 0）✓",
    "",
    "★ 顺带清场：★ 探针遗留的我方未保存文档已**循环关掉**（★ 只关**我方**的；",
    "  有非我方文档就**停手交人**）⇒ 会话已验证干净 ✓",
    "",
    「**下一批要做（B2 收口）**：」,
    "1. ★ 按**官方签名**补 `GetBodies2(BodyType, BVisibleOnly)` ⇒ 修 `bodies`/`faces` 两个读数 ✓",
    "2. ★ 第 0 格改成**连读三次、比第 2 与第 3 次**（★ 让文档先稳定）✓",
    "3. ★ 写操作**按 ToolSpec 契约**接（★ 现在用的是能力层公开函数，形状不对 ⇒ 抛 TypeError）⇒",
    "   把 `features`/`bodies`/`faces`/`dirty`/`config` 从 `untested` 推到**有证据**或**明写不可见** ✓",
    "4. ★ **查清 `GetDocuments` 为什么返回空**（★ 这是 B5 门禁能否用 COM 路的前提）✓",
    "",
]
lines_g, i2, hit = s.splitlines(), 0, False
out2 = []
while i2 < len(lines_g):
    if lines_g[i2].startswith(「## 下一个动作」):
        hit = True
        out2 += NEW
        i2 += 1
        while i2 < len(lines_g) and not lines_g[i2].startswith("## "):
            i2 += 1
        continue
    out2.append(lines_g[i2]); i2 += 1
assert hit, 「没找到「下一个动作」段」
s2 = "\n".join(out2) + "\n"
s2 = s2.replace("- **B2 指纹与灵敏度**：⚪ 未开始（★ 下一步）",
                "- **B2 指纹与灵敏度**：🟡 **半程**（指纹模块已交付 · `selection`/`edit_mode` 已验 sensitive；"
                "★ 其余 `untested`，★ 见「下一个动作」的四条）")
g.write_text(s2, encoding="utf-8")
print(「goal-bar 已更新:」, 「真机查出三个真问题」 in s2)
