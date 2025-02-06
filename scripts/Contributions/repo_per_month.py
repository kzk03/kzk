import pandas as pd
import os

# 1. データの読み込み
def load_all_contribution_data(data_dir):
    """
    ディレクトリ内の全ての開発者データを統合
    :param data_dir: データディレクトリのパス
    :return: 統合されたデータフレーム
    """
    all_data = []
    for file_name in os.listdir(data_dir):
        if file_name.endswith('.csv'):
            developer = os.path.splitext(file_name)[0].split('_')[0]  # ファイル名から開発者名を抽出
            contribution_type = os.path.splitext(file_name)[0].split('_')[1]  # PR か Issue かを判定
            df = pd.read_csv(os.path.join(data_dir, file_name))
            df['developer'] = developer  # 開発者名を追加
            df['type'] = contribution_type  # 貢献タイプを追加
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

# データディレクトリのパス
data_dir = "./../results/developer_data"
df_all = load_all_contribution_data(data_dir)

# 必要なカラムチェック
required_columns = ['developer', 'repository_url', 'created_at']
for col in required_columns:
    if col not in df_all.columns:
        raise KeyError(f"カラム '{col}' がデータに存在しません: {df_all.columns.tolist()}")

# リポジトリ名の抽出
df_all['repository'] = df_all['repository_url'].str.extract(r'repos/([^/]+/[^/]+)')

# created_at の変換と不正値除外
df_all['created_at'] = pd.to_datetime(df_all['created_at'], errors='coerce')
df_all = df_all.dropna(subset=['created_at'])  # 不正な日付を除外

# 必要なカラムを整形し時系列でソート
df_all = df_all[['repository', 'created_at', 'type']].sort_values(by='created_at')

# 2. 月単位でリポジトリごとの貢献量を集計
# 月単位での期間を追加
df_all['month'] = df_all['created_at'].dt.to_period('M')  # 月単位の列を追加

# 月単位でリポジトリとタイプごとにグループ化して集計
repository_contributions = df_all.groupby(
    ['month', 'repository', 'type']
).size().reset_index(name='contribution_count')

# 結果を確認
print(repository_contributions)

# 3. 結果を保存
output_path = "./../results/monthly_repository_contributions.csv"
repository_contributions.to_csv(output_path, index=False)

print(f"✅ 月単位でのリポジトリごとの貢献量を保存しました: {output_path}")
