"""
車両維持費 年間計画アプリ - Streamlit UI

年間計画ベースの維持費管理・シミュレーション
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from pathlib import Path
from typing import Dict, Any, Optional

from vehicle_finance.core.annual_plan_manager import AnnualPlanManager
from vehicle_finance.data.annual_plan_models import (
    VehicleInfo,
    AnnualMaintenancePlan,
    ActualExpense,
)


# ========================================
# ヘルパー関数
# ========================================

def render_expense_input_form(
    category: str,
    label: str,
    min_value: int = 0,
    value: int = 0,
    step: int = 1000,
    help_text: str = "",
    key_suffix: str = ""
) -> int:
    """
    費用入力フォームを生成する共通関数
    
    Args:
        category: カテゴリ名（表示用）
        label: 入力フィールドのラベル
        min_value: 最小値
        value: 初期値
        step: ステップ値
        help_text: ヘルプテキスト
        key_suffix: キーのサフィックス（重複回避用）
    
    Returns:
        入力された値
    """
    return st.number_input(
        label,
        min_value=min_value,
        value=value,
        step=step,
        help=help_text,
        key=f"{category}_{label}_{key_suffix}" if key_suffix else None
    )


def render_common_expense_inputs(
    existing_data: Optional[Any] = None,
    is_plan: bool = True,
    key_suffix: str = ""
) -> Dict[str, Any]:
    """
    共通の費用入力項目を生成
    
    Args:
        existing_data: 既存のデータ（AnnualMaintenancePlan または ActualExpense）
        is_plan: 計画入力かどうか（False=実績入力）
        key_suffix: キーのサフィックス
    
    Returns:
        入力された値の辞書
    """
    result = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        if is_plan:
            # 計画モード：燃料費の詳細入力
            st.markdown("**🚗 走行・燃料費**")
            result['annual_mileage'] = st.number_input(
                "年間走行距離（km）",
                min_value=0.0,
                value=float(existing_data.annual_mileage) if existing_data else 10000.0,
                step=1000.0,
                key=f"mileage_{key_suffix}"
            )
            result['fuel_efficiency'] = st.number_input(
                "燃費（km/L）",
                min_value=0.1,
                value=float(existing_data.fuel_efficiency) if existing_data else 15.0,
                step=0.5,
                key=f"efficiency_{key_suffix}"
            )
            result['fuel_price_per_liter'] = st.number_input(
                "燃料単価（円/L）",
                min_value=0.0,
                value=float(existing_data.fuel_price_per_liter) if existing_data else 160.0,
                step=1.0,
                key=f"fuel_price_{key_suffix}"
            )
        else:
            # 実績モード：燃料費の直接入力
            st.markdown("**🚗 燃料費**")
            result['fuel_cost'] = render_expense_input_form(
                "fuel", "燃料費（円）",
                value=int(existing_data.fuel_cost) if existing_data else 0,
                help_text="年間の実際のガソリン代・電気代",
                key_suffix=key_suffix
            )
        
        # 車検費用
        st.markdown("**🔧 車検費用**")
        if is_plan:
            result['inspection_year'] = st.checkbox(
                "車検実施年",
                value=existing_data.inspection_year if existing_data else False,
                key=f"inspection_year_{key_suffix}"
            )
            if result['inspection_year']:
                result['inspection_base_fee'] = render_expense_input_form(
                    "inspection", "車検基本料（円）",
                    value=int(existing_data.inspection_base_fee) if existing_data else 50000,
                    key_suffix=key_suffix
                )
                result['weight_tax'] = render_expense_input_form(
                    "weight", "重量税（円）",
                    value=int(existing_data.weight_tax) if existing_data else 32800,
                    key_suffix=key_suffix
                )
                result['liability_insurance'] = render_expense_input_form(
                    "liability", "自賠責保険（2年分）（円）",
                    value=int(existing_data.liability_insurance) if existing_data else 20010,
                    key_suffix=key_suffix
                )
                result['inspection_other'] = render_expense_input_form(
                    "insp_other", "その他費用（円）",
                    value=int(existing_data.inspection_other) if existing_data else 5000,
                    key_suffix=key_suffix
                )
            else:
                result['inspection_base_fee'] = 0
                result['weight_tax'] = 0
                result['liability_insurance'] = 0
                result['inspection_other'] = 0
        else:
            result['inspection_cost'] = render_expense_input_form(
                "inspection", "車検費用（円）",
                value=int(existing_data.inspection_cost) if existing_data else 0,
                help_text="車検基本料 + 重量税 + 自賠責保険等",
                key_suffix=key_suffix
            )
        
        # 保険・税金
        st.markdown("**🛡️ 保険・税金**")
        if is_plan:
            result['voluntary_insurance'] = render_expense_input_form(
                "insurance", "任意保険（年額）（円）",
                value=int(existing_data.voluntary_insurance) if existing_data else 60000,
                key_suffix=key_suffix
            )
            result['automobile_tax'] = render_expense_input_form(
                "tax", "自動車税（年額）（円）",
                value=int(existing_data.automobile_tax) if existing_data else 39500,
                step=500,
                key_suffix=key_suffix
            )
        else:
            result['insurance_cost'] = render_expense_input_form(
                "insurance", "任意保険料（円）",
                value=int(existing_data.insurance_cost) if existing_data else 0,
                help_text="年間の任意保険料",
                key_suffix=key_suffix
            )
            result['tax_cost'] = render_expense_input_form(
                "tax", "自動車税（円）",
                value=int(existing_data.tax_cost) if existing_data else 0,
                step=500,
                help_text="年間の自動車税・軽自動車税",
                key_suffix=key_suffix
            )
    
    with col2:
        # 駐車場代
        st.markdown("**🅿️ 駐車場代**")
        if is_plan:
            result['monthly_parking_fee'] = render_expense_input_form(
                "parking", "月額駐車場代（円）",
                value=int(existing_data.monthly_parking_fee) if existing_data else 10000,
                key_suffix=key_suffix
            )
        else:
            st.info("駐車場代は実績入力では不要です")
            result['parking_cost'] = 0
        
        # メンテナンス
        st.markdown("**🔧 メンテナンス費用**")
        if is_plan:
            result['oil_change_count'] = st.number_input(
                "オイル交換回数（年間）",
                min_value=0,
                value=existing_data.oil_change_count if existing_data else 2,
                step=1,
                key=f"oil_count_{key_suffix}"
            )
            result['oil_change_cost'] = render_expense_input_form(
                "oil", "オイル交換単価（円）",
                value=int(existing_data.oil_change_cost) if existing_data else 5000,
                step=500,
                key_suffix=key_suffix
            )
            result['tire_change'] = st.checkbox(
                "タイヤ交換",
                value=existing_data.tire_change if existing_data else False,
                key=f"tire_change_{key_suffix}"
            )
            result['tire_change_cost'] = render_expense_input_form(
                "tire", "タイヤ交換費用（円）",
                value=int(existing_data.tire_change_cost) if existing_data else 60000,
                step=5000,
                key_suffix=key_suffix
            )
            result['other_maintenance'] = render_expense_input_form(
                "maint_other", "その他メンテナンス（円）",
                value=int(existing_data.other_maintenance) if existing_data else 20000,
                key_suffix=key_suffix
            )
        else:
            # 実績入力でも詳細項目を表示
            result['oil_change_cost'] = render_expense_input_form(
                "oil", "オイル交換費用（円）",
                value=int(existing_data.oil_change_cost) if existing_data else 0,
                help_text="年間のオイル交換費用合計",
                key_suffix=key_suffix
            )
            result['tire_change_cost'] = render_expense_input_form(
                "tire", "タイヤ交換費用（円）",
                value=int(existing_data.tire_change_cost) if existing_data else 0,
                help_text="タイヤ交換した場合の費用",
                key_suffix=key_suffix
            )
            result['other_maintenance_cost'] = render_expense_input_form(
                "maint_other", "その他メンテナンス（円）",
                value=int(existing_data.other_maintenance_cost) if existing_data else 0,
                help_text="修理・点検・部品交換等",
                key_suffix=key_suffix
            )
        
        # その他
        st.markdown("**📦 その他費用**")
        if is_plan:
            result['car_wash'] = render_expense_input_form(
                "wash", "洗車・消耗品（年額）（円）",
                value=int(existing_data.car_wash) if existing_data else 12000,
                key_suffix=key_suffix
            )
            result['unexpected_expense'] = render_expense_input_form(
                "unexpected", "予備費（円）",
                value=int(existing_data.unexpected_expense) if existing_data else 30000,
                key_suffix=key_suffix
            )
        else:
            result['other_cost'] = render_expense_input_form(
                "other", "その他費用（円）",
                value=int(existing_data.other_cost) if existing_data else 0,
                help_text="洗車・消耗品・予備費等",
                key_suffix=key_suffix
            )
    
    return result


# ページ設定
st.set_page_config(
    page_title="車両維持費計画",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# タイトル
st.title("🚗 車両維持費 年間計画システム")
st.markdown("車の年間維持費を計画・シミュレーションするアプリケーションです")

# セッション状態の初期化
if "manager" not in st.session_state:
    st.session_state.manager = AnnualPlanManager()
    st.session_state.manager.load()

manager = st.session_state.manager

# サイドバー - 車両選択
st.sidebar.title("🚗 車両選択")

vehicles = manager.list_vehicles()
if vehicles:
    # デフォルト車両の決定：「テスト」を含む車両以外の最初の車両を優先
    default_vehicle = None
    non_test_vehicles = [
        v for v in vehicles 
        if "テスト" not in v and "test" not in v.lower()
    ]
    
    if non_test_vehicles:
        default_vehicle = non_test_vehicles[0]
    else:
        default_vehicle = vehicles[0]
    
    # デフォルトインデックスを設定
    try:
        default_index = vehicles.index(default_vehicle)
    except ValueError:
        default_index = 0
    
    selected_vehicle = st.sidebar.selectbox("車両を選択", vehicles, index=default_index)
else:
    selected_vehicle = None
    st.sidebar.info("車両が登録されていません。下記から新規登録してください。")

# サイドバー - 車両登録
with st.sidebar.expander("➕ 新規車両登録", expanded=not bool(vehicles)):
    with st.form("add_vehicle_form"):
        st.markdown("**車両情報を入力**")
        
        vehicle_name = st.text_input("車両名", placeholder="例: トヨタ プリウス")
        current_year = date.today().year
        ownership_start_year = st.number_input(
            "所有開始年", 
            min_value=1990, 
            max_value=current_year + 1, 
            value=current_year, 
            step=1
        )
        purchase_price = st.number_input("購入価格（円）", min_value=0, value=2000000, step=100000)
        vehicle_type = st.selectbox("車両区分", ["軽自動車", "普通車", "小型車", "大型車"])
        fuel_type = st.selectbox("燃料タイプ", ["ガソリン", "ハイブリッド", "電気", "ディーゼル"])
        displacement = st.number_input("排気量（cc）", min_value=0, value=1500, step=100)
        
        submit_vehicle = st.form_submit_button("車両を登録")
        
        if submit_vehicle:
            if not vehicle_name:
                st.error("車両名を入力してください")
            elif vehicle_name in vehicles:
                st.error(f"車両 '{vehicle_name}' は既に登録されています")
            else:
                try:
                    vehicle_info = VehicleInfo(
                        name=vehicle_name,
                        ownership_start_year=int(ownership_start_year),
                        purchase_price=float(purchase_price),
                        vehicle_type=vehicle_type,
                        fuel_type=fuel_type,
                        displacement=int(displacement) if displacement > 0 else None,
                    )
                    manager.add_vehicle_plan(vehicle_info)
                    
                    # デフォルトの10年計画を作成
                    manager.create_default_plan(vehicle_name, int(ownership_start_year), num_years=10)
                    
                    manager.save()
                    st.success(f"✅ 車両 '{vehicle_name}' を登録し、{ownership_start_year}年から10年間の計画を作成しました")
                    st.rerun()
                except Exception as e:
                    st.error(f"エラー: {e}")

# メインコンテンツ
if selected_vehicle:
    plan_obj = manager.get_vehicle_plan(selected_vehicle)
    
    if plan_obj:
        vehicle = plan_obj.vehicle_info
        
        # タブ構成
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 年間計画サマリー",
            "⚙️ 年度別設定",
            "📝 実績入力",
            "📈 長期シミュレーション",
            "💡 比較分析",
        ])
        
        # タブ1: 年間計画サマリー
        with tab1:
            st.subheader(f"📊 {selected_vehicle} - 年間計画サマリー")
            
            # 車両情報
            with st.expander("🚗 車両情報", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("所有開始年", f"{vehicle.ownership_start_year}年")
                with col2:
                    st.metric("購入価格", f"{vehicle.purchase_price:,.0f} 円")
                with col3:
                    st.metric("車両区分", vehicle.vehicle_type)
                with col4:
                    st.metric("燃料タイプ", vehicle.fuel_type)
            
            if plan_obj.annual_plans:
                # 今年の計画
                current_year = date.today().year
                current_plan = plan_obj.get_year_plan(current_year)
                
                if current_plan:
                    st.markdown(f"### 💰 {current_year}年の維持費計画")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("年間合計", f"{current_plan.total_annual_cost:,.0f} 円")
                    with col2:
                        st.metric("月平均", f"{current_plan.monthly_average_cost:,.0f} 円")
                    with col3:
                        inspection_status = "🔧 車検年" if current_plan.inspection_year else "通常年"
                        st.metric("年度区分", inspection_status)
                    
                    # 内訳
                    st.markdown("#### 📋 費用の内訳")
                    breakdown = current_plan.breakdown()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("燃料費", f"{breakdown['燃料費']:,.0f} 円")
                        st.caption(f"年間{current_plan.annual_mileage:,.0f}km / {current_plan.fuel_efficiency}km/L")
                    with col2:
                        st.metric("車検費用", f"{breakdown['車検費用']:,.0f} 円")
                        if current_plan.inspection_year:
                            st.caption("今年は車検年です")
                    with col3:
                        st.metric("任意保険", f"{breakdown['任意保険']:,.0f} 円")
                    with col4:
                        st.metric("自動車税", f"{breakdown['自動車税']:,.0f} 円")
                    
                    col5, col6, col7, col8 = st.columns(4)
                    with col5:
                        st.metric("駐車場代", f"{breakdown['駐車場代']:,.0f} 円")
                        st.caption(f"月額{current_plan.monthly_parking_fee:,.0f}円")
                    with col6:
                        st.metric("メンテナンス", f"{breakdown['メンテナンス']:,.0f} 円")
                    with col7:
                        st.metric("洗車・消耗品", f"{breakdown['洗車・消耗品']:,.0f} 円")
                    with col8:
                        st.metric("予備費", f"{breakdown['予備費']:,.0f} 円")
                    
                    # 円グラフ
                    st.markdown("#### 📊 費用配分")
                    fig_pie = px.pie(
                        values=list(breakdown.values()),
                        names=list(breakdown.keys()),
                        title=f"{current_year}年の維持費内訳"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # 複数年の推移
                st.markdown("### 📈 維持費の年次推移")
                
                years = [p.year for p in plan_obj.annual_plans]
                totals = [p.total_annual_cost for p in plan_obj.annual_plans]
                inspection_flags = [p.inspection_year for p in plan_obj.annual_plans]
                
                colors = ["red" if flag else "lightblue" for flag in inspection_flags]
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    x=years,
                    y=[t / 10000 for t in totals],
                    marker_color=colors,
                    text=[f"{t/10000:.0f}万円" for t in totals],
                    textposition="auto",
                ))
                fig_bar.update_layout(
                    title="年間維持費の推移（車検年は赤色）",
                    xaxis_title="年度",
                    yaxis_title="維持費（万円）",
                    height=400,
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("年間計画が作成されていません")
        
        # タブ2: 年度別設定
        with tab2:
            st.subheader(f"⚙️ {selected_vehicle} - 年度別設定")
            
            if plan_obj.annual_plans:
                # 年度選択
                years = [p.year for p in plan_obj.annual_plans]
                selected_year = st.selectbox("編集する年度を選択", years)
                
                plan = plan_obj.get_year_plan(selected_year)
                
                if plan:
                    with st.form(f"edit_plan_{selected_year}"):
                        st.markdown(f"### {selected_year}年の維持費計画")
                        
                        # 共通関数で入力フォームを生成
                        inputs = render_common_expense_inputs(
                            existing_data=plan,
                            is_plan=True,
                            key_suffix=f"plan_{selected_year}"
                        )
                        
                        submit_edit = st.form_submit_button("この年度の計画を更新")
                        
                        if submit_edit:
                            try:
                                updated_plan = AnnualMaintenancePlan(
                                    year=selected_year,
                                    annual_mileage=inputs['annual_mileage'],
                                    fuel_efficiency=inputs['fuel_efficiency'],
                                    fuel_price_per_liter=inputs['fuel_price_per_liter'],
                                    inspection_year=inputs['inspection_year'],
                                    inspection_base_fee=float(inputs['inspection_base_fee']),
                                    weight_tax=float(inputs['weight_tax']),
                                    liability_insurance=float(inputs['liability_insurance']),
                                    inspection_other=float(inputs['inspection_other']),
                                    voluntary_insurance=float(inputs['voluntary_insurance']),
                                    automobile_tax=float(inputs['automobile_tax']),
                                    monthly_parking_fee=float(inputs['monthly_parking_fee']),
                                    oil_change_count=inputs['oil_change_count'],
                                    oil_change_cost=float(inputs['oil_change_cost']),
                                    tire_change=inputs['tire_change'],
                                    tire_change_cost=float(inputs['tire_change_cost']),
                                    other_maintenance=float(inputs['other_maintenance']),
                                    car_wash=float(inputs['car_wash']),
                                    unexpected_expense=float(inputs['unexpected_expense']),
                                )
                                
                                plan_obj.add_year_plan(updated_plan)
                                manager.save()
                                st.success(f"✅ {selected_year}年の計画を更新しました")
                                st.rerun()
                            except Exception as e:
                                st.error(f"エラー: {e}")
            else:
                st.warning("年間計画が作成されていません")
        
        # タブ3: 実績入力
        with tab3:
            st.subheader(f"📝 {selected_vehicle} - 実績入力")
            
            st.markdown("### 過去の維持費実績を入力")
            
            # 年度選択
            if plan_obj.annual_plans:
                years = [p.year for p in plan_obj.annual_plans]
                actual_year = st.selectbox("実績を入力する年度を選択", years, key="actual_year_select")
                
                # 既存の実績があれば取得
                existing_actual = plan_obj.get_actual_expense(actual_year)
                
                with st.form(f"actual_expense_{actual_year}"):
                    st.markdown(f"#### {actual_year}年の実績費用")
                    
                    # 共通関数で入力フォームを生成
                    inputs = render_common_expense_inputs(
                        existing_data=existing_actual,
                        is_plan=False,
                        key_suffix=f"actual_{actual_year}"
                    )
                    
                    # 合計表示（駐車代は不要のため除外、メンテナンスは詳細合計）
                    total_maintenance = (
                        inputs['oil_change_cost'] + inputs['tire_change_cost'] + 
                        inputs['other_maintenance_cost']
                    )
                    total_actual = (
                        inputs['fuel_cost'] + inputs['inspection_cost'] + inputs['insurance_cost'] + 
                        inputs['tax_cost'] + total_maintenance + inputs['other_cost']
                    )
                    
                    st.markdown(f"**合計実績費用: {total_actual:,.0f} 円**")
                    st.caption(f"メンテナンス内訳: オイル{inputs['oil_change_cost']:,.0f}円 + タイヤ{inputs['tire_change_cost']:,.0f}円 + その他{inputs['other_maintenance_cost']:,.0f}円")
                    
                    # 計画との比較
                    plan = plan_obj.get_year_plan(actual_year)
                    if plan:
                        plan_total = plan.total_annual_cost
                        diff = total_actual - plan_total
                        diff_pct = (diff / plan_total * 100) if plan_total > 0 else 0
                        
                        if diff > 0:
                            st.warning(f"⚠️ 計画比 +{diff:,.0f} 円（+{diff_pct:.1f}%）超過")
                        elif diff < 0:
                            st.success(f"✅ 計画比 {diff:,.0f} 円（{diff_pct:.1f}%）削減")
                        else:
                            st.info("📊 計画通り")
                    
                    submit_actual = st.form_submit_button("実績を保存")
                    
                    if submit_actual:
                        try:
                            actual_expense = ActualExpense(
                                year=actual_year,
                                fuel_cost=float(inputs['fuel_cost']),
                                inspection_cost=float(inputs['inspection_cost']),
                                insurance_cost=float(inputs['insurance_cost']),
                                tax_cost=float(inputs['tax_cost']),
                                parking_cost=float(inputs['parking_cost']),
                                maintenance_cost=0.0,  # 詳細項目を使用するため0
                                other_cost=float(inputs['other_cost']),
                                # メンテナンス詳細項目
                                oil_change_cost=float(inputs['oil_change_cost']),
                                tire_change_cost=float(inputs['tire_change_cost']),
                                other_maintenance_cost=float(inputs['other_maintenance_cost']),
                            )
                            
                            plan_obj.add_actual_expense(actual_expense)
                            manager.save()
                            st.success(f"✅ {actual_year}年の実績を保存しました")
                            st.rerun()
                        except Exception as e:
                            st.error(f"エラー: {e}")
                
                # 実績一覧
                if plan_obj.actual_expenses:
                    st.markdown("### 📋 登録済み実績一覧")
                    
                    actual_data = []
                    actual_data_for_csv = []  # CSV用の数値データ
                    
                    for actual in plan_obj.actual_expenses:
                        plan = plan_obj.get_year_plan(actual.year)
                        plan_total = plan.total_annual_cost if plan else 0
                        diff = actual.total_cost - plan_total
                        
                        # 表示用データ（フォーマット済み）
                        actual_data.append({
                            "年度": actual.year,
                            "燃料費": f"{actual.fuel_cost:,.0f}",
                            "車検": f"{actual.inspection_cost:,.0f}",
                            "保険": f"{actual.insurance_cost:,.0f}",
                            "税金": f"{actual.tax_cost:,.0f}",
                            # "駐車場": f"{actual.parking_cost:,.0f}",  # 駐車代は不要
                            "メンテ": f"{actual.maintenance_cost:,.0f}",
                            "その他": f"{actual.other_cost:,.0f}",
                            "合計": f"{actual.total_cost:,.0f}",
                            "計画比": f"{diff:+,.0f}" if plan else "-",
                        })
                        
                        # CSV用データ（数値）
                        actual_data_for_csv.append({
                            "年度": actual.year,
                            "燃料費": actual.fuel_cost,
                            "車検": actual.inspection_cost,
                            "保険": actual.insurance_cost,
                            "税金": actual.tax_cost,
                            "メンテ": actual.maintenance_cost,
                            "その他": actual.other_cost,
                            "合計": actual.total_cost,
                            "計画額": plan_total if plan else 0,
                            "計画比": diff if plan else 0,
                        })
                    
                    df_actual = pd.DataFrame(actual_data)
                    df_actual_csv = pd.DataFrame(actual_data_for_csv)
                    
                    st.dataframe(df_actual, use_container_width=True, hide_index=True)
                    
                    # CSV出力・読み込み
                    col_csv1, col_csv2 = st.columns(2)
                    
                    with col_csv1:
                        csv_data = df_actual_csv.to_csv(index=False, encoding="utf-8-sig")
                        st.download_button(
                            label="📥 実績一覧をCSVダウンロード",
                            data=csv_data,
                            file_name=f"{selected_vehicle}_実績一覧_{date.today().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )
                    
                    with col_csv2:
                        uploaded_file = st.file_uploader(
                            "📤 実績CSVをアップロード",
                            type=["csv"],
                            help="CSVから実績データを読み込みます",
                            key=f"upload_actual_{selected_vehicle}",
                        )
                        
                        if uploaded_file is not None:
                            try:
                                df_upload = pd.read_csv(uploaded_file, encoding="utf-8-sig")
                                
                                # データの検証
                                required_cols = ["年度", "燃料費", "車検", "保険", "税金", "メンテ", "その他"]
                                if not all(col in df_upload.columns for col in required_cols):
                                    st.error(f"必須カラムが不足しています: {required_cols}")
                                else:
                                    # 実績データを更新
                                    imported_count = 0
                                    for _, row in df_upload.iterrows():
                                        actual_expense = ActualExpense(
                                            year=int(row["年度"]),
                                            fuel_cost=float(row["燃料費"]),
                                            inspection_cost=float(row["車検"]),
                                            insurance_cost=float(row["保険"]),
                                            tax_cost=float(row["税金"]),
                                            parking_cost=0.0,  # 駐車代は0固定
                                            maintenance_cost=float(row["メンテ"]),
                                            other_cost=float(row["その他"]),
                                        )
                                        plan_obj.add_actual_expense(actual_expense)
                                        imported_count += 1
                                    
                                    manager.save()
                                    st.success(f"✅ {imported_count}件の実績データをインポートしました")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"CSVの読み込みエラー: {e}")
            else:
                st.warning("年間計画が作成されていません")
        
        # タブ4: 長期シミュレーション
        with tab4:
            st.subheader(f"📈 {selected_vehicle} - 長期シミュレーション")
            
            st.markdown("### 🔮 生涯コスト試算")
            
            ownership_years = st.slider("保有期間（年）", min_value=1, max_value=20, value=10, step=1)
            
            lifetime_result = plan_obj.lifetime_cost(ownership_years)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("車両本体価格", f"{lifetime_result['車両本体価格']:,.0f} 円")
            with col2:
                st.metric("維持費合計", f"{lifetime_result['維持費合計']:,.0f} 円")
            with col3:
                st.metric("総額", f"{lifetime_result['総額']:,.0f} 円")
            
            col4, col5 = st.columns(2)
            with col4:
                st.metric("年平均コスト", f"{lifetime_result['年平均']:,.0f} 円")
            with col5:
                st.metric("月平均コスト", f"{lifetime_result['月平均']:,.0f} 円")
            
            # 累積コストグラフ
            st.markdown("### 📊 累積コストの推移")
            
            cumulative_costs = [vehicle.purchase_price]
            years_list = [0]
            
            for i in range(1, ownership_years + 1):
                year = vehicle.ownership_start_year + i
                plan = plan_obj.get_year_plan(year)
                
                if plan:
                    annual_cost = plan.total_annual_cost
                else:
                    # デフォルト値で推定
                    if plan_obj.annual_plans:
                        base_plan = plan_obj.annual_plans[0]
                        is_inspection = (i == 2) or (i > 2 and (i - 2) % 2 == 0)
                        annual_cost = (
                            base_plan.fuel_cost
                            + (base_plan.inspection_cost if is_inspection else 0)
                            + base_plan.voluntary_insurance
                            + base_plan.automobile_tax
                            + base_plan.parking_cost
                            + base_plan.maintenance_cost
                            + base_plan.car_wash
                            + base_plan.unexpected_expense
                        )
                    else:
                        annual_cost = 300000  # デフォルト値
                
                cumulative_costs.append(cumulative_costs[-1] + annual_cost)
                years_list.append(i)
            
            fig_cumulative = go.Figure()
            fig_cumulative.add_trace(go.Scatter(
                x=years_list,
                y=[c / 10000 for c in cumulative_costs],
                mode="lines+markers",
                name="累積コスト",
                fill="tozeroy",
            ))
            fig_cumulative.update_layout(
                title=f"{ownership_years}年間の累積コスト",
                xaxis_title="経過年数",
                yaxis_title="累積コスト（万円）",
                height=400,
            )
            st.plotly_chart(fig_cumulative, use_container_width=True)
        
        # タブ5: 比較分析
        with tab5:
            st.subheader(f"💡 {selected_vehicle} - 比較分析")
            st.info("📊 複数車両の比較分析機能は今後実装予定です")
            st.markdown("""
            **今後実装予定の機能**:
            - 複数車両の維持費比較
            - ガソリン車 vs ハイブリッド vs 電気自動車
            - 新車 vs 中古車のコスト比較
            - リース vs 購入の比較
            """)

else:
    st.info("👈 サイドバーから車両を登録してください")
    
    st.markdown("""
    ### 📝 使い方
    
    1. **車両を登録**: サイドバーから車両情報を入力
    2. **年間計画を確認**: 自動的に10年分の計画が作成されます
    3. **年度別に調整**: 各年度の維持費項目を細かく設定可能
    4. **長期シミュレーション**: 生涯コストを試算
    
    ### 💡 特徴
    
    - ✅ 年間計画ベースの維持費管理
    - ✅ 車検年を自動判定（初回3年、以降2年ごと）
    - ✅ 燃料費・保険・税金・メンテナンスを一元管理
    - ✅ 複数年の推移を可視化
    - ✅ 生涯コストのシミュレーション
    """)
