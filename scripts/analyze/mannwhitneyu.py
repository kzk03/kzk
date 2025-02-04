import pandas as pd
from scipy.stats import mannwhitneyu
import numpy as np

# データ読み込み
file_path = "/Users/kazuki-h/scripts/results/movement/out_dependencies.csv"  # CSVファイルのパスを指定
data = pd.read_csv(file_path)

# グループの選択（2つのグループに限定）
group1 = data[data["dependencies"] == "Direct"]["out"]
group2 = data[data["dependencies"] == "No"]["out"]

# マンホイットニーU検定
u_stat, p_value = mannwhitneyu(group1, group2, alternative='two-sided')
print("Mann-Whitney U Test Results:")
print(f"U-statistic: {u_stat:.2f}, p-value: {p_value:.30f}")

# 結果解釈
if p_value < 0.05:
    print("結果: 有意差があります (p < 0.05)")
else:
    print("結果: 有意差はありません (p >= 0.05)")

# 効果量の計算 (Cliff's Delta)
n1, n2 = len(group1), len(group2)
rank_diff = [np.sign(x1 - x2) for x1 in group1 for x2 in group2]
cliffs_delta = sum(rank_diff) / (n1 * n2)
print(f"\nCliff's Delta (効果量): {cliffs_delta:.3f}")

# 効果量の解釈
if abs(cliffs_delta) < 0.147:
    interpretation = "ごく小さい効果"
elif abs(cliffs_delta) < 0.33:
    interpretation = "小さい効果"
elif abs(cliffs_delta) < 0.474:
    interpretation = "中程度の効果"
else:
    interpretation = "大きい効果"
print(f"効果量の解釈: {interpretation}")
