最近三次交接（**2026-10-01 轮 49 更新**；此前停留在 `3df8670`，已过期多轮）:
  2026-10-01  e26baea        **Spec Kit `converge` 步跑通 002**：6 条 FR 全成立；
                            5 条 SC 里 4 条成立、1 条（SC-004）是**时点判据**。
                            🔴 抓到 1 处真实不符合项并修掉：矩阵能力面列的 **`⚠` 标记**
                            含义原先**只在生成器代码注释里** ⇒ 图例补自解释。
                            ⚠ 遗留：T-005 的验收命令 `capability_gap.py` **不在仓库里**。
  2026-10-01  eadbd3a        **`CONST→接口` 映射表全清 35/0/0**：最后 1 条 `swFmRefSurface`
                            的依据是官方 **Returns 段逐字列出**（`ISweepFeatureData.SweepType`：
                            `swFmSweep` / `swFmSweepCut` / `swRefSurface`(swept surface)）
                            ⇒ 三条独立佐证（官方示例名 / 括注 / 无 `ISurfaceSweep*` 接口）。
                            同轮对 **003 跑 converge** ⇒ 抓到「无许可路径未验」与
                            「`limitations[15]/[16]` 写『维持 stitched』而 `level` 已是 verified」两处。
  2026-10-01  924407b        **AGENTS.md 超指令预算被截断**（66746 > 65536）：
                            截断保留前缀 ⇒ **被截掉的正是末尾最新的事实**（静默退化）。
                            ⇒ 62 条事实**原样**抽到 `docs/known-facts.md`（**零信息损失**），
                            §六 留 21 条速查 + 指针 ⇒ AGENTS.md **40529 字节**，余量 ~25 KB。
