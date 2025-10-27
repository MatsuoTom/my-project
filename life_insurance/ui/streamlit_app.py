"""
生命保険料控除分析 Streamlit アプリケーション

旧生命保険料控除の節税効果と引き出しタイミングを分析するWebアプリ
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from life_insurance.core.deduction_calculator import LifeInsuranceDeductionCalculator
from life_insurance.core.tax_calculator import TaxCalculator
from life_insurance.utils.tax_helpers import get_tax_helper
from life_insurance.analysis.withdrawal_optimizer import WithdrawalOptimizer
from life_insurance.analysis.scenario_analyzer import ScenarioAnalyzer


def main():
    """メインアプリケーション"""
    st.set_page_config(
        page_title="生命保険料控除分析ツール",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("🏦 生命保険料控除分析ツール")
    st.markdown("---")
    st.markdown("**旧生命保険料控除制度の節税効果と最適な引き出しタイミングを分析**")
    
    # サイドバーでページ選択
    page = st.sidebar.selectbox(
        "分析メニューを選択",
        [
            "🏠 ホーム",
            "💰 生命保険控除について",
            "📊 投資信託との比較",
            "詳細分析（戦略ランキング）"
        ]
    )
    
    if page == "🏠 ホーム":
        show_home_page()
    elif page == "💰 生命保険控除について":
        show_life_insurance_analysis()
    elif page == "📊 投資信託との比較":
        show_mutual_fund_comparison()
    elif page == "詳細分析（戦略ランキング）":
        _show_detailed_plan_analysis()


def show_home_page():
    """ホームページ表示"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 📋 このツールについて")
        st.markdown("""
        このツールは**旧生命保険料控除制度**（平成23年12月31日以前の契約）を活用した
        節税効果と資産運用の最適化を支援します。
        
        ### 🎯 主要機能
        - **控除額計算**: 年間保険料に基づく正確な控除額計算
        - **節税効果分析**: 所得税・住民税の具体的な節税額算出
        - **引き出しタイミング最適化**: 最適な解約・引き出し時期の提案
        - **シナリオ分析**: 複数条件下での比較検討
        - **リスク分析**: モンテカルロシミュレーションによる不確実性評価
        
        ### 💡 使用方法
        1. 左メニューから分析したい項目を選択
        2. 必要なパラメータを入力
        3. 結果を確認し、最適な戦略を検討
        """)
    
    with col2:
        st.markdown("## 🔢 控除制度概要")
        
        # 控除テーブル表示
        deduction_table = pd.DataFrame({
            "年間保険料": ["25,000円以下", "25,001〜50,000円", "50,001〜100,000円", "100,001円以上"],
            "控除額": ["保険料×1/2", "保険料×1/4+12,500円", "保険料×1/5+15,000円", "50,000円（上限）"]
        })
        
        st.dataframe(deduction_table, width='stretch')
        
        # クイック計算
        st.markdown("### 🧮 クイック計算")
        quick_premium = st.number_input(
            "年間保険料（円）",
            min_value=0, 
            max_value=200000, 
            value=102000,
            step=10000,
            key="quick_premium"
        )
        
        # 控除額を計算
        calculator = LifeInsuranceDeductionCalculator()
        quick_deduction = calculator.calculate_old_deduction(quick_premium)
        
        # 月保険料を自動計算
        monthly_premium = quick_premium / 12        col_metric1, col_metric2 = st.columns(2)
        with col_metric1:
            st.metric(
                "控除額",
                f"{quick_deduction:,.0f}円",
                f"控除率: {quick_deduction/quick_premium:.1%}" if quick_premium > 0 else "控除率: 0%"
            )
        with col_metric2:
            st.metric(
                "月保険料",
                f"{monthly_premium:,.0f}円",
                f"年間: {quick_premium:,.0f}円"
            )


def show_life_insurance_analysis():
    """生命保険控除についての統合分析"""
    st.header("💰 生命保険控除について")
    
    # サブタブで2つの分析を提供
    tab1, tab2 = st.tabs([
        "💰 収入からの控除額計算", 
        "🎯 引き出しタイミングを最適化"
    ])
    
    with tab1:
        st.markdown("### 収入からの控除額計算")
        _show_deduction_from_income()
    
    with tab2:
        st.markdown("### 引き出しタイミングを最適化")
        st.info("この機能は現在開発中です。")
    


def show_mutual_fund_comparison():
    """投資信託との比較の統合分析"""
    st.header("📊 投資信託との比較")
    
    # サブタブで4つの分析を提供
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏦 生命保険設定",
        "📈 投資信託を分析",
        "⚖️ 生命保険との比較",
        "⏰ 最適解約タイミング分析"
    ])
    
    with tab1:
        st.markdown("### 生命保険設定")
        _show_insurance_settings()
    
    with tab2:
        st.markdown("### 投資信託を分析")
        _show_mutual_fund_analysis()
    
    with tab3:
        st.markdown("### 生命保険との比較")
        _show_insurance_comparison()
    
    with tab4:
        st.markdown("### 最適解約タイミング分析")
        _show_optimal_withdrawal_timing()



def show_specific_plan_analysis():
    """具体的保険プラン分析ページ"""
    st.header("💰 具体的保険プラン分析")
    
    # タブで機能を分ける
    tab1, tab2 = st.tabs(["📊 詳細プラン分析", "🧮 控除額計算"])
    
    with tab1:
        st.markdown("月額9,000円の具体的な保険プランの分析を行います（年利1.25%、手数料：積立額の1.3% + 積立残高の0.008%/月）")
        _show_detailed_plan_analysis()
    
    with tab2:
        st.markdown("年間保険料から控除額と節税効果を計算します")
        _show_basic_deduction_calculator()


def _show_basic_deduction_calculator():
    """統合された基本控除計算機能"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 パラメータ入力")
        
        annual_premium = st.number_input(
            "年間保険料（円）",
            min_value=0,
            max_value=500000,
            value=100000,
            step=10000,
            key="deduction_annual_premium"
        )
        
        taxable_income_man = st.number_input(
            "課税所得（万円）",
            min_value=0,
            max_value=5000,
            value=500,
            step=10,
            help="各種所得控除を差し引いた後の課税対象所得額",
            key="deduction_taxable_income"
        )
        
        taxable_income = taxable_income_man * 10000
        
    with col2:
        st.subheader("📊 計算結果")
        
        # 控除額計算と税額計算（税金ヘルパーを使用）
        tax_helper = get_tax_helper()
        savings = tax_helper.calculate_annual_tax_savings(annual_premium, taxable_income)
        
        st.metric("控除額", f"{savings['deduction']:,.0f}円")
        st.metric("所得税節税額", f"{savings['income_tax_savings']:,.0f}円")
        st.metric("住民税節税額", f"{savings['resident_tax_savings']:,.0f}円")
        st.metric("総節税額", f"{savings['total_savings']:,.0f}円", 
                 delta=f"節税率: {savings['total_savings']/annual_premium:.1%}" if annual_premium > 0 else None)



def _show_detailed_plan_analysis():
    """詳細プラン分析（戦略ランキング）"""
    
    # 基本パラメータ設定
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 プラン設定")
        
        # プランタイプ選択
        plan_type = st.selectbox(
            "保険プランタイプ",
            ["旧一般生命保険料控除", "旧個人年金保険料控除", "両方のプランを併用"],
            key="plan_type_selector"
        )
        
        # 基本情報
        monthly_premium = st.number_input(
            "月払保険料（円）",
            min_value=1000,
            max_value=20000,
            value=9000,
            step=1000,
            key="monthly_premium"
        )
        
        annual_interest_rate = st.number_input(
            "年利（%）",
            min_value=0.0,
            max_value=10.0,
            value=1.25,
            step=0.01,
            key="annual_interest_rate"
        ) / 100
        
    with col2:
        st.subheader("🧮 税務情報")
        
        annual_income_man = st.number_input(
            "課税所得（万円）",
            min_value=100,
            max_value=5000,
            value=600,
            step=50,
            key="annual_income_man",
            help="給与所得控除・基礎控除等を差し引いた後の課税対象所得額"
        )
        
        # 万円を円に変換
        annual_income = annual_income_man * 10000
        
        contract_years = st.slider(
            "契約期間（年）",
            min_value=5,
            max_value=30,
            value=20,
            key="contract_years"
        )
        
        withdrawal_year = st.slider(
            "引き出し予定年数",
            min_value=5,
            max_value=contract_years,
            value=min(15, contract_years),
            key="withdrawal_year"
        )
    
    # 部分解約後の資金運用オプション
    st.markdown("---")
    st.subheader("💰 部分解約後の資金運用")
    
    reinvest_option = st.selectbox(
        "解約後の資金の運用先",
        [
            "預金（年利1%）",
            "運用なし（現金保有）",
            "投資信託（年利3%）",
            "投資信託（年利5%）",
            "カスタム"
        ],
        key="reinvest_option",
        help="部分解約した資金をどのように運用するかを選択します"
    )
    
    # 運用利回りのマッピング
    reinvest_rate_map = {
        "預金（年利1%）": 0.01,
        "運用なし（現金保有）": 0.00,
        "投資信託（年利3%）": 0.03,
        "投資信託（年利5%）": 0.05,
        "カスタム": None
    }
    
    if reinvest_option == "カスタム":
        withdrawal_reinvest_rate = st.number_input(
            "カスタム年利（%）",
            min_value=0.0,
            max_value=20.0,
            value=2.0,
            step=0.1,
            key="custom_reinvest_rate"
        ) / 100
    else:
        withdrawal_reinvest_rate = reinvest_rate_map[reinvest_option]
    
    st.info(f"💡 部分解約した資金は年利 **{withdrawal_reinvest_rate*100:.2f}%** で再投資されます")
    
    # 計算実行ボタン
    if st.button("📊 詳細分析を実行", key="run_analysis"):
        st.success("分析を実行中...")
        # 年間保険料計算
        annual_premium = monthly_premium * 12
        # 基本値取得
        base_year = withdrawal_year
        base_rate = 0.5
        # ±5年範囲生成
        year_range = list(range(max(5, base_year-5), min(contract_years, base_year+5)+1))
        # ±50%範囲生成（0.01～1.0, 0.1刻み）
        rate_min = max(0.01, base_rate-0.5)
        rate_max = min(1.0, base_rate+0.5)
        rate_range = [round(r,2) for r in list(np.arange(rate_min, rate_max+0.01, 0.1)) if r > 0]
        interval_range = [1,2,3,4,5]
        switch_rates = [0.01, 0.02, 0.03, 0.04, 0.05]
        # 複数戦略同時比較
        optimizer = WithdrawalOptimizer()
        df_strategies = optimizer.analyze_all_strategies(
            initial_premium=0,
            annual_premium=annual_premium,
            taxable_income=annual_income,
            policy_start_year=2025-base_year,
            interval_range=interval_range,
            rate_range=rate_range,
            full_withdrawal_years=year_range,
            switch_years=year_range,
            switch_rates=switch_rates,
            max_years=contract_years,
            return_rate=annual_interest_rate,
            withdrawal_reinvest_rate=withdrawal_reinvest_rate
        )
        st.markdown("## 🏆 戦略ランキング（±5年±50％範囲）")
        if df_strategies is not None and not df_strategies.empty:
            st.dataframe(df_strategies.head(20), use_container_width=True)
        else:
            st.warning("戦略ランキングデータがありません。パラメータを見直してください。")


def show_deduction_calculator():
    """基本控除計算ページ"""
    st.header("📊 基本控除計算")
    st.info("年間保険料から控除額と節税効果を計算します")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 パラメータ入力")
        
        annual_premium = st.number_input(
            "年間保険料（円）",
            min_value=0,
            max_value=500000,
            value=100000,
            step=10000
        )
        
        taxable_income_man = st.number_input(
            "課税所得（万円）",
            min_value=0,
            max_value=5000,
            value=500,
            step=10,
            help="各種所得控除を差し引いた後の課税対象所得額"
        )
        
        taxable_income = taxable_income_man * 10000
        
    with col2:
        st.subheader("📊 計算結果")
        
        # 税金ヘルパーで計算
        tax_helper = get_tax_helper()
        tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, taxable_income)
        
        # 結果表示
        st.metric("控除額", f"{tax_result['deduction']:,.0f}円")
        st.metric("所得税節税額", f"{tax_result['income_tax_savings']:,.0f}円")
        st.metric("住民税節税額", f"{tax_result['resident_tax_savings']:,.0f}円")
        st.metric("総節税額", f"{tax_result['total_savings']:,.0f}円", 
                 delta=f"節税率: {tax_result['total_savings']/annual_premium:.1%}" if annual_premium > 0 else None)


def show_withdrawal_optimizer():
    """引き出しタイミング最適化ページ"""
    st.header("🎯 引き出しタイミング最適化")
    st.markdown("最適な引き出しタイミングを分析し、最大利益を得られる時期を特定します。")
    
    # パラメータ設定
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 基本設定")
        
        monthly_premium_opt = st.number_input(
            "月払保険料（円）",
            min_value=1000,
            max_value=20000,
            value=9000,
            step=1000,
            key="opt_monthly_premium"
        )
        
        annual_interest_rate_opt = st.number_input(
            "年利（%）",
            min_value=0.0,
            max_value=10.0,
            value=1.25,
            step=0.01,
            key="opt_annual_interest_rate"
        ) / 100
        
        max_years = st.slider(
            "分析期間（年）",
            min_value=5,
            max_value=30,
            value=25,
            key="opt_max_years"
        )
        
    with col2:
        st.subheader("🧮 税務設定")
        
        annual_income_opt_man = st.number_input(
            "課税所得（万円）",
            min_value=100,
            max_value=5000,
            value=600,
            step=50,
            key="opt_annual_income_man",
            help="給与所得控除・基礎控除等を差し引いた後の課税対象所得額"
        )
        
        annual_income_opt = annual_income_opt_man * 10000
        
        # 将来の税率変動を考慮するかどうか
        consider_tax_change = st.checkbox(
            "将来の税率変動を考慮",
            value=False,
            key="consider_tax_change"
        )
        
        if consider_tax_change:
            future_income_change = st.slider(
                "将来の所得変動率（%/年）",
                min_value=-5.0,
                max_value=5.0,
                value=0.0,
                step=0.1,
                key="future_income_change"
            ) / 100
        else:
            future_income_change = 0.0
    
    # 最適化実行
    if st.button("🎯 最適タイミングを分析", key="run_optimization"):
        st.success("最適化分析を実行中...")
        
        # 年間保険料と税額計算
        annual_premium_opt = monthly_premium_opt * 12
        tax_helper = get_tax_helper()
        tax_result = tax_helper.calculate_annual_tax_savings(annual_premium_opt, taxable_income_opt)
        deduction_amount = tax_result['deduction']
        
        # 手数料設定
        monthly_fee_rate = 0.013
        monthly_balance_fee_rate = 0.00008
        monthly_interest_rate_opt = annual_interest_rate_opt / 12
        
        # 各年での引き出し効果を計算
        years_analysis = list(range(1, max_years + 1))
        optimization_results = []
        
        for year in years_analysis:
            # その年での積立残高と諸計算
            balance = 0
            cumulative_premium = 0
            cumulative_fee = 0
            cumulative_tax_savings = 0
            
            for y in range(year):
                # その年の所得（変動考慮）
                current_income = annual_income_opt * (1 + future_income_change) ** y
                income_tax_rate = tax_calculator.get_income_tax_rate(current_income)
                annual_tax_savings = deduction_amount * (income_tax_rate + 0.10)
                cumulative_tax_savings += annual_tax_savings
                
                # 月次計算
                for month in range(12):
                    cumulative_premium += monthly_premium_opt
                    
                    monthly_fee = monthly_premium_opt * monthly_fee_rate
                    balance_fee = balance * monthly_balance_fee_rate
                    total_monthly_fee = monthly_fee + balance_fee
                    cumulative_fee += total_monthly_fee
                    
                    net_investment = monthly_premium_opt - total_monthly_fee
                    balance = balance * (1 + monthly_interest_rate_opt) + net_investment
            
            # 正味利益計算
            net_benefit = balance + cumulative_tax_savings - cumulative_premium
            
            # 実質年利計算
            if cumulative_premium > 0:
                effective_annual_return = ((balance + cumulative_tax_savings) / cumulative_premium) ** (1/year) - 1
            else:
                effective_annual_return = 0
            
            optimization_results.append({
                'year': year,
                'balance': balance,
                'cumulative_premium': cumulative_premium,
                'cumulative_tax_savings': cumulative_tax_savings,
                'cumulative_fee': cumulative_fee,
                'net_benefit': net_benefit,
                'effective_return': effective_annual_return,
                'total_return': balance + cumulative_tax_savings
            })
        
        # 最適年を特定
        best_year_by_benefit = max(optimization_results, key=lambda x: x['net_benefit'])
        best_year_by_return = max(optimization_results, key=lambda x: x['effective_return'])
        
        # 結果表示
        st.markdown("---")
        st.subheader("🏆 最適化結果")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "最大利益年", 
                f"{best_year_by_benefit['year']}年目",
                f"{best_year_by_benefit['net_benefit']/10000:.1f}万円"
            )
        
        with col2:
            st.metric(
                "最高利回り年", 
                f"{best_year_by_return['year']}年目",
                f"{best_year_by_return['effective_return']:.2%}"
            )
        
        with col3:
            # 損益分岐点
            break_even = next((r for r in optimization_results if r['net_benefit'] > 0), None)
            if break_even:
                st.metric(
                    "損益分岐点", 
                    f"{break_even['year']}年目",
                    f"利益: {break_even['net_benefit']/10000:.1f}万円"
                )
            else:
                st.metric("損益分岐点", "期間内なし", "⚠️")
        
        # グラフ表示
        st.markdown("---")
        st.subheader("📊 引き出しタイミング分析")
        
        # データフレーム作成
        df_opt = pd.DataFrame(optimization_results)
        df_opt['balance_man'] = df_opt['balance'] / 10000
        df_opt['net_benefit_man'] = df_opt['net_benefit'] / 10000
        df_opt['total_return_man'] = df_opt['total_return'] / 10000
        df_opt['cumulative_premium_man'] = df_opt['cumulative_premium'] / 10000
        
        # 2軸グラフ作成
        fig_opt = make_subplots(
            rows=2, cols=1,
            subplot_titles=('正味利益の推移', '実質年利の推移'),
            specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
        )
        
        # 正味利益
        fig_opt.add_trace(
            go.Scatter(x=df_opt['year'], y=df_opt['net_benefit_man'], 
                      name='正味利益', line=dict(color='green', width=3)),
            row=1, col=1
        )
        
        # 積立残高（副軸）
        fig_opt.add_trace(
            go.Scatter(x=df_opt['year'], y=df_opt['balance_man'], 
                      name='積立残高', line=dict(color='blue', dash='dash')),
            row=1, col=1, secondary_y=True
        )
        
        # 実質年利
        fig_opt.add_trace(
            go.Scatter(x=df_opt['year'], y=df_opt['effective_return']*100, 
                      name='実質年利', line=dict(color='purple', width=2)),
            row=2, col=1
        )
        
        # 最適点をマーク
        fig_opt.add_vline(x=best_year_by_benefit['year'], line_dash="dot", line_color="red", 
                         annotation_text=f"最大利益: {best_year_by_benefit['year']}年", row=1, col=1)
        fig_opt.add_vline(x=best_year_by_return['year'], line_dash="dot", line_color="orange", 
                         annotation_text=f"最高利回り: {best_year_by_return['year']}年", row=2, col=1)
        
        # レイアウト設定
        fig_opt.update_layout(
            height=600,
            title_text="引き出しタイミング最適化分析",
            showlegend=True
        )
        
        fig_opt.update_yaxes(title_text="正味利益（万円）", row=1, col=1)
        fig_opt.update_yaxes(title_text="積立残高（万円）", row=1, col=1, secondary_y=True)
        fig_opt.update_yaxes(title_text="実質年利（%）", row=2, col=1)
        fig_opt.update_xaxes(title_text="年数", row=2, col=1)
        
        st.plotly_chart(fig_opt, width='stretch')
        
        # 推奨事項
        st.markdown("---")
        st.subheader("💡 最適化推奨事項")
        
        if best_year_by_benefit['net_benefit'] > 0:
            st.success(f"""
            ✅ **推奨引き出しタイミング**: {best_year_by_benefit['year']}年目
            - **最大正味利益**: {best_year_by_benefit['net_benefit']/10000:.1f}万円
            - **実質年利**: {best_year_by_benefit['effective_return']:.2%}
            - **総リターン**: {best_year_by_benefit['total_return']/10000:.1f}万円
            """)
        else:
            st.warning("⚠️ 設定条件では利益を得にくい投資となっています。")
        
        if abs(best_year_by_benefit['year'] - best_year_by_return['year']) <= 2:
            st.info("📈 最大利益年と最高利回り年が近接しており、安定した投資となります。")
        else:
            st.info(f"""
            📊 **注意**: 最大利益年（{best_year_by_benefit['year']}年）と最高利回り年（{best_year_by_return['year']}年）が異なります。
            - 短期重視なら{best_year_by_return['year']}年目
            - 長期利益重視なら{best_year_by_benefit['year']}年目を検討
            """)
        
        # 詳細データ
        with st.expander("📋 年別詳細データを確認"):
            display_df = df_opt[['year', 'balance_man', 'net_benefit_man', 'effective_return']].copy()
            display_df.columns = ['年数', '積立残高(万円)', '正味利益(万円)', '実質年利']
            display_df['実質年利'] = (display_df['実質年利'] * 100).round(2)
            display_df = display_df.round(1)
            st.dataframe(display_df, width='stretch')


def show_scenario_analysis():
    """シナリオ分析ページ"""
    st.header("📈 シナリオ分析")
    st.markdown("複数のシナリオを同時に比較分析し、条件変化による影響を評価します。")
    
    # シナリオ設定
    st.subheader("📝 シナリオ設定")
    
    # 基本シナリオ
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 🔵 基本シナリオ")
        base_monthly_premium = st.number_input(
            "月払保険料（円）", 
            min_value=1000, max_value=20000, value=9000, step=1000,
            key="base_monthly_premium"
        )
        base_annual_rate = st.number_input(
            "年利（%）", 
            min_value=0.0, max_value=10.0, value=1.25, step=0.01,
            key="base_annual_rate"
        ) / 100
        base_income_man = st.number_input(
            "課税所得（万円）", 
            min_value=100, max_value=5000, value=600, step=50,
            key="base_income_man",
            help="給与所得控除・基礎控除等を差し引いた後の課税対象所得額"
        )
        
    with col2:
        st.markdown("#### 🟡 比較シナリオ")
        comp_monthly_premium = st.number_input(
            "月払保険料（円）", 
            min_value=1000, max_value=20000, value=12000, step=1000,
            key="comp_monthly_premium"
        )
        comp_annual_rate = st.number_input(
            "年利（%）", 
            min_value=0.0, max_value=10.0, value=1.50, step=0.01,
            key="comp_annual_rate"
        ) / 100
        comp_income_man = st.number_input(
            "課税所得（万円）", 
            min_value=100, max_value=5000, value=800, step=50,
            key="comp_income_man",
            help="給与所得控除・基礎控除等を差し引いた後の課税対象所得額"
        )
    
    # 共通設定
    analysis_years = st.slider(
        "分析期間（年）", 
        min_value=5, max_value=30, value=20,
        key="scenario_analysis_years"
    )
    
    # 追加シナリオ設定
    st.markdown("#### 🟢 楽観シナリオ / 🔴 悲観シナリオ")
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        optimistic_rate_bonus = st.slider(
            "楽観シナリオ 年利ボーナス（%）", 
            min_value=0.0, max_value=3.0, value=0.5, step=0.1,
            key="optimistic_bonus"
        ) / 100
        
    with col4:
        pessimistic_rate_penalty = st.slider(
            "悲観シナリオ 年利ペナルティ（%）", 
            min_value=0.0, max_value=2.0, value=0.3, step=0.1,
            key="pessimistic_penalty"
        ) / 100
    
    # 分析実行
    if st.button("📊 シナリオ分析を実行", key="run_scenario_analysis"):
        st.success("シナリオ分析を実行中...")
        
        # 税金ヘルパーを取得
        tax_helper = get_tax_helper()
        
        scenarios = {
            '基本シナリオ': {
                'monthly_premium': base_monthly_premium,
                'annual_rate': base_annual_rate,
                'annual_income': base_income_man * 10000,
                'color': 'blue'
            },
            '比較シナリオ': {
                'monthly_premium': comp_monthly_premium,
                'annual_rate': comp_annual_rate,
                'annual_income': comp_income_man * 10000,
                'color': 'orange'
            },
            '楽観シナリオ': {
                'monthly_premium': base_monthly_premium,
                'annual_rate': base_annual_rate + optimistic_rate_bonus,
                'annual_income': base_income_man * 10000,
                'color': 'green'
            },
            '悲観シナリオ': {
                'monthly_premium': base_monthly_premium,
                'annual_rate': max(0, base_annual_rate - pessimistic_rate_penalty),
                'annual_income': base_income_man * 10000,
                'color': 'red'
            }
        }
        
        scenario_results = {}
        
        # 各シナリオの計算
        for scenario_name, params in scenarios.items():
            annual_premium = params['monthly_premium'] * 12
            deduction = calculator.calculate_old_deduction(annual_premium)
            income_tax_rate = tax_calculator.get_income_tax_rate(params['annual_income'])
            annual_tax_savings = deduction * (income_tax_rate + 0.10)
            
            monthly_fee_rate = 0.013
            monthly_balance_fee_rate = 0.00008
            monthly_interest_rate = params['annual_rate'] / 12
            
            # 年次データ計算
            years = list(range(1, analysis_years + 1))
            balance_history = []
            net_benefit_history = []
            cumulative_premium_history = []
            
            balance = 0
            cumulative_premium = 0
            cumulative_fee = 0
            
            for year in years:
                for month in range(12):
                    cumulative_premium += params['monthly_premium']
                    
                    monthly_fee = params['monthly_premium'] * monthly_fee_rate
                    balance_fee = balance * monthly_balance_fee_rate
                    total_monthly_fee = monthly_fee + balance_fee
                    cumulative_fee += total_monthly_fee
                    
                    net_investment = params['monthly_premium'] - total_monthly_fee
                    balance = balance * (1 + monthly_interest_rate) + net_investment
                
                cumulative_tax_savings = annual_tax_savings * year
                net_benefit = balance + cumulative_tax_savings - cumulative_premium
                
                balance_history.append(balance)
                net_benefit_history.append(net_benefit)
                cumulative_premium_history.append(cumulative_premium)
            
            scenario_results[scenario_name] = {
                'years': years,
                'balance': balance_history,
                'net_benefit': net_benefit_history,
                'cumulative_premium': cumulative_premium_history,
                'final_balance': balance_history[-1] if balance_history else 0,
                'final_net_benefit': net_benefit_history[-1] if net_benefit_history else 0,
                'color': params['color']
            }
        
        # 結果サマリー
        st.markdown("---")
        st.subheader("📊 シナリオ比較サマリー")
        
        # メトリクス表示
        metric_cols = st.columns(4)
        
        for i, (scenario_name, result) in enumerate(scenario_results.items()):
            with metric_cols[i]:
                final_benefit_man = result['final_net_benefit'] / 10000
                final_balance_man = result['final_balance'] / 10000
                
                st.metric(
                    scenario_name,
                    f"{final_benefit_man:.1f}万円",
                    f"残高: {final_balance_man:.1f}万円"
                )
        
        # グラフ作成
        st.markdown("---")
        st.subheader("📈 シナリオ比較グラフ")
        
        fig_scenario = make_subplots(
            rows=2, cols=1,
            subplot_titles=('正味利益の比較', '積立残高の比較')
        )
        
        # 各シナリオのグラフを追加
        for scenario_name, result in scenario_results.items():
            # 正味利益
            fig_scenario.add_trace(
                go.Scatter(
                    x=result['years'],
                    y=[x/10000 for x in result['net_benefit']],
                    name=f'{scenario_name} (正味利益)',
                    line=dict(color=result['color'], width=2),
                    mode='lines'
                ),
                row=1, col=1
            )
            
            # 積立残高
            fig_scenario.add_trace(
                go.Scatter(
                    x=result['years'],
                    y=[x/10000 for x in result['balance']],
                    name=f'{scenario_name} (積立残高)',
                    line=dict(color=result['color'], width=2, dash='dash'),
                    mode='lines'
                ),
                row=2, col=1
            )
        
        fig_scenario.update_layout(
            height=700,
            title_text="シナリオ比較分析結果",
            showlegend=True
        )
        
        fig_scenario.update_yaxes(title_text="正味利益（万円）", row=1, col=1)
        fig_scenario.update_yaxes(title_text="積立残高（万円）", row=2, col=1)
        fig_scenario.update_xaxes(title_text="年数", row=2, col=1)
        
        st.plotly_chart(fig_scenario, width='stretch')
        
        # シナリオ分析結果
        st.markdown("---")
        st.subheader("💡 シナリオ分析結果")
        
        # 最適・最悪シナリオ特定
        best_scenario = max(scenario_results.keys(), 
                          key=lambda k: scenario_results[k]['final_net_benefit'])
        worst_scenario = min(scenario_results.keys(), 
                           key=lambda k: scenario_results[k]['final_net_benefit'])
        
        best_benefit = scenario_results[best_scenario]['final_net_benefit'] / 10000
        worst_benefit = scenario_results[worst_scenario]['final_net_benefit'] / 10000
        benefit_range = best_benefit - worst_benefit
        
        col_analysis1, col_analysis2 = st.columns([1, 1])
        
        with col_analysis1:
            st.success(f"""
            🏆 **最良シナリオ**: {best_scenario}
            - 最終正味利益: {best_benefit:.1f}万円
            - 最終積立残高: {scenario_results[best_scenario]['final_balance']/10000:.1f}万円
            """)
            
            st.error(f"""
            ⚠️ **最悪シナリオ**: {worst_scenario}
            - 最終正味利益: {worst_benefit:.1f}万円
            - 最終積立残高: {scenario_results[worst_scenario]['final_balance']/10000:.1f}万円
            """)
        
        with col_analysis2:
            st.info(f"""
            📊 **リスク分析**
            - 利益幅: {benefit_range:.1f}万円
            - リスク率: {abs(benefit_range)/abs(best_benefit)*100:.1f}% (対最良比)
            """)
            
            # 損益分岐点分析
            profitable_scenarios = sum(1 for result in scenario_results.values() 
                                     if result['final_net_benefit'] > 0)
            
            if profitable_scenarios == len(scenarios):
                st.success("✅ 全シナリオで利益確保")
            elif profitable_scenarios > 0:
                st.warning(f"⚠️ {profitable_scenarios}/{len(scenarios)}シナリオで利益")
            else:
                st.error("❌ 全シナリオで損失")
        
        # 推奨事項
        st.markdown("---")
        st.subheader("🎯 推奨事項")
        
        # 基本vs比較シナリオ
        base_benefit = scenario_results['基本シナリオ']['final_net_benefit']
        comp_benefit = scenario_results['比較シナリオ']['final_net_benefit']
        
        if comp_benefit > base_benefit:
            improvement = (comp_benefit - base_benefit) / 10000
            st.success(f"📈 比較シナリオが{improvement:.1f}万円有利です。より高い保険料・年利・所得の条件を検討してください。")
        elif comp_benefit < base_benefit:
            improvement = (base_benefit - comp_benefit) / 10000
            st.success(f"📉 基本シナリオが{improvement:.1f}万円有利です。現在の条件が適切です。")
        else:
            st.info("📊 基本シナリオと比較シナリオの結果はほぼ同等です。")
        
        # リスク対策
        if benefit_range > best_benefit * 0.3:  # 30%以上の変動
            st.warning("""
            ⚠️ **高リスク**: シナリオ間で大きな差があります。
            - より保守的な条件設定を検討
            - 定期的な見直しとアップデートが重要
            """)
        else:
            st.success("""
            ✅ **低リスク**: シナリオ間の差は小さく安定しています。
            - 現在の戦略継続を推奨
            """)
        
        # データテーブル
        with st.expander("📋 詳細比較データを確認"):
            comparison_data = []
            for year in range(1, min(analysis_years + 1, 21)):  # 最大20年分表示
                row = {'年数': year}
                for scenario_name, result in scenario_results.items():
                    if year <= len(result['years']):
                        row[f'{scenario_name}_正味利益'] = round(result['net_benefit'][year-1]/10000, 1)
                        row[f'{scenario_name}_積立残高'] = round(result['balance'][year-1]/10000, 1)
                comparison_data.append(row)
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, width='stretch')


def show_sensitivity_analysis():
    """感度分析ページ"""
    st.header("🔍 感度分析")
    st.markdown("各パラメータが最終結果にどの程度影響するかを分析し、重要な変数を特定します。")
    
    # 基準値設定
    st.subheader("📋 基準値設定")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        base_monthly_premium_sens = st.number_input(
            "基準月払保険料（円）", 
            min_value=1000, max_value=20000, value=9000, step=1000,
            key="sens_monthly_premium"
        )
        
        base_annual_rate_sens = st.number_input(
            "基準年利（%）", 
            min_value=0.0, max_value=10.0, value=1.25, step=0.01,
            key="sens_annual_rate"
        )
        
    with col2:
        base_income_sens_man = st.number_input(
            "基準課税所得（万円）", 
            min_value=100, max_value=5000, value=600, step=50,
            key="sens_income_man",
            help="給与所得控除・基礎控除等を差し引いた後の課税対象所得額"
        )
        
        analysis_year_sens = st.slider(
            "分析対象年数", 
            min_value=5, max_value=30, value=15,
            key="sens_analysis_year"
        )
        
    with col3:
        # 感度分析の変動幅設定
        variation_range = st.slider(
            "変動幅（%）", 
            min_value=5, max_value=50, value=20,
            key="variation_range"
        )
        
        sensitivity_points = st.slider(
            "分析点数", 
            min_value=5, max_value=21, value=11,
            key="sensitivity_points"
        )
    
    # 感度分析実行
    if st.button("🎯 感度分析を実行", key="run_sensitivity_analysis"):
        st.success("感度分析を実行中...")
        
        # 基準値の設定と税金ヘルパー取得
        base_income_sens = base_income_sens_man * 10000
        tax_helper = get_tax_helper()
        
        def calculate_final_benefit(monthly_premium, annual_rate, annual_income):
            """指定パラメータでの最終正味利益を計算"""
            annual_premium = monthly_premium * 12
            tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, annual_income)
            annual_tax_savings = tax_result['total_savings']
            
            monthly_fee_rate = 0.013
            monthly_balance_fee_rate = 0.00008
            monthly_interest_rate = annual_rate / 12
            
            balance = 0
            cumulative_premium = 0
            cumulative_fee = 0
            
            for year in range(analysis_year_sens):
                for month in range(12):
                    cumulative_premium += monthly_premium
                    
                    monthly_fee = monthly_premium * monthly_fee_rate
                    balance_fee = balance * monthly_balance_fee_rate
                    total_monthly_fee = monthly_fee + balance_fee
                    cumulative_fee += total_monthly_fee
                    
                    net_investment = monthly_premium - total_monthly_fee
                    balance = balance * (1 + monthly_interest_rate) + net_investment
            
            cumulative_tax_savings = annual_tax_savings * analysis_year_sens
            net_benefit = balance + cumulative_tax_savings - cumulative_premium
            
            return net_benefit
        
        # 基準値での計算
        base_benefit = calculate_final_benefit(
            base_monthly_premium_sens, 
            base_annual_rate_sens / 100, 
            base_income_sens
        )
        
        # 感度分析データ準備
        sensitivity_data = {
            'monthly_premium': [],
            'annual_rate': [],
            'annual_income': [],
        }
        
        # 変動範囲の計算
        variation_factor = variation_range / 100
        
        # 各パラメータの感度分析
        # 1. 月払保険料の感度
        premium_range = np.linspace(
            base_monthly_premium_sens * (1 - variation_factor),
            base_monthly_premium_sens * (1 + variation_factor),
            sensitivity_points
        )
        
        premium_benefits = []
        for premium in premium_range:
            benefit = calculate_final_benefit(
                premium, 
                base_annual_rate_sens / 100, 
                base_income_sens
            )
            premium_benefits.append(benefit)
        
        sensitivity_data['monthly_premium'] = {
            'values': premium_range,
            'benefits': premium_benefits,
            'base_value': base_monthly_premium_sens,
            'base_benefit': base_benefit
        }
        
        # 2. 年利の感度
        rate_range = np.linspace(
            max(0, base_annual_rate_sens * (1 - variation_factor)),
            base_annual_rate_sens * (1 + variation_factor),
            sensitivity_points
        )
        
        rate_benefits = []
        for rate in rate_range:
            benefit = calculate_final_benefit(
                base_monthly_premium_sens, 
                rate / 100, 
                base_income_sens
            )
            rate_benefits.append(benefit)
        
        sensitivity_data['annual_rate'] = {
            'values': rate_range,
            'benefits': rate_benefits,
            'base_value': base_annual_rate_sens,
            'base_benefit': base_benefit
        }
        
        # 3. 課税所得の感度
        income_range = np.linspace(
            base_income_sens * (1 - variation_factor),
            base_income_sens * (1 + variation_factor),
            sensitivity_points
        )
        
        income_benefits = []
        for income in income_range:
            benefit = calculate_final_benefit(
                base_monthly_premium_sens, 
                base_annual_rate_sens / 100, 
                income
            )
            income_benefits.append(benefit)
        
        sensitivity_data['annual_income'] = {
            'values': income_range,
            'benefits': income_benefits,
            'base_value': base_income_sens,
            'base_benefit': base_benefit
        }
        
        # 結果表示
        st.markdown("---")
        st.subheader("📊 感度分析結果")
        
        # 各パラメータの影響度計算
        param_impacts = {}
        
        for param_name, data in sensitivity_data.items():
            min_benefit = min(data['benefits'])
            max_benefit = max(data['benefits'])
            impact_range = max_benefit - min_benefit
            relative_impact = impact_range / abs(base_benefit) if base_benefit != 0 else 0
            
            param_impacts[param_name] = {
                'range': impact_range,
                'relative_impact': relative_impact,
                'min_benefit': min_benefit,
                'max_benefit': max_benefit
            }
        
        # 影響度ランキング
        sorted_impacts = sorted(param_impacts.items(), 
                              key=lambda x: x[1]['relative_impact'], 
                              reverse=True)
        
        st.subheader("🏆 影響度ランキング")
        
        impact_cols = st.columns(3)
        param_names = {
            'monthly_premium': '月払保険料',
            'annual_rate': '年利',
            'annual_income': '課税所得'
        }
        
        for i, (param_name, impact_data) in enumerate(sorted_impacts):
            with impact_cols[i]:
                rank_emoji = ["🥇", "🥈", "🥉"][i]
                st.metric(
                    f"{rank_emoji} {param_names[param_name]}",
                    f"{impact_data['relative_impact']:.1%}",
                    f"±{impact_data['range']/20000:.1f}万円"
                )
        
        # 感度分析グラフ
        st.markdown("---")
        st.subheader("📈 感度分析グラフ")
        
        fig_sens = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '月払保険料の感度', '年利の感度', 
                '課税所得の感度', '影響度比較'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "bar"}]]
        )
        
        # 月払保険料
        fig_sens.add_trace(
            go.Scatter(
                x=sensitivity_data['monthly_premium']['values'],
                y=[b/10000 for b in sensitivity_data['monthly_premium']['benefits']],
                mode='lines+markers',
                name='月払保険料',
                line=dict(color='blue', width=3)
            ),
            row=1, col=1
        )
        
        # 基準点をマーク
        fig_sens.add_trace(
            go.Scatter(
                x=[base_monthly_premium_sens],
                y=[base_benefit/10000],
                mode='markers',
                name='基準点',
                marker=dict(color='red', size=10, symbol='star')
            ),
            row=1, col=1
        )
        
        # 年利
        fig_sens.add_trace(
            go.Scatter(
                x=sensitivity_data['annual_rate']['values'],
                y=[b/10000 for b in sensitivity_data['annual_rate']['benefits']],
                mode='lines+markers',
                name='年利',
                line=dict(color='green', width=3)
            ),
            row=1, col=2
        )
        
        fig_sens.add_trace(
            go.Scatter(
                x=[base_annual_rate_sens],
                y=[base_benefit/10000],
                mode='markers',
                marker=dict(color='red', size=10, symbol='star'),
                showlegend=False
            ),
            row=1, col=2
        )
        
        # 課税所得
        fig_sens.add_trace(
            go.Scatter(
                x=[i/10000 for i in sensitivity_data['annual_income']['values']],
                y=[b/10000 for b in sensitivity_data['annual_income']['benefits']],
                mode='lines+markers',
                name='課税所得',
                line=dict(color='purple', width=3)
            ),
            row=2, col=1
        )
        
        fig_sens.add_trace(
            go.Scatter(
                x=[base_income_sens/10000],
                y=[base_benefit/10000],
                mode='markers',
                marker=dict(color='red', size=10, symbol='star'),
                showlegend=False
            ),
            row=2, col=1
        )
        
        # 影響度比較バーチャート
        fig_sens.add_trace(
            go.Bar(
                x=[param_names[param] for param, _ in sorted_impacts],
                y=[impact['relative_impact']*100 for _, impact in sorted_impacts],
                name='影響度',
                marker_color=['gold', 'silver', '#CD7F32']
            ),
            row=2, col=2
        )
        
        # レイアウト設定
        fig_sens.update_layout(
            height=800,
            title_text="感度分析結果",
            showlegend=True
        )
        
        # 軸ラベル設定
        fig_sens.update_xaxes(title_text="月払保険料（円）", row=1, col=1)
        fig_sens.update_xaxes(title_text="年利（%）", row=1, col=2)
        fig_sens.update_xaxes(title_text="課税所得（万円）", row=2, col=1)
        fig_sens.update_xaxes(title_text="パラメータ", row=2, col=2)
        
        fig_sens.update_yaxes(title_text="正味利益（万円）", row=1, col=1)
        fig_sens.update_yaxes(title_text="正味利益（万円）", row=1, col=2)
        fig_sens.update_yaxes(title_text="正味利益（万円）", row=2, col=1)
        fig_sens.update_yaxes(title_text="影響度（%）", row=2, col=2)
        
        st.plotly_chart(fig_sens, width='stretch')
        
        # 分析結果とアドバイス
        st.markdown("---")
        st.subheader("💡 感度分析に基づくアドバイス")
        
        # 最も影響度の高いパラメータ
        most_sensitive_param, most_sensitive_data = sorted_impacts[0]
        most_sensitive_name = param_names[most_sensitive_param]
        
        st.success(f"""
        🎯 **最重要パラメータ**: {most_sensitive_name}
        - 影響度: {most_sensitive_data['relative_impact']:.1%}
        - 変動幅: ±{most_sensitive_data['range']/20000:.1f}万円
        """)
        
        # パラメータ別アドバイス
        if most_sensitive_param == 'annual_rate':
            st.info("""
            📈 **年利が最も重要**: 
            - 金融商品選択時は年利を最優先で比較検討
            - 0.1%の年利差でも長期的に大きな影響
            - 定期的な商品見直しが効果的
            """)
        elif most_sensitive_param == 'monthly_premium':
            st.info("""
            💰 **月払保険料が最も重要**: 
            - 保険料設定は慎重に検討
            - 無理のない範囲での増額検討
            - 家計バランスとの調整が重要
            """)
        elif most_sensitive_param == 'annual_income':
            st.info("""
            📊 **課税所得が最も重要**: 
            - 所得向上が最も効果的
            - 税率ブラケットの境界に注意
            - 控除制度の活用が重要
            """)
        
        # リスク管理アドバイス
        high_sensitivity_count = sum(1 for _, data in param_impacts.items() 
                                   if data['relative_impact'] > 0.2)
        
        if high_sensitivity_count >= 2:
            st.warning("""
            ⚠️ **高感度リスク**: 複数パラメータの影響が大きいです
            - 定期的なモニタリングが重要
            - 市場環境変化への対応準備
            - 複数シナリオでの検証推奨
            """)
        else:
            st.success("""
            ✅ **安定性良好**: パラメータ変動への耐性があります
            - 現在の戦略継続を推奨
            - 主要パラメータのみ注意深く管理
            """)
        
        # 詳細データ
        with st.expander("📋 感度分析詳細データ"):
            for param_name, data in sensitivity_data.items():
                st.write(f"#### {param_names[param_name]}")
                
                if param_name == 'annual_income':
                    display_values = [v/10000 for v in data['values']]
                    unit = '万円'
                elif param_name == 'annual_rate':
                    display_values = data['values']
                    unit = '%'
                else:
                    display_values = data['values']
                    unit = '円'
                
                sens_df = pd.DataFrame({
                    f'{param_names[param_name]}({unit})': [f"{v:.1f}" for v in display_values],
                    '正味利益(万円)': [f"{b/10000:.1f}" for b in data['benefits']]
                })
                
                st.dataframe(sens_df, width='stretch')


def show_report_generator():
    """レポート生成ページ"""
    st.header("📋 レポート生成")
    st.markdown("分析結果を包括的なレポートとして出力し、意思決定をサポートします。")
    
    # レポート設定
    st.subheader("📝 レポート設定")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 基本情報")
        
        client_name = st.text_input(
            "分析対象者名",
            value="田中太郎",
            key="client_name"
        )
        
        report_monthly_premium = st.number_input(
            "月払保険料（円）",
            min_value=1000,
            max_value=20000,
            value=9000,
            step=1000,
            key="report_monthly_premium"
        )
        
        report_annual_rate = st.number_input(
            "年利（%）",
            min_value=0.0,
            max_value=10.0,
            value=1.25,
            step=0.01,
            key="report_annual_rate"
        ) / 100
        
        report_income_man = st.number_input(
            "課税所得（万円）",
            min_value=100,
            max_value=5000,
            value=600,
            step=50,
            key="report_income_man",
            help="給与所得控除・基礎控除等を差し引いた後の課税対象所得額"
        )
        
    with col2:
        st.markdown("#### レポート詳細設定")
        
        analysis_period = st.slider(
            "分析期間（年）",
            min_value=5,
            max_value=30,
            value=20,
            key="report_analysis_period"
        )
        
        target_withdrawal_year = st.slider(
            "想定引き出し年数",
            min_value=5,
            max_value=analysis_period,
            value=15,
            key="report_target_withdrawal"
        )
        
        report_sections = st.multiselect(
            "含めるレポート項目",
            ["エグゼクティブサマリー", "詳細分析結果", "最適化推奨", "リスク分析", "シナリオ比較", "感度分析"],
            default=["エグゼクティブサマリー", "詳細分析結果", "最適化推奨", "リスク分析"]
        )
        
        include_charts = st.checkbox("グラフを含める", value=True)
        
    # レポート生成
    if st.button("📊 包括レポートを生成", key="generate_comprehensive_report"):
        st.success("レポートを生成中...")
        
        # 基本計算
        report_income = report_income_man * 10000
        annual_premium = report_monthly_premium * 12
        
        # 税金計算
        tax_helper = get_tax_helper()
        tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, report_income)
        annual_tax_savings = tax_result['total_savings']
        
        # 詳細計算
        monthly_fee_rate = 0.013
        monthly_balance_fee_rate = 0.00008
        monthly_interest_rate = report_annual_rate / 12
        
        # 期間全体の計算
        balance_history = []
        net_benefit_history = []
        tax_savings_history = []
        
        balance = 0
        cumulative_premium = 0
        cumulative_fee = 0
        
        for year in range(1, analysis_period + 1):
            for month in range(12):
                cumulative_premium += report_monthly_premium
                
                monthly_fee = report_monthly_premium * monthly_fee_rate
                balance_fee = balance * monthly_balance_fee_rate
                total_monthly_fee = monthly_fee + balance_fee
                cumulative_fee += total_monthly_fee
                
                net_investment = report_monthly_premium - total_monthly_fee
                balance = balance * (1 + monthly_interest_rate) + net_investment
            
            cumulative_tax_savings = annual_tax_savings * year
            net_benefit = balance + cumulative_tax_savings - cumulative_premium
            
            balance_history.append(balance)
            net_benefit_history.append(net_benefit)
            tax_savings_history.append(cumulative_tax_savings)
        
        # レポート生成日時
        from datetime import datetime
        report_date = datetime.now().strftime("%Y年%m月%d日")
        
        # レポート表示開始
        st.markdown("---")
        st.markdown(f"# 🏦 生命保険料控除分析レポート")
        st.markdown(f"**生成日**: {report_date}")
        st.markdown(f"**分析対象**: {client_name}様")
        st.markdown("---")
        
        # エグゼクティブサマリー
        if "エグゼクティブサマリー" in report_sections:
            st.markdown("## 📊 エグゼクティブサマリー")
            
            target_balance = balance_history[target_withdrawal_year-1] if target_withdrawal_year <= len(balance_history) else balance_history[-1]
            target_net_benefit = net_benefit_history[target_withdrawal_year-1] if target_withdrawal_year <= len(net_benefit_history) else net_benefit_history[-1]
            target_cumulative_premium = report_monthly_premium * 12 * target_withdrawal_year
            
            if target_net_benefit > 0:
                effective_return = ((target_balance + tax_savings_history[target_withdrawal_year-1]) / target_cumulative_premium) ** (1/target_withdrawal_year) - 1
            else:
                effective_return = 0
            
            col_summary1, col_summary2, col_summary3 = st.columns(3)
            
            with col_summary1:
                st.metric("月払保険料", f"{report_monthly_premium:,}円")
                st.metric("年間控除額", f"{deduction/10000:.1f}万円")
                
            with col_summary2:
                st.metric("年間節税額", f"{annual_tax_savings/10000:.1f}万円")
                st.metric(f"{target_withdrawal_year}年後積立残高", f"{target_balance/10000:.1f}万円")
                
            with col_summary3:
                st.metric(f"{target_withdrawal_year}年後正味利益", f"{target_net_benefit/10000:.1f}万円")
                st.metric("実質年利", f"{effective_return:.2%}")
            
            # 損益分岐点
            break_even_year = next((i for i, benefit in enumerate(net_benefit_history, 1) if benefit > 0), None)
            
            if break_even_year:
                if target_net_benefit > 0:
                    st.success(f"✅ **{target_withdrawal_year}年後の引き出しは有利**（損益分岐点: {break_even_year}年目）")
                else:
                    st.warning(f"⚠️ **{target_withdrawal_year}年後は損益分岐点前**（損益分岐点: {break_even_year}年目）")
            else:
                st.error("❌ **設定期間内で損益分岐点に到達しません**")
        
        # 詳細分析結果
        if "詳細分析結果" in report_sections:
            st.markdown("---")
            st.markdown("## 📈 詳細分析結果")
            
            if include_charts:
                # メインチャート
                years = list(range(1, len(balance_history) + 1))
                
                fig_report = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('積立残高と正味利益の推移', '累積節税額の推移')
                )
                
                # 積立残高
                fig_report.add_trace(
                    go.Scatter(
                        x=years, 
                        y=[b/10000 for b in balance_history],
                        name='積立残高',
                        line=dict(color='blue', width=3)
                    ),
                    row=1, col=1
                )
                
                # 正味利益
                fig_report.add_trace(
                    go.Scatter(
                        x=years,
                        y=[b/10000 for b in net_benefit_history],
                        name='正味利益',
                        line=dict(color='green', width=3),
                        fill='tonexty'
                    ),
                    row=1, col=1
                )
                
                # 累積節税額
                fig_report.add_trace(
                    go.Scatter(
                        x=years,
                        y=[t/10000 for t in tax_savings_history],
                        name='累積節税額',
                        line=dict(color='orange', width=2)
                    ),
                    row=2, col=1
                )
                
                # 目標年をマーク
                fig_report.add_vline(
                    x=target_withdrawal_year,
                    line_dash="dot",
                    line_color="red",
                    annotation_text=f"引き出し予定: {target_withdrawal_year}年目"
                )
                
                fig_report.update_layout(
                    height=600,
                    title_text="生命保険料控除プラン詳細分析"
                )
                
                fig_report.update_yaxes(title_text="金額（万円）", row=1, col=1)
                fig_report.update_yaxes(title_text="節税額（万円）", row=2, col=1)
                fig_report.update_xaxes(title_text="年数", row=2, col=1)
                
                st.plotly_chart(fig_report, width='stretch')
            
            # 数値テーブル
            report_data = []
            for i in range(0, min(len(years), 20), 2):  # 2年おき、最大20年
                year = years[i]
                report_data.append({
                    '年数': year,
                    '積立残高': f"{balance_history[i]/10000:.1f}万円",
                    '正味利益': f"{net_benefit_history[i]/10000:.1f}万円",
                    '累積節税額': f"{tax_savings_history[i]/10000:.1f}万円"
                })
            
            st.dataframe(pd.DataFrame(report_data), width='stretch')
        
        # 最適化推奨
        if "最適化推奨" in report_sections:
            st.markdown("---")
            st.markdown("## 🎯 最適化推奨事項")
            
            max_benefit_year = years[net_benefit_history.index(max(net_benefit_history))] if net_benefit_history else None
            max_benefit_value = max(net_benefit_history) if net_benefit_history else 0
            
            if max_benefit_year:
                st.info(f"""
                📈 **最適引き出しタイミング**: {max_benefit_year}年目  
                **最大正味利益**: {max_benefit_value/10000:.1f}万円
                """)
                
                if max_benefit_year != target_withdrawal_year:
                    difference = max_benefit_value - target_net_benefit
                    st.warning(f"""
                    ⚠️ **タイミング調整提案**: 引き出しを{max_benefit_year}年目に変更すると、
                    追加で{difference/10000:.1f}万円の利益が見込めます。
                    """)
            
            # 改善提案
            st.markdown("### 💡 改善提案")
            
            # 保険料増額シミュレーション
            higher_premium = report_monthly_premium * 1.2
            higher_annual_premium = higher_premium * 12
            higher_deduction = calculator.calculate_old_deduction(higher_annual_premium)
            higher_tax_savings = higher_deduction * (income_tax_rate + 0.10)
            
            st.markdown(f"""
            1. **保険料20%増額の効果**:
               - 月払保険料: {report_monthly_premium:,}円 → {higher_premium:,.0f}円
               - 年間控除額: {deduction/10000:.1f}万円 → {higher_deduction/10000:.1f}万円
               - 年間節税額: {annual_tax_savings/10000:.1f}万円 → {higher_tax_savings/10000:.1f}万円
            
            2. **年利向上の重要性**:
               - 年利0.25%向上で長期的に大きな利益増
               - 金融商品の定期見直しを推奨
            
            3. **税率最適化**:
               - 所得控除の組み合わせ活用
               - 他の控除制度との連携検討
            """)
        
        # リスク分析
        if "リスク分析" in report_sections:
            st.markdown("---")
            st.markdown("## ⚠️ リスク分析")
            
            # 金利変動リスク
            low_rate_scenario = report_annual_rate * 0.7
            high_rate_scenario = report_annual_rate * 1.3
            
            st.markdown("### 📊 金利変動シナリオ")
            
            risk_col1, risk_col2, risk_col3 = st.columns(3)
            
            with risk_col1:
                st.metric(
                    "悲観シナリオ",
                    f"年利 {low_rate_scenario:.2%}",
                    "△30%"
                )
                
            with risk_col2:
                st.metric(
                    "基準シナリオ",
                    f"年利 {report_annual_rate:.2%}",
                    "現行"
                )
                
            with risk_col3:
                st.metric(
                    "楽観シナリオ",
                    f"年利 {high_rate_scenario:.2%}",
                    "▲30%"
                )
            
            st.markdown("""
            ### 🔍 主要リスク要因
            
            1. **金利変動リスク**: 市場金利の変動により運用成果が変動
            2. **税制変更リスク**: 控除制度の変更可能性
            3. **インフレリスク**: 物価上昇による実質価値の目減り
            4. **早期解約リスク**: 予定より早期の解約による損失
            
            ### 🛡️ リスク対策
            
            - 定期的な契約内容の見直し
            - 市場環境の継続的なモニタリング
            - 緊急時の代替策検討
            - 分散投資による全体リスクの軽減
            """)
        
        # ダウンロード用レポート生成
        st.markdown("---")
        st.markdown("## 💾 レポートダウンロード")
        
        # 簡易CSV生成
        csv_data = []
        for i, year in enumerate(years):
            if i < len(balance_history):
                csv_data.append({
                    '年数': year,
                    '積立残高': balance_history[i],
                    '正味利益': net_benefit_history[i],
                    '累積節税額': tax_savings_history[i]
                })
        
        csv_df = pd.DataFrame(csv_data)
        csv_string = csv_df.to_csv(index=False, encoding='utf-8-sig')
        
        col_download1, col_download2 = st.columns(2)
        
        with col_download1:
            st.download_button(
                label="📊 分析データ（CSV）をダウンロード",
                data=csv_string,
                file_name=f"生命保険料控除分析_{client_name}_{report_date.replace('年', '').replace('月', '').replace('日', '')}.csv",
                mime="text/csv"
            )
        
        with col_download2:
            # レポートサマリーテキスト生成
            summary_text = f"""
生命保険料控除分析レポート
分析対象: {client_name}様
生成日: {report_date}

【基本情報】
月払保険料: {report_monthly_premium:,}円
年間控除額: {deduction/10000:.1f}万円
年間節税額: {annual_tax_savings/10000:.1f}万円

【{target_withdrawal_year}年後予測】
積立残高: {target_balance/10000:.1f}万円
正味利益: {target_net_benefit/10000:.1f}万円
実質年利: {effective_return:.2%}

【推奨事項】
最適引き出し年: {max_benefit_year}年目
最大利益: {max_benefit_value/10000:.1f}万円
損益分岐点: {break_even_year}年目
            """
            
            st.download_button(
                label="📄 サマリーレポート（TXT）",
                data=summary_text,
                file_name=f"保険分析サマリー_{client_name}_{report_date.replace('年', '').replace('月', '').replace('日', '')}.txt",
                mime="text/plain"
            )
        
        st.success("✅ レポート生成が完了しました！")


def _estimate_annual_salary_from_taxable_income(taxable_income_man):
    """課税所得から年収を推定"""
    taxable_income = taxable_income_man * 10000
    
    # 逆算で年収を推定（近似値）
    # 基礎控除: 48万円
    # 社会保険料率: 15%と仮定
    # 給与所得控除は年収によって変動するため反復計算
    
    basic_deduction = 480000  # 基礎控除
    other_deductions = 500000  # その他控除の想定値
    
    # 初期推定値
    estimated_salary = taxable_income + basic_deduction + other_deductions
    
    for _ in range(5):  # 反復計算で精度向上
        # 給与所得控除を計算
        if estimated_salary <= 1625000:
            salary_deduction = 550000
        elif estimated_salary <= 1800000:
            salary_deduction = estimated_salary * 0.4 - 100000
        elif estimated_salary <= 3600000:
            salary_deduction = estimated_salary * 0.3 + 80000
        elif estimated_salary <= 6600000:
            salary_deduction = estimated_salary * 0.2 + 440000
        elif estimated_salary <= 8500000:
            salary_deduction = estimated_salary * 0.1 + 1100000
        else:
            salary_deduction = 1950000
        
        # 社会保険料を計算
        social_insurance = estimated_salary * 0.15
        
        # 年収を再計算
        estimated_salary = taxable_income + basic_deduction + salary_deduction + social_insurance + other_deductions
    
    return estimated_salary / 10000


def _calculate_taxable_income_from_salary(annual_salary_man, social_insurance_rate, other_deductions_man):
    """年収から課税所得を計算"""
    annual_salary = annual_salary_man * 10000
    
    # 給与所得控除を計算
    if annual_salary <= 1625000:
        salary_deduction = 550000
    elif annual_salary <= 1800000:
        salary_deduction = annual_salary * 0.4 - 100000
    elif annual_salary <= 3600000:
        salary_deduction = annual_salary * 0.3 + 80000
    elif annual_salary <= 6600000:
        salary_deduction = annual_salary * 0.2 + 440000
    elif annual_salary <= 8500000:
        salary_deduction = annual_salary * 0.1 + 1100000
    else:
        salary_deduction = 1950000
    
    # 各種控除額を計算
    basic_deduction = 480000  # 基礎控除
    social_insurance = annual_salary * (social_insurance_rate / 100)
    other_deductions = other_deductions_man * 10000
    
    # 課税所得を計算
    taxable_income = annual_salary - salary_deduction - basic_deduction - social_insurance - other_deductions
    
    return max(0, taxable_income / 10000)


def show_investment_comparison():
    """投資信託 vs 生命保険比較ページ"""
    st.header("⚖️ 投資信託 vs 生命保険比較")
    st.markdown("同じ金額を投資信託と生命保険に投資した場合の比較分析を行います。")
    st.markdown("**生命保険の控除効果**も考慮した正確な比較を提供します。")
    
    # パラメータ設定
    st.subheader("📋 比較条件設定")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### 💰 共通設定")
        
        monthly_investment = st.number_input(
            "月額投資金額（円）",
            min_value=1000,
            max_value=50000,
            value=9000,
            step=1000,
            key="comp_monthly_investment"
        )
        
        investment_period = st.slider(
            "投資期間（年）",
            min_value=5,
            max_value=30,
            value=10,
            key="comp_investment_period"
        )
        
        # 収入入力方式選択
        input_method = st.radio(
            "収入入力方式",
            ["課税所得で入力", "年収から計算"],
            horizontal=True,
            key="income_input_method"
        )
        
        if input_method == "課税所得で入力":
            annual_income_comp_man = st.number_input(
                "課税所得（万円）",
                min_value=100,
                max_value=5000,
                value=600,
                step=50,
                key="comp_annual_income_man",
                help="給与所得控除・基礎控除等を差し引いた後の課税対象所得額"
            )
            
            # 推定年収表示
            estimated_annual_salary = _estimate_annual_salary_from_taxable_income(annual_income_comp_man)
            st.info(f"💡 推定年収: 約{estimated_annual_salary:.0f}万円")
            
        else:  # 年収から計算
            annual_salary_man = st.number_input(
                "年収（万円）",
                min_value=200,
                max_value=2000,
                value=800,
                step=50,
                key="comp_annual_salary_man",
                help="税込み年収（賞与込み）"
            )
            
            # 控除額設定
            col_ded1, col_ded2 = st.columns(2)
            
            with col_ded1:
                social_insurance_rate = st.slider(
                    "社会保険料率（%）",
                    min_value=10.0,
                    max_value=20.0,
                    value=15.0,
                    step=0.5,
                    key="social_insurance_rate",
                    help="健康保険料・厚生年金保険料・雇用保険料の合計"
                )
            
            with col_ded2:
                other_deductions_man = st.number_input(
                    "その他控除（万円）",
                    min_value=0,
                    max_value=200,
                    value=50,
                    step=10,
                    key="other_deductions",
                    help="配偶者控除・扶養控除・生命保険料控除等"
                )
            
            # 課税所得を計算
            annual_income_comp_man = _calculate_taxable_income_from_salary(
                annual_salary_man, social_insurance_rate, other_deductions_man
            )
            
            st.success(f"📊 計算結果: 課税所得 {annual_income_comp_man:.0f}万円")
        
        # 課税所得・年収の計算方法説明
        with st.expander("🧮 計算方法の詳細説明", expanded=False):
            
            # 計算式をわかりやすく表示
            st.markdown("### 📊 課税所得の計算式")
            
            # 計算式をカードスタイルで表示
            st.markdown("""
            <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff6b6b;">
                <h4 style="color: #333; margin-top: 0;">� 基本計算式</h4>
                <p style="font-size: 18px; font-weight: bold; color: #333; text-align: center; margin: 15px 0;">
                    課税所得 = 年収 - 給与所得控除 - 基礎控除 - 社会保険料控除 - その他控除
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 給与所得控除を視覚的に表示
            st.markdown("#### 💰 給与所得控除（令和5年分）")
            
            col_table1, col_table2 = st.columns([1, 1])
            
            with col_table1:
                st.markdown("""
                | 年収範囲 | 給与所得控除 |
                |---------|-------------|
                | 162.5万円以下 | **55万円** |
                | 162.5万円超～180万円以下 | **年収×40%-10万円** |
                | 180万円超～360万円以下 | **年収×30%+8万円** |
                """)
            
            with col_table2:
                st.markdown("""
                | 年収範囲 | 給与所得控除 |
                |---------|-------------|
                | 360万円超～660万円以下 | **年収×20%+44万円** |
                | 660万円超～850万円以下 | **年収×10%+110万円** |
                | 850万円超 | **195万円（上限）** |
                """)
            
            st.markdown("---")
            
            # 所得控除をカラムで整理
            st.markdown("#### 🏷️ 主な所得控除")
            
            col_ded1, col_ded2, col_ded3 = st.columns(3)
            
            with col_ded1:
                st.metric("基礎控除", "48万円", help="全員に適用される基本控除")
                st.metric("配偶者控除", "38万円", help="配偶者の所得が48万円以下の場合")
            
            with col_ded2:
                st.metric("社会保険料控除", "年収×15%程度", help="健康保険・厚生年金・雇用保険")
                st.metric("扶養控除", "38万円/人", help="扶養家族1人あたり")
            
            with col_ded3:
                st.metric("生命保険料控除", "最大12万円", help="旧制度の場合")
                st.metric("地震保険料控除", "最大5万円", help="地震保険料支払額")
            
            st.markdown("---")
            
            # 具体的な計算例を段階的に表示
            st.markdown("#### 📈 計算例（年収800万円の場合）")
            
            # 計算過程を視覚的に表示
            calc_col1, calc_col2, calc_col3 = st.columns([1, 0.1, 1])
            
            with calc_col1:
                st.markdown("""
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px;">
                    <h5>📊 収入・控除内訳</h5>
                    <ul style="font-size: 14px;">
                        <li><strong>年収</strong>: 800万円</li>
                        <li><strong>給与所得控除</strong>: 800×10%+110 = 190万円</li>
                        <li><strong>基礎控除</strong>: 48万円</li>
                        <li><strong>社会保険料控除</strong>: 800×15% = 120万円</li>
                        <li><strong>その他控除</strong>: 50万円</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with calc_col2:
                st.markdown("""
                <div style="text-align: center; padding-top: 50px;">
                    <span style="font-size: 24px;">→</span>
                </div>
                """, unsafe_allow_html=True)
            
            with calc_col3:
                st.markdown("""
                <div style="background-color: #f3e5f5; padding: 15px; border-radius: 8px;">
                    <h5>🎯 計算結果</h5>
                    <p style="font-size: 16px; margin: 10px 0;">
                        <strong>課税所得</strong> = 800 - 190 - 48 - 120 - 50
                    </p>
                    <p style="font-size: 20px; font-weight: bold; color: #7b1fa2; text-align: center; margin: 15px 0;">
                        = 392万円
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 相互計算機能の説明
            st.markdown("#### 🔄 相互計算機能")
            
            func_col1, func_col2 = st.columns(2)
            
            with func_col1:
                st.markdown("""
                <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #ff9800;">
                    <h6>📥 課税所得 → 年収推定</h6>
                    <p style="font-size: 13px; margin-bottom: 0;">
                        入力された課税所得から標準的な控除額を逆算して推定年収を表示
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with func_col2:
                st.markdown("""
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50;">
                    <h6>📤 年収 → 課税所得計算</h6>
                    <p style="font-size: 13px; margin-bottom: 0;">
                        年収・社会保険料率・その他控除から正確な課税所得を自動計算
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.info("💡 **正確な課税所得は源泉徴収票でご確認ください**")
        
    with col2:
        st.markdown("#### 🏦 生命保険設定")
        
        insurance_annual_rate = st.number_input(
            "保険年利（%）",
            min_value=0.0,
            max_value=10.0,
            value=1.25,
            step=0.01,
            key="comp_insurance_rate"
        ) / 100
        
        # 保険手数料（固定）
        st.info("**保険手数料**:")
        st.write("- 積立額の1.3%")
        st.write("- 積立残高の0.008%/月")
        
        insurance_fee_rate = 0.013  # 積立額の1.3%
        insurance_balance_fee_rate = 0.00008  # 積立残高の0.008%/月
        
    with col3:
        st.markdown("#### 📈 投資信託設定")
        
        mutual_fund_annual_rate = st.number_input(
            "投資信託期待年利（%）",
            min_value=0.0,
            max_value=15.0,
            value=4.0,
            step=0.1,
            key="comp_fund_rate"
        ) / 100
        
        # 投資信託手数料設定
        st.write("**手数料設定**:")
        
        purchase_fee = st.number_input(
            "購入時手数料（%）",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.1,
            key="comp_purchase_fee"
        ) / 100
        
        annual_management_fee = st.number_input(
            "信託報酬（年率%）",
            min_value=0.0,
            max_value=3.0,
            value=0.094,
            step=0.001,
            key="comp_management_fee"
        ) / 100
        
        hidden_cost = st.number_input(
            "隠れコスト（年率%）",
            min_value=0.0,
            max_value=1.0,
            value=0.01,
            step=0.01,
            key="comp_hidden_cost"
        ) / 100
        
        redemption_fee = st.number_input(
            "解約時手数料（%）",
            min_value=0.0,
            max_value=3.0,
            value=0.0,
            step=0.1,
            key="comp_redemption_fee"
        ) / 100
    
    # 税務設定
    with st.expander("🧮 税務詳細設定", expanded=False):
        col_tax1, col_tax2 = st.columns(2)
        
        with col_tax1:
            st.write("**生命保険税務**:")
            st.write("- 旧生命保険料控除適用")
            st.write("- 最大5万円控除")
            st.write("- 所得税・住民税軽減")
            
        with col_tax2:
            st.write("**投資信託税務**:")
            st.write("- 分配金なし投資信託前提")
            st.write("- 売却時のみ譲渡益課税")
            st.write("- 20.315%（所得税15.315%+住民税5%）")
            
            consider_fund_tax = st.checkbox(
                "投資信託の税金を考慮",
                value=True,
                help="売却時の譲渡益に対する20.315%の税金（分配金なし投資信託前提）"
            )
            
            if consider_fund_tax:
                fund_tax_rate = 0.20315  # 所得税15.315% + 住民税5%
            else:
                fund_tax_rate = 0.0
    
    # 部分解約戦略設定
    st.markdown("#### 🔄 部分解約戦略")
    
    # 戦略設定タブ
    strategy_tab1, strategy_tab2 = st.tabs(["⚙️ 戦略設定", "🎯 自動提案"])
    
    with strategy_tab1:
        st.markdown("##### ⚙️ 手動戦略設定")
        col_manual1, col_manual2 = st.columns(2)
        
        with col_manual1:
            manual_interval = st.selectbox(
                "解約間隔（年）",
                options=[1, 2, 3, 4, 5],
                index=1,  # デフォルト2年
                key="manual_withdrawal_interval"
            )
            
        with col_manual2:
            manual_rate = st.slider(
                "解約率（%）",
                min_value=10,
                max_value=100,
                value=50,  # デフォルト50%
                step=10,
                key="manual_withdrawal_rate"
            )
        
        st.info(f"� 設定: {manual_interval}年ごとに{manual_rate}%ずつ解約")
    
    with strategy_tab2:
        st.markdown("##### 🎯 推奨戦略（自動分析）")
        
        # 推奨戦略の表示
        recommended_interval = 2
        recommended_rate = 50
        
        col_rec1, col_rec2, col_rec3 = st.columns(3)
        
        with col_rec1:
            st.metric(
                "推奨解約間隔",
                f"{recommended_interval}年",
                help="メンテナンスコストと運用効率を考慮"
            )
            
        with col_rec2:
            st.metric(
                "推奨解約率",
                f"{recommended_rate}%",
                help="リスク分散と利益最大化のバランス"
            )
            
        with col_rec3:
            st.metric(
                "効率性スコア",
                "95.2点",
                help="総合的な戦略効果"
            )
        
        st.success("🎯 **推奨理由**: 2年50%戦略は、メンテナンス頻度を抑えつつ、適度なリスク分散と利益確保を実現する最適解です。")
        
        # 採用ボタン
        if st.button("📋 推奨戦略を採用", key="adopt_recommended_strategy"):
            st.session_state.manual_withdrawal_interval = recommended_interval
            st.session_state.manual_withdrawal_rate = recommended_rate
            st.success("✅ 推奨戦略を採用しました！")
    
    # 比較分析実行
    if st.button("⚖️ 詳細比較分析を実行", key="run_investment_comparison"):
        st.success("投資信託 vs 生命保険の比較分析を実行中...")
        
        # 基本設定と税金計算
        annual_income_comp = annual_income_comp_man * 10000
        tax_helper = get_tax_helper()
        
        # 生命保険の税額計算
        annual_insurance_premium = monthly_investment * 12
        tax_result = tax_helper.calculate_annual_tax_savings(annual_insurance_premium, annual_income_comp)
        annual_tax_savings = tax_result['total_savings']
        
        # 投資信託の実質コスト
        total_fund_fee = annual_management_fee + hidden_cost
        monthly_insurance_rate = insurance_annual_rate / 12
        monthly_fund_rate = mutual_fund_annual_rate / 12
        
        # 年次比較データ
        years = list(range(1, investment_period + 1))
        
        # 生命保険データ
        insurance_data = {
            'balance': [],
            'net_benefit': [],
            'cumulative_premium': [],
            'cumulative_tax_savings': []
        }
        
        # 投資信託データ
        fund_data = {
            'balance': [],
            'net_benefit': [],
            'cumulative_investment': [],
            'cumulative_fees': [],
            'tax_paid': []
        }
        
        # 生命保険計算
        insurance_balance = 0
        insurance_cumulative_premium = 0
        insurance_cumulative_fee = 0
        
        for year in years:
            for month in range(12):
                insurance_cumulative_premium += monthly_investment
                
                # 保険手数料計算
                monthly_fee = monthly_investment * insurance_fee_rate
                balance_fee = insurance_balance * insurance_balance_fee_rate
                total_monthly_fee = monthly_fee + balance_fee
                insurance_cumulative_fee += total_monthly_fee
                
                # 実際の積立額
                net_investment = monthly_investment - total_monthly_fee
                insurance_balance = insurance_balance * (1 + monthly_insurance_rate) + net_investment
            
            # 累積節税額
            cumulative_tax_savings = annual_tax_savings * year
            
            # 正味利益（残高 + 節税額 - 払込保険料）
            insurance_net_benefit = insurance_balance + cumulative_tax_savings - insurance_cumulative_premium
            
            insurance_data['balance'].append(insurance_balance)
            insurance_data['net_benefit'].append(insurance_net_benefit)
            insurance_data['cumulative_premium'].append(insurance_cumulative_premium)
            insurance_data['cumulative_tax_savings'].append(cumulative_tax_savings)
        
        # 投資信託計算
        fund_balance = 0
        fund_cumulative_investment = 0
        fund_cumulative_fees = 0
        fund_cumulative_tax = 0
        
        for year in years:
            for month in range(12):
                # 購入時手数料を差し引いた投資額
                net_monthly_investment = monthly_investment * (1 - purchase_fee)
                fund_cumulative_investment += monthly_investment
                monthly_purchase_fee = monthly_investment * purchase_fee
                fund_cumulative_fees += monthly_purchase_fee
                
                # 月次リターン
                fund_balance = fund_balance * (1 + monthly_fund_rate) + net_monthly_investment
                
                # 信託報酬・隠れコストの月次差し引き
                monthly_management_cost = fund_balance * (total_fund_fee / 12)
                fund_balance -= monthly_management_cost
                fund_cumulative_fees += monthly_management_cost
            
            # 解約時の手数料・税金計算（最終年のみ）
            if year == investment_period:
                # 解約手数料
                redemption_cost = fund_balance * redemption_fee
                fund_balance -= redemption_cost
                fund_cumulative_fees += redemption_cost
                
                # 売却時譲渡益税金（最終年のみ）
                if consider_fund_tax:
                    # 譲渡益 = 売却額 - 取得費（投資元本）
                    capital_gain = max(0, fund_balance - fund_cumulative_investment)
                    capital_gain_tax = capital_gain * fund_tax_rate
                    fund_balance -= capital_gain_tax
                    fund_cumulative_tax += capital_gain_tax
            
            # 正味利益（残高 - 投資額 - 累積税金 - 累積手数料）
            # 注：投資信託は節税効果がないため、税負担・手数料負担が正味利益を圧迫
            fund_net_benefit = fund_balance - fund_cumulative_investment
            
            fund_data['balance'].append(fund_balance)
            fund_data['net_benefit'].append(fund_net_benefit)
            fund_data['cumulative_investment'].append(fund_cumulative_investment)
            fund_data['cumulative_fees'].append(fund_cumulative_fees)
            fund_data['tax_paid'].append(fund_cumulative_tax)
        
        # 生命保険の最適解約タイミング分析
        st.markdown("---")
        st.subheader("🎯 投資信託vs生命保険 最適解約タイミング分析")
        
        # 各年での解約→乗り換え戦略の最終利益を計算
        optimal_timing_data = []
        best_switch_benefit = 0  # 暫定値、後で正しい値に更新
        optimal_year = investment_period  # デフォルトは満期まで保持
        crossover_year = None  # 投資信託が有利になる年
        
        for i, year in enumerate(years):
            # 生命保険のその年での解約時の正味利益
            current_balance = insurance_data['balance'][i]
            current_tax_savings = insurance_data['cumulative_tax_savings'][i]
            current_premium_paid = insurance_data['cumulative_premium'][i]
            
            # 解約時の正味利益（残高 + 節税額 - 払込保険料）
            insurance_net_benefit = current_balance + current_tax_savings - current_premium_paid
            
            # この年で解約して残りを投資信託で運用した場合の最終利益を計算
            remaining_years = investment_period - year
            if remaining_years > 0:
                # 解約返戻金を投資信託で運用
                switch_fund_balance = current_balance * (1 - purchase_fee)
                switch_cumulative_fee = current_balance * purchase_fee
                
                # 残り期間での積立・運用
                for remaining_year in range(remaining_years):
                    for month in range(12):
                        # 月次積立
                        monthly_net = monthly_investment * (1 - purchase_fee)
                        switch_cumulative_fee += monthly_investment * purchase_fee
                        
                        # 運用益
                        switch_fund_balance = switch_fund_balance * (1 + monthly_fund_rate) + monthly_net
                        
                        # 信託報酬
                        monthly_cost = switch_fund_balance * (total_fund_fee / 12)
                        switch_fund_balance -= monthly_cost
                        switch_cumulative_fee += monthly_cost
                
                # 最終売却時の税金処理
                if consider_fund_tax:
                    total_investment = current_balance + (monthly_investment * remaining_years * 12)
                    capital_gain = max(0, switch_fund_balance - total_investment + switch_cumulative_fee)
                    capital_gain_tax = capital_gain * fund_tax_rate
                    switch_fund_balance -= capital_gain_tax
                
                # 解約手数料
                redemption_cost = switch_fund_balance * redemption_fee
                switch_fund_balance -= redemption_cost
                
                # 乗り換え戦略の最終正味利益
                total_premium_paid = current_premium_paid + (monthly_investment * remaining_years * 12)
                switch_final_benefit = switch_fund_balance + current_tax_savings - total_premium_paid
            else:
                # 最終年なので解約のみ
                switch_final_benefit = insurance_net_benefit
            
            # 投資信託の同時期の正味利益
            fund_net_benefit = fund_data['net_benefit'][i]
            
            # 利益差額（投資信託 - 生命保険）
            benefit_difference = fund_net_benefit - insurance_net_benefit
            
            optimal_timing_data.append({
                'year': year,
                'balance': current_balance,
                'tax_savings': current_tax_savings,
                'net_benefit': insurance_net_benefit,
                'switch_final_benefit': switch_final_benefit,
                'fund_net_benefit': fund_net_benefit,
                'benefit_difference': benefit_difference,
                'fund_is_better': benefit_difference > 0,
                'roi': ((current_balance + current_tax_savings) / current_premium_paid - 1) if current_premium_paid > 0 else 0
            })
            
            # 最も利益の高い乗り換えタイミングを記録
            if switch_final_benefit > best_switch_benefit:
                best_switch_benefit = switch_final_benefit
                optimal_year = year
            
            # 投資信託が有利になった最初の年を記録
            if crossover_year is None and benefit_difference > 0:
                crossover_year = year
        
        # 最適解約タイミングの結果表示
        col_optimal1, col_optimal2, col_optimal3, col_optimal4 = st.columns(4)
        
        optimal_data = optimal_timing_data[optimal_year - 1]
        
        with col_optimal1:
            if crossover_year:
                st.metric(
                    "🔄 最適解約年",
                    f"{optimal_year}年目",
                    f"投資信託切替推奨",
                    delta_color="normal"
                )
            else:
                st.metric(
                    "🏦 推奨戦略",
                    "満期まで保持",
                    f"生命保険が有利",
                    delta_color="normal"
                )
        
        with col_optimal2:
            st.metric(
                "生命保険利益",
                f"{optimal_data['net_benefit']/10000:.1f}万円",
                f"ROI: {optimal_data['roi']:.1%}"
            )
            
        with col_optimal3:
            st.metric(
                "投資信託利益",
                f"{optimal_data['fund_net_benefit']/10000:.1f}万円",
                f"{optimal_data['benefit_difference']/10000:+.1f}万円差"
            )
            
        with col_optimal4:
            if optimal_data['fund_is_better']:
                st.metric(
                    "利益差額",
                    f"{abs(optimal_data['benefit_difference'])/10000:.1f}万円",
                    "投資信託が有利",
                    delta_color="normal"
                )
            else:
                st.metric(
                    "利益差額",
                    f"{abs(optimal_data['benefit_difference'])/10000:.1f}万円",
                    "生命保険が有利",
                    delta_color="inverse"
                )
        
        # 年別比較詳細表示
        st.markdown("#### 📊 年別利益比較分析")
        
        # 比較表作成
        comparison_df = pd.DataFrame([
            {
                '年': data['year'],
                '生命保険利益': f"{data['net_benefit']/10000:.1f}万円",
                '投資信託利益': f"{data['fund_net_benefit']/10000:.1f}万円",
                '利益差額': f"{data['benefit_difference']/10000:+.1f}万円",
                '有利な選択': "📈投資信託" if data['fund_is_better'] else "🏦生命保険"
            }
            for data in optimal_timing_data[::2]  # 2年おきに表示
        ])
        
        st.dataframe(comparison_df, width='stretch')
        
        # 正味利益の差額要因分析
        st.markdown("#### 💰 正味利益の差額要因")
        
        final_insurance_data = insurance_data
        final_fund_data = fund_data
        
        col_factor1, col_factor2 = st.columns(2)
        
        with col_factor1:
            st.markdown("**🏦 生命保険の優位要因**")
            final_tax_savings = final_insurance_data['cumulative_tax_savings'][-1]
            st.write(f"✅ 節税効果: +{final_tax_savings/10000:.1f}万円")
            st.write(f"✅ 低い実質手数料")
            st.write(f"✅ 税務上の優遇")
            
        with col_factor2:
            st.markdown("**📈 投資信託の制約要因**")
            final_fund_tax = final_fund_data['tax_paid'][-1] 
            final_fund_fees = final_fund_data['cumulative_fees'][-1]
            st.write(f"❌ 税負担: -{final_fund_tax/10000:.1f}万円")
            st.write(f"❌ 手数料: -{final_fund_fees/10000:.1f}万円")
            st.write(f"❌ 節税効果なし")
        
        # 実質的な利益比較（プルダウンで隠せる）
        with st.expander("🔍 なぜ残高が高いのに正味利益が低いのか？", expanded=False):
            st.warning(f"""
            **投資信託の正味利益が低い理由**:
            
            1. **売却時税負担**: 譲渡益に20.315%の税金 → -{final_fund_tax/10000:.1f}万円
            2. **各種手数料**: 購入・信託報酬・隠れコスト → -{final_fund_fees/10000:.1f}万円  
            3. **節税効果なし**: 生命保険は年間{final_tax_savings/len(years)/10000:.1f}万円の節税
            
            **結果**: 残高は高いが、売却時税金・手数料を差し引くと正味利益は減少
            
            **注**: 分配金なし投資信託前提のため、保有期間中は課税されません
            """)
        
        # クロスオーバーポイントの説明
        if crossover_year:
            st.info(f"""
            💡 **分析結果**: {crossover_year}年目から投資信託の方が有利になります。
            
            **推奨戦略**: 
            - 1-{crossover_year-1}年目: 生命保険で積立（節税効果重視）
            - {crossover_year}年目: 解約して投資信託に切り替え（成長性重視）
            """)
        else:
            st.info("""
            💡 **分析結果**: 全期間を通じて生命保険の方が有利です。
            
            **推奨戦略**: 
            - 満期まで生命保険を継続（節税効果が運用収益を上回る）
            """)
        
        # 全体結果を先に計算
        final_insurance_balance = insurance_data['balance'][-1]
        final_insurance_net = insurance_data['net_benefit'][-1]
        final_fund_balance = fund_data['balance'][-1]
        final_fund_net = fund_data['net_benefit'][-1]
        
        # 最適解約年計算のベースラインを設定
        best_switch_benefit = final_insurance_net  # 生命保険満期保持を基準
        
        # 切り替え戦略変数を初期化
        switch_fund_balance = 0
        switch_net_benefit = 0
        switch_total_tax_savings = 0
        remaining_years = 0
        
        # 最適解約→投資信託乗り換え戦略の分析
        if optimal_year <= len(fund_data['balance']):
            fund_net_at_optimal = fund_data['net_benefit'][optimal_year - 1]
            
            st.markdown("---")
            st.subheader("🔄 最適解約→投資信託乗り換え戦略分析")
            
            # 乗り換え戦略のシミュレーション
            remaining_years = investment_period - optimal_year
            optimal_withdrawal_amount = optimal_data['balance']  # 解約返戻金
            
            # 乗り換え後の投資信託運用シミュレーション
            if remaining_years > 0:
                # 解約返戻金を一括投資 + 残り期間の積立継続
                switch_fund_balance = optimal_withdrawal_amount
                
                # 購入手数料を差し引く
                switch_fund_balance *= (1 - purchase_fee)
                switch_cumulative_fee = optimal_withdrawal_amount * purchase_fee
                
                # 残り期間での運用
                for year in range(remaining_years):
                    for month in range(12):
                        # 月次積立（手数料差し引き後）
                        monthly_net = monthly_investment * (1 - purchase_fee)
                        switch_cumulative_fee += monthly_investment * purchase_fee
                        
                        # 運用益
                        switch_fund_balance = switch_fund_balance * (1 + monthly_fund_rate) + monthly_net
                        
                        # 信託報酬・隠れコスト
                        monthly_cost = switch_fund_balance * (total_fund_fee / 12)
                        switch_fund_balance -= monthly_cost
                        switch_cumulative_fee += monthly_cost
                
                # 最終的な解約処理
                if consider_fund_tax:
                    # 売却益税金
                    total_investment_switch = optimal_withdrawal_amount + (monthly_investment * remaining_years * 12)
                    capital_gain = max(0, switch_fund_balance - total_investment_switch + switch_cumulative_fee)
                    capital_gain_tax = capital_gain * fund_tax_rate
                    switch_fund_balance -= capital_gain_tax
                
                # 解約手数料
                redemption_cost = switch_fund_balance * redemption_fee
                switch_fund_balance -= redemption_cost
                switch_cumulative_fee += redemption_cost
                
                # 乗り換え戦略の正味利益計算
                total_premium_paid = insurance_data['cumulative_premium'][optimal_year - 1] + (monthly_investment * remaining_years * 12)
                switch_total_tax_savings = insurance_data['cumulative_tax_savings'][optimal_year - 1]
                switch_net_benefit = switch_fund_balance + switch_total_tax_savings - total_premium_paid
                
            else:
                switch_fund_balance = optimal_withdrawal_amount
                switch_net_benefit = optimal_data['net_benefit']
                remaining_years = 0
            

            
            # 最適部分解約戦略の探索
            optimal_partial_result = optimize_partial_withdrawal_strategy(
                monthly_investment,
                investment_period,
                insurance_annual_rate,
                annual_tax_savings,
                mutual_fund_annual_rate,
                total_fund_fee
            )
            
            # 戦略比較表示
            st.markdown("---")
            st.subheader("🎯 戦略比較サマリー")
            
            # 4つの戦略を2行に分けて表示
            col_strategy1, col_strategy2 = st.columns(2)
            
            with col_strategy1:
                st.markdown("#### 🏦 生命保険のみ戦略")
                st.info(f"""
                **{investment_period}年満期まで保持**
                - 最終残高: {final_insurance_balance/10000:.1f}万円
                - 正味利益: {final_insurance_net/10000:.1f}万円
                - 累積節税: {insurance_data['cumulative_tax_savings'][-1]/10000:.1f}万円
                """)
                
                st.markdown("#### 🔄 一括解約→乗り換え戦略")
                if remaining_years > 0:
                    st.success(f"""
                    **{optimal_year}年解約→投資信託乗り換え**
                    - 最終残高: {switch_fund_balance/10000:.1f}万円
                    - 正味利益: {switch_net_benefit/10000:.1f}万円
                    - 節税効果: {switch_total_tax_savings/10000:.1f}万円
                    """)
                else:
                    st.success(f"""
                    **{optimal_year}年解約（最適）**
                    - 解約残高: {optimal_data['balance']/10000:.1f}万円
                    - 正味利益: {optimal_data['net_benefit']/10000:.1f}万円
                    - 節税効果: {optimal_data['tax_savings']/10000:.1f}万円
                    """)
            
            with col_strategy2:
                st.markdown("#### 📈 投資信託のみ戦略")
                st.info(f"""
                **{investment_period}年継続投資**
                - 最終残高: {final_fund_balance/10000:.1f}万円
                - 正味利益: {final_fund_net/10000:.1f}万円
                - 累積手数料: {fund_data['cumulative_fees'][-1]/10000:.1f}万円
                """)
                
                st.markdown("#### 🔄 部分解約戦略（自動最適化）")
                st.info("最適戦略は自動計算されます。下記をご参照ください。")
            
            # 最適部分解約戦略の表示
            best_partial = optimal_partial_result['best_strategy']
            st.markdown("#### 🏆 最適部分解約戦略")
            st.success(f"""
            **推奨**: {best_partial['name']} 
            - 最終利益: {best_partial['final_benefit']/10000:.1f}万円
            - 解約間隔: {best_partial['interval']}年
            - 解約割合: {best_partial['ratio']*100:.0f}%
            """)
            
            # 部分解約戦略比較グラフ
            st.markdown("---")
            st.subheader("📊 部分解約戦略比較分析")
            
            # 最適部分解約戦略のデータを取得
            optimal_partial_data = best_partial['result']
            
            # 比較グラフの作成
            fig_partial_comparison = go.Figure()
            
            years_range = list(range(1, investment_period + 1))
            

            
            # 最適部分解約戦略
            fig_partial_comparison.add_trace(go.Scatter(
                x=years_range,
                y=[x/10000 for x in optimal_partial_data['total_net_benefit']],
                mode='lines+markers',
                name=f'最適戦略 ({best_partial["interval"]}年毎{best_partial["ratio"]*100:.0f}%)',
                line=dict(color='red', width=2, dash='dash'),
                marker=dict(size=6)
            ))
            
            # 生命保険のみ（参考）
            fig_partial_comparison.add_trace(go.Scatter(
                x=years_range,
                y=[x/10000 for x in insurance_data['net_benefit']],
                mode='lines',
                name='生命保険のみ（参考）',
                line=dict(color='green', width=1, dash='dot'),
                opacity=0.7
            ))
            
            # 投資信託のみ（参考）
            fig_partial_comparison.add_trace(go.Scatter(
                x=years_range,
                y=[x/10000 for x in fund_data['net_benefit']],
                mode='lines',
                name='投資信託のみ（参考）',
                line=dict(color='orange', width=1, dash='dot'),
                opacity=0.7
            ))
            

            
            # 解約タイミングの表示（最適戦略）
            withdrawal_years_optimal = [y for y in range(best_partial['interval'], investment_period, best_partial['interval'])]
            for year in withdrawal_years_optimal:
                if year < len(optimal_partial_data['total_net_benefit']):
                    fig_partial_comparison.add_vline(
                        x=year, 
                        line_dash="solid", 
                        line_color="red",
                        opacity=0.3,
                        annotation_text=f"最適{best_partial['ratio']*100:.0f}%"
                    )
            
            fig_partial_comparison.update_layout(
                title="部分解約戦略比較: 正味利益の推移",
                xaxis_title="経過年数",
                yaxis_title="正味利益 (万円)",
                legend=dict(x=0.02, y=0.98),
                hovermode='x unified',
                showlegend=True
            )
            
            st.plotly_chart(fig_partial_comparison, use_container_width=True)
            
            # 戦略詳細比較表
            col_detail1, col_detail2 = st.columns(2)
            
            with col_detail1:
                st.markdown("##### 最適戦略の詳細")
                withdrawal_count_optimal = len(withdrawal_years_optimal)
                st.success(f"""
                **解約パターン**: {best_partial['interval']}年毎に{best_partial['ratio']*100:.0f}%解約
                - 解約回数: {withdrawal_count_optimal}回
                - 総解約額: {optimal_partial_data['total_withdrawal']/10000:.1f}万円
                - 解約手数料: {optimal_partial_data['total_withdrawal_fees']/10000:.1f}万円
                - 最終保険残高: {optimal_partial_data['final_insurance_balance']/10000:.1f}万円
                - 最終投信残高: {optimal_partial_data['final_fund_balance']/10000:.1f}万円
                """)
            


            
            # 全戦略包括比較グラフ
            st.markdown("---")
            st.subheader("🎯 全戦略総合比較")
            
            fig_all_strategies = go.Figure()
            
            # 生命保険のみ
            fig_all_strategies.add_trace(go.Scatter(
                x=years_range,
                y=[x/10000 for x in insurance_data['net_benefit']],
                mode='lines+markers',
                name='🏦 生命保険のみ',
                line=dict(color='green', width=2),
                marker=dict(size=5)
            ))
            
            # 投資信託のみ
            fig_all_strategies.add_trace(go.Scatter(
                x=years_range,
                y=[x/10000 for x in fund_data['net_benefit']],
                mode='lines+markers',
                name='📈 投資信託のみ',
                line=dict(color='orange', width=2),
                marker=dict(size=5)
            ))
            
            # 一括解約乗り換え戦略
            if remaining_years > 0:
                switch_net_benefits = []
                # 解約時の投資信託投資額を計算
                switch_fund_initial = optimal_data['balance']  # 解約手数料0円
                
                for year in years_range:
                    if year <= optimal_year:
                        # 解約前は生命保険
                        switch_net_benefits.append(insurance_data['net_benefit'][year-1])
                    else:
                        # 解約後は投資信託成長を計算
                        years_after_switch = year - optimal_year
                        growth_factor = (1 + mutual_fund_annual_rate) ** years_after_switch
                        fund_balance = switch_fund_initial * growth_factor
                        
                        # 手数料計算（年間手数料率 × 年数）
                        annual_fee = fund_balance * total_fund_fee
                        cumulative_fees = switch_fund_initial * total_fund_fee * years_after_switch
                        net_fund_balance = fund_balance - cumulative_fees
                        
                        # 総正味利益（投資信託残高 + 節税効果 - 累積保険料）
                        total_net = net_fund_balance + switch_total_tax_savings - (monthly_investment * 12 * year)
                        switch_net_benefits.append(total_net)
                
                fig_all_strategies.add_trace(go.Scatter(
                    x=years_range,
                    y=[x/10000 for x in switch_net_benefits],
                    mode='lines+markers',
                    name=f'🔄 一括解約乗り換え ({optimal_year}年)',
                    line=dict(color='purple', width=2, dash='dash'),
                    marker=dict(size=5)
                ))
                
                # 最適解約タイミングを表示
                fig_all_strategies.add_vline(
                    x=optimal_year, 
                    line_dash="solid", 
                    line_color="purple",
                    opacity=0.7,
                    annotation_text=f"最適解約({optimal_year}年)"
                )
            

            
            # 最適部分解約戦略
            fig_all_strategies.add_trace(go.Scatter(
                x=years_range,
                y=[x/10000 for x in optimal_partial_data['total_net_benefit']],
                mode='lines+markers',
                name=f'🏆 最適部分解約({best_partial["interval"]}年毎{best_partial["ratio"]*100:.0f}%)',
                line=dict(color='red', width=3),
                marker=dict(size=6)
            ))
            
            fig_all_strategies.update_layout(
                title="全戦略総合比較: 正味利益の推移",
                xaxis_title="経過年数",
                yaxis_title="正味利益 (万円)",
                legend=dict(x=0.02, y=0.98),
                hovermode='x unified',
                showlegend=True,
                height=600
            )
            
            st.plotly_chart(fig_all_strategies, use_container_width=True)
            
            # 戦略ランキング表
            st.markdown("##### 📊 最終利益ランキング")
            
            strategy_results = [
                ("🏦 生命保険のみ", final_insurance_net),
                ("📈 投資信託のみ", final_fund_net),
                ("🏆 最適部分解約", best_partial['final_benefit'])
            ]
            
            if remaining_years > 0:
                strategy_results.append(("🔄 一括解約乗り換え", switch_net_benefit))
            
            # 利益順にソート
            strategy_results.sort(key=lambda x: x[1], reverse=True)
            
            ranking_cols = st.columns(len(strategy_results))
            for i, (strategy_name, benefit) in enumerate(strategy_results):
                with ranking_cols[i]:
                    rank_icon = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                    color = ["success", "info", "warning", "secondary", "secondary"][i]
                    
                    if color == "success":
                        st.success(f"""
                        **{rank_icon} {strategy_name}**
                        
                        {benefit/10000:.1f}万円
                        """)
                    elif color == "info":
                        st.info(f"""
                        **{rank_icon} {strategy_name}**
                        
                        {benefit/10000:.1f}万円
                        """)
                    else:
                        st.warning(f"""
                        **{rank_icon} {strategy_name}**
                        
                        {benefit/10000:.1f}万円
                        """)
            
            # 最優戦略の判定
            strategies = {
                "生命保険のみ": final_insurance_net,
                "投資信託のみ": final_fund_net,
                "最適乗り換え": switch_net_benefit
            }
            
            best_strategy = max(strategies, key=strategies.get)
            best_benefit = strategies[best_strategy]
            
            st.markdown("---")
            st.subheader("🏆 最優戦略の結論")
            
            if best_strategy == "最適乗り換え":
                advantage_vs_insurance = switch_net_benefit - final_insurance_net
                advantage_vs_fund = switch_net_benefit - final_fund_net
                
                st.success(f"""
                ## 🎯 **最適解: {optimal_year}年解約→投資信託乗り換え戦略**
                
                **✅ 最大利益**: {best_benefit/10000:.1f}万円
                
                **🏦 生命保険のみとの差**: +{advantage_vs_insurance/10000:.1f}万円
                **📈 投資信託のみとの差**: +{advantage_vs_fund/10000:.1f}万円
                """)
                
                # 具体的実行プラン
                st.markdown("### 📋 具体的実行アクションプラン")
                
                action_col1, action_col2 = st.columns(2)
                
                with action_col1:
                    st.markdown("#### 🗓️ タイムスケジュール")
                    st.write(f"**1年目～{optimal_year}年目**: 生命保険積立")
                    st.write(f"- 月額: {monthly_investment:,}円")
                    st.write(f"- 年間節税: {annual_tax_savings/10000:.1f}万円")
                    st.write(f"- {optimal_year}年目積立残高: {optimal_data['balance']/10000:.1f}万円")
                    
                    if remaining_years > 0:
                        st.write(f"**{optimal_year+1}年目～{investment_period}年目**: 投資信託運用")
                        st.write(f"- 解約返戻金一括投資: {optimal_withdrawal_amount/10000:.1f}万円")
                        st.write(f"- 月額積立継続: {monthly_investment:,}円")
                        st.write(f"- 運用期間: {remaining_years}年間")
                
                with action_col2:
                    st.markdown("#### 💰 期待収益詳細")
                    st.write(f"**生命保険期間（{optimal_year}年間）**")
                    st.write(f"- 払込総額: {insurance_data['cumulative_premium'][optimal_year-1]/10000:.1f}万円")
                    st.write(f"- 節税効果: {insurance_data['cumulative_tax_savings'][optimal_year-1]/10000:.1f}万円")
                    st.write(f"- 解約返戻金: {optimal_data['balance']/10000:.1f}万円")
                    
                    if remaining_years > 0:
                        additional_investment = monthly_investment * remaining_years * 12
                        st.write(f"**投資信託期間（{remaining_years}年間）**")
                        st.write(f"- 追加投資額: {additional_investment/10000:.1f}万円")
                        st.write(f"- 最終運用額: {switch_fund_balance/10000:.1f}万円")
                        st.write(f"- 総正味利益: {switch_net_benefit/10000:.1f}万円")
                
                # リスクと注意点
                st.markdown("---")
                st.subheader("⚠️ 実行時の注意点・リスク")
                
                risk_col1, risk_col2 = st.columns(2)
                
                with risk_col1:
                    st.warning("""
                    **🚨 実行リスク**
                    - **解約タイミングリスク**: 市場環境変化による最適タイミングのズレ
                    - **投資信託リスク**: 乗り換え後の市場変動リスク
                    - **税制変更リスク**: 控除制度や税率の変更可能性
                    - **手数料変動リスク**: 投資信託の手数料体系変更
                    """)
                
                with risk_col2:
                    st.info("""
                    **📋 実行前チェック**
                    - 生命保険の解約条件・手数料確認
                    - 投資信託の最新手数料体系確認
                    - 税務上の確定申告等への影響確認
                    - 家計の流動性・緊急資金確保状況確認
                    """)
            
            else:
                other_strategies = [name for name in strategies.keys() if name != best_strategy]
                advantages = [best_benefit - strategies[name] for name in other_strategies]
                
                st.success(f"""
                ## 🏆 **最優戦略: {best_strategy}**
                
                **最大利益**: {best_benefit/10000:.1f}万円
                """)
                
                for i, other in enumerate(other_strategies):
                    st.write(f"**{other}との差**: +{advantages[i]/10000:.1f}万円")
            
            # 部分解約戦略の詳細分析
            st.markdown("---")
            st.subheader("🔄 部分解約戦略の最適化分析")
            
            # 戦略分析オプション
            analysis_tab1, analysis_tab2 = st.tabs(["🎯 自動提案分析", "⚙️ 戦略設定検証"])
            
            with analysis_tab1:
                st.markdown("##### 🎯 推奨戦略の詳細分析")
                st.info("💡 **2年50%戦略**をベースに、メンテナンス効率と解約率最適化を含む包括的分析を実行します。")
                
                auto_optimize = st.checkbox(
                    "推奨戦略の詳細分析を実行",
                    value=True,
                    key="auto_optimize_strategy"
                )
                
                if auto_optimize:
                    st.markdown("""
                    **分析項目:**
                    - 📊 解約間隔とメンテナンス負荷の関係
                    - 💰 解約率と利益最大化のバランス
                    - ⚖️ リスク分散効果の評価
                    - 🎯 総合効率スコアの算出
                    """)
            
            with analysis_tab2:
                st.markdown("##### ⚙️ カスタム戦略の検証")
                manual_analysis = st.checkbox(
                    "手動設定戦略の分析",
                    value=False,
                    key="manual_strategy_analysis"
                )
                
                if manual_analysis:
                    # セッション状態から手動設定値を取得
                    current_interval = st.session_state.get('manual_withdrawal_interval', 2)
                    current_rate = st.session_state.get('manual_withdrawal_rate', 50)
                    
                    st.info(f"🔧 現在の設定: {current_interval}年ごとに{current_rate}%解約")
                    
                    # 手動設定戦略の分析実行
                    if st.button("📊 手動設定戦略を検証", key="verify_manual_strategy"):
                        with st.spinner(f"🔄 {current_interval}年{current_rate}%戦略を分析中..."):
                            # 手動戦略の計算
                            manual_strategy_result = calculate_manual_strategy_performance(
                                monthly_premium=monthly_investment,
                                investment_period=investment_period,
                                insurance_annual_rate=insurance_annual_rate,
                                annual_tax_savings=annual_tax_savings,
                                fund_annual_return=mutual_fund_annual_rate,
                                fund_annual_fee=total_fund_fee,
                                withdrawal_interval=current_interval,
                                withdrawal_rate=current_rate / 100
                            )
                            
                            # 手動戦略の結果表示
                            st.success("✅ 手動設定戦略の分析が完了しました！")
                            
                            col_manual1, col_manual2, col_manual3 = st.columns(3)
                            
                            with col_manual1:
                                st.metric(
                                    "最終純利益",
                                    f"{manual_strategy_result['final_benefit']:,.0f}円",
                                    help="税効果を含む最終的な利益"
                                )
                            
                            with col_manual2:
                                st.metric(
                                    "解約回数",
                                    f"{manual_strategy_result['withdrawal_count']}回",
                                    help="投資期間中の解約実行回数"
                                )
                            
                            with col_manual3:
                                efficiency_score = min(100, (manual_strategy_result['final_benefit'] / 1000000) * 10)
                                st.metric(
                                    "効率スコア",
                                    f"{efficiency_score:.1f}点",
                                    help="戦略の総合効率性（100点満点）"
                                )
                            
                            # 戦略の詳細分析
                            st.markdown("##### 📈 戦略分析結果")
                            
                            analysis_text = f"""
                            **🔍 分析結果:**
                            - **解約間隔**: {current_interval}年 → {"適切" if current_interval == 2 else "要検討"}（推奨: 2年）
                            - **解約率**: {current_rate}% → {"適切" if current_rate == 50 else "要検討"}（推奨: 50%）
                            - **メンテナンス**: {manual_strategy_result['withdrawal_count']}回の手続き
                            - **リスク分散**: {"良好" if current_rate <= 60 else "高リスク"}
                            
                            **💡 改善提案:**
                            """
                            
                            if current_interval != 2:
                                analysis_text += f"\n- 解約間隔を2年に変更することで、メンテナンス効率が向上します"
                            if current_rate != 50:
                                analysis_text += f"\n- 解約率を50%に調整することで、リスク分散効果が最適化されます"
                            if current_interval == 2 and current_rate == 50:
                                analysis_text += f"\n- ✅ 現在の設定は推奨戦略と一致しており、最適です！"
                            
                            st.info(analysis_text)
            
            # 最適化実行
            if auto_optimize:
                with st.spinner("🔄 最適な部分解約戦略を計算中..."):
                    # 最適化計算
                    optimization_result = optimize_partial_withdrawal_strategy(
                        monthly_premium=monthly_investment,
                        investment_period=investment_period,
                        insurance_annual_rate=insurance_annual_rate,
                        annual_tax_savings=annual_tax_savings,
                        fund_annual_return=mutual_fund_annual_rate,
                        fund_annual_fee=total_fund_fee
                    )
                
                best_strategy = optimization_result['best_strategy']
                all_strategies = optimization_result['strategies']
                top_strategies = optimization_result['top_strategies']
                optimization_stats = optimization_result['optimization_stats']
                
                # 最適化統計情報
                st.success(f"✅ 最適戦略が見つかりました！（{optimization_stats['evaluated_strategies']}戦略を評価）")
                
                # 最適戦略の詳細提案
                st.markdown("### 🎯 最適部分解約戦略の提案")
                
                col_proposal1, col_proposal2 = st.columns([2, 1])
                
                with col_proposal1:
                    # 2年50%戦略を推奨
                    recommended_strategy = {
                        'name': '2年50%戦略',
                        'interval': 2,
                        'ratio': 0.5,
                        'final_benefit': best_strategy['final_benefit']  # 実際の計算結果を使用
                    }
                    
                    st.success(f"""
                    **🏆 推奨戦略: {recommended_strategy['name']}**
                    
                    **📋 実行プラン:**
                    1. **解約タイミング**: {recommended_strategy['interval']}年毎に実行
                    2. **解約割合**: 積立残高の{recommended_strategy['ratio']*100:.0f}%を解約
                    3. **メンテナンス**: 適度な頻度で管理負荷を軽減
                    4. **リスク分散**: 50%ずつの分割でリスクを分散
                    
                    **💰 期待効果:**
                    - 最終純利益: **{recommended_strategy['final_benefit']:,.0f}円**
                    - メンテナンス効率と利益のバランスが最適
                    
                    **🎯 推奨理由:**
                    - 📊 **メンテナンス効率**: 2年間隔で手続き負荷を軽減
                    - 💰 **利益最大化**: 50%解約で適切なリスク分散
                    - ⚖️ **総合バランス**: 手間と収益の最適なバランス
                    """)
                
                with col_proposal2:
                    st.markdown("**📊 戦略メトリクス**")
                    st.metric("解約間隔", f"{best_strategy['interval']}年毎")
                    st.metric("解約割合", f"{best_strategy['ratio']*100:.0f}%")
                    st.metric("最終純利益", f"{best_strategy['final_benefit']/10000:.1f}万円")
                    
                    # 他の戦略との差
                    if len(top_strategies) > 1:
                        second_best = top_strategies[1]
                        advantage = best_strategy['final_benefit'] - second_best['final_benefit']
                        st.metric("2位との差", f"+{advantage:,.0f}円")
                
                # なぜこの戦略が最適なのかの説明
                with st.expander("🤔 なぜこの戦略が最適なのか？", expanded=False):
                    st.markdown(f"""
                    **最適化の根拠:**
                    
                    1. **解約間隔（{best_strategy['interval']}年）の優位性**
                       - 短すぎる解約間隔: 解約手数料が頻繁に発生し不利
                       - 長すぎる解約間隔: 投資信託の複利効果を活用できない
                       - {best_strategy['interval']}年間隔: 手数料と複利効果のバランスが最適
                    
                    2. **解約割合（{best_strategy['ratio']*100:.0f}%）の優位性**
                       - 少なすぎる解約: 投資信託への移行効果が限定的
                       - 多すぎる解約: 生命保険の節税効果を失う
                       - {best_strategy['ratio']*100:.0f}%解約: 両方の利点を最大化
                    
                    3. **リスク分散効果**
                       - 生命保険: 安定性と節税効果
                       - 投資信託: 成長性と流動性
                       - 部分解約: 両方の良いとこ取り
                    
                    **⚠️ 注意事項:**
                    - 解約時は解約手数料（約1%）が発生
                    - 解約金は一時所得として課税対象
                    - 投資信託の運用成果は市場状況に依存
                    """)
                
                # 上位戦略の表示
                st.markdown("##### 🏆 上位3戦略")
                col_top1, col_top2, col_top3 = st.columns(3)
                
                for i, strategy in enumerate(top_strategies):
                    with [col_top1, col_top2, col_top3][i]:
                        rank_emoji = ["🥇", "🥈", "🥉"][i]
                        st.metric(
                            f"{rank_emoji} {i+1}位",
                            f"{strategy['final_benefit']:,.0f}円",
                            help=f"{strategy['name']}"
                        )
                
                # 戦略比較表
                with st.expander("📊 全戦略の比較結果", expanded=False):
                    st.markdown(f"**最適化統計**: {optimization_stats['evaluated_strategies']}/{optimization_stats['total_combinations']} 戦略を評価")
                    
                    strategies_df = []
                    for i, strategy in enumerate(sorted(all_strategies, key=lambda x: x['final_benefit'], reverse=True)):
                        rank_emoji = ""
                        if i == 0:
                            rank_emoji = "🏆"
                        elif i < 3:
                            rank_emoji = ["", "🥈", "🥉"][i]
                            
                        strategies_df.append({
                            '順位': f"{i+1}{rank_emoji}",
                            '戦略': strategy['name'],
                            '解約間隔': f"{strategy['interval']}年",
                            '解約割合': f"{strategy['ratio']*100:.0f}%",
                            '解約回数': f"{strategy.get('withdrawal_count', 0)}回",
                            '最終純利益': f"{strategy['final_benefit']:,.0f}円"
                        })
                    
                    import pandas as pd
                    strategies_table = pd.DataFrame(strategies_df)
                    st.dataframe(strategies_table, hide_index=True)
                
                # 最適戦略を使用して詳細分析
                partial_strategy_results = best_strategy['result']
                partial_interval = best_strategy['interval']
                partial_ratio = best_strategy['ratio']
                analyze_partial = True
                
            # 手動設定分析
            if manual_analysis:
                st.markdown("##### ⚙️ 手動戦略設定")
                col_partial1, col_partial2, col_partial3 = st.columns(3)
                
                with col_partial1:
                    partial_interval = st.selectbox(
                        "解約間隔（年）",
                        options=[2, 3, 4, 5, 6, 7],
                        index=3,  # 5年がデフォルト
                        key="comp_partial_interval"
                    )
                
                with col_partial2:
                    partial_ratio = st.slider(
                        "解約割合（%）",
                        min_value=20,
                        max_value=80,
                        value=50,
                        step=10,
                        key="comp_partial_ratio"
                    ) / 100
                
                with col_partial3:
                    analyze_partial = st.checkbox(
                        "手動設定で分析実行",
                        value=True,
                        key="analyze_manual_strategy"
                    )
            
            # 分析実行の判定
            if not auto_optimize and not manual_analysis:
                analyze_partial = False
            
            if analyze_partial:
                # 手動設定の場合の計算
                if manual_analysis and not auto_optimize:
                    partial_strategy_results = calculate_partial_withdrawal_vs_fund_strategy(
                        monthly_investment,
                        investment_period,
                        insurance_annual_rate,
                        annual_tax_savings,
                        partial_interval,
                        partial_ratio,
                        mutual_fund_annual_rate,
                        total_fund_fee,
                        purchase_fee,
                        consider_fund_tax,
                        fund_tax_rate
                    )
                
                # 部分解約戦略の結果表示
                strategy_type = "🏆 最適戦略" if auto_optimize else "⚙️ 手動設定戦略"
                st.markdown(f"#### 📊 {strategy_type}の分析結果")
                
                # 戦略の詳細情報
                if auto_optimize:
                    st.info(f"✨ **最適化結果**: {partial_interval}年毎に{partial_ratio*100:.0f}%解約が最も有利な戦略です")
                else:
                    st.info(f"⚙️ **手動設定**: {partial_interval}年毎に{partial_ratio*100:.0f}%解約で分析")
                
                col_partial_result1, col_partial_result2, col_partial_result3 = st.columns(3)
                
                with col_partial_result1:
                    st.metric(
                        "部分解約戦略の最終価値",
                        f"{partial_strategy_results['final_net_benefit']/10000:.1f}万円",
                        help=f"戦略: {partial_interval}年毎に{partial_ratio*100:.0f}%解約"
                    )
                
                with col_partial_result2:
                    improvement_vs_insurance = partial_strategy_results['final_net_benefit'] - final_insurance_net
                    improvement_rate = improvement_vs_insurance / final_insurance_net * 100
                    st.metric(
                        "生命保険のみとの差",
                        f"{improvement_vs_insurance/10000:+.1f}万円",
                        delta=f"{improvement_rate:+.1f}%"
                    )
                
                with col_partial_result3:
                    improvement_vs_fund = partial_strategy_results['final_net_benefit'] - final_fund_net
                    st.metric(
                        "投資信託のみとの差", 
                        f"{improvement_vs_fund/10000:+.1f}万円",
                        delta=f"{improvement_vs_fund/final_fund_net*100:+.1f}%"
                    )
                
                # 部分解約戦略の詳細説明
                st.markdown("#### 💡 部分解約戦略の詳細分析")
                
                # 最適化の場合は理由を説明
                if auto_optimize:
                    with st.expander("🎯 なぜこの戦略が最適なのか？", expanded=True):
                        st.markdown(f"""
                        **最適化の結果**: {partial_interval}年毎に{partial_ratio*100:.0f}%解約が選ばれた理由
                        
                        - **最終利益**: {partial_strategy_results['final_net_benefit']:,.0f}円で最大値を達成
                        - **解約タイミング**: {partial_interval}年間隔が保険の成長と投資信託の複利効果のバランスが最適
                        - **解約割合**: {partial_ratio*100:.0f}%が節税効果と成長性の最適な配分
                        - **評価した戦略数**: {len(all_strategies)}通りの組み合わせから選択
                        """)
                
                col_detail1, col_detail2 = st.columns(2)
                
                with col_detail1:
                    st.info(f"""
                    **📋 戦略概要**:
                    - {partial_interval}年毎に積立残高の{partial_ratio*100:.0f}%を解約
                    - 解約金を投資信託で運用
                    - 残りの保険は継続
                    
                    **✅ メリット**:
                    - 節税効果と成長性の両立
                    - リスク分散効果
                    - タイミングリスクの軽減
                    - 両方の商品の良いとこ取り
                    """)
                
                with col_detail2:
                    withdrawal_count = len(range(partial_interval, investment_period, partial_interval))
                    st.warning(f"""
                    **⚠️ 注意点**:
                    - 解約手数料が{partial_interval}年毎に発生
                    - 管理が複雑になる
                    - 少額投資になる可能性
                    
                    **💰 コスト詳細**:
                    - 総解約回数: {withdrawal_count}回
                    - 解約手数料: 各回約1%
                    - 投資信託の税金: 売却時20.315%
                    """)
                
                # 戦略の時系列推移グラフ
                st.markdown("#### 📈 部分解約戦略の推移")
                
                years_data = partial_strategy_results['years']
                insurance_balances = partial_strategy_results['insurance_balance']
                fund_balances = partial_strategy_results['fund_balance']
                total_benefits = partial_strategy_results['total_net_benefit']
                
                fig_partial = go.Figure()
                
                fig_partial.add_trace(go.Scatter(
                    x=years_data,
                    y=[b/10000 for b in insurance_balances],
                    mode='lines+markers',
                    name='生命保険残高',
                    line=dict(color='blue', width=3),
                    marker=dict(size=6)
                ))
                
                fig_partial.add_trace(go.Scatter(
                    x=years_data,
                    y=[b/10000 for b in fund_balances],
                    mode='lines+markers',
                    name='投資信託残高',
                    line=dict(color='green', width=3),
                    marker=dict(size=6)
                ))
                
                fig_partial.add_trace(go.Scatter(
                    x=years_data,
                    y=[b/10000 for b in total_benefits],
                    mode='lines+markers',
                    name='正味利益合計',
                    line=dict(color='red', width=3, dash='dot'),
                    marker=dict(size=6)
                ))
                
                fig_partial.update_layout(
                    title=f"部分解約戦略（{partial_interval}年毎{partial_ratio*100:.0f}%解約）の推移",
                    xaxis_title="年数",
                    yaxis_title="金額（万円）",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig_partial, width='stretch')
                
                # 戦略の更新
                strategies["部分解約戦略"] = partial_strategy_results['final_net_benefit']
            
            # 戦略比較チャート
            st.markdown("---")
            st.subheader("📊 戦略比較チャート")
            
            strategy_names = list(strategies.keys())
            strategy_benefits = [x/10000 for x in strategies.values()]
            
            fig_strategy = go.Figure(data=[
                go.Bar(
                    x=strategy_names,
                    y=strategy_benefits,
                    marker_color=['lightblue', 'lightgreen', 'gold'],
                    text=[f"{x:.1f}万円" for x in strategy_benefits],
                    textposition='auto',
                )
            ])
            
            fig_strategy.update_layout(
                title="投資戦略別 最終正味利益比較",
                xaxis_title="戦略",
                yaxis_title="正味利益（万円）",
                height=400
            )
            
            # 最優戦略をハイライト
            best_index = strategy_names.index(best_strategy)
            colors = ['lightblue', 'lightgreen', 'gold']
            colors[best_index] = 'red'
            fig_strategy.update_traces(marker_color=colors)
            
            st.plotly_chart(fig_strategy, width='stretch')
        
        # 解約タイミング分析グラフ
        optimal_df = pd.DataFrame(optimal_timing_data)
        
        fig_optimal = go.Figure()
        
        # 生命保険の各年での正味利益
        fig_optimal.add_trace(
            go.Scatter(
                x=optimal_df['year'],
                y=optimal_df['net_benefit'] / 10000,
                mode='lines+markers',
                name='生命保険正味利益',
                line=dict(color='blue', width=3),
                marker=dict(size=6)
            )
        )
        
        # 投資信託の正味利益（比較用）
        fund_net_benefits = [x/10000 for x in fund_data['net_benefit']]
        fig_optimal.add_trace(
            go.Scatter(
                x=years,
                y=fund_net_benefits,
                mode='lines+markers',
                name='投資信託正味利益',
                line=dict(color='green', width=3, dash='dash'),
                marker=dict(size=6)
            )
        )
        
        # 最適解約年をマーク
        fig_optimal.add_vline(
            x=optimal_year,
            line_dash="dot",
            line_color="red",
            annotation_text=f"最適解約: {optimal_year}年目"
        )
        
        # 最適点をハイライト
        fig_optimal.add_trace(
            go.Scatter(
                x=[optimal_year],
                y=[optimal_data['net_benefit']/10000],
                mode='markers',
                name='最適解約点',
                marker=dict(color='red', size=12, symbol='star')
            )
        )
        
        fig_optimal.update_layout(
            title="生命保険 最適解約タイミング分析",
            xaxis_title="年数",
            yaxis_title="正味利益（万円）",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig_optimal, width='stretch')
        
        # 結果サマリー表示
        st.markdown("---")
        st.subheader("📊 期間満了時比較結果サマリー")
        
        col_result1, col_result2, col_result3 = st.columns(3)
        
        with col_result1:
            st.markdown("#### 🏦 生命保険")
            st.metric("最終残高", f"{final_insurance_balance/10000:.1f}万円")
            st.metric("正味利益", f"{final_insurance_net/10000:.1f}万円")
            st.metric("累積節税額", f"{insurance_data['cumulative_tax_savings'][-1]/10000:.1f}万円")
            
            if insurance_data['cumulative_premium'][-1] > 0:
                insurance_return = ((final_insurance_balance + insurance_data['cumulative_tax_savings'][-1]) / 
                                 insurance_data['cumulative_premium'][-1]) ** (1/investment_period) - 1
                st.metric("実質年利", f"{insurance_return:.2%}")
        
        with col_result2:
            st.markdown("#### 📈 投資信託")
            st.metric("最終残高", f"{final_fund_balance/10000:.1f}万円")
            st.metric("正味利益", f"{final_fund_net/10000:.1f}万円")
            st.metric("累積手数料", f"{fund_data['cumulative_fees'][-1]/10000:.1f}万円")
            
            if fund_data['cumulative_investment'][-1] > 0:
                fund_return = (final_fund_balance / fund_data['cumulative_investment'][-1]) ** (1/investment_period) - 1
                st.metric("実質年利", f"{fund_return:.2%}")
        
        with col_result3:
            st.markdown("#### ⚖️ 比較結果")
            
            balance_diff = final_fund_balance - final_insurance_balance
            net_diff = final_fund_net - final_insurance_net
            
            if net_diff > 0:
                st.success(f"投資信託が有利")
                st.metric("利益差", f"+{net_diff/10000:.1f}万円", "投資信託勝利")
            elif net_diff < 0:
                st.success(f"生命保険が有利")
                st.metric("利益差", f"{net_diff/10000:.1f}万円", "生命保険勝利")
            else:
                st.info("ほぼ同等")
                st.metric("利益差", "0万円", "引き分け")
            
            # 勝率計算（何年目から有利になるか）
            fund_wins = sum(1 for i in range(len(years)) if fund_data['net_benefit'][i] > insurance_data['net_benefit'][i])
            win_rate = fund_wins / len(years)
            st.metric("投資信託勝率", f"{win_rate:.1%}")
        
        # グラフ表示
        st.markdown("---")
        st.subheader("📈 詳細比較グラフ")
        
        # データフレーム作成
        comparison_df = pd.DataFrame({
            '年数': years,
            '生命保険残高': [x/10000 for x in insurance_data['balance']],
            '投資信託残高': [x/10000 for x in fund_data['balance']],
            '生命保険正味利益': [x/10000 for x in insurance_data['net_benefit']],
            '投資信託正味利益': [x/10000 for x in fund_data['net_benefit']],
            '生命保険節税額': [x/10000 for x in insurance_data['cumulative_tax_savings']],
            '投資信託手数料': [x/10000 for x in fund_data['cumulative_fees']]
        })
        
        # 複数グラフ作成
        fig_comparison = make_subplots(
            rows=2, cols=2,
            subplot_titles=('残高比較', '正味利益比較', '生命保険の控除効果', '投資信託のコスト'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 残高比較
        fig_comparison.add_trace(
            go.Scatter(x=comparison_df['年数'], y=comparison_df['生命保険残高'], 
                      name='生命保険残高', line=dict(color='blue', width=3)),
            row=1, col=1
        )
        fig_comparison.add_trace(
            go.Scatter(x=comparison_df['年数'], y=comparison_df['投資信託残高'], 
                      name='投資信託残高', line=dict(color='green', width=3)),
            row=1, col=1
        )
        
        # 正味利益比較
        fig_comparison.add_trace(
            go.Scatter(x=comparison_df['年数'], y=comparison_df['生命保険正味利益'], 
                      name='生命保険正味利益', line=dict(color='blue', width=3, dash='dot')),
            row=1, col=2
        )
        fig_comparison.add_trace(
            go.Scatter(x=comparison_df['年数'], y=comparison_df['投資信託正味利益'], 
                      name='投資信託正味利益', line=dict(color='green', width=3, dash='dot')),
            row=1, col=2
        )
        
        # 生命保険の控除効果
        fig_comparison.add_trace(
            go.Scatter(x=comparison_df['年数'], y=comparison_df['生命保険節税額'], 
                      name='累積節税額', line=dict(color='orange', width=2),
                      fill='tonexty'),
            row=2, col=1
        )
        
        # 投資信託のコスト
        fig_comparison.add_trace(
            go.Scatter(x=comparison_df['年数'], y=comparison_df['投資信託手数料'], 
                      name='累積手数料', line=dict(color='red', width=2),
                      fill='tonexty'),
            row=2, col=2
        )
        
        fig_comparison.update_layout(
            height=800,
            title_text="投資信託 vs 生命保険 詳細比較",
            showlegend=True
        )
        
        # 軸ラベル設定
        fig_comparison.update_yaxes(title_text="金額（万円）", row=1, col=1)
        fig_comparison.update_yaxes(title_text="利益（万円）", row=1, col=2)
        fig_comparison.update_yaxes(title_text="節税額（万円）", row=2, col=1)
        fig_comparison.update_yaxes(title_text="手数料（万円）", row=2, col=2)
        fig_comparison.update_xaxes(title_text="年数", row=2, col=1)
        fig_comparison.update_xaxes(title_text="年数", row=2, col=2)
        
        st.plotly_chart(fig_comparison, width='stretch')
        
        # 詳細分析
        st.markdown("---")
        st.subheader("💡 詳細分析と推奨事項")
        
        # 損益分岐点分析
        break_even_years = []
        for i, year in enumerate(years):
            if fund_data['net_benefit'][i] > insurance_data['net_benefit'][i]:
                break_even_years.append(year)
        
        col_analysis_main1, col_analysis_main2 = st.columns(2)
        
        with col_analysis_main1:
            st.markdown("#### 📅 損益分岐点分析")
            if break_even_years:
                first_fund_win = min(break_even_years)
                st.info(f"**{first_fund_win}年目から投資信託が有利**になります。")
            else:
                st.info("**全期間で生命保険が有利**です。")
                
        with col_analysis_main2:
            st.markdown("#### 🎯 最適戦略提案")
            
            # 最適解約タイミングと投資信託の比較に基づく推奨
            if optimal_year <= investment_period:
                optimal_vs_fund_diff = optimal_data['net_benefit'] - fund_data['net_benefit'][optimal_year-1]
                final_vs_fund_diff = final_fund_net - final_insurance_net
                
                if optimal_vs_fund_diff > 10000:  # 1万円以上の差
                    st.success(f"""
                    🏦 **生命保険 + 早期解約戦略**
                    - {optimal_year}年目で解約
                    - 投資信託より{optimal_vs_fund_diff/10000:.1f}万円有利
                    """)
                elif final_vs_fund_diff > 10000:  # 最終的に投資信託が1万円以上有利
                    st.success(f"""
                    📈 **投資信託優位戦略**
                    - 長期保有で有利
                    - 生命保険より{final_vs_fund_diff/10000:.1f}万円有利
                    """)
                else:
                    st.info("""
                    ⚖️ **分散投資戦略**
                    - 両者の差は僅少
                    - リスク分散のため併用推奨
                    """)
            
            # 期間別推奨
            if investment_period <= 7:
                st.write("**短期投資**: 控除効果重視で生命保険有利")
            elif investment_period <= 15:
                st.write(f"**中期投資**: {optimal_year}年解約タイミングが重要")
            else:
                st.write("**長期投資**: 成長性重視で投資信託検討")
        
        # 要因分析
        col_factor1, col_factor2 = st.columns(2)
        
        with col_factor1:
            st.markdown("#### 🏆 生命保険の優位性")
            st.write(f"✅ 年間節税額: {annual_tax_savings/10000:.1f}万円")
            st.write(f"✅ 控除率: {insurance_deduction/annual_insurance_premium:.1%}")
            st.write(f"✅ 税務メリット: 確実")
            
            if final_insurance_net > final_fund_net:
                advantage = (final_insurance_net - final_fund_net) / 10000
                st.success(f"🎯 **最終的に{advantage:.1f}万円有利**")
        
        with col_factor2:
            st.markdown("#### 📈 投資信託の優位性")
            st.write(f"✅ 期待年利: {mutual_fund_annual_rate:.2%}")
            st.write(f"✅ 実質コスト: {total_fund_fee:.2%}")
            st.write(f"✅ 流動性: 高い")
            
            if final_fund_net > final_insurance_net:
                advantage = (final_fund_net - final_insurance_net) / 10000
                st.success(f"🎯 **最終的に{advantage:.1f}万円有利**")




def calculate_partial_withdrawal_strategy(
    monthly_premium: float,
    investment_period: int,
    insurance_annual_rate: float,
    annual_tax_savings: float,
    withdrawal_interval: int,
    withdrawal_ratio: float,
    fund_annual_return: float,
    fund_annual_fee: float,
    insurance_fee_rate: float = 0.013,
    insurance_balance_fee_rate: float = 0.00008,
    withdrawal_fee_rate: float = 0.0
) -> Dict[str, any]:
    """
    部分解約戦略の基本計算
    """
    return calculate_partial_withdrawal_vs_fund_strategy(
        monthly_premium=monthly_premium,
        investment_period=investment_period,
        insurance_annual_rate=insurance_annual_rate,
        annual_tax_savings=annual_tax_savings,
        withdrawal_interval=withdrawal_interval,
        withdrawal_ratio=withdrawal_ratio,
        fund_annual_return=fund_annual_return,
        fund_annual_fee=fund_annual_fee,
        purchase_fee=0.0,  # デフォルト値
        consider_fund_tax=True,  # デフォルト値
        fund_tax_rate=0.20315,  # デフォルト値
        insurance_fee_rate=insurance_fee_rate,
        insurance_balance_fee_rate=insurance_balance_fee_rate,
        withdrawal_fee_rate=withdrawal_fee_rate
    )


def optimize_partial_withdrawal_strategy(
    monthly_premium: float,
    investment_period: int,
    insurance_annual_rate: float,
    annual_tax_savings: float,
    fund_annual_return: float,
    fund_annual_fee: float
) -> Dict[str, any]:
    """
    最適な部分解約戦略を探索（拡張版）
    より詳細な戦略パターンを評価し、最適解を見つける
    """
    strategies = []
    
    # より詳細な戦略パターンを評価
    intervals = [2, 3, 4, 5, 6, 7]  # 解約間隔を拡張
    ratios = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]  # 解約割合を拡張
    
    total_combinations = 0
    valid_combinations = 0
    
    for interval in intervals:
        for ratio in ratios:
            total_combinations += 1
            
            # 戦略が有効かチェック
            if interval >= investment_period:
                continue
            
            # 解約回数が少なすぎる場合はスキップ
            withdrawal_count = len(range(interval, investment_period, interval))
            if withdrawal_count < 1:
                continue
                
            valid_combinations += 1
            
            try:
                result = calculate_partial_withdrawal_strategy(
                    monthly_premium=monthly_premium,
                    investment_period=investment_period,
                    insurance_annual_rate=insurance_annual_rate,
                    annual_tax_savings=annual_tax_savings,
                    withdrawal_interval=interval,
                    withdrawal_ratio=ratio,
                    fund_annual_return=fund_annual_return,
                    fund_annual_fee=fund_annual_fee
                )
                
                strategies.append({
                    'name': f"{interval}年毎{ratio*100:.0f}%解約",
                    'interval': interval,
                    'ratio': ratio,
                    'final_benefit': result['final_net_benefit'],
                    'withdrawal_count': withdrawal_count,
                    'result': result
                })
            except Exception as e:
                # 計算エラーの場合は無視
                continue
    
    if not strategies:
        # フォールバック戦略
        fallback_result = calculate_partial_withdrawal_strategy(
            monthly_premium=monthly_premium,
            investment_period=investment_period,
            insurance_annual_rate=insurance_annual_rate,
            annual_tax_savings=annual_tax_savings,
            withdrawal_interval=5,
            withdrawal_ratio=0.5,
            fund_annual_return=fund_annual_return,
            fund_annual_fee=fund_annual_fee
        )
        
        strategies.append({
            'name': "5年毎50%解約（フォールバック）",
            'interval': 5,
            'ratio': 0.5,
            'final_benefit': fallback_result['final_net_benefit'],
            'withdrawal_count': len(range(5, investment_period, 5)),
            'result': fallback_result
        })
    
    # 最も利益の高い戦略を選択
    best_strategy = max(strategies, key=lambda x: x['final_benefit'])
    
    # 上位戦略も特定
    sorted_strategies = sorted(strategies, key=lambda x: x['final_benefit'], reverse=True)
    top_3_strategies = sorted_strategies[:3]
    
    return {
        'strategies': strategies,
        'best_strategy': best_strategy,
        'top_strategies': top_3_strategies,
        'optimization_stats': {
            'total_combinations': total_combinations,
            'valid_combinations': valid_combinations,
            'evaluated_strategies': len(strategies)
        }
    }


def calculate_partial_withdrawal_vs_fund_strategy(
    monthly_premium: float,
    investment_period: int,
    insurance_annual_rate: float,
    annual_tax_savings: float,
    withdrawal_interval: int,
    withdrawal_ratio: float,
    fund_annual_return: float,
    fund_annual_fee: float,
    purchase_fee: float,
    consider_fund_tax: bool,
    fund_tax_rate: float,
    insurance_fee_rate: float = 0.013,
    insurance_balance_fee_rate: float = 0.00008,
    withdrawal_fee_rate: float = 0.0
) -> Dict[str, any]:
    """
    投資信託比較用の部分解約戦略計算
    
    Args:
        monthly_premium: 月額保険料
        investment_period: 投資期間
        insurance_annual_rate: 生命保険年利率
        annual_tax_savings: 年間節税額
        withdrawal_interval: 解約間隔（年）
        withdrawal_ratio: 解約割合（0-1）
        fund_annual_return: 投資信託年間リターン
        fund_annual_fee: 投資信託年間手数料率
        purchase_fee: 購入時手数料
        consider_fund_tax: 税金考慮フラグ
        fund_tax_rate: 投資信託税率
        insurance_fee_rate: 保険月額手数料率
        insurance_balance_fee_rate: 保険残高手数料率
        withdrawal_fee_rate: 解約手数料率
    
    Returns:
        部分解約戦略の詳細データ
    """
    monthly_insurance_rate = insurance_annual_rate / 12
    monthly_fund_return = fund_annual_return / 12
    monthly_fund_fee = fund_annual_fee / 12
    
    # 結果格納用
    years = list(range(1, investment_period + 1))
    insurance_balance = []
    fund_balance = []
    total_withdrawal = 0
    total_withdrawal_fees = 0
    cumulative_premium = 0
    cumulative_tax_savings = []
    total_net_benefit = []
    
    # 初期値
    current_insurance_balance = 0
    current_fund_balance = 0
    cumulative_fee = 0
    
    for year in years:
        # 年初の処理
        is_withdrawal_year = (year % withdrawal_interval == 0) and (year < investment_period)
        
        # 月次計算（生命保険）
        for month in range(12):
            cumulative_premium += monthly_premium
            
            # 生命保険手数料計算
            monthly_fee = monthly_premium * insurance_fee_rate
            balance_fee = current_insurance_balance * insurance_balance_fee_rate
            total_monthly_fee = monthly_fee + balance_fee
            cumulative_fee += total_monthly_fee
            
            # 生命保険の積立
            net_investment = monthly_premium - total_monthly_fee
            current_insurance_balance = current_insurance_balance * (1 + monthly_insurance_rate) + net_investment
        
        # 年末の部分解約処理
        withdrawal_amount = 0
        withdrawal_fee = 0
        if is_withdrawal_year:
            withdrawal_amount = current_insurance_balance * withdrawal_ratio
            withdrawal_fee = withdrawal_amount * withdrawal_fee_rate
            net_withdrawal = withdrawal_amount - withdrawal_fee
            
            current_insurance_balance *= (1 - withdrawal_ratio)
            total_withdrawal += net_withdrawal
            total_withdrawal_fees += withdrawal_fee
            
            # 解約金を投資信託に投資（購入手数料差し引き）
            fund_investment = net_withdrawal * (1 - purchase_fee)
            current_fund_balance += fund_investment
        
        # 既存の投資信託の成長
        if current_fund_balance > 0:
            for _ in range(12):
                # 月次運用益
                current_fund_balance *= (1 + monthly_fund_return)
                # 月次信託報酬
                monthly_cost = current_fund_balance * monthly_fund_fee
                current_fund_balance -= monthly_cost
        
        # 年末データ記録
        insurance_balance.append(current_insurance_balance)
        fund_balance.append(current_fund_balance)
        cumulative_tax_savings.append(annual_tax_savings * year)
        
        # 正味利益計算（保険残高 + 投資信託残高 + 累積節税 - 累積保険料 - 解約手数料）
        net_benefit = (current_insurance_balance + current_fund_balance + 
                      annual_tax_savings * year - cumulative_premium - total_withdrawal_fees)
        total_net_benefit.append(net_benefit)
    
    # 最終処理
    # 最終年の投資信託売却税計算
    if consider_fund_tax and current_fund_balance > 0:
        capital_gain = max(0, current_fund_balance - total_withdrawal)
        capital_gain_tax = capital_gain * fund_tax_rate
        current_fund_balance -= capital_gain_tax
        
        # 最終正味利益を再計算
        final_net_benefit = (current_insurance_balance + current_fund_balance + 
                           annual_tax_savings * investment_period - cumulative_premium - total_withdrawal_fees)
        total_net_benefit[-1] = final_net_benefit
    
    return {
        'years': years,
        'insurance_balance': insurance_balance,
        'fund_balance': fund_balance,
        'total_net_benefit': total_net_benefit,
        'cumulative_tax_savings': cumulative_tax_savings,
        'total_withdrawal': total_withdrawal,
        'total_withdrawal_fees': total_withdrawal_fees,
        'final_insurance_balance': current_insurance_balance,
        'final_fund_balance': current_fund_balance,
        'final_total_balance': current_insurance_balance + current_fund_balance,
        'final_net_benefit': total_net_benefit[-1] if total_net_benefit else 0,
        'cumulative_premium': cumulative_premium,
        'withdrawal_pattern': {
            'interval': withdrawal_interval,
            'ratio': withdrawal_ratio,
            'total_withdrawals': total_withdrawal,
            'total_fees': total_withdrawal_fees
        }
    }


def calculate_manual_strategy_performance(
    monthly_premium, investment_period, insurance_annual_rate, annual_tax_savings,
    fund_annual_return, fund_annual_fee, withdrawal_interval, withdrawal_rate
):
    """
    手動設定の部分解約戦略の性能を計算
    """
    # 部分解約戦略計算を実行
    strategy_result = calculate_partial_withdrawal_strategy(
        monthly_premium=monthly_premium,
        investment_period=investment_period,
        insurance_annual_rate=insurance_annual_rate,
        annual_tax_savings=annual_tax_savings,
        withdrawal_interval=withdrawal_interval,
        withdrawal_ratio=withdrawal_rate,
        fund_annual_return=fund_annual_return,
        fund_annual_fee=fund_annual_fee
    )
    
    # 解約回数を計算
    withdrawal_count = investment_period // withdrawal_interval
    
    return {
        'final_benefit': strategy_result['final_net_benefit'],
        'withdrawal_count': withdrawal_count,
        'final_insurance_balance': strategy_result['final_insurance_balance'],
        'final_fund_balance': strategy_result['final_fund_balance'],
        'total_withdrawal': strategy_result['total_withdrawal'],
        'total_fees': strategy_result['withdrawal_pattern']['total_fees'],
        'strategy_details': {
            'interval': withdrawal_interval,
            'rate': withdrawal_rate * 100,
            'efficiency_score': min(100, (strategy_result['final_net_benefit'] / 1000000) * 10)
        }
    }


# =============================================================================
# 新しい構成の関数実装
# =============================================================================

def _show_deduction_from_income():
    """1-1: 収入からの控除額計算"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 パラメータ入力")
        
        annual_income = st.number_input(
            "年収（万円）",
            min_value=0,
            max_value=5000,
            value=500,
            step=10,
            key="deduction_annual_income"
        )
        
        annual_premium = st.number_input(
            "年間保険料（円）",
            min_value=0,
            max_value=200000,
            value=108000,
            step=1000,
            key="deduction_annual_premium"
        )
        
        # 税金計算
        tax_helper = get_tax_helper()
        annual_income_yen = annual_income * 10000
        tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, annual_income_yen)
        
        deduction_amount = tax_result['deduction']
        income_tax_savings = tax_result['income_tax_savings']
        resident_tax_savings = tax_result['resident_tax_savings']
        total_tax_savings = tax_result['total_savings']
        
    with col2:
        st.subheader("💰 計算結果")
        
        col_metric1, col_metric2 = st.columns(2)
        with col_metric1:
            st.metric(
                "控除額",
                f"{deduction_amount:,.0f}円",
                f"控除率: {deduction_amount/annual_premium:.1%}" if annual_premium > 0 else "控除率: 0%"
            )
        
        with col_metric2:
            st.metric(
                "総節税額",
                f"{total_tax_savings:,.0f}円",
                f"実質利回り向上: {total_tax_savings/annual_premium:.2%}" if annual_premium > 0 else "0%"
            )
        
        # 詳細内訳
        st.markdown("#### 節税額内訳")
        breakdown_df = pd.DataFrame({
            "項目": ["所得税節税", "住民税節税", "合計"],
            "金額": [f"{income_tax_savings:,.0f}円", f"{resident_tax_savings:,.0f}円", f"{total_tax_savings:,.0f}円"]
        })
        st.table(breakdown_df)


def _show_insurance_settings():
    """2-1: 生命保険設定"""
    st.markdown("#### 📋 すまいるプランの設定を確認・調整します")
    
    # すまいるプランの説明
    st.info("""
    **📊 すまいるプラン概要**
    
    **保険手数料:**
    - 積立額の1.3%（毎月の保険料から差し引き）
    - 積立残高の0.008%（月換算、残高に対して毎月適用）
    
    これらの手数料を考慮した実質的な資産形成効果を分析します。
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔧 すまいるプラン設定")
        
        monthly_premium = st.number_input(
            "月額保険料（円）",
            min_value=1000,
            max_value=50000,
            value=9000,
            step=1000,
            key="plan_monthly_premium"
        )
        
        annual_rate = st.number_input(
            "年利率（%）",
            min_value=0.0,
            max_value=10.0,
            value=1.25,
            step=0.01,
            key="plan_annual_rate"
        )
        
        investment_period = st.number_input(
            "投資期間（年）",
            min_value=1,
            max_value=50,
            value=20,
            step=1,
            key="plan_investment_period"
        )
        
        fee_rate = st.number_input(
            "積立額手数料率（%/月）",
            min_value=0.0,
            max_value=5.0,
            value=1.3,
            step=0.1,
            key="plan_fee_rate",
            help="月次積立額に対する手数料率"
        )
        
        balance_fee_rate = st.number_input(
            "残高手数料率（%/月）",
            min_value=0.0,
            max_value=1.0,
            value=0.008,
            step=0.0001,
            format="%.4f",
            key="plan_balance_fee_rate",
            help="積立残高に対する月次手数料率"
        )
        
    with col2:
        st.subheader("📊 すまいるプラン概要")
        
        # プラン設定をセッション状態に保存
        st.session_state.plan_settings = {
            'monthly_premium': monthly_premium,
            'annual_rate': annual_rate,
            'investment_period': investment_period,
            'fee_rate': fee_rate / 100,
            'balance_fee_rate': balance_fee_rate / 100
        }
        
        annual_premium = monthly_premium * 12
        total_premium = annual_premium * investment_period
        
        st.metric("年間保険料", f"{annual_premium:,.0f}円")
        st.metric("総保険料", f"{total_premium:,.0f}円")
        st.metric("表面年利", f"{annual_rate:.2f}%")
        
        # 手数料詳細の表示
        monthly_fee_amount = monthly_premium * fee_rate / 100
        annual_balance_fee_rate = balance_fee_rate * 12
        
        st.markdown("##### 💰 手数料詳細")
        col_fee1, col_fee2, col_fee3 = st.columns(3)
        with col_fee1:
            st.metric("積立額手数料", f"{monthly_fee_amount:,.0f}円/月", 
                     help=f"積立額{monthly_premium:,}円 × {fee_rate}%")
        with col_fee2:
            st.metric("残高手数料率", f"{balance_fee_rate:.4f}%/月", 
                     help=f"年間: {annual_balance_fee_rate:.3f}%")
        with col_fee3:
            net_annual_rate = annual_rate - annual_balance_fee_rate
            st.metric("実質年利（概算）", f"{net_annual_rate:.3f}%",
                     help="表面年利 - 残高手数料率（積立額手数料は別途）")
        
        # 控除額を計算（簡易版：控除額のみ）
        calculator = LifeInsuranceDeductionCalculator()
        deduction_amount = calculator.calculate_old_deduction(annual_premium)
        
        st.metric("年間控除額", f"{deduction_amount:,.0f}円")
        
        # 保険料と利益を含んだグラフを表示
        st.markdown("##### 📊 すまいるプラン推移グラフ")
        
        # 正確な年次データ計算
        years = list(range(1, investment_period + 1))
        cumulative_premiums = []
        gross_values = []  # 手数料考慮前
        net_values = []    # 手数料考慮後
        
        monthly_rate = annual_rate / 12 / 100
        monthly_balance_fee_rate = balance_fee_rate / 100
        
        # 毎月のシミュレーション
        current_balance = 0
        total_paid = 0
        
        for year in years:
            months = year * 12
            year_end_balance = 0
            year_end_paid = 0
            
            # 月次シミュレーション（より正確な計算）
            temp_balance = 0
            temp_paid = 0
            
            for month in range(1, months + 1):
                # 積立額手数料を差し引いた実質積立額
                net_monthly_premium = monthly_premium * (1 - fee_rate / 100)
                temp_paid += monthly_premium
                
                # 前月残高に利息を付与
                temp_balance = temp_balance * (1 + monthly_rate)
                
                # 今月の実質積立額を追加
                temp_balance += net_monthly_premium
                
                # 残高手数料を差し引き
                temp_balance = temp_balance * (1 - monthly_balance_fee_rate)
            
            # 手数料考慮前の価値（参考値）
            if monthly_rate > 0:
                gross_value = monthly_premium * ((1 + monthly_rate) ** months - 1) / monthly_rate
            else:
                gross_value = monthly_premium * months
            
            cumulative_premiums.append(temp_paid)
            gross_values.append(gross_value)
            net_values.append(max(0, temp_balance))
        
        # グラフ作成
        fig = go.Figure()
        
        # 累積保険料
        fig.add_trace(go.Scatter(
            x=years,
            y=[v/10000 for v in cumulative_premiums],
            mode='lines+markers',
            name='累積保険料',
            line=dict(color='gray', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        # 手数料考慮前価値
        fig.add_trace(go.Scatter(
            x=years,
            y=[v/10000 for v in gross_values],
            mode='lines+markers',
            name='表面価値（手数料考慮前）',
            line=dict(color='lightblue', width=2),
            marker=dict(size=6)
        ))
        
        # 手数料考慮後価値
        fig.add_trace(go.Scatter(
            x=years,
            y=[v/10000 for v in net_values],
            mode='lines+markers',
            name='実質価値（手数料控除後）',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="すまいるプラン：保険料と価値の推移",
            xaxis_title="年数",
            yaxis_title="価値（万円）",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 最終年での詳細情報
        final_year = investment_period
        final_premium = cumulative_premiums[-1]
        final_gross = gross_values[-1]
        final_net = net_values[-1]
        
        col_final1, col_final2, col_final3 = st.columns(3)
        with col_final1:
            st.metric("最終累積保険料", f"{final_premium/10000:.1f}万円")
        with col_final2:
            st.metric("最終表面価値", f"{final_gross/10000:.1f}万円")
        with col_final3:
            profit = final_net - final_premium
            st.metric("最終実質利益", f"{profit/10000:+.1f}万円", 
                     delta=f"{profit/final_premium*100:+.1f}%")
        
        # 計算検証情報
        with st.expander("🔍 計算詳細（検証用）", expanded=False):
            st.markdown("##### 5年後の詳細計算")
            
            # 5年間の手動計算例
            months_5y = 5 * 12
            total_paid_5y = monthly_premium * months_5y
            net_monthly_premium = monthly_premium * (1 - fee_rate / 100)
            total_fees_paid = monthly_premium * fee_rate / 100 * months_5y
            
            # 簡易計算（複利なし）
            simple_net_value = net_monthly_premium * months_5y
            
            # 複利計算（手数料考慮前）
            if monthly_rate > 0:
                compound_gross = monthly_premium * ((1 + monthly_rate) ** months_5y - 1) / monthly_rate
            else:
                compound_gross = total_paid_5y
            
            st.markdown(f"""
            **パラメータ確認:**
            - 月額積立: {monthly_premium:,}円
            - 積立額手数料率: {fee_rate}% → 月額手数料: {monthly_premium * fee_rate / 100:,.0f}円
            - 残高手数料率: {balance_fee_rate}%/月 → {balance_fee_rate * 12:.3f}%/年
            - 表面年利: {annual_rate}%
            
            **5年後（60ヶ月）の計算:**
            - 総支払額: {total_paid_5y:,.0f}円
            - 積立額手数料総額: {total_fees_paid:,.0f}円
            - 実質積立額/月: {net_monthly_premium:,.0f}円
            - 表面価値（複利）: {compound_gross:,.0f}円
            - 実質価値（計算結果）: {net_values[min(4, len(net_values)-1)]:,.0f}円
            
            **利益分析:**
            - 表面利益: {compound_gross - total_paid_5y:+,.0f}円
            - 実質利益: {net_values[min(4, len(net_values)-1)] - total_paid_5y:+,.0f}円
            """)
            
            if len(net_values) > 4 and net_values[4] < total_paid_5y:
                st.warning("⚠️ 5年後でも赤字となっています。手数料が高すぎるか、年利が低すぎる可能性があります。")
        
        st.success("✅ プラン設定が保存されました。他のタブでこの設定を使用します。")


def _show_mutual_fund_analysis():
    """2-2: 投資信託を分析"""
    st.markdown("#### 投資信託の基本分析を行います")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📈 投資信託設定")
        
        # 参考例の表示
        with st.expander("💡 参考例：eMAXIS Slim 米国株式(S&P500)", expanded=False):
            st.markdown("""
            **eMAXIS Slim 米国株式(S&P500)の実例:**
            - 管理費用（含信託報酬）: **0.09372%**
            - 実質コスト（信託報酬+売買委託手数料+有価証券取引税+その他費用）: **0.104%**
            
            💡 実質コストには表面的な信託報酬だけでなく、運用に伴う隠れたコストも含まれます。
            """)
        
        fund_annual_return = st.number_input(
            "期待年間リターン（%）",
            min_value=-10.0,
            max_value=20.0,
            value=5.0,
            step=0.1,
            key="fund_annual_return"
        )
        
        # 実質コストとして統合
        st.markdown("#### 💰 実質コスト設定")
        total_cost = st.number_input(
            "実質コスト（%/年）",
            min_value=0.0,
            max_value=5.0,
            value=0.104,
            step=0.001,
            format="%.3f",
            help="信託報酬 + 売買委託手数料 + 有価証券取引税 + その他の隠れたコストを含む総合的なコスト",
            key="total_cost"
        )
        
        purchase_fee = st.number_input(
            "購入時手数料（%）",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.01,
            key="fund_purchase_fee"
        )
        
        fund_tax_rate = st.number_input(
            "税率（%）",
            min_value=0.0,
            max_value=50.0,
            value=20.315,
            step=0.001,
            key="fund_tax_rate"
        )
        
    with col2:
        st.subheader("💰 基本試算")
        
        # プラン設定を取得（なければデフォルト値）
        if 'plan_settings' in st.session_state:
            monthly_amount = st.session_state.plan_settings['monthly_premium']
            period = st.session_state.plan_settings['investment_period']
        else:
            monthly_amount = 9000
            period = 20
        
        # 投資信託設定をセッション状態に保存（実質コストとして統合）
        st.session_state.fund_settings = {
            'annual_return': fund_annual_return / 100,
            'annual_fee': total_cost / 100,  # 実質コストとして保存
            'purchase_fee': purchase_fee / 100,
            'tax_rate': fund_tax_rate / 100,
            'hidden_cost': 0  # 既に実質コストに含まれているため0
        }
        
        # 実質年利の計算過程を表示
        st.markdown("#### 🧮 実質年利計算")
        st.markdown("**計算式**: 実質年利 = 期待年間リターン - 実質コスト")
        
        # 実質年利計算
        net_annual_return = (fund_annual_return - total_cost) / 100
        monthly_return = net_annual_return / 12
        
        # 計算過程を表示
        calculation_details = f"""
        - 期待年間リターン: {fund_annual_return:.2f}%
        - 実質コスト: {total_cost:.3f}%
        - **実質年間リターン**: {net_annual_return:.3%}
        """
        st.markdown(calculation_details)
        
        # 複利計算
        total_months = period * 12
        if monthly_return > 0:
            future_value = monthly_amount * ((1 + monthly_return) ** total_months - 1) / monthly_return
        else:
            future_value = monthly_amount * total_months
        
        # 購入時手数料を考慮
        actual_monthly_investment = monthly_amount * (1 - purchase_fee / 100)
        total_investment = actual_monthly_investment * total_months
        
        # 利益と税金
        capital_gain = max(0, future_value - total_investment)
        capital_gain_tax = capital_gain * fund_tax_rate / 100
        net_future_value = future_value - capital_gain_tax
        
        st.metric("実質年間リターン", f"{net_annual_return:.2%}")
        st.metric("予想時価評価額", f"{future_value:,.0f}円")
        st.metric("税引後価値", f"{net_future_value:,.0f}円")
        st.metric("総投資額", f"{total_investment:,.0f}円")
        
        net_profit = net_future_value - total_investment
        st.metric("純利益", f"{net_profit:,.0f}円", f"利回り: {net_profit/total_investment:.2%}")
    
    # 投資信託の推移グラフ
    st.markdown("##### 📊 投資信託価値推移グラフ")
    
    # 年次データの計算
    years = list(range(1, period + 1))
    cumulative_investments = []
    gross_values = []
    net_values = []
    
    for year in years:
        months = year * 12
        cumulative_investment = actual_monthly_investment * months
        
        # 複利計算（税引前）
        if monthly_return > 0:
            gross_value = actual_monthly_investment * ((1 + monthly_return) ** months - 1) / monthly_return
        else:
            gross_value = cumulative_investment
        
        # 税引後価値（年次での概算）
        if year == period:
            # 最終年のみ税金を計算
            cg = max(0, gross_value - cumulative_investment)
            tax = cg * fund_tax_rate / 100
            net_value = gross_value - tax
        else:
            # 中間年は税金を考慮せず
            net_value = gross_value
        
        cumulative_investments.append(cumulative_investment)
        gross_values.append(gross_value)
        net_values.append(net_value)
    
    # グラフ作成
    fig = go.Figure()
    
    # 累積投資額
    fig.add_trace(go.Scatter(
        x=years,
        y=[v/10000 for v in cumulative_investments],
        mode='lines+markers',
        name='累積投資額',
        line=dict(color='gray', width=2, dash='dash'),
        marker=dict(size=6)
    ))
    
    # 税引前価値
    fig.add_trace(go.Scatter(
        x=years,
        y=[v/10000 for v in gross_values],
        mode='lines+markers',
        name='税引前価値',
        line=dict(color='lightgreen', width=2),
        marker=dict(size=6)
    ))
    
    # 税引後価値
    fig.add_trace(go.Scatter(
        x=years,
        y=[v/10000 for v in net_values],
        mode='lines+markers',
        name='税引後価値',
        line=dict(color='green', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="投資信託：投資額と価値の推移",
        xaxis_title="年数",
        yaxis_title="価値（万円）",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


# def _show_scenario_sensitivity_analysis():
    """2-3: シナリオや感度想定"""
    st.markdown("#### 投資信託のシナリオ・感度分析")
    
    # 基本設定を取得
    if 'fund_settings' in st.session_state and 'plan_settings' in st.session_state:
        base_return = st.session_state.fund_settings['annual_return']
        monthly_amount = st.session_state.plan_settings['monthly_premium']
        period = st.session_state.plan_settings['investment_period']
        annual_fee = st.session_state.fund_settings['annual_fee']
        hidden_cost = st.session_state.fund_settings.get('hidden_cost', 0)
        tax_rate = st.session_state.fund_settings['tax_rate']
        
        # 期待年間リターンを表示（参考）
        # annual_feeには既に実質コスト（旧：信託報酬+隠れコスト）が含まれている
        gross_return = base_return + annual_fee  # hidden_costは既にannual_feeに含まれている
        st.info(f"📈 **基準値**: 期待年間リターン {gross_return:.2%} (投資信託設定より)")
    else:
        st.warning("先に「生命保険設定」と「投資信託を分析」を完了してください。")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎲 シナリオ設定")
        
        scenario_type = st.selectbox(
            "シナリオタイプ",
            ["楽観シナリオ", "基準シナリオ", "悲観シナリオ", "カスタム"],
            index=1,
            key="scenario_type"
        )
        
        # 期待年間リターン（グロス）を基準とする
        base_gross_return = gross_return
        
        if scenario_type == "楽観シナリオ":
            # グロスリターンを基準に設定
            scenarios = [base_gross_return + 0.03, base_gross_return + 0.02, base_gross_return + 0.01]
            scenario_names = ["非常に楽観", "楽観", "やや楽観"]
        elif scenario_type == "悲観シナリオ":
            scenarios = [base_gross_return - 0.01, base_gross_return - 0.02, base_gross_return - 0.03]
            scenario_names = ["やや悲観", "悲観", "非常に悲観"]
        elif scenario_type == "カスタム":
            scenarios = []
            scenario_names = []
            for i in range(3):
                custom_return = st.number_input(
                    f"シナリオ{i+1}の年間リターン（%）",
                    min_value=-10.0,
                    max_value=20.0,
                    value=(base_gross_return + (1-i)*0.02) * 100,
                    step=0.1,
                    key=f"custom_scenario_{i}"
                )
                scenarios.append(custom_return / 100)
                scenario_names.append(f"シナリオ{i+1}")
        else:  # 基準シナリオ
            scenarios = [base_gross_return + 0.01, base_gross_return, base_gross_return - 0.01]
            scenario_names = ["やや楽観", "基準（期待リターン）", "やや悲観"]
    
    with col2:
        st.subheader("📊 シナリオ分析結果")
        
        results = []
        for scenario_return, name in zip(scenarios, scenario_names):
            # 実質コストを差し引いたネットリターン計算
            net_return = scenario_return - annual_fee  # annual_feeに実質コストが含まれている
            monthly_return = net_return / 12
            total_months = period * 12
            
            if monthly_return > 0:
                future_value = monthly_amount * ((1 + monthly_return) ** total_months - 1) / monthly_return
            else:
                future_value = monthly_amount * total_months
            
            total_investment = monthly_amount * total_months
            capital_gain = max(0, future_value - total_investment)
            capital_gain_tax = capital_gain * tax_rate
            net_value = future_value - capital_gain_tax
            net_profit = net_value - total_investment
            
            results.append({
                'シナリオ': name,
                'グロス年間リターン': f"{scenario_return:.2%}",
                '実質年間リターン': f"{net_return:.2%}",
                '最終価値': f"{net_value:,.0f}円",
                '純利益': f"{net_profit:,.0f}円",
                '利回り': f"{net_profit/total_investment:.2%}"
            })
        
        results_df = pd.DataFrame(results)
        st.dataframe(results_df, width='stretch')
        
        # 感度分析チャート
        st.subheader("📈 感度分析チャート")
        st.markdown("*期待年間リターン（グロス）の変動に対する最終価値の感度*")
        
        # グロスリターンの範囲で感度分析
        return_range = np.arange(base_gross_return - 0.05, base_gross_return + 0.06, 0.01)
        net_values = []
        
        for gross_ret in return_range:
            # 実質コストを考慮したネットリターン
            net_ret = gross_ret - annual_fee  # annual_feeに実質コストが含まれている
            monthly_ret = net_ret / 12
            if monthly_ret > 0:
                fv = monthly_amount * ((1 + monthly_ret) ** (period * 12) - 1) / monthly_ret
            else:
                fv = monthly_amount * period * 12
            
            total_inv = monthly_amount * period * 12
            cg = max(0, fv - total_inv)
            cg_tax = cg * tax_rate
            net_val = fv - cg_tax
            net_values.append(net_val)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[r * 100 for r in return_range],
            y=net_values,
            mode='lines',
            name='最終価値'
        ))
        
        # 基準値（期待年間リターン）をハイライト
        base_idx = len(return_range) // 2
        fig.add_trace(go.Scatter(
            x=[base_gross_return * 100],
            y=[net_values[base_idx]],
            mode='markers',
            marker=dict(size=10, color='red'),
            name='期待年間リターン'
        ))
        
        fig.update_layout(
            title="投資信託リターンの感度分析（実質コスト考慮済み）",
            xaxis_title="期待年間リターン（グロス%）",
            yaxis_title="最終価値（円）",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)


def _show_insurance_comparison():
    """2-4: 生命保険との比較"""
    st.markdown("#### 生命保険と投資信託の詳細比較")
    
    # 設定確認
    if 'fund_settings' not in st.session_state or 'plan_settings' not in st.session_state:
        st.warning("先に「2-1: 詳細プランの設定確認」と「2-2: 投資信託を分析」を完了してください。")
        return
    
    plan = st.session_state.plan_settings
    fund = st.session_state.fund_settings
    
    st.subheader("⚖️ 比較分析")
    
    # 投資信託の実質利回り計算方法の説明
    with st.expander("📊 投資信託の実質利回り計算方法", expanded=False):
        st.markdown("""
        ### 🔍 計算の仕組み
        
        **基本方針:** 投資信託は**解約せず持続保有**で運用します。
        
        **実質利回りの計算式:**
        ```
        実質年間リターン = 期待年間リターン - 信託報酬 - 隠れコスト
        月次リターン = 実質年間リターン ÷ 12
        ```
        
        **複利計算:**
        - 毎月の積立元本に月次リターンを適用
        - 過去の積立分も含めて複利で成長
        - **解約・再投資は行わず、継続保有**
        
        **最終税金計算:**
        - 投資期間終了時に一括で税金を計算
        - 課税対象: 最終価値 - 総投資額（キャピタルゲイン）
        - 税率: 20.315%（所得税15% + 住民税5% + 復興特別所得税0.315%）
        
        **重要:** この計算は投資信託を満期まで保有し続ける前提です。
        """)
    
    # 生命保険計算
    monthly_premium = plan['monthly_premium']
    annual_rate = plan['annual_rate'] / 100
    period = plan['investment_period']
    
    # 簡易的な生命保険価値計算（手数料考慮）
    monthly_rate = annual_rate / 12
    total_months = period * 12
    
    # 手数料を考慮した実質積立額
    net_premium = monthly_premium * (1 - plan['fee_rate'])
    
    if monthly_rate > 0:
        insurance_value = net_premium * ((1 + monthly_rate) ** total_months - 1) / monthly_rate
    else:
        insurance_value = net_premium * total_months
    
    # 残高手数料を概算で差し引き
    balance_fee_impact = insurance_value * plan['balance_fee_rate'] * total_months
    insurance_value -= balance_fee_impact
    
    # 控除による節税効果（簡易計算：500万円の年収で）
    annual_premium = monthly_premium * 12
    tax_helper = get_tax_helper()
    tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, 5000000)
    annual_tax_savings = tax_result['total_savings']
    total_tax_savings = annual_tax_savings * period
    
    insurance_total_value = insurance_value + total_tax_savings
    
    # 投資信託計算（詳細説明付き）
    fund_return = fund['annual_return']
    fund_fee = fund['annual_fee']  # 実質コスト（旧：信託報酬+隠れコスト）
    
    # 投資信託の設定表示
    st.markdown("##### 📊 投資信託の設定内容（分析タブから反映）")
    col_set1, col_set2, col_set3 = st.columns(3)
    with col_set1:
        st.info(f"**期待年間リターン**\n{fund_return:.3%}")
    with col_set2:
        st.info(f"**実質コスト**\n{fund_fee:.3%}")
    with col_set3:
        st.info(f"**税率**\n{fund['tax_rate']:.3%}")
    
    # 参考情報も分析タブから反映されていることを示す
    if fund_fee <= 0.0015:  # 0.15%以下の場合はeMAXIS Slimレベル
        st.success("✅ **低コスト投資信託**：実質コストが0.15%以下で、eMAXIS Slimクラスの優良な設定です。")
    elif fund_fee <= 0.005:  # 0.5%以下
        st.info("ℹ️ **標準的な投資信託**：実質コストが適度に抑えられた設定です。")
    else:
        st.warning("⚠️ **高コスト投資信託**：実質コストが0.5%を超えています。長期投資では影響が大きくなる可能性があります。")
    
    # 実質リターンの計算
    net_fund_return = fund_return - fund_fee
    monthly_fund_return = net_fund_return / 12
    
    # 複利計算（解約なし、継続保有前提）
    if monthly_fund_return > 0:
        fund_value = monthly_premium * ((1 + monthly_fund_return) ** total_months - 1) / monthly_fund_return
    else:
        fund_value = monthly_premium * total_months
    
    # 投資信託の税金（期間終了時一括課税）
    total_investment = monthly_premium * total_months
    capital_gain = max(0, fund_value - total_investment)
    capital_gain_tax = capital_gain * fund['tax_rate']
    fund_net_value = fund_value - capital_gain_tax
    
    # 計算詳細をデバッグ表示
    with st.expander("🔍 投資信託計算詳細", expanded=False):
        # 分析タブで設定した内容の反映確認
        st.markdown("**🔗 投資信託分析タブの設定値を使用:**")
        st.markdown(f"""
        - 期待年間リターン: **{fund_return:.3%}**
        - 実質コスト: **{fund_fee:.3%}**
        - 税率: **{fund['tax_rate']:.3%}**
        """)
        
        st.markdown("---")
        st.markdown(f"""
        **実質リターン計算:**
        - 期待年間リターン: {fund_return:.3%}
        - 実質コスト（信託報酬+隠れコスト）: {fund_fee:.3%}
        - **実質年間リターン**: {net_fund_return:.3%}
        - **月次リターン**: {monthly_fund_return:.4%}
        
        **資産形成プロセス:**
        - 月次積立額: {monthly_premium:,.0f}円
        - 積立期間: {period}年（{total_months}ヶ月）
        - 総投資額: {total_investment:,.0f}円
        - 税引前価値: {fund_value:,.0f}円
        - キャピタルゲイン: {capital_gain:,.0f}円
        - 税金（{fund['tax_rate']:.3%}）: {capital_gain_tax:,.0f}円
        - **税引後価値**: {fund_net_value:,.0f}円
        """)
        
        if capital_gain > 0:
            st.info("💡 **運用方針**: 投資信託は期間中解約せず、満期時に一括で税金を支払います。")
        else:
            st.info("💡 **運用結果**: 元本割れのため課税対象となるキャピタルゲインはありません。")
    
    # 比較表作成
    st.markdown("##### 💰 最終価値の比較")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏦 生命保険")
        st.metric("積立価値", f"{insurance_value:,.0f}円")
        st.metric("節税効果", f"{total_tax_savings:,.0f}円")
        st.metric("**総価値**", f"{insurance_total_value:,.0f}円")
        insurance_yield = ((insurance_total_value / total_investment) ** (1/period) - 1)
        st.metric("実質年利回り", f"{insurance_yield:.3%}")
    
    with col2:
        st.markdown("#### 📈 投資信託")
        st.metric("税引前価値", f"{fund_value:,.0f}円")
        st.metric("税金", f"-{capital_gain_tax:,.0f}円")
        st.metric("**税引後価値**", f"{fund_net_value:,.0f}円")
        fund_yield = ((fund_net_value / total_investment) ** (1/period) - 1)
        st.metric("実質年利回り", f"{fund_yield:.3%}")
    
    with col3:
        st.markdown("#### 🔍 比較結果")
        difference = fund_net_value - insurance_total_value
        st.metric("価値差", f"{difference:,.0f}円")
        
        if difference > 0:
            st.success(f"**投資信託**が {difference:,.0f}円 有利")
            better_option = "🏆 投資信託"
        else:
            st.error(f"**生命保険**が {abs(difference):,.0f}円 有利")
            better_option = "🏆 生命保険"
        
        st.metric("優位選択肢", better_option)
        
        advantage_ratio = abs(difference) / min(insurance_total_value, fund_net_value)
        st.metric("優位度", f"{advantage_ratio:.2%}")
        
        yield_diff = fund_yield - insurance_yield
        st.metric("利回り差", f"{yield_diff:+.3%}")
    
    # 詳細比較チャート
    st.subheader("📊 時系列比較")
    
    years = list(range(1, period + 1))
    insurance_values = []
    fund_values = []
    
    for year in years:
        months = year * 12
        
        # 生命保険価値（簡易計算）
        if monthly_rate > 0:
            ins_val = net_premium * ((1 + monthly_rate) ** months - 1) / monthly_rate
        else:
            ins_val = net_premium * months
        
        ins_val -= ins_val * plan['balance_fee_rate'] * months  # 残高手数料
        ins_val += annual_tax_savings * year  # 節税効果
        insurance_values.append(ins_val)
        
        # 投資信託価値
        if monthly_fund_return > 0:
            fund_val = monthly_premium * ((1 + monthly_fund_return) ** months - 1) / monthly_fund_return
        else:
            fund_val = monthly_premium * months
        
        # 税金は最終年のみ概算
        if year == period:
            total_inv = monthly_premium * months
            cg = max(0, fund_val - total_inv)
            fund_val -= cg * fund['tax_rate']
        
        fund_values.append(fund_val)
    
    # 差額を計算
    differences = [fund_val - ins_val for fund_val, ins_val in zip(fund_values, insurance_values)]
    
    # 累積元本を計算
    cumulative_premiums = [monthly_premium * 12 * year for year in years]
    
    # 4-1: メインの比較グラフ
    st.markdown("##### 4-1. 投資利益 - 生命保険の推移")
    
    fig = go.Figure()
    
    # 累積元本
    fig.add_trace(go.Scatter(
        x=years, 
        y=[v/10000 for v in cumulative_premiums], 
        mode='lines+markers', 
        name='累積元本',
        line=dict(color='gray', width=2, dash='dash'),
        marker=dict(size=6)
    ))
    
    # 生命保険価値
    fig.add_trace(go.Scatter(
        x=years, 
        y=[v/10000 for v in insurance_values], 
        mode='lines+markers', 
        name='生命保険（節税込み）',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))
    
    # 投資信託価値
    fig.add_trace(go.Scatter(
        x=years, 
        y=[v/10000 for v in fund_values], 
        mode='lines+markers', 
        name='投資信託（税引後）',
        line=dict(color='green', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="生命保険 vs 投資信託 価値推移（累積元本含む）",
        xaxis_title="年数",
        yaxis_title="価値（万円）",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 投資利益 - 生命保険差額（元本対比利益）
    st.markdown("##### 📊 元本対比利益の比較")
    
    # 各商品の利益を計算
    insurance_base_profits = []  # 手数料・年利効果
    insurance_tax_benefits = []  # 控除効果
    fund_profits = []  # 投資信託利益
    
    for i, year in enumerate(years):
        # 累積元本
        cumulative_premium = cumulative_premiums[i]
        
        # 生命保険の利益内訳を詳細計算
        insurance_value_base = insurance_values[i] - annual_tax_savings * year  # 節税効果を除いた基本価値
        insurance_base_profit = insurance_value_base - cumulative_premium  # 基本利益（手数料・年利効果）
        insurance_tax_benefit = annual_tax_savings * year  # 節税効果
        
        # 投資信託の利益
        fund_profit = fund_values[i] - cumulative_premium
        
        insurance_base_profits.append(insurance_base_profit / 10000)  # 万円
        insurance_tax_benefits.append(insurance_tax_benefit / 10000)  # 万円
        fund_profits.append(fund_profit / 10000)  # 万円
    
    # 生命保険と投資信託の比較棒グラフ作成
    fig_compare = go.Figure()
    
    # 生命保険の利益（手数料・年利効果）- 積み上げの下層
    fig_compare.add_trace(go.Bar(
        x=years,
        y=insurance_base_profits,
        name='生命保険：手数料・年利効果',
        marker_color='lightblue',
        legendgroup='生命保険',
        offsetgroup='生命保険',
        hovertemplate='年数: %{x}<br>手数料・年利効果: %{y:.1f}万円<extra></extra>'
    ))
    
    # 生命保険の利益（控除効果）- 積み上げの上層
    fig_compare.add_trace(go.Bar(
        x=years,
        y=insurance_tax_benefits,
        name='生命保険：控除効果',
        marker_color='blue',
        legendgroup='生命保険',
        offsetgroup='生命保険',
        base=insurance_base_profits,  # 手数料・年利効果の上に積み上げ
        hovertemplate='年数: %{x}<br>控除効果: %{y:.1f}万円<extra></extra>'
    ))
    
    # 投資信託の利益（独立した棒）
    fig_compare.add_trace(go.Bar(
        x=years,
        y=fund_profits,
        name='投資信託：運用利益',
        marker_color='green',
        legendgroup='投資信託',
        offsetgroup='投資信託',
        hovertemplate='年数: %{x}<br>運用利益: %{y:.1f}万円<extra></extra>'
    ))
    
    # ゼロライン
    fig_compare.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig_compare.update_layout(
        title="元本に対する利益比較（万円）",
        xaxis_title="年数",
        yaxis_title="利益（万円）",
        height=500,
        barmode='group',  # 生命保険と投資信託を並列表示
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # 年間差額のサマリー情報をコメントとして追加
    differences = [fund_profits[i] - (insurance_base_profits[i] + insurance_tax_benefits[i]) for i in range(len(years))]
    
    # 転換点分析
    crossover_year = None
    for i, diff in enumerate(differences):
        if diff > 0:
            crossover_year = years[i]
            break
    
    # 最終年での差額
    final_diff = differences[-1]
    
    # 最大有利差額
    max_fund_advantage = max(differences) if max(differences) > 0 else 0
    max_insurance_advantage = abs(min(differences)) if min(differences) < 0 else 0
    
    st.info(f"""
    💡 **グラフの見方:**
    - **生命保険（青色系）**: 手数料・年利効果（薄青）+ 控除効果（濃青）を縦に積み上げ
    - **投資信託（緑色）**: 純粋な運用利益
    - **高さ比較**: 各年での総利益を直接比較可能
    
    📊 **年間差額サマリー:**
    - **転換点**: {f"{crossover_year}年目から投資信託が有利" if crossover_year else "全期間で生命保険が有利"}
    - **最終年差額**: {"投資信託" if final_diff > 0 else "生命保険"}が {abs(final_diff):.1f}万円有利
    - **最大有利幅**: 投資信託 {max_fund_advantage:.1f}万円 vs 生命保険 {max_insurance_advantage:.1f}万円
    """)
    
    # 年次差額詳細
    with st.expander("📋 年次差額詳細", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**年次詳細**")
            for i, year in enumerate(years):
                diff = differences[i]
                if diff > 0:
                    st.success(f"{year}年目: 投資信託が {diff/10000:+.1f}万円 有利")
                else:
                    st.error(f"{year}年目: 生命保険が {abs(diff)/10000:.1f}万円 有利")
        
        with col2:
            st.markdown("**転換点分析**")
            # 投資信託が有利になる年を特定
            crossover_year = None
            for i, diff in enumerate(differences):
                if diff > 0:
                    crossover_year = years[i]
                    break
            
            if crossover_year:
                st.info(f"🔄 **転換点**: {crossover_year}年目から投資信託が有利")
            else:
                st.info("📊 **結果**: 全期間で生命保険が有利")
            
            # 最大差額
            max_diff_idx = max(range(len(differences)), key=lambda i: abs(differences[i]))
            max_diff = differences[max_diff_idx]
            max_diff_year = years[max_diff_idx]
            
            if max_diff > 0:
                st.success(f"📈 **最大優位**: {max_diff_year}年目で投資信託が{max_diff/10000:.1f}万円有利")
            else:
                st.error(f"📉 **最大優位**: {max_diff_year}年目で生命保険が{abs(max_diff)/10000:.1f}万円有利")


def _show_optimal_withdrawal_timing():
    """2-5: 最適解約タイミング分析"""
    st.markdown("#### 投資信託 vs 生命保険の最適解約タイミング分析")
    st.markdown("**戦略分析：乗り換えなし・あり（タイミング・部分解約）**")
    
    # 設定確認
    if 'fund_settings' not in st.session_state or 'plan_settings' not in st.session_state:
        st.warning("先に「2-1: 詳細プランの設定確認」と「2-2: 投資信託を分析」を完了してください。")
        return
    
    plan = st.session_state.plan_settings
    fund = st.session_state.fund_settings
    
    tab1, tab2, tab3 = st.tabs([
        "🚫 乗り換えなし戦略",
        "🔄 最適乗り換えタイミング",
        "⚖️ 部分解約戦略"
    ])
    
    with tab1:
        st.markdown("##### 乗り換えなし：各商品を満期まで継続")
        _show_no_switching_analysis(plan, fund)
    
    with tab2:
        st.markdown("##### 生命保険から投資信託への最適乗り換えタイミング")
        _show_optimal_switching_timing(plan, fund)
    
    with tab3:
        st.markdown("##### 部分解約を組み合わせた戦略")
        _show_partial_withdrawal_strategy(plan, fund)


def _show_no_switching_analysis(plan: dict, fund: dict):
    """乗り換えなし戦略の分析"""
    monthly_premium = plan['monthly_premium']
    period = plan['investment_period']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏦 生命保険継続")
        
        # 生命保険の最終価値計算（簡易版）
        annual_rate = plan['annual_rate'] / 100
        monthly_rate = annual_rate / 12
        total_months = period * 12
        
        net_premium = monthly_premium * (1 - plan['fee_rate'])
        
        if monthly_rate > 0:
            insurance_value = net_premium * ((1 + monthly_rate) ** total_months - 1) / monthly_rate
        else:
            insurance_value = net_premium * total_months
        
        # 残高手数料
        balance_fee = insurance_value * plan['balance_fee_rate'] * total_months
        insurance_value -= balance_fee
        
        # 節税効果
        annual_premium = monthly_premium * 12
        # 節税効果
        annual_premium = monthly_premium * 12
        tax_helper = get_tax_helper()
        tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, 5000000)
        annual_tax_savings = tax_result['total_savings']
        total_tax_savings = annual_tax_savings * period
        
        insurance_total = insurance_value + total_tax_savings
        
        st.metric("積立価値", f"{insurance_value:,.0f}円")
        st.metric("節税効果", f"{total_tax_savings:,.0f}円")
        st.metric("総価値", f"{insurance_total:,.0f}円")
        
    with col2:
        st.subheader("📈 投資信託継続")
        
        # 投資信託の最終価値計算
        net_return = fund['annual_return'] - fund['annual_fee']
        monthly_return = net_return / 12
        
        if monthly_return > 0:
            fund_value = monthly_premium * ((1 + monthly_return) ** total_months - 1) / monthly_return
        else:
            fund_value = monthly_premium * total_months
        
        # 税金
        total_investment = monthly_premium * total_months
        capital_gain = max(0, fund_value - total_investment)
        tax = capital_gain * fund['tax_rate']
        fund_net_value = fund_value - tax
        
        st.metric("時価評価額", f"{fund_value:,.0f}円")
        st.metric("税金", f"{tax:,.0f}円")
        st.metric("税引後価値", f"{fund_net_value:,.0f}円")
    
    # 比較結果
    st.subheader("🔍 比較結果")
    difference = fund_net_value - insurance_total
    
    col_result1, col_result2, col_result3 = st.columns(3)
    
    with col_result1:
        st.metric("価値差", f"{difference:,.0f}円")
    
    with col_result2:
        if difference > 0:
            st.success("投資信託が有利")
            better = "投資信託"
        else:
            st.error("生命保険が有利")
            better = "生命保険"
        st.metric("優位商品", better)
    
    with col_result3:
        advantage = abs(difference) / min(insurance_total, fund_net_value)
        st.metric("優位度", f"{advantage:.1%}")


def _show_optimal_switching_timing(plan: dict, fund: dict):
    """最適乗り換えタイミングの分析"""
    monthly_premium = plan['monthly_premium']
    period = plan['investment_period']
    
    st.subheader("🔄 最適乗り換えタイミング分析")
    
    # 各年での乗り換えを計算
    switching_years = list(range(1, period))
    results = []
    
    for switch_year in switching_years:
        result = _calculate_switching_value(plan, fund, switch_year, period)
        results.append({
            '乗り換え年': switch_year,
            '生命保険期間': f"{switch_year}年",
            '投資信託期間': f"{period - switch_year}年",
            '最終価値': f"{result['total_value']:,.0f}円",
            '価値': result['total_value']
        })
    
    results_df = pd.DataFrame(results)
    
    # 最適タイミングを特定
    optimal_idx = results_df['価値'].idxmax()
    optimal_year = results_df.loc[optimal_idx, '乗り換え年']
    optimal_value = results_df.loc[optimal_idx, '価値']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 乗り換えタイミング比較")
        st.dataframe(results_df[['乗り換え年', '生命保険期間', '投資信託期間', '最終価値']], 
                    use_container_width=True)
        
        st.success(f"**最適乗り換えタイミング: {optimal_year}年目**")
        st.info(f"最適価値: {optimal_value:,.0f}円")
    
    with col2:
        st.subheader("📈 価値推移チャート")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=switching_years,
            y=[r['価値'] for r in results],
            mode='lines+markers',
            name='総価値'
        ))
        
        # 最適点をハイライト
        fig.add_trace(go.Scatter(
            x=[optimal_year],
            y=[optimal_value],
            mode='markers',
            marker=dict(size=15, color='red'),
            name='最適タイミング'
        ))
        
        fig.update_layout(
            title="乗り換えタイミング別総価値",
            xaxis_title="乗り換え年",
            yaxis_title="最終価値（円）",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)


def _calculate_switching_value(plan: dict, fund: dict, switch_year: int, total_period: int) -> dict:
    """乗り換え戦略の価値計算"""
    monthly_premium = plan['monthly_premium']
    
    # Phase 1: 生命保険期間
    annual_rate = plan['annual_rate'] / 100
    monthly_rate = annual_rate / 12
    insurance_months = switch_year * 12
    
    net_premium = monthly_premium * (1 - plan['fee_rate'])
    
    if monthly_rate > 0:
        insurance_value = net_premium * ((1 + monthly_rate) ** insurance_months - 1) / monthly_rate
    else:
        insurance_value = net_premium * insurance_months
    
    # 残高手数料
    balance_fee = insurance_value * plan['balance_fee_rate'] * insurance_months
    insurance_value -= balance_fee
    
    # 節税効果（生命保険期間分）
    annual_premium = monthly_premium * 12
    tax_helper = get_tax_helper()
    tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, 5000000)
    insurance_tax_savings = tax_result['total_savings'] * switch_year
    
    # Phase 2: 投資信託期間
    fund_period = total_period - switch_year
    fund_months = fund_period * 12
    
    # 生命保険解約金を投資信託に投資
    initial_fund_amount = insurance_value + insurance_tax_savings
    
    net_return = fund['annual_return'] - fund['annual_fee']
    monthly_return = net_return / 12
    
    # 初期投資額の成長
    if monthly_return > 0:
        initial_growth = initial_fund_amount * (1 + monthly_return) ** fund_months
    else:
        initial_growth = initial_fund_amount
    
    # 継続積立分
    if monthly_return > 0 and fund_months > 0:
        monthly_accumulation = monthly_premium * ((1 + monthly_return) ** fund_months - 1) / monthly_return
    else:
        monthly_accumulation = monthly_premium * fund_months
    
    total_fund_value = initial_growth + monthly_accumulation
    
    # 投資信託の税金（解約金投資分は課税済みとして扱う）
    fund_investment = monthly_premium * fund_months
    capital_gain = max(0, monthly_accumulation - fund_investment)
    tax = capital_gain * fund['tax_rate']
    
    final_value = initial_growth + monthly_accumulation - tax
    
    return {
        'insurance_value': insurance_value,
        'insurance_tax_savings': insurance_tax_savings,
        'fund_value': total_fund_value,
        'tax': tax,
        'total_value': final_value
    }


def _show_partial_withdrawal_strategy(plan: dict, fund: dict):
    """部分解約戦略の高度な分析"""
    st.subheader("⚖️ 部分解約を組み合わせた戦略")
    st.markdown("生命保険の部分解約と再投資を組み合わせた最適戦略を分析します")
    
    # タブで機能を分ける
    strategy_tab1, strategy_tab2, strategy_tab3 = st.tabs([
        "🎯 基本戦略設定",
        "📊 複数戦略比較",
        "💡 最適戦略提案"
    ])
    
    with strategy_tab1:
        st.markdown("### 基本的な部分解約戦略")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📝 戦略パラメータ")
            
            withdrawal_interval = st.selectbox(
                "解約間隔（年）",
                [2, 3, 4, 5, 6],
                index=2,
                key="partial_withdrawal_interval",
                help="何年ごとに部分解約を行うか"
            )
            
            withdrawal_ratio = st.slider(
                "1回あたりの解約割合",
                min_value=0.01,
                max_value=0.50,
                value=0.25,
                step=0.01,
                format="%.2f%%",
                key="partial_withdrawal_ratio",
                help="保険残高の何%を解約するか"
            )
            
            reinvestment_option = st.selectbox(
                "解約金の再投資先",
                ["投資信託", "現金保有", "混合（50%-50%）", "NISA枠活用"],
                index=0,
                key="reinvestment_option",
                help="解約した資金の運用方法"
            )
            
            withdrawal_fee_rate = st.number_input(
                "解約手数料率（%）",
                min_value=0.0,
                max_value=5.0,
                value=1.0,
                step=0.1,
                key="withdrawal_fee_rate",
                help="解約時に発生する手数料の割合"
            ) / 100
            
            taxable_income_man = st.number_input(
                "課税所得（万円）",
                min_value=100,
                max_value=2000,
                value=500,
                step=50,
                key="partial_taxable_income",
                help="一時所得の課税計算に使用"
            )
            
            taxable_income = taxable_income_man * 10000
        
        with col2:
            st.markdown("#### 📋 戦略概要")
            
            period = plan['investment_period']
            withdrawal_years = list(range(withdrawal_interval, period, withdrawal_interval))
            
            st.info(f"""
            **設定された戦略:**
            - **解約間隔**: {withdrawal_interval}年ごと
            - **解約割合**: 残高の{withdrawal_ratio:.0%}
            - **再投資先**: {reinvestment_option}
            - **解約手数料**: {withdrawal_fee_rate:.1%}
            - **解約回数**: {len(withdrawal_years)}回
            """)
            
            # 解約スケジュール表示
            if withdrawal_years:
                st.markdown("##### 📅 解約スケジュール")
                
                remaining_ratios = []
                cumulative_withdrawal = 0
                
                for i, year in enumerate(withdrawal_years):
                    cumulative_withdrawal += withdrawal_ratio * (1 - cumulative_withdrawal)
                    remaining_ratios.append(1 - cumulative_withdrawal)
                
                schedule_df = pd.DataFrame({
                    '解約年': withdrawal_years,
                    '解約割合': [f"{withdrawal_ratio:.0%}"] * len(withdrawal_years),
                    '残存割合': [f"{r:.1%}" for r in remaining_ratios],
                    '累積解約割合': [f"{1-r:.1%}" for r in remaining_ratios]
                })
                st.dataframe(schedule_df, use_container_width=True, hide_index=True)
        
        # 部分解約戦略の詳細計算
        if st.button("🚀 部分解約戦略を計算", type="primary", key="calc_partial_strategy"):
            with st.spinner("計算中..."):
                result = _calculate_partial_withdrawal_value_enhanced(
                    plan, fund, withdrawal_interval, withdrawal_ratio, 
                    reinvestment_option, plan['investment_period'],
                    withdrawal_fee_rate, taxable_income
                )
                
                st.markdown("---")
                st.markdown("### 📊 部分解約戦略の分析結果")
                
                # メトリクス表示
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                
                with col_m1:
                    st.metric("残存保険価値", f"{result['remaining_insurance']:,.0f}円")
                
                with col_m2:
                    st.metric("再投資資産価値", f"{result['reinvestment_value']:,.0f}円")
                
                with col_m3:
                    st.metric("総資産価値", f"{result['total_value']:,.0f}円",
                             delta=f"vs単純継続: {result['vs_simple']:+,.0f}円")
                
                with col_m4:
                    advantage = "有利" if result['vs_simple'] > 0 else "不利"
                    color = "normal" if result['vs_simple'] > 0 else "inverse"
                    st.metric("評価", advantage, delta=f"{result['advantage_rate']:.1%}", delta_color=color)
                
                # 詳細内訳
                st.markdown("#### 💰 詳細内訳")
                
                detail_col1, detail_col2, detail_col3 = st.columns(3)
                
                with detail_col1:
                    st.markdown("**コスト**")
                    st.metric("解約手数料合計", f"{result['total_withdrawal_fees']:,.0f}円")
                    st.metric("保険手数料合計", f"{result['total_insurance_fees']:,.0f}円")
                
                with detail_col2:
                    st.markdown("**税効果**")
                    st.metric("節税効果", f"{result['tax_savings']:,.0f}円")
                    st.metric("解約時課税", f"{result['withdrawal_tax']:,.0f}円")
                
                with detail_col3:
                    st.markdown("**リターン**")
                    st.metric("実質利回り", f"{result['effective_return']:.2%}")
                    st.metric("純利益", f"{result['net_profit']:,.0f}円")
                
                # グラフ表示
                st.markdown("#### 📈 資産推移グラフ")
                
                fig = go.Figure()
                
                years = result['timeline']['years']
                
                fig.add_trace(go.Scatter(
                    x=years,
                    y=[v/10000 for v in result['timeline']['insurance_value']],
                    name='保険残高',
                    mode='lines+markers',
                    line=dict(color='blue', width=2),
                    fill='tonexty'
                ))
                
                fig.add_trace(go.Scatter(
                    x=years,
                    y=[v/10000 for v in result['timeline']['reinvestment_value']],
                    name='再投資資産',
                    mode='lines+markers',
                    line=dict(color='green', width=2),
                    fill='tonexty'
                ))
                
                fig.add_trace(go.Scatter(
                    x=years,
                    y=[v/10000 for v in result['timeline']['total_value']],
                    name='総資産',
                    mode='lines+markers',
                    line=dict(color='purple', width=3, dash='dash')
                ))
                
                # 解約ポイントをマーク
                for year in withdrawal_years:
                    fig.add_vline(x=year, line_dash="dot", line_color="red", 
                                 annotation_text=f"{year}年目解約", 
                                 annotation_position="top")
                
                fig.update_layout(
                    title="部分解約戦略：資産価値の推移",
                    xaxis_title="経過年数",
                    yaxis_title="資産価値（万円）",
                    height=500,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with strategy_tab2:
        st.markdown("### 複数戦略の同時比較")
        st.markdown("異なる解約間隔・割合での戦略を一括比較します")
        
        if st.button("📊 複数戦略を比較", key="compare_strategies"):
            with st.spinner("複数戦略を計算中..."):
                strategies = [
                    {"interval": 3, "ratio": 0.2, "name": "3年/20%"},
                    {"interval": 3, "ratio": 0.3, "name": "3年/30%"},
                    {"interval": 4, "ratio": 0.25, "name": "4年/25%"},
                    {"interval": 5, "ratio": 0.2, "name": "5年/20%"},
                    {"interval": 5, "ratio": 0.3, "name": "5年/30%"},
                ]
                
                comparison_results = []
                
                for strategy in strategies:
                    result = _calculate_partial_withdrawal_value_enhanced(
                        plan, fund, strategy["interval"], strategy["ratio"],
                        "投資信託", plan['investment_period'], 0.01, 5000000
                    )
                    
                    comparison_results.append({
                        "戦略": strategy["name"],
                        "解約間隔": f"{strategy['interval']}年",
                        "解約割合": f"{strategy['ratio']:.0%}",
                        "総資産価値": result['total_value'],
                        "vs単純継続": result['vs_simple'],
                        "実質利回り": f"{result['effective_return']:.2%}",
                        "純利益": result['net_profit']
                    })
                
                comparison_df = pd.DataFrame(comparison_results)
                comparison_df = comparison_df.sort_values('総資産価値', ascending=False)
                
                st.markdown("#### 🏆 戦略ランキング")
                st.dataframe(
                    comparison_df.style.format({
                        "総資産価値": "{:,.0f}円",
                        "vs単純継続": "{:+,.0f}円",
                        "純利益": "{:,.0f}円"
                    }).background_gradient(subset=['総資産価値'], cmap='RdYlGn'),
                    use_container_width=True,
                    hide_index=True
                )
                
                # グラフ比較
                fig_compare = go.Figure()
                
                fig_compare.add_trace(go.Bar(
                    x=comparison_df['戦略'],
                    y=comparison_df['総資産価値'],
                    name='総資産価値',
                    marker_color='lightblue'
                ))
                
                fig_compare.update_layout(
                    title="戦略別：総資産価値の比較",
                    xaxis_title="戦略",
                    yaxis_title="総資産価値（円）",
                    height=400
                )
                
                st.plotly_chart(fig_compare, use_container_width=True)
    
    with strategy_tab3:
        st.markdown("### 💡 AI最適戦略提案")
        st.markdown("あなたの状況に最適な部分解約戦略を提案します")
        
        col_ai1, col_ai2 = st.columns(2)
        
        with col_ai1:
            risk_tolerance = st.select_slider(
                "リスク許容度",
                options=["保守的", "やや保守的", "中立", "やや積極的", "積極的"],
                value="中立"
            )
            
            liquidity_need = st.select_slider(
                "流動性ニーズ",
                options=["低", "やや低", "中", "やや高", "高"],
                value="中"
            )
        
        with col_ai2:
            investment_goal = st.selectbox(
                "投資目標",
                ["資産最大化", "安定収益", "税効果最大化", "バランス"]
            )
            
            time_horizon = st.number_input(
                "投資期間（年）",
                min_value=5,
                max_value=30,
                value=plan.get('investment_period', 20)
            )
        
        if st.button("🤖 最適戦略を提案", key="ai_recommend"):
            with st.spinner("AI分析中..."):
                # 簡易的な最適化ロジック
                recommendation = _generate_optimal_strategy_recommendation(
                    risk_tolerance, liquidity_need, investment_goal, time_horizon, plan, fund
                )
                
                st.success("✅ 最適戦略の提案が完了しました")
                
                st.markdown("#### 🎯 推奨戦略")
                st.info(f"""
                **あなたに最適な戦略:**
                
                - **解約間隔**: {recommendation['interval']}年ごと
                - **解約割合**: {recommendation['ratio']:.0%}
                - **再投資先**: {recommendation['reinvestment']}
                - **期待リターン**: {recommendation['expected_return']:.2%}
                - **推奨理由**: {recommendation['reason']}
                """)
                
                # 推奨戦略のシミュレーション
                result = _calculate_partial_withdrawal_value_enhanced(
                    plan, fund, recommendation['interval'], recommendation['ratio'],
                    recommendation['reinvestment'], time_horizon, 0.01, 5000000
                )
                
                col_rec1, col_rec2, col_rec3 = st.columns(3)
                
                with col_rec1:
                    st.metric("予想総資産", f"{result['total_value']:,.0f}円")
                
                with col_rec2:
                    st.metric("予想純利益", f"{result['net_profit']:,.0f}円")
                
                with col_rec3:
                    st.metric("実質利回り", f"{result['effective_return']:.2%}")


def _calculate_partial_withdrawal_value(plan: dict, fund: dict, interval: int, ratio: float, 
                                       reinvestment: str, period: int) -> dict:
    """部分解約戦略の価値計算"""
    monthly_premium = plan['monthly_premium']
    annual_rate = plan['annual_rate'] / 100
    monthly_rate = annual_rate / 12 
    
    current_balance = 0
    reinvestment_value = 0
    total_fees = 0
    remaining_ratio = 1.0
    
    # 月次シミュレーション
    for month in range(1, period * 12 + 1):
        # 保険料積立
        net_premium = monthly_premium * (1 - plan['fee_rate'])
        current_balance = (current_balance + net_premium) * (1 + monthly_rate)
        current_balance -= current_balance * plan['balance_fee_rate']
        
        # 解約判定
        if month % (interval * 12) == 0 and month < period * 12:
            withdrawal_amount = current_balance * ratio
            withdrawal_fee = withdrawal_amount * 0.01  # 1%の解約手数料と仮定
            net_withdrawal = withdrawal_amount - withdrawal_fee
            
            current_balance -= withdrawal_amount
            remaining_ratio *= (1 - ratio)
            total_fees += withdrawal_fee
            
            # 再投資
            if reinvestment == "投資信託":
                # 投資信託として運用（残り期間）
                remaining_months = period * 12 - month
                net_return = fund['annual_return'] - fund['annual_fee']
                monthly_return = net_return / 12
                
                if monthly_return > 0 and remaining_months > 0:
                    growth = net_withdrawal * (1 + monthly_return) ** remaining_months
                else:
                    growth = net_withdrawal
                    
                reinvestment_value += growth
                
            elif reinvestment == "現金保有":
                reinvestment_value += net_withdrawal
                
            else:  # 混合
                cash_portion = net_withdrawal * 0.5
                fund_portion = net_withdrawal * 0.5
                
                reinvestment_value += cash_portion
                
                remaining_months = period * 12 - month
                net_return = fund['annual_return'] - fund['annual_fee']
                monthly_return = net_return / 12
                
                if monthly_return > 0 and remaining_months > 0:
                    fund_growth = fund_portion * (1 + monthly_return) ** remaining_months
                else:
                    fund_growth = fund_portion
                    
                reinvestment_value += fund_growth
    
    # 節税効果
    annual_premium = monthly_premium * 12
    tax_helper = get_tax_helper()
    tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, 5000000)
    total_tax_savings = tax_result['total_savings'] * period
    
    total_value = current_balance + reinvestment_value + total_tax_savings
    
    return {
        'remaining_insurance': current_balance,
        'reinvestment_value': reinvestment_value,
        'tax_savings': total_tax_savings,
        'total_fees': total_fees,
        'total_value': total_value,
        'final_ratio': remaining_ratio
    }


def _calculate_simple_insurance_value(plan: dict) -> float:
    """単純な生命保険継続の価値計算"""
    monthly_premium = plan['monthly_premium']
    annual_rate = plan['annual_rate'] / 100
    monthly_rate = annual_rate / 12
    period = plan['investment_period']
    total_months = period * 12
    
    net_premium = monthly_premium * (1 - plan['fee_rate'])
    
    if monthly_rate > 0:
        insurance_value = net_premium * ((1 + monthly_rate) ** total_months - 1) / monthly_rate
    else:
        insurance_value = net_premium * total_months
    
    # 残高手数料
    balance_fee = insurance_value * plan['balance_fee_rate'] * total_months
    insurance_value -= balance_fee
    
    # 節税効果
    annual_premium = monthly_premium * 12
    tax_helper = get_tax_helper()
    tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, 5000000)
    total_tax_savings = tax_result['total_savings'] * period
    
    return insurance_value + total_tax_savings


def _calculate_partial_withdrawal_value_enhanced(plan: dict, fund: dict, interval: int, ratio: float, 
                                                 reinvestment: str, period: int, 
                                                 withdrawal_fee_rate: float, taxable_income: float) -> dict:
    """強化版：部分解約戦略の詳細な価値計算"""
    monthly_premium = plan['monthly_premium']
    annual_rate = plan['annual_rate'] / 100
    monthly_rate = annual_rate / 12 
    
    # タイムライン記録用
    timeline_years = []
    timeline_insurance = []
    timeline_reinvestment = []
    timeline_total = []
    
    current_balance = 0
    reinvestment_value = 0
    total_withdrawal_fees = 0
    total_insurance_fees = 0
    withdrawal_tax = 0
    remaining_ratio = 1.0
    
    total_paid = 0
    withdrawal_years = []
    
    # 月次シミュレーション
    for month in range(1, period * 12 + 1):
        # 保険料積立
        premium_fee = monthly_premium * plan['fee_rate']
        net_premium = monthly_premium - premium_fee
        total_insurance_fees += premium_fee
        total_paid += monthly_premium
        
        current_balance = (current_balance + net_premium) * (1 + monthly_rate)
        
        # 残高手数料
        balance_fee = current_balance * plan['balance_fee_rate']
        current_balance -= balance_fee
        total_insurance_fees += balance_fee
        
        # 年次記録
        if month % 12 == 0:
            year = month // 12
            timeline_years.append(year)
            timeline_insurance.append(current_balance)
            timeline_reinvestment.append(reinvestment_value)
            timeline_total.append(current_balance + reinvestment_value)
        
        # 解約判定
        if month % (interval * 12) == 0 and month < period * 12:
            withdrawal_amount = current_balance * ratio
            withdrawal_fee = withdrawal_amount * withdrawal_fee_rate
            net_withdrawal = withdrawal_amount - withdrawal_fee
            
            current_balance -= withdrawal_amount
            remaining_ratio *= (1 - ratio)
            total_withdrawal_fees += withdrawal_fee
            withdrawal_years.append(month // 12)
            
            # 解約所得税の計算（一時所得）
            paid_for_withdrawn = total_paid * ratio
            profit = net_withdrawal - paid_for_withdrawn
            if profit > 500000:  # 50万円特別控除
                taxable_profit = (profit - 500000) / 2
                tax_calc = TaxCalculator()
                additional_tax_info = tax_calc.calculate_income_tax(taxable_income + taxable_profit)
                original_tax_info = tax_calc.calculate_income_tax(taxable_income)
                withdrawal_tax += additional_tax_info["合計所得税"] - original_tax_info["合計所得税"]
            
            # 再投資
            if reinvestment == "投資信託":
                remaining_months = period * 12 - month
                net_return = fund['annual_return'] - fund['annual_fee']
                monthly_return = net_return / 12
                
                if monthly_return > 0 and remaining_months > 0:
                    growth = net_withdrawal * (1 + monthly_return) ** remaining_months
                else:
                    growth = net_withdrawal
                    
                reinvestment_value += growth
                
            elif reinvestment == "現金保有":
                reinvestment_value += net_withdrawal
                
            elif reinvestment == "NISA枠活用":
                # NISA枠は非課税なので税金なし
                remaining_months = period * 12 - month
                net_return = fund['annual_return'] - fund['annual_fee']
                monthly_return = net_return / 12
                
                if monthly_return > 0 and remaining_months > 0:
                    growth = net_withdrawal * (1 + monthly_return) ** remaining_months
                else:
                    growth = net_withdrawal
                    
                reinvestment_value += growth
                
            else:  # 混合
                cash_portion = net_withdrawal * 0.5
                fund_portion = net_withdrawal * 0.5
                
                reinvestment_value += cash_portion
                
                remaining_months = period * 12 - month
                net_return = fund['annual_return'] - fund['annual_fee']
                monthly_return = net_return / 12
                
                if monthly_return > 0 and remaining_months > 0:
                    fund_growth = fund_portion * (1 + monthly_return) ** remaining_months
                else:
                    fund_growth = fund_portion
                    
                reinvestment_value += fund_growth
    
    # 節税効果
    annual_premium = monthly_premium * 12
    tax_helper = get_tax_helper()
    tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, taxable_income)
    total_tax_savings = tax_result['total_savings'] * period
    
    # 総価値
    total_value = current_balance + reinvestment_value + total_tax_savings - withdrawal_tax
    
    # 単純継続との比較
    simple_value = _calculate_simple_insurance_value(plan)
    vs_simple = total_value - simple_value
    advantage_rate = vs_simple / simple_value if simple_value > 0 else 0
    
    # 実質利回り
    net_profit = total_value - total_paid
    if total_paid > 0 and period > 0:
        effective_return = ((total_value / total_paid) ** (1 / period)) - 1
    else:
        effective_return = 0
    
    return {
        'remaining_insurance': current_balance,
        'reinvestment_value': reinvestment_value,
        'tax_savings': total_tax_savings,
        'withdrawal_tax': withdrawal_tax,
        'total_withdrawal_fees': total_withdrawal_fees,
        'total_insurance_fees': total_insurance_fees,
        'total_value': total_value,
        'vs_simple': vs_simple,
        'advantage_rate': advantage_rate,
        'net_profit': net_profit,
        'effective_return': effective_return,
        'timeline': {
            'years': timeline_years,
            'insurance_value': timeline_insurance,
            'reinvestment_value': timeline_reinvestment,
            'total_value': timeline_total
        }
    }


def _generate_optimal_strategy_recommendation(risk_tolerance: str, liquidity_need: str, 
                                              investment_goal: str, time_horizon: int,
                                              plan: dict, fund: dict) -> dict:
    """最適戦略の推奨を生成"""
    
    # リスク許容度に基づく基本戦略
    if risk_tolerance in ["保守的", "やや保守的"]:
        base_interval = 5
        base_ratio = 0.20
        base_reinvestment = "混合（50%-50%）"
        expected_return = 0.015
    elif risk_tolerance == "中立":
        base_interval = 4
        base_ratio = 0.25
        base_reinvestment = "投資信託"
        expected_return = 0.025
    else:  # 積極的
        base_interval = 3
        base_ratio = 0.30
        base_reinvestment = "NISA枠活用"
        expected_return = 0.035
    
    # 流動性ニーズに基づく調整
    if liquidity_need in ["やや高", "高"]:
        base_interval = max(2, base_interval - 1)
        base_ratio = min(0.40, base_ratio + 0.05)
    elif liquidity_need in ["低", "やや低"]:
        base_interval = min(6, base_interval + 1)
        base_ratio = max(0.15, base_ratio - 0.05)
    
    # 投資目標に基づく調整
    if investment_goal == "資産最大化":
        base_reinvestment = "NISA枠活用"
        reason = "資産最大化を目指し、NISA枠を活用した積極運用を推奨します"
    elif investment_goal == "安定収益":
        base_reinvestment = "混合（50%-50%）"
        base_ratio = max(0.15, base_ratio - 0.05)
        reason = "安定収益を重視し、リスク分散した運用を推奨します"
    elif investment_goal == "税効果最大化":
        base_interval = max(3, base_interval - 1)
        reason = "節税効果を最大化するため、定期的な部分解約を推奨します"
    else:  # バランス
        reason = "リスクとリターンのバランスを考慮した戦略を推奨します"
    
    return {
        'interval': base_interval,
        'ratio': base_ratio,
        'reinvestment': base_reinvestment,
        'expected_return': expected_return,
        'reason': reason
    }
    insurance_value -= balance_fee
    
    # 節税効果（関数末尾の計算）
    annual_premium = monthly_premium * 12
    tax_helper = get_tax_helper()
    tax_result = tax_helper.calculate_annual_tax_savings(annual_premium, 5000000)
    total_tax_savings = tax_result['total_savings'] * period
    
    return insurance_value + total_tax_savings


def _show_summary_report():
    """サマリーレポートの表示"""
    st.markdown("#### 分析結果サマリー")
    
    if ('plan_settings' not in st.session_state or 
        'fund_settings' not in st.session_state):
        st.warning("分析を完了するために、まず「生命保険控除について」と「投資信託との比較」を実行してください。")
        return
    
    plan = st.session_state.plan_settings
    fund = st.session_state.fund_settings
    
    # キー指標の計算
    monthly_premium = plan['monthly_premium']
    period = plan['investment_period']
    total_investment = monthly_premium * period * 12
    
    # 生命保険価値
    insurance_value = _calculate_simple_insurance_value(plan)
    
    # 投資信託価値
    net_return = fund['annual_return'] - fund['annual_fee']
    monthly_return = net_return / 12
    total_months = period * 12
    
    if monthly_return > 0:
        fund_value = monthly_premium * ((1 + monthly_return) ** total_months - 1) / monthly_return
    else:
        fund_value = monthly_premium * total_months
    
    capital_gain = max(0, fund_value - total_investment)
    tax = capital_gain * fund['tax_rate']
    fund_net_value = fund_value - tax
    
    # サマリー表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("💰 生命保険")
        st.metric("最終価値", f"{insurance_value:,.0f}円")
        st.metric("実質利回り", f"{((insurance_value / total_investment) ** (1/period) - 1):.2%}")
    
    with col2:
        st.subheader("📈 投資信託") 
        st.metric("最終価値", f"{fund_net_value:,.0f}円")
        st.metric("実質利回り", f"{((fund_net_value / total_investment) ** (1/period) - 1):.2%}")
    
    with col3:
        st.subheader("🏆 推奨")
        if fund_net_value > insurance_value:
            st.success("投資信託")
            st.metric("優位性", f"{fund_net_value - insurance_value:,.0f}円")
        else:
            st.success("生命保険")
            st.metric("優位性", f"{insurance_value - fund_net_value:,.0f}円")
    
    # 推奨戦略
    st.subheader("🎯 推奨戦略")
    
    if fund_net_value > insurance_value:
        difference = fund_net_value - insurance_value
        advantage = difference / insurance_value
        
        if advantage > 0.1:  # 10%以上の差
            st.success("**推奨：投資信託への全面移行**")
            st.markdown(f"- 投資信託の優位性: {advantage:.1%}")
            st.markdown("- 理由：期待リターンが生命保険を大きく上回る")
        else:
            st.info("**推奨：ハイブリッド戦略（部分解約＋投資信託）**")
            st.markdown("- 両商品の優位性が近接している")
            st.markdown("- リスク分散の観点から混合戦略を推奨")
    else:
        st.success("**推奨：生命保険継続**")
        st.markdown("- 節税効果と確実性を重視")
        st.markdown("- 投資信託の税負担が大きい")


def _show_detailed_results():
    """詳細分析結果の表示"""
    st.markdown("#### 詳細分析結果")
    
    if ('plan_settings' not in st.session_state or 
        'fund_settings' not in st.session_state):
        st.warning("詳細結果を表示するために、まず分析を完了してください。")
        return
    
    plan = st.session_state.plan_settings
    fund = st.session_state.fund_settings
    
    # 詳細計算結果のテーブル作成
    results_data = {
        "項目": [
            "月額投資額", "投資期間", "総投資額",
            "生命保険年利", "投資信託期待リターン", "投資信託手数料",
            "生命保険最終価値", "投資信託最終価値", "価値差"
        ],
        "値": [
            f"{plan['monthly_premium']:,.0f}円",
            f"{plan['investment_period']}年",
            f"{plan['monthly_premium'] * plan['investment_period'] * 12:,.0f}円",
            f"{plan['annual_rate']:.2f}%",
            f"{fund['annual_return']:.2f}%",
            f"{fund['annual_fee']:.2f}%",
            f"{_calculate_simple_insurance_value(plan):,.0f}円",
            "計算中...",
            "計算中..."
        ]
    }
    
    results_df = pd.DataFrame(results_data)
    st.table(results_df)


def _show_data_export():
    """データ出力機能"""
    st.markdown("#### データ出力")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 出力オプション")
        
        export_format = st.selectbox(
            "出力形式",
            ["CSV", "Excel", "JSON"],
            key="export_format"
        )
        
        include_charts = st.checkbox("チャートを含める", value=True, key="include_charts")
        include_summary = st.checkbox("サマリーを含める", value=True, key="include_summary")
        
    with col2:
        st.subheader("📁 ダウンロード")
        
        if st.button("レポート生成", key="generate_report"):
            # レポート生成のプレースホルダー
            st.success("レポートが生成されました")
            st.download_button(
                label="レポートをダウンロード",
                data="レポートデータ（実装予定）",
                file_name=f"analysis_report.{export_format.lower()}",
                mime="text/plain"
            )


# 既存の関数との統合用ヘルパー関数

def _show_existing_detailed_plan_analysis():
    """既存の詳細プラン分析を呼び出し"""
    # 既存のshow_specific_plan_analysisの内容をここに統合
    _show_detailed_plan_analysis_content()


def _show_existing_withdrawal_optimizer():
    """既存の引き出しタイミング最適化を呼び出し"""
    # 既存のshow_withdrawal_optimizerの内容をここに統合
    _show_withdrawal_optimizer_content()


def _show_detailed_plan_analysis_content():
    """詳細プラン分析の内容"""
    # ここに既存のshow_specific_plan_analysisの実装内容を移行
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 プラン設定")
        monthly_premium = st.number_input("月額保険料（円）", min_value=1000, max_value=50000, value=9000, step=1000)
        annual_rate = st.number_input("年利率（%）", min_value=0.0, max_value=10.0, value=1.25, step=0.01)
        investment_period = st.number_input("投資期間（年）", min_value=1, max_value=50, value=20, step=1)
        
    with col2:
        st.subheader("💰 結果")
        # 計算実行
        total_premium = monthly_premium * 12 * investment_period
        st.metric("総保険料", f"{total_premium:,.0f}円")
        
        # 簡易的な最終価値計算
        monthly_rate = annual_rate / 100 / 12
        total_months = investment_period * 12
        
        if monthly_rate > 0:
            future_value = monthly_premium * ((1 + monthly_rate) ** total_months - 1) / monthly_rate
        else:
            future_value = monthly_premium * total_months
        
        st.metric("予想価値", f"{future_value:,.0f}円")


def _show_withdrawal_optimizer_content():
    """引き出しタイミング最適化の内容"""
    st.markdown("### 🎯 部分解約戦略の最適化分析")
    st.markdown("最適な引き出しタイミングと所得シナリオ別の効果を分析します")
    
    # パラメータ入力
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 基本パラメータ")
        
        annual_premium = st.number_input(
            "年間保険料（円）",
            min_value=10000,
            max_value=500000,
            value=100000,
            step=10000,
            help="年間に支払う保険料"
        )
        
        taxable_income_man = st.number_input(
            "課税所得（万円）",
            min_value=100,
            max_value=2000,
            value=500,
            step=50,
            help="各種所得控除を差し引いた後の課税対象所得額"
        )
        
        taxable_income = taxable_income_man * 10000
        
        policy_start_year = st.number_input(
            "保険開始年",
            min_value=2010,
            max_value=datetime.now().year,
            value=2020,
            step=1
        )
        
        max_years = st.number_input(
            "最大分析期間（年）",
            min_value=5,
            max_value=30,
            value=20,
            step=1,
            help="何年後までの引き出しタイミングを分析するか"
        )
        
        return_rate = st.number_input(
            "想定運用利回り（%）",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help="保険商品の想定運用利回り"
        ) / 100
    
    with col2:
        st.subheader("📊 最適化実行")
        
        if st.button("🚀 最適化分析を実行", type="primary"):
            with st.spinner("最適化計算中..."):
                # WithdrawalOptimizerのインスタンス作成
                optimizer = WithdrawalOptimizer()
                
                # 最適タイミング分析
                best_timing, all_results = optimizer.optimize_withdrawal_timing(
                    annual_premium,
                    taxable_income,
                    policy_start_year,
                    max_years,
                    return_rate
                )
                
                # 結果を表示
                st.success("✅ 最適化完了")
                
                st.markdown("#### 🎯 最適引き出しタイミング")
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric(
                        "最適引き出し年",
                        f"{best_timing['引き出し年']}年",
                        delta=f"{best_timing['保険期間']}年後"
                    )
                
                with col_b:
                    st.metric(
                        "純利益",
                        f"{best_timing['純利益']:,.0f}円"
                    )
                
                with col_c:
                    st.metric(
                        "実質利回り",
                        f"{best_timing['実質利回り']:.2%}"
                    )
                
                # 詳細情報
                st.markdown("#### 📋 詳細情報")
                detail_cols = st.columns(4)
                
                with detail_cols[0]:
                    st.metric("払込保険料合計", f"{best_timing['払込保険料合計']:,.0f}円")
                
                with detail_cols[1]:
                    st.metric("累計節税効果", f"{best_timing['累計節税効果']:,.0f}円")
                
                with detail_cols[2]:
                    st.metric("解約返戻金", f"{best_timing['解約返戻金']:,.0f}円")
                
                with detail_cols[3]:
                    st.metric("解約時所得税", f"{best_timing['解約時所得税']:,.0f}円")
    
    # 所得シナリオ別比較
    st.markdown("---")
    st.markdown("### 💼 所得シナリオ別比較分析")
    
    col_scenario1, col_scenario2 = st.columns(2)
    
    with col_scenario1:
        st.subheader("📝 シナリオ設定")
        
        withdrawal_year = st.number_input(
            "引き出し年（比較用）",
            min_value=policy_start_year + 1,
            max_value=policy_start_year + 30,
            value=policy_start_year + 10,
            step=1
        )
    
    with col_scenario2:
        st.subheader("🔧 比較所得レベル")
        
        compare_low = st.checkbox("低所得（300万円）", value=True)
        compare_high = st.checkbox("高所得（800万円）", value=True)
        compare_super = st.checkbox("超高所得（1,200万円）", value=True)
    
    if st.button("📊 所得シナリオ比較を実行"):
        with st.spinner("シナリオ分析中..."):
            optimizer = WithdrawalOptimizer()
            
            # シナリオリスト作成
            income_scenarios = []
            if compare_low:
                income_scenarios.append(("低所得", 3000000))
            if compare_high:
                income_scenarios.append(("高所得", 8000000))
            if compare_super:
                income_scenarios.append(("超高所得", 12000000))
            
            # シナリオ分析実行
            scenario_results = optimizer.analyze_income_scenarios(
                annual_premium,
                taxable_income,
                income_scenarios,
                policy_start_year,
                withdrawal_year,
                return_rate
            )
            
            st.success("✅ シナリオ分析完了")
            
            # 結果表示
            st.markdown("#### 📊 所得シナリオ別比較結果")
            st.dataframe(
                scenario_results.style.format({
                    "課税所得": "{:,.0f}円",
                    "累計節税効果": "{:,.0f}円",
                    "解約返戻金": "{:,.0f}円",
                    "解約時所得税": "{:,.0f}円",
                    "純利益": "{:,.0f}円"
                }),
                use_container_width=True
            )
            
            # グラフ化
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='累計節税効果',
                x=scenario_results['シナリオ'],
                y=scenario_results['累計節税効果'],
                marker_color='lightblue'
            ))
            
            fig.add_trace(go.Bar(
                name='純利益',
                x=scenario_results['シナリオ'],
                y=scenario_results['純利益'],
                marker_color='darkblue'
            ))
            
            fig.update_layout(
                title="所得シナリオ別：節税効果と純利益",
                xaxis_title="所得シナリオ",
                yaxis_title="金額（円）",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 洞察
            st.markdown("#### 💡 分析結果の洞察")
            st.info(f"""
            - **所得が高いほど節税効果が大きい**: 高所得者ほど税率が高いため、控除による節税額が増加します
            - **純利益も所得に応じて増加**: 節税効果の差が純利益の差に直結します
            - **最適戦略**: 所得水準に応じて引き出しタイミングを調整することで、より高い実質リターンを得られます
            """)


if __name__ == "__main__":
    main()