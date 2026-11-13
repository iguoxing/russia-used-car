# -*- coding: utf-8 -*-
"""生成 rules.html（基本出口规则说明）与 russia-export-rules.md"""
import os, sys, html
sys.path.insert(0, os.path.dirname(__file__))
from rules_data import (FLOW_CN, FLOW_RU, DOCS, TIMELINE, PITFALLS, CHECKLIST,
                        CONFLICTS, SOURCES, RATE_DATE)
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = lambda x: html.escape(str(x), quote=True)

base = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
CSS = base.split("<style>", 1)[1].split("</style>", 1)[0]

EXTRA = r"""
.flow2{display:grid;grid-template-columns:1fr 1fr;gap:15px}
.flowcol{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:18px}
.flowcol.cn{border-top:3px solid var(--a1)}
.flowcol.ru{border-top:3px solid var(--a2)}
.flowcol h3{margin:0 0 4px;font-size:17px}
.flowcol .sub{font-size:12.5px;color:var(--muted);margin:0 0 14px}
.step{display:flex;gap:11px;padding:10px 0;border-bottom:1px dashed var(--line)}
.step:last-child{border-bottom:0}
.step .n{flex:0 0 30px;height:30px;border-radius:8px;background:var(--panel2);border:1px solid var(--line);
 display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:var(--a1)}
.step b{font-size:13.5px;color:var(--text)}
.step p{margin:3px 0 0;font-size:12.5px;color:var(--muted);line-height:1.7}
.step .meta{font-size:11px;margin-top:4px}
.step .meta span{margin-right:9px}
.tag.b{background:rgba(77,156,255,.13);color:#9ec8ff;border-color:rgba(77,156,255,.4)}
.tag.warn{background:rgba(235,105,80,.14);color:#ff9a80;border-color:rgba(235,105,80,.4)}
.tl{position:relative;padding-left:22px;margin-top:8px}
.tl:before{content:"";position:absolute;left:6px;top:6px;bottom:6px;width:2px;background:var(--line)}
.tli{position:relative;padding:9px 0 9px 4px;border-bottom:1px dashed var(--line)}
.tli:last-child{border-bottom:0}
.tli:before{content:"";position:absolute;left:-20px;top:16px;width:9px;height:9px;border-radius:50%;background:var(--a1);border:2px solid var(--bg)}
.tli.c:before{background:var(--a3)}
.tli .d{font-size:12px;font-weight:700;color:var(--a1);letter-spacing:.03em}
.tli.c .d{color:var(--a3)}
.tli .t{font-size:13.5px;color:var(--text);margin:2px 0}
.tli .s{font-size:12px;color:var(--muted)}
.chk{display:flex;gap:10px;align-items:flex-start;padding:9px 11px;border:1px solid var(--line);border-radius:9px;background:var(--panel2);margin:7px 0;cursor:pointer;font-size:13px;line-height:1.6}
.chk input{margin-top:4px;flex:0 0 auto}
.chk.done{background:rgba(52,201,161,.10);border-color:rgba(52,201,161,.4)}
.chk.done span{text-decoration:line-through;color:var(--muted)}
.pit{border-left:3px solid var(--a4);background:var(--panel2);border-radius:0 10px 10px 0;padding:12px 15px;margin:9px 0}
.pit b{color:#ff9a80;font-size:13.5px}
.pit p{margin:5px 0 0;font-size:12.8px;color:var(--muted);line-height:1.75}
.mini{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.mini .card{margin:0}
.mini h4{margin:0 0 8px;font-size:14px;color:var(--a1)}
.mini p{margin:0;font-size:12.8px;color:var(--muted);line-height:1.75}
.biglink{display:inline-block;margin-top:10px;padding:9px 15px;border-radius:9px;background:rgba(77,156,255,.16);border:1px solid var(--a1);color:#9ec8ff;font-weight:700;font-size:13px}
.biglink:hover{text-decoration:none;background:rgba(77,156,255,.26)}
@media(max-width:900px){.flow2,.mini{grid-template-columns:1fr}}
@media print{
 body{background:#fff!important;color:#16202c!important}
 :root{--text:#16202c;--muted:#475569;--panel:#fff;--panel2:#f7fafc;--line:#cbd5e1;--bg:#fff}
 nav,.btn,.biglink{display:none!important}
 .card,.flowcol,.pit,.chk,.kpi,.mini .card{background:#fff!important;border-color:#cbd5e1!important;color:#16202c!important}
 h1,h2,h3,h4,.eyebrow,.sub,.kpi-v,.kpi-l,.kpi-s,.step b,.step p,.tli .t,.tli .s,.pit p,.pit b,.mini p,.lead,.cap,td,th,p,li,footer{color:#16202c!important}
 .step .d,.tli .d{color:#1d4ed8!important}
 th{background:#e8eef5!important;color:#16202c!important}
 .tbl-scroll{overflow:visible!important}
 table{table-layout:auto!important}
 th,td{padding:5px 7px!important;font-size:10.5px!important;white-space:normal!important}
 .card,.flowcol,.pit,.tli{page-break-inside:avoid}
 section{margin:20px 0}
 html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
}
"""


def nav(active):
    pages = [("index", "index.html", "总览看板"),
             ("segments", "segments.html", "细分市场 · 6 大赛道"),
             ("quotation", "quotation.html", "报价计算器"),
             ("rules", "rules.html", "出口规则说明")]
    p = "".join('<a class="ptab' + (' on' if k == active else '') + '" href="' + u + '">' + E(t) + '</a>'
                for k, u, t in pages)
    anchors = [("#top", "概览"), ("#flow", "全流程"), ("#cn", "中国出口侧"), ("#ru", "俄罗斯进口侧"),
               ("#docs", "单证清单"), ("#timeline", "政策时间线"), ("#pay", "收汇与合规"),
               ("#pits", "常见坑"), ("#check", "报价前检查"), ("#conflicts", "口径冲突"),
               ("#sources", "来源"), ("#downloads", "配套下载")]
    return '<nav><div class="wrap">' + p + '<span class="psep"></span>' + \
           "".join('<a href="%s">%s</a>' % (u, t) for u, t in anchors) + '</div></nav>'


def table(head, rows, cls=""):
    th = "".join("<th>%s</th>" % h for h in head)
    tr = "".join("<tr>" + "".join("<td>%s</td>" % x for x in r) + "</tr>" for r in rows)
    return '<div class="tbl-scroll %s"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (cls, th, tr)


def tag(g):
    c = "a" if g.startswith("A") else "c" if g.startswith("C") else "b"
    return '<span class="tag %s">%s</span>' % (c, E(g))


def steps(arr):
    return "".join(
        '<div class="step"><div class="n">%s</div><div><b>%s</b><p>%s</p>'
        '<div class="meta"><span>来源 %s</span><span>%s 级</span></div></div></div>'
        % (E(n), E(t), E(d), E(src), E(g)) for n, t, d, src, g in arr)


cn_steps = steps(FLOW_CN)
ru_steps = steps(FLOW_RU)
doc_rows = [[E(a), E(b), E(c), E(d), tag(e)] for a, b, c, d, e in DOCS]
tl = "".join(
    '<div class="tli%s"><div class="d">%s</div><div class="t">%s</div>'
    '<div class="s">依据 %s · %s 级　｜　%s</div></div>'
    % (" c" if g.startswith("C") else "", E(d), E(t), E(src), E(g), E(note))
    for d, t, src, g, note in TIMELINE)
pits = "".join(
    '<div class="pit"><b>%s</b> <span class="tag %s">%s · %s</span><p>%s</p></div>'
    % (E(t), "a" if g.startswith("A") else "c", E(src), E(g), E(d))
    for t, d, src, g in PITFALLS)
checks = "".join(
    '<label class="chk" data-i="%d"><input type="checkbox" id="ck%d"><span>%s</span></label>'
    % (i, i, E(c)) for i, c in enumerate(CHECKLIST))
conf_rows = [[E(a), E(b), E(c)] for a, b, c in CONFLICTS]
src_rows = [[E(a), E(b), E(c), tag(d),
             '<a href="%s" target="_blank" rel="noopener">链接</a>' % E(e)] for a, b, c, d, e in SOURCES]

DL = [
    ("russia-quotation-calculator.xlsx", "报价计算器 Excel 模板", "带公式，参数可迭代"),
    ("russia-export-rules.pdf", "本页 PDF 版", "打印友好 / 可归档"),
    ("russia-export-rules.md", "本页 Markdown 版", "便于二次编辑"),
    ("russia-parallel-import-report.pdf", "主报告 PDF（17 页）", "四维 + 核验 + 维度优化"),
    ("russia-top100-clients.xlsx", "TOP100 客户 Excel", "8 个工作表"),
    ("russia-segment-analysis.pdf", "细分市场分析 PDF", "6 大赛道机会图谱"),
]
dls = "".join(
    '<a href="downloads/%s" style="display:block;padding:11px 14px;margin:8px 0;border:1px solid var(--line);'
    'border-radius:10px;background:var(--panel2);color:var(--text);text-decoration:none">'
    '<b>%s</b> <span style="color:var(--muted);font-size:12px">— %s</span></a>' % (f, E(t), E(d))
    for f, t, d in DL)

JS = r"""
<script>
(function(){
 var box=document.querySelectorAll(".chk");
 function load(){try{var s=localStorage.getItem("ru_rules_checks");if(!s)return;
   var d=JSON.parse(s);box.forEach(function(b,i){var c=b.querySelector("input");
   if(d[i]){c.checked=true;b.classList.add("done")}});update()}catch(e){}}
 function update(){var n=document.querySelectorAll(".chk.done").length;
   document.getElementById("chkStat").textContent=n+" / "+box.length+" 项已完成"}
 function save(){var d=[];box.forEach(function(b){d.push(b.querySelector("input").checked)});
   try{localStorage.setItem("ru_rules_checks",JSON.stringify(d))}catch(e){}}
 box.forEach(function(b){b.querySelector("input").addEventListener("change",function(){
   b.classList.toggle("done",this.checked);save();update()})});
 document.getElementById("chkReset").addEventListener("click",function(){
   box.forEach(function(b){b.querySelector("input").checked=false;b.classList.remove("done")});save();update()});
 document.getElementById("chkCopy").addEventListener("click",function(){
   var t="【俄罗斯汽车出口 · 报价前检查清单】\n"+Array.prototype.map.call(box,function(b,i){
     return (b.querySelector("input").checked?"[x] ":"[ ] ")+b.querySelector("span").textContent}).join("\n");
   var a=document.createElement("textarea");a.value=t;a.style.position="fixed";a.style.opacity=0;
   document.body.appendChild(a);a.select();try{document.execCommand("copy");
     this.textContent="已复制 ✓";var self=this;setTimeout(function(){self.textContent="复制清单"},1600)}catch(e){}
   document.body.removeChild(a)});
 load();update();
})();
</script>
"""

BODY = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>俄罗斯汽车出口基本规则说明｜中国出口侧 · 俄罗斯进口侧 · 单证与收汇</title>
<style>@@CSS@@</style></head><body>
@@NAV@@
<div class="wrap" id="top">
<header>
 <div class="eyebrow">RUSSIA · EXPORT COMPLIANCE BASICS · @@DATE@@</div>
 <h1>俄罗斯汽车出口基本规则说明</h1>
 <p class="sub">从「谁有资格出口」到「车怎么在俄上牌」：中俄两侧流程、单证、税费、收汇与常见坑</p>
 <div class="badges"><span class="badge">新增 Tab 页 · @@DATE@@</span><span class="badge">7 步中方 + 6 步俄方</span><span class="badge">12 类单证</span><span class="badge">17 条来源 · 4 处口径冲突</span></div>
 <p class="lead" style="margin-top:20px">这份说明按「做一单生意实际要走的路」写，不按法规章节写。每条规则标了来源与证据等级：A = 官方法规/海关/政府公告，B = 权威机构经媒体转述或行业实操指南，C = 行业调研、二手转述或口径存疑。<b>落地前请让俄方持牌报关行与你的开户行复核当期要求。</b></p>
 <a class="biglink" href="quotation.html">→ 去报价计算器，按这些规则算一单落地成本</a>
</header>

<div class="kpis">
 <div class="kpi"><div class="kpi-v">7 + 6</div><div class="kpi-l">中方 / 俄方流程步骤</div><div class="kpi-s">从备案到上牌</div></div>
 <div class="kpi"><div class="kpi-v">13%</div><div class="kpi-l">整车 / 二手车出口退税</div><div class="kpi-s">单证一致才可退</div></div>
 <div class="kpi"><div class="kpi-v">一批一证</div><div class="kpi-l">出口许可证</div><div class="kpi-s">单证最多 20 台 / 6 个月</div></div>
 <div class="kpi"><div class="kpi-v">30 / 70</div><div class="kpi-l">建议付款结构</div><div class="kpi-s">预付 + 见单付尾款</div></div>
 <div class="kpi"><div class="kpi-v">160 hp</div><div class="kpi-l">报废税资格线</div><div class="kpi-s">过线直接转商业系数</div></div>
 <div class="kpi"><div class="kpi-v">欧 5</div><div class="kpi-l">俄方排放门槛</div><div class="kpi-s">国六不可等效替代</div></div>
</div>

<div class="card warn"><b>⚠ 先分清三件事，否则规则会用错</b><br/>
① <b>新车还是二手车</b>：二手车多出企业备案、WM/T 8-2022 检测、「转让待出口」签注、180 天售后确认书与通关后注销登记；<br/>
② <b>法人商业进口还是个人自用</b>：个人优惠档需同时满足 ≤3 年 / ≤3.0L / ≤160hp / 一年 1 辆 / 12 个月不转售，且功率过 160hp 即失效，商业批量根本不适用；<br/>
③ <b>官方授权还是平行进口</b>：平行进口只解决特定真品的知识产权例外，<b>不豁免</b> EAC 认证、俄文标签、ЭПТС、报废税，且不得宣称官方授权或提供原厂质保 [S14]。</div>

<section id="flow"><h2><span class="n">01</span>一页看懂：中俄两侧全流程</h2>
<p class="lead">左边是中国出口侧（你把车发出去），右边是俄罗斯进口侧（客户把车清出来上牌）。贸易术语决定中间哪一段由谁负责，详见报价计算器的「成本阶梯」。</p>
<div class="flow2">
 <div class="flowcol cn"><h3>中国出口侧</h3><p class="sub">主体资质 → 单证 → 报关 → 收汇 → 退税</p>@@CNSTEPS@@</div>
 <div class="flowcol ru"><h3>俄罗斯进口侧</h3><p class="sub">合同 → 运输 → 完税 → 认证 → 上牌</p>@@RUSTEPS@@</div>
</div></section>

<section id="cn"><h2><span class="n">02</span>中国出口侧：资质、许可证与退税</h2>
<div class="mini">
 <div class="card"><h4>① 谁能出口</h4><p>营业执照经营范围含汽车销售 / 二手车经销；海关进出口货物收发货人备案；<b>二手车出口企业还须在「商务部业务系统统一平台」向省级商务主管部门备案</b>，审核通过后一年内可经营、年度需报送。谁出口谁申领许可证，不可代办 [S13]。</p></div>
 <div class="card"><h4>② 许可证怎么领</h4><p>一批一证、同一商品编码最多 20 台、有效期 6 个月且截止当年 12-31；省级商务主管部门 3 个工作日签发；许可证 HS 编码必须与车辆动力类型一致（插混 8703602300 / 纯电 8703603300 不同），填错会被海关按申报不实处罚 [S12][S13]。</p></div>
 <div class="card"><h4>③ 退税与单证</h4><p>整车 / 二手车出口退税率 <b>13%</b>，一台 10 万元的车可退一万多；但购进发票、过户凭证、合同与报关单金额必须一致并完整留档，否则退税被卡。资料齐全最快 3 个工作日；部分基地还有退税周转资金池 [S11]。</p></div>
 <div class="card"><h4>④ 二手车额外动作</h4><p>收购后办理「转让待出口」签注（临牌最长 60 日，此后不得再境内交易）；按 WM/T 8-2022 一车一检；<b>注册登记未满 180 天的新车须生产企业出具《售后维修服务确认书》</b>（2026-01-01 起强制）；海关通关后 2 个月内办注销登记 [S12][S13]。</p></div>
 <div class="card"><h4>⑤ 新能源特殊要求</h4><p>属 9 类危险品：海运需提前订危险品舱、准备英文 MSDS 与 UN38.3 报告、完成海事申报；燃油车油量控制在 1/4 以下、新能源电量 30–50%；申报要素含电池容量 [S09][S12]。</p></div>
 <div class="card"><h4>⑥ 申报规范</h4><p>单一窗口无纸化；商品名称统一填「旧+品牌+排量+车型」，完整录入 17 位 VIN；如实申报品牌型号、发动机类型、座位数、是否中规车、新旧程度、电池容量。低报货值会同时触发俄方重新核价与国内退税单证不一致 [S10][S12]。</p></div>
</div></section>

<section id="ru"><h2><span class="n">03</span>俄罗斯进口侧：主体、税费、认证与上牌</h2>
<div class="card"><h3 style="margin-top:0">3.1 进口主体决定税额量级</h3>
<p>法人商业进口按完税价格缴关税、消费税、增值税、报废税与清关手续费；个人自用仅在同一年内 1 辆、≤3 年、≤3.0L、≤160hp、12 个月不转售时适用报废税优惠系数 0.17 / 0.26（3,400 / 5,200 卢布）。<b>功率一旦超过 160hp，优惠档直接失效转商业系数</b>：同款途观 1.4T 150hp 报废税 3,400 卢布，2.0T 180hp 为 114,600 卢布，差 30 马力多 11 万卢布 [S04][S17]。</p>
<p>商业系数按排量 × 车龄查表（1–2L 新车 12.95、旧车 33.84；2–3L 新车 27.51、旧车 84.01；3L+ 137+），乘用车基准 20,000 卢布，卡车/客车/挂车 150,000 卢布。<b>报废税通常是单车最大税费项</b>，不是关税 [S04][S05]。</p></div>
<div class="card" style="margin-top:14px"><h3 style="margin-top:0">3.2 认证与车辆护照</h3>
<p>整车须符合 EAEU 技术法规 <b>TR CU 018/2011</b>（制动、灯光、安全带、VIN、排放、整体安全）。两条路径：<b>ОТТС</b> 整车型式认证（2025-07 起须俄境内实验室，周期 3–6 个月）；<b>СБКТС</b> 单车安全结构证书（约 4 万卢布 / 5–10 天，无 ОТТС 时逐车 10–25 万卢布 + 30–60 天）。拿到认证 + 缴清报废税后申请 <b>ЭПТС 电子车辆护照</b>，未缴清差额前 EPTS 一直是 Draft，车不能上牌、不能合法销售、不能过户 [S08][S16]。</p>
<p>另需 <b>ЭРА-ГЛОНАСС</b> 紧急呼叫（缺装需俄认证机构加装 3.5–6.5 万卢布）；排放强制欧 5，<b>中国国六标准不能等效替代</b>，需单独合规认证；二手车车龄限制与 SBKTS 要求按当期清单核验 [S08][S16]。</p></div>
<div class="card" style="margin-top:14px"><h3 style="margin-top:0">3.3 平行进口不是「免检通道」</h3>
<p>第 463-FZ 号联邦法把平行进口清单授权延续适用至 2026 年，工贸部 2025 年第 4769 号令部分调整自 2026-05-27 生效。需按进口发生时有效的清单逐项核验：是否真品、是否境外合法投放市场、HS 编码与品牌是否在清单内、有无品牌排除或型号限制。<b>被移出清单不等于禁止进口</b>，只是不能再凭平行进口特别措施免除知识产权责任。即使符合条件，仍须遵守海关申报、EAC 认证、俄文标签、数字标识、产品安全与消费者权益规定；不得卖假货、擅自换标、误导性改装或虚假宣称官方授权。「零公里二手车」是商业叫法，不是法定分类 [S14]。</p></div>
<div class="card" style="margin-top:14px"><h3 style="margin-top:0">3.4 上牌与售后</h3>
<p>海参崴→莫斯科内陆运输 15–25 万卢布 / 7–14 天。到 ГИБДД 上牌需五件：ЭПТС、СБКТС、报关单（ПТД/ТПО）、ОСАГО 交强险、车主身份证件，齐备当日发牌。平行进口<b>无原厂质保</b>，由进口商/销售方自行承担售后，需提前落实延保方案、易损件库存、俄语车机与说明书、冬季适配 [S08][S14]。</p></div></section>

<section id="docs"><h2><span class="n">04</span>单证清单（按环节）</h2>
<p class="lead">缺一张就可能卡在港口。所有涉及 VIN、品牌、排量、功率、动力类型的字段，在许可证、登记证、检测报告、报关单、发票之间必须完全一致。</p>
<div class="card">@@DOCTBL@@</div></section>

<section id="timeline"><h2><span class="n">05</span>政策时间线（2024 → 2027）</h2>
<p class="lead">黄色圆点 = 来源存在冲突或证据等级 C，落地前必须核原文。长周期合同一定要写费率与汇率调价条款。</p>
<div class="card"><div class="tl">@@TIMELINE@@</div></div></section>

<section id="pay"><h2><span class="n">06</span>收汇、结算与合规筛查</h2>
<div class="mini">
 <div class="card"><h4>付款结构</h4><p>建议 <b>30% 预付 + 70% 见清关单/提单副本</b>，避免全款预付；船发前确认款项实际到账再放行提单；警惕第三方代付带来的洗钱与合规风险。合同加入制裁条款：任一方或其银行被列入制裁名单导致通道中断时，可终止合同并按已履约比例结算、30 日内无息退还预付款 [S15]。</p></div>
 <div class="card"><h4>结算通道</h4><p>优先人民币或卢布本币结算，绕开美元清算：<b>CIPS / SPFS / VTB 上海分行</b>、边境口岸银行。中俄贸易本币结算比例已很高，但仍需确认开户行对汽车品类的受理政策，避开受制裁俄金融机构与涉美通道；高价值交易可能需更复杂的合规结构 [S15][S17 相关]。</p></div>
 <div class="card"><h4>汇率与调价</h4><p>卢布年波动多次超 30%（2026 年 52 周区间 70.79–87.00 RUB/USD）。合同可约定「结算日较签约日波动超 5% 的部分按比例分担」或直接用人民币计价；大额订单可做远期结汇 / 锁汇。报废税每年 1 月调整，2027-01-01 预计再涨 10–20% [S01][S17]。</p></div>
 <div class="card"><h4>制裁与主体筛查</h4><p>签约前核查俄方公司、股东、最终受益人是否在制裁名单；核对汇款账户与合同主体一致；关注最终用户 / 最终用途声明、车辆与车机电子件的出口管制归类；俄罗斯个人数据本地化存储要求也适用于客户信息管理 [S15]。</p></div>
 <div class="card"><h4>清关节点管控</h4><p>协议写明因经销商单证瑕疵导致滞港的违约金（如每日货值 0.1%、上限合同额 15%）；建立绿 / 黄 / 红灯机制：5 个工作日正常、超 5 日高层介入、超 10 日启动法律保全与替代物流 [S15]。</p></div>
 <div class="card"><h4>退税前置条件</h4><p>13% 退税是重要现金流，但要求单证与报关单金额匹配、业务资料逻辑一致。中小出口商最容易忽略单证留存，导致退税款卡住。建议把「单证一致性检查」写进发货 SOP [S11]。</p></div>
</div></section>

<section id="pits"><h2><span class="n">07</span>八个最常见的坑</h2>
@@PITS@@</section>

<section id="check"><h2><span class="n">08</span>报价前十项检查清单</h2>
<p class="lead">可勾选，状态存在本机浏览器，下次打开自动恢复；也可一键复制清单发给同事。<b id="chkStat">0 / 10 项已完成</b></p>
<div class="card">@@CHECKS@@
<div class="btn-row" style="grid-template-columns:repeat(2,1fr);max-width:320px;margin-top:12px">
 <button class="btn" id="chkCopy">复制清单</button><button class="btn" id="chkReset">清空勾选</button>
</div></div></section>

<section id="conflicts"><h2><span class="n">09</span>四处口径冲突（报价前必须核）</h2>
<p class="lead">这些不是算错，是公开来源本身打架。计算器给了默认值，但<b>不替你拍板</b>。</p>
<div class="card">@@CONFTBL@@</div></section>

<section id="sources"><h2><span class="n">10</span>数据来源与证据等级</h2>
<div class="card">@@SRCTBL@@</div></section>

<section id="downloads"><h2><span class="n">↓</span>配套文件下载</h2><p class="lead">Excel 模板带公式可离线迭代；PDF / Markdown 为本页完整文字版。</p><div class="card">@@DLS@@</div></section>
<footer>本页为业务操作指引，规则与税率随政策调整，所有条目均标注来源与证据等级，不构成法律或税务意见。正式交易前请由俄方持牌报关行、中方开户行与法务复核当期要求，尤其涉及 EAEU 转口、认证状态与制裁名单的部分。配套落地成本测算见「报价计算器」Tab。</footer>
</div>
@@JS@@
</body></html>"""

out = (BODY.replace("@@CSS@@", CSS + EXTRA)
       .replace("@@NAV@@", nav("rules"))
       .replace("@@DATE@@", RATE_DATE)
       .replace("@@CNSTEPS@@", cn_steps)
       .replace("@@RUSTEPS@@", ru_steps)
       .replace("@@DOCTBL@@", table(["环节", "单证 / 材料", "办理时点", "来源", "等级"], doc_rows))
       .replace("@@TIMELINE@@", tl)
       .replace("@@PITS@@", pits)
       .replace("@@CHECKS@@", checks)
       .replace("@@CONFTBL@@", table(["冲突点", "两种记载", "本页处理"], conf_rows))
       .replace("@@SRCTBL@@", table(["编号", "来源", "关键内容", "等级", "链接"], src_rows))
       .replace("@@DLS@@", dls)
       .replace("@@JS@@", JS))
open(os.path.join(SITE, "rules.html"), "w", encoding="utf-8").write(out)
print("[OK] rules.html", len(out) // 1024, "KB")

# ---------------- Markdown ----------------
L = []
A = L.append
A("# 俄罗斯汽车出口基本规则说明\n")
A("> 2026-11-13 版｜从「谁有资格出口」到「车怎么在俄上牌」：中俄两侧流程、单证、税费、收汇与常见坑\n")
A("> 证据等级：A = 官方法规/海关/政府公告；B = 权威机构经媒体转述或行业实操指南；C = 行业调研、二手转述或口径存疑\n")
A("\n配套：[报价计算器](quotation.html) · [总览看板](index.html) · [细分市场](segments.html)\n")
A("\n## 先分清三件事\n")
A("1. **新车还是二手车**：二手车多出企业备案、WM/T 8-2022 检测、「转让待出口」签注、180 天售后确认书与通关后注销登记。\n")
A("2. **法人商业进口还是个人自用**：个人优惠档需同时满足 ≤3 年 / ≤3.0L / ≤160hp / 一年 1 辆 / 12 个月不转售，功率过 160hp 即失效，商业批量不适用。\n")
A("3. **官方授权还是平行进口**：平行进口只解决特定真品的知识产权例外，**不豁免** EAC 认证、俄文标签、ЭПТС、报废税，且不得宣称官方授权或提供原厂质保 [S14]。\n")
A("\n## 01 中国出口侧（7 步）\n")
for n, t, d, s, g in FLOW_CN:
    A(f"**{n} {t}**（{s}，{g} 级）\n\n{d}\n\n")
A("### 关键补充\n")
A("- **谁能出口**：营业执照含汽车销售/二手车经销 + 海关收发货人备案；二手车出口企业须在「商务部业务系统统一平台」向省级商务主管部门备案，审核通过后一年内可经营、年度需报送 [S13]。\n")
A("- **许可证**：一批一证、同一商品编码最多 20 台、有效期 6 个月且截止当年 12-31；省级商务主管部门 3 个工作日签发；HS 编码须与动力类型一致（插混 8703602300 / 纯电 8703603300），填错按申报不实处罚 [S12][S13]。\n")
A("- **二手车额外动作**：「转让待出口」签注（临牌最长 60 日，此后不得境内交易）、WM/T 8-2022 一车一检、注册未满 180 天须《售后维修服务确认书》（2026-01-01 起）、通关后 2 个月内注销登记 [S12][S13]。\n")
A("- **新能源**：属 9 类危险品，海运需订危险品舱 + 英文 MSDS + UN38.3 + 海事申报；燃油车油量 <1/4、新能源电量 30–50% [S09][S12]。\n")
A("- **出口退税 13%**：一台 10 万元的车可退一万多；购进发票、过户凭证、合同与报关单金额必须一致并留档，否则退税被卡；资料齐全最快 3 个工作日 [S11]。\n")
A("\n## 02 俄罗斯进口侧（6 步）\n")
for n, t, d, s, g in FLOW_RU:
    A(f"**{n} {t}**（{s}，{g} 级）\n\n{d}\n\n")
A("### 进口主体决定税额量级\n")
A("法人商业进口按完税价格缴关税、消费税、增值税、报废税与清关手续费。个人自用仅在一年 1 辆、≤3 年、≤3.0L、≤160hp、12 个月不转售时适用报废税优惠系数 0.17 / 0.26（3,400 / 5,200 卢布）。**功率超过 160hp 优惠档直接失效转商业系数**：同款途观 1.4T 150hp 为 3,400 卢布，2.0T 180hp 为 114,600 卢布，差 30 马力多 11 万卢布 [S04][S17]。\n")
A("\n商业系数按排量 × 车龄查表（乘用车基准 20,000 卢布）：\n")
A("\n| 排量档 | ≤3 年系数 | >3 年系数 | 新车报废税 | 旧车报废税 |\n|---|---|---|---|---|\n")
for lo, hi, a, b, n in [(0, 1000, 8.92, 20.70, "≤1.0L"), (1000, 2000, 12.95, 33.84, "1.0–2.0L"),
                         (2000, 3000, 27.51, 84.01, "2.0–3.0L"), (3000, 1e9, 137, 137, ">3.0L")]:
    A(f"| {n} | {a} | {b} | {int(20000*a):,} ₽ | {int(20000*b):,} ₽ |\n")
A("\n### 认证与车辆护照\n")
A("整车须符合 EAEU **TR CU 018/2011**。两条路径：**ОТТС** 整车型式认证（2025-07 起须俄境内实验室，3–6 个月）；**СБКТС** 单车安全结构证书（约 4 万卢布 / 5–10 天，无 ОТТС 时逐车 10–25 万卢布 + 30–60 天）。认证 + 缴清报废税后申请 **ЭПТС 电子车辆护照**，未缴清差额前 EPTS 为 Draft，车不能上牌、销售或过户 [S08][S16]。另需 **ЭРА-ГЛОНАСС**（缺装加装 3.5–6.5 万卢布）；排放强制欧 5，**中国国六不可等效替代** [S16]。\n")
A("\n### 平行进口不是免检通道\n")
A("第 463-FZ 延续平行进口清单授权至 2026 年，工贸部 2025 年第 4769 号令部分规定 2026-05-27 生效。须按进口发生时有效清单核验真品、境外合法投放、HS 与品牌、品牌排除与型号限制。被移出清单不等于禁止进口，只是不能再凭特别措施免除知识产权责任；仍须遵守 EAC 认证、俄文标签、数字标识、产品安全与消费者权益规定，不得卖假货、换标、误导改装或虚假宣称官方授权。「零公里二手车」不是法定分类 [S14]。\n")
A("\n### 上牌与售后\n")
A("海参崴→莫斯科 15–25 万卢布 / 7–14 天。ГИБДД 上牌五件：ЭПТС、СБКТС、报关单、ОСАГО、车主身份证件，齐备当日发牌。平行进口无原厂质保，由进口商/销售方承担，需提前落实延保、易损件、俄语车机与冬季适配 [S08][S14]。\n")
A("\n## 03 单证清单\n")
A("\n| 环节 | 单证 / 材料 | 办理时点 | 来源 | 等级 |\n|---|---|---|---|---|\n")
for a, b, c, d, e in DOCS:
    A(f"| {a} | {b} | {c} | {d} | {e} |\n")
A("\n## 04 政策时间线（2024 → 2027）\n")
A("\n| 日期 | 内容 | 依据 | 等级 | 备注 |\n|---|---|---|---|---|\n")
for d, t, src, g, note in TIMELINE:
    A(f"| {d} | {t} | {src} | {g} | {note} |\n")
A("\n## 05 收汇、结算与合规筛查\n")
A("- **付款结构**：30% 预付 + 70% 见清关单/提单副本；船发前确认实际到账再放行提单；警惕第三方代付。合同加制裁条款（通道中断可终止、按履约比例结算、30 日内无息退预付款）[S15]。\n")
A("- **结算通道**：优先人民币/卢布本币，走 **CIPS / SPFS / VTB 上海分行**、边境口岸银行；确认开户行对汽车品类受理政策，避开受制裁俄金融机构与涉美通道 [S15]。\n")
A("- **汇率与调价**：卢布 52 周区间 70.79–87.00 RUB/USD；可约定波动超 5% 分担或人民币计价，大额订单做远期结汇/锁汇；报废税每年 1 月调整，2027-01-01 预计再涨 10–20% [S01][S17]。\n")
A("- **主体筛查**：核查俄方公司、股东、最终受益人是否在制裁名单；核对汇款账户与合同主体一致；关注最终用户/用途声明与车机电子件出口管制；俄个人数据本地化要求 [S15]。\n")
A("- **清关节点**：协议写明滞港违约金（如每日货值 0.1%、上限 15%）；绿/黄/红灯机制（5 日正常、5–10 日高层介入、>10 日法律保全与替代物流）[S15]。\n")
A("- **退税前置**：单证与报关单金额匹配、资料逻辑一致，写进发货 SOP [S11]。\n")
A("\n## 06 八个最常见的坑\n")
for t, d, src, g in PITFALLS:
    A(f"**{t}**（{src}，{g} 级）\n\n{d}\n\n")
A("\n## 07 报价前十项检查清单\n")
for i, c in enumerate(CHECKLIST, 1):
    A(f"- [ ] {c}\n")
A("\n## 08 四处口径冲突\n")
A("\n| 冲突点 | 两种记载 | 处理方式 |\n|---|---|---|\n")
for a, b, c in CONFLICTS:
    A(f"| {a} | {b} | {c} |\n")
A("\n## 09 数据来源\n")
A("\n| 编号 | 来源 | 关键内容 | 等级 | 链接 |\n|---|---|---|---|---|\n")
for a, b, c, d, e in SOURCES:
    A(f"| {a} | {b} | {c} | {d} | {e} |\n")
A("\n---\n\n*本页为业务操作指引，不构成法律或税务意见。规则与税率随政策调整，正式交易前请由俄方持牌报关行、中方开户行与法务复核当期要求，尤其涉及 EAEU 转口、认证状态与制裁名单的部分。*\n")
md = "".join(L)
open(os.path.join(SITE, "downloads", "russia-export-rules.md"), "w", encoding="utf-8").write(md)
print("[OK] downloads/russia-export-rules.md", len(md) // 1024, "KB")
