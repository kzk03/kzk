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

# 必要なカラムの存在を確認
required_columns = ['developer', 'repository_url', 'created_at', 'type']
for col in required_columns:
    if col not in df_all.columns:
        raise KeyError(f"カラム '{col}' がデータに存在しません: {df_all.columns.tolist()}")

# 2. リポジトリ名の抽出
df_all['repository'] = df_all['repository_url'].str.extract(r'repos/([^/]+/[^/]+)')

# 3. created_at を datetime 型に変換
df_all['created_at'] = pd.to_datetime(df_all['created_at'], errors='coerce')
df_all = df_all.dropna(subset=['created_at'])  # 不正な日付を除外

# 4. 月ごとに集計するための列を追加
df_all['month'] = df_all['created_at'].dt.to_period('M')  # 年月単位で集計

# 5. データを集計
monthly_contributions = df_all.groupby(['developer', 'repository', 'month', 'type']).size().reset_index(name='contribution_count')

# 6. 結果を保存
output_path = "./../results/monthly_contributions.csv"
monthly_contributions.to_csv(output_path, index=False)

print(f"✅ 1か月ごとの貢献量を '{output_path}' に保存しました！")
