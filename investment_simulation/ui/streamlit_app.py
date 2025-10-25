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
    from investment_simulation.core.brand_master import get_brand_master
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

if 'brand_master' not in st.session_state:
    st.session_state.brand_master = get_brand_master()
    # 既存データからマスタへ自動インポート
    if not st.session_state.nisa_data.empty:
        result = st.session_state.brand_master.import_from_dataframe(st.session_state.nisa_data)
        if result['brands'] > 0 or result['methods'] > 0 or result['brokers'] > 0:
            print(f"マスタへ自動インポート: 銘柄{result['brands']}件, 投資方法{result['methods']}件, 証券会社{result['brokers']}件")

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
    tab1, tab2, tab3 = st.tabs([
        "📝 銘柄登録・データ管理", 
        "🔧 マスタ管理",
        "📊 パフォーマンス分析・積立シナリオ"
    ])

    with tab1:
        show_data_input()

    with tab2:
        show_brand_master_management()

    with tab3:
        show_performance_and_scenario()


def show_brand_master_management():
    """
    銘柄マスタ管理画面
    """
    st.header("🔧 マスタ管理")
    st.markdown("銘柄・投資方法・証券会社の初期登録・編集を行います。")
    
    master = st.session_state.brand_master
    
    # サブタブ
    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "🏷️ 銘柄マスタ",
        "📈 投資方法",
        "🏦 証券会社"
    ])
    
    # ========== 銘柄マスタ ==========
    with sub_tab1:
        st.subheader("🏷️ 銘柄マスタ")
        
        # 新規銘柄登録
        with st.expander("➕ 新規銘柄登録", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_code = st.text_input("銘柄コード*", key="new_brand_code", 
                                        help="ティッカーシンボル、ファンドコード等")
            with col2:
                new_name = st.text_input("銘柄名*", key="new_brand_name")
            
            col3, col4, col5, col6 = st.columns(4)
            with col3:
                broker_options = master.get_brokers()
                new_broker = st.selectbox("証券会社", [""] + broker_options, key="new_brand_broker")
            with col4:
                account_options = ["積立NISA", "特定", "NISA"]
                new_account = st.selectbox("口座", account_options, key="new_brand_account", index=1)
            with col5:
                categories = ["ETF", "投資信託", "個別株", "債券", "その他"]
                new_category = st.selectbox("カテゴリ", categories, key="new_brand_category")
            with col6:
                regions = ["米国", "日本", "全世界", "先進国", "新興国", "その他"]
                new_region = st.selectbox("地域", regions, key="new_brand_region")
            
            if st.button("銘柄を追加", use_container_width=True, type="primary"):
                if new_code and new_name:
                    if master.add_brand(new_code, new_name, new_broker, new_account, new_category, new_region):
                        st.success(f"✅ 銘柄 '{new_code}' を追加しました")
                        st.rerun()
                    else:
                        st.error(f"❌ 銘柄コード '{new_code}' は既に登録されています")
                else:
                    st.warning("銘柄コードと銘柄名は必須です")
        
        # 既存銘柄一覧
        st.markdown("---")
        st.subheader("📋 登録済み銘柄")
        
        # フィルタ
        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.selectbox(
                "カテゴリで絞込",
                ["全て"] + master.get_categories(),
                key="filter_category"
            )
        with col2:
            filter_region = st.selectbox(
                "地域で絞込",
                ["全て"] + master.get_regions(),
                key="filter_region"
            )
        
        # 銘柄リスト取得
        brands = master.get_brands(
            category=None if filter_category == "全て" else filter_category,
            region=None if filter_region == "全て" else filter_region
        )
        
        if brands:
            # DataFrameで表示
            df_brands = pd.DataFrame(brands)
            # 必要なカラムのみ選択（存在確認）
            display_cols = ['code', 'name', 'broker', 'account', 'category', 'region']
            available_cols = [col for col in display_cols if col in df_brands.columns]
            df_brands = df_brands[available_cols]
            
            # カラム名を日本語に変更
            col_mapping = {
                'code': 'コード',
                'name': '銘柄名',
                'broker': '証券会社',
                'account': '口座',
                'category': 'カテゴリ',
                'region': '地域'
            }
            df_brands.columns = [col_mapping.get(col, col) for col in df_brands.columns]
            
            edited_brands = st.data_editor(
                df_brands,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "コード": st.column_config.TextColumn("コード", width="small", disabled=True),
                    "銘柄名": st.column_config.TextColumn("銘柄名", width="large"),
                    "証券会社": st.column_config.SelectboxColumn(
                        "証券会社",
                        options=[""] + master.get_brokers(),
                        width="medium"
                    ),
                    "口座": st.column_config.SelectboxColumn(
                        "口座",
                        options=["積立NISA", "特定", "NISA"],
                        width="small"
                    ),
                    "カテゴリ": st.column_config.SelectboxColumn(
                        "カテゴリ",
                        options=["ETF", "投資信託", "個別株", "債券", "その他"],
                        width="small"
                    ),
                    "地域": st.column_config.SelectboxColumn(
                        "地域",
                        options=["米国", "日本", "全世界", "先進国", "新興国", "その他"],
                        width="small"
                    )
                },
                hide_index=True,
                key="brand_editor"
            )
            
            # 更新・削除ボタン
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("💾 変更を保存", use_container_width=True):
                    # 更新処理
                    for idx in range(len(edited_brands)):
                        row = edited_brands.iloc[idx]
                        original = brands[idx]
                        if row['コード'] == original['code']:
                            # 変更があった場合のみ更新
                            changes = {}
                            if '銘柄名' in row and row['銘柄名'] != original.get('name'):
                                changes['name'] = row['銘柄名']
                            if '証券会社' in row and row['証券会社'] != original.get('broker', ''):
                                changes['broker'] = row['証券会社']
                            if '口座' in row and row['口座'] != original.get('account', '特定'):
                                changes['account'] = row['口座']
                            if 'カテゴリ' in row and row['カテゴリ'] != original.get('category'):
                                changes['category'] = row['カテゴリ']
                            if '地域' in row and row['地域'] != original.get('region'):
                                changes['region'] = row['地域']
                            
                            if changes:
                                master.update_brand(row['コード'], **changes)
                    st.success("✅ 変更を保存しました")
                    st.rerun()
            
            with col2:
                st.info(f"登録銘柄数: {len(brands)}件")
        else:
            st.info("該当する銘柄がありません")
        
        # 削除機能
        st.markdown("---")
        with st.expander("🗑️ 銘柄削除", expanded=False):
            delete_code = st.selectbox(
                "削除する銘柄を選択",
                master.get_brand_code_list(),
                key="delete_brand_code"
            )
            if st.button("削除実行", use_container_width=True, type="secondary"):
                if master.delete_brand(delete_code):
                    st.success(f"✅ 銘柄 '{delete_code}' を削除しました")
                    st.rerun()
                else:
                    st.error(f"❌ 削除に失敗しました")
    
    # ========== 投資方法 ==========
    with sub_tab2:
        st.subheader("📈 投資方法マスタ")
        
        # 新規追加
        col1, col2 = st.columns([3, 1])
        with col1:
            new_method = st.text_input("新規投資方法", key="new_method")
        with col2:
            st.write("")  # スペーサー
            st.write("")
            if st.button("追加", key="add_method", use_container_width=True):
                if new_method:
                    if master.add_method(new_method):
                        st.success(f"✅ '{new_method}' を追加しました")
                        st.rerun()
                    else:
                        st.error("既に登録されています")
                else:
                    st.warning("投資方法名を入力してください")
        
        # 既存一覧
        st.markdown("---")
        methods = master.get_methods()
        if methods:
            st.write(f"**登録済み投資方法（{len(methods)}件）:**")
            for method in methods:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"• {method}")
                with col2:
                    if st.button("🗑️", key=f"del_method_{method}"):
                        if master.delete_method(method):
                            st.success(f"✅ '{method}' を削除しました")
                            st.rerun()
        else:
            st.info("登録されている投資方法がありません")
    
    # ========== 証券会社 ==========
    with sub_tab3:
        st.subheader("🏦 証券会社マスタ")
        
        # 新規追加
        col1, col2 = st.columns([3, 1])
        with col1:
            new_broker = st.text_input("新規証券会社", key="new_broker")
        with col2:
            st.write("")  # スペーサー
            st.write("")
            if st.button("追加", key="add_broker", use_container_width=True):
                if new_broker:
                    if master.add_broker(new_broker):
                        st.success(f"✅ '{new_broker}' を追加しました")
                        st.rerun()
                    else:
                        st.error("既に登録されています")
                else:
                    st.warning("証券会社名を入力してください")
        
        # 既存一覧
        st.markdown("---")
        brokers = master.get_brokers()
        if brokers:
            st.write(f"**登録済み証券会社（{len(brokers)}件）:**")
            for broker in brokers:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"• {broker}")
                with col2:
                    if st.button("🗑️", key=f"del_broker_{broker}"):
                        if master.delete_broker(broker):
                            st.success(f"✅ '{broker}' を削除しました")
                            st.rerun()
        else:
            st.info("登録されている証券会社がありません")
    
    # リセット機能
    st.markdown("---")
    with st.expander("⚠️ マスタデータのリセット", expanded=False):
        st.warning("すべてのマスタデータをデフォルトに戻します。この操作は取り消せません。")
        if st.button("デフォルトにリセット", type="secondary"):
            master.reset_to_default()
            st.success("✅ マスタデータをリセットしました")
            st.rerun()


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
    master = st.session_state.brand_master
    brand_display_options = master.get_brand_display_list()
    brand_code_options = master.get_brand_code_list()
    method_options = master.get_methods()
    broker_options = master.get_brokers()
    
    # 過去データからも抽出（マスタにない場合に備えて）
    if not st.session_state.nisa_data.empty:
        brands_raw = st.session_state.nisa_data['銘柄'].dropna().astype(str).tolist()
        historical_brands = sorted(set([b.strip() for line in brands_raw for b in line.split(',') if b.strip()]))
        # マスタにない銘柄を追加
        for b in historical_brands:
            if b not in brand_code_options:
                brand_code_options.append(b)
                brand_display_options.append(b)

    with col3:
        if input_mode == "継続入力（パフォーマンス）" and brand_display_options:
            selected_brand_display = st.selectbox(
                "銘柄選択",
                ["新規入力"] + brand_display_options,
                key="select_brand_input"
            )
            if selected_brand_display == "新規入力":
                brand = st.text_input("新規銘柄入力（カンマ区切り可）", value="", key="manual_brand_input")
            else:
                # "コード: 名前" から コードを抽出
                brand = selected_brand_display.split(':')[0].strip()
                st.caption(f"選択: {brand}")
        else:
            # マスタから選択または手動入力
            brand_input_mode = st.radio(
                "銘柄入力方法",
                ["マスタから選択", "手動入力"],
                horizontal=True,
                key="brand_input_mode"
            )
            if brand_input_mode == "マスタから選択" and brand_display_options:
                selected_brand_display = st.selectbox(
                    "銘柄選択",
                    brand_display_options,
                    key="select_brand_master"
                )
                brand = selected_brand_display.split(':')[0].strip()
            else:
                brand = st.text_input("銘柄（複数はカンマ区切り）", value="", key="manual_brand")
    
    with col4:
        if method_options:
            method_input_mode = st.radio(
                "投資方法入力",
                ["マスタから選択", "手動入力"],
                horizontal=True,
                key="method_input_mode"
            )
            if method_input_mode == "マスタから選択":
                method = st.selectbox("投資方法選択", method_options, key="select_method")
            else:
                method = st.text_input("投資方法入力", value="", key="manual_method")
        else:
            method = st.text_input("投資方法", value="", key="method_only")
    
    with col5:
        if broker_options:
            broker_input_mode = st.radio(
                "証券会社入力",
                ["マスタから選択", "手動入力"],
                horizontal=True,
                key="broker_input_mode"
            )
            if broker_input_mode == "マスタから選択":
                broker = st.selectbox("証券会社選択", broker_options, key="select_broker")
            else:
                broker = st.text_input("証券会社入力", value="", key="manual_broker")
        else:
            broker = st.text_input("証券会社", value="", key="broker_only")
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