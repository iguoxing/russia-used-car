# 俄罗斯汽车平行进口市场分析看板

静态站点，部署于 GitHub Pages，自定义域名：`russia.used-car.cn`

## 内容
- `index.html` — 交互式分析看板（自包含单页，5 张趋势图内嵌，100 家客户可搜索/排序/展开）
- `downloads/russia-parallel-import-report.pdf` — 12 页正式报告
- `downloads/russia-top100-clients.xlsx` — 100 家重点客户名单（6 个工作表）
- `downloads/russia-parallel-import-report.md` — 可编辑 Markdown 文稿

## 数据源
用户提供的 6 份关单 / 进口商名单（2022-08 ~ 2025-03）＋ 2026 年公开市场数据。

关单数据存在时效差，客户名单触达前须做工商与联系方式核验。

## 部署
GitHub Pages 源：main 分支根目录。DNS 需在 DNSPod 添加 CNAME 记录：
`russia.used-car.cn` → `iguoxing.github.io`
