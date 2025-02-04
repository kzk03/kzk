import pandas as pd

# CSVファイルのパスを指定
file_path = "/Users/kazuki-h/scripts/results/repository_data_with_repo.csv"  # ファイル名を適切に設定

data = pd.read_csv(file_path)

# 重複数をカウント
repo_counts = data['repo_base'].value_counts().reset_index()
repo_counts.columns = ['repo_base', 'count']  # 列名を設定

# 確認
print(repo_counts)

# CSVファイルに保存
repo_counts.to_csv("repo_kinds.csv", index=False)