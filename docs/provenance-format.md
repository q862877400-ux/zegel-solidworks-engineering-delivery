# 来源标注制（每个移植函数都要有）

每个移植函数必须带来源头注释，并入 `capabilities.yaml` 的条目另带结构化 `provenance` 字段；许可必须与来源表一致（见 [sources.md](sources.md)）。

头注释模板：

```python
# ── 来源 ─────────────────────────────────────────────────────────
# 仓库: xarial/codestack  (MIT License)
# 文件: solidworks-api/document/drawing/create-third-angle-views.md
# 定位: Create3rdAngleViews2 正确入口
# 官方签名依据: C:\swapi\types\IDrawingDoc\Create3rdAngleViews2.md
#              + D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\
# 本函数为静态移植，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────
```

最后那行「未实测」标注不许删：静态移植与实测是两种状态，删掉它等于把 `source_verified` 说成 `verified`。

`capabilities.yaml` 条目的结构化出处：

```yaml
provenance:
  - {repo: Slacker-LLC/solidworks-mcp, license: Apache-2.0, files: ["sw_feature.py"], upstream_verified: "SW 2026 SP3.2"}
    # repo 要写 owner/repo 全名，不只写目录名；upstream_verified 填来源自己声明的验证环境，没有就留空
```

`repo` 写 `owner/repo` 全名，`license` 在白名单内，`files` 列出实际移植的文件；来源清单与许可判定表见 [sources.md](sources.md)。
