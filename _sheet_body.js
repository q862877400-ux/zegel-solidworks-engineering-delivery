// 项目对比表 —— 4 个工作表
// 数据来源（全部现场量过，见 D:\AI\SW 的本次运行记录）：
//   · 四家的工具数/许可：tools/union-sources.json（权威口径，按操作名去重）
//   · 17 域矩阵：docs/union-coverage-matrix.md（可重新生成）
//   · 我们的五层账：现场跑命令得到（881 族 / 15466 成员 / 963 枚举 / 81 模块 / 692 函数 / 103 按钮）
//   · 候选 51 族：D:\AI\SW\output\candidate-51.json（含"有现成来源可抄"标记）

const HEAD = { bg: { rgb: "#1F4E79" }, cl: { rgb: "#FFFFFF" }, bl: 1 };
const SUB  = { bg: { rgb: "#DDEBF7" }, bl: 1 };
const WARN = { bg: { rgb: "#FCE4D6" }, bl: 1 };
const GOOD = { bg: { rgb: "#E2EFDA" }, bl: 1 };

function put(sheet, a1, grid, style) {
  const rng = sheet.getRange(a1 + ":" + endA1(a1, grid.length, grid[0].length));
  rng.setValues(grid);
  return rng;
}
function colName(n) { // 0-based -> A,B,...
  let s = "";
  n += 1;
  while (n > 0) { const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); }
  return s;
}
function endA1(a1, rows, cols) {
  const m = /^([A-Z]+)(\d+)$/.exec(a1);
  const c0 = m[1].split("").reduce((a, ch) => a * 26 + (ch.charCodeAt(0) - 64), 0) - 1;
  return colName(c0 + cols - 1) + (parseInt(m[2], 10) + rows - 1);
}

// ══════════════ ① 总览 ══════════════
const s1 = workbook.getActiveSheet();
s1.setName("① 总览");
const t1 = [
  ["项目", "工具数", "许可", "自己声明真机跑过", "测试文件", "备注"],
  ["Eduardof0nt/Solidworks-MCP-Server", 187, "MIT", "未声明", 0, "工具最多，测试文件 0 个"],
  ["andrewbartels1/SolidworksMCP-python", 128, "MIT", "未声明（README 自述 under active construction）", 128, ""],
  ["vespo92/SolidworksMCP-TS", 103, "MIT", "未声明", 7, "TypeScript 实现"],
  ["Slacker-LLC/solidworks-mcp", 92, "Apache-2.0", "SW 2026 SP3.2 简体中文（全工具）", 1, "唯一声明全工具跑过；92 个里没有仿真/动画/拓扑/钣金/焊件/公差"],
  ["★ 本仓库", 103, "MIT（已含 Apache-2.0 来源的 NOTICE）", "2 条链真机跑过（仿真、拓扑）", 393, "工具数 = 我们新挂 58 + 上游 server.py 45"],
  ["", "", "", "", "", ""],
  ["口径说明", "工具数取自 tools/union-sources.json（按操作名去重）；★ 用别的数法（数装饰器）会得到不同值，见备注", "", "", "", ""],
];
put(s1, "A1", t1);
s1.getRange("A1:F1").setFontWeight("bold").setBackgroundColor("#1F4E79").setFontColor("#FFFFFF");
s1.getRange("A6:F6").setBackgroundColor("#FFF2CC");
s1.getRange("A8:F8").setBackgroundColor("#F2F2F2");
s1.setColumnWidths(0, 1, 300);
s1.setColumnWidths(1, 1, 80);
s1.setColumnWidths(2, 1, 210);
s1.setColumnWidths(3, 1, 320);
s1.setColumnWidths(4, 1, 90);
s1.setColumnWidths(5, 1, 420);

// ══════════════ ② 17 域对比 ══════════════
const s2 = workbook.create("② 17域对比", 40, 10);
const t2 = [
  ["域", "Eduardof0nt", "andrewbartels1", "vespo92", "Slacker-LLC", "本仓库·MCP台面", "本仓库·能力面(已实现)", "并集", "我们缺(MCP)"],
  ["① 会话 / 文档 / 文件", 14, 22, 10, 7, 7, 49, 44, 37],
  ["② 参考几何", 3, 3, "·", 3, "·", 25, 4, 4],
  ["③ 草图", 26, 15, 16, 20, 1, 62, 43, 42],
  ["④ 尺寸 / 约束 / 参数", 6, 2, 6, 2, 1, 13, 12, 11],
  ["⑤ 零件特征", 23, 11, 3, 13, 6, 59, 34, 28],
  ["⑥ 曲面", 11, "·", 1, "·", 3, 19, 15, 12],
  ["⑦ 钣金", 10, "·", 1, "·", 6, 9, 17, 11],
  ["⑧ 焊件", 5, "·", "·", "·", 5, 14, 10, 5],
  ["⑨ 模具", 3, "·", "·", "·", 7, 8, 10, 3],
  ["⑩ 装配", 13, 7, 4, 3, 7, 55, 26, 19],
  ["⑪ 工程图", 18, 18, 15, 17, 5, 44, 54, 49],
  ["⑫ 检查 / 测量 / 反馈", 11, 3, 7, 6, 3, 22, 19, 16],
  ["⑬ 仿真 / Motion", 3, "·", 1, "·", 6, 80, 10, 4],
  ["⑭ 外观 / 材质 / 配置", 10, 1, 3, 2, 6, 43, 16, 10],
  ["⑮ 宏 / 自动化", 4, 22, 21, "·", 1, 19, 43, 42],
  ["⑯ 高级 / 专项（护城河候选）", "·", "·", "·", "·", 15, 10, 15, "✓ 只有我们有"],
  ["⑰ 未归类", 18, 17, 10, 16, 24, 398, 67, 43],
  ["", "", "", "", "", "", "", "", ""],
  ["合计", "", "", "", "", "", "", 439, 336],
];
put(s2, "A1", t2);
s2.getRange("A1:I1").setFontWeight("bold").setBackgroundColor("#1F4E79").setFontColor("#FFFFFF");
s2.getRange("A17:I17").setBackgroundColor("#E2EFDA");
s2.getRange("A20:I20").setFontWeight("bold").setBackgroundColor("#FFE699");
s2.setColumnWidths(0, 1, 300);
s2.setColumnWidths(1, 6, 96);
s2.setColumnWidths(7, 9, 96);
s2.getRange("I2:I20").setBackgroundColor("#FCE4D6");

// ══════════════ ③ 我们的五层账 ══════════════
const s3 = workbook.create("③ 我们的五层账", 30, 5);
const t3 = [
  ["层", "项", "数量", "说明"],
  ["1 · SolidWorks 官方开的门", "接口族（IFeatureManager 这种）", 881, "官方给的，不是我们写的"],
  ["1 · SolidWorks 官方开的门", "成员（接口里的方法/属性）", 15466, "真正要拉的把手"],
  ["1 · SolidWorks 官方开的门", "枚举（下拉菜单的取值）", 963, "官方枚举文件数"],
  ["1 · 其中有问题的", "★ 没归到业务分类的族", "507（57.5%）", "不是兜底，是「我们没给它分类」"],
  ["2 · 我们写的 Python 函数", "模块 sw_*.py", 81, "把把手包成好用的"],
  ["2 · 我们写的 Python 函数", "公开函数（能直接调的）", 692, "★ 但 AI 看不见这些"],
  ["3 · 挂到柜台上（MCP 按钮）", "我们新挂的（声明式）", 58, "AI 能直接点"],
  ["3 · 挂到柜台上（MCP 按钮）", "上游 server.py 里的装饰器", 45, "原本就有"],
  ["3 · 挂到柜台上（MCP 按钮）", "★ 合计按钮", 103, "= 58 + 45"],
  ["4 · 跟别人比（操作名口径）", "并集（大家一共做过多少种）", 439, "四家 + 上游 + 我们"],
  ["4 · 跟别人比（操作名口径）", "我们缺的", 336, "★ 这是台面缺口，不是能力缺口"],
  ["4 · 跟别人比（操作名口径）", "只有我们有的（独家）", 90, "含护城河域"],
  ["5 · 到底能不能用", "verified（真机跑过、有证据）", 33, "能力清单 39 条里"],
  ["5 · 到底能不能用", "stitched（写好了没真机跑过）", 5, ""],
  ["5 · 到底能不能用", "not_implemented（没做）", 1, ""],
  ["5 · 到底能不能用", "★ 真机证据脚本", 2, "只有仿真、拓扑两条链"],
];
put(s3, "A1", t3);
s3.getRange("A1:D1").setFontWeight("bold").setBackgroundColor("#1F4E79").setFontColor("#FFFFFF");
s3.getRange("A5:D5").setBackgroundColor("#FCE4D6");
s3.getRange("A9:D9").setBackgroundColor("#DDEBF7");
s3.getRange("A10:D12").setBackgroundColor("#FFF2CC");
s3.getRange("A17:D17").setBackgroundColor("#FCE4D6");
s3.setColumnWidths(0, 1, 270);
s3.setColumnWidths(1, 1, 320);
s3.setColumnWidths(2, 1, 110);
s3.setColumnWidths(3, 1, 430);

// ══════════════ ④ 候选 51 族 ══════════════
const s4 = workbook.create("④ 候选51族", 60, 5);
const rows51 = [
  ["IRefAxis", "Feature Interfaces/Reference Geometry", 3, "有"],
  ["IRefPlane", "Feature Interfaces/Reference Geometry", 4, "有"],
  ["IRefPoint", "Feature Interfaces/Reference Geometry", 1, "有"],
  ["ISimulationMotorFeatureData", "Motion Studies", 20, "有"],
  ["IMotionStudyResults", "Motion Studies", 9, "有"],
  ["IAttributeDef", "Model Interfaces", 7, "无"],
  ["ICalloutStringVariable", "Annotation Interfaces/IDisplayDimension", 1, "无"],
  ["ICollisionDetectionManager", "Assembly Interfaces", 9, "无"],
  ["IComplexCornerTreatmentFeatureData", "Feature Interfaces/Structure Systems", 9, "无"],
  ["ICornerMember", "Feature Interfaces/Structure Systems", 3, "无"],
  ["ICosmeticWeldBeadFolder", "Feature Interfaces/Folders", 11, "无"],
  ["IDragOperator", "Assembly Interfaces", 25, "无"],
  ["IFamilyTableAnnotation", "Annotation Interfaces/Table Annotations", 2, "无"],
  ["IFeatureFolder", "Feature Interfaces/Folders", 2, "无"],
  ["IFeatureStatistics", "Feature Interfaces/Others", 11, "无"],
  ["IGeneralToleranceTableAnnotation", "Annotation Interfaces/Table Annotations", 1, "无"],
  ["IGraphicsBody", "Model Interfaces", 4, "无"],
  ["IHelixFeatureData", "Feature Interfaces/Reference Geometry", 17, "无"],
  ["IImportedCurveFeatureData", "Feature Interfaces/Reference Geometry", 3, "无"],
  ["IInstanceToVaryOptions", "Feature Interfaces/Patterns and Mirroring", 13, "无"],
  ["ILight", "Feature Interfaces/Lights and Cameras", 1, "无"],
  ["ILinearCouplerMateFeatureData", "Assembly Interfaces/Mates", 7, "无"],
  ["IMeshBody", "Model Interfaces", 4, "无"],
  ["IMotionPlotFeatureData", "Motion Studies", 4, "无"],
  ["IPMIDatumData", "Annotation Interfaces", 3, "无"],
  ["IPMIDimensionData", "Annotation Interfaces", 3, "无"],
  ["IPMIFrameData", "Annotation Interfaces", 6, "无"],
  ["IPartialEdgeFilletData", "Feature Interfaces/Fillets", 12, "无"],
  ["IPrimaryMemberFacePlaneIntersectionFeatureData", "Feature Interfaces/Structure Systems", 6, "无"],
  ["IPrimaryMemberPathSegmentFeatureData", "Feature Interfaces/Structure Systems", 4, "无"],
  ["IPrimaryMemberRefPlaneFeatureData", "Feature Interfaces/Structure Systems", 9, "无"],
  ["IPrimaryStructuralMemberFeatureData", "Feature Interfaces/Structure Systems", 1, "无"],
  ["IPunchTableAnnotation", "Annotation Interfaces/Table Annotations", 1, "无"],
  ["IReferenceCurve", "Feature Interfaces/Reference Geometry", 6, "无"],
  ["ISMNormalCutGroupData", "Feature Interfaces/Sheet Metal", 2, "无"],
  ["ISecondaryMemberBetweenPointsFeatureData", "Feature Interfaces/Structure Systems", 12, "无"],
  ["ISecondaryMemberSupportPlaneFeatureData", "Feature Interfaces/Structure Systems", 6, "无"],
  ["ISecondaryMemberUpToMembersFeatureData", "Feature Interfaces/Structure Systems", 12, "无"],
  ["ISecondaryStructuralMemberFeatureData", "Feature Interfaces/Structure Systems", 1, "无"],
  ["ISheetMetalGaugeTableParameters", "Feature Interfaces/Sheet Metal", 16, "无"],
  ["ISimpleCornerTreatmentFeatureData", "Feature Interfaces/Structure Systems", 5, "无"],
  ["ISimulation3DContactFeatureData", "Motion Studies", 14, "无"],
  ["ISimulationGravityFeatureData", "Motion Studies", 4, "无"],
  ["ITabAndSlotGroupData", "Feature Interfaces/Others", 21, "无"],
  ["ITitleBlockTableAnnotation", "Annotation Interfaces/Table Annotations", 1, "无"],
  ["ITwoMemberCornerTreatmentFeatureData", "Feature Interfaces/Structure Systems", 6, "无"],
  ["IAVIParameter", "Motion Studies", 15, "无"],
  ["ICosmosMotionStudyProperties", "Motion Studies", 13, "无"],
  ["IMotionPlotFeatureOutput", "Motion Studies", 2, "无"],
  ["IMotionStudyProperties", "Motion Studies", 2, "无"],
  ["IPhysicalSimulationMotionStudyProperties", "Motion Studies", 2, "无"],
];
const t4 = [["接口族", "官方分类", "成员数", "有现成来源可抄？", "怎么判的"]].concat(
  rows51.map((r) => [r[0], r[1], r[2], r[3], r[3] === "有" ? "四家/上游代码里出现过该接口名 ⇒ 能抄 ⇒ 便宜" : "来源里找不到 ⇒ 只能照官方文档自建 ⇒ 贵"])
);
put(s4, "A1", t4);
s4.getRange("A1:E1").setFontWeight("bold").setBackgroundColor("#1F4E79").setFontColor("#FFFFFF");
s4.getRange("A2:E6").setBackgroundColor("#E2EFDA");
s4.setColumnWidths(0, 1, 340);
s4.setColumnWidths(1, 1, 330);
s4.setColumnWidths(2, 1, 80);
s4.setColumnWidths(3, 1, 130);
s4.setColumnWidths(4, 1, 400);
s4.getRange("A53:E53").setFontWeight("bold").setBackgroundColor("#FFE699");
s4.getRange("A53").setValue("小结");
s4.getRange("B53").setValue("有来源可抄 = 5 个（优先做）；其余 46 个要照官方文档自建");

return {
  sheets: workbook.getSheets().map((s) => s.getSheetName()),
  s1Last: s1.getLastRow(),
  s2Last: s2.getLastRow(),
  s3Last: s3.getLastRow(),
  s4Last: s4.getLastRow(),
};
