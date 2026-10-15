# Tasks — 换路由第 1 批（KFactor / MaterialIdName）

**Feature**: `specs/261-routing-batch1-adapt-args/`
**日期**: 2026-10-10

## T-001 读后继官方签名
- **状态**：☑ 完成（★ 3 个后继的形参都拿到了）。

## T-002 改 2 处 + 复核
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -c 'get_com_member(definition, "KFactor")\|get_com_member(model, "MaterialIdName")' scripts/sw_sheet_metal.py scripts/sw_simulation.py
  ```
- **期望**：两个都是 **0**。 **状态**：☑ 完成。

## T-003 真机复验（★ 走护栏）
- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --timeout 240 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe261_verify.py
  ```
- **期望**：新 `'AISI 1020'` · 旧 `'solidworks materials|AISI 1020|2'` ⇒ ★ **不等价**。
- **状态**：☑ 完成。

## T-004 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_routing_batch1_adapt_args.py -q 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-005 ★★ 生成器链 + 门禁（★ 改了 `scripts/`）
- **状态**：☑ 生成器链 7 步 OK；☐ 门禁见 `acceptance.md`。

## T-006 夹具零件未被改
- **验收**：
  ```bash
  cd "D:/AI/SW" && ls -l --time-style="+%m-%d %H:%M" "output/fixtures/刀柄_Holder.sldprt"
  ```
- **期望**：mtime 仍是 **`09-27 11:37`**。 **状态**：☑ 完成。

## T-007 回写四处状态
- **状态**：☐
