# 网站迁移 SOP（Platform 防 SEO 流量崩盘版）

> 来源：https://developers.google.com/search/docs/crawling-indexing/site-move-no-url-changes
> 创建：2026-06-10 / 维护：kelly@example.com
> 适用场景：Platform 切换 CDN / 迁移服务器 / 跨云迁移（无 URL 变化）

---

## 一、什么时候用本 SOP

- 切 Cloudflare → 别的 CDN
- 切 AWS → GCP / Azure
- 切 fly.io → 别的 PaaS
- 增加新 PoP（韩国/俄罗斯节点）
- **任何不改 URL 的基础架构变化**

> URL 会变？看「网站重定向迁移」文档（另一份）

---

## 二、迁移 4 阶段（Google 官方流程）

```
准备新基础架构 → 开始迁移 → 监控流量 → 关闭旧基础架构
```

---

## 三、Pre-Migration Checklist（迁移前 1-2 周）

### 1. 新环境准备
- [ ] 上传/同步所有内容到新服务器/CDN
- [ ] 创建测试环境（按 IP 限制访问）
- [ ] 临时 hostname（如 `beta.example.com`）
- [ ] **临时 hostname 上 `noindex` meta + robots.txt `Disallow: /`**（防意外索引）

### 2. Googlebot 访问验证
- [ ] GSC URL 检查工具测试新基础架构
- [ ] 检查防火墙/DoS 防御是否阻断 Googlebot
- [ ] 验证 Googlebot 真实 IP（用 `Verify Googlebot` 工具）

### 3. DNS 准备
- [ ] **迁移前 1 周降低 TTL 至 3600 秒以内**（推荐几小时）
- [ ] 准备好新 DNS 记录（A / AAAA / CNAME）

### 4. Search Console 验证保留
- [ ] HTML 验证文件 `/google[token].html` 复制到新副本
- [ ] `<head>` 的 meta 验证标签保留
- [ ] DNS TXT 记录验证保留
- [ ] Google Analytics 代码保留

### 5. 临时 hostname 在 GSC 验证（可选）
- [ ] 添加 `beta.example.com` property
- [ ] 验证 Googlebot 能访问 beta（不索引）

---

## 四、Migration Execution（D-Day）

### 1. 移除临时阻断
- [ ] **关键**：从新副本中移除 staging 的 `robots.txt: Disallow: /`
- [ ] 移除 `<meta name="robots" content="noindex">`
- [ ] 移除 `X-Robots-Tag: noindex` HTTP header

### 2. DNS 切换
- [ ] 更新 DNS A/AAAA 记录指向新基础架构
- [ ] 在多个公共 DNS 检查工具验证传播状态
- [ ] 监控 ISP DNS 缓存刷新进度

### 3. 立即验证
- [ ] 主页跑 `seo-audit audit https://example.com`
- [ ] 关键页（/futures, /price/btc, /learn）逐个 audit
- [ ] 跑 `scripts/batch_audit.py` 全 10 页对比基线

---

## 五、Migration Monitoring（迁移后 1-7 天）

### 1. 流量监控
- [ ] 新服务器流量上升、旧服务器流量下降
- [ ] 24h 内 80%+ 流量应该到新服务器
- [ ] 48h 内旧服务器流量应 < 10%

### 2. GSC 监控
- [ ] **索引涵盖范围**：已索引数应稳定
- [ ] **抓取统计**：临时下降正常，1 周内恢复
- [ ] **手动处置措施**：无新增

### 3. 错误监控
- [ ] 5xx 错误率 < 1%
- [ ] Googlebot 5xx 错误率特别监控
- [ ] Cloudflare/CDN 日志看异常

### 4. Composite Score 对比
跑 `seo-audit audit` 对比迁移前后 8 个 composite scores：
| 维度 | 迁移前 | 迁移后 | 期望 |
|---|---|---|---|
| crawlability | X | X | 不变 |
| performance | X | X | 不变或更好 |
| 其他 | X | X | 不变 |

任一维度跌 > 0.10 = 警报。

---

## 六、Post-Migration（迁移完成后）

### 1. 关闭旧基础架构
- [ ] 检查旧服务器访问日志归零
- [ ] 旧基础架构留 30 天作为 fallback（不立即关）
- [ ] 30 天后正式下线

### 2. GSC 重新配置
- [ ] 如果是新 CDN 域名，在 GSC 添加 CDN property
- [ ] 验证 CDN 域名所有权

### 3. 复盘 + 沉淀
- [ ] 记录到 `tasks/lessons.md`
- [ ] 如有事故，记录到 `rules/platform/google-action-history.md`
- [ ] 更新 Platform 内部 runbook

---

## 七、Platform 迁移红线（必修清单）

迁移期任何时刻发现以下情况，**立即回滚**：

1. ❌ GSC 报告"无法访问主机"
2. ❌ Googlebot 5xx 错误率 > 5%
3. ❌ 索引涵盖范围下降 > 10%
4. ❌ `seo-audit audit` Brand SEO Score 跌 > 20 分
5. ❌ 收到 manual action 通知
6. ❌ Composite scores 任一维度跌 > 0.15

---

## 八、与 Multi-Engine SEO Audit Skill 集成

| 迁移阶段 | Skill 命令 |
|---|---|
| Pre-Migration 验证 | `seo-audit audit https://beta.example.com` |
| D-Day 验证 | `scripts/batch_audit.py` 全 10 页 |
| 24h 监控 | `seo-audit watch example.com` |
| 对比基线 | 上次 batch_audit JSON snapshot diff |
| 红线检测 | `audit` 输出 Composite Scores 是否跌 |

---

## 九、对应规则

- `platforms/google/_rules/site-migration.yaml`（8 条规则）
- 每条对应迁移 SOP 的具体检查点
