import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import kruskal

# 1. CSVファイルを読み込む
file_path = "/Users/kazuki-h/scripts/results/into_zookeeper.csv"  # CSVファイルのパスを指定
data = pd.read_csv(file_path)

# 2. 必要な列を確認する
print("データの先頭5行:")
print(data.head())  # データ確認

# 3. dependenciesごとにデータを分割
groups = [group["into"].values for name, group in data.groupby("dependencies")]

# 4. Kruskal-Wallis検定を実施
h_stat, p_value = kruskal(*groups)
print("\nKruskal-Wallis Test Results:")
print(f"H-statistic: {h_stat:.2f}, p-value: {p_value:.4f}")

# 5. 結果解釈
if p_value < 0.05:
    print("結果: 有意差があります (p < 0.05)")
else:
    print("結果: 有意差はありません (p >= 0.05)")

# 6. 箱ひげ図を作成 (分布の可視化)
plt.figure(figsize=(10, 6))
data.boxplot(column="into", by="dependencies", grid=False, vert=True, patch_artist=True)

# グラフの装飾
plt.title('Boxplot of "into" Grouped by "dependencies"')
plt.suptitle('')  # デフォルトのsuptitleを削除
plt.xlabel("Dependencies")
plt.ylabel("Into Values")
plt.show()