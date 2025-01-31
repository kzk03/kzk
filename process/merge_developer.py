import os
import pandas as pd

# ディレクトリを指定
directory_path = "../results/developer_data"

# CSVファイルのパスを動的に取得
file_paths = {os.path.splitext(f)[0]: os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith(".csv")}

# 結果を格納するリスト
results = []

# 各ファイルを処理
for file_name, file_path in file_paths.items():
    try:
        # ファイル名から開発者名を抽出
        developer = file_name.split("_")[0]
        
        # ファイルを読み込む
        df = pd.read_csv(file_path)
        
        # repository_url列、created_at列、comments列を抽出
        if 'repository_url' in df.columns and 'created_at' in df.columns and 'comments' in df.columns:
            for _, row in df[['repository_url', 'created_at', 'comments']].dropna().iterrows():
                results.append({
                    "開発者名": developer,
                    "貢献先リポジトリ": row['repository_url'],
                    "作成日": row['created_at'],
                    "コメント数": row['comments']
                })
    except Exception as e:
        print(f"Error processing {file_name}: {e}")

# データフレームに変換
final_df = pd.DataFrame(results)

# ファイルに保存
output_file = "../results/developer_merge_contributions.csv"
final_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"結果は次のファイルに保存されました: {output_file}")
