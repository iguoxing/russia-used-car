# 俄罗斯汽车平行进口市场分析看板

静态站点，部署于 GitHub Pages，自定义域名：`russia.used-car.cn`

## 内容
- `index.html` — 交互式分析看板（8 个章节，100 家客户可搜索/排序/展开）；gzip 后约 26 KB
- `charts/chart1~5.webp` — 5 张趋势图（WebP + 懒加载，替代原先的 base64 内嵌，避免国内链路大响应被截断）
- `downloads/russia-parallel-import-report.pdf` — 12 页正式报告
- `downloads/russia-top100-clients.xlsx` — 100 家重点客户名单（6 个工作表）
- `downloads/russia-parallel-import-report.md` — 可编辑 Markdown 文稿

> 本地 `~/Desktop/俄罗斯/分析输出/俄罗斯平行进口分析看板.html` 仍是自包含单文件版（图片 base64 内嵌），适合离线发送；线上版为提速做了拆分，内容一致。

## 数据源
用户提供的 6 份关单 / 进口商名单（2022-08 ~ 2025-03）＋ 2026 年公开市场数据。
关单数据存在时效差，客户名单触达前须做工商与联系方式核验。

## 部署
GitHub Pages 源：main 分支根目录。DNS（DNSPod）已添加 CNAME：
`russia.used-car.cn` → `iguoxing.github.io`

更新内容：改本目录文件后 `git push origin main`，Pages 自动重建。
