import pandas as pd

# ファイルのパスを指定（ローカル環境）
file_path = "../results/contributions_by_repository.csv"

# CSVを読み込む
contributions_data = pd.read_csv(file_path)

# 開発者ごとの貢献リポジトリを取得
developer_repositories = contributions_data.groupby('user_login')['repository'].unique().reset_index()

# 各開発者の貢献リポジトリ数をカウント
developer_repositories['repository_count'] = developer_repositories['repository'].apply(len)

# 結果をCSVに保存
developer_repositories_file = "../results/developer_repositories.csv"
developer_repositories.to_csv(developer_repositories_file, index=False)

print(f"開発者ごとの貢献リポジトリデータを {developer_repositories_file} に保存しました。")
