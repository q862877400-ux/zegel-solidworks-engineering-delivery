. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# ★ 闭环验证：用刚建的知识库复核我自己以前做的设计
# 对象：主轴壳体_Housing.sldprt（Ø80/Ø62×110 薄壁筒）
# 之前我做过静力学分析：2.564 MPa，FoS=137（当时就标注"偏乐观"）
$parts = "D:\AI\SW\AI Solidworks\模型"
$null = Call 'open_document' @{ file_path="$parts\主轴壳体_Housing.sldprt" }

Write-Output "════ ① 几何事实（先确认这是什么零件）════"
$g = Call 'analyze_model' @{ analysis_type='geometry' }
"  $($g.cadState.features[0])"
$m = Call 'analyze_model' @{ analysis_type='mass_properties' }
"  $($m.cadState.features[0])"
$f = Call 'analyze_model' @{ analysis_type='faces' }
$fj = $f.cadState.features[0] | ConvertFrom-Json
"  面数 = $($fj.faces.Count)"
$areas = $fj.faces | Sort-Object { -$_.area } | Select-Object -First 4
"  最大的 4 个面:"
$areas | ForEach-Object { "    face[$($_.i)]  面积 = $([math]::Round($_.area*1e6,1)) mm²  法向 = $((($_.normal) -join ','))" }

Write-Output ""
Write-Output "════ ② 按知识库 general.casting 规则核对 ════"
# 薄壁筒：外径80 内径62 壁厚9 长110
$Ro=0.040; $Ri=0.031; $L=0.110
$wall = ($Ro-$Ri)*1000
"  壁厚 = $wall mm（外Ø80 / 内Ø62）"
"  知识库: 铸造件最小壁厚 = max(4, D/50+2.5)"
$minWall = [math]::Max(4, ($Ro*2000)/50 + 2.5)
"  按 D=$([int]($Ro*2000))mm 算，最小壁厚 = $([math]::Round($minWall,1)) mm"
if($wall -ge $minWall){ "  ✅ 壁厚满足" } else { "  ❌ 壁厚不足" }
"  知识库: 拔模角 1°~3°（铸件）"
"  ⚠ 这是【圆筒/回转体】，用【无心毛坯】无需拔模；若做锻件也不需要 ⇒ 此项 N/A"

Write-Output ""
Write-Output "════ ③ 按知识库 general.roughness 核对（最容易漏的）════"
"  知识库默认值:"
"    轴承配合轴颈 → Ra 0.8"
"    一般机加工面 → Ra 3.2"
"    铸造表面     → Ra 12.5~25"
"  ★ 这个零件【两端是配合面】（与主轴/轴承配合），应为 Ra 0.8~1.6"
"  ★ 检查：我建这个模型时【从未设过粗糙度】—— 静力学校核用不到它，但"
"    实际图纸上必须标注，否则装配方无法确定配合等级"

Write-Output ""
Write-Output "════ ④ 按知识库 general.tolerance 核对 ════"
"  ★ 未注公差应按 GB/T 1804-m（中等）标注"
"  ★ 直径 80 属于 >30~120 尺寸段，GB/T 1804-m 的极限偏差量级为【±0.3mm】"
"  ⚠ 检查：这个零件【没有任何公差/配合标注】"

Write-Output ""
Write-Output "════ ⑤ 复核我之前那个 FoS=137 的结论 ════"
"  我当时的条件：10kN 内压（等效），AISI 1020 屈服 351.571 MPa"
"  ⇒ 2.564 MPa / 351.571 MPa = 0.0073 ⇒ FoS = 137"
""
"  ★ 用知识库重新审视："
"    1) 【工况】：内压 10kN 不是我实测的，是【我假设的】。"
"       真实工况若是【轴承载荷】（那是目标里一直想验证的），应力量级完全不同。"
"    2) 【材料】：AISI 1020 是 SolidWorks 库里的近似牌号，不是国标 45 钢。"
"       知识库注明：45钢 σs=355MPa，与 AISI1020 的 351.571 接近，但"
"       ★ 这只是巧合接近，不能当作'我选了 45钢'。"
"    3) 【安全系数】：知识库没有任何一条说 FoS=137 是安全的。"
"       脆性/静载常用许用应力 [σ]=σs/(1.5~3)，即 FoS 应在 1.5~3。"
"       ⇒ FoS=137 说明【载荷假设严重偏小】，不是'零件超安全'。"
""
"  ★ 结论：我当初说'FoS=137 偏乐观'是对的，但当时没指出【偏在哪】——"
"    偏在【载荷假设】，不在材料或几何。"
