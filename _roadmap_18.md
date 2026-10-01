            ⑱ ★★★ **`CONST→接口` 映射表全清：35 唯一 / 0 歧义 / 0 未映射**（轮 48）
               ⇒ 官方 `CreateDefinition` 列出的 **35 个常量一个不剩**都有归属
               （起点 20/4/11 → 轮41 31/0/4 → 轮44 34/0/1 → **本轮 35/0/0**）
               ★ 最后 1 条 `swFmRefSurface` 的依据**不是文本推断**：
                 `ISweepFeatureData/SweepType.md` 的 `## Returns` **逐字列出**
                 「swFmSweep (swept boss) / swFmSweepCut (swept cut) / **swRefSurface (swept surface)**」
                 ⇒ 同一接口，前端靠 `SweepType` 分 boss/cut/surface
               ★ 三条独立佐证：① 该接口 `_overview.md` 的官方示例就叫
                 **"Insert Swept-surface Feature (VBA)"**（文件真存在）；② 括注 `(surface sweep)`；
                 ③ 全 swapi **没有**任何 `ISurfaceSweep*` 接口
               ★ **顺带**：同一条证据**官方确认了**已有的 `swFmSweep`/`swFmSweepCut`（依据变硬）
               ⚠ **同时修掉一处陈旧记载**：⑪ 原先写「剩 4 条未映射需人核」——**已过期**（实际 0）
            ⑲ ★ **Spec Kit 的 `converge` 步已对 003 跑通**（轮 48）：
               `specs/003-topology-closed-loop/converge.md` —— 逐条把 spec 的验收判据
               与**交付物实测**对齐（不是复述 spec），并记下 3 处**不符合项**与处置
