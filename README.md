# 俄罗斯汽车出口 · 分析与报价工具站

静态站点，部署于 GitHub Pages，自定义域名：`https://russia.used-car.cn`

一句话分工：**总览看板讲「找谁」→ 细分市场讲「卖什么」→ 报价计算器讲「怎么报价」→ 出口规则说明讲「怎么合规走完一单」**。

## 页面（单页 Tab 菜单工作台，4 个模块）

打开 `https://russia.used-car.cn/` 就是 **Tab 菜单页**：顶部 4 个菜单原地切换，不跳页、不丢计算器参数；第二行是当前模块的章节快捷导航，右侧可刷新 / 打印 / 独立打开本模块。URL 支持 `#/quotation`、`#/rules`、`#/segments` 直达并可分享；旧链接如 `index.html#clients` 会自动落到总览对应章节。

`index.html` 是 Tab 容器（懒加载 iframe + 高度自适应 + hash 路由），4 个子页带 `?embed=1` 时自动隐藏自身导航并把模块互链 / 锚点交给容器接管；不带参数时仍是可独立访问、打印、分享的完整页面。

| Tab | 独立页面 | 内容 |
|---|---|---|
| 01 总览看板 | `analysis.html` | 四维信号、趋势图、100 家客户可搜索/排序/展开、数据核验 v2、第 10 章分析逻辑复核与 v3 维度优化 |
| 02 细分市场 | `segments.html` | **6 大赛道**（2026-11-13）：乘用车 / 摩托·ATV·雪地车 / 新能源 / 皮卡越野 / 房车旅居车 / 商用车；加权机会评分、品类 Tab、内部关单价位带、政策矩阵、TOP100 客户联动、18 条来源 A/B/C 分级 |
| 03 报价计算器 | `quotation.html` | （2026-11-13 新增）30+ 可编辑参数，实时算 CIF / 关税 / 消费税 / 增值税 / 报废税 / 清关费 / 认证 / 落地成本；四种贸易术语报价、成本阶梯与承担方、7 组情景敏感性、中/俄文报价单一键复制、CSV 导出、参数本机保存、4 个车型预设（支持 `?preset=power` 等链接直达） |
| 04 出口规则说明 | `rules.html` | （2026-11-13 新增）中方 7 步 / 俄方 6 步流程、12 类单证清单、认证（ОТТС/СБКТС/ЭПТС/ЭРА-ГЛОНАСС）、收汇与制裁合规、2024–2027 政策时间线、8 个常见坑、可勾选的报价前十项检查清单 |

## 下载文件（`downloads/`）

| 文件 | 内容 |
|---|---|
| `russia-quotation-calculator.xlsx` | **报价计算器 Excel 模板，6 个工作表**（2026-11-13 新增）：黄色输入 / 绿色公式，改参数自动重算；含参数与来源、税率查表、单证清单、中俄流程、时间线与风险 |
| `russia-export-rules.pdf` | **基本出口规则说明 PDF，15 页**（新增，打印友好白底版） |
| `russia-export-rules.md` | **基本出口规则说明 Markdown**（新增） |
| `russia-parallel-import-report.pdf` | 主报告，17 页 |
| `russia-top100-clients.xlsx` | TOP100 客户，8 个工作表（含 v3 维度优化示范） |
| `russia-parallel-import-report.md` | 主报告 Markdown |
| `data-verification-report.md` | 第一轮数据核验底稿 v2 |
| `review-and-dimension-optimization.md` | 第二轮复核与维度优化建议 |
| `russia-segment-analysis.pdf` | 细分市场报告，16 页 |
| `russia-segment-analysis.xlsx` | 细分市场数据表，5 个工作表 |
| `russia-segment-analysis.md` | 细分市场报告 Markdown |

`charts/chart1~5.webp` — 5 张趋势图（WebP + 懒加载，替代原先的 base64 内嵌，避免国内链路大响应被截断）。

> 本地 `~/Desktop/俄罗斯/分析输出/俄罗斯平行进口分析看板.html` 仍是自包含单文件版（图片 base64 内嵌），适合离线发送。2026-11-12 之后新增的细分市场、报价计算器、规则说明只在站点与 `downloads/` 中；当时系统权限拒绝写入桌面目录，请直接从线上下载区保存。

## 报价计算器口径（重要）

- **汇率**：USD/RUB 82.98（俄央行 2026-11-13 官方）、CNY/USD 6.70（由俄央行交叉价推算示例，请填实际结汇价）。
- **税费**：关税 20%（15–25% 与 20–38% 两种口径并存）、增值税 22%（425-ФЗ 2026-01-01 起；部分资料仍写 20%）、报废税 = 20,000 ₽ × 系数（按排量 / 车龄 / 主体查表，个人优惠 0.17 / 0.26 需 ≤3 年 + ≤3.0L + ≤160hp）、消费税按马力阶梯、清关费按 2026 第 1638 号决议 8 档。
- **公式**：FOB = 车价 + 出口本地费；CIF = FOB + 运费 + 保险；VAT = (完税价 + 关税 + 消费税) × 税率；报废税单列不计入 VAT 基数；报价 = 该术语累计成本 ÷ (1 − 毛利率)；我方毛利含 13% 出口退税。全部公式在 `quotation.html` 第 04 章与 Excel 模板中公开。
- **四处口径冲突**：增值税 20/22%、关税 15–25% vs 20–38%、EAEU 补差新规是否生效、报废税上调年份。计算器给默认值但**不替业务拍板**，正式报价须由俄方持牌报关行按 HS 子目书面核定；2027-01-01 报废税预计再涨 10–20%，长周期合同必须留调价条款。
- **这不是报关系统**：所有参数标注来源编号与 A/B/C 证据等级，见页面「参数来源」「数据来源」章节。

## 数据口径（分析部分）

- 6 份源表（2022-08 ~ 2025-03）：5,000 行明细 HS 全为 8703 乘用车，1,084 条转口明细为 ATV/雪地车/迷你摩托；**商用车、房车、新能源、皮卡无内部关单证据**，其规模数据来自外部公开来源并标注证据等级。
- 385 家经中亚名单不含原产国字段，只代表第三国转口渠道能力，不代表买过中国车。
- 关单最新 2025-03；TOP100 中 0 家有电话/邮箱，仅 64 家有 INN。名单定位为「待验真线索池」。

## 构建与复算（`tools/`）

```bash
python3 tools/build_calculator.py   # 生成 quotation.html
python3 tools/build_rules.py        # 生成 rules.html + downloads/russia-export-rules.md
python3 tools/build_xlsx.py         # 生成 downloads/russia-quotation-calculator.xlsx
python3 tools/patch_site.py         # 统一子页 Tab / 下载区 / 首页入口卡（前两步之后必须跑）
python3 tools/build_tabs.py         # 最后跑：生成 Tab 容器 index.html + analysis.html，给 4 个子页注入 embed 模式（幂等，可反复运行）
```

`build_tabs.py` 必须放在 `patch_site.py` 之后：后者会重写各页 `<nav>`，会覆盖嵌入模式下的导航改写。

`tools/rules_data.py` 是所有参数、来源、流程、单证、时间线与风险提示的唯一数据源，改这里即可全局重算。规则 PDF 由 Chrome headless 打印 `rules.html` 生成（页面已内置 `@media print` 白底样式）。

本地自检（需先起 `python3 -m http.server`）：`index.html?selftest=1` 依次加载 4 个 Tab 并输出高度 / 标题 / 章节数；`index.html?selftest=2` 验证互链接管、章节跳转与计算器在 Tab 内可算。

## 部署

GitHub Pages 源：main 分支根目录。DNS（DNSPod）CNAME：`russia.used-car.cn` → `iguoxing.github.io`。

更新内容：`git push origin main`，Pages 自动重建。若遇大文件推送 HTTP 400，本仓库已设 `http.postBuffer=524288000`、`http.version=HTTP/1.1`。
