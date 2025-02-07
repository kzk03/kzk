import matplotlib.pyplot as plt
import pandas as pd

# 1. CSVファイルを読み込む
file_path = "/Users/kazuki-h/scripts/results/into_zookeeper.csv"  # ここにCSVファイルのパスを入力
data = pd.read_csv(file_path)

# 2. 必要な列を確認する
print(data.head())  # データの最初の数行を表示して内容を確認

# 3. 箱ひげ図を作成する
column_name = "into"  # 箱ひげ図にする数値列の名前
group_column = "dependencies"  # グループ化する列の名前

# 箱ひげ図作成
plt.figure(figsize=(10, 6))
boxplot = data.boxplot(column=column_name, by=group_column, grid=False, vert=True, patch_artist=True)

# 4. 各グループの中央値を計算
group_medians = data.groupby(group_column)[column_name].median()
print("\nMedian values for each group:")
print(group_medians)

# 5. 箱ひげ図上に中央値を表示
for i, median in enumerate(group_medians):
    plt.text(i + 1, median, f'{median:.2f}', color='red', ha='center', va='bottom')

# グラフの装飾
plt.title(f'Boxplot of "{column_name}" Grouped by "{group_column}"')
plt.suptitle('')  # デフォルトのsuptitleを削除
plt.xlabel(group_column)
plt.ylabel(column_name)

# グラフを表示
plt.show()