# 本地资源速查

```
★ 上下文压缩 / 新会话后第一个读这个：
D:\AI\SW\docs\ROADMAP.md                    长程施工计划（游标 = 现在在哪、下一步做什么）
                                            它不重述规矩，只链接；规矩在 AGENTS.md

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

── 抢救出的自有成果：D:\AI\SW\solidpilot-salvage\（241 文件 / 11 MB）──
源自 C:\Users\Zegel\solidpilot-mcp\（SolidPilot AGPL-3.0 的克隆，原目录保留当备份、注册已停用），
里面混着我们自己的成果，清点后抢救出来；只有这几件与本任务直接相关：
官方文档\拓扑优化_官方做法.md                 拓扑优化是三个护城河域之一（A9），做它时先读这份
官方文档\Simulation载荷夹具API签名全表.md     Simulation 域的接口签名
loose\问题交接2_DISPPARAMS已通卡E_INVALIDARG.md   COM byref 的实操记录
loose\问题交接_Simulation夹具API调不通.md     Simulation 夹具 API 的坑
loose\swdoc.ps1 / swdoc2.ps1                 官方文档检索工具（上面那份 swdoc.ps1 的同源副本）
cs-patches\ + _MANIFEST.tsv                  C# 执行层 14 个文件（6 改上游 + 8 新增）
刻意没搬：知识库\（与 mech-design skill 的知识库是同一份）、调研\GitHub项目\（140 MB、10 个
git 克隆可重取，且含破解投递页 —— 铁律 2 红线零接触）。目录清单与逐件说明见它的 README.md。
```

产出落点（写在工作副本里，随自建仓库一起走）：`docs/union-conventions.md`、`docs/union-coverage-matrix.md`、`docs/capability-matrix.md`、`docs/gap-analysis.md`、`docs/signature-audit.md`、`docs/harvest-report.md`、`tools/build_union_sources.py`、`tools/build_union_map.py`、`tools/union-sources.json`、`scripts/check_union_conventions.py`。
