"""
analyze_all_strategies メソッドのテストスクリプト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'life_insurance'))

from life_insurance.analysis.withdrawal_optimizer import WithdrawalOptimizer
import numpy as np

def test_analyze_all_strategies():
    """analyze_all_strategies メソッドのテスト"""
    print("=== analyze_all_strategies テスト開始 ===\n")
    
    # パラメータ設定
    annual_premium = 108000  # 月9,000円 × 12
    taxable_income = 6000000  # 課税所得600万円
    policy_start_year = 2010  # 2025-15年
    contract_years = 20
    withdrawal_year = 15
    annual_interest_rate = 0.0125  # 1.25%
    
    # パラメータ範囲生成
    base_year = withdrawal_year
    base_rate = 0.5
    year_range = list(range(max(5, base_year-5), min(contract_years, base_year+5)+1))
    rate_min = max(0.01, base_rate-0.5)
    rate_max = min(1.0, base_rate+0.5)
    rate_range = [round(r, 2) for r in list(np.arange(rate_min, rate_max+0.01, 0.1)) if r > 0]
    interval_range = [1, 2, 3, 4, 5]
    switch_rates = [0.01, 0.02, 0.03, 0.04, 0.05]
    
    print("パラメータ:")
    print(f"  年間保険料: {annual_premium:,}円")
    print(f"  課税所得: {taxable_income:,}円")
    print(f"  契約期間: {contract_years}年")
    print(f"  年利: {annual_interest_rate*100:.2f}%")
    print(f"  引き出し年範囲: {year_range}")
    print(f"  部分解約割合範囲: {rate_range}")
    print(f"  部分解約間隔範囲: {interval_range}")
    print(f"  乗り換え手数料率: {switch_rates}")
    print()
    
    # WithdrawalOptimizer インスタンス作成
    optimizer = WithdrawalOptimizer()
    
    print("analyze_all_strategies を実行中...\n")
    
    try:
        # 複数戦略同時比較（部分解約後は預金1%で再投資）
        df_strategies = optimizer.analyze_all_strategies(
            initial_premium=0,
            annual_premium=annual_premium,
            taxable_income=taxable_income,
            policy_start_year=policy_start_year,
            interval_range=interval_range,
            rate_range=rate_range,
            full_withdrawal_years=year_range,
            switch_years=year_range,
            switch_rates=switch_rates,
            max_years=contract_years,
            return_rate=annual_interest_rate,
            withdrawal_reinvest_rate=0.01  # 預金1%で再投資
        )
        
        print("✅ 実行成功！\n")
        print(f"戦略数: {len(df_strategies)}")
        print(f"\nTop 10 戦略ランキング:\n")
        print(df_strategies.head(10).to_string(index=False))
        
        print(f"\n\n戦略タイプ別集計:")
        print(df_strategies.groupby("戦略タイプ")["純利益(円)"].agg(['count', 'mean', 'max']).to_string())
        
        # 再投資利回りの影響を検証
        print("\n\n=== 再投資利回りの影響分析 ===\n")
        
        reinvest_scenarios = [
            ("運用なし（現金保有）", 0.00),
            ("預金（年利1%）", 0.01),
            ("投資信託（年利3%）", 0.03),
            ("投資信託（年利5%）", 0.05)
        ]
        
        comparison_results = []
        
        for scenario_name, reinvest_rate in reinvest_scenarios:
            df_scenario = optimizer.analyze_all_strategies(
                initial_premium=0,
                annual_premium=annual_premium,
                taxable_income=taxable_income,
                policy_start_year=policy_start_year,
                interval_range=[2],  # 2年間隔のみ
                rate_range=[0.51],   # 51%解約のみ
                full_withdrawal_years=[15],  # 15年後全解約のみ
                switch_years=[],  # 乗り換えなし
                switch_rates=[],
                max_years=contract_years,
                return_rate=annual_interest_rate,
                withdrawal_reinvest_rate=reinvest_rate
            )
            
            partial_withdrawal = df_scenario[df_scenario["戦略タイプ"] == "部分解約"]
            full_withdrawal = df_scenario[df_scenario["戦略タイプ"] == "全解約"]
            
            if not partial_withdrawal.empty:
                partial_benefit = partial_withdrawal["純利益(円)"].iloc[0]
            else:
                partial_benefit = 0
            
            if not full_withdrawal.empty:
                full_benefit = full_withdrawal["純利益(円)"].iloc[0]
            else:
                full_benefit = 0
            
            comparison_results.append({
                "再投資シナリオ": scenario_name,
                "再投資利回り": f"{reinvest_rate*100:.1f}%",
                "部分解約純利益": f"{partial_benefit:,.0f}円",
                "全解約純利益": f"{full_benefit:,.0f}円",
                "差額": f"{partial_benefit - full_benefit:+,.0f}円"
            })
        
        import pandas as pd
        df_comparison = pd.DataFrame(comparison_results)
        print(df_comparison.to_string(index=False))
        
        print("\n💡 結論:")
        print("  - 部分解約後の資金の運用利回りが高いほど、部分解約戦略の純利益が増加")
        print("  - 再投資利回りが保険の運用利回りを上回る場合、部分解約戦略が有利")
        print("  - 預金（1%）程度でも、適切なタイミングでの部分解約により資金効率が向上")
        
    except Exception as e:
        print(f"❌ エラー発生: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"analyze_all_strategies の実行中に例外: {type(e).__name__}: {e}")


if __name__ == "__main__":
    try:
        test_analyze_all_strategies()
        print("\n\n=== テスト完了: 成功 ✅ ===")
    except Exception:
        print("\n\n=== テスト完了: 失敗 ❌ ===")
        sys.exit(1)
