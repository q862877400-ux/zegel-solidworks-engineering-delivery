# 本地资源速查

```
D:\AI\SW\AGENTS.md                          根指令文件（唯一真源，勿复制到别处）
D:\AI\SW\                                   工作区仓库（git，提交 1f86c5d 起）
C:\swprojects\sw-skill-fork\                代码工作副本（git，唯一改代码的地方）

── 官方离线源（细节见 docs/sources.md）──
D:\AI\SW\AI Solidworks\官方文档\SWhelp\     29,697 文件 / 285.4 MB（CHM 解包，权威）
    sldworksapi 11579 | sldworksapivb6 16718 | swconst 1353 | cosworks 47
D:\AI\SW\AI Solidworks\手册\swdoc.ps1       官方文档全文检索（-Q / -File / -List）
C:\swapi\                                    566 类型 / 963 枚举 / 11,557 成员 / 2,839 示例
%USERPROFILE%\.agents\skills\mech-design\tools\sw_know.py    结构化检索工具
D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\      interop DLL（反射原料，无 XMLDoc）

── 素材仓库 ──
C:\swprojects\                               23 个目录：21 个项目 + sw-skill-fork + _tmp_mcp
C:\swprojects\sw-automation-skill\           上游只读克隆（与 24 星的 djlex83 消歧）
C:\swprojects\{Eduardof0nt,andrewbartels1,SolidworksMCP-TS,Slacker-LLC}\   四家外部 MCP
C:\swtest\                                   此前的 B1/B2 实测脚本（只读参考，本项目不执行）
```

产出落点（写在工作副本里，随 fork 一起走）：`docs/union-conventions.md`、`docs/union-coverage-matrix.md`、`docs/capability-matrix.md`、`docs/gap-analysis.md`、`docs/signature-audit.md`、`docs/harvest-report.md`、`tools/build_union_sources.py`、`tools/build_union_map.py`、`tools/union-sources.json`、`scripts/check_union_conventions.py`。
