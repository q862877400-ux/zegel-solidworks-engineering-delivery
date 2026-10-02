# 判据优先去开源项目里找


> 用户原话：「**当你需要判据的时候，先去开源项目里找，找不到再自己搓**」

**落到可执行的形态**（顺序不可颠倒）：
```
1. ★ **先找**：写任何真机探针 / 证据脚本**之前**，先查四家有没有现成的判据 ——
     Get-ChildItem C:\swprojects\andrewbartels1 -Recurse -Filter 'test_live_*.py'
   ★ 那是本机**最富的真机判据语料**：**6 个 live、~3800 行 / 543 处断言**，
     写的是「**什么算对**」而不是实现（例：`test_live_sw_add_chamfer_tool.py`
     327 行 / 48 断言，带**几何推出的倒角体积公式** 与"点会漂移 1mm"这类实战警告）。
   （同族：Slacker-LLC 1 个 live · vespo92 0 个 · Eduardof0nt **0 个测试文件**）
2. ★ **抄判据，不抄实现**：
     · 期望值优先用**几何推出的公式**（如倒角体积 `0.5·w²·L`），不用"看着像对"
     · 抄它的**实战警告**（漂移量、边界条件）
     · ★ **实现**仍须过命名 / 单位 / 选择三关 **+ 真机验证** —— 理由见事实 170：
       本会话实测「声明层只占 29%」，**贵的是验证**；而四家 **3/4 没声明真机跑过**。
3. ★ **找不到才自己搓** —— 但要**说明"找过"**（在哪找的、结果如何），
   否则"自己搓"与"没去找"无法区分。
```

★ **许可**：`andrewbartels1` 是 **MIT** ⇒ 抄**判据/期望值**可，保留版权声明即可；
  Apache-2.0（`Slacker-LLC`）另带 NOTICE 义务。见铁律 6。

★ **为什么这条重要**：判据（"什么算对"）比代码更贵 —— 代码可以重写，
  而"知道该断言什么"要靠**真机试错**换来。开源项目里已经有人付过这个成本。

并入六条规则（全文 `C:\swprojects\sw-skill-fork\docs\union-conventions.md`，机器校验 `scripts/check_union_conventions.py`，已在 `release_check.py` 里硬失败）：
| # | 规则 | 校验 |
|---|---|---|
| 1 | 命名统一 `solidworks_<域>_<动作>`；headless 路线用 `cadstudio_*`，两者不混用 | 工具名正则 |
| 2 | 长度参数 `_mm` 结尾、角度 `_deg` 结尾，换算只在边界做一次（`sw_connect.mm()`） | 参数名与描述 |
| 3 | 选择用声明式 `selection`，不写裸坐标，并按 mark 分配 | 参数 schema 无裸 `x` / `y` / `z` |
| 4 | 验证等级五级 `verified` / `source_verified` / `stitched` / `indexed` / `not_implemented`；`source_verified` 不得写成 `verified` | `level` 在枚举内，`verified` 要有 `evidence` |
| 5 | 每条并入条目带 `provenance{repo(owner/repo), license, files, upstream_verified}` | `repo` 匹配 `owner/repo`，`license` 在白名单 |
| 6 | 建特征之后查 `EditRebuild3` + `GetWhatsWrong2`，不静默成功 | 建特征类工具都要调 |


