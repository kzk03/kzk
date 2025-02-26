import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv("config/.env")

# GitHub API 認証情報
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# 各開発者のCSVが保存されているディレクトリ
input_directory = "/Users/kazuki-h/newresearch/res/commit_history2"
output_directory = "/Users/kazuki-h/newresearch/results/commit-diff"
os.makedirs(output_directory, exist_ok=True)

# ファイルを保存するディレクトリを作成する関数
def ensure_directory_exists(file_path):
    """
    指定されたファイルパスの親ディレクトリを作成
    """
    parent_dir = os.path.dirname(file_path)
    os.makedirs(parent_dir, exist_ok=True)

# GitHub API から変更ファイルの diff を取得
def get_commit_patch(owner, repo, commit_sha, file_path, max_retries=5):
    """
    コミット SHA とファイル名を使って、そのファイルの変更内容（diff）を取得
    一時的な接続エラーが発生した場合はリトライする
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)

            # 成功した場合
            if response.status_code == 200:
                commit_data = response.json()
                for file in commit_data.get("files", []):
                    if file["filename"] == file_path:
                        return file.get("patch", "")
                return None  # ファイルが見つからなかった場合

            # APIレート制限 (403) の場合
            elif response.status_code == 403:
                reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait_time = reset_time - int(time.time())
                print(f"⚠ APIのレート制限。{wait_time}秒待機... ({attempt+1}/{max_retries})")
                time.sleep(max(wait_time, 1))  # 1秒以上待機

            else:
                print(f"⚠ APIエラー: {response.status_code} ({attempt+1}/{max_retries})")
                time.sleep(5)

        except requests.exceptions.ConnectionError:
            print(f"⚠ 接続エラー。10秒待機して再試行 ({attempt+1}/{max_retries})")
            time.sleep(10)

        except requests.exceptions.Timeout:
            print(f"⚠ タイムアウト。5秒待機して再試行 ({attempt+1}/{max_retries})")
            time.sleep(5)

    print("❌ 最大リトライ回数を超えました")
    return None

# フォルダ内のすべての開発者 CSV を処理
for dev_filename in os.listdir(input_directory):
    if dev_filename.endswith(".csv"):
        filepath = os.path.join(input_directory, dev_filename)
        developer_name = dev_filename.replace(".csv", "")  # 開発者名を取得

        print(f"📂 Processing developer: {developer_name} ({dev_filename})")

        # CSV を読み込む
        df = pd.read_csv(filepath)

        # `patch` カラムを追加するためのリスト
        commit_patch_data = []

        # 各コミットの変更ファイルを処理
        for _, row in df.iterrows():
            repo = row["repo"]  # "owner/repo" の形式
            commit_sha = row["commit_sha"]
            changed_files = row["changed_files"]

            # `changed_files` の中に複数のファイルが含まれている場合があるため、リストに分割
            file_list = [file.strip() for file in str(changed_files).split(",")]

            # リポジトリ情報を分割
            try:
                owner, repo_name = repo.split("/")
            except ValueError:
                print(f"⚠ Invalid repo format: {repo}")
                continue

            for file_path in file_list:  # `filename` を `file_path` に変更
                print(f"🔍 Fetching patch for {commit_sha} - {file_path} in {repo}...")

                patch = get_commit_patch(owner, repo_name, commit_sha, file_path)

                commit_patch_data.append([
                    commit_sha, repo, file_path, patch, developer_name  # `developer` カラムを追加
                ])

            time.sleep(1)  # API制限回避のため遅延

        # DataFrame に変換
        commit_patch_df = pd.DataFrame(commit_patch_data, columns=["commit_sha", "repo_name", "filename", "patch", "developer"])

        # **修正: `developer_name.csv` に統一**
        output_csv = os.path.join(output_directory, f"{developer_name}.csv")
        ensure_directory_exists(output_csv)  # ディレクトリを確認・作成

        commit_patch_df.to_csv(output_csv, index=False, encoding="utf-8")

        print(f"✅ 変更されたファイルの内容を追加し、保存しました: {output_csv}")

print("🎉 すべての開発者のCSVに変更ファイルの内容を追加しました！")
