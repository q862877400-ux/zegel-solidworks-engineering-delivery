# 否定裁决：统一反而更差

配套 `SKILL.md`。这是整套方法里**最反直觉、也最贵**的一条经验，两条都用硬数字否决过。

## 核心命题

> **验证能力 > 去重收益。**

有些「重复实现」不是债，是**门禁的抓手**。本仓那几道 dispatch 门禁（`check_dispatch_byref_guard` / `check_dispatch_entry_guard` / `check_dispatch_arg_*` / `check_dispatch_forward_*`）的原理是：识别「分发口」——一个把**成员名字面量**转成实际成员的本地函数 —— 然后逐条核验「传进去的成员名在官方 API 源里查得到」。

★ 一旦把两处本地 `def` 换成一处导入，调用点虽然逐字不变，但门禁**不再把它们识别成分发口** ⇒ 那些调用点从「已核验」变成「看不见」。数字掉下去，代码看起来一样干净。

## 裁决一：`_optional_com_member` / `_safe_com_member` / `_safe_member`

- 形态：同一段逻辑（`if obj is None: return default` + `try/except` 回 default）**三个名字三份逐字相同**，分别在 `scripts/sw_delivery.py`、`scripts/sw_part.py`、`subskills/.../drawing_workflow.py`。
- 做法：把 `sw_part` 与 `sw_delivery` 的本地 `def` 改成导入别名。
- **实测结果**：
  - `check_dispatch_byref_guard` 已核调用点 **323 → 302（−21）**
  - `check_dispatch_entry_guard` 从全 PASS 变 **5 处违规**
- 判定：**不统一，回滚。** 回滚后 byref 回到 323、entry 全 PASS。
- 注：`subskills/` 不在门禁扫描根里，所以组串只出现两个名字，第三份是同族。

## 裁决二：`_checked` ×4 → 只取两份

- 形态：`sw_pdm` / `sw_simulation_results` 各一份 **11 行逐字相同**（签名表靠 `table` 参数传），另两份是参数化过的变体。
- 做法：本地 `def` 换导入别名，**调用点零改动**。
- **实测结果**（四项棘轮同时破）：
  - 可解析调用点 **327 → 317（−10）**
  - 可解析分发口 **18 → 16**
  - 分发口 **37 → 36**
  - 不可见 **84 → 83**
- 判定：**不统一，回滚。**

## 复验命令与必须守住的计数

改任何 dispatch 类辅助函数（含「看起来只是挪个位置」）之前先记下，改完复验：

| 门禁 | 必须守住 |
|---|---|
| `check_dispatch_byref_guard` | 可解析分发口 21 · **已核调用点 323** |
| `check_dispatch_entry_guard` | 分发口 37 · 已声明 37 · 不可见 84 · 可解析 18 |
| `check_dispatch_arg_*` | 45 / 41 / 131 |
| `check_dispatch_forward_*` | 8 / 4 / 12 |
| `check_dispatch_upstream_*` | 3 / 10 / 5 |
| `check_dispatch_blindspot*` | 371 |

★ **掉一个数就是回归**，不看代码是不是更短。

## 另两类「不能统一」的重复

### 同代码不同目标

`scripts/engineering/automation.py` 与 `jobs.py` 各有一个 `assert_no_com_imports`，函数体逐字相同。但它们各自 `Path(__file__).read_text()` 读**自己的源码**扫 COM 标记词 —— 语义是「这个模块自己不 import COM」。合并到一处后，两边都去查**那个共享模块** ⇒ 两个自证都变成「永远通过」的假自证。

⇒ 重复是**真的**，统一会把它们变成**假的**。

### 生成模板的一部分

12 个 `sw_api_*.py` 各有一份 `_require`，文件头逐字写着「官方 API 的完整抄录／逐条机械生成，不手抄、不折叠、不合并重载」。`_require` 是生成模板的一部分（每文件恰用 1 次）⇒ 手改会被下次重生成覆盖，且给「纯抄录」文件引入运行期依赖。

⇒ 要收敛，得改**生成器**，不是改产物。这是「统一目标定错了层」。

## 怎么写进基线

否定裁决**必须登记**，否则下一轮会重新「发现」同一组重复并再统一一次：

```json
{
  "functions": "_checked",
  "files": ["scripts/sw_pdm.py", "scripts/sw_simulation_results.py"],
  "verdict": "★ 判定【不统一】—— 保留两份",
  "reason": "…★ 实测数据 + 为什么会掉核验面（≥100 字）…",
  "evidence": "回滚后六道门禁逐个复验回到基线：byref 323 · entry 37/37 可解析 18/37 · …",
  "date": "2026-10-22"
}
```

三条硬要求：**有实测数字**、**有可复跑的 evidence**、**写清「为什么统一会更差」而不是「暂时不想动」**。

★ 「暂时不想动」是另一类，叫**暂缓**：不登记豁免、继续计入基线、另记一条「待裁决 + 理由」。两类不能混 —— 混了就等于用豁免掩盖工作量。
