"""
生命保険 vs 投資信託 比較分析アプリ

旧生命保険料控除を活用した生命保険と、投資信託（eMAXIS Slim S&P500等）の
資産形成効果を詳細に比較するための専用Streamlitアプリケーション。

使用方法:
    streamlit run life_insurance/ui/comparison_app.py

主要機能:
- 生命保険料控除の節税効果を考慮した実質リターン計算
- 投資信託の運用益・手数料を考慮した比較
- 税制の違いを反映した詳細分析
- インタラクティブなグラフによる可視化

注意:
このアプリは投資信託との比較に特化しています。
生命保険の引き出しタイミング最適化は streamlit_app.py をご利用ください。
"""

# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from life_insurance.core.deduction_calculator import LifeInsuranceDeductionCalculator
from life_insurance.core.tax_calculator import TaxCalculator

# Phase 2統合: InsuranceCalculatorとモデル
from life_insurance.analysis.insurance_calculator import InsuranceCalculator
from life_insurance.models import InsurancePlan, FundPlan


def main():
    """保険 vs 投資信託比較アプリ"""
    st.set_page_config(page_title="保険 vs 投資信託 比較分析", page_icon="⚖️", layout="wide")

    st.title("⚖️ 保険 vs 投資信託 比較分析")
    st.markdown("---")
    st.markdown(
        "**生命保険料控除を使った場合と、控除を使わずにeMAXIS Slim S&P500に投資した場合の実質的なリターンを比較します**"
    )

    show_insurance_vs_investment_comparison()


def show_insurance_vs_investment_comparison():
    """保険 vs 投資信託の比較分析"""
    st.markdown(
        """
    この分析では、以下の2つのシナリオを比較します：
    
    1. **純粋投資信託**: 生命保険控除を使わずに、全額をeMAXIS Slim S&P500に投資
    2. **保険+投資信託**: 生命保険控除の限度額まで保険に加入し、一定のタイミングで引き出して投資信託に移行
    """
    )

    # 共通パラメータ設定
    st.subheader("📊 比較条件設定")

    col1, col2 = st.columns(2)
    with col1:
        monthly_amount = st.number_input(
            "月額投資金額（円）",
            min_value=5000,
            max_value=50000,
            value=9000,
            step=1000,
            help="毎月投資する金額を設定してください",
        )
        annual_income = (
            st.number_input(
                "年間課税所得（万円）",
                min_value=200,
                max_value=2000,
                value=500,
                step=50,
                help="税額計算の基礎となる年間課税所得",
            )
            * 10000
        )
        analysis_years = st.slider(
            "分析期間（年）", min_value=5, max_value=30, value=20, help="分析する期間を年単位で設定"
        )

    with col2:
        # 投資信託設定
        st.markdown("**📈 投資信託設定（eMAXIS Slim S&P500想定）**")
        investment_return = (
            st.number_input(
                "年利 (%)",
                min_value=3.0,
                max_value=10.0,
                value=7.0,
                step=0.1,
                help="S&P500の長期平均リターン想定",
            )
            / 100
        )
        investment_fee = (
            st.number_input(
                "信託報酬 (%)",
                min_value=0.0,
                max_value=1.0,
                value=0.0968,
                step=0.01,
                help="eMAXIS Slim S&P500の実際の信託報酬",
            )
            / 100
        )

        # 保険設定
        st.markdown("**🏦 生命保険設定**")
        insurance_return = (
            st.number_input(
                "保険年利 (%)",
                min_value=0.5,
                max_value=3.0,
                value=1.25,
                step=0.05,
                help="保険の予定利率",
            )
            / 100
        )
        setup_fee_rate = (
            st.number_input(
                "初回手数料 (%)",
                min_value=0.5,
                max_value=3.0,
                value=1.3,
                step=0.1,
                help="保険加入時の手数料",
            )
            / 100
        )
        monthly_fee_rate = (
            st.number_input(
                "年間管理手数料 (%)",
                min_value=0.005,
                max_value=0.02,
                value=0.096,
                step=0.001,
                help="保険の年間管理手数料（残高に対して）",
            )
            / 100
        )

    # 引き出しタイミング設定
    st.subheader("⏰ 保険引き出し戦略")

    col1, col2 = st.columns(2)
    with col1:
        withdrawal_strategy = st.selectbox(
            "引き出し戦略",
            [
                "元本回収後すぐに投資信託へ",
                "5年後に投資信託へ",
                "10年後に投資信託へ",
                "15年後に投資信託へ",
                "満期まで保険継続",
            ],
            help="保険をいつ解約して投資信託に移行するかを選択",
        )

    with col2:
        if withdrawal_strategy != "満期まで保険継続":
            reinvest_strategy = st.selectbox(
                "引き出し後の投資戦略",
                ["一括投資信託へ", "引き出し額＋継続月額投資"],
                help="保険解約後の投資方法を選択",
            )
        else:
            reinvest_strategy = "保険継続"

    if st.button("🔍 詳細比較分析を実行", type="primary"):
        with st.spinner("計算中..."):
            # 税金計算機を初期化
            tax_calc = TaxCalculator()

            # 1. 純粋投資信託シナリオ
            investment_scenario = calculate_pure_investment_scenario(
                monthly_amount, investment_return, investment_fee, analysis_years
            )

            # 2. 保険＋投資信託シナリオ
            insurance_scenario = calculate_insurance_investment_scenario(
                monthly_amount,
                annual_income,
                insurance_return,
                setup_fee_rate,
                monthly_fee_rate,
                withdrawal_strategy,
                investment_return,
                investment_fee,
                analysis_years,
                tax_calc,
                reinvest_strategy,
            )

            # 結果表示
            display_comparison_results(
                investment_scenario,
                insurance_scenario,
                analysis_years,
                monthly_amount,
                withdrawal_strategy,
            )


def calculate_pure_investment_scenario(monthly_amount, annual_return, fee_rate, years):
    """純粋な投資信託投資シナリオ計算"""
    net_return = annual_return - fee_rate
    monthly_return = net_return / 12

    results = []
    total_invested = 0
    account_value = 0

    for year in range(1, years + 1):
        for month in range(12):
            total_invested += monthly_amount
            account_value = (account_value + monthly_amount) * (1 + monthly_return)

        results.append(
            {
                "year": year,
                "total_invested": total_invested,
                "account_value": account_value,
                "profit": account_value - total_invested,
                "annual_return": (
                    ((account_value / total_invested) ** (1 / year) - 1) * 100
                    if total_invested > 0
                    else 0
                ),
            }
        )

    return results


def calculate_insurance_investment_scenario(
    monthly_amount,
    annual_income,
    insurance_return,
    setup_fee_rate,
    monthly_fee_rate,
    withdrawal_strategy,
    investment_return,
    investment_fee,
    years,
    tax_calc,
    reinvest_strategy,
):
    """
    保険＋投資信託シナリオ計算

    Phase 2で統合されたInsuranceCalculatorを使用。
    """

    # 年間保険料と控除計算
    annual_premium = monthly_amount * 12
    monthly_premium = monthly_amount

    # 引き出しタイミングの決定
    if withdrawal_strategy == "元本回収後すぐに投資信託へ":
        withdrawal_year = calculate_breakeven_year(
            annual_premium, insurance_return, setup_fee_rate, monthly_fee_rate
        )
    elif withdrawal_strategy == "5年後に投資信託へ":
        withdrawal_year = 5
    elif withdrawal_strategy == "10年後に投資信託へ":
        withdrawal_year = 10
    elif withdrawal_strategy == "15年後に投資信託へ":
        withdrawal_year = 15
    else:
        withdrawal_year = years  # 満期まで継続

    # InsurancePlanに変換
    insurance_plan = InsurancePlan(
        monthly_premium=monthly_premium,
        annual_rate=insurance_return * 100,
        investment_period=years,
        fee_rate=setup_fee_rate,
        balance_fee_rate=monthly_fee_rate / 12,  # 月次手数料に変換
        withdrawal_fee_rate=0.01,
    )

    # FundPlanに変換
    net_investment_return = investment_return - investment_fee
    fund_plan = FundPlan(
        annual_return=net_investment_return * 100,
        annual_fee=0.0,  # 既に差し引き済み
        capital_gains_tax_rate=0.20315,
        reinvestment_rate=1.0 if reinvest_strategy == "引き出し額＋継続月額投資" else 0.0,
        use_nisa=False,
    )

    # InsuranceCalculatorで計算
    calculator = InsuranceCalculator()
    result = calculator.calculate_switching_value(
        insurance_plan=insurance_plan,
        switch_year=withdrawal_year,
        fund_plan=fund_plan,
        taxable_income=annual_income,
    )

    # 年次結果を生成
    results = []
    total_invested = 0

    for year in range(1, years + 1):
        total_invested = annual_premium * year

        if year <= withdrawal_year:
            # 保険期間中
            # 簡易推定（線形補間）
            insurance_value = result.surrender_value * (year / withdrawal_year)
            investment_value = 0
            total_tax_savings = result.tax_benefit * (year / years)
        else:
            # 引き出し後
            insurance_value = 0
            # 投資信託価値の推定
            remaining_ratio = (year - withdrawal_year) / (years - withdrawal_year)
            investment_value = result.reinvestment_value * remaining_ratio
            total_tax_savings = result.tax_benefit

        total_value = insurance_value + investment_value + total_tax_savings

        results.append(
            {
                "year": year,
                "total_invested": total_invested,
                "insurance_value": insurance_value,
                "investment_value": investment_value,
                "total_tax_savings": total_tax_savings,
                "total_value": total_value,
                "profit": total_value - total_invested,
                "annual_return": (
                    ((total_value / total_invested) ** (1 / year) - 1) * 100
                    if total_invested > 0
                    else 0
                ),
                "withdrawal_year": withdrawal_year,
            }
        )

    return results


def calculate_breakeven_year(annual_premium, insurance_return, setup_fee_rate, monthly_fee_rate):
    """
    元本回収年を計算

    Phase 2で統合されたInsuranceCalculatorを使用。
    """
    monthly_premium = annual_premium / 12

    # InsurancePlanに変換
    insurance_plan = InsurancePlan(
        monthly_premium=monthly_premium,
        annual_rate=insurance_return * 100,
        investment_period=30,  # 最大30年
        fee_rate=setup_fee_rate,
        balance_fee_rate=monthly_fee_rate / 12,  # 月次手数料
        withdrawal_fee_rate=0.0,
    )

    # FundPlanはダミー（使用しない）
    fund_plan = FundPlan(
        annual_return=0.0,
        annual_fee=0.0,
        capital_gains_tax_rate=0.20315,
        reinvestment_rate=0.0,
        use_nisa=False,
    )

    # InsuranceCalculatorで計算
    calculator = InsuranceCalculator()
    breakeven_year = calculator.calculate_breakeven_year(
        insurance_plan=insurance_plan, fund_plan=fund_plan, max_years=30
    )

    return breakeven_year if breakeven_year else 30


def display_comparison_results(
    investment_scenario, insurance_scenario, years, monthly_amount, withdrawal_strategy
):
    """比較結果の表示"""

    st.success("✅ 分析完了！")

    # 最終年の結果比較
    final_investment = investment_scenario[-1]
    final_insurance = insurance_scenario[-1]

    st.subheader("🏆 最終結果比較（{}年後）".format(years))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "純投資信託",
            f"{final_investment['account_value']:,.0f}円",
            f"利益: +{final_investment['profit']:,.0f}円",
        )
        st.caption(f"年率リターン: {final_investment['annual_return']:.2f}%")

    with col2:
        st.metric(
            "保険＋投資信託",
            f"{final_insurance['total_value']:,.0f}円",
            f"利益: +{final_insurance['profit']:,.0f}円",
        )
        st.caption(f"年率リターン: {final_insurance['annual_return']:.2f}%")

    with col3:
        difference = final_insurance["total_value"] - final_investment["account_value"]
        advantage = "保険併用有利" if difference > 0 else "純投資有利"

        st.metric("差額", f"{difference:+,.0f}円", advantage)

        if difference > 0:
            percentage_advantage = (difference / final_investment["account_value"]) * 100
            st.caption(f"保険併用が {percentage_advantage:.1f}% 有利")
        else:
            percentage_advantage = (abs(difference) / final_insurance["total_value"]) * 100
            st.caption(f"純投資が {percentage_advantage:.1f}% 有利")

    # 詳細分析
    st.subheader("📊 詳細分析")

    # 累計節税効果
    total_tax_savings = final_insurance["total_tax_savings"]
    withdrawal_year = final_insurance.get("withdrawal_year", years)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("累計節税額", f"{total_tax_savings:,.0f}円")

    with col2:
        st.metric("月額投資", f"{monthly_amount:,}円")

    with col3:
        if withdrawal_year < years:
            st.metric("保険解約年", f"{withdrawal_year}年目")
        else:
            st.metric("戦略", "保険継続")

    with col4:
        total_invested = final_investment["total_invested"]
        st.metric("累計投資額", f"{total_invested:,.0f}円")

    # グラフ表示
    st.subheader("📈 資産推移比較")

    # データフレーム作成
    df_investment = pd.DataFrame(investment_scenario)
    df_insurance = pd.DataFrame(insurance_scenario)

    # Plotlyでインタラクティブグラフ
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_investment["year"],
            y=df_investment["account_value"],
            name="純投資信託",
            line=dict(color="blue", width=3),
            hovertemplate="年: %{x}<br>資産価値: %{y:,.0f}円<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_insurance["year"],
            y=df_insurance["total_value"],
            name="保険＋投資信託",
            line=dict(color="red", width=3),
            hovertemplate="年: %{x}<br>資産価値: %{y:,.0f}円<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_insurance["year"],
            y=df_insurance["total_invested"],
            name="累計投資額",
            line=dict(color="gray", dash="dash", width=2),
            hovertemplate="年: %{x}<br>投資額: %{y:,.0f}円<extra></extra>",
        )
    )

    # 解約タイミングをマーク
    if withdrawal_year < years:
        fig.add_vline(
            x=withdrawal_year,
            line_dash="dot",
            line_color="orange",
            annotation_text=f"保険解約({withdrawal_year}年目)",
        )

    fig.update_layout(
        title="資産価値推移比較",
        xaxis_title="年数",
        yaxis_title="資産価値（円）",
        hovermode="x unified",
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)

    # 年別損益グラフ
    st.subheader("💰 年別損益比較")

    profit_fig = go.Figure()

    profit_fig.add_trace(
        go.Scatter(
            x=df_investment["year"],
            y=df_investment["profit"],
            name="純投資信託利益",
            line=dict(color="blue", width=3),
            fill="tonexty",
        )
    )

    profit_fig.add_trace(
        go.Scatter(
            x=df_insurance["year"],
            y=df_insurance["profit"],
            name="保険＋投資信託利益",
            line=dict(color="red", width=3),
            fill="tonexty",
        )
    )

    profit_fig.update_layout(
        title="累計利益の推移",
        xaxis_title="年数",
        yaxis_title="利益（円）",
        hovermode="x unified",
        height=400,
    )

    st.plotly_chart(profit_fig, use_container_width=True)

    # 詳細データ表
    st.subheader("📋 年次詳細データ")

    tab1, tab2, tab3 = st.tabs(["📊 比較サマリー", "🔍 詳細内訳", "📈 リターン分析"])

    with tab1:
        comparison_df = pd.DataFrame(
            {
                "年": df_investment["year"],
                "純投資信託価値": df_investment["account_value"].apply(lambda x: f"{x:,.0f}円"),
                "保険＋投資信託価値": df_insurance["total_value"].apply(lambda x: f"{x:,.0f}円"),
                "差額": (df_insurance["total_value"] - df_investment["account_value"]).apply(
                    lambda x: f"{x:+,.0f}円"
                ),
                "投資信託利益": df_investment["profit"].apply(lambda x: f"{x:,.0f}円"),
                "保険組合せ利益": df_insurance["profit"].apply(lambda x: f"{x:,.0f}円"),
                "投資信託年率": df_investment["annual_return"].apply(lambda x: f"{x:.2f}%"),
                "保険組合せ年率": df_insurance["annual_return"].apply(lambda x: f"{x:.2f}%"),
            }
        )

        st.dataframe(comparison_df, hide_index=True, use_container_width=True)

    with tab2:
        detailed_df = pd.DataFrame(
            {
                "年": df_insurance["year"],
                "累計投資額": df_insurance["total_invested"].apply(lambda x: f"{x:,.0f}円"),
                "保険価値": df_insurance["insurance_value"].apply(lambda x: f"{x:,.0f}円"),
                "投資信託価値": df_insurance["investment_value"].apply(lambda x: f"{x:,.0f}円"),
                "累計節税額": df_insurance["total_tax_savings"].apply(lambda x: f"{x:,.0f}円"),
                "合計価値": df_insurance["total_value"].apply(lambda x: f"{x:,.0f}円"),
            }
        )

        st.dataframe(detailed_df, hide_index=True, use_container_width=True)

    with tab3:
        # リターン比較分析
        st.markdown("#### 年率リターン推移")

        return_fig = go.Figure()

        return_fig.add_trace(
            go.Scatter(
                x=df_investment["year"],
                y=df_investment["annual_return"],
                name="純投資信託年率",
                line=dict(color="blue", width=3),
            )
        )

        return_fig.add_trace(
            go.Scatter(
                x=df_insurance["year"],
                y=df_insurance["annual_return"],
                name="保険＋投資信託年率",
                line=dict(color="red", width=3),
            )
        )

        return_fig.update_layout(
            title="実質年率リターン推移",
            xaxis_title="年数",
            yaxis_title="年率リターン（%）",
            hovermode="x unified",
            height=400,
        )

        st.plotly_chart(return_fig, use_container_width=True)

        # 統計サマリー
        st.markdown("#### 📊 統計サマリー")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**純投資信託**")
            st.write(f"- 最終年率リターン: {final_investment['annual_return']:.2f}%")
            st.write(f"- 最大年間利益: {max([s['profit'] for s in investment_scenario]):,.0f}円")
            st.write(
                f"- 投資効率: {final_investment['profit']/final_investment['total_invested']*100:.1f}%"
            )

        with col2:
            st.markdown("**保険＋投資信託**")
            st.write(f"- 最終年率リターン: {final_insurance['annual_return']:.2f}%")
            st.write(f"- 最大年間利益: {max([s['profit'] for s in insurance_scenario]):,.0f}円")
            st.write(
                f"- 投資効率: {final_insurance['profit']/final_insurance['total_invested']*100:.1f}%"
            )
            st.write(
                f"- 節税効果: {total_tax_savings:,.0f}円 ({total_tax_savings/final_insurance['total_invested']*100:.1f}%)"
            )

    # 推奨事項
    st.subheader("💡 推奨事項")

    if difference > 0:
        st.success(
            f"""
        **保険併用戦略が有利**: {difference:,.0f}円の追加利益
        
        - 生命保険料控除による節税効果: {total_tax_savings:,.0f}円
        - {withdrawal_strategy}の戦略が効果的
        - 長期的な資産形成において保険併用が有効
        """
        )
    else:
        st.warning(
            f"""
        **純投資信託戦略が有利**: {abs(difference):,.0f}円の追加利益
        
        - 投資信託の複利効果が保険の節税効果を上回る
        - 手数料や保険コストが利益を圧迫
        - より積極的な資産運用を検討することを推奨
        """
        )

    # ダウンロード機能
    st.subheader("💾 結果データダウンロード")

    # 比較結果をCSV形式で準備
    export_df = pd.DataFrame(
        {
            "年": df_investment["year"],
            "純投資信託価値": df_investment["account_value"],
            "保険組合せ価値": df_insurance["total_value"],
            "純投資信託利益": df_investment["profit"],
            "保険組合せ利益": df_insurance["profit"],
            "差額": df_insurance["total_value"] - df_investment["account_value"],
            "累計節税額": df_insurance["total_tax_savings"],
            "投資信託年率": df_investment["annual_return"],
            "保険組合せ年率": df_insurance["annual_return"],
        }
    )

    csv_data = export_df.to_csv(index=False, encoding="utf-8-sig")

    st.download_button(
        label="📁 比較結果をCSVダウンロード",
        data=csv_data,
        file_name=f"insurance_vs_investment_comparison_{monthly_amount}_{years}years.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
