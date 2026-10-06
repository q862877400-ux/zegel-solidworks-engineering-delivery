# 规格 210 · 指纹标定记录（B2 的收口产物）

> ★ 由 `tools/gen_fingerprint_calibration.py` 从**真机标定结果**生成 —— **不要手改**。
> ★★ 验收判据（规格 210 · B2）：**每一类状态都有灵敏度证据，或明写「这类写入当前不可见」** ✓

## 第 0 格 · 读数只读（★ 先验「量具本身不改状态」）

★ 连读三次、**只比第 2 与第 3 次**（★ 第 1 次当「加热」，★ 因为刚建好的零件还在自己稳）：
**完全相等 ✓ —— 读数**没有副作用****

★ 读不到的类：display

## 逐类结论

**`bodies`** ⇒ `sensitive`

· 结论：★ **有灵敏度证据**（写操作动了这一类）
· 写操作：`solidworks_extrude_boss`（返回体说成功：True）
· 读数：前 `0` ⇒ 后 `1`

**`config`** ⇒ `sensitive`

· 结论：★ **有灵敏度证据**（写操作动了这一类）
· 写操作：`solidworks_config_create`（返回体说成功：True）
· 读数：前 `'默认'` ⇒ 后 `'MCP_CALIB_1791292909615310300'`

**`dirty`** ⇒ `sensitive`

· 结论：★ **有灵敏度证据**（写操作动了这一类）
· 写操作：`solidworks_config_create`（返回体说成功：True）
· 读数：前 `False` ⇒ 后 `True`

**`display`** ⇒ `unreadable`

· 结论：★★ **读数本身读不到**（★ 与「不可见」**不是一回事** —— 读数要修）
· 写操作：`solidworks_set_standard_view`（返回体说成功：True）
· 读数：前 `None` ⇒ 后 `None`

**`edit_mode`** ⇒ `sensitive`

· 结论：★ **有灵敏度证据**（写操作动了这一类）
· 写操作：`solidworks_sketch_start`（返回体说成功：True）
· 读数：前 `'none'` ⇒ 后 `'sketch:草图1'`

**`faces`** ⇒ `sensitive`

· 结论：★ **有灵敏度证据**（写操作动了这一类）
· 写操作：`solidworks_extrude_boss`（返回体说成功：True）
· 读数：前 `0` ⇒ 后 `6`

**`features`** ⇒ `sensitive`

· 结论：★ **有灵敏度证据**（写操作动了这一类）
· 写操作：`solidworks_extrude_boss`（返回体说成功：True）
· 读数：前 `18` ⇒ 后 `20`

**`rebuild`** ⇒ `not_detected`

· 结论：★★ **这一类在本形状下不可见**（写操作**成功**而读数没动）
· 写操作：`solidworks_session_rebuild`（返回体说成功：True）
· 读数：前 `False` ⇒ 后 `False`

**`selection`** ⇒ `not_detected`

· 结论：★★ **这一类在本形状下不可见**（写操作**成功**而读数没动）
· 写操作：`solidworks_clear_selection`（返回体说成功：True）
· 读数：前 `0` ⇒ 后 `0`

## 三档统计

not_detected **2**★ 「 + 」 · sensitive **6**★ 「 + 」 · unreadable **1**

★★ **收口判据的满足情况**：★ 有灵敏度证据的 **6** 类；★ 明确记「不可见 / 读数待修 / 没试」的 **3** 类；★ 两者相加 = **9**，★ 与九类相等则**每一类都有结论** ✓

## ⚠ 本记录的限度（★ 不许当成「九类全都敏感」）

· ★ **`not_detected` 不等于「读数瞎」** —— ★ 真机查明它多半是「**写操作没有真的改变任何东西**」（★ 前置已满足 / 参数被复用 / 缺前置）✓
· ★ **`unreadable` 与 `not_detected` 是两件事**（★ 前者是**读数**的问题，★ 后者是**这一类不可见**）✓
· ★ 标定**每一类各用一个新零件** —— ★ 同一文档上顺序标定会**互相污染**（★ 真机踩过：前面的类把文档弄脏/用掉草图 ⇒ 后面的类「没得变了」）✓

