import csv
import requests
import base64
import os

# GitHubのパーソナルアクセストークン（レート制限回避のため）
TOKEN = 'YOUR_GITHUB_TOKEN'
HEADERS = {'Authorization': f'token {TOKEN}'}

def get_file_content(owner, repo, path):
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return content
    else:
        return None

# 対象の依存関係ファイルリスト（Gradleファイルも含む）
dependency_files = ['pom.xml', 'requirements.txt', 'package.json', 'build.gradle', 'build.gradle.kts']

# 出力先のディレクトリを作成
output_dir = 'dependency_files'
os.makedirs(output_dir, exist_ok=True)

# CSVファイルからリポジトリ情報を読み込む（CSVファイルには "owner" と "repo" のカラムがあることを前提）
csv_file = "repos.csv"
with open(csv_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        owner = row['owner']
        repo = row['repo']
        repo_dir = os.path.join(output_dir, f"{owner}_{repo}")
        os.makedirs(repo_dir, exist_ok=True)
        print(f'Processing {owner}/{repo}')
        for file in dependency_files:
            content = get_file_content(owner, repo, file)
            if content:
                print(f'  Found {file} in {owner}/{repo}')
                file_path = os.path.join(repo_dir, file)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                print(f'  {file} not found in {owner}/{repo}')
