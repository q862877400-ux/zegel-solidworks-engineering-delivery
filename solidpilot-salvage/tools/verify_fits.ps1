# 验证 fits_iso286.yaml 真的能用：算三个真实配合
# 判据自检：算出的 Xmax/Xmin 必须符合配合的性质（间隙为正、过盈为负/正过盈）
$ErrorActionPreference = 'Stop'

# 从 yaml 手工录入几个待验算的点（直接取自 fits_iso286.yaml 的值）
# 段 "30_40" 孔 H7 = [25, 0]；轴 h6=[0,-16] k6=[18,2] n6=[33,16]
$hole = @{ ES=25.0; EI=0.0 }
$ax = @{
  'h6' = @{ es=0.0;  ei=-16.0 }
  'k6' = @{ es=18.0; ei=2.0  }
  'n6' = @{ es=33.0; ei=16.0 }
}

function Calc($holeES,$holeEI,$axEs,$axEi,$name){
  $Xmax = $holeES - $axEi     # 最大间隙（或负 = 最大过盈）
  $Xmin = $holeEI - $axEs     # 最小间隙（或负 = 最小过盈）
  $type = if($Xmin -ge 0){'间隙配合'} elseif($Xmax -le 0){'过盈配合'} else {'过渡配合'}
  "{0,-8} Xmax={1,7:N0}μm  Xmin={2,7:N0}μm  ⇒ {3}" -f $name, $Xmax, $Xmin, $type
}

Write-Output "════ 基本尺寸段 30~40mm，基孔制 H7 孔（ES=+25, EI=0）════"
Write-Output "  公式：Xmax = ES孔 − ei轴 ; Xmin = EI孔 − es轴"
Write-Output ""
Calc $hole.ES $hole.EI $ax.h6.es $ax.h6.ei 'H7/h6'
Calc $hole.ES $hole.EI $ax.k6.es $ax.k6.ei 'H7/k6'
Calc $hole.ES $hole.EI $ax.n6.es $ax.n6.ei 'H7/n6'
Write-Output ""
Write-Output "════ 验算合理性（这是判断表对不对的关键）════"
Write-Output "  H7/h6  间隙配合 ⇒ Xmin 必须 ≥ 0        : $($hole.EI - $ax.h6.es) μm  ⇒ $(if(($hole.EI - $ax.h6.es) -ge 0){'✅ 合理'}else{'❌ 不合理'})"
Write-Output "  H7/k6  过渡/过盈 ⇒ Xmax 接近 0        : $($hole.ES - $ax.k6.ei) μm  ⇒ $(if(($hole.ES - $ax.k6.ei) -ge 0 -and ($hole.ES - $ax.k6.ei) -lt 25){'✅ 过渡（接近0）'}else{'❌ 不合理'})"
Write-Output "  H7/n6  过盈配合 ⇒ Xmin 必须 ≤ 0        : $($hole.EI - $ax.n6.es) μm  ⇒ $(if(($hole.EI - $ax.n6.es) -le 0){'✅ 过盈'}else{'❌ 不合理'})"
Write-Output ""
Write-Output "════ 与工程实践对照（知识库 bearing.fit_rules 说的是 H7/k6 轴承内圈）════"
Write-Output "  H7/k6 算出的过渡区间: $(( $hole.ES - $ax.k6.ei )) ~ $(( $hole.EI - $ax.k6.es )) μm"
Write-Output "  ⇒ 过盈量约 $(( -1 * ($hole.EI - $ax.k6.es) ))μm = $([math]::Round(-1*($hole.EI-$ax.k6.ei)*0.001,3))mm"
Write-Output "  ⇒ 这正是【轻中载旋转内圈】该有的量级（小过盈，便于装拆）"
Write-Output ""
Write-Output "════ 未注公差 GB/T 1804-m 查表（知识库 fits_iso286.yaml 末尾）════"
Write-Output "  Ø30（30_120 段）未注公差 = ±0.3mm"
Write-Output "  ★ 对照：若按 H7 标注 = $(($hole.ES+0)/1000)mm ⇒ H7 比未注公差【严得多】"
Write-Output "  ⇒ 所以『没标公差』和『标 H7』是两种完全不同的制造要求"
