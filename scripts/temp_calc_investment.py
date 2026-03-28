import pandas as pd

# CSVを読み込み
df = pd.read_csv('investment_simulation/data/sample_sbi_emaxis_slim_sp500.csv', encoding='utf-8-sig')

# 数値に変換
df['金額(円)'] = pd.to_numeric(df['金額(円)'])
df['数量(口)'] = pd.to_numeric(df['数量(口)'])
df['個別元本'] = pd.to_numeric(df['個別元本'])

# 累計投資額を計算
cumulative = 0
buy_total = 0
sell_total = 0

print('=== 累計投資額の推移 ===\n')

for idx, row in df.iterrows():
    if row['取引区分'] == '買付':
        cumulative += row['金額(円)']
        buy_total += row['金額(円)']
        print(f"{row['発生日']}: 買付 +{row['金額(円)']:>10,}円 → 累計: {cumulative:>12,.0f}円")
    elif row['取引区分'] == '売却':
        # 個別元本は1万口あたりの価格なので、実際の元本は: 数量 × 個別元本 / 10000
        sell_cost = (row['数量(口)'] * row['個別元本']) / 10000
        cumulative -= sell_cost
        sell_total += sell_cost
        print(f"{row['発生日']}: 売却 -{sell_cost:>10,.0f}円 ({row['数量(口)']:,}口 × {row['個別元本']:,.0f}円/万口) → 累計: {cumulative:>12,.0f}円")

print(f'\n{"="*60}')
print(f'【総買付額】     : {buy_total:>15,.0f}円')
print(f'【総売却元本】   : {sell_total:>15,.0f}円')
print(f'【最終累計投資額】: {cumulative:>15,.0f}円')
print(f'【買付回数】     : {len(df[df["取引区分"] == "買付"]):>15}回')
print(f'【売却回数】     : {len(df[df["取引区分"] == "売却"]):>15}回')
print(f'{"="*60}')
