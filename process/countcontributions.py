import os
import pandas as pd
import ast
import glob

# データディレクトリを指定
data_dir = "../results/developer_data"

# 全ての *_pulls.csv と *_issues.csv ファイルを検索
pull_files = glob.glob(os.path.join(data_dir, "*_pulls.csv"))
issue_files = glob.glob(os.path.join(data_dir, "*_issues.csv"))

# 開発者ごとの統合データフレームを用意
all_contributions = []

def extract_user_login(user_info):
    """ 'user' カラムからGitHubユーザー名を抽出する関数 """
    try:
        return ast.literal_eval(user_info).get('login', None)
    except (ValueError, SyntaxError):
        return None

def extract_repo_name(repo_url):
    """ `repository_url` からリポジトリ名を抽出する関数 """
    try:
        return repo_url.rstrip('/').split('/')[-1]  # 最後の部分（リポジトリ名）を取得
    except AttributeError:
        return None

# PRデータの処理
for pull_file in pull_files:
    pulls_data = pd.read_csv(pull_file)

    # `repository_url` からリポジトリ名を取得し、新しい `repository` カラムを追加
    pulls_data['repository'] = pulls_data['repository_url'].apply(extract_repo_name)

    # `created_at` に日付形式以外のデータが含まれていないかチェックし、日付のみをフィルタ
    valid_dates_mask = pulls_data['created_at'].astype(str).str.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', na=False)
    pulls_data = pulls_data[valid_dates_mask]
    pulls_data['created_at'] = pd.to_datetime(pulls_data['created_at'])

    # 開発者名を抽出
    pulls_data['user_login'] = pulls_data['user'].apply(extract_user_login)

    # PR数を集計（リポジトリごとに開発者別）
    pr_counts = pulls_data.groupby(['repository', 'user_login']).size().reset_index(name='pr_count')

    all_contributions.append(pr_counts)

# Issueデータの処理
for issue_file in issue_files:
    issues_data = pd.read_csv(issue_file)

    # `repository_url` からリポジトリ名を取得し、新しい `repository` カラムを追加
    issues_data['repository'] = issues_data['repository_url'].apply(extract_repo_name)

    # `created_at` のチェック
    valid_dates_mask = issues_data['created_at'].astype(str).str.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', na=False)
    issues_data = issues_data[valid_dates_mask]
    issues_data['created_at'] = pd.to_datetime(issues_data['created_at'])

    # 開発者名を抽出
    issues_data['user_login'] = issues_data['user'].apply(extract_user_login)

    # Issue数を集計（リポジトリごとに開発者別）
    issue_counts = issues_data.groupby(['repository', 'user_login']).size().reset_index(name='issue_count')

    all_contributions.append(issue_counts)

# すべてのデータを統合
final_contributions = pd.concat(all_contributions, ignore_index=True)

# PR数とIssue数を統合
final_contributions = final_contributions.groupby(['repository', 'user_login']).sum().reset_index()

# 結果をCSVに保存
output_file = "../results/contributions_by_repository.csv"
final_contributions.to_csv(output_file, index=False)

print(f"開発者ごとの貢献データを {output_file} に保存しました。")
