# 026 · Plan

## 步骤
1. 查 75 条「查不到」的成员到底属于哪个程序集
   ⇒ 搜遍 `api\redist` 下所有 DLL ⇒ 命中 **cosworks.dll**
2. 发现 `_raw/reflect/enum_cosworks.txt` **已有**该程序集的枚举转储
3. ⇒ **不新建转储**（不重造），改门禁读多份
4. 加测试：`sws*` 能查到 + 合并优先级
5. ★ 改 `gate-classification.json` 时踩了 **JSON 转义**（Windows 路径）⇒ 修正
6. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 以为"官方没有"就到此为止 | ★ 先确认是**哪个程序集**，再找该程序集的转储 |
| 自己再造一份转储 | **不造** —— 已有 `enum_cosworks.txt` |
| 往 JSON 里写 Windows 路径 | 用正斜杠（本轮踩过）|
