# 高德地图 API 备注

## API Key

通过以下方式之一提供：
- 命令行参数 `--key`
- 环境变量 `AMAP_API_KEY`

## 使用的 API 端点

| 功能 | 端点 |
|------|------|
| 地理编码 | `https://restapi.amap.com/v3/geocode/geo` |
| 驾车路线 | `https://restapi.amap.com/v3/direction/driving` |
| 步行路线 | `https://restapi.amap.com/v3/direction/walking` |
| 公交路线 | `https://restapi.amap.com/v3/direction/transit/integrated` |
| 骑行路线 | `https://restapi.amap.com/v4/direction/bicycling` |

## 注意

- 骑行接口是 v4 版本，返回结构与其他不同
- 公交接口需要额外传 `city` 参数
- 地理编码接口需要传 `address` 参数，返回 `location` 字段为 "经度,纬度"
