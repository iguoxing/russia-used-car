# -*- coding: utf-8 -*-
"""统一四页 Tab 互链、补齐下载区与首页入口卡"""
import os, re
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEW_LINKS = (
    '<a href="downloads/russia-quotation-calculator.xlsx" style="display:block;padding:11px 14px;margin:8px 0;'
    'border:1px solid var(--line);border-radius:10px;background:var(--panel2);color:var(--text);text-decoration:none">'
    '<b>报价计算器 Excel 模板</b> <span style="color:var(--muted);font-size:12px">— 带公式，参数可离线迭代（新增）</span></a>'
    '<a href="downloads/russia-export-rules.pdf" style="display:block;padding:11px 14px;margin:8px 0;'
    'border:1px solid var(--line);border-radius:10px;background:var(--panel2);color:var(--text);text-decoration:none">'
    '<b>基本出口规则说明 PDF（15 页）</b> <span style="color:var(--muted);font-size:12px">— 中俄两侧流程与单证（新增）</span></a>'
    '<a href="downloads/russia-export-rules.md" style="display:block;padding:11px 14px;margin:8px 0;'
    'border:1px solid var(--line);border-radius:10px;background:var(--panel2);color:var(--text);text-decoration:none">'
    '<b>基本出口规则说明 Markdown</b> <span style="color:var(--muted);font-size:12px">— 便于二次编辑（新增）</span></a>'
)

NAV_CSS = (
    "\nnav .wrap{flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;scrollbar-width:thin}\n"
    "nav .wrap::-webkit-scrollbar{height:5px}\n"
    "nav .wrap::-webkit-scrollbar-thumb{background:var(--line);border-radius:5px}\n"
    "nav .wrap a,nav .psep{flex:0 0 auto}\n"
)

ENTRY_CARD = (
    '<div class="card" style="margin-top:14px;border-left:4px solid var(--a1);'
    'background:linear-gradient(90deg,rgba(77,156,255,.10),rgba(77,156,255,.02))">'
    '<b style="color:var(--a1)">新增工具：报价计算器 + 出口规则说明 →</b> '
    '<a href="quotation.html" style="font-weight:700">按关税 / 增值税 / 报废税 / 认证实时算 DDP 落地成本与四种口径报价</a>，'
    '可导出中俄文报价单与带公式 Excel 模板；'
    '<a href="rules.html" style="font-weight:700">中俄两侧流程、12 类单证、收汇合规与报价前检查清单</a>。'
    '<span style="color:var(--muted);font-size:12.5px">（2026-11-13 新增）</span></div>'
)


def nav_prefix(active):
    pages = [("index", "index.html", "总览看板"),
             ("segments", "segments.html", "细分市场 · 6 大赛道"),
             ("quotation", "quotation.html", "报价计算器"),
             ("rules", "rules.html", "出口规则说明")]
    return '<nav><div class="wrap">' + "".join(
        '<a class="ptab%s" href="%s">%s</a>' % (' on' if k == active else '', u, t)
        for k, u, t in pages) + '<span class="psep"></span>'


for fn, active in [("index.html", "index"), ("segments.html", "segments"),
                   ("quotation.html", "quotation"), ("rules.html", "rules")]:
    p = os.path.join(SITE, fn)
    s = open(p, encoding="utf-8").read()
    before = len(s)
    m = re.search(r'<nav><div class="wrap">.*?<span class="psep"></span>', s, re.S)
    assert m, fn + " 找不到 nav 前缀"
    s = s[:m.start()] + nav_prefix(active) + s[m.end():]

    # 导航单行横向滚动（避免 4 个 Tab + 多个锚点换成两行）
    if 'nav .wrap{flex-wrap:nowrap' not in s:
        s = s.replace('</style>', NAV_CSS + '</style>', 1)

    # 下载区补 3 个新文件
    a = s.find('<section id="downloads">')
    assert a >= 0, fn + " 找不到下载区"
    b = s.find('</section>', a)
    block = s[a:b]
    if 'russia-quotation-calculator.xlsx' not in block:
        i = block.rfind('</div>')
        assert i > 0, fn + " 下载区无 card div"
        block = block[:i] + NEW_LINKS + block[i:]
        s = s[:a] + block + s[b:]

    # 首页加新工具入口卡
    if fn == "index.html" and '新增工具：报价计算器' not in s:
        j = s.find('</header>')
        assert j > 0
        s = s[:j] + ENTRY_CARD + s[j:]

    open(p, "w", encoding="utf-8").write(s)
    tabs = re.findall(r'class="ptab[^"]*" href="([^"]+)"', s)
    print("[OK] %-16s %3d→%3d KB | Tab %s | 新文件链接 %d" %
          (fn, before // 1024, len(s) // 1024, ",".join(tabs),
           s.count('russia-quotation-calculator.xlsx')))
