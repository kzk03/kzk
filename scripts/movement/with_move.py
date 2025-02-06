import pandas as pd
import os
from datetime import timedelta
from collections import defaultdict

# 1. データの読み込み
def load_all_developer_data(data_dir):
    """
    ディレクトリ内の全ての開発者データを統合
    :param data_dir: データディレクトリのパス
    :return: 統合されたデータフレーム
    """
    all_data = []
    for file_name in os.listdir(data_dir):
        if file_name.endswith('.csv'):
            # ファイル名から開発者名を抽出（アンダースコアの前の部分）
            developer = os.path.splitext(file_name)[0].split('_')[0]
            df = pd.read_csv(os.path.join(data_dir, file_name))
            df['developer'] = developer  # 抽出した開発者名を追加
            all_data.append(df)
    
    return pd.concat(all_data, ignore_index=True)

# データディレクトリのパスを指定
data_dir = "./../results/developer_data"
df_all = load_all_developer_data(data_dir)

# 必要なカラムをチェック
required_columns = ['developer', 'repository_url', 'created_at']
for col in required_columns:
    if col not in df_all.columns:
        raise KeyError(f"カラム '{col}' がデータに存在しません。現在のカラム: {df_all.columns.tolist()}")

# 2. 'repository_url' から 'repository' を生成
# URLの形式: https://api.github.com/repos/owner_name/repository_name
df_all['repository'] = df_all['repository_url'].str.extract(r'repos/([^/]+/[^/]+)')

# 必要なカラムを選択して確認
print("生成されたカラム 'repository':")
print(df_all[['repository_url', 'repository']].head())

# 'created_at' カラムをタイムスタンプ形式に変換（不正値を処理）
df_all['created_at'] = pd.to_datetime(df_all['created_at'], errors='coerce')

# 不正値を除外
if df_all['created_at'].isna().any():
    print("不正な値が含まれています。除外します。")
    invalid_values = df_all.loc[df_all['created_at'].isna()]
    print("不正値:", invalid_values)
    df_all = df_all.dropna(subset=['created_at'])

# 必要なカラムを選択して並び替え
df_all = df_all[['developer', 'repository', 'created_at']].sort_values(by=['developer', 'created_at'])

# 3. 幅を持たせた移動のための期間設定
time_window = timedelta(days=5)  # 30日間の幅を設定

# 4. 期間内のリポジトリ移動を分析
movement_groups = defaultdict(list)

for developer, group in df_all.groupby('developer'):
    # 開発者ごとの貢献履歴を取得
    for idx, row in group.iterrows():
        # 現在のリポジトリとそのタイムスタンプを取得
        current_repo = row['repository']
        current_time = row['created_at']

        # 幅を持たせた期間で他の開発者を調査
        recent_contributions = df_all[
            (df_all['created_at'] >= current_time - time_window) &
            (df_all['created_at'] <= current_time + time_window) &
            (df_all['repository'] == current_repo) &  # 同じリポジトリを対象
            (df_all['developer'] != developer)       # 自分以外の開発者
        ]

        # 同時に行動している開発者を収集
        for _, matched_row in recent_contributions.iterrows():
            movement_groups[(developer, current_repo)].append(matched_row['developer'])

# 結果を整形
results = []
for key, developers in movement_groups.items():
    dev, repo = key
    results.append({
        "developer": dev,
        "repository": repo,
        "co_contributors": list(set(developers)),  # 重複を排除
        "co_count": len(set(developers))
    })

# データフレーム化
df_results = pd.DataFrame(results)

# 結果を保存
output_path = "./../results/5_co_contribution_analysis.csv"
df_results.to_csv(output_path, index=False)

print(f"✅ 分析結果を '{output_path}' に保存しました！")
