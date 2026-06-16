# Manual Actions + Reconsideration Request 工作流（Platform 防复发版）

> 来源：https://support.google.com/webmasters/answer/9044175?hl=zh-Hans
> 创建：2026-06-10 / 维护：kelly@example.com
> 战略价值：⭐⭐⭐ 某加密交易所行业案例（2026-Q1）后必备 SOP

---

## 一、人工处置措施 18 大类型（速查）

| 类型 | 严重度 | Platform 高风险场景 |
|---|---|---|
| **严重网络垃圾问题（Pure Spam）** | ⚠️⚠️⚠️ 全站影响 | 程序化生成大量低质币种页 / 模板化复用 |
| **被黑网页（Hacked Content）** | ⚠️⚠️⚠️ 安全+SEO 双重 | 被注入菠菜/赌博/色情 keyword |
| **伪装真实内容/欺骗性重定向（Cloaking）** | ⚠️⚠️⚠️ 全站 | A/B test 误判 Googlebot / GeoIP 配置错 |
| **内容贫乏，附加价值低（Thin Content）** | ⚠️⚠️ 某加密交易所案例 L01 同源 | 转载文章未补足原创增量 |
| **结构化数据政策违规** | ⚠️⚠️ 某加密交易所案例 L04 同源 | AggregateRating 字段虚假 |
| 指向网站的非自然链接 | ⚠️⚠️ | 竞品 negative SEO / 买过链接 |
| 来自网站的非自然链接 | ⚠️⚠️ | KOL 联盟链接未加 rel='sponsored' |
| 隐藏文字/关键字堆砌 | ⚠️⚠️ | 前端代码 bug 引入 |
| 用户生成的垃圾内容 | ⚠️ | UGC 评论区未审核 |
| 网站充斥第三方垃圾 | ⚠️ | 文件上传/免费托管被滥用 |
| 伪装真实内容的图片 | ⚠️ | 图片优化服务配置错 |
| 欺骗性移动重定向 | ⚠️ | 第三方广告脚本 / 被黑 |
| 返回按钮劫持 | ⚠️ | 第三方 SDK / 弹窗 |
| AMP 内容不匹配 | ℹ️（AMP 淘汰中）| 不再适用 |
| Google 新闻/Discover 政策违规 | ⚠️⚠️ | 危险内容/仇恨/露骨 |

---

## 二、Reconsideration Request 标准模板

Google 文档明确要求重新审核请求包含三个要素：

```markdown
## 1. 准确阐释网站上存在的质量问题

**问题类型**：[选择对应的 manual action 类型]
**影响范围**：[具体哪些 URL pattern 受影响]
**根因分析**：[为什么会发生 — 注意：不是甩锅给"前员工""第三方"等]

## 2. 描述您为修正问题所采取的措施

**已删除/修正的内容**：
- URL X: 已删除转载内容，添加 cross-domain canonical 到原文
- URL Y: 已删除 AggregateRating schema 字段

**已实施的预防措施**：
- 上线 Multi-Engine SEO Audit Skill Pre-publish Gate（防复发）
- 添加每周 Watch 全站 audit
- ContentForge 集成 audit pre-check

## 3. 记录您在采取措施后获得的成果

**修复后的证据**：
- Multi-Engine SEO Audit Skill 跑 audit 输出（含 0 blocker / 0 high finding）
- 截图：受影响页面修复前后对比
- GSC URL 检查工具显示已修复
- 流量恢复趋势图（如适用）
```

---

## 三、重新审核流程时间预期

| 类型 | 预计审核时间 |
|---|---|
| 一般 manual action | 几天 ~ 几周 |
| 链接相关 reconsideration | 比平时更长（可能数月）|
| Pure Spam 重审 | 数月（最难恢复）|

**重要约束**：
- 收到审核确认邮件后**不要**重复提交
- 等 Google 给出最终决定后再行动
- 一次性提交完整修复证据（不要分次提交）

---

## 四、Platform 防复发 SOP

### 4.1 主动监控（每日）
- 检查 GSC「人工处置措施」报告（必须有 GSC 服务账号）
- 跑 `seo-audit watch` 命令
- Slack 告警监听

### 4.2 被动响应（收到通知后 1 小时内）
1. 立即在 Slack 通知 Kelly + Will + CTO
2. 在 Search Console 中展开处置说明
3. 列出所有受影响 URL pattern
4. 启动 audit `--mode forensic` 全站扫描

### 4.3 修复阶段（1-7 天）
1. 用 Multi-Engine SEO Audit Skill 检出根因
2. 应用 patch 模板（已有 11 个）
3. 跑 `seo-audit audit <修复后 URL>` 验证 0 blocker
4. 跑 golden fixture 测试不退化
5. Will 团队人工 review

### 4.4 提交 Reconsideration（修复完成后）
1. 用上述「标准模板」准备文档
2. 附 Multi-Engine SEO Audit Report（PDF/JSON）作证据
3. Kelly 在 GSC 提交
4. 邮件归档审核确认信
5. 进入等待期

### 4.5 处置撤销后
1. 跑全站 `seo-audit watch` 确认未退化
2. 在 `tasks/lessons.md` 记录完整复盘
3. 在 `rules/platform/google-action-history.md` 增加案例
4. 沉淀新规则（避免下次再犯）

---

## 五、与 Multi-Engine SEO Audit Skill 的对接

| Skill 能力 | 用于 Manual Action 流程的哪一步 |
|---|---|
| `audit <url>` | 4.3 修复阶段 + 4.5 验证 |
| `gate <md>` | 4.2 防复发 — Pre-publish 卡审 |
| `watch <site>` | 4.1 主动监控 |
| Brand SEO Score | 4.5 量化恢复程度 |
| Patch templates | 4.3 修复阶段自动 patch |
| Lessons.md | 4.5 复盘沉淀 |
| Google action history | 4.5 案例库扩充 |

---

## 六、Will 团队 vs 我们 Skill 的协同

| 任务 | Will 团队负责 | Skill 负责 |
|---|---|---|
| 监控 GSC 人工处置通知 | ✅ Kelly 收邮件 | ✅ watch 命令 |
| 根因分析 | ✅ 人工 review | ✅ audit 自动定位 |
| 修复执行 | ✅ 编辑/开发 | ✅ patch 模板 |
| 验证修复 | ✅ 人工 spot check | ✅ audit 0 blocker 验证 |
| Reconsideration 文档 | ✅ Kelly 撰写 | ✅ 自动生成 SEO 报告作附件 |
| 复盘 + 规则沉淀 | ✅ Will 写知识库 | ✅ lessons.md + rules/ 沉淀 |

---

## 七、新增规则文件

本知识 MD 对应的可执行规则：
`platforms/google/_rules/manual-actions-prevention.yaml`（15 条规则）

每条规则都对应一种 manual action 类型的预防 + 检测。
