import base64
import csv
import os
import random
import time

import requests
from dotenv import load_dotenv
from tqdm import tqdm

# .envファイルを読み込む（スクリプト実行時のカレントディレクトリからの相対パスに注意）
load_dotenv("config/.env")

# GitHub API 認証情報を.envから取得
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN2")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN2 が .env に設定されていません。")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def get_file_content(owner, repo, path):
    """
    GitHub API を用いて、指定リポジトリの依存関係ファイルの内容を取得する。
    レート制限超過時（HTTP 403）が発生した場合のみ、X-RateLimit-Reset ヘッダーを参照して待機し、再試行する。
    """
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return content
    elif response.status_code == 403:
        reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
        sleep_duration = max(reset_time - time.time(), 0) + 5  # 余裕をもって5秒追加
        tqdm.write(f"Rate limit exceeded for {owner}/{repo}/{path}. Sleeping for {sleep_duration:.0f} seconds.")
        time.sleep(sleep_duration)
        return get_file_content(owner, repo, path)
    else:
        return None

# 対象の依存関係ファイルリスト（Gradleファイルも含む）
dependency_files = ['pom.xml', 'requirements.txt', 'package.json', 'build.gradle', 'build.gradle.kts']

# 出力先のディレクトリ（絶対パスまたは実行時のカレントディレクトリからの相対パス）
output_dir = '/Users/kazuki-h/newresearch/results/dependencies_files'
os.makedirs(output_dir, exist_ok=True)

# チェックポイントファイルのパス
checkpoint_file = "processed_repos.txt"

# 既に処理済みのリポジトリ（owner/repo形式）のリストを読み込む
processed_repos = set()
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, 'r', encoding='utf-8') as cp:
        for line in cp:
            processed_repos.add(line.strip())

# CSVファイルからリポジトリ情報を読み込む
csv_file = "results/dependencies/devideRepo.csv"
with open(csv_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    repo_list = list(reader)  # 全リポジトリ情報をリストに格納

# tqdm を使ってリポジトリごとの進捗を表示
for row in tqdm(repo_list, desc="Processing repositories", unit="repo"):
    owner = row['owner']
    repo = row['repo']
    repo_key = f"{owner}/{repo}"
    
    # チェックポイントファイルに記録済みならスキップ
    if repo_key in processed_repos:
        tqdm.write(f"Skipping already processed repository: {repo_key}")
        continue

    repo_dir = os.path.join(output_dir, f"{owner}_{repo}")
    os.makedirs(repo_dir, exist_ok=True)
    tqdm.write(f'Processing {repo_key}')
    
    # 各依存関係ファイルについて進捗表示
    for file in tqdm(dependency_files, desc=f"{repo_key} dependency files", leave=False):
        file_path = os.path.join(repo_dir, file)
        content = get_file_content(owner, repo, file)
        if content:
            tqdm.write(f'  Found {file} in {repo_key}')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            tqdm.write(f'  {file} not found in {repo_key}')
    
    # 1リポジトリ処理完了後にランダムスリープ（例：2～5秒）
    sleep_time = random.uniform(1, 3)
    tqdm.write(f"Sleeping for {sleep_time:.1f} seconds before next repository...")
    time.sleep(sleep_time)
    
    # チェックポイントファイルに処理済みリポジトリを記録
    with open(checkpoint_file, 'a', encoding='utf-8') as cp:
        cp.write(f"{repo_key}\n")
