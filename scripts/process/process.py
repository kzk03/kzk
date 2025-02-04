import pandas as pd

# CSVファイルを読み込む（ファイルパスを指定）
input_file = "./results/developer_merge_contributions.csv"  # ファイル名を適宜変更
output_file = "./results/repository_data_with_repo.csv"  # 保存先ファイル

# データを読み込む
df = pd.read_csv(input_file)

# repository_url列からrepo（apache/helix）を抽出
df["repo"] = df["repository_url"].apply(lambda x: "/".join(x.split("/")[-2:]) if pd.notnull(x) else None)

# repository_url列からrepo_base（helix）を抽出
df["repo_base"] = df["repository_url"].apply(lambda x: x.split("/")[-1] if pd.notnull(x) else None)

# 結果を保存
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"処理が完了しました。結果は以下のファイルに保存されています: {output_file}")
