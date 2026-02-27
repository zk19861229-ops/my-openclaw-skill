---
name: huggingface-trending
description: 获取 Hugging Face 热门趋势。使用场景：查询 HF trending 模型/数据集/Spaces、发现热门 AI 模型、追踪最新开源模型、按任务/库筛选 trending、生成 HF 热点报告。支持模型、数据集、Spaces 三类资源，可按 library 和 task 筛选。
---

# Hugging Face Trending Skill

获取 Hugging Face 上当前最热门的趋势项目，包括模型、数据集和 Spaces。

## 何时使用

✅ **使用场景：**
- "看看今天 HF 上什么模型最火"
- "获取 trending 的文本生成模型"
- "最近有什么热门的数据集"
- "发现新的 diffusion 模型"
- "生成 Hugging Face 趋势报告"
- "追踪 AI 模型最新动态"

❌ **不使用：**
- 特定模型的详细信息 → 用 HF API
- 模型下载 → 用 `huggingface-cli`
- 模型训练 → 用 Transformers 库

## 快速开始

### 获取全部 trending（模型 + 数据集 + Spaces）

```bash
python scripts/get_trending.py
```

### 只获取模型

```bash
python scripts/get_trending.py -t models
```

### 只获取数据集

```bash
python scripts/get_trending.py -t datasets
```

### 只获取 Spaces

```bash
python scripts/get_trending.py -t spaces
```

### 按库筛选模型

```bash
# transformers 模型
python scripts/get_trending.py -t models -l transformers

# diffusers 模型
python scripts/get_trending.py -t models -l diffusers

# peft 模型
python scripts/get_trending.py -t models -l peft
```

### 按任务筛选模型

```bash
# 文本生成
python scripts/get_trending.py -t models --task text-generation

# 图像分类
python scripts/get_trending.py -t models --task image-classification

# 问答
python scripts/get_trending.py -t models --task question-answering
```

### 输出 JSON 格式

```bash
python scripts/get_trending.py -f json
```

### 限制结果数量

```bash
python scripts/get_trending.py -n 5
```

## 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--type` | `-t` | 类型：models/datasets/spaces/all | all |
| `--library` | `-l` | 模型库筛选 (transformers/diffusers/peft) | 无 |
| `--task` | | 任务筛选 (text-generation 等) | 无 |
| `--format` | `-f` | 输出格式：markdown/json | markdown |
| `--limit` | `-n` | 限制结果数量 | 10 |

## 输出示例

### Markdown 格式

```markdown
# 🤗 Hugging Face Trending - 今日热点

*更新时间：2026-02-27 00:05*

## 🔥 热门模型 (Top 10)

| # | 模型 | 任务 | 库 | 👍 Likes | 📥 下载 | 🔥 Trending |
|---|------|------|-----|---------|--------|-------------|
| 1 | [meta-llama/Llama-3-70B](...) | text-generation | transformers | 12,345 | 1,234,567 | 98.5 |
| 2 | [stabilityai/sdxl](...) | text-to-image | diffusers | 8,901 | 567,890 | 87.3 |

---

## 📊 热门数据集 (Top 10)

| # | 数据集 | 👍 Likes | 📥 下载 | 🔥 Trending |
|---|--------|---------|--------|-------------|
| 1 | [OpenAssistant/oasst1](...) | 5,678 | 234,567 | 76.2 |

---

## 🚀 热门 Spaces (Top 10)

| # | Space | SDK | 👍 Likes | 🔥 Trending |
|---|-------|-----|---------|-------------|
| 1 | [gradio/calculator](...) | gradio | 3,456 | 65.4 |
```

### JSON 格式

```json
{
  "updated_at": "2026-02-27T00:05:00",
  "models": [
    {
      "id": "meta-llama/Llama-3-70B",
      "author": "meta-llama",
      "name": "Llama-3-70B",
      "url": "https://huggingface.co/meta-llama/Llama-3-70B",
      "task": "text-generation",
      "library": "transformers",
      "downloads": 1234567,
      "likes": 12345,
      "trending_score": 98.5
    }
  ],
  "datasets": [...],
  "spaces": [...]
}
```

## 支持的库过滤

常用 library：
- `transformers` - Transformer 模型
- `diffusers` - 扩散模型（图像生成）
- `peft` - 参数高效微调
- `sentence-transformers` - 句向量
- `timm` - 图像模型
- `safetensors` - 安全张量格式

## 支持的任务过滤

常用 pipeline_tag：
- `text-generation` - 文本生成
- `text-classification` - 文本分类
- `question-answering` - 问答
- `image-classification` - 图像分类
- `text-to-image` - 文生图
- `image-to-text` - 图生文
- `automatic-speech-recognition` - 语音识别
- `translation` - 翻译
- `summarization` - 摘要
- `fill-mask` - 完形填空

## 依赖

```bash
pip install requests
```

## API 说明

本技能使用 Hugging Face 公开 API：

| 端点 | 说明 |
|------|------|
| `https://huggingface.co/api/models` | 模型列表 |
| `https://huggingface.co/api/datasets` | 数据集列表 |
| `https://huggingface.co/api/spaces` | Spaces 列表 |

**无需 API Key** - 使用公开数据

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `Error fetching Hugging Face` | 网络问题或 API 限流 | 稍后重试，检查网络 |
| 空结果 | 筛选条件太严格 | 放宽筛选条件 |

## 注意事项

- 无需 Hugging Face API key
- 避免频繁调用（可能触发限流）
- 建议缓存结果（至少 30 分钟）
- trendingScore 是 HF 的内部算法分数

## 扩展建议

如需更详细的模型信息（如配置文件、训练数据等），可结合 Hugging Face Hub 库：

```python
from huggingface_hub import HfApi

api = HfApi()
model_info = api.model_info("meta-llama/Llama-3-70B")
```

## 与其他技能配合

- **github-trending** - 同时追踪 GitHub 和 HF 的 AI 项目趋势
- **ai-daily-digest** - 将 HF trending 纳入每日 AI 摘要
