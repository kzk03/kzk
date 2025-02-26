import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv("config/.env")

# GitHub API 認証情報を.envから取得
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN が .env に設定されていません。")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# 取得する開発者リストのCSVファイル
developer_list_file = "/Users/kazuki-h/newresearch/results/B.csv"
developers_df = pd.read_csv(developer_list_file)

# 取得する日付範囲を指定
SINCE_DATE = "2005-01-01T00:00:00Z"
UNTIL_DATE = "2024-12-31T23:59:59Z"

# 保存フォルダを作成
output_dir = "/Users/kazuki-h/newresearch/results/commit_history"
os.makedirs(output_dir, exist_ok=True)

# APIのレート制限を確認する関数
def check_rate_limit(response):
    if response.status_code == 403 and "X-RateLimit-Reset" in response.headers:
        reset_time = int(response.headers["X-RateLimit-Reset"])
        current_time = int(time.time())
        wait_time = reset_time - current_time
        if wait_time > 0:
            print(f"⚠ APIのレート制限に達しました。{wait_time}秒待機します...")
            time.sleep(wait_time + 1)
        return True
    return False

# 各開発者のコミット履歴を取得し、個別のCSVに保存
for developer in developers_df['developer'].dropna():
    print(f"Fetching commits for {developer} from {SINCE_DATE} to {UNTIL_DATE}...")
    commit_data = []  # 個別のリストを作成
    page = 1

    while True:
        url = f"https://api.github.com/search/commits?q=author:{developer}+committer-date:{SINCE_DATE}..{UNTIL_DATE}&sort=committer-date&per_page=100&page={page}"
        
        response = requests.get(url, headers=HEADERS)

        if check_rate_limit(response):
            continue  # レート制限後に再試行

        if response.status_code != 200:
            print(f"Error fetching {developer}: {response.status_code}")
            break

        commits = response.json().get('items', [])
        if not commits:
            break

        for commit in commits:
            sha = commit['sha']
            repo_name = commit['repository']['full_name']
            commit_message = commit['commit']['message']
            commit_date = commit['commit']['committer']['date']

            # 各コミットの変更ファイル情報を取得
            commit_details_url = f"https://api.github.com/repos/{repo_name}/commits/{sha}"
            commit_response = requests.get(commit_details_url, headers=HEADERS)

            if check_rate_limit(commit_response):
                continue  # レート制限後に再試行

            if commit_response.status_code == 200:
                commit_details = commit_response.json()
                changed_files = [file['filename'] for file in commit_details.get('files', [])]
            else:
                print(f"⚠ ファイル情報を取得できませんでした: {commit_details_url}")
                changed_files = []

            commit_data.append([
                developer,
                repo_name,
                sha,
                commit_message,
                commit_date,
                ", ".join(changed_files)  # 変更ファイルをカンマ区切りで保存
            ])

        page += 1
        time.sleep(1)

    # DataFrame に変換
    if commit_data:
        commit_df = pd.DataFrame(commit_data, columns=['developer', 'repo', 'commit_sha', 'commit_message', 'commit_date', 'changed_files'])

        # 各開発者ごとにCSV保存
        developer_filename = os.path.join(output_dir, f"{developer}.csv")
        commit_df.to_csv(developer_filename, index=False, encoding="utf-8")

        print(f"✅ {developer} のコミット履歴を保存しました: {developer_filename}")
    else:
        print(f"⚠ {developer} のコミット履歴は見つかりませんでした。")

print("🎉 すべてのコミット履歴の取得と保存が完了しました！")