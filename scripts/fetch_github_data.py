import os

import pandas as pd
import requests
from dotenv import load_dotenv

# `.env` ファイルを読み込む
load_dotenv("config/.env")

# GitHubの設定（トークンを環境変数から取得）
GITHUB_USERNAME = "rzezeski"  # 取得したい開発者のGitHubユーザー名
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # 環境変数から取得
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# 出力ディレクトリの設定
OUTPUT_DIR = "../results/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# GitHub APIのエンドポイント
ISSUES_URL = f"https://api.github.com/search/issues?q=author:{GITHUB_USERNAME}+type:issue&per_page=100"
PULLS_URL = f"https://api.github.com/search/issues?q=author:{GITHUB_USERNAME}+type:pr&per_page=100"

def fetch_github_data(url):
    """GitHub APIからデータを取得する"""
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []

def process_data(data):
    """必要な情報を抽出してデータフレームに変換"""
    processed_data = []
    for item in data:
        processed_data.append({
            "url": item.get("html_url"),
            "repository_url": item.get("repository_url"),
            "number": item.get("number"),
            "title": item.get("title"),
            "state": item.get("state"),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
            "closed_at": item.get("closed_at"),
            "comments": item.get("comments", 0),
            "comments_url": item.get("comments_url"),
        })
    return pd.DataFrame(processed_data)

# Issuesのデータ取得
issues_data = fetch_github_data(ISSUES_URL)
df_issues = process_data(issues_data)
issues_output_path = os.path.join(OUTPUT_DIR, f"{GITHUB_USERNAME}_issues.csv")
df_issues.to_csv(issues_output_path, index=False)
print(f"Issueデータを {issues_output_path} に保存しました。")

# Pull Requestのデータ取得
pulls_data = fetch_github_data(PULLS_URL)
df_pulls = process_data(pulls_data)
pulls_output_path = os.path.join(OUTPUT_DIR, f"{GITHUB_USERNAME}_pulls.csv")
df_pulls.to_csv(pulls_output_path, index=False)
print(f"Pull Requestデータを {pulls_output_path} に保存しました。")
