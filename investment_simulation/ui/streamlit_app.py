# NISA投資シミュレーション・マスタ管理アプリ
# 銘柄・投資方法・証券会社のマスタ管理 + 月次データ入力

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
from pathlib import Path

# モジュールのインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)).rsplit(os.sep, 2)[0])

try:
    from investment_simulation.core.brand_master import get_brand_master
    from investment_simulation.core.nisa_utils import (
        load_nisa_data, save_nisa_data, add_monthly_record,
        calculate_cumulative_values
    )
    from investment_simulation.ui.monthly_data_input import show_monthly_data_input
except ImportError as e:
    st.error(f"モジュールのインポートエラー: {e}")
    st.stop()

# ページ設定
st.set_page_config(
    page_title="NISA銘柄マスタ管理",
    page_icon="🏷️",
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


NISA_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "nisa_monthly_data.csv"


@st.cache_resource
def _load_brand_master_resource():
    return get_brand_master()


def _get_nisa_data_mtime() -> float:
    return NISA_DATA_FILE.stat().st_mtime if NISA_DATA_FILE.exists() else 0.0


@st.cache_data(show_spinner=False)
def _load_nisa_data_cached(file_mtime: float) -> pd.DataFrame:
    _ = file_mtime
    return load_nisa_data()


def _ensure_session_state() -> None:
    if 'brand_master' not in st.session_state:
        st.session_state.brand_master = _load_brand_master_resource()
    if 'nisa_data' not in st.session_state:
        st.session_state.nisa_data = _load_nisa_data_cached(_get_nisa_data_mtime())

def main():
    _ensure_session_state()

    # サイドバー
    with st.sidebar:
        st.header("🎯 設定")
        
        # データ保存・読込
        st.subheader("📁 データ管理")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 保存", key="save_data_btn"):
                if save_nisa_data(st.session_state.nisa_data):
                    _load_nisa_data_cached.clear()
                    st.success("✅ 保存完了")
                else:
                    st.error("❌ 保存失敗")
        with col2:
            if st.button("🔄 再読込", key="reload_data_btn"):
                _load_nisa_data_cached.clear()
                st.session_state.nisa_data = _load_nisa_data_cached(_get_nisa_data_mtime())
                st.success("✅ 再読込完了")
                st.rerun()
    
    # メインコンテンツ
    st.title("🏷️ NISA投資管理システム")
    st.markdown("---")
    
    # タブ構成
    tab1, tab2 = st.tabs([
        "🔧 マスタ管理",
        "📝 月次データ入力"
    ])
    
    with tab1:
        show_brand_master_management()
    
    with tab2:
        st.session_state.nisa_data = show_monthly_data_input(
            st.session_state.brand_master,
            st.session_state.nisa_data,
            add_monthly_record,
            calculate_cumulative_values
        )


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
        st.subheader("🏷️ 銘柄管理（表形式入力）")
        
        st.info("💡 表を直接編集して銘柄情報を入力・更新してください。現在価格・利益額・購入開始時期を入力すると、元本・利率・年利が自動計算されます。")
        
        # 銘柄リスト取得
        brands = master.get_brands()
        
        if brands:
            # DataFrameで表示
            df_brands = pd.DataFrame(brands)
            # 必要なカラムのみ選択（存在確認）
            display_cols = ['code', 'name', 'broker', 'account', 'category', 'region', 
                          'current_price', 'profit', 'investment_date', 
                          'principal', 'profit_rate', 'annual_return']
            available_cols = [col for col in display_cols if col in df_brands.columns]
            df_brands = df_brands[available_cols]
            
            # investment_dateを日付型に変換（空文字列はNaTに）
            if 'investment_date' in df_brands.columns:
                df_brands['investment_date'] = pd.to_datetime(df_brands['investment_date'], errors='coerce')
            
            # カラム名を日本語に変更
            col_mapping = {
                'code': 'コード',
                'name': '銘柄名',
                'broker': '証券会社',
                'account': '口座',
                'category': 'カテゴリ',
                'region': '地域',
                'current_price': '現在価格',
                'profit': '利益額',
                'investment_date': '購入開始時期',
                'principal': '元本',
                'profit_rate': '利率(%)',
                'annual_return': '年利(%)'
            }
            df_brands.columns = [col_mapping.get(col, col) for col in df_brands.columns]
            
            edited_brands = st.data_editor(
                df_brands,
                width='stretch',
                num_rows="fixed",
                column_config={
                    "コード": st.column_config.TextColumn("コード", width="small", disabled=True),
                    "銘柄名": st.column_config.TextColumn("銘柄名", width="medium"),
                    "証券会社": st.column_config.SelectboxColumn(
                        "証券会社",
                        options=[""] + master.get_brokers(),
                        width="small"
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
                    ),
                    "現在価格": st.column_config.NumberColumn(
                        "現在価格",
                        help="現在の評価額（円）",
                        min_value=0.0,
                        format="¥%.0f",
                        width="small"
                    ),
                    "利益額": st.column_config.NumberColumn(
                        "利益額",
                        help="利益額（円）",
                        format="¥%.0f",
                        width="small"
                    ),
                    "購入開始時期": st.column_config.DateColumn(
                        "購入開始時期",
                        help="購入を開始した年月日（YYYY-MM-DD形式）",
                        format="YYYY-MM-DD",
                        width="small"
                    ),
                    "元本": st.column_config.NumberColumn(
                        "元本",
                        help="自動計算（現在価格 - 利益額）",
                        format="¥%.0f",
                        width="small",
                        disabled=True
                    ),
                    "利率(%)": st.column_config.NumberColumn(
                        "利率(%)",
                        help="自動計算（利益額 / 元本 × 100）",
                        format="%.2f%%",
                        width="small",
                        disabled=True
                    ),
                    "年利(%)": st.column_config.NumberColumn(
                        "年利(%)",
                        help="自動計算（年平均利回り）",
                        format="%.2f%%",
                        width="small",
                        disabled=True
                    )
                },
                hide_index=True,
                key="brand_editor"
            )
            
            # 更新ボタン
            if st.button("💾 変更を保存", key="save_brands_btn"):
                # 更新処理
                updated_count = 0
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
                        if '現在価格' in row and row['現在価格'] != original.get('current_price', 0.0):
                            changes['current_price'] = row['現在価格']
                        if '利益額' in row and row['利益額'] != original.get('profit', 0.0):
                            changes['profit'] = row['利益額']
                        if '購入開始時期' in row:
                            # DateColumnはdatetimeオブジェクトを返すので文字列に変換
                            new_date = row['購入開始時期']
                            if pd.notna(new_date):
                                if hasattr(new_date, 'strftime'):
                                    new_date_str = new_date.strftime('%Y-%m-%d')
                                else:
                                    new_date_str = str(new_date)
                                if new_date_str != original.get('investment_date', ''):
                                    changes['investment_date'] = new_date_str
                        
                        if changes:
                            master.update_brand(row['コード'], **changes)
                            updated_count += 1
                
                if updated_count > 0:
                    st.success(f"✅ {updated_count}件の変更を保存しました")
                    st.rerun()
                else:
                    st.info("変更はありません")
            
            # 損益情報を表示（サマリー）
            total_current = sum([b.get('current_price', 0.0) for b in brands])
            total_profit = sum([b.get('profit', 0.0) for b in brands])
            total_principal = sum([b.get('principal', 0.0) for b in brands])
            avg_profit_rate = (total_profit / total_principal * 100) if total_principal > 0 else 0.0
            
            st.info(f"📊 銘柄数: {len(brands)}件 | 元本合計: ¥{total_principal:,.0f} | 評価額: ¥{total_current:,.0f} | 利益合計: ¥{total_profit:,.0f} | 平均利率: {avg_profit_rate:+.2f}%")
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
            if st.button("削除実行", key="delete_brand_btn", type="secondary"):
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
            if st.button("追加", key="add_method"):
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
            if st.button("追加", key="add_broker"):
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



if __name__ == "__main__":
    main()