import pandas as pd
from scipy.stats import f_oneway

# データ読み込み
file_path = "/Users/kazuki-h/scripts/results/into_zookeeper.csv"  # ファイルパスを指定
data = pd.read_csv(file_path)

# グループごとにデータを分割
groups = [group["into"].values for name, group in data.groupby("dependencies")]

# 一元分散分析 (ANOVA)
f_stat, p_value = f_oneway(*groups)
print("ANOVA Results:")
print(f"F-statistic: {f_stat:.2f}, p-value: {p_value:.4f}")

# 統計量の計算
group_stats = data.groupby("dependencies")["into"].agg(['mean', 'std', 'var', 'count'])
print("\nGroup Statistics:")
print(group_stats)

# 結果解釈
if p_value < 0.05:
    print("\n結果: 有意差があります (p < 0.05)")
else:
    print("\n結果: 有意差はありません (p >= 0.05)")
