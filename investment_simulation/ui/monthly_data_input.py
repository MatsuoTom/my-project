"""
月次データ入力モジュール
マスタと連動した月次投資データの入力・編集機能を提供
"""

import streamlit as st
import pandas as pd
from datetime import datetime


def show_monthly_data_input(master, nisa_data, add_monthly_record, calculate_cumulative_values):
    """
    月次データ入力画面（マスタ連動）
    
    Args:
        master: BrandMasterインスタンス
        nisa_data: 月次データのDataFrame
        add_monthly_record: 月次データ追加関数
        calculate_cumulative_values: 累計値計算関数
    
    Returns:
        更新された月次データのDataFrame
    """
    st.header("📝 月次投資データ入力")
    st.markdown("マスタに登録された銘柄を選択して、月次の投資データを入力します。")
    
    # 新規データ追加フォーム
    st.subheader("➕ 新規データ追加")
    
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 3, 3, 3, 3])
    
    with col1:
        year = st.selectbox("年", range(2020, 2031), index=datetime.now().year - 2020, key="input_year")
    
    with col2:
        month = st.selectbox("月", range(1, 13), index=datetime.now().month - 1, key="input_month")
    
    with col3:
        # マスタから銘柄選択
        brand_options = master.get_brand_display_list()
        if brand_options:
            selected_brand = st.selectbox(
                "銘柄選択",
                brand_options,
                key="monthly_brand_select"
            )
            # "コード: 名前" から コードを抽出
            brand_code = selected_brand.split(':')[0].strip() if ':' in selected_brand else selected_brand
        else:
            st.warning("銘柄マスタが空です")
            brand_code = ""
    
    with col4:
        # マスタから投資方法選択
        method_options = master.get_methods()
        if method_options:
            method = st.selectbox("投資方法", method_options, key="monthly_method_select")
        else:
            method = ""
    
    with col5:
        # マスタから証券会社選択
        broker_options = master.get_brokers()
        if broker_options:
            broker = st.selectbox("証券会社", broker_options, key="monthly_broker_select")
        else:
            broker = ""
    
    col7, col8, col9, col10 = st.columns([3, 3, 3, 2])
    
    with col7:
        investment = st.number_input("投資額（円）", min_value=0, value=0, step=1000, key="monthly_investment")
    
    with col8:
        evaluation = st.number_input("評価額（円）", min_value=0, value=0, step=1000, key="monthly_evaluation")
    
    with col9:
        note = st.text_input("備考", value="", key="monthly_note")
    
    with col10:
        st.write("")  # スペーサー
        st.write("")
        if st.button("追加", key="add_monthly_data_btn", type="primary"):
            if brand_code and method and broker:
                nisa_data = add_monthly_record(
                    nisa_data,
                    year,
                    month,
                    investment,
                    evaluation,
                    brands=brand_code,
                    note=note,
                    method=method,
                    broker=broker
                )
                st.success("✅ データを追加しました")
                st.rerun()
            else:
                st.error("銘柄、投資方法、証券会社を選択してください")
    
    # データ一覧表示
    st.markdown("---")
    st.subheader("📋 登録済みデータ")
    
    if not nisa_data.empty:
        # データ編集テーブル
        df_edit = nisa_data.copy()
        
        # 銘柄・備考カラムのNaNを空文字に変換
        for col in ['銘柄', '備考', '投資方法', '証券会社']:
            if col in df_edit.columns:
                df_edit[col] = df_edit[col].fillna('').astype(str)
        
        edited_data = st.data_editor(
            df_edit,
            width='stretch',
            num_rows="dynamic",
            column_config={
                "年": st.column_config.NumberColumn("年", min_value=2020, max_value=2030, step=1, format="%d"),
                "月": st.column_config.NumberColumn("月", min_value=1, max_value=12, step=1, format="%d"),
                "銘柄": st.column_config.TextColumn("銘柄"),
                "投資方法": st.column_config.SelectboxColumn(
                    "投資方法",
                    options=master.get_methods(),
                    width="small"
                ),
                "証券会社": st.column_config.SelectboxColumn(
                    "証券会社",
                    options=master.get_brokers(),
                    width="small"
                ),
                "投資額": st.column_config.NumberColumn("投資額（円）", min_value=0, step=1000, format="¥%.0f"),
                "評価額": st.column_config.NumberColumn("評価額（円）", min_value=0, step=1000, format="¥%.0f"),
                "累計投資額": st.column_config.NumberColumn("累計投資額（円）", disabled=True, format="¥%.0f"),
                "累計評価額": st.column_config.NumberColumn("累計評価額（円）", disabled=True, format="¥%.0f"),
                "損益": st.column_config.NumberColumn("損益（円）", disabled=True, format="¥%.0f"),
                "累計損益": st.column_config.NumberColumn("累計損益（円）", disabled=True, format="¥%.0f"),
                "損益率": st.column_config.NumberColumn("損益率（%）", disabled=True, format="%.2f%%"),
                "備考": st.column_config.TextColumn("備考"),
            },
            hide_index=True,
            key="monthly_data_editor"
        )
        
        # 保存ボタンを追加（自動更新を停止）
        if st.button("💾 データを保存", key="save_monthly_data_btn"):
            # 文字列カラムをstr型に統一
            for col in ['銘柄', '備考', '投資方法', '証券会社']:
                if col in edited_data.columns:
                    edited_data[col] = edited_data[col].fillna('').astype(str)
            nisa_data = calculate_cumulative_values(edited_data)
            st.success("✅ データを保存しました")
            st.rerun()
        
        # サマリー情報
        st.markdown("---")
        st.subheader("📊 サマリー")
        
        total_investment = nisa_data['累計投資額'].iloc[-1] if len(nisa_data) > 0 else 0
        total_evaluation = nisa_data['累計評価額'].iloc[-1] if len(nisa_data) > 0 else 0
        total_profit = total_evaluation - total_investment
        profit_rate = (total_profit / total_investment * 100) if total_investment > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("累計投資額", f"¥{total_investment:,.0f}")
        with col2:
            st.metric("現在評価額", f"¥{total_evaluation:,.0f}")
        with col3:
            st.metric("累計損益", f"¥{total_profit:,.0f}", delta=f"{profit_rate:+.2f}%")
        with col4:
            st.metric("データ数", f"{len(nisa_data)}件")
    else:
        st.info("データがありません。上記フォームからデータを追加してください。")
    
    return nisa_data
