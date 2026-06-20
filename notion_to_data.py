#!/usr/bin/env python3
"""讀取 Notion 頁面裡的 JSON 程式碼區塊，存成 data.json。
不做任何運算，只是把每日任務已經算好、寫在 Notion 的成品抄下來。
需要環境變數：NOTION_TOKEN（唯讀 integration token）、NOTION_PAGE_ID。
"""
import os
import sys
import json
import urllib.request

TOKEN = os.environ["NOTION_TOKEN"]
PAGE_ID = os.environ["NOTION_PAGE_ID"]
NOTION_VERSION = "2022-06-28"


def api(url):
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Notion-Version": NOTION_VERSION,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def get_all_blocks(page_id):
    blocks, cursor = [], None
    while True:
        url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        data = api(url)
        blocks.extend(data.get("results", []))
        if data.get("has_more"):
            cursor = data.get("next_cursor")
        else:
            break
    return blocks


def main():
    blocks = get_all_blocks(PAGE_ID)

    code_text = None
    for b in blocks:
        if b.get("type") == "code":
            rich = b["code"].get("rich_text", [])
            code_text = "".join(t.get("plain_text", "") for t in rich)
            break

    if not code_text:
        print("找不到 JSON 程式碼區塊", file=sys.stderr)
        sys.exit(1)

    # 驗證確實是合法 JSON，再寫出（避免把壞資料推上線）
    obj = json.loads(code_text)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

    print(f"data.json 已更新，lastUpdated = {obj.get('lastUpdated')}")


if __name__ == "__main__":
    main()
