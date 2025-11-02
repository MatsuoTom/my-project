"""
投資詳細解析 Streamlitアプリ

SBI証券などのCSV明細から詳細な投資パフォーマンス分析を実施
"""

import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path

# モジュールのインポート
sys.path.append(str(Path(__file__).parent.parent.parent))

from investment_simulation.analysis.sbi_csv_parser import SBICSVParser
from investment_simulation.analysis.performance_analyzer import PerformanceAnalyzer
from investment_simulation.analysis.risk_analyzer import RiskAnalyzer
from investment_simulation.analysis.simulator import InvestmentSimulator

# ページ設定
st.set_page_config(
    page_title="投資詳細解析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .big-metric {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .positive { color: #00C851; }
    .negative { color: #ff4444; }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'parser' not in st.session_state:
    st.session_state.parser = None
if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = None

def load_sample_data():
    """サンプルデータを読み込み"""
    sample_path = Path(__file__).parent.parent / 'data' / 'sample_sbi_emaxis_slim_sp500.csv'
    if sample_path.exists():
        parser = SBICSVParser()
        parser.load_csv(str(sample_path))
        parser.parse_data()
        return parser
    return None

def main():
    st.title("📊 投資詳細解析システム")
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("📁 データ読込")
        
        # ファイルアップロード
        uploaded_file = st.file_uploader(
            "CSVファイルをアップロード",
            type=['csv'],
            help="SBI証券の取引明細CSVをアップロードしてください"
        )
        
        # サンプルデータボタン
        if st.button("📄 サンプルデータを使用", use_container_width=True):
            parser = load_sample_data()
            if parser:
                st.session_state.parser = parser
                st.session_state.parsed_data = parser.parsed_data
                st.success("✅ サンプルデータを読み込みました")
                st.rerun()
            else:
                st.error("サンプルデータが見つかりません")
        
        # ファイルアップロード処理
        if uploaded_file is not None:
            try:
                # 一時ファイルに保存
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                parser = SBICSVParser()
                parser.load_csv(temp_path)
                parser.parse_data()
                
                st.session_state.parser = parser
                st.session_state.parsed_data = parser.parsed_data
                
                # 一時ファイル削除
                os.remove(temp_path)
                
                st.success(f"✅ {uploaded_file.name} を読み込みました")
                st.rerun()
            except Exception as e:
                st.error(f"エラー: {e}")
        
        # データ情報
        if st.session_state.parsed_data is not None:
            st.markdown("---")
            st.subheader("📈 データ情報")
            df = st.session_state.parsed_data
            st.info(f"レコード数: {len(df)}件")
            st.info(f"期間: {df['発生日'].min().strftime('%Y/%m/%d')} ～ {df['発生日'].max().strftime('%Y/%m/%d')}")
    
    # メインコンテンツ
    if st.session_state.parser is None:
        st.info("👈 サイドバーからCSVファイルをアップロードするか、サンプルデータを使用してください。")
        
        # 使い方ガイド
        with st.expander("📖 使い方ガイド", expanded=True):
            st.markdown("""
            ### SBI証券のCSV明細取得方法
            
            1. **SBI証券サイトにログイン**
            2. **「口座管理」→「投資信託」→「保有残高」**
            3. **銘柄を選択**
            4. **「取引履歴」または「詳細履歴」**
            5. **「CSVダウンロード」ボタン**
            
            ### 対応フォーマット
            
            必要なカラム:
            - 発生日
            - 取引区分（買付/売却）
            - 口座種別（特定/NISA等）
            - 数量、金額、当日基準価額、評価金額、個別元本
            
            ### 機能概要
            
            - **サマリーダッシュボード**: 重要指標の一覧
            - **詳細分析**: 時系列グラフと統計
            - **リスク分析**: ドローダウン、ボラティリティ
            - **シミュレーション**: 将来予測
            """)
        return
    
    # データが読み込まれている場合
    parser = st.session_state.parser
    df = st.session_state.parsed_data
    
    # タブ構成
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 サマリーダッシュボード",
        "📈 詳細分析",
        "🔍 リスク分析",
        "🚀 シミュレーション"
    ])
    
    # タブ1: サマリーダッシュボード
    with tab1:
        show_summary_dashboard(parser, df)
    
    # タブ2: 詳細分析
    with tab2:
        show_detailed_analysis(parser, df)
    
    # タブ3: リスク分析
    with tab3:
        show_risk_analysis(parser, df)
    
    # タブ4: シミュレーション
    with tab4:
        show_simulation(parser, df)


def show_summary_dashboard(parser: SBICSVParser, df: pd.DataFrame):
    """サマリーダッシュボードを表示"""
    st.header("📊 サマリーダッシュボード")
    
    # 基本統計を取得
    stats = parser.get_basic_stats()
    
    # 主要指標をカードで表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "総投資額",
            f"¥{stats['総投資額']:,.0f}",
            f"{stats['買付回数']}回"
        )
    
    with col2:
        st.metric(
            "現在評価額",
            f"¥{stats['現在評価額']:,.0f}",
            f"{stats['現在保有数量']:,.0f}口"
        )
    
    with col3:
        profit_color = "normal" if stats['総合損益'] >= 0 else "inverse"
        st.metric(
            "総合損益",
            f"¥{stats['総合損益']:,.0f}",
            f"{stats['総合リターン率']:+.2f}%",
            delta_color=profit_color
        )
    
    with col4:
        st.metric(
            "年率リターン (CAGR)",
            f"{stats['年率換算リターン_CAGR']:+.2f}%",
            f"{stats['保有期間_年数']:.1f}年"
        )
    
    st.markdown("---")
    
    # 詳細情報
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 損益内訳")
        
        # 損益データ
        profit_data = pd.DataFrame({
            '項目': ['実現損益', '含み損益'],
            '金額': [stats['実現損益'], stats['含み損益']]
        })
        
        st.dataframe(
            profit_data.style.format({'金額': '¥{:,.0f}'}),
            hide_index=True,
            use_container_width=True
        )
        
        # 売却情報
        if stats['売却回数'] > 0:
            st.info(f"💡 売却: {stats['売却回数']}回、総額¥{stats['総売却額']:,.0f}")
    
    with col2:
        st.subheader("📅 保有期間")
        
        period_data = pd.DataFrame({
            '項目': ['最初の買付日', '最終更新日', '保有期間'],
            '値': [
                stats['最初の買付日'].strftime('%Y年%m月%d日') if stats['最初の買付日'] else '-',
                stats['最終更新日'].strftime('%Y年%m月%d日') if stats['最終更新日'] else '-',
                f"{stats['保有期間_日数']}日（{stats['保有期間_年数']:.2f}年）"
            ]
        })
        
        st.dataframe(period_data, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    # 口座別集計
    st.subheader("🏦 口座別集計")
    account_summary = parser.get_account_summary()
    
    # スタイル付きDataFrame
    styled_df = account_summary.style.format({
        '投資額': '¥{:,.0f}',
        '保有数量': '{:,.0f}口',
        '買付回数': '{:,.0f}回'
    })
    
    st.dataframe(styled_df, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    # 口座別表示オプション
    show_by_account = st.checkbox("📊 口座別に表示", value=False, key="summary_by_account")
    
    # パフォーマンスグラフ（2列）
    col1, col2 = st.columns(2)
    
    analyzer = PerformanceAnalyzer(df)
    
    with col1:
        st.subheader("📈 評価額推移")
        fig = analyzer.plot_cumulative_performance(by_account=show_by_account)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 リターン率推移")
        fig = analyzer.plot_return_rate(by_account=show_by_account)
        st.plotly_chart(fig, use_container_width=True)


def show_detailed_analysis(parser: SBICSVParser, df: pd.DataFrame):
    """詳細分析を表示"""
    st.header("📈 詳細分析")
    
    analyzer = PerformanceAnalyzer(df)
    
    # 基準価額推移と取引タイミング
    st.subheader("💹 基準価額推移と取引タイミング")
    fig = analyzer.plot_unit_price_history()
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 月次投資額
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💰 月次投資額")
        fig = analyzer.plot_monthly_investment()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📅 月次サマリー")
        monthly_summary = parser.get_monthly_summary()
        st.dataframe(
            monthly_summary.style.format({
                '投資額': '¥{:,.0f}',
                '取得数量': '{:,.0f}口',
                '平均基準価額': '¥{:,.0f}',
                '個別元本': '¥{:,.0f}'
            }),
            hide_index=True,
            use_container_width=True,
            height=400
        )
    
    st.markdown("---")
    
    # ドルコスト平均法の効果
    st.subheader("💡 ドルコスト平均法の効果分析")
    
    dca_analysis = analyzer.analyze_dollar_cost_averaging()
    
    if dca_analysis:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("平均取得単価", f"¥{dca_analysis['平均取得単価']:,.0f}")
            st.metric("最終個別元本", f"¥{dca_analysis['最終個別元本']:,.0f}")
        
        with col2:
            price_stats = dca_analysis['基準価額統計']
            st.metric("最高価格", f"¥{price_stats['最高価格']:,.0f}")
            st.metric("最低価格", f"¥{price_stats['最低価格']:,.0f}")
        
        with col3:
            st.metric("平均価格", f"¥{price_stats['平均価格']:,.0f}")
            st.metric("価格変動率", f"{price_stats['価格変動率']:.2f}%")
        
        # 高値掴み/安値拾い
        with st.expander("📊 高値掴み/安値拾い分析", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**最高値での買付**")
                st.info(f"回数: {dca_analysis['最高値での買付回数']}回")
                st.info(f"金額: ¥{dca_analysis['最高値での買付額']:,.0f}")
            
            with col2:
                st.write("**最低値での買付**")
                st.info(f"回数: {dca_analysis['最低値での買付回数']}回")
                st.info(f"金額: ¥{dca_analysis['最低値での買付額']:,.0f}")
    
    st.markdown("---")
    
    # 一括投資との比較
    st.subheader("🔄 一括投資との比較")
    
    comparison = analyzer.compare_with_lump_sum()
    
    if comparison:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**一括投資（初回に全額）**")
            st.metric("評価額", f"¥{comparison['一括投資_評価額']:,.0f}")
            st.metric("リターン率", f"{comparison['一括投資_リターン率']:+.2f}%")
        
        with col2:
            st.write("**積立投資（実績）**")
            st.metric("評価額", f"¥{comparison['積立投資_評価額']:,.0f}")
            st.metric("リターン率", f"{comparison['積立投資_リターン率']:+.2f}%")
        
        # 差異
        diff_color = "🟢" if comparison['差異_評価額'] >= 0 else "🔴"
        st.info(f"{diff_color} 差異: ¥{comparison['差異_評価額']:+,.0f} ({comparison['差異_リターン率']:+.2f}%)")


def show_risk_analysis(parser: SBICSVParser, df: pd.DataFrame):
    """リスク分析を表示"""
    st.header("🔍 リスク分析")
    
    risk_analyzer = RiskAnalyzer(df)
    
    # 最大ドローダウン
    st.subheader("📉 最大ドローダウン")
    
    dd_info = risk_analyzer.calculate_max_drawdown()
    
    if dd_info:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "最大DD率",
                f"{dd_info['最大ドローダウン率']:.2f}%",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "ピーク評価額",
                f"¥{dd_info['ピーク評価額']:,.0f}"
            )
        
        with col3:
            recovery_text = f"{dd_info['回復期間_日数']}日" if dd_info['回復期間_日数'] else "未回復"
            st.metric("回復期間", recovery_text)
        
        # ドローダウングラフ
        fig = risk_analyzer.plot_drawdown()
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ボラティリティ
    st.subheader("📊 ボラティリティ分析")
    
    vol_info = risk_analyzer.calculate_volatility()
    
    if vol_info:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("日次ボラティリティ", f"{vol_info['日次ボラティリティ']:.2f}%")
        
        with col2:
            st.metric("年率ボラティリティ", f"{vol_info['年率ボラティリティ']:.2f}%")
        
        with col3:
            sharpe = risk_analyzer.calculate_sharpe_ratio()
            st.metric("シャープレシオ", f"{sharpe:.2f}")
        
        # リターン分布
        col1, col2 = st.columns(2)
        
        with col1:
            fig = risk_analyzer.plot_return_distribution()
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = risk_analyzer.plot_rolling_volatility(window=30)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # VaRと下方リスク
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ VaR (Value at Risk)")
        
        var_info = risk_analyzer.calculate_var(confidence_level=0.95)
        
        if var_info:
            st.metric("VaR (95%)", f"¥{var_info['ヒストリカルVaR_金額']:,.0f}")
            st.info(f"95%の確率で、1日の損失が ¥{abs(var_info['ヒストリカルVaR_金額']):,.0f} を超えない")
    
    with col2:
        st.subheader("📉 下方リスク")
        
        downside = risk_analyzer.analyze_downside_risk()
        
        if downside:
            st.metric("下方偏差（年率）", f"{downside['下方偏差_年率']:.2f}%")
            st.metric("マイナス頻度", f"{downside['マイナスリターン頻度']:.1f}%")


def show_simulation(parser: SBICSVParser, df: pd.DataFrame):
    """シミュレーションを表示"""
    st.header("🚀 将来予測シミュレーション")
    
    simulator = InvestmentSimulator(df)
    
    # 将来価値シミュレーション
    st.subheader("📈 将来価値予測（複数シナリオ）")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sim_years = st.slider("予測期間（年）", 1, 30, 10)
    
    with col2:
        monthly_inv = st.number_input(
            "月次投資額（円）",
            min_value=0,
            max_value=1000000,
            value=None,
            step=10000,
            help="空欄の場合は過去の平均を使用"
        )
    
    with col3:
        scenarios_text = st.text_input(
            "リターンシナリオ（%、カンマ区切り）",
            value="3,5,7,10"
        )
    
    try:
        scenarios = [float(x.strip())/100 for x in scenarios_text.split(',')]
    except:
        scenarios = [0.03, 0.05, 0.07, 0.10]
    
    if st.button("🔮 シミュレーション実行", type="primary"):
        result = simulator.simulate_future_value(
            years=sim_years,
            monthly_investment=monthly_inv,
            scenarios=scenarios
        )
        
        # 結果表示
        st.success(f"✅ {sim_years}年後の予測結果")
        
        # メトリクス
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("現在評価額", f"¥{result['現在評価額']:,.0f}")
        
        with col2:
            st.metric("月次投資額", f"¥{result['月次投資額']:,.0f}")
        
        with col3:
            st.metric("予測期間", f"{sim_years}年")
        
        # グラフ
        fig = simulator.plot_future_scenarios(result)
        st.plotly_chart(fig, use_container_width=True)
        
        # シナリオ詳細
        st.subheader("📊 シナリオ別詳細")
        
        scenario_df = pd.DataFrame([
            {
                'シナリオ': name,
                '年率リターン': f"{data['年率リターン']:.1f}%",
                '最終評価額': f"¥{data['最終評価額']:,.0f}",
                '追加投資額': f"¥{data['追加投資額']:,.0f}",
                '総利益': f"¥{data['総利益']:,.0f}",
                'リターン率': f"{data['リターン率']:.2f}%"
            }
            for name, data in result['シナリオ結果'].items()
        ])
        
        st.dataframe(scenario_df, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    # 目標達成シミュレーション
    st.subheader("🎯 目標金額達成シミュレーション")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        target_amount = st.number_input(
            "目標金額（円）",
            min_value=1000000,
            max_value=100000000,
            value=5000000,
            step=1000000
        )
    
    with col2:
        goal_monthly = st.number_input(
            "月次投資額（円）",
            min_value=0,
            max_value=1000000,
            value=None,
            step=10000,
            key="goal_monthly",
            help="空欄の場合は過去平均"
        )
    
    with col3:
        expected_return = st.slider(
            "期待年率リターン（%）",
            0.0, 20.0, 5.0, 0.5
        ) / 100
    
    if st.button("🎯 目標達成分析", type="primary"):
        goal_result = simulator.calculate_goal_achievement(
            target_amount=target_amount,
            monthly_investment=goal_monthly,
            expected_return=expected_return
        )
        
        if goal_result.get('ステータス') == '達成済み':
            st.success(f"🎉 既に目標を達成しています！ 超過額: ¥{goal_result['超過額']:,.0f}")
        else:
            st.info(f"📅 目標達成予想: {goal_result['到達予想期間_年']:.1f}年後（{goal_result['到達予想期間_月']:.0f}ヶ月）")
            
            # メトリクス
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("現在評価額", f"¥{goal_result['現在評価額']:,.0f}")
                st.metric("不足額", f"¥{goal_result['不足額']:,.0f}")
            
            with col2:
                st.metric("月次投資額", f"¥{goal_result['月次投資額']:,.0f}")
                st.metric("追加投資総額", f"¥{goal_result['追加投資総額']:,.0f}")
            
            with col3:
                st.metric("期待年率", f"{goal_result['期待年率リターン']:.1f}%")
                st.metric("必要最小月額", f"¥{goal_result['必要月額_最小']:,.0f}")


if __name__ == "__main__":
    main()
