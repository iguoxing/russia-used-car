# -*- coding: utf-8 -*-
"""生成 russia-quotation-calculator.xlsx —— 带公式的离线报价模板"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from rules_data import (PARAMS, SOURCES, UTIL_COMMERCIAL, UTIL_PERSONAL_NEW,
                        UTIL_PERSONAL_OLD, EXCISE, CUSTOMS_FEE, FREIGHT_PRESETS,
                        DOCS, FLOW_CN, FLOW_RU, TIMELINE, PITFALLS, CHECKLIST,
                        CONFLICTS, RATE_DATE)
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.properties import CalcProperties

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "downloads", "russia-quotation-calculator.xlsx")

NAVY = "1B3350"; LIGHT = "F2F6FB"; YEL = "FFF3D6"; GRN = "E4F6EF"; GREY = "EDF1F6"
hf = PatternFill("solid", fgColor=NAVY)
hfont = Font(name="Arial", size=10, bold=True, color="FFFFFF")
cf = Font(name="Arial", size=10)
bf = Font(name="Arial", size=10, bold=True)
title_f = Font(name="Arial", size=13, bold=True, color=NAVY)
note_f = Font(name="Arial", size=9, color="66788C")
input_fill = PatternFill("solid", fgColor=YEL)
calc_fill = PatternFill("solid", fgColor=GRN)
alt_fill = PatternFill("solid", fgColor=LIGHT)
sec_fill = PatternFill("solid", fgColor=GREY)
thin = Side(style="thin", color="D5DEE8")
bd = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = openpyxl.Workbook()
wb.remove(wb.active)
try:
    wb.calculation = CalcProperties(calcMode="auto", fullCalcOnLoad=True, forceFullCalc=True)
except Exception:
    pass


def head(ws, row, labels, widths=None):
    for i, t in enumerate(labels, 1):
        c = ws.cell(row, i, t)
        c.fill = hf; c.font = hfont; c.border = bd
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 30
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def put(ws, row, values, fills=None, fmt=None, height=None):
    for i, v in enumerate(values, 1):
        c = ws.cell(row, i, v)
        c.font = cf; c.border = bd
        c.alignment = Alignment(vertical="top", wrap_text=True)
        if fills and i in fills:
            c.fill = fills[i]
        elif row % 2 == 0:
            c.fill = alt_fill
        if fmt and i in fmt:
            c.number_format = fmt[i]
    if height:
        ws.row_dimensions[row].height = height


# ================= Sheet 1 报价计算器 =================
w = wb.create_sheet("报价计算器")
w.sheet_view.zoomScale = 85
w.merge_cells("A1:G1")
w["A1"] = "俄罗斯整车出口报价计算器｜带公式模板（" + RATE_DATE + " 参数）"
w["A1"].font = title_f
w.row_dimensions[1].height = 28
w.merge_cells("A2:G2")
w["A2"] = ("黄色单元格 = 可改输入；绿色 = Excel 自动计算；「静态示例值」列由生成脚本预算，方便未打开 Excel 时预览。"
           "所有税率为公开资料参考值，正式报价前必须由俄方持牌报关行按 HS 子目书面核定。")
w["A2"].font = note_f
w["A2"].alignment = Alignment(wrap_text=True, vertical="center")
w.row_dimensions[2].height = 32

head(w, 4, ["输入参数", "值", "单位", "说明", "计算项", "公式结果", "静态示例值"],
     [26, 15, 11, 46, 30, 18, 18])

INPUTS = [
    ("车价（含税采购价）", 128000, "CNY", "二手车以收购发票价为准；如用 USD 计价请自行换算"),
    ("CNY / USD", 6.70, "汇率", "由俄央行 2026-11-12 交叉价推算，请填实际结汇价"),
    ("USD / RUB", 82.98, "汇率", "俄央行 2026-11-13 官方 82.9803"),
    ("中国出口本地费", 300, "USD", "报关、许可证、拖车、装卸、单证（单台分摊）"),
    ("国际运费", 4000, "USD", "铁路班列预设；海运 2500 / TIR 1200 / 整箱 3000"),
    ("保险费率", 0.003, "比率", "基数 = FOB + 运费"),
    ("海关估价调整", 0, "比率", "俄海关可按市场价重新估价；低报有罚款风险"),
    ("进口关税率", 0.20, "比率", "2025-01 起 20–38%；另有 15–25% 从价口径，须核定"),
    ("增值税 НДС", 0.22, "比率", "425-ФЗ 2026-01-01 起 22%；部分资料仍写 20%"),
    ("报废税基准费率", 20000, "RUB", "乘用车 20000；卡车/客车/挂车 150000"),
    ("报废税系数", 12.95, "系数", "按排量/车龄/主体查「税率查表」；功率 >160hp 须另核"),
    ("消费税总额", 9450, "RUB", "150hp × 63 ₽/hp；或按「税率查表」手算后填入"),
    ("清关手续费", 13541, "RUB", "2026 第 1638 号决议 8 档；见「税率查表」"),
    ("СБКТС / ОТТС 认证", 40000, "RUB", "无 ОТТС 时逐车 100000–250000"),
    ("报关代理 + 装卸", 40000, "RUB", "含 PRR 25000–35000"),
    ("俄境内运输", 0, "RUB", "DDP 才计入；海参崴→莫斯科 150000–250000"),
    ("PDI / 整备 / 仓储", 15000, "RUB", "冬季适配、防腐、俄语车机"),
    ("质保售后准备金率", 0.02, "比率", "基数 = 车价 RUB；平行进口无原厂质保"),
    ("其他杂费", 0, "RUB", ""),
    ("目标毛利率", 0.12, "比率", "毛利率法：报价 = 成本 ÷ (1 − 毛利率)"),
    ("出口退税率", 0.13, "比率", "计入我方收益，不影响对客报价"),
    ("数量", 1, "台", ""),
    ("车型 / 配置", "中国产 SUV 1.5T / 150hp", "文本", "会写进报价描述"),
]
for i, (n, v, u, d) in enumerate(INPUTS, 5):
    put(w, i, [n, v, u, d], fills={2: input_fill}, height=25)
    if isinstance(v, float) and v < 1:
        w.cell(i, 2).number_format = "0.000%"

# B 列行号映射
B = {name: i for i, (name, *_rest) in enumerate(INPUTS, 5)}
R = lambda name: "$B$%d" % B[name]

CALC = [
    ("车价 USD", "={0}/{1}".format(R("车价（含税采购价）"), R("CNY / USD")), "priceUSD"),
    ("FOB USD", "=F5+" + R("中国出口本地费"), "fobUSD"),
    ("保险 USD", "=(F6+" + R("国际运费") + ")*" + R("保险费率"), "insurance"),
    ("CIF USD", "=F6+" + R("国际运费") + "+F7", "cifUSD"),
    ("车价 RUB", "=F5*" + R("USD / RUB"), "carRUB"),
    ("出口本地费 RUB", "=" + R("中国出口本地费") + "*" + R("USD / RUB"), "localRUB"),
    ("运费保险 RUB", "=(" + R("国际运费") + "+F7)*" + R("USD / RUB"), "frtRUB"),
    ("CIF RUB", "=SUM(F9:F11)", "cifRUB"),
    ("海关估价调整 RUB", "=F12*" + R("海关估价调整"), "adjRUB"),
    ("完税价格 RUB", "=F12+F13", "declared"),
    ("进口关税", "=F14*" + R("进口关税率"), "duty"),
    ("消费税", "=" + R("消费税总额"), "excise"),
    ("增值税 НДС", "=(F14+F15+F16)*" + R("增值税 НДС"), "vat"),
    ("报废税", "=" + R("报废税基准费率") + "*" + R("报废税系数"), "util"),
    ("清关手续费", "=" + R("清关手续费"), "cfee"),
    ("认证/代理/内陆/PDI/质保", "=" + "+".join([R(x) for x in
        ["СБКТС / ОТТС 认证", "报关代理 + 装卸", "俄境内运输", "PDI / 整备 / 仓储", "其他杂费"]])
     + "+F9*" + R("质保售后准备金率"), "svc"),
    ("DDP 落地成本", "=F14+F15+F16+F17+F18+F19+F20", "landed"),
    ("俄方税费合计", "=SUM(F15:F19)", "taxTotal"),
    ("税费占落地成本", "=F22/F21", "taxShare"),
    ("EXW 成本", "=F9", "exw"),
    ("FOB 成本", "=F9+F10", "fob"),
    ("CIF 成本", "=F12", "cif"),
    ("建议报价 EXW", "=F24/(1-" + R("目标毛利率") + ")", "qExw"),
    ("建议报价 FOB", "=F25/(1-" + R("目标毛利率") + ")", "qFob"),
    ("建议报价 CIF", "=F26/(1-" + R("目标毛利率") + ")", "qCif"),
    ("建议报价 DDP", "=F21/(1-" + R("目标毛利率") + ")", "qDdp"),
    ("中国出口退税收益 RUB", "=" + R("车价（含税采购价）") + "/1.13*" + R("出口退税率")
     + "/" + R("CNY / USD") + "*" + R("USD / RUB"), "refund"),
    ("我方毛利（CIF 口径）", "=F29-(F26-F31)", "profit"),
    ("批量总价（CIF 口径）", "=F29*" + R("数量"), "total"),
]
for i, (n, f, key) in enumerate(CALC, 5):
    c1 = w.cell(i, 5, n); c1.font = cf; c1.border = bd
    c1.alignment = Alignment(vertical="center", wrap_text=True)
    c2 = w.cell(i, 6, f); c2.font = bf; c2.border = bd; c2.fill = calc_fill
    c2.number_format = "#,##0.00"
    if key == "taxShare":
        c2.number_format = "0.0%"
    c3 = w.cell(i, 7); c3.font = cf; c3.border = bd; c3.number_format = "#,##0"
    if key == "taxShare":
        c3.number_format = "0.0%"

# 静态示例值（Python 独立复算）
p = {name: v for name, v, _u, _d in INPUTS}
r = p["USD / RUB"]; cny = p["CNY / USD"]
priceUSD = p["车价（含税采购价）"] / cny
fobUSD = priceUSD + p["中国出口本地费"]
insurance = (fobUSD + p["国际运费"]) * p["保险费率"]
cifUSD = fobUSD + p["国际运费"] + insurance
carRUB = priceUSD * r; localRUB = p["中国出口本地费"] * r
frtRUB = (p["国际运费"] + insurance) * r
cifRUB = carRUB + localRUB + frtRUB
adjRUB = cifRUB * p["海关估价调整"]; declared = cifRUB + adjRUB
duty = declared * p["进口关税率"]; excise = p["消费税总额"]
vat = (declared + duty + excise) * p["增值税 НДС"]
util = p["报废税基准费率"] * p["报废税系数"]; cfee = p["清关手续费"]
svc = (p["СБКТС / ОТТС 认证"] + p["报关代理 + 装卸"] + p["俄境内运输"] +
       p["PDI / 整备 / 仓储"] + p["其他杂费"] + carRUB * p["质保售后准备金率"])
landed = declared + duty + excise + vat + util + cfee + svc
taxTotal = duty + excise + vat + util + cfee
fac = 1 / (1 - p["目标毛利率"])
refund = p["车价（含税采购价）"] / 1.13 * p["出口退税率"] / cny * r
static = dict(priceUSD=priceUSD, fobUSD=fobUSD, insurance=insurance, cifUSD=cifUSD,
              carRUB=carRUB, localRUB=localRUB, frtRUB=frtRUB, cifRUB=cifRUB,
              adjRUB=adjRUB, declared=declared, duty=duty, excise=excise, vat=vat,
              util=util, cfee=cfee, svc=svc, landed=landed, taxTotal=taxTotal,
              taxShare=taxTotal / landed, exw=carRUB, fob=carRUB + localRUB, cif=cifRUB,
              qExw=carRUB * fac, qFob=(carRUB + localRUB) * fac, qCif=cifRUB * fac,
              qDdp=landed * fac, refund=refund, profit=cifRUB * fac - (cifRUB - refund),
              total=cifRUB * fac * p["数量"])
for i, (n, f, key) in enumerate(CALC, 5):
    w.cell(i, 7, round(static[key], 2))

# 成本阶梯表
sr = 38
w.merge_cells(start_row=sr - 1, start_column=1, end_row=sr - 1, end_column=6)
w.cell(sr - 1, 1, "成本阶梯（公式引用上方计算区，改任一输入自动重算）").font = title_f
head(w, sr, ["#", "成本项目", "金额 RUB（公式）", "静态示例值", "占落地成本", "贸易术语边界"])
STAGES = [
    (1, "车价 EXW", "=F9", carRUB, "EXW"),
    (2, "中国出口本地费", "=F10", localRUB, "FOB"),
    (3, "国际运费 + 保险", "=F11", frtRUB, "CIF"),
    (4, "海关估价调整", "=F13", adjRUB, "俄方清关"),
    (5, "进口关税", "=F15", duty, "俄方清关"),
    (6, "消费税", "=F16", excise, "俄方清关"),
    (7, "增值税 НДС", "=F17", vat, "俄方清关"),
    (8, "报废税", "=F18", util, "俄方清关"),
    (9, "清关手续费", "=F19", cfee, "俄方清关"),
    (10, "认证/代理/内陆/PDI/质保", "=F20", svc, "DDP 落地"),
]
for i, (n, name, f, val, term) in enumerate(STAGES, sr + 1):
    put(w, i, [n, name, f, round(val), "=C%d/$C$%d" % (i, sr + 11), term],
        fills={3: calc_fill}, fmt={3: "#,##0", 4: "#,##0", 5: "0.0%"}, height=22)
last = sr + 11
put(w, last, ["", "DDP 落地成本合计", "=SUM(C%d:C%d)" % (sr + 1, last - 1),
              round(landed), "=C%d/$C$%d" % (last, last), "应与 F21 一致"],
    fills={3: calc_fill}, fmt={3: "#,##0", 4: "#,##0", 5: "0.0%"}, height=24)
for c in w[last]:
    c.font = bf; c.fill = sec_fill
w.merge_cells(start_row=last + 2, start_column=1, end_row=last + 2, end_column=6)
w.cell(last + 2, 1, "注意：DDP 需俄方具备进口主体与清关资质，中方一般不能直接作为俄进口商；"
       "首单建议 FOB/CIF + 俄方指定清关代理。报废税系数每年 1 月调整，2027-01-01 预计再涨 10–20%。").font = note_f
w.row_dimensions[last + 2].height = 28
w.freeze_panes = "A5"

# ================= Sheet 2 参数与来源 =================
w2 = wb.create_sheet("参数与来源")
w2.merge_cells("A1:F1"); w2["A1"] = "默认参数、口径说明与数据来源"; w2["A1"].font = title_f
head(w2, 3, ["参数", "默认值", "单位", "等级", "来源", "说明"], [26, 15, 12, 10, 12, 78])
for i, (a, b, c, d, e, f) in enumerate(PARAMS, 4):
    put(w2, i, [a, b, c, d, e, f], height=30)
r = 4 + len(PARAMS) + 2
w2.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
w2.cell(r, 1, "数据来源清单").font = title_f
head(w2, r + 1, ["编号", "来源", "关键内容", "等级", "链接", ""])
for i, (a, b, c, d, e) in enumerate(SOURCES, r + 2):
    put(w2, i, [a, b, c, d, e, ""], height=42)
w2.freeze_panes = "A4"

# ================= Sheet 3 税率查表 =================
w3 = wb.create_sheet("税率查表")
w3.merge_cells("A1:E1"); w3["A1"] = "报废税 / 消费税 / 清关手续费查表"; w3["A1"].font = title_f
head(w3, 3, ["排量档", "≤3 年系数", ">3 年系数", "新车报废税 RUB", "旧车报废税 RUB"], [22, 16, 16, 20, 20])
for i, (lo, hi, a, b, n) in enumerate(UTIL_COMMERCIAL, 4):
    put(w3, i, [n, a, b, int(20000 * a), int(20000 * b)], height=22)
r = 10
w3.cell(r, 1, "个人自用优惠档：≤3 年 0.17（3,400 ₽）、>3 年 0.26（5,200 ₽）；须同时满足 ≤3.0L / ≤160hp / 一年 1 辆 / 12 个月不转售。功率过 160hp 即转商业系数。").font = note_f
w3.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
w3.row_dimensions[r].height = 28
head(w3, r + 2, ["消费税马力档", "单价 RUB/hp", "边界处理", "", ""], [22, 16, 42, 20, 20])
for i, (lo, hi, v) in enumerate(EXCISE, r + 3):
    put(w3, i, ["%s–%s hp" % (lo, "∞" if hi > 10000 else hi), v,
                "按上界闭合（≤%s 归本档）" % ("∞" if hi > 10000 else hi), "", ""], height=22)
r2 = r + 3 + len(EXCISE) + 1
head(w3, r2, ["清关手续费：完税价格上限 RUB", "手续费 RUB", "依据", "", ""], [30, 16, 44, 20, 20])
for i, (lim, v) in enumerate(CUSTOMS_FEE, r2 + 1):
    put(w3, i, ["≤ %s" % ("10,000,000+" if lim > 1e12 else f"{lim:,}"), v,
                "2026-01-01 起第 1638 号决议", "", ""], height=22)
r3 = r2 + len(CUSTOMS_FEE) + 3
head(w3, r3, ["运输方式", "单台运费 USD", "时效 / 说明", "", ""], [30, 16, 60, 20, 20])
for i, (k, t, v, n) in enumerate(FREIGHT_PRESETS, r3 + 1):
    put(w3, i, [t, v, n, "", ""], height=30)
w3.freeze_panes = "A4"

# ================= Sheet 4 出口单证清单 =================
w4 = wb.create_sheet("出口单证清单")
w4.merge_cells("A1:E1"); w4["A1"] = "中俄两侧单证清单（按环节）"; w4["A1"].font = title_f
head(w4, 3, ["环节", "单证 / 材料", "办理时点", "来源", "等级"], [16, 76, 24, 14, 10])
for i, (a, b, c, d, e) in enumerate(DOCS, 4):
    put(w4, i, [a, b, c, d, e], height=40)
w4.freeze_panes = "A4"; w4.auto_filter.ref = "A3:E%d" % (3 + len(DOCS))

# ================= Sheet 5 中俄流程 =================
w5 = wb.create_sheet("中俄流程")
w5.merge_cells("A1:E1"); w5["A1"] = "中国出口侧 7 步 + 俄罗斯进口侧 6 步"; w5["A1"].font = title_f
head(w5, 3, ["侧", "步骤", "动作", "要点", "来源 / 等级"], [14, 8, 24, 92, 16])
for side, arr in [("中国出口", FLOW_CN), ("俄罗斯进口", FLOW_RU)]:
    start = w5.max_row + 1 if w5.max_row > 3 else 4
    for i, (n, t, d, s, g) in enumerate(arr, start):
        put(w5, i, [side, n, t, d, "%s / %s" % (s, g)], height=56)
w5.freeze_panes = "A4"

# ================= Sheet 6 时间线与风险 =================
w6 = wb.create_sheet("时间线与风险")
w6.merge_cells("A1:E1"); w6["A1"] = "政策时间线 / 常见坑 / 报价前检查 / 口径冲突"; w6["A1"].font = title_f
head(w6, 3, ["日期", "内容", "依据", "等级", "备注"], [16, 62, 26, 10, 62])
for i, (d, t, s, g, n) in enumerate(TIMELINE, 4):
    put(w6, i, [d, t, s, g, n], height=38)
r = 4 + len(TIMELINE) + 1
head(w6, r, ["常见坑", "说明", "来源", "等级", ""], [30, 92, 18, 10, 20])
for i, (t, d, s, g) in enumerate(PITFALLS, r + 1):
    put(w6, i, [t, d, s, g, ""], height=48)
r2 = r + len(PITFALLS) + 2
head(w6, r2, ["报价前检查", "内容", "", "", ""], [16, 100, 20, 10, 20])
for i, c in enumerate(CHECKLIST, r2 + 1):
    put(w6, i, ["☐", c, "", "", ""], height=26)
r3 = r2 + len(CHECKLIST) + 2
head(w6, r3, ["口径冲突", "两种记载", "处理方式", "", ""], [30, 76, 62, 10, 20])
for i, (a, b, c) in enumerate(CONFLICTS, r3 + 1):
    put(w6, i, [a, b, c, "", ""], height=52)
w6.freeze_panes = "A4"

wb.save(OUT)
print("[OK] russia-quotation-calculator.xlsx", os.path.getsize(OUT) // 1024, "KB")
print("     工作表:", wb.sheetnames)
print("     静态校验: DDP 落地 %.0f ₽ / CIF 报价 %.0f ₽ / 税费占比 %.1f%%" %
      (landed, static["qCif"], taxTotal / landed * 100))
