#!/usr/bin/env python3
"""高德地图路线规划工具 - 支持驾车/步行/公交/骑行"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse

# Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE_V3 = "https://restapi.amap.com/v3"
BASE_V4 = "https://restapi.amap.com/v4"


def api_get(url, params):
    qs = urllib.parse.urlencode(params)
    full = f"{url}?{qs}"
    with urllib.request.urlopen(full, timeout=10) as resp:
        return json.loads(resp.read().decode())


def geocode(address, key):
    """地名 -> 经度,纬度"""
    if "," in address:
        parts = address.split(",")
        try:
            float(parts[0]); float(parts[1])
            return address
        except ValueError:
            pass
    data = api_get(f"{BASE_V3}/geocode/geo", {"address": address, "key": key})
    if data.get("status") != "1" or not data.get("geocodes"):
        print(f"❌ 无法识别地点：{address}")
        sys.exit(1)
    return data["geocodes"][0]["location"]


def fmt_distance(meters):
    m = int(meters)
    return f"{m/1000:.1f}公里" if m >= 1000 else f"{m}米"


def fmt_duration(seconds):
    s = int(seconds)
    if s >= 3600:
        return f"{s//3600}小时{s%3600//60}分钟"
    return f"{s//60}分钟"


def route_driving(origin, dest, key):
    data = api_get(f"{BASE_V3}/direction/driving", {
        "origin": origin, "destination": dest, "key": key,
        "extensions": "base", "strategy": 0
    })
    if data.get("status") != "1":
        return f"❌ 驾车路线查询失败：{data.get('info', '未知错误')}"
    route = data["route"]
    paths = route.get("paths", [])
    if not paths:
        return "❌ 未找到驾车路线"
    p = paths[0]
    lines = [
        f"🚗 驾车路线",
        f"总距离：{fmt_distance(p['distance'])}",
        f"预计耗时：{fmt_duration(p['duration'])}",
        f"",
        f"📍 详细路线："
    ]
    for i, step in enumerate(p.get("steps", []), 1):
        inst = step.get("instruction", step.get("action", ""))
        dist = fmt_distance(step.get("distance", 0))
        lines.append(f"  {i}. {inst}（{dist}）")
    return "\n".join(lines)


def route_walking(origin, dest, key):
    data = api_get(f"{BASE_V3}/direction/walking", {
        "origin": origin, "destination": dest, "key": key
    })
    if data.get("status") != "1":
        return f"❌ 步行路线查询失败：{data.get('info', '未知错误')}"
    route = data["route"]
    paths = route.get("paths", [])
    if not paths:
        return "❌ 未找到步行路线"
    p = paths[0]
    lines = [
        f"🚶 步行路线",
        f"总距离：{fmt_distance(p['distance'])}",
        f"预计耗时：{fmt_duration(p['duration'])}",
        f"",
        f"📍 详细路线："
    ]
    for i, step in enumerate(p.get("steps", []), 1):
        inst = step.get("instruction", "")
        dist = fmt_distance(step.get("distance", 0))
        lines.append(f"  {i}. {inst}（{dist}）")
    return "\n".join(lines)


def route_bicycling(origin, dest, key):
    data = api_get(f"{BASE_V4}/direction/bicycling", {
        "origin": origin, "destination": dest, "key": key
    })
    d = data.get("data", {})
    paths = d.get("paths", [])
    if not paths:
        return "❌ 未找到骑行路线"
    p = paths[0]
    lines = [
        f"🚲 骑行路线",
        f"总距离：{fmt_distance(p['distance'])}",
        f"预计耗时：{fmt_duration(p['duration'])}",
        f"",
        f"📍 详细路线："
    ]
    for i, step in enumerate(p.get("steps", []), 1):
        inst = step.get("instruction", "")
        dist = fmt_distance(step.get("distance", 0))
        lines.append(f"  {i}. {inst}（{dist}）")
    return "\n".join(lines)


def route_transit(origin, dest, city, key):
    if not city:
        return "❌ 公交模式需要提供 --city 参数（起点城市名）"
    data = api_get(f"{BASE_V3}/direction/transit/integrated", {
        "origin": origin, "destination": dest, "key": key,
        "city": city, "strategy": 0
    })
    if data.get("status") != "1":
        return f"❌ 公交路线查询失败：{data.get('info', '未知错误')}"
    route = data["route"]
    transits = route.get("transits", [])
    if not transits:
        return "❌ 未找到公交路线"
    lines = [f"🚌 公交路线（共 {len(transits)} 个方案）", ""]
    for idx, t in enumerate(transits[:3], 1):
        cost = t.get("cost", "未知")
        dur = fmt_duration(t.get("duration", 0))
        dist = fmt_distance(t.get("distance", 0))
        walking_dist = fmt_distance(t.get("walking_distance", 0))
        lines.append(f"--- 方案 {idx}：{dist}，耗时 {dur}，步行 {walking_dist}，费用 {cost}元 ---")
        for seg in t.get("segments", []):
            bus = seg.get("bus", {})
            buslines = bus.get("buslines", [])
            walk = seg.get("walking", {})
            if buslines:
                bl = buslines[0]
                name = bl.get("name", "未知线路")
                dep = bl.get("departure_stop", {}).get("name", "")
                arr = bl.get("arrival_stop", {}).get("name", "")
                via = bl.get("via_num", 0)
                lines.append(f"  🚍 {name}：{dep} → {arr}（经过 {via} 站）")
            if walk and walk.get("distance", "0") != "0":
                lines.append(f"  🚶 步行 {fmt_distance(walk.get('distance', 0))}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="高德地图路线规划")
    parser.add_argument("--origin", required=True, help="起点（地名或经纬度）")
    parser.add_argument("--destination", required=True, help="终点（地名或经纬度）")
    parser.add_argument("--mode", default="driving",
                        choices=["driving", "walking", "transit", "bicycling"],
                        help="出行方式")
    parser.add_argument("--city", default="", help="公交模式的起点城市")
    parser.add_argument("--key", default=os.environ.get("AMAP_API_KEY", ""),
                        help="高德 API Key")
    args = parser.parse_args()

    if not args.key:
        print("❌ 请提供高德 API Key（--key 或环境变量 AMAP_API_KEY）")
        sys.exit(1)

    origin = geocode(args.origin, args.key)
    dest = geocode(args.destination, args.key)

    print(f"起点：{args.origin}（{origin}）")
    print(f"终点：{args.destination}（{dest}）")
    print()

    if args.mode == "driving":
        print(route_driving(origin, dest, args.key))
    elif args.mode == "walking":
        print(route_walking(origin, dest, args.key))
    elif args.mode == "bicycling":
        print(route_bicycling(origin, dest, args.key))
    elif args.mode == "transit":
        print(route_transit(origin, dest, args.city, args.key))


if __name__ == "__main__":
    main()

