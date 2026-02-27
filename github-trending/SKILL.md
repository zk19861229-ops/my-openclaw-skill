---
name: github-trending
description: 获取 GitHub 热门趋势项目。使用场景：查询 GitHub trending、发现热门开源项目、获取项目趋势排名、查找新兴技术项目、按语言筛选 trending、生成项目摘要报告。支持按日/周/月时间范围和编程语言筛选。
---

# GitHub Trending Skill

获取 GitHub 上当前最热门的趋势项目，包含项目描述、Star 数、Fork 数等详细信息。

## 何时使用

✅ **使用场景：**
- "看看今天 GitHub 上什么项目最火"
- "获取本周 trending 项目"
- "Python 项目最近有什么热门的"
- "发现新兴的开源项目"
- "生成 GitHub 趋势报告"

❌ **不使用：**
- 特定仓库的详细信息 → 用 GitHub API
- 代码搜索 → 用 GitHub Search
- 历史数据分析 → 用 GitHub Archive

## 快速开始

### 获取今日 trending

```bash
python scripts/get_trending.py
```

### 获取本周 trending

```bash
python scripts/get_trending.py --timeframe weekly
```

### 按语言筛选

```bash
python scripts/get_trending.py --language python
python scripts/get_trending.py -l javascript -t weekly
```

### 输出 JSON 格式

```bash
python scripts/get_trending.py --format json
```

### 限制结果数量

```bash
python scripts/get_trending.py -n 5
```

## 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--timeframe` | `-t` | 时间范围：daily/weekly/monthly | daily |
| `--language` | `-l` | 编程语言筛选 (如 python, javascript) | 无 |
| `--format` | `-f` | 输出格式：markdown/json | markdown |
| `--limit` | `-n` | 限制结果数量 | 全部 |

## 输出示例

### Markdown 格式

```markdown
# 🔥 GitHub Trending - 今日

*更新时间：2026-02-26 23:52*

共 25 个项目

---

## 1. [openai/openclaw](https://github.com/openai/openclaw)

**描述**: AI agent framework for building autonomous workflows

**语言**: Python  |  **Stars**: ⭐ 12,345  |  **Forks**: 🍴 2,345
**趋势**: 1,234 stars today

---
```

### JSON 格式

```json
{
  "updated_at": "2026-02-26T23:52:00",
  "count": 25,
  "projects": [
    {
      "owner": "openai",
      "name": "openclaw",
      "full_name": "openai/openclaw",
      "url": "https://github.com/openai/openclaw",
      "description": "AI agent framework...",
      "language": "Python",
      "stars": 12345,
      "forks": 2345,
      "trending_info": "1,234 stars today"
    }
  ]
}
```

## 支持的语言

常用语言代码：
- `python`
- `javascript`
- `typescript`
- `go`
- `rust`
- `java`
- `cpp`
- `vue`
- `jupyter-notebook`

完整列表参考 GitHub trending 页面。

## 依赖

```bash
pip install requests beautifulsoup4
```

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `Error fetching GitHub trending` | 网络问题或 GitHub 反爬 | 稍后重试，检查网络 |
| `No trending projects found` | 解析失败或页面结构变化 | 检查 GitHub 页面是否正常 |

## 注意事项

- 无需 GitHub API key（使用网页抓取）
- 避免频繁调用（可能触发反爬）
- 建议缓存结果（至少 1 小时）
- 页面结构变化可能导致解析失败

## 扩展建议

如需更详细的仓库信息（如最近提交、issue 数量等），可结合 GitHub API 使用：
- 先用此脚本获取 trending 列表
- 再用 GitHub API 获取详细信息
