import os
import pandas as pd

# データディレクトリのパス（変更してください）
data_dir = "../../results/developer_data"

# 開発者ごとの Issue コメント数と Pull Request コメント数を格納する辞書
developer_comments = {}

# ディレクトリ内のすべてのCSVファイルを取得
for filename in os.listdir(data_dir):
    file_path = os.path.join(data_dir, filename)
    
    # CSVファイルのみ処理
    if filename.endswith(".csv"):
        # CSVデータを読み込む
        df = pd.read_csv(file_path)
        
        # 開発者名をファイル名から取得（"developer_issues.csv" や "developer_pulls.csv" の形式を想定）
        developer_name = filename.split("_")[0]

        # コメントの種類を判別（Issue か Pull Request か）
        if "issues" in filename:
            comment_type = "issue_comments"
        elif "pulls" in filename:
            comment_type = "pull_comments"
        else:
            continue  # その他のファイルは無視

        # 'comments' カラムが存在する場合のみ処理
        if 'comments' in df.columns:
            # 数値型に変換（エラーが出るデータは 0 にする）
            df['comments'] = pd.to_numeric(df['comments'], errors='coerce').fillna(0).astype(int)
            total_comments = df['comments'].sum()
            
            # 開発者ごとのコメント数を集計
            if developer_name not in developer_comments:
                developer_comments[developer_name] = {"issue_comments": 0, "pull_comments": 0}

            developer_comments[developer_name][comment_type] += total_comments

# 結果をデータフレームに変換
df_comments = pd.DataFrame.from_dict(developer_comments, orient="index").reset_index()
df_comments.rename(columns={"index": "Developer"}, inplace=True)

# 結果をCSVに保存（オプション）
output_path = os.path.join(data_dir, "../../results/developer_comments_split.csv")
df_comments.to_csv(output_path, index=False)

# 結果を表示
print(df_comments)
print(f"結果を {output_path} に保存しました。")
