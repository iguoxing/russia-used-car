# 俄罗斯汽车平行进口市场分析看板

静态站点，部署于 GitHub Pages，自定义域名：`russia.used-car.cn`

## 页面（顶部 Tab 切换）
- `index.html` — **总览看板**：四维信号、趋势图、100 家客户可搜索/排序/展开、数据核验 v2、第 10 章分析逻辑复核
- `segments.html` — **细分市场 · 6 大赛道**（2026-11-13 新增）：乘用车 / 摩托车·ATV·雪地车 / 新能源 / 皮卡越野 / 房车旅居车 / 商用车；含加权机会评分、品类 Tab、内部关单价位带、政策矩阵、TOP100 客户联动、18 条来源与证据等级

## 下载文件
| 文件 | 内容 |
|---|---|
| `russia-parallel-import-report.pdf` | 主报告，17 页 |
| `russia-top100-clients.xlsx` | TOP100 客户，8 个工作表（含 v3 维度优化示范） |
| `russia-parallel-import-report.md` | 主报告 Markdown |
| `data-verification-report.md` | 第一轮数据核验底稿 v2 |
| `review-and-dimension-optimization.md` | 第二轮复核与维度优化建议 |
| `russia-segment-analysis.pdf` | **细分市场报告，16 页（打印友好白底版）** |
| `russia-segment-analysis.xlsx` | **细分市场数据表，5 个工作表** |
| `russia-segment-analysis.md` | **细分市场报告 Markdown** |

`charts/chart1~5.webp` — 5 张趋势图（WebP + 懒加载，替代原先的 base64 内嵌，避免国内链路大响应被截断）。

> 本地 `~/Desktop/俄罗斯/分析输出/俄罗斯平行进口分析看板.html` 仍是自包含单文件版（图片 base64 内嵌），适合离线发送；线上版为提速做了拆分。新增的细分市场页仅在线上站点与 downloads 中，桌面目录因系统权限未同步。

## 数据口径
- 6 份源表（2022-08 ~ 2025-03）：5,000 行明细 HS 全为 8703 乘用车，1,084 条转口明细为 ATV/雪地车/迷你摩托；**商用车、房车、新能源、皮卡无内部关单证据**，其规模数据来自外部公开来源并标注 A/B/C 证据等级。
- 385 家经中亚名单不含原产国字段，只代表第三国转口渠道能力，不代表买过中国车。
- 关单最新 2025-03，距今约 20 个月；TOP100 中 0 家有电话/邮箱，仅 64 家有 INN。名单定位为「待验真线索池」。
- 2026-04-01 EAEU 补差新规存在「已生效 / 推迟无生效日」两种记载，报价前须核俄政府令原文。

## 部署
GitHub Pages 源：main 分支根目录。DNS（DNSPod）已添加 CNAME：
`russia.used-car.cn` → `iguoxing.github.io`

更新内容：改本目录文件后 `git push origin main`，Pages 自动重建。若遇大文件推送 HTTP 400，本仓库已设 `http.postBuffer=524288000`、`http.version=HTTP/1.1`。
