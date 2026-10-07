# 规格 216 · ② AVI：**边界收窄了一整环**（★ 本轮实测）

> **探针**：`output/_t216_avi_probe.py`（★ `output/` 被 gitignore ⇒ 读数抄在这里）
> **跑法**：★ `python tools/sw_guard.py --timeout 900 -- python output/_t216_avi_probe.py`
> ⇒ ★ **9.8 s · 0 弹窗 · `aborted_for_llm: false`** ✓

## 一、★ 先订正**我自己**引错的前提

★ 我（在本规格的目标里）引的是台账 **第 4 版**那条：「边界已定位：`SaveToAVI` 需要
**`CosmosMotion` 系列算例**，而本机拿不到那种算例」。
★★ 而台账那条其实有**六版演进**、★ **最终版（轮 288/289）**的结论**是另一条** ——
**一条可修的链**：★「**组件插入时零件文件没保存好** ⇒ 组件未解析 ⇒ 面上没有几何 ⇒
**找不到圆柱面** ⇒ 马达建不出 ⇒ 没有动画 ⇒ 导出空文件」✓
⇒ ★★ **第 4 版与最终版说的不是同一件事**：★ 前者是"算例类型不可得"、★ 后者是"建件链断了"。
★ 只看其中一版就会误判 —— ★ 这正是「**一个探测的结果与从它推出的结论要分开记**」（★ 台账自己那条教训）✓

## 二、★★ 本轮实测：**最终版那条卡点已被解决**

★ 我按**文档写法**重建试件（★ 起因见 `recon/bd-declarative-selection.md` §五/六：
★ `sw_part.sketch()` 是**上下文管理器**、★ 且**本模块长度单位是毫米**；★ 而
`tools/verify_motion_avi_e2e.py` **既没有 `with`、又用了 `0.02`/`0.1` 这种数**）✓
```
with sw_part.sketch(part, "Front Plane") as sk:
    sw_part.sketch_circle(part, 0.0, 0.0, 20.0)     # ★ 毫米
sw_part.extrude_boss(part, sk, 40.0)
```

★ **逐环读数（★ 全 ok）**：

| 环 | ★ 读数 |
|---|---|
| `save_document(part)` | ★ **保存成功**（★ 轮 288 那条链正是在这里回的 `False`）✓ |
| `add_component` ×2（x=0 / x=0.06）| ★ 两个都加上 ✓ |
| `ensure_motion_type_library()` | ★ ok ✓ |
| `get_motion_study_manager(asm)` | ★ ok ✓ |
| `create_motion_study(type=2)` | ★ ok · ★ `StudyType` **回读 2** ✓ |
| ★★ `add_constant_speed_rotary_motor_by_cylinders(study, c1, c2, rpm=60)` | ★★ **ok · `motor_ok = True`** ⇒ ★★ **轮 288 的卡点（「找不到圆柱面 ⇒ 马达建不出」）不复现** ✓ |
| `calculate_and_play(study, play=False)` | ★ ok ✓ |
| `create_avi_parameter(mgr)` · `configure_avi_parameter(ap, FramePerSecond=10)` | ★ ok ✓ |
| `export_motion_study_avi(study, avi, ap)` | ★ ok（★ 而**返回值不算数**）|
| ★★ **判据**：文件存在且大小 > 0 | ★★ **`avi_exists = False` · `size_bytes = 0`** ⇒ ★ **唯一仍失败的**是这一步 ✗ |

## 三、★ 由此定下的**边界（★ 比原来锐利一整环）**

★ **两条路要分清**：
1. ★ **CosmosMotion 家族（`StudyType` = 4 / 8 / 16）** ⇒ ★ 本机**静默降级**（设了回读仍是 **2**），
   ★ 且 Motion 加载项 **4 个 ProgID 全 `None`** ⇒ ★ **不可得**（★ 这是**机器／许可边界**）✗
   ★ 依据：★ `tools/verify_motion_avi_e2e.py` L151-162 的**逐值实测矩阵**（轮 66）✓
2. ★★ **PhysicalSimulation(2)** ⇒ ★ **除最后一步外全通**（★ 含**马达建成**）✓
   ⇒ ★★ **唯一剩下的**是 `SaveToAVI` **没有写出文件** ✗

★ **候选下一步**（★ 台账既记过一部分）：★ `IAVIParameter` 的 `OutputType` / `StartTime` / `EndTime` /
`SaveEntireAnimation` · ★ 先 `Play` 再导 · ★ **先保存装配体** ——
★★ 而「有马达 + 挑对算例 + `ActivateMotionStudy` + 保存装配体 + 先 `Play` ⇒ **仍 `False`**」
★ **当时也试过** ⇒ ★★ 故本轮**只声明边界收窄**、★ **不声明已解决** ✓

## 四、★ 顺带产出：**建件写法**这条经验可以复用到别处

★ 「`sw_part.sketch()` 必须用 `with`」+「该模块单位是**毫米**」⇒
★ 本仓自己的 `tools/verify_motion_avi_e2e.py` **两样都没按** ⇒ ★ 它**现在仍会失败** ✗
★ **未改它**（★ 它是**证据脚本**、★ 且它"失败"这件事**本身是它要报的读数**）⇒
★ 建议：★ 修它之前先想清"它应当验的是**能力**还是**建件写法**" ✓
