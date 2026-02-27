---
name: amap-route
description: 基于高德地图API的路线规划。支持驾车、步行、公交、骑行四种模式。当用户需要查询两地之间的路线、距离、耗时、导航方案时使用。触发词：路线规划、怎么走、怎么去、导航、多远、多久、驾车路线、公交路线、步行路线、骑行路线。
---

# 高德路线规划 Skill

## 使用流程

1. 从用户输入中提取：起点、终点、出行方式（驾车/步行/公交/骑行，默认驾车）
2. 运行 `scripts/route.py` 获取路线
3. 将结果格式化输出给用户

## 运行脚本

```bash
python scripts/route.py --origin "起点地名" --destination "终点地名" --mode driving
```

参数说明：
- `--origin`：起点（地名或 "经度,纬度"）
- `--destination`：终点（地名或 "经度,纬度"）
- `--mode`：出行方式，可选 `driving`（驾车）、`walking`（步行）、`transit`（公交）、`bicycling`（骑行），默认 `driving`
- `--city`：公交模式必填，起点所在城市名称
- `--key`：高德 API Key（也可通过环境变量 `AMAP_API_KEY` 传入）

## 输出格式

脚本直接输出格式化的中文路线信息，包含：
- 总距离、预计耗时
- 分段路线步骤
- 公交模式额外显示换乘方案

## 注意事项

- 地名会自动通过高德地理编码 API 转换为坐标
- 如果地名有歧义，脚本会返回第一个匹配结果
- 公交模式需要提供 `--city` 参数
- API Key 参考 references/api-notes.md
