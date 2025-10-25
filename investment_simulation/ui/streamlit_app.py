# NISA投資シミュレーション・管理アプリ
# 月次投資データの入力・分析・可視化

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, date
import io
import sys
import os

# モジュールのインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)).rsplit(os.sep, 2)[0])

try:
    from investment_simulation.core.nisa_utils import (
        load_nisa_data, save_nisa_data, get_default_nisa_data, 
        add_monthly_record, get_investment_summary, validate_nisa_data,
        calculate_cumulative_values, NISACalculator
    )
    from investment_simulation.analysis.investment_analyzer import InvestmentAnalyzer
except ImportError as e:
    st.error(f"モジュールのインポートエラー: {e}")
    st.stop()

# ページ設定
st.set_page_config(
    page_title="NISA投資シミュレーション",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .positive { color: #00C851; }
    .negative { color: #ff4444; }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'nisa_data' not in st.session_state:
    st.session_state.nisa_data = load_nisa_data()

def main():
    # サイドバー
    with st.sidebar:
        st.header("🎯 設定")
        
        # データの保存・読込
        st.subheader("📁 データ管理")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 保存", use_container_width=True):
                if save_nisa_data(st.session_state.nisa_data):
                    st.success("✅ 保存完了")
                else:
                    st.error("❌ 保存失敗")
        
        with col2:
            if st.button("🔄 再読込", use_container_width=True):
                st.session_state.nisa_data = load_nisa_data()
                st.success("✅ 再読込完了")
                st.rerun()
        
        # CSVファイルのインポート
        uploaded_file = st.file_uploader(
            "📥 CSVファイルをインポート",
            type=['csv'],
            help="年,月,投資額,評価額の形式のCSVファイル"
        )
        
        if uploaded_file is not None:
            try:
                df_uploaded = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                # データ検証
                errors = validate_nisa_data(df_uploaded)
                if errors:
                    st.error("データエラー:")
                    for error in errors:
                        st.write(f"- {error}")
                else:
                    st.session_state.nisa_data = calculate_cumulative_values(df_uploaded)
                    st.success("✅ インポート完了")
                    st.rerun()
            except Exception as e:
                st.error(f"インポートエラー: {e}")
        
        # データのエクスポート
        if not st.session_state.nisa_data.empty:
            csv_data = st.session_state.nisa_data.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📤 CSVダウンロード",
                data=csv_data,
                file_name=f"nisa_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # 分析設定
        st.subheader("⚙️ 分析設定")
        future_months = st.slider("予測期間（月）", 6, 60, 24)
        expected_return = st.slider("期待年利（%）", -10.0, 20.0, 5.0, 0.5)
    
    # メインコンテンツ
    st.title("💰 NISA投資シミュレーション")
    st.markdown("---")
    
    # 新タブ構成
    tab1, tab2 = st.tabs([
        "📝 銘柄登録・データ管理", 
        "� パフォーマンス分析・積立シナリオ"
    ])

    with tab1:
        show_data_input()

    with tab2:
        show_performance_and_scenario()
def show_performance_and_scenario():
    """
    パフォーマンス分析＋積立シナリオ画面
    """
    st.header("📊 パフォーマンス分析・積立シナリオ")
    if st.session_state.nisa_data.empty or len(st.session_state.nisa_data) < 2:
        st.info("分析には2ヶ月以上のデータが必要です。")
        return

    # 既存データの分析（リターン・リスク・損益グラフ）
    st.subheader("現状パフォーマンス分析")
    show_detailed_analysis()

    # 積立シナリオ入力
    st.subheader("積立投資シナリオシミュレーション")
    col1, col2, col3 = st.columns(3)
    with col1:
        scenario_months = st.number_input("積立期間（月）", min_value=6, max_value=120, value=24, step=1)
    with col2:
        scenario_amount = st.number_input("毎月積立額（円）", min_value=0, value=30000, step=1000)
    with col3:
        scenario_return = st.number_input("期待年利（%）", min_value=-10.0, max_value=20.0, value=5.0, step=0.5)

    # シナリオ計算・グラフ
    st.markdown("---")
    st.subheader("シナリオ別将来予測グラフ")
    calculator = NISACalculator(st.session_state.nisa_data)
    scenario_result = calculator.project_future_value(scenario_months, scenario_amount, scenario_return)
    st.metric(f"{scenario_months}ヶ月後の予測評価額", f"¥{scenario_result['future_value']:,.0f}")
    st.metric(f"{scenario_months}ヶ月後の累計投資額", f"¥{scenario_result['total_investment']:,.0f}")
    st.metric("予測損益", f"¥{scenario_result['projected_profit']:,.0f}", delta=f"{scenario_result['projected_return_rate']:.2f}%")

    # 予測グラフ（簡易）
    import plotly.graph_objects as go
    months = list(range(1, scenario_months + 1))
    future_values = []
    fv = scenario_result['future_value'] - scenario_amount * scenario_months
    for m in months:
        fv = fv * (1 + (scenario_return/100)/12) + scenario_amount
        future_values.append(fv)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=future_values, mode='lines+markers', name='予測評価額'))
    fig.update_layout(title="積立シナリオ将来予測", xaxis_title="期間（月）", yaxis_title="予測評価額（円）", height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_dashboard():
    """ダッシュボード表示"""
    st.header("📈 投資サマリー")
    
    if st.session_state.nisa_data.empty:
        st.info("データがありません。「データ入力・編集」タブからデータを入力してください。")
        return
    
    # サマリー情報を取得
    summary = get_investment_summary(st.session_state.nisa_data)
    
    # メトリクス表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "累計投資額",
            f"¥{summary['total_investment']:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "現在評価額",
            f"¥{summary['total_evaluation']:,.0f}",
            delta=f"¥{summary['total_profit_loss']:,.0f}"
        )
    
    with col3:
        color = "normal" if summary['profit_loss_rate'] >= 0 else "inverse"
        st.metric(
            "損益率",
            f"{summary['profit_loss_rate']:.2f}%",
            delta=f"{summary['profit_loss_rate']:.2f}%",
            delta_color=color
        )
    
    with col4:
        st.metric(
            "平均月投資額",
            f"¥{summary['monthly_avg_investment']:,.0f}",
            delta=f"{summary['months_count']}ヶ月"
        )
    
    # 銘柄・投資方法選択
    brands = st.session_state.nisa_data['銘柄'].dropna().unique().tolist()
    brands = [b for b in brands if b]
    selected_brand = None
    if brands:
        selected_brand = st.selectbox("銘柄で絞り込み", ["全体"] + brands, index=0)
    methods = st.session_state.nisa_data['投資方法'].dropna().unique().tolist() if '投資方法' in st.session_state.nisa_data.columns else []
    methods = [m for m in methods if m]
    selected_method = None
    if methods:
        selected_method = st.selectbox("投資方法で絞り込み", ["全体"] + methods, index=0)
    # グラフ表示
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 投資推移")
        show_investment_trend_chart(selected_brand, selected_method)
    with col2:
        st.subheader("💹 損益推移")
        show_profit_loss_chart(selected_brand, selected_method)

def show_data_input():
    # 入力モード選択
    st.subheader("入力モード選択")
    input_mode = st.radio("入力モード", ["新規登録", "継続入力（パフォーマンス）"], index=1, horizontal=True)

    # 新規登録時は開始年月入力欄を表示
    if input_mode == "新規登録":
        st.markdown("**新規登録：開始年月を入力してください**")
        start_year = st.selectbox("開始年", range(2000, 2031), index=24)
        start_month = st.selectbox("開始月", range(1, 13), index=datetime.now().month-1)
    """データ入力・編集画面"""
    st.header("📝 月次データ管理")
    
    # --- 一括登録 ---
    st.subheader("🔢 複数銘柄一括登録")
    empty_rows = 10
    default_bulk_df = pd.DataFrame({
        "年": [datetime.now().year] * empty_rows,
        "月": [datetime.now().month] * empty_rows,
        "銘柄": ["" for _ in range(empty_rows)],
        "投資方法": ["" for _ in range(empty_rows)],
        "証券会社": ["" for _ in range(empty_rows)],
        "投資額": [0 for _ in range(empty_rows)],
        "評価額": [0 for _ in range(empty_rows)],
        "備考": ["" for _ in range(empty_rows)]
    })
    bulk_df = st.data_editor(
        default_bulk_df,
        num_rows="dynamic",
        column_config={
            "年": st.column_config.NumberColumn("年", min_value=2020, max_value=2030, step=1, format="%d"),
            "月": st.column_config.NumberColumn("月", min_value=1, max_value=12, step=1, format="%d"),
            "銘柄": st.column_config.TextColumn("銘柄"),
            "投資方法": st.column_config.TextColumn("投資方法"),
            "証券会社": st.column_config.TextColumn("証券会社"),
            "投資額": st.column_config.NumberColumn("投資額（円）", min_value=0, step=1000, format="¥%.0f"),
            "評価額": st.column_config.NumberColumn("評価額（円）", min_value=0, step=1000, format="¥%.0f"),
            "備考": st.column_config.TextColumn("備考")
        },
        key="bulk_register_editor"
    )
    if st.button("一括登録", key="bulk_register_btn"):
        from investment_simulation.core.nisa_utils import add_bulk_records
        st.session_state.nisa_data = add_bulk_records(st.session_state.nisa_data, bulk_df)
        st.success("一括登録が完了しました")
        st.rerun()
    # 新規データ追加フォーム
    st.subheader("➕ 新規データ追加")
    
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 2, 3, 3, 3, 3, 2, 3])
    with col1:
        if input_mode == "新規登録":
            year = start_year
        else:
            year = st.selectbox("年", range(2020, 2030), index=4)
    with col2:
        if input_mode == "新規登録":
            month = start_month
        else:
            month = st.selectbox("月", range(1, 13), index=datetime.now().month-1)
    # 過去データから銘柄・投資方法リスト抽出
    brand_options = []
    method_options = []
    if not st.session_state.nisa_data.empty:
        # 銘柄（カンマ区切りを分割してユニーク化）
        brands_raw = st.session_state.nisa_data['銘柄'].dropna().astype(str).tolist()
        brand_options = sorted(set([b.strip() for line in brands_raw for b in line.split(',') if b.strip()]))
        method_options = sorted(set(st.session_state.nisa_data['投資方法'].dropna().astype(str).tolist()))

    with col3:
        if input_mode == "継続入力（パフォーマンス）" and brand_options:
            selected_brands = st.multiselect("銘柄（選択/追加可）", options=brand_options, default=brand_options[:1])
            new_brand = st.text_input("新規銘柄追加（カンマ区切り可）", value="")
            # 選択＋新規追加を合成
            brand = ','.join(selected_brands + ([new_brand] if new_brand else []))
        else:
            brand = st.text_input("銘柄（複数はカンマ区切り）", value="")
    with col4:
        if input_mode == "継続入力（パフォーマンス）" and method_options:
            method = st.selectbox("投資方法（選択/追加可）", options=["新規入力"] + method_options, index=1 if method_options else 0)
            if method == "新規入力":
                method = st.text_input("新規投資方法入力", value="")
        else:
            method = st.text_input("投資方法", value="")
    with col5:
        broker = st.text_input("証券会社", value="")
    with col6:
        note = st.text_input("備考", value="")
    with col5:
        investment = st.number_input("投資額（円）", min_value=0, value=0, step=1000)
    with col6:
        evaluation = st.number_input("評価額（円）", min_value=0, value=0, step=1000)
    with col7:
        if st.button("追加", use_container_width=True):
            st.session_state.nisa_data = add_monthly_record(
                st.session_state.nisa_data, year, month, investment, evaluation, brands=brand, note=note, method=method, broker=broker
            )
            st.success("✅ データを追加しました")
            st.rerun()
    
    # データ編集テーブル
    st.subheader("📋 データ編集")
    
    if not st.session_state.nisa_data.empty:
        # 銘柄・備考カラムのNaNを空文字に変換し、str型に統一
        df_edit = st.session_state.nisa_data.copy()
        for col in ['銘柄', '備考', '投資方法', '証券会社']:
            if col in df_edit.columns:
                df_edit[col] = df_edit[col].fillna('').astype(str)
        # データ編集
        edited_data = st.data_editor(
            df_edit,
            width='stretch',
            num_rows="dynamic",
            column_config={
                "年": st.column_config.NumberColumn(
                    "年",
                    min_value=2020,
                    max_value=2030,
                    step=1,
                    format="%d"
                ),
                "月": st.column_config.NumberColumn(
                    "月",
                    min_value=1,
                    max_value=12,
                    step=1,
                    format="%d"
                ),
                "銘柄": st.column_config.TextColumn("銘柄"),
                "投資方法": st.column_config.TextColumn("投資方法"),
                "証券会社": st.column_config.TextColumn("証券会社"),
                "投資額": st.column_config.NumberColumn(
                    "投資額（円）",
                    min_value=0,
                    step=1000,
                    format="¥%.0f"
                ),
                "評価額": st.column_config.NumberColumn(
                    "評価額（円）",
                    min_value=0,
                    step=1000,
                    format="¥%.0f"
                ),
                "累計投資額": st.column_config.NumberColumn(
                    "累計投資額（円）",
                    disabled=True,
                    format="¥%.0f"
                ),
                "累計評価額": st.column_config.NumberColumn(
                    "累計評価額（円）",
                    disabled=True,
                    format="¥%.0f"
                ),
                "損益": st.column_config.NumberColumn(
                    "損益（円）",
                    disabled=True,
                    format="¥%.0f"
                ),
                "累計損益": st.column_config.NumberColumn(
                    "累計損益（円）",
                    disabled=True,
                    format="¥%.0f"
                ),
                "損益率": st.column_config.NumberColumn(
                    "損益率（%）",
                    disabled=True,
                    format="%.2f%%"
                ),
                "備考": st.column_config.TextColumn("備考"),
            }
        )
        # データの更新
        if not edited_data.equals(st.session_state.nisa_data):
            # 文字列カラムをstr型に統一
            for col in ['銘柄', '備考', '投資方法']:
                if col in edited_data.columns:
                    edited_data[col] = edited_data[col].fillna('').astype(str)
            st.session_state.nisa_data = calculate_cumulative_values(edited_data)
            st.success("✅ データを更新しました")
            st.rerun()
    else:
        st.info("データがありません。上記フォームからデータを追加してください。")

def show_detailed_analysis():
    """詳細分析画面"""
    st.header("📊 詳細分析")
    
    if st.session_state.nisa_data.empty or len(st.session_state.nisa_data) < 2:
        st.info("分析には2ヶ月以上のデータが必要です。")
        return
    
    analyzer = InvestmentAnalyzer(st.session_state.nisa_data)
    calculator = NISACalculator(st.session_state.nisa_data)
    
    # リスク指標
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚡ リスク指標")
        risk_metrics = analyzer.calculate_risk_metrics()
        
        st.metric("年率ボラティリティ", f"{risk_metrics['volatility']:.2f}%")
        st.metric("最大ドローダウン", f"{risk_metrics['max_drawdown']:.2f}%")
        st.metric("VaR (95%)", f"{risk_metrics['var_95']:.2f}%")
        st.metric("シャープレシオ", f"{risk_metrics['sharpe_ratio']:.3f}")
    
    with col2:
        st.subheader("📈 投資効率")
        efficiency = analyzer.analyze_investment_efficiency()
        
        st.metric("年率リターン", f"{efficiency['annualized_return']:.2f}%")
        st.metric("コスト効率", f"¥{efficiency['cost_efficiency']:,.0f}")
        st.metric("投資一貫性", f"{efficiency['investment_consistency']:.3f}")
        st.metric("CAGR", f"{calculator.calculate_annual_return():.2f}%")
    
    # 複利効果分析
    st.subheader("🔄 複利効果分析")
    compound_analysis = analyzer.calculate_compound_interest_effect()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "複利の恩恵", 
            f"¥{compound_analysis['compound_benefit']:,.0f}",
            help="複利運用と単利運用の差額"
        )
    
    with col2:
        if compound_analysis['simple_vs_compound']['simple'] > 0:
            benefit_ratio = (compound_analysis['compound_benefit'] / compound_analysis['simple_vs_compound']['simple']) * 100
            st.metric("恩恵率", f"{benefit_ratio:.2f}%")
    
    # 複利効果グラフ
    if compound_analysis['compound_progression']:
        show_compound_effect_chart(compound_analysis)
    
    # 月次リターン分析
    st.subheader("📅 月次パフォーマンス")
    show_monthly_return_chart(analyzer)

def show_future_projection(future_months: int, expected_return: float):
    """将来予測画面"""
    st.header("🔮 将来予測シミュレーション")
    
    if st.session_state.nisa_data.empty:
        st.info("予測にはデータが必要です。")
        return
    
    analyzer = InvestmentAnalyzer(st.session_state.nisa_data)
    calculator = NISACalculator(st.session_state.nisa_data)
    
    # 予測パラメーター
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_investment = st.number_input(
            "月次投資額（円）", 
            min_value=0, 
            value=30000, 
            step=5000,
            help="将来の月次投資予定額"
        )
    
    with col2:
        st.metric("設定年利", f"{expected_return:.1f}%")
    
    # 将来価値計算
    projection = calculator.project_future_value(future_months, monthly_investment, expected_return)
    
    # 予測結果表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            f"{future_months}ヶ月後の予測評価額",
            f"¥{projection['future_value']:,.0f}"
        )
    
    with col2:
        st.metric(
            f"{future_months}ヶ月後の累計投資額",
            f"¥{projection['total_investment']:,.0f}"
        )
    
    with col3:
        color = "normal" if projection['projected_profit'] >= 0 else "inverse"
        st.metric(
            "予測損益",
            f"¥{projection['projected_profit']:,.0f}",
            delta=f"{projection['projected_return_rate']:.2f}%",
            delta_color=color
        )
    
    # シナリオ分析
    st.subheader("📊 シナリオ分析")
    scenarios = analyzer.generate_future_scenarios(future_months)
    show_scenario_chart(scenarios, future_months)

def show_data_details():
    """データ詳細画面"""
    st.header("📋 データ詳細")
    
    if st.session_state.nisa_data.empty:
        st.info("データがありません。")
        return
    
    # データ統計
    st.subheader("📊 データ統計")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**基本統計**")
        numeric_columns = ['投資額', '評価額', '損益', '損益率']
        stats = st.session_state.nisa_data[numeric_columns].describe()
        st.dataframe(stats, use_container_width=True)
    
    with col2:
        st.write("**データ品質**")
        data_quality = {
            "総レコード数": len(st.session_state.nisa_data),
            "アクティブな投資月": len(st.session_state.nisa_data[st.session_state.nisa_data['投資額'] > 0]),
            "データ期間": f"{st.session_state.nisa_data['年'].min()}年{st.session_state.nisa_data['月'].min()}月 - {st.session_state.nisa_data['年'].max()}年{st.session_state.nisa_data['月'].max()}月",
            "完全性": f"{((st.session_state.nisa_data['投資額'] > 0).sum() / len(st.session_state.nisa_data) * 100):.1f}%"
        }
        
        for key, value in data_quality.items():
            st.metric(key, value)
    
    # 生データ表示
    st.subheader("🗂️ 全データ")
    st.dataframe(st.session_state.nisa_data, use_container_width=True)

def show_investment_trend_chart(selected_brand=None, selected_method=None):
    """投資推移チャート（銘柄・投資方法対応）"""
    df = st.session_state.nisa_data.copy()
    if selected_brand and selected_brand != "全体":
        df = df[df['銘柄'] == selected_brand]
    if selected_method and selected_method != "全体" and '投資方法' in df.columns:
        df = df[df['投資方法'] == selected_method]
    df = df.sort_values(['年', '月'])
    df['年月'] = df['年'].astype(str) + '/' + df['月'].astype(str).str.zfill(2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['年月'],
        y=df['累計投資額'],
        mode='lines+markers',
        name='累計投資額',
        line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df['年月'],
        y=df['累計評価額'],
        mode='lines+markers',
        name='累計評価額',
        line=dict(color='green', width=2)
    ))
    title = "投資額vs評価額推移"
    if selected_brand and selected_brand != "全体":
        title += f"（{selected_brand}）"
    if selected_method and selected_method != "全体":
        title += f"[{selected_method}]"
    fig.update_layout(
        title=title,
        xaxis_title="年月",
        yaxis_title="金額（円）",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def show_profit_loss_chart(selected_brand=None, selected_method=None):
    """損益チャート（銘柄・投資方法対応）"""
    df = st.session_state.nisa_data.copy()
    if selected_brand and selected_brand != "全体":
        df = df[df['銘柄'] == selected_brand]
    if selected_method and selected_method != "全体" and '投資方法' in df.columns:
        df = df[df['投資方法'] == selected_method]
    df = df.sort_values(['年', '月'])
    df['年月'] = df['年'].astype(str) + '/' + df['月'].astype(str).str.zfill(2)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # 損益額
    fig.add_trace(
        go.Bar(
            x=df['年月'],
            y=df['累計損益'],
            name='累計損益（円）',
            marker_color=np.where(df['累計損益'] >= 0, 'green', 'red'),
            opacity=0.7
        ),
        secondary_y=False,
    )
    # 損益率
    fig.add_trace(
        go.Scatter(
            x=df['年月'],
            y=df['損益率'],
            mode='lines+markers',
            name='損益率（%）',
            line=dict(color='orange', width=2)
        ),
        secondary_y=True,
    )
    title = "損益推移"
    if selected_brand and selected_brand != "全体":
        title += f"（{selected_brand}）"
    if selected_method and selected_method != "全体":
        title += f"[{selected_method}]"
    fig.update_xaxes(title_text="年月")
    fig.update_yaxes(title_text="損益（円）", secondary_y=False)
    fig.update_yaxes(title_text="損益率（%）", secondary_y=True)
    fig.update_layout(
        title=title,
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def show_compound_effect_chart(compound_analysis):
    """複利効果チャート"""
    months = list(range(1, len(compound_analysis['compound_progression']) + 1))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=compound_analysis['simple_progression'],
        mode='lines',
        name='単利運用',
        line=dict(color='blue', dash='dash', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=months,
        y=compound_analysis['compound_progression'],
        mode='lines',
        name='複利運用（実績）',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title="複利効果の比較",
        xaxis_title="投資期間（月）",
        yaxis_title="評価額（円）",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_monthly_return_chart(analyzer):
    """月次リターンチャート"""
    if hasattr(analyzer, 'monthly_data') and not analyzer.monthly_data.empty:
        df = analyzer.monthly_data.copy()
        df['年月'] = df['年'].astype(str) + '/' + df['月'].astype(str).str.zfill(2)
        
        fig = go.Figure()
        
        colors = np.where(df['月次リターン率'] >= 0, 'green', 'red')
        
        fig.add_trace(go.Bar(
            x=df['年月'],
            y=df['月次リターン率'],
            name='月次リターン率',
            marker_color=colors,
            opacity=0.7
        ))
        
        fig.update_layout(
            title="月次リターン率",
            xaxis_title="年月",
            yaxis_title="リターン率（%）",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_scenario_chart(scenarios, future_months):
    """シナリオチャート"""
    months = list(range(1, future_months + 1))
    
    fig = go.Figure()
    
    for scenario_name, values in scenarios.items():
        fig.add_trace(go.Scatter(
            x=months,
            y=values,
            mode='lines',
            name=f'年利{scenario_name}',
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title="将来価値シナリオ分析",
        xaxis_title="期間（月）",
        yaxis_title="予測評価額（円）",
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()