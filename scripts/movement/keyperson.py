import pandas as pd
import os
from datetime import timedelta
from collections import defaultdict

# 1. データの準備
def load_all_developer_data(data_dir):
    all_data = []
    for file_name in os.listdir(data_dir):
        if file_name.endswith('.csv'):
            developer = os.path.splitext(file_name)[0].split('_')[0]
            df = pd.read_csv(os.path.join(data_dir, file_name))
            df['developer'] = developer
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

data_dir = "./../results/developer_data"
df_all = load_all_developer_data(data_dir)

# 必要なカラムチェック
required_columns = ['developer', 'repository_url', 'created_at']
for col in required_columns:
    if col not in df_all.columns:
        raise KeyError(f"カラム '{col}' がデータに存在しません: {df_all.columns.tolist()}")

# リポジトリ名の抽出
df_all['repository'] = df_all['repository_url'].str.extract(r'repos/([^/]+/[^/]+)')

# created_at の変換と不正値除外
df_all['created_at'] = pd.to_datetime(df_all['created_at'], errors='coerce')
df_all = df_all.dropna(subset=['created_at'])

# 必要なカラムを整形
df_all = df_all[['developer', 'repository', 'created_at']].sort_values(by=['developer', 'created_at'])

# 2. キーパーソンの特定（移動回数が多い人を抽出）
time_window = timedelta(days=30)
repository_movements = defaultdict(list)

for developer, group in df_all.groupby('developer'):
    for idx, row in group.iterrows():
        current_repo = row['repository']
        current_time = row['created_at']

        similar_contributions = group[
            (group['created_at'] >= current_time - time_window) &
            (group['created_at'] <= current_time + time_window) &
            (group['repository'] != current_repo)
        ]

        for _, sim_row in similar_contributions.iterrows():
            repository_movements[(developer, current_repo)].append(sim_row['repository'])

# 移動回数が多い人（キーパーソン）を特定
movement_counts = defaultdict(int)
for (developer, _), to_repos in repository_movements.items():
    movement_counts[developer] += len(set(to_repos))

# キーパーソンとして上位3名を抽出
key_persons = sorted(movement_counts.items(), key=lambda x: x[1], reverse=True)[:3]
key_persons = [person[0] for person in key_persons]

# 3. キーパーソンの移動に連動する人を分析
key_person_movements = []

for key_person in key_persons:
    key_person_data = df_all[df_all['developer'] == key_person]

    for _, row in key_person_data.iterrows():
        current_repo = row['repository']
        current_time = row['created_at']

        # キーパーソンの移動先
        next_contributions = df_all[
            (df_all['created_at'] >= current_time - time_window) &
            (df_all['created_at'] <= current_time + time_window) &
            (df_all['repository'] != current_repo) &
            (df_all['developer'] != key_person)
        ]

        for _, sim_row in next_contributions.iterrows():
            key_person_movements.append({
                "key_person": key_person,
                "from_repository": current_repo,
                "to_repository": sim_row['repository'],
                "follower": sim_row['developer'],
                "time": sim_row['created_at']
            })

# 結果をデータフレーム化
df_key_movements = pd.DataFrame(key_person_movements)

# 4. 結果を保存
output_path = "./../results/key_person_movements.csv"
df_key_movements.to_csv(output_path, index=False)
print(f"✅ キーパーソンの移動分析結果を保存しました: {output_path}")
