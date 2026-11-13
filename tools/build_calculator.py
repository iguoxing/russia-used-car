# -*- coding: utf-8 -*-
"""生成 quotation.html —— 俄罗斯整车出口报价计算器"""
import os, sys, json, html
sys.path.insert(0, os.path.dirname(__file__))
from rules_data import (PARAMS, FREIGHT_PRESETS, UTIL_COMMERCIAL, UTIL_PERSONAL_NEW,
                        UTIL_PERSONAL_OLD, EXCISE, CUSTOMS_FEE, SOURCES,
                        CONFLICTS, RATE_DATE, ROUTES, VEHICLES)
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = lambda x: html.escape(str(x), quote=True)

# index.html 现已是 Tab 容器，共享样式改从 analysis.html（原总览看板）取
base = open(os.path.join(SITE, "analysis.html"), encoding="utf-8").read()
CSS = base.split("<style>", 1)[1].split("</style>", 1)[0]

EXTRA = r"""
/* ===== 计算器专用 ===== */
.calc{display:grid;grid-template-columns:390px 1fr;gap:18px;align-items:start}
.form-panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;position:sticky;top:64px;max-height:calc(100vh - 84px);overflow-y:auto}
.form-panel::-webkit-scrollbar{width:8px}.form-panel::-webkit-scrollbar-thumb{background:var(--line);border-radius:8px}
.fgroup{border:1px solid var(--line);border-radius:10px;padding:12px 13px;margin-bottom:13px;background:var(--panel2)}
.fgroup h4{margin:0 0 10px;font-size:12.5px;letter-spacing:.06em;color:var(--a1);text-transform:uppercase}
.frow{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:7px 0}
.frow label{font-size:12.5px;color:var(--muted);flex:1;line-height:1.4}
.frow label b{color:var(--text);font-weight:600}
input[type=number],input[type=text],select{background:#0f1a26;border:1px solid var(--line);color:var(--text);border-radius:7px;padding:6px 8px;font-size:12.5px;font-family:inherit;width:118px;text-align:right}
input[type=text]{text-align:left}
select{text-align:left;width:132px}
input[type=number]:focus,select:focus,input[type=text]:focus{outline:none;border-color:var(--a1);box-shadow:0 0 0 2px rgba(77,156,255,.18)}
input[type=checkbox]{accent-color:var(--a1);width:15px;height:15px}
.unit{font-size:11px;color:var(--muted);width:38px;text-align:left}
.frow .hint{font-size:10.5px;color:var(--muted);line-height:1.5;margin:2px 0 6px}
.presets{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.presets button,.btn{border:1px solid var(--line);background:var(--panel2);color:var(--text);border-radius:8px;padding:7px 11px;font-size:12px;cursor:pointer;font-family:inherit}
.presets button:hover,.btn:hover{border-color:var(--a1);color:var(--a1)}
.btn.pri{background:rgba(77,156,255,.18);border-color:var(--a1);color:#9ec8ff;font-weight:700;width:100%;padding:11px;font-size:14px;margin-top:4px}
.btn.ok{background:rgba(52,201,161,.15);border-color:var(--a2);color:#71e3c1}
.btn-row{display:grid;grid-template-columns:repeat(2,1fr);gap:7px;margin-top:9px}
.result-panel{min-width:0}
.kpis4{display:grid;grid-template-columns:repeat(4,1fr);gap:11px;margin-bottom:15px}
.kpi.big .kpi-v{font-size:26px}
.kpi.hl{background:linear-gradient(135deg,rgba(77,156,255,.16),rgba(77,156,255,.03));border-color:rgba(77,156,255,.4)}
.kpi.hl2{background:linear-gradient(135deg,rgba(52,201,161,.15),rgba(52,201,161,.03));border-color:rgba(52,201,161,.4)}
.kpi.warn{background:linear-gradient(135deg,rgba(235,105,80,.15),rgba(235,105,80,.03));border-color:rgba(235,105,80,.4)}
.stack{display:flex;width:100%;height:42px;border-radius:8px;overflow:hidden;border:1px solid var(--line);margin:6px 0 12px}
.stack div{height:100%;min-width:1px;transition:width .3s}
.legend{display:flex;flex-wrap:wrap;gap:9px 16px;font-size:12px;color:var(--muted);margin-bottom:6px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.legend b{color:var(--text);font-weight:600}
.tbl-scroll table{font-size:12.5px}
.tbl-scroll td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.tbl-scroll tr.sum td{background:rgba(77,156,255,.10);font-weight:700;color:#9ec8ff}
.tbl-scroll tr.buyer td{color:var(--muted);opacity:.72}
.tbl-scroll tr.active td{background:rgba(52,201,161,.10)}
.tag{font-size:10.5px;padding:2px 8px;border-radius:12px;border:1px solid var(--line);color:var(--muted);white-space:nowrap}
.tag.a{background:rgba(52,201,161,.14);color:#71e3c1;border-color:rgba(52,201,161,.4)}
.tag.c{background:rgba(245,170,60,.14);color:#f7c274;border-color:rgba(245,170,60,.4)}
.notice{font-size:12.5px;color:var(--muted);line-height:1.7;margin-top:10px}
.notice b{color:var(--a3)}
.quote-box{background:#0f1a26;border:1px solid var(--line);border-radius:9px;padding:13px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;white-space:pre-wrap;color:var(--text);max-height:340px;overflow:auto;margin-top:10px;line-height:1.65}
.cols2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
input.ro{background:#101b27!important;color:var(--muted)!important}
/* ===== 显示币种切换 ===== */
.curbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px 13px;margin-bottom:14px}
.curbar .lab{font-size:12.5px;color:var(--muted);font-weight:600;margin-right:2px}
.curbar button{border:1px solid var(--line);background:var(--panel2);color:var(--muted);border-radius:8px;padding:6px 13px;font-size:12.5px;font-weight:600;cursor:pointer;font-family:inherit}
.curbar button:hover{border-color:var(--a1);color:var(--a1)}
.curbar button.on{background:rgba(77,156,255,.18);border-color:var(--a1);color:#9ec8ff}
.curbar .rate{margin-left:auto;font-size:11.5px;color:var(--muted);line-height:1.5}
.curbar .cap{width:100%;margin:0;font-size:11.5px;color:var(--muted)}
.curbar .cap b{color:var(--a1)}
select:disabled{opacity:.72;cursor:not-allowed}
[data-amt]{font-variant-numeric:tabular-nums}
nav .wrap{flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;scrollbar-width:thin}
nav .wrap::-webkit-scrollbar{height:5px}
nav .wrap::-webkit-scrollbar-thumb{background:var(--line);border-radius:5px}
nav .wrap a,nav .psep{flex:0 0 auto}
@media(max-width:760px){.curbar .rate{margin-left:0}}
@media print{.curbar button,.curbar .lab,.curbar .cap{display:none}}
@media(max-width:1000px){.calc{grid-template-columns:1fr}.form-panel{position:static;max-height:none}.kpis4{grid-template-columns:repeat(2,1fr)}.cols2{grid-template-columns:1fr}}
@media(max-width:820px){.kpis4{grid-template-columns:repeat(2,1fr)}}
@media print{
 body{background:#fff!important;color:#16202c!important}
 :root{--text:#16202c;--muted:#475569;--panel:#fff;--panel2:#f7fafc;--line:#cbd5e1}
 nav,.form-panel,.presets,.btn,.btn-row,#exports,.ptabs{display:none!important}
 .calc{display:block!important}
 .result-panel{width:100%}
 .card,.kpi,.chartbox{background:#fff!important;border-color:#cbd5e1!important;color:#16202c!important}
 .kpi-v,.kpi-l,.kpi-s,section h2,h1,h3,h4,.lead,.cap,td,th,p,li,footer{color:#16202c!important}
 .kpi.hl,.kpi.hl2,.kpi.warn{background:#fff!important}
 th{background:#e8eef5!important;color:#16202c!important}
 .stack{border-color:#cbd5e1}
 .tbl-scroll{overflow:visible!important}
 table{table-layout:auto!important}
 th,td{padding:5px 7px!important;font-size:10.5px!important;white-space:normal!important}
 .card,.chartbox{page-break-inside:avoid}
 section{margin:18px 0}
 html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
}
/* ===== 利润 / 方案 / 口岸 / 车型 模块 ===== */
.mrow{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0}
.mini{border:1px solid var(--line);background:var(--panel2);color:var(--text);border-radius:6px;padding:4px 9px;font-size:11.5px;cursor:pointer;font-family:inherit;white-space:nowrap}
.mini:hover{border-color:var(--a1);color:var(--a1)}
.mini.on{background:rgba(77,156,255,.18);border-color:var(--a1);color:#9ec8ff}
.tbl-scroll td.mid{text-align:center}
.planbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:10px}
.planbar .grow{flex:1;min-width:170px}
.hintbox{font-size:12px;color:var(--muted);line-height:1.7;background:var(--panel2);border:1px solid var(--line);border-radius:9px;padding:10px 12px;margin:10px 0}
.hintbox b{color:var(--a3)}
.rowsel td{background:rgba(52,201,161,.10)}
@media print{.planbar,.mrow,.mini,#routeMsg,#vehicleMsg{display:none!important}}
"""


def nav(active):
    pages = [("index", "index.html", "总览看板"),
             ("segments", "segments.html", "细分市场 · 6 大赛道"),
             ("quotation", "quotation.html", "报价计算器"),
             ("rules", "rules.html", "出口规则说明")]
    p = "".join('<a class="ptab' + (' on' if k == active else '') + '" href="' + u + '">' + E(t) + '</a>'
                for k, u, t in pages)
    anchors = [("#top", "概览"), ("#calc", "报价计算器"), ("#stages", "成本阶梯"),
               ("#terms", "多口径报价"), ("#profit", "利润保本"), ("#plans", "方案对比"),
               ("#scenes", "情景敏感"), ("#params", "参数来源"), ("#routes", "口岸运费"),
               ("#vehicles", "车型库"), ("#conflicts", "口径冲突"),
               ("#how", "计算公式"), ("#downloads", "配套下载")]
    return '<nav><div class="wrap">' + p + '<span class="psep"></span>' + \
           "".join('<a href="%s">%s</a>' % (u, t) for u, t in anchors) + '</div></nav>'


def frow(id_, label, val, unit="", hint="", typ="number", step="any", ro=False,
         money=None, hint_raw=False):
    roattr = ' readonly class="ro"' if ro else ''
    mattr = ' data-money="%s"' % money if money else ''
    inp = ('<input type="%s" id="%s" value="%s" step="%s"%s%s data-k="%s">'
           % (typ, id_, E(val), step, roattr, mattr, id_))
    h = '<div class="hint">%s</div>' % (hint if hint_raw else E(hint)) if hint else ""
    return ('<div class="frow"><label for="%s">%s</label>%s<span class="unit" data-u="%s">%s</span></div>%s'
            % (id_, label, inp, id_, E(unit), h))


def sel(id_, label, options, selected=""):
    opts = "".join('<option value="%s"%s>%s</option>' % (E(v), ' selected' if v == selected else "", E(t))
                   for v, t in options)
    return '<div class="frow"><label for="%s">%s</label><select id="%s" data-k="%s">%s</select></div>' % (
        id_, label, id_, id_, opts)


def check(id_, label, checked=False):
    return ('<div class="frow"><label for="%s">%s</label><input type="checkbox" id="%s"%s data-k="%s"></div>'
            % (id_, label, id_, ' checked' if checked else '', id_))


FORM = r"""
<div class="form-panel">
 <div class="presets">
  <button data-preset="base">主流 1.5L / 150hp</button>
  <button data-preset="power">2.0T / 200hp（超功率）</button>
  <button data-preset="bev">纯电 SUV</button>
  <button data-preset="used">二手车 3 年+</button>
 </div>

 <div class="fgroup"><h4>A · 车辆与进口主体</h4>
  {sel_vehicle}
  <div class="frow"><label>参考 HS 子目<br>（带入车型后显示）</label><input type="text" id="vehicleHs" value="—" readonly class="ro" style="width:118px"></div>
  <div class="frow"><label for="model"><b>车型 / 配置描述</b></label><input type="text" id="model" value="中国产 SUV 1.5T / 150hp" data-k="model"></div>
  {sel_priceCcy}
  {f_price}
  {f_cnyUsd}
  {f_qty}
  {sel_importer}
  {sel_age}
  {sel_engine}
  {f_disp}
  {f_power}
  <div class="frow"><label for="utilNote">当前报废税系数<br>（自动查表，可覆盖）</label><input type="number" id="utilCoefManual" value="12.95" step="0.01" data-k="utilCoefManual"><span class="unit">×</span></div>
  {check_utilAuto}
  <div class="hint" id="coefHint">个人自用需同时满足 ≤3 年 / ≤3.0L / ≤160hp；功率过线即转商业系数。</div>
 </div>

 <div class="fgroup"><h4>B · 贸易条款与物流</h4>
  {sel_term}
  {sel_freightPreset}
  {f_freight}
  {f_insRate}
  {f_exportLocal}
  {f_usdRub}
  {f_customsAdj}
 </div>

 <div class="fgroup"><h4>C · 俄方税费参数</h4>
  {sel_dutyPreset}
  {f_dutyRate}
  {sel_vatPreset}
  {f_vatRate}
  {f_utilBase}
  {f_exciseManual}
  {check_exciseAuto}
  {f_customsFeeManual}
  {check_feeAuto}
  <div class="hint">消费税按马力阶梯 ≤90 免 / ≤150 63 / ≤200 610 / ≤300 1,000 / ≤400 1,036 / &gt;400 1,128 RUB 每马力（边界按上界闭合）；纯电默认 0，如俄方按电机功率核定请取消自动并手填总额。</div>
 </div>

 <div class="fgroup"><h4>D · 落地费用与利润</h4>
  {f_sbkts}
  {f_era}
  {f_broker}
  {f_inland}
  {f_pdi}
  {f_warrantyRate}
  {f_otherFee}
  {f_margin}
  {sel_marginMode}
  {f_refundRate}
  {check_refundOn}
 </div>
 <div class="fgroup"><h4>E · 成交与利润（内部测算）</h4>
  {f_targetPrice}
  {f_commissionRate}
  {f_sellFee}
  <div class="hint">这三项只影响内部净利与保本价，<b>不会写进对客报价单</b>。目标成交价填 0 = 按建议报价成交。</div>
 </div>
 <button class="btn pri" id="btnCalc">重新计算 →</button>
 <div class="btn-row">
  <button class="btn" id="btnSave">保存参数</button>
  <button class="btn" id="btnReset">恢复默认</button>
 </div>
 <div class="notice" id="saveMsg"></div>
</div>
"""

FORM = FORM.format(
    sel_vehicle=sel("vehiclePick", "<b>车型库一键带入</b>",
                   [("", "— 手动填参数 —")] + [(v[0], v[1] + " " + v[2]) for v in VEHICLES], ""),
    sel_priceCcy=('<div class="frow"><label for="priceCcy">车价币种</label>'
                  '<select id="priceCcy" data-k="priceCcy" disabled>'
                  '<option value="RUB">跟随全局 · RUB</option>'
                  '<option value="USD">跟随全局 · USD</option>'
                  '<option value="CNY">跟随全局 · CNY</option>'
                  '</select></div>'),
    f_price=frow("price", "<b>单台车价（含税）</b>", "128000", "CNY",
                 "二手车以收购发票价为准；数值随上方全局计价币种自动折算", money="CNY"),
    f_cnyUsd=frow("cnyUsd", "CNY / USD 汇率", "6.70", "", "由俄央行 2026-11-12 交叉价推算，请按实际结汇价改"),
    f_qty=frow("qty", "数量", "1", "台"),
    sel_importer=sel("importer", "进口主体", [("company", "法人 · 商业进口"), ("personal", "个人 · 自用（限 1 辆/年）")], "company"),
    sel_age=sel("age", "车龄", [("new", "≤3 年 / 新车"), ("old", ">3 年 / 二手车")], "new"),
    sel_engine=sel("engine", "动力类型", [("ice", "汽油 / 柴油"), ("hybrid", "混动 / 增程"), ("bev", "纯电")], "ice"),
    f_disp=frow("disp", "排量", "1500", "cc", "纯电填 0"),
    f_power=frow("power", "功率", "150", "hp", "160hp 是报废税资格线，不是加价线"),
    check_utilAuto=check("utilCoefAuto", "自动查表选系数", True),
    sel_term=sel("term", "<b>贸易术语 / 报价口径</b>", [("EXW", "EXW 工厂交货"), ("FOB", "FOB 装运港"), ("CIF", "CIF 到岸"), ("DDP", "DDP 完税落地")], "CIF"),
    sel_freightPreset=sel("freightPreset", "运输方式预设", [(k, t) for k, t, _, _ in FREIGHT_PRESETS], "rail"),
    f_freight=frow("freight", "国际运费（单台）", "4000", "USD", money="USD"),
    f_insRate=frow("insRate", "保险费率", "0.30", "%"),
    f_exportLocal=frow("exportLocal", "中国出口本地费", "300", "USD", money="USD"),
    f_usdRub=frow("usdRub", "<b>USD / RUB 汇率</b>", "82.98", "", "俄央行 2026-11-13 官方 82.9803"),
    f_customsAdj=frow("customsAdj", "海关估价调整", "0", "%", "低报会被重新核价并罚款"),
    sel_dutyPreset=sel("dutyPreset", "关税快速预设", [("15", "15% 从价"), ("20", "20%（默认）"), ("25", "25%"), ("30", "30%"), ("38", "38% 上限")], "20"),
    f_dutyRate=frow("dutyRate", "进口关税", "20", "%"),
    sel_vatPreset=sel("vatPreset", "增值税口径", [("20", "20%（旧口径）"), ("22", "22%（425-ФЗ）")], "22"),
    f_vatRate=frow("vatRate", "增值税 НДС", "22", "%"),
    f_utilBase=frow("utilBase", "报废税基准", "20000", "RUB",
                    '乘用车 <span data-amt="20000" data-from="RUB">20,000 ₽</span>；'
                    '卡车/客车/挂车 <span data-amt="150000" data-from="RUB">150,000 ₽</span>',
                    money="RUB", hint_raw=True),
    f_exciseManual=frow("exciseManual", "消费税总额（手填）", "0", "RUB", money="RUB"),
    check_exciseAuto=check("exciseAuto", "按马力阶梯自动算消费税", True),
    f_customsFeeManual=frow("customsFeeManual", "清关手续费（手填）", "13541", "RUB", money="RUB"),
    check_feeAuto=check("customsFeeAuto", "按 2026 分档自动算", True),
    f_sbkts=frow("sbkts", "СБКТС / ОТТС 认证", "40000", "RUB", money="RUB"),
    f_era=frow("era", "ЭРА-ГЛОНАСС 加装", "0", "RUB", money="RUB"),
    f_broker=frow("broker", "报关代理 + 装卸", "40000", "RUB", money="RUB"),
    f_inland=frow("inland", "俄境内运输", "0", "RUB",
                  'DDP 才计入；海参崴→莫斯科 <span data-amt="150000" data-from="RUB">150,000 ₽</span>–'
                  '<span data-amt="250000" data-from="RUB">250,000 ₽</span>',
                  money="RUB", hint_raw=True),
    f_pdi=frow("pdi", "PDI / 整备 / 仓储", "15000", "RUB", money="RUB"),
    f_warrantyRate=frow("warrantyRate", "质保售后准备金", "2.0", "% 车价"),
    f_otherFee=frow("otherFee", "其他杂费", "0", "RUB", money="RUB"),
    f_margin=frow("margin", "<b>目标毛利 / 加成</b>", "12", "%"),
    sel_marginMode=sel("marginMode", "利润算法", [("gross", "毛利率法 成本÷(1−r)"), ("markup", "加成法 成本×(1+r)")], "gross"),
    f_refundRate=frow("refundRate", "中国出口退税", "13", "%", "计入我方收益，不影响对客报价"),
    check_refundOn=check("refundOn", "计入退税收益", True),
    f_targetPrice=frow("targetPrice", "<b>目标成交价（实收）</b>", "0", "RUB",
                      "填 0 = 按建议报价成交；填客户还价可反算净利与降价空间", money="RUB"),
    f_commissionRate=frow("commissionRate", "佣金 / 渠道返利", "3", "%"),
    f_sellFee=frow("sellFee", "单台销售费用", "0", "RUB", money="RUB"),
)

# 参数来源表
def amt_default(val, unit, name):
    """金额型默认值包一层动态标记；汇率那两行是无量纲比率，不参与换算。"""
    if "汇率" in name:
        return E(val)
    try:
        x = float(str(val).replace(",", ""))
    except (TypeError, ValueError):
        return E(val)
    if unit not in ("RUB", "CNY", "USD"):
        return E(val)
    return '<span data-amt="%s" data-from="%s">%s %s</span>' % (x, unit, E(val), E(unit))


param_rows = "".join(
    "<tr><td><b>%s</b></td><td class=\"num\">%s</td><td>%s</td><td><span class=\"tag %s\">%s</span></td><td>%s</td><td>%s</td></tr>"
    % (E(a), amt_default(b, c, a), E(c), "a" if d.startswith("A") else "c" if d.startswith("C") else "",
       E(d), E(e), E(f))
    for a, b, c, d, e, f in PARAMS)
src_rows = "".join(
    "<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td><span class=\"tag %s\">%s</span></td><td><a href=\"%s\" target=\"_blank\" rel=\"noopener\">链接</a></td></tr>"
    % (E(a), E(b), E(c), "a" if d.startswith("A") else "c" if d.startswith("C") else "", E(d), E(e))
    for a, b, c, d, e in SOURCES)
conf_rows = "".join(
    "<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>" % (E(a), E(b), E(c))
    for a, b, c in CONFLICTS)
freight_rows = "".join(
    "<tr><td><b>%s</b></td><td class=\"num\"><span data-amt=\"%s\" data-from=\"USD\">$%s</span></td><td>%s</td></tr>"
    % (E(t), v, f"{v:,}", E(n))
    for _, t, v, n in FREIGHT_PRESETS)
util_rows = "".join(
    "<tr><td><b>%s</b></td><td class=\"num\">%.2f</td><td class=\"num\">%.2f</td>"
    "<td class=\"num\"><span data-amt=\"%d\" data-from=\"RUB\">%s ₽</span></td>"
    "<td class=\"num\"><span data-amt=\"%d\" data-from=\"RUB\">%s ₽</span></td></tr>"
    % (E(n), a, b, int(20000*a), f"{int(20000*a):,}", int(20000*b), f"{int(20000*b):,}")
    for _, _, a, b, n in UTIL_COMMERCIAL)

route_rows = "".join(
    '<tr><td><b>%s</b><div class="cap">%s ｜ %s</div></td>'
    '<td class="num"><span data-amt="%d" data-from="USD">$%s</span></td>'
    '<td class="num">%s</td>'
    '<td class="num"><span data-amt="%d" data-from="RUB" data-zero="—">%s</span></td>'
    '<td class="mid"><button class="mini" data-route="%s" type="button">应用</button></td>'
    '<td class="mid"><span class="tag %s">%s</span></td>'
    '<td>%s<div class="cap">来源 %s</div></td></tr>'
    % (E(r[1]), E(r[2]), E(r[3]), r[4], f"{r[4]:,}", E(r[5]),
       r[6], (f"{r[6]:,} ₽" if r[6] else "—"), r[0],
       "a" if r[9].startswith("B") and "/" not in r[9] else "c", E(r[9]),
       E(r[8]), E(r[10]))
    for r in ROUTES)
vehicle_rows = "".join(
    '<tr><td><b>%s</b><div class="cap">%s ｜ %s kg</div></td>'
    '<td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>'
    '<td class="mid">%s</td><td class="mid">%s</td>'
    '<td class="num"><span data-amt="%d" data-from="CNY">¥%s</span></td>'
    '<td class="mid"><button class="mini" data-vehicle="%s" type="button">带入</button></td>'
    '<td class="mid"><span class="tag %s">%s</span></td></tr>'
    % (E(v[2]), E(v[1]), f"{v[9]:,}",
       f"{v[4]:,} cc", f"{v[5]} hp", {"ice": "燃油", "hybrid": "插混", "bev": "纯电"}[v[3]],
       "≤3 年" if v[6] == "new" else ">3 年", E(v[7]),
       v[8], f"{v[8]:,}", v[0],
       "a" if v[11].startswith("B") and "/" not in v[11] else "c", E(v[11]))
    for v in VEHICLES)
ROUTES_JS = "var ROUTES=" + json.dumps(
    {r[0]: {"usd": r[4], "inland": r[6], "preset": r[7], "name": r[1], "days": r[5]}
     for r in ROUTES}, ensure_ascii=False) + ";"
VEHICLES_JS = "var VEHICLES=" + json.dumps(
    {v[0]: {"price": v[8], "disp": v[4], "power": v[5], "engine": v[3],
            "age": v[6], "hs": v[7], "name": v[1] + " " + v[2]}
     for v in VEHICLES}, ensure_ascii=False) + ";"

DL = [
    ("russia-quotation-calculator.xlsx", "报价计算器 Excel 模板", "带公式，参数可迭代（新增）"),
    ("russia-export-rules.pdf", "基本出口规则说明 PDF", "中俄两侧流程与单证（新增）"),
    ("russia-export-rules.md", "基本出口规则说明 Markdown", "便于二次编辑（新增）"),
    ("russia-parallel-import-report.pdf", "主报告 PDF（17 页）", "四维 + 核验 + 维度优化"),
    ("russia-top100-clients.xlsx", "TOP100 客户 Excel", "8 个工作表"),
    ("russia-segment-analysis.pdf", "细分市场分析 PDF", "6 大赛道机会图谱"),
    ("russia-segment-analysis.xlsx", "细分市场数据表 Excel", "5 个工作表"),
]
dls = "".join(
    '<a href="downloads/%s" style="display:block;padding:11px 14px;margin:8px 0;border:1px solid var(--line);'
    'border-radius:10px;background:var(--panel2);color:var(--text);text-decoration:none">'
    '<b>%s</b> <span style="color:var(--muted);font-size:12px">— %s</span></a>' % (f, E(t), E(d))
    for f, t, d in DL)

JS = r"""
<script>
(function(){
"use strict";
var $=function(id){return document.getElementById(id)};
var N=function(id){var e=$(id);if(!e)return 0;var v=parseFloat(e.value);return isNaN(v)?0:v};
var C=function(id){var e=$(id);return e?e.checked:false};
var S=function(id){var e=$(id);return e?e.value:""};
var fmt=function(n){return (Math.round(n||0)).toLocaleString("ru-RU")};
var f2=function(n){return (n||0).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2})};
/* ===== 显示币种层：内部一切金额仍以 RUB 计算，这里只做展示换算 ===== */
var CUR="RUB",CV=null;
var CUR_INFO={RUB:{s:"₽",tag:"RUB",name:"卢布",loc:"ru-RU"},
              USD:{s:"$",tag:"USD",name:"美元",loc:"en-US"},
              CNY:{s:"¥",tag:"CNY",name:"人民币",loc:"zh-CN"}};
var sym=function(){return CUR_INFO[CUR].s};
var ctag=function(){return CUR_INFO[CUR].tag};
var toCur=function(n,v){
  var vv=v||CV||{usdRub:82.98,cnyUsd:6.70};
  var r=vv.usdRub||82.98,c=vv.cnyUsd||6.70;
  if(CUR==="USD")return (n||0)/r;
  if(CUR==="CNY")return (n||0)*c/r;
  return n||0;
};
var money=function(n,v){
  var x=toCur(n,v),d=CUR==="RUB"?0:2;
  return x.toLocaleString(CUR_INFO[CUR].loc,{minimumFractionDigits:d,maximumFractionDigits:d});
};
var moneyS=function(n,v){return CUR==="RUB" ? money(n,v)+" ₽" : sym()+money(n,v)};
var altStr=function(n,v){
  var vv=v||CV||{usdRub:82.98,cnyUsd:6.70};
  if(CUR==="USD")return "≈ "+fmt(n)+" ₽";
  return "≈ $"+f2((n||0)/(vv.usdRub||82.98));
};
var refCur=function(n,v){
  var vv=v||CV||{usdRub:82.98,cnyUsd:6.70};
  return CUR==="RUB" ? "$"+f2((n||0)/(vv.usdRub||82.98)) : fmt(n)+" ₽";
};
/* ===== 全站计价币种：每个金额字段各有一个「锚定币种」 =====
   price 锚 CNY（中国采购）、freight/exportLocal 锚 USD（国际物流）、
   其余俄方费用锚 RUB（法规/本地服务）。BASE[k] 存锚定币种的金额，
   输入框与所有结果只是它按当前汇率的投影，切换币种不改变锚定值。 */
var MONEY={
 price:{base:"CNY",native:"RUB"},
 freight:{base:"USD",native:"USD"},
 exportLocal:{base:"USD",native:"USD"},
 utilBase:{base:"RUB",native:"RUB"},
 exciseManual:{base:"RUB",native:"RUB"},
 customsFeeManual:{base:"RUB",native:"RUB"},
 sbkts:{base:"RUB",native:"RUB"},
 era:{base:"RUB",native:"RUB"},
 broker:{base:"RUB",native:"RUB"},
 inland:{base:"RUB",native:"RUB"},
 pdi:{base:"RUB",native:"RUB"},
 otherFee:{base:"RUB",native:"RUB"},
 targetPrice:{base:"RUB",native:"RUB"},
 sellFee:{base:"RUB",native:"RUB"}
};
var MK=Object.keys(MONEY),BASE={};
function ratesOf(over){
 var ue=$("usdRub"),ce=$("cnyUsd");
 var r=ue?(parseFloat(ue.value)||82.98):82.98;
 var c=ce?(parseFloat(ce.value)||6.70):6.70;
 if(over){if(over.usdRub)r=over.usdRub;if(over.cnyUsd)c=over.cnyUsd}
 return {usdRub:r,cnyUsd:c};
}
function rubPer(ccy,v){
 if(ccy==="USD")return v.usdRub;
 if(ccy==="CNY")return v.usdRub/v.cnyUsd;
 return 1;
}
function conv(x,from,to,v){return (x||0)*rubPer(from,v)/rubPer(to,v)}
function putNum(x){
 var s=(x||0).toFixed(2);
 if(s.slice(-3)===".00")s=s.slice(0,-3);
 return s;
}
function dispAmt(x,from,v){
 var y=conv(x,from,CUR,v),d=CUR==="RUB"?0:2;
 return (CUR==="RUB"?"":sym())+Number(y).toLocaleString(CUR_INFO[CUR].loc,{minimumFractionDigits:d,maximumFractionDigits:d})+(CUR==="RUB"?" "+sym():"");
}
function initBase(){MK.forEach(function(k){var e=$(k);BASE[k]=e?(parseFloat(e.value)||0):0})}
function syncFromInput(k){
 if(!MONEY[k])return;var e=$(k);if(!e)return;
 BASE[k]=conv(parseFloat(e.value)||0,CUR,MONEY[k].base,ratesOf());
 e.setAttribute("data-proj",e.value);
}
function projectAll(){
 var v=ratesOf();
 MK.forEach(function(k){
  var e=$(k);if(!e)return;
  var s=putNum(conv(BASE[k]||0,MONEY[k].base,CUR,v));
  e.value=s;e.setAttribute("data-proj",s);
  var u=document.querySelector('[data-u="'+k+'"]');if(u)u.textContent=ctag();
 });
 var pc=$("priceCcy");if(pc)pc.value=CUR;
}
function applyStaticCurrency(){
 var v=ratesOf();
 document.querySelectorAll("[data-amt][data-from]").forEach(function(s){
  var amt=parseFloat(s.getAttribute("data-amt"))||0;
  if(amt===0&&s.hasAttribute("data-zero")){s.textContent=s.getAttribute("data-zero");return}
  s.textContent=dispAmt(amt,s.getAttribute("data-from"),v);
 });
 document.querySelectorAll("[data-thccy]").forEach(function(s){s.textContent=ctag()});
}
var esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})};
var COLORS={car:"#4d9cff",local:"#7c8fb0",freight:"#34c9a1",adj:"#aa84f7",duty:"#f5aa3c",
            excise:"#e9784f",vat:"#eb6950",util:"#d94f6a",fee:"#8fa3b8",svc:"#5bc0be"};

var PRESETS={
 base:{price:128000,disp:1500,power:150,engine:"ice",age:"new",importer:"company",model:"中国产 SUV 1.5T / 150hp"},
 power:{price:238000,disp:2000,power:200,engine:"ice",age:"new",importer:"company",model:"中国产 2.0T 中大型 SUV / 200hp"},
 bev:{price:168000,disp:0,power:204,engine:"bev",age:"new",importer:"company",model:"中国产纯电 SUV / 150kW"},
 used:{price:86000,disp:1800,power:150,engine:"ice",age:"old",importer:"company",model:"3 年车龄二手 SUV / 150hp"}
};
var FREIGHT={sea:2500,rail:4000,truck:1200,container:3000};
var EXCISE=[[0,90,0],[90,150,63],[150,200,610],[200,300,1000],[300,400,1036],[400,1e9,1128]];
/* 阶梯边界公开资料写法含糊，本工具按「上界闭合」处理：≤150hp 归 63 档，>150 归 610 档。
   若报关行按其他口径核定，请取消自动并手填消费税总额。 */
var FEE=[[200000,1231],[450000,2462],[1200000,4924],[2700000,13541],[4200000,18465],[5500000,21344],[10000000,49240],[1e15,73860]];
var UTIL=[[0,1000,8.92,20.70],[1000,2000,12.95,33.84],[2000,3000,27.51,84.01],[3000,1e9,137,137]];

function excisePerHp(hp){if(hp<=90)return 0;if(hp<=150)return 63;if(hp<=200)return 610;
  if(hp<=300)return 1000;if(hp<=400)return 1036;return 1128}
function feeBand(v){for(var i=0;i<FEE.length;i++){if(v<=FEE[i][0])return FEE[i][1]}return 73860}
function utilAuto(disp,age,power,importer){
  if(importer==="personal"&&disp<=3000&&power<=160) return {c:(age==="new"?0.17:0.26),personal:true,note:"个人自用优惠档（需同时满足 ≤3 年 / ≤3.0L / ≤160hp / 一年 1 辆）"};
  for(var i=0;i<UTIL.length;i++){if(disp>=UTIL[i][0]&&disp<UTIL[i][1])
    return {c:(age==="new"?UTIL[i][2]:UTIL[i][3]),personal:false,note:"商业系数 · "+(age==="new"?"≤3 年":">3 年")+" · 按排量档查表（S05）"}}
  return {c:137,personal:false,note:"排量超表，取 137+ 下限"};
}
function readV(over){
  var v={},rt=ratesOf(over);
  ["cnyUsd","qty","disp","power","utilCoefManual","insRate","usdRub","customsAdj",
   "dutyRate","vatRate","warrantyRate","margin","refundRate","commissionRate"].forEach(function(k){v[k]=N(k)});
  v.usdRub=rt.usdRub;v.cnyUsd=rt.cnyUsd;
  MK.forEach(function(k){v[k]=conv(BASE[k]||0,MONEY[k].base,MONEY[k].native,v)});
  ["priceCcy","importer","age","engine","term","marginMode","freightPreset","dutyPreset","vatPreset"].forEach(function(k){v[k]=S(k)});
  ["utilCoefAuto","exciseAuto","customsFeeAuto","refundOn"].forEach(function(k){v[k]=C(k)});
  v.model=S("model");
  v.utilCoefScale=1;
  if(over)for(var k in over)v[k]=over[k];
  return v;
}
function compute(v){
  var priceUSD = v.price/v.usdRub;          /* v.price 已归一化为 RUB */
  var priceCNY = priceUSD*v.cnyUsd;
  var r = v.usdRub;
  var insurance = (priceUSD+v.exportLocal+v.freight)*v.insRate/100;
  var carRUB=priceUSD*r, localRUB=v.exportLocal*r, frtRUB=(v.freight+insurance)*r;
  var cifRUB=carRUB+localRUB+frtRUB;
  var adjRUB=cifRUB*v.customsAdj/100;
  var declared=cifRUB+adjRUB;
  var duty=declared*v.dutyRate/100;
  var excise = v.exciseAuto ? (v.engine==="bev"?0:v.power*excisePerHp(v.power)) : v.exciseManual;
  var vat=(declared+duty+excise)*v.vatRate/100;
  var ua=utilAuto(v.disp,v.age,v.power,v.importer);
  var uc = (v.utilCoefAuto ? ua.c : v.utilCoefManual) * v.utilCoefScale;
  var util=v.utilBase*uc;
  var cfee = v.customsFeeAuto ? feeBand(declared) : v.customsFeeManual;
  var warranty=carRUB*v.warrantyRate/100;
  var svc=v.sbkts+v.era+v.broker+v.inland+v.pdi+warranty+v.otherFee;
  var landed=declared+duty+excise+vat+util+cfee+svc;
  var stages=[
   {k:"EXW",n:"车价（EXW）",v:carRUB,c:COLORS.car},
   {k:"FOB",n:"中国出口本地费",v:localRUB,c:COLORS.local},
   {k:"CIF",n:"国际运费 + 保险",v:frtRUB,c:COLORS.freight},
   {k:"CUS",n:"海关估价调整",v:adjRUB,c:COLORS.adj},
   {k:"CUS",n:"进口关税 "+f2(v.dutyRate)+"%",v:duty,c:COLORS.duty},
   {k:"CUS",n:"消费税",v:excise,c:COLORS.excise},
   {k:"CUS",n:"增值税 НДС "+f2(v.vatRate)+"%",v:vat,c:COLORS.vat},
   {k:"CUS",n:"报废税（系数 "+f2(uc)+"）",v:util,c:COLORS.util},
   {k:"CUS",n:"清关手续费",v:cfee,c:COLORS.fee},
   {k:"DDP",n:"认证 / 代理 / 内陆 / PDI / 质保",v:svc,c:COLORS.svc}
  ];
  var cum={EXW:carRUB,FOB:carRUB+localRUB,CIF:cifRUB,DDP:landed};
  var factor = v.marginMode==="gross" ? 1/(1-v.margin/100) : (1+v.margin/100);
  var quoteBase=cum[v.term]||cifRUB;
  var quote=quoteBase*factor;
  var buyerCost=landed-quoteBase;
  var refund = v.refundOn ? (priceCNY/1.13*(v.refundRate/100))/v.cnyUsd*r : 0;
  var netCost=quoteBase-refund;
  var grossProfit=quote-netCost;
  /* ===== 内部利润层：不改动上面任何成本 / 报价结果 ===== */
  var sellPrice = v.targetPrice>0 ? v.targetPrice : quote;
  var commission = sellPrice*v.commissionRate/100;
  var netRevenue = sellPrice-commission-v.sellFee;
  var netProfit = netRevenue-netCost;
  var netMargin = sellPrice>0 ? netProfit/sellPrice*100 : 0;
  var cm = Math.max(0,v.commissionRate)/100;
  var breakEven = cm<1 ? (netCost+v.sellFee)/(1-cm) : 0;      /* 净利 = 0 的成交价 */
  var priceRoom = sellPrice-breakEven;
  var roomPct = sellPrice>0 ? priceRoom/sellPrice*100 : 0;
  var floorDenom = 1-cm-v.margin/100;
  var targetFloor = floorDenom>0 ? (netCost+v.sellFee)/floorDenom : 0;  /* 净利率达目标所需最低成交价 */
  return {v:v,priceUSD:priceUSD,priceCNY:priceCNY,insurance:insurance,carRUB:carRUB,localRUB:localRUB,
    frtRUB:frtRUB,cifRUB:cifRUB,adjRUB:adjRUB,declared:declared,duty:duty,excise:excise,vat:vat,
    util:util,uc:uc,ua:ua,cfee:cfee,warranty:warranty,svc:svc,landed:landed,stages:stages,cum:cum,
    factor:factor,quoteBase:quoteBase,quote:quote,buyerCost:buyerCost,refund:refund,netCost:netCost,
    grossProfit:grossProfit,grossMargin:quote>0?grossProfit/quote*100:0,
    taxTotal:duty+excise+vat+util+cfee,
    sellPrice:sellPrice,commission:commission,netRevenue:netRevenue,netProfit:netProfit,
    netMargin:netMargin,breakEven:breakEven,priceRoom:priceRoom,roomPct:roomPct,
    targetFloor:targetFloor,floorDenom:floorDenom};
}
function rowsTable(head,rows,cls){
  return '<div class="tbl-scroll '+cls+'"><table><thead><tr>'+head.map(function(h){return "<th>"+h+"</th>"}).join("")+
    '</tr></thead><tbody>'+rows.join("")+'</tbody></table></div>';
}
function render(x){
  var v=x.v;CV=v;updateRate();applyStaticCurrency();
  // KPI
  var kp=[["DDP 完税落地成本",moneyS(x.landed,v),altStr(x.landed,v),"hl"],
    ["对客报价 · "+v.term,moneyS(x.quote,v),altStr(x.quote,v),"hl2"],
    ["我方单台毛利",moneyS(x.grossProfit,v),"含退税 "+moneyS(x.refund,v),""],
    ["税费占落地成本",(x.landed>0?(x.taxTotal/x.landed*100).toFixed(1):"0")+"%","俄方税费共 "+moneyS(x.taxTotal,v),"warn"]];
  $("kpis").innerHTML=kp.map(function(a){return '<div class="kpi big '+a[3]+'"><div class="kpi-v">'+a[1]+'</div><div class="kpi-l">'+a[0]+'</div><div class="kpi-s">'+a[2]+'</div></div>'}).join("");
  // 堆叠条
  var total=x.landed||1;
  $("stack").innerHTML=x.stages.filter(function(s){return s.v>0}).map(function(s){
    return '<div style="width:'+(s.v/total*100).toFixed(2)+'%;background:'+s.c+'" title="'+esc(s.n)+' '+moneyS(s.v,v)+'"></div>'}).join("");
  $("legend").innerHTML=x.stages.filter(function(s){return s.v>0}).map(function(s){
    return '<span><i style="background:'+s.c+'"></i>'+esc(s.n)+' <b>'+(s.v/total*100).toFixed(1)+'%</b></span>'}).join("");
  // 成本阶梯
  var acc=0,rows=[];
  x.stages.forEach(function(s,i){
    acc+=s.v;
    var mine = (v.term==="EXW"&&i===0)||(v.term==="FOB"&&i<=1)||(v.term==="CIF"&&i<=2)||(v.term==="DDP");
    rows.push('<tr class="'+(mine?"active":"buyer")+'"><td>'+(i+1)+'</td><td>'+esc(s.n)+'</td><td class="num">'+money(s.v,v)+'</td><td class="num">'+(s.v/total*100).toFixed(1)+'%</td><td class="num">'+money(acc,v)+'</td><td>'+(mine?"我方承担":"买方承担")+'</td></tr>');
  });
  rows.push('<tr class="sum"><td></td><td><b>DDP 落地成本合计</b></td><td class="num">'+money(x.landed,v)+'</td><td class="num">100%</td><td class="num">'+money(x.landed,v)+'</td><td>'+altStr(x.landed,v)+'</td></tr>');
  $("stagesTbl").innerHTML=rowsTable(["#","成本项目","金额 "+ctag(),"占比","累计 "+ctag(),"承担方"],rows,"");
  // 多口径报价
  var tq=[];
  [["EXW","工厂交货"],["FOB","装运港交货"],["CIF","到岸（不含俄方税费）"],["DDP","完税落地全包"]].forEach(function(a){
    var b=x.cum[a[0]],q=b*x.factor;
    var buyer=x.landed-b;
    tq.push('<tr class="'+(a[0]===v.term?"active":"")+'"><td><b>'+a[0]+'</b> <span class="tag">'+a[1]+'</span></td>'+
      '<td class="num">'+money(b,v)+'</td><td class="num">'+money(q,v)+'</td><td class="num">'+refCur(q,v)+'</td>'+
      '<td class="num">'+(buyer>0?money(buyer,v):"—")+'</td><td>'+(a[0]===v.term?'<span class="tag a">当前口径</span>':"")+'</td></tr>');
  });
  $("termsTbl").innerHTML=rowsTable(["口径","我方成本 "+ctag(),"建议报价 "+ctag(),"折 "+(CUR==="RUB"?"USD":"RUB"),"买方另需承担 "+ctag(),""],tq,"");
  // 情景
  var scenes=[
   ["基准（当前参数）",{}],
   ["功率改 180hp（超 160 线）",{power:180,importer:"company"}],
   ["车龄 >3 年",{age:"old"}],
   ["汇率 +10%（卢布贬值）",{usdRub:v.usdRub*1.1}],
   ["关税改 30%",{dutyRate:30}],
   ["报废税系数 +20%（2027 预期）",{utilCoefScale:1.2}],
   ["增值税按 20% 旧口径",{vatRate:20}]
  ];
  var sr=[],baseLanded=x.landed;
  scenes.forEach(function(a,i){
    var y=(i===0)?x:compute(readV(a[1]));
    var d=y.landed-baseLanded;
    sr.push('<tr'+(i===0?' class="sum"':'')+'><td>'+esc(a[0])+'</td><td class="num">'+f2(y.uc)+'</td><td class="num">'+money(y.taxTotal,y.v)+'</td>'+
      '<td class="num">'+money(y.landed,y.v)+'</td><td class="num">'+(i===0?"—":formatSigned(d,y.v))+'</td>'+
      '<td class="num">'+(i===0?"—":(d/baseLanded*100>=0?"+":"")+(d/baseLanded*100).toFixed(1)+"%")+'</td></tr>');
  });
  $("scenesTbl").innerHTML=rowsTable(["情景","报废税系数","俄方税费 "+ctag(),"落地成本 "+ctag(),"较基准 "+ctag(),"变化 %"],sr,"");
  // 提示
  var warns=[];
  if(v.importer==="personal"&&v.power>160)warns.push("个人自用优惠档已失效：功率 >160hp，已按商业系数 "+f2(x.uc)+" 计算，报废税从 "+moneyS(3400,v)+" 级别跳到 "+moneyS(x.util,v)+"。");
  if(v.importer==="personal"&&v.power<=160&&v.disp<=3000)warns.push("使用个人自用优惠系数 "+f2(x.uc)+"：须同时满足 ≤3 年 / ≤3.0L / ≤160hp / 一年 1 辆 / 12 个月内不得转售，商业批量不适用。");
  if(v.power>160&&v.importer==="company")warns.push("功率 >160hp：公开资料未给出完整的商业功率分档表，当前系数来自排量×车龄查表，请按报关行核定后手动覆盖。");
  if(v.exciseAuto&&v.engine!=="bev"&&v.power>=145&&v.power<=165)warns.push("消费税阶梯边界公开资料写法含糊，本工具按「≤150hp 归 63 ₽/hp、>150 归 610 ₽/hp」处理；当前 "+fmt(v.power)+"hp 适用 "+excisePerHp(v.power)+" ₽/hp。若报关行按另一口径核定，请取消自动并手填总额。");
  if(v.engine==="bev"&&v.exciseAuto)warns.push("纯电按消费税 0 处理；若俄方按电机 30 分钟额定功率核定消费税，请取消「自动算消费税」并手填总额。");
  if(v.term==="DDP")warns.push("DDP 需俄方具备进口主体与清关资质，中方通常不能直接作为俄进口商；且需垫付全部俄方税费，资金与合规风险最高。");
  if(v.customsAdj!==0)warns.push("已计入海关估价调整 "+f2(v.customsAdj)+"%：低报货值会被俄海关重新核价并罚款，也会连带影响国内退税单证一致性。");
  warns.push("报废税系数与增值税率存在来源冲突，且 2027-01-01 预计再上调 10–20%；正式报价请让俄方报关行书面确认后重算。");
  warns.push("全站计价币种 "+ctag()+"：左侧金额输入、单位、预设与右侧结果、报价单、CSV 均按此币种；车价锚人民币、运费锚美元、俄方费用锚卢布，按 USD/RUB "+f2(v.usdRub)+"、CNY/USD "+f2(v.cnyUsd)+" 折算，切换币种不改变落地成本。");
  $("warns").innerHTML=warns.map(function(w){return "<li>"+esc(w)+"</li>"}).join("");
  // 参数快照 + 报价单
  window.__X=x;
  renderProfit(x);renderPlans();
  buildQuote(x);
}

@@ROUTESJS@@
@@VEHICLESJS@@
/* ===== 利润与保本价 ===== */
function renderProfit(x){
  var v=x.v;
  var pk=[["单台净利（内部）",moneyS(x.netProfit,v),"已扣佣金 / 销售费 · 含退税",x.netProfit>=0?"hl2":"warn"],
    ["净利率",x.netMargin.toFixed(1)+"%","目标 "+f2(v.margin)+"%",""],
    ["保本成交价",moneyS(x.breakEven,v),"净利 = 0 的最低价",""],
    ["可降价空间",moneyS(x.priceRoom,v),"占成交价 "+x.roomPct.toFixed(1)+"%",x.priceRoom>=0?"hl":"warn"]];
  $("profitKpis").innerHTML=pk.map(function(a){return '<div class="kpi big '+a[3]+'"><div class="kpi-v">'+a[1]+'</div><div class="kpi-l">'+a[0]+'</div><div class="kpi-s">'+a[2]+'</div></div>'}).join("");
  var rows=[
    ["建议报价（"+v.term+"）",x.quote,"对外报价，成本不出现在报价单里"],
    ["目标成交价 / 实收",x.sellPrice,v.targetPrice>0?"客户还价（手填）":"未填，按建议报价成交"],
    ["我方净成本",x.netCost,"累计成本 − 出口退税 "+moneyS(x.refund,v)],
    ["佣金 / 渠道返利",-x.commission,f2(v.commissionRate)+"% × 成交价"],
    ["单台销售费用",-v.sellFee,"市场 / 差旅 / 平台 / 翻译分摊"],
    ["单台净利",x.netProfit,"净收入 − 净成本（内部口径）"],
    ["保本成交价",x.breakEven,"(净成本 + 销售费) ÷ (1 − 佣金率)"],
    ["可降价空间",x.priceRoom,"成交价 − 保本价，还能让多少"],
    ["达标最低成交价",x.targetFloor,"净利率达到 "+f2(v.margin)+"% 所需；"+(x.floorDenom>0?"可达":"佣金＋目标 ≥100%，不可达")]
  ];
  var tr=rows.map(function(r,i){
    return '<tr'+(i===5?' class="sum"':'')+'><td>'+(i+1)+'</td><td><b>'+r[0]+'</b></td>'+
      '<td class="num">'+money(r[1],v)+'</td><td>'+r[2]+'</td></tr>';
  });
  $("profitTbl").innerHTML=rowsTable(["#","项目","金额 "+ctag(),"口径 / 公式"],tr,"");
  $("profitWarn").textContent="当前成交价 "+moneyS(x.sellPrice,v)+"，净利 "+moneyS(x.netProfit,v)+
    "（净利率 "+x.netMargin.toFixed(1)+"%）；低于 "+moneyS(x.breakEven,v)+" 即亏本，最多还能让 "+
    moneyS(Math.max(0,x.priceRoom),v)+"。以上为内部测算，报价单与 CSV 明细不含净利字段，可直接发客户。";
}
/* ===== 多方案报价对比 ===== */
var PLAN_KEY="ru_quote_plans",PLAN_MAX=6;
function getPlans(){try{return JSON.parse(localStorage.getItem(PLAN_KEY)||"[]")}catch(e){return []}}
function putPlans(a){try{localStorage.setItem(PLAN_KEY,JSON.stringify(a))}catch(e){}}
function planSnapshot(name){
  var x=window.__X;if(!x)return null;
  var p={id:"p"+Date.now()+Math.floor(Math.random()*1000),name:name,
         ts:new Date().toLocaleString("zh-CN"),ccy:CUR,params:{},base:{},res:{}};
  document.querySelectorAll("[data-k]").forEach(function(e){
    if(MONEY[e.id])return;
    p.params[e.id]=e.type==="checkbox"?e.checked:e.value;
  });
  MK.forEach(function(k){p.base[k]=BASE[k]});
  var v=x.v;
  p.res={quote:x.quote,landed:x.landed,netCost:x.netCost,grossProfit:x.grossProfit,
    netProfit:x.netProfit,netMargin:x.netMargin,breakEven:x.breakEven,priceRoom:x.priceRoom,
    taxTotal:x.taxTotal,term:v.term,model:v.model,power:v.power,disp:v.disp,
    freight:v.freight,uc:x.uc,usdRub:v.usdRub,cnyUsd:v.cnyUsd,qty:v.qty};
  return p;
}
function planMsg(t){var e=$("planMsg");if(e)e.textContent=t}
function addPlan(){
  var a=getPlans();
  if(a.length>=PLAN_MAX){planMsg("最多保存 "+PLAN_MAX+" 个方案，请先删一个");return}
  var el=$("planName"),name=(el&&el.value.trim())||("方案 "+String.fromCharCode(65+a.length));
  var p=planSnapshot(name);if(!p){planMsg("尚未完成计算，请稍候重试");return}
  a.push(p);putPlans(a);if(el)el.value="";
  planMsg("已存「"+name+"」，共 "+a.length+" 个方案");renderPlans();
}
function delPlan(id){
  var a=getPlans().filter(function(p){return p.id!==id});putPlans(a);
  renderPlans();planMsg("已删除，剩余 "+a.length+" 个方案");
}
function loadPlan(id){
  var p=getPlans().filter(function(q){return q.id===id})[0];if(!p)return;
  Object.keys(p.params||{}).forEach(function(k){var e=$(k);if(!e)return;
    if(e.type==="checkbox")e.checked=!!p.params[k];else e.value=p.params[k]});
  MK.forEach(function(k){if(typeof p.base[k]==="number")BASE[k]=p.base[k]});
  setCur(p.ccy||"RUB",false,true);
  syncCoef();render(compute(readV()));
  planMsg("已载入「"+p.name+"」：左侧参数、汇率与计价币种一并还原");
}
function renderPlans(){
  var a=getPlans(),v=window.__X?window.__X.v:ratesOf();
  if(!a.length){
    $("plansTbl").innerHTML='<div class="hintbox">还没有保存方案。调好左侧参数（车型 / 口岸 / 术语 / 汇率 / 客户还价）后，'
      +'点「把当前参数存为方案」，最多存 '+PLAN_MAX+' 套并排对比。方案只存在本机浏览器，换电脑不会同步。</div>';
    return;
  }
  var b=a[0].res;
  var head=["方案","车型 / 功率","术语","报价 "+ctag(),"落地成本 "+ctag(),"净利 "+ctag(),
            "净利率","较基准净利 "+ctag(),"当时汇率","操作"];
  var rows=a.map(function(p,i){
    var r=p.res,d=r.netProfit-b.netProfit;
    return '<tr'+(i===0?' class="sum"':'')+'><td><b>'+esc(p.name)+'</b><div class="cap">'+esc(p.ts)+' · '+esc(p.ccy)+'</div></td>'+
      '<td>'+esc(r.model||"—")+'<div class="cap">'+fmt(r.power)+'hp / '+fmt(r.disp)+'cc</div></td>'+
      '<td class="mid">'+esc(r.term)+'</td>'+
      '<td class="num">'+money(r.quote,v)+'</td><td class="num">'+money(r.landed,v)+'</td>'+
      '<td class="num">'+money(r.netProfit,v)+'</td><td class="num">'+r.netMargin.toFixed(1)+'%</td>'+
      '<td class="num">'+(i===0?"—":formatSigned(d,v))+'</td>'+
      '<td class="num">'+f2(r.usdRub)+'</td>'+
      '<td class="mid"><button class="mini" data-load="'+p.id+'" type="button">载入</button> '
      +'<button class="mini" data-del="'+p.id+'" type="button">删</button></td></tr>';
  });
  $("plansTbl").innerHTML=rowsTable(head,rows,"");
  $("plansTbl").querySelectorAll("[data-load]").forEach(function(btn){
    btn.addEventListener("click",function(){loadPlan(btn.getAttribute("data-load"))})});
  $("plansTbl").querySelectorAll("[data-del]").forEach(function(btn){
    btn.addEventListener("click",function(){delPlan(btn.getAttribute("data-del"))})});
}
function exportPlanCSV(){
  var a=getPlans();if(!a.length){planMsg("还没有方案可导出");return}
  var v=window.__X?window.__X.v:ratesOf();
  var num=function(n){return toCur(n,v).toFixed(2)};
  var rows=[["方案","保存时间","币种","车型","术语","报价 "+ctag(),"落地成本 "+ctag(),
             "净成本 "+ctag(),"单台净利 "+ctag(),"净利率 %","保本价 "+ctag(),"USD/RUB","CNY/USD"]];
  a.forEach(function(p){var r=p.res;rows.push([p.name,p.ts,p.ccy,r.model,r.term,
    num(r.quote),num(r.landed),num(r.netCost),num(r.netProfit),r.netMargin.toFixed(2),
    num(r.breakEven),r.usdRub,r.cnyUsd])});
  var csv="\ufeff"+rows.map(function(r){return r.map(function(c){return '"'+String(c).replace(/"/g,'""')+'"'}).join(",")}).join("\n");
  var a2=document.createElement("a");a2.href=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));
  a2.download="russia-plan-compare-"+ctag()+".csv";a2.click();URL.revokeObjectURL(a2.href);
  planMsg("已导出 "+a.length+" 个方案（当前币种 "+ctag()+"）");
}
/* ===== 口岸 / 车型一键带入 ===== */
function applyRoute(id){
  var r=ROUTES[id];if(!r)return;
  BASE.freight=r.usd;BASE.inland=r.inland;
  var fp=$("freightPreset");if(fp)fp.value=r.preset;
  projectAll();syncCoef();render(compute(readV()));
  $("routeMsg").innerHTML="已应用 <b>"+esc(r.name)+"</b>：单台运费 $"+f2(r.usd)+"、全程 "+esc(r.days)+
    " 天、俄境内段 "+fmt(r.inland)+" ₽，左侧「国际运费」与「俄境内运输」已同步；可继续手动微调。";
  document.querySelectorAll("[data-route]").forEach(function(b){
    b.classList.toggle("on",b.getAttribute("data-route")===id)});
}
function applyVehicle(id){
  var m=VEHICLES[id];if(!m)return;
  BASE.price=m.price;
  var vals={disp:m.disp,power:m.power,engine:m.engine,age:m.age,model:m.name};
  Object.keys(vals).forEach(function(k){var e=$(k);if(e)e.value=vals[k]});
  var hs=$("vehicleHs");if(hs)hs.value=m.hs;
  var pick=$("vehiclePick");if(pick)pick.value=id;
  syncCoef();projectAll();render(compute(readV()));
  $("vehicleMsg").innerHTML="已带入 <b>"+esc(m.name)+"</b>：车价 "+fmt(m.price)+" CNY、"+fmt(m.disp)+
    "cc / "+fmt(m.power)+"hp、参考 HS "+esc(m.hs)+"。价格是国内指导价占位，<b>请按实际采购发票价覆盖</b>；"
    +"混动 / 纯电的功率口径与 HS 子目须由报关行核定。";
  document.querySelectorAll("[data-vehicle]").forEach(function(b){
    b.classList.toggle("on",b.getAttribute("data-vehicle")===id)});
}
function formatSigned(n,v){return (n>=0?"+":"−")+money(Math.abs(n),v)}
function buildQuote(x){
  var v=x.v, d=new Date(), ds=d.getFullYear()+"-"+("0"+(d.getMonth()+1)).slice(-2)+"-"+("0"+d.getDate()).slice(-2);
  var lines=[
    "【报价单 / QUOTATION】  编号 RU-"+ds.replace(/-/g,"")+"-01",
    "日期："+ds+"    报价有效期：15 天",
    "车型 / 配置："+(v.model||"—"),
    "数量："+fmt(v.qty)+" 台    动力："+({ice:"汽油/柴油",hybrid:"混动/增程",bev:"纯电"}[v.engine])+"    "+fmt(v.disp)+" cc / "+fmt(v.power)+" hp",
    "贸易术语："+v.term+"（不含项见下）    目的国：俄罗斯",
    "报价币种："+ctag()+"（"+CUR_INFO[CUR].name+"）    USD/RUB "+f2(v.usdRub)+"    CNY/USD "+f2(v.cnyUsd),
    "",
    "── 单台报价 ──",
    "建议报价："+moneyS(x.quote,v)+" / 台   "+altStr(x.quote,v),
    "批量总价："+moneyS(x.quote*v.qty,v)+"   "+altStr(x.quote*v.qty,v),
    "DDP 完税落地成本（参考）："+moneyS(x.landed,v)+" / 台",
    "该口径下买方另需承担："+(x.buyerCost>0?moneyS(x.buyerCost,v)+" / 台":"无"),
    "",
    "── 成本构成（单台，"+ctag()+"）──",
    "车价 "+money(x.carRUB,v)+" ｜ 出口本地费 "+money(x.localRUB,v)+" ｜ 运费保险 "+money(x.frtRUB,v),
    "关税 "+money(x.duty,v)+" ｜ 消费税 "+money(x.excise,v)+" ｜ 增值税 "+money(x.vat,v),
    "报废税 "+money(x.util,v)+"（系数 "+f2(x.uc)+"）｜ 清关费 "+money(x.cfee,v),
    "认证/代理/内陆/整备/质保 "+money(x.svc,v),
    "",
    "── 商务条款 ──",
    "付款：30% 预付 + 70% 见提单副本 / 清关单复印件；人民币结算优先（CIPS / SPFS）",
    "交期：收到预付款且出口许可证办妥后 __ 天；运输方式按合同约定",
    "质保：平行进口无原厂质保，由我方提供 __ 个月 / __ 公里有限质保（含易损件与备件供应）",
    "报价含：车价、中国出口单证与报关、"+(v.term==="DDP"?"俄方全部税费与认证":"至"+v.term+"条款止的费用"),
    "报价不含："+(v.term==="DDP"?"俄境内上牌、ОСАГО 保险":"俄方进口关税、增值税、报废税、认证、清关与境内运输（由买方承担）"),
    "",
    "── 重要声明 ──",
    "本报价为成本测算结果，非正式报关依据。税率、报废税系数、汇率均按签约日俄海关 / 俄央行核定值为准；",
    "报废税系数每年 1 月调整（2027-01-01 预计再上调 10–20%），长周期合同须含费率与汇率调价条款。",
    "参数快照：USD/RUB "+f2(v.usdRub)+"，CNY/USD "+f2(v.cnyUsd)+"，关税 "+f2(v.dutyRate)+"%，增值税 "+f2(v.vatRate)+"%，报废税系数 "+f2(x.uc)+"，目标毛利/加成 "+f2(v.margin)+"%"
  ];
  var ru=[
    "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ  № RU-"+ds.replace(/-/g,"")+"-01",
    "Дата: "+ds+"    Срок действия: 15 дней",
    "Автомобиль: "+esc(v.model||"—"),
    "Количество: "+fmt(v.qty)+" шт.    Двигатель: "+fmt(v.disp)+" см³ / "+fmt(v.power)+" л.с.",
    "Условия поставки (Инкотермс): "+v.term+"    Страна: Россия",
    "Валюта цены: "+ctag()+"    Курс USD/RUB "+f2(v.usdRub)+"    CNY/USD "+f2(v.cnyUsd),
    "",
    "Цена за единицу: "+moneyS(x.quote,v)+"  ("+altStr(x.quote,v)+")",
    "Итого за партию: "+moneyS(x.quote*v.qty,v),
    "Справочно: полная стоимость с растаможкой (DDP) — "+moneyS(x.landed,v)+" / шт.",
    "Дополнительные расходы покупателя: "+(x.buyerCost>0?moneyS(x.buyerCost,v)+" / шт.":"нет"),
    "",
    "Состав затрат ("+ctag()+" / шт.):",
    "Стоимость авто "+money(x.carRUB,v)+" | Экспортные расходы КНР "+money(x.localRUB,v)+" | Фрахт и страховка "+money(x.frtRUB,v),
    "Пошлина "+money(x.duty,v)+" | Акциз "+money(x.excise,v)+" | НДС "+money(x.vat,v),
    "Утилизационный сбор "+money(x.util,v)+" (коэф. "+f2(x.uc)+") | Таможенный сбор "+money(x.cfee,v),
    "Сертификация, брокер, доставка, PDI, гарантия "+money(x.svc,v),
    "",
    "Условия оплаты: 30% предоплата + 70% по копии коносамента / таможенной декларации.",
    "Расчёты предпочтительно в CNY (CIPS / SPFS).",
    "Гарантия: заводская гарантия отсутствует (параллельный импорт); предоставляется ограниченная гарантия продавца.",
    "",
    "ВНИМАНИЕ: расчёт предварительный. Ставки пошлин, НДС, коэффициент утилизационного сбора и курс",
    "подлежат подтверждению таможенным брокером и ЦБ РФ на дату подписания контракта.",
    "Коэффициент утильсбора индексируется ежегодно (следующее изменение — 01.01.2027)."
  ];
  $("quoteCn").textContent=lines.join("\n");
  $("quoteRu").textContent=ru.join("\n");
}
function copyText(t,btn){
  var done=function(){var o=btn.textContent;btn.textContent="已复制 ✓";setTimeout(function(){btn.textContent=o},1600)};
  if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(done,function(){fallback(t,done)})}
  else fallback(t,done);
}
function fallback(t,done){var a=document.createElement("textarea");a.value=t;a.style.position="fixed";a.style.opacity=0;
  document.body.appendChild(a);a.select();try{document.execCommand("copy");done()}catch(e){alert("复制失败，请手动选中文本复制")}document.body.removeChild(a)}
function downloadCSV(){
  var x=window.__X;if(!x)return;
  var num=function(n){return toCur(n,x.v).toFixed(2)};
  var rows=[["#","成本项目","金额 "+ctag(),"占比 %","累计 "+ctag(),"承担方"]],acc=0;
  x.stages.forEach(function(s,i){acc+=s.v;rows.push([i+1,s.n,num(s.v),(s.v/x.landed*100).toFixed(2),num(acc),
    ((x.v.term==="EXW"&&i===0)||(x.v.term==="FOB"&&i<=1)||(x.v.term==="CIF"&&i<=2)||(x.v.term==="DDP"))?"我方承担":"买方承担"])});
  rows.push(["","DDP 落地成本合计",num(x.landed),100,num(x.landed),""]);
  rows.push(["","建议报价 "+x.v.term,num(x.quote),"","",""]);
  rows.push(["","显示币种",ctag(),"USD/RUB",x.v.usdRub,"CNY/USD "+x.v.cnyUsd]);
  var csv="\ufeff"+rows.map(function(r){return r.map(function(c){return '"'+String(c).replace(/"/g,'""')+'"'}).join(",")}).join("\n");
  var a=document.createElement("a");a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));
  a.download="russia-quotation-"+ctag()+".csv";a.click();URL.revokeObjectURL(a.href);
}
function saveParams(){
  var d={__ccy:CUR,__base:{}};
  MK.forEach(function(k){d.__base[k]=BASE[k]});
  document.querySelectorAll("[data-k]").forEach(function(e){
    if(MONEY[e.id])return;                       /* 金额存锚定值，不存显示值 */
    d[e.id]=e.type==="checkbox"?e.checked:e.value;
  });
  try{localStorage.setItem("ru_quote_params",JSON.stringify(d));
    $("saveMsg").textContent="参数已保存到本机浏览器（"+Object.keys(d).length+" 项，金额按锚定币种存储）"}catch(e){$("saveMsg").textContent="保存失败："+e.message}
}
function loadParams(){
  try{
    var s=localStorage.getItem("ru_quote_params");if(!s)return null;
    var d=JSON.parse(s);
    Object.keys(d).forEach(function(k){
      if(k.charAt(0)==="_")return;
      var e=$(k);if(!e)return;
      if(e.type==="checkbox")e.checked=!!d[k];else e.value=d[k];
    });
    if(d.__base)MK.forEach(function(k){if(typeof d.__base[k]==="number")BASE[k]=d.__base[k]});
    $("saveMsg").textContent="已恢复上次保存的参数（金额按锚定值存储，随当前计价币种折算）";
    return d.__ccy||null;
  }catch(e){return null}
}
function applyPreset(name){
  var p=PRESETS[name];if(!p)return;
  BASE.price=p.price;                              /* 预设车价按人民币锚定 */
  Object.keys(p).forEach(function(k){
    if(k==="price")return;
    var e=$(k);if(!e)return;
    if(e.type==="checkbox")e.checked=!!p[k];else e.value=p[k];
  });
  projectAll();
  syncCoef();render(compute(readV()));
  try{history.replaceState(null,"","?preset="+name+(CUR!=="RUB"?"&ccy="+CUR:""))}catch(e){}
}
function syncCoef(){
  var v=readV(),ua=utilAuto(v.disp,v.age,v.power,v.importer);
  if(v.utilCoefAuto)$("utilCoefManual").value=ua.c.toFixed(2);
  $("coefHint").textContent=ua.note+"｜当前系数 "+(v.utilCoefAuto?ua.c.toFixed(2):v.utilCoefManual);
}
function updateRate(){
  var v=readV(),e=$("curRate");
  if(e)e.textContent="1 USD = "+f2(v.usdRub)+" ₽ ｜ 1 USD = "+f2(v.cnyUsd)+" CNY";
}
function setCur(c,save,noSync){
  if(!CUR_INFO[c])c="RUB";
  if(!noSync)MK.forEach(function(k){
    var e=$(k);
    if(e&&e.value!==e.getAttribute("data-proj"))syncFromInput(k);
  });   /* 只固化未同步的手工编辑，避免显示精度被反复回算造成漂移 */
  CUR=c;
  document.querySelectorAll("#curbar button[data-ccy]").forEach(function(b){
    b.classList.toggle("on",b.getAttribute("data-ccy")===c)});
  if(save)try{localStorage.setItem("ru_quote_ccy",c)}catch(e){}
  projectAll();applyStaticCurrency();
  syncCoef();render(compute(readV()));
}
function bind(){
  document.querySelectorAll("[data-preset]").forEach(function(b){b.addEventListener("click",function(){applyPreset(b.dataset.preset)})});
  $("freightPreset").addEventListener("change",function(){BASE.freight=FREIGHT[this.value]||0;projectAll();render(compute(readV()))});
  $("dutyPreset").addEventListener("change",function(){$("dutyRate").value=this.value;render(compute(readV()))});
  $("vatPreset").addEventListener("change",function(){$("vatRate").value=this.value;render(compute(readV()))});
  /* 车价币种已跟随全站计价币种，不再单独绑定 */
  document.querySelectorAll(".form-panel input,.form-panel select").forEach(function(e){
    e.addEventListener("input",function(){
      if(MONEY[e.id])syncFromInput(e.id);
      if(["disp","age","power","importer","utilCoefAuto"].indexOf(e.id)>=0)syncCoef();
      render(compute(readV()));
    });
    e.addEventListener("change",function(){
      if(MONEY[e.id])syncFromInput(e.id);
      if(e.id==="usdRub"||e.id==="cnyUsd")projectAll();  /* 汇率失焦后按新汇率重投影 */
      if(["disp","age","power","importer","utilCoefAuto"].indexOf(e.id)>=0)syncCoef();
      render(compute(readV()));
    });
  });
  document.querySelectorAll("#curbar button[data-ccy]").forEach(function(b){
    b.addEventListener("click",function(){setCur(b.getAttribute("data-ccy"),true)});
  });
  $("btnCalc").addEventListener("click",function(){syncCoef();render(compute(readV()))});
  $("btnSave").addEventListener("click",saveParams);
  $("btnReset").addEventListener("click",function(){localStorage.removeItem("ru_quote_params");location.reload()});
  $("copyCn").addEventListener("click",function(){copyText($("quoteCn").textContent,this)});
  $("copyRu").addEventListener("click",function(){copyText($("quoteRu").textContent,this)});
  $("btnCsv").addEventListener("click",downloadCSV);
  $("btnPrint").addEventListener("click",function(){window.print()});
  $("btnPlanAdd").addEventListener("click",addPlan);
  $("btnPlanCsv").addEventListener("click",exportPlanCSV);
  $("btnPlanClear").addEventListener("click",function(){putPlans([]);renderPlans();planMsg("已清空全部方案")});
  document.querySelectorAll("[data-route]").forEach(function(b){
    b.addEventListener("click",function(){applyRoute(b.getAttribute("data-route"))})});
  document.querySelectorAll("[data-vehicle]").forEach(function(b){
    b.addEventListener("click",function(){applyVehicle(b.getAttribute("data-vehicle"))})});
  var vp=$("vehiclePick");
  if(vp)vp.addEventListener("change",function(){if(vp.value)applyVehicle(vp.value)});
}
initBase();
var loadedCcy=loadParams();
bind();
var cm=/[?&]ccy=(RUB|USD|CNY)/i.exec(location.search),saved=null;
try{saved=localStorage.getItem("ru_quote_ccy")}catch(e){}
var target=cm?cm[1].toUpperCase():((loadedCcy&&CUR_INFO[loadedCcy])?loadedCcy:((saved&&CUR_INFO[saved])?saved:"RUB"));
setCur(target,false,true);
var pm=/[?&]preset=(base|power|bev|used)/.exec(location.search);
if(pm)applyPreset(pm[1]);
})();
</script>
"""

BODY = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>俄罗斯整车出口报价计算器｜落地成本 · 报废税 · 多口径报价</title>
<style>@@CSS@@</style></head><body>
@@NAV@@
<div class="wrap" id="top">
<header>
 <div class="eyebrow">RUSSIA · LANDED COST CALCULATOR · @@DATE@@</div>
 <h1>俄罗斯整车出口报价计算器</h1>
 <p class="sub">从车价到 DDP 落地，逐项算清关税、增值税、报废税与认证，直接出中/俄文报价单</p>
 <div class="badges"><span class="badge">新增 Tab 页 · @@DATE@@</span><span class="badge">俄央行汇率 @@DATE@@</span><span class="badge">17 条来源 · 4 处口径冲突</span><span class="badge">参数全部可改 / 可保存</span></div>
 <p class="lead" style="margin-top:20px">总览看板讲「找谁」、细分市场讲「卖什么」，本页讲「怎么报价」。改左边任一参数，右边实时重算成本阶梯、四种贸易术语报价、情景敏感性与可复制报价单。</p>
</header>

<div class="card warn"><b>⚠ 先读：这是成本测算工具，不是报关系统</b><br/>
默认参数取自 2026 年公开法规与行业实操资料，逐条标了来源与证据等级（见「参数来源」）。俄罗斯整车进口税率存在 <b>20%/22% 增值税</b>、<b>15–25% / 20–38% 关税</b>、<b>EAEU 补差新规是否生效</b> 三处来源冲突，报废税系数还按排量、车龄、功率、进口主体四维变化。<b>正式报价前必须让俄方报关行按 HS 子目书面核定税率与系数</b>，并预留 2027-01-01 报废税再上调 10–20% 的调价条款。报价单里请把税费分行列出，别让客户在清关时才发现价格翻番。</div>

<section id="calc"><h2><span class="n">01</span>报价计算器</h2>
<p class="lead">默认示例：一台约 12.8 万元、1.5L / 150hp 的中国产 SUV，法人商业进口、CIF 口径、铁路班列运输。先在下面选一个计价币种，整个计算器的输入与输出都会统一到该币种；点预设可切换车型，感受 160 马力门槛对落地成本的影响。</p>
<div class="curbar" id="curbar">
   <span class="lab">全站计价币种</span>
   <button type="button" data-ccy="RUB" class="on">₽ 卢布 RUB</button>
   <button type="button" data-ccy="USD">$ 美元 USD</button>
   <button type="button" data-ccy="CNY">¥ 人民币 CNY</button>
   <span class="rate" id="curRate"></span>
   <p class="cap">选一个币种，<b>整个计算器都跟着变</b>：左侧所有金额输入框的数值与单位、车型 / 运输预设、右侧成本阶梯、四种口径报价、情景敏感性、中俄文报价单、CSV 与打印，以及下方参考表的金额，全部按该币种显示。内部仍以卢布为基准计算，切换币种<b>不改变任何结果</b>；车价锚定人民币、运费与出口本地费锚定美元、俄方费用与法规阈值锚定卢布，因此改汇率只影响外币计价项，卢布法定金额不会被汇率带走。</p>
 </div>
<div class="calc">
@@FORM@@
<div class="result-panel">
 <div class="kpis4" id="kpis"></div>
 <div class="card"><h3 style="margin-top:0">成本构成（占 DDP 落地成本）</h3>
   <div class="stack" id="stack"></div><div class="legend" id="legend"></div>
   <p class="cap">税费类（关税 + 消费税 + 增值税 + 报废税 + 清关费）通常是最大项。经销商协会拆过一台 271 万卢布的车：税费合计 118 万、占 44%，其中报废税 80.08 万、增值税 22.97 万、关税 13.5 万 [S03]。</p>
 </div>
 <div class="card warn" style="margin-top:14px"><b>本次测算提示</b><ul id="warns" style="margin:8px 0 0;padding-left:20px;line-height:1.8"></ul></div>
 <div class="card" id="stages" style="margin-top:14px"><h3 style="margin-top:0">成本阶梯与承担方</h3>
   <div id="stagesTbl"></div>
   <p class="cap">「我方承担」按你选的贸易术语界限划分：EXW 只含车价，FOB 加出口本地费，CIF 加运费保险，DDP 含俄方全部税费与落地服务。<b>俄方税费由买方承担的口径下，落地成本仍列出，方便你向客户解释「到手还要多少钱」。</b></p>
 </div>
 <div class="card" id="terms" style="margin-top:14px"><h3 style="margin-top:0">四种口径报价对照</h3>
   <div id="termsTbl"></div>
   <p class="cap">利润算法默认毛利率法（成本 ÷ (1 − 毛利率)），可在左侧切换加成法。<b>DDP 需俄方具备进口主体资质，中方一般不能直接做俄进口商</b>，且要垫付全部税费，首单建议 FOB/CIF + 俄方指定清关代理。</p>
 </div>
 <div class="card" id="scenes" style="margin-top:14px"><h3 style="margin-top:0">情景敏感性（哪些变量最要命）</h3>
   <div id="scenesTbl"></div>
   <p class="cap">每个情景只改一个变量，其余保持当前输入。<b>功率过 160hp</b> 会把个人自用优惠档直接打掉，<b>车龄 >3 年</b> 让商业报废税系数跳 2–3 倍，<b>2027 系数 +20%</b> 是长周期合同必须预留的变量。</p>
 </div>
 <div class="card" id="exports" style="margin-top:14px"><h3 style="margin-top:0">导出与报价单</h3>
   <div class="btn-row" style="grid-template-columns:repeat(4,1fr)">
     <button class="btn ok" id="copyCn">复制中文报价单</button>
     <button class="btn ok" id="copyRu">复制俄文报价单</button>
     <button class="btn" id="btnCsv">导出成本明细 CSV</button>
     <button class="btn" id="btnPrint">打印 / 存 PDF</button>
   </div>
   <div class="cols2" style="margin-top:12px">
     <div><b style="font-size:12.5px;color:var(--a1)">中文报价单</b><div class="quote-box" id="quoteCn"></div></div>
     <div><b style="font-size:12.5px;color:var(--a2)">Коммерческое предложение（俄文）</b><div class="quote-box" id="quoteRu"></div></div>
   </div>
   <p class="cap">报价单已含车型、数量、贸易术语、成本构成、付款结构（30/70）、质保声明与「税费以报关行核定为准」的免责条款，可直接贴进邮件或 WhatsApp。参数可点「保存参数」存在本机浏览器，下次打开自动恢复。</p>
 </div>
</div></div>
</section>

<section id="profit"><h2><span class="n">02</span>利润与保本价（内部测算）</h2>
<p class="lead">上面算的是「成本 + 建议报价」，这里算的是「这一单真正赚多少、最低能卖到多少」。在左侧 E 组填客户还价、佣金与销售费用，下面实时反算净利、净利率、保本成交价与还能让多少价。</p>
<div class="kpis4" id="profitKpis"></div>
<div class="card"><h3 style="margin-top:0">单台利润拆解（金额随全站计价币种）</h3>
 <div id="profitTbl"></div>
 <p class="cap">净成本 = 该贸易术语下我方承担成本 − 出口退税；净利 = 成交价 − 佣金 − 销售费用 − 净成本。保本价按「净利 = 0」倒推，达标最低成交价按「净利率 = 目标毛利率」倒推。原「我方单台毛利」是未扣佣金 / 销售费的账面毛利，两者口径不同。</p>
</div>
<div class="card warn" style="margin-top:14px"><b>内部口径，别发给客户</b><p id="profitWarn" style="margin:8px 0 0;line-height:1.8"></p>
<p class="cap" style="margin-top:8px">中文 / 俄文报价单与「导出成本明细 CSV」都不含净利、净成本、保本价，可直接发客户；方案对比 CSV 是内部对账用，转发前请自行确认。</p></div>
</section>

<section id="plans"><h2><span class="n">03</span>多方案报价对比</h2>
<p class="lead">同一台车，换口岸、换术语、改汇率、客户压价，到底哪个方案更赚？把当前参数存成方案，最多 6 套并排对比，点「载入」可一键还原全部参数与币种。</p>
<div class="card">
 <div class="planbar">
   <input type="text" id="planName" class="grow" placeholder="方案名，如：客户还价 / 海运方案 / 2027 税率">
   <button class="btn ok" id="btnPlanAdd">把当前参数存为方案</button>
   <button class="btn" id="btnPlanCsv">导出对比 CSV</button>
   <button class="btn" id="btnPlanClear">清空</button>
 </div>
 <div id="planMsg" class="cap"></div>
 <div id="plansTbl"></div>
 <p class="cap">方案存的是「锚定基准金额 + 全部参数 + 当时的汇率」，不是显示值；对比表统一按当前计价币种与汇率折算，所以切币种不会改变方案之间的差异。第一套方案是基准，「较基准净利」以它为 0 点。</p>
</div>
</section>

<section id="params"><h2><span class="n">04</span>默认参数与来源</h2>
<p class="lead">A = 官方法规 / 海关 / 俄央行；B = 权威机构经媒体转述或行业实操指南；C = 行业调研、二手转述或口径存疑。所有值都能在左侧直接改；表中金额型默认值随上方计价币种换算，两行汇率是无量纲比率、不参与换算。</p>
<div class="card"><div class="tbl-scroll"><table><thead><tr><th>参数</th><th>默认值</th><th>单位</th><th>等级</th><th>来源</th><th>说明</th></tr></thead><tbody>@@PARAMROWS@@</tbody></table></div></div>
<div class="card" style="margin-top:14px"><h3 style="margin-top:0">运输方式预设（单台运费参考）</h3>
<div class="tbl-scroll"><table><thead><tr><th>方式 / 时效</th><th>默认 USD</th><th>说明</th></tr></thead><tbody>@@FREIGHTROWS@@</tbody></table></div></div>
<div class="card" style="margin-top:14px"><h3 style="margin-top:0">商业进口报废税系数表（基准 20,000 ₽ × 系数）</h3>
<div class="tbl-scroll"><table><thead><tr><th>排量档</th><th>≤3 年</th><th>&gt;3 年</th><th>新车报废税</th><th>旧车报废税</th></tr></thead><tbody>@@UTILROWS@@</tbody></table></div>
<p class="cap">个人自用另有优惠档：≤3 年 0.17（3,400 ₽）、&gt;3 年 0.26（5,200 ₽），但必须同时满足 ≤3.0L / ≤160hp / 一年 1 辆 / 12 个月内不转售。功率一过 160hp 即转商业系数 [S04][S05][S17]。</p></div>
</section>

<section id="conflicts"><h2><span class="n">05</span>四处口径冲突：报价前必须核</h2>
<p class="lead">这些不是算错，是公开来源本身打架。计算器给出了默认值，但<b>不替你拍板</b>。</p>
<div class="card"><div class="tbl-scroll"><table><thead><tr><th>冲突点</th><th>两种记载</th><th>本页处理</th></tr></thead><tbody>@@CONFROWS@@</tbody></table></div></div>
<div class="card warn" style="margin-top:14px"><b>还有一条时间炸弹</b><br/>报废税系数每年 1 月指数化，2026 年初已上调一轮 10–20%，按俄工贸部口径 <b>2027-01-01 再上调 10–20%</b>，规划延续到 2030 年。经销商可能提前把预期涨价算进在售车成本。所以：长周期合同必须写「费率变动与汇率分担条款」，别用今天的系数锁半年后的价 [S17]。</div>
</section>

<section id="routes"><h2><span class="n">06</span>口岸与运费表（点「应用」带入计算器）</h2>
<p class="lead">把「运输方式预设」拆到具体线路：不同出境口岸的运费、全程天数、俄境内段差异很大。点任一行的「应用」，会把单台运费、运输方式与俄境内运输一次性写进左侧表单并立即重算。</p>
<div class="card warn"><b>运价是参考中值，不是货代报价</b><br/>运费锚定美元，取 2026 年公开物流资料的单台参考区间中值；俄境内段锚定卢布，按远东 / 圣彼得堡到莫斯科的常见区间取值。<b>表内金额随上方全站计价币种换算，RUB 模式下看到的是折算后的卢布，切到 USD 才会显示原始美元参考价。</b>旺季订舱、燃油附加费、冬季破冰费、滞港费、超限车型附加费都会让实际报价大幅偏离；签约前必须让货代按实际车型尺寸与发运日期报实价。</div>
<div class="card" style="margin-top:14px"><div class="tbl-scroll"><table><thead><tr>
 <th>线路 / 出境口岸</th><th>单台运费 <span data-thccy></span></th><th>全程天数</th><th>俄境内段 <span data-thccy></span></th><th>操作</th><th>等级</th><th>要点与来源</th>
</tr></thead><tbody>@@ROUTEROWS@@</tbody></table></div>
<p class="cap">「俄境内段」在 DDP 口径下才计入落地成本；FOB / CIF 由买方承担，应用后左侧仍会写入该值，切换术语时按承担方自动区分。「—」表示该线路不含额外俄境内段。</p></div>
<div id="routeMsg" class="hintbox">尚未应用线路，当前用的是表单里的运输方式预设。金额随上方全站计价币种换算。</div>
</section>

<section id="vehicles"><h2><span class="n">07</span>车型参数库（点「带入」一键填 30+ 参数）</h2>
<p class="lead">每次报价手填车价、排量、功率、动力类型、车龄最容易出错，而功率直接决定消费税档位与 160 马力资格线。选一个车型，左侧 A 组参数、参考 HS 子目与车型描述会一次性带入，报废税系数自动重查。</p>
<div class="card warn"><b>参数与价格都是参考值，务必按实车覆盖</b><br/>车价列是国内指导价 / 公开配置页的<b>占位参考</b>，不是出口采购价，报价前必须换成实际采购发票价；混动 / 纯电的功率按驱动电机峰值折算，俄方是否按额定功率核定消费税与报废税须逐车确认；HS 子目只是常见归类，最终以报关行按 VIN 与动力类型核定为准。证据等级 B/C，改动会同步影响落地成本。</div>
<div class="card" style="margin-top:14px"><div class="tbl-scroll"><table><thead><tr>
 <th>车型 / 品牌</th><th>排量</th><th>功率</th><th>动力</th><th>车龄</th><th>参考 HS</th><th>参考价 <span data-thccy></span></th><th>操作</th><th>等级</th>
</tr></thead><tbody>@@VEHICLEROWS@@</tbody></table></div>
<p class="cap">参考价是国内指导价（人民币），表内金额随上方全站计价币种换算；带入后车价锚定人民币，切币种只换显示。160hp 是个人自用优惠档的资格线，不是加价线 —— 用 156hp 的瑞虎 7 与 184hp 的 Jetour T2 对比最直观。</p></div>
<div id="vehicleMsg" class="hintbox">尚未带入车型，当前为默认示例（1.5L / 150hp 中国产 SUV）。</div>
</section>

<section id="how"><h2><span class="n">08</span>计算公式（可复核）</h2>
<div class="card"><div class="tbl-scroll"><table><thead><tr><th>步骤</th><th>公式</th><th>说明</th></tr></thead><tbody>
<tr><td><b>1 CIF</b></td><td>FOB（车价 ÷ CNY/USD ＋ 出口本地费）＋ 运费 ＋ (FOB ＋ 运费) × 保险费率</td><td>严格等于成本阶梯前三项累加，可逐行对账</td></tr>
<tr><td><b>2 完税价格</b></td><td>CIF × USD/RUB × (1 ＋ 海关估价调整%)</td><td>俄海关有权按市场价重新核价</td></tr>
<tr><td><b>3 关税</b></td><td>完税价格 × 关税率</td><td>按 HS 子目 / 车龄 / 主体核定</td></tr>
<tr><td><b>4 消费税</b></td><td>马力 × 阶梯单价（≤90 免 / ≤150 63 / ≤200 610 / ≤300 1,000 / ≤400 1,036 / &gt;400 1,128 ₽）</td><td>阶梯边界按上界闭合（150hp 归 63 档）；纯电默认 0，是否按电机功率征须另核</td></tr>
<tr><td><b>5 增值税</b></td><td>(完税价格 ＋ 关税 ＋ 消费税) × 增值税率</td><td>报废税不计入增值税基数</td></tr>
<tr><td><b>6 报废税</b></td><td>基准费率 20,000 ₽ × 系数（排量 / 车龄 / 主体 / 功率）</td><td>单列，通常是最大单项</td></tr>
<tr><td><b>7 清关手续费</b></td><td>按完税价格自动落入 2026 年 8 档（1,231 ~ 73,860 ₽）</td><td>第 1638 号决议，2026-01-01 起</td></tr>
<tr><td><b>8 落地成本</b></td><td>上述全部 ＋ 认证 / 代理 / 内陆 / PDI / 质保 / 杂费</td><td>DDP 全包成本</td></tr>
<tr><td><b>9 报价</b></td><td>该术语对应累计成本 ÷ (1 − 毛利率)　或　× (1 ＋ 加成率)</td><td>买卖双方承担项按术语边界切分</td></tr>
<tr><td><b>10 我方毛利</b></td><td>报价 − (我方承担成本 − 出口退税)</td><td>退税 = 含税采购价 ÷ 1.13 × 13% ÷ CNY/USD × USD/RUB</td></tr>
<tr><td><b>11 净利</b></td><td>成交价 − 成交价 × 佣金率 − 销售费用 − 净成本</td><td>目标成交价留空时按建议报价成交；佣金 / 销售费只进内部测算</td></tr>
<tr><td><b>12 保本价</b></td><td>(净成本 + 销售费用) ÷ (1 − 佣金率)</td><td>净利恰为 0 的最低价；低于此价即亏本</td></tr>
<tr><td><b>13 达标最低价</b></td><td>(净成本 + 销售费用) ÷ (1 − 佣金率 − 目标净利率)</td><td>分母 ≤ 0 时目标不可达，页面显示 0</td></tr>
</tbody></table></div>
<p class="cap">所有中间结果在右侧成本阶梯表里逐行列出，可导出 CSV 与 Excel 模板逐项对账。<b>公式透明是本工具的原则</b>：任何一项你觉得不对，直接改左侧输入框，不要改公式。</p></div></section>

<section id="sources"><h2><span class="n">09</span>数据来源</h2>
<div class="card"><div class="tbl-scroll"><table><thead><tr><th>编号</th><th>来源</th><th>关键内容</th><th>等级</th><th>链接</th></tr></thead><tbody>@@SRCROWS@@</tbody></table></div></div></section>

<section id="downloads"><h2><span class="n">↓</span>配套文件下载</h2><p class="lead">Excel 模板带公式、可离线迭代参数；规则说明 PDF 覆盖中俄两侧全流程与单证清单。</p><div class="card">@@DLS@@</div></section>
<footer>本页为报价成本测算工具，所有税率、系数与汇率均标注来源与证据等级，不构成报关依据或税务意见。正式交易前请由俄方持牌报关行按 HS 子目书面核定，并完成进口主体、认证、制裁名单与收汇通道核验。配套「基本出口规则说明」见页面级 Tab。</footer>
</div>
@@JS@@
</body></html>"""

out = (BODY.replace("@@CSS@@", CSS + EXTRA)
       .replace("@@NAV@@", nav("quotation"))
       .replace("@@DATE@@", RATE_DATE)
       .replace("@@FORM@@", FORM)
       .replace("@@PARAMROWS@@", param_rows)
       .replace("@@FREIGHTROWS@@", freight_rows)
       .replace("@@UTILROWS@@", util_rows)
       .replace("@@ROUTEROWS@@", route_rows)
       .replace("@@VEHICLEROWS@@", vehicle_rows)
       .replace("@@CONFROWS@@", conf_rows)
       .replace("@@SRCROWS@@", src_rows)
       .replace("@@DLS@@", dls)
       .replace("@@JS@@", JS)
       .replace("@@ROUTESJS@@", ROUTES_JS)
       .replace("@@VEHICLESJS@@", VEHICLES_JS))
path = os.path.join(SITE, "quotation.html")
open(path, "w", encoding="utf-8").write(out)
print("[OK] quotation.html", len(out) // 1024, "KB")
for k in ["@@", "id=\"calc\"", "id=\"profit\"", "id=\"plans\"", "id=\"routes\"", "id=\"vehicles\"", "id=\"scenes\"", "compute(", "applyRoute(", "applyVehicle("]:
    print("   %-22s → %d" % (k, out.count(k)))
