#!/usr/bin/env python3
"""Fetch Zhihu hot list via public endpoint with standard library only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_URL = "https://www.zhihu.com/api/v3/feed/topstory/hot-list-web"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.zhihu.com/hot",
}


def fetch_hot_list(limit: int = 50, timeout: int = 10) -> list[dict[str, Any]]:
    params = urlencode({"limit": limit, "desktop": "true"})
    request = Request(f"{API_URL}?{params}", headers=DEFAULT_HEADERS)

    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    result: list[dict[str, Any]] = []
    for idx, item in enumerate(payload.get("data", []), start=1):
        target = item.get("target", {})
        title = target.get("title") or item.get("card_title") or ""
        excerpt = target.get("excerpt") or ""
        question_id = target.get("id")
        url = (
            f"https://www.zhihu.com/question/{question_id}"
            if question_id
            else target.get("url")
        )

        metrics_area = item.get("detail_text") or item.get("metrics_area", {})
        heat = metrics_area if isinstance(metrics_area, str) else metrics_area.get("text", "")

        result.append(
            {
                "rank": idx,
                "title": title,
                "excerpt": excerpt,
                "url": url,
                "heat": heat,
            }
        )

    return result


def save_output(data: list[dict[str, Any]], output_path: Path) -> None:
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def print_table(data: list[dict[str, Any]]) -> None:
    for item in data:
        print(f"{item['rank']:>2}. {item['title']}")
        if item["heat"]:
            print(f"    热度: {item['heat']}")
        if item["url"]:
            print(f"    链接: {item['url']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取知乎热榜")
    parser.add_argument("--limit", type=int, default=20, help="抓取数量，默认 20")
    parser.add_argument("--timeout", type=int, default=10, help="请求超时秒数，默认 10")
    parser.add_argument("--output", type=Path, help="输出 JSON 文件路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        data = fetch_hot_list(limit=args.limit, timeout=args.timeout)
    except URLError as exc:
        print(f"抓取失败：{exc}", file=sys.stderr)
        print("提示：当前环境可能限制了外网访问或代理隧道。", file=sys.stderr)
        raise SystemExit(1) from exc

    if args.output:
        save_output(data, args.output)
        print(f"已保存 {len(data)} 条热榜到: {args.output}")
    else:
        print_table(data)


if __name__ == "__main__":
    main()
