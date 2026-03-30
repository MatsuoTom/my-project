from __future__ import annotations

# 年金シミュレーター（高度版）
# - 納付実績の可視化
# - 将来年収予測
# - 年金受給額の試算
# - 損益分岐・最適化 分析（詳細版）

import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# プロジェクトルートをパスに追加
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pension_calc.core.pension_utils as putils


@st.cache_data(show_spinner=False)
def _get_career_model_cached(kind: str, to_yen: bool) -> pd.DataFrame:
    return putils.get_career_model(kind, to_yen=to_yen)


def _interpolate_model_income(career_df: pd.DataFrame, age: int, income_col: str) -> float:
    matching_rows = career_df[career_df["年齢"] == age]
    if len(matching_rows) > 0:
        return float(matching_rows.iloc[0][income_col])
    if age < career_df["年齢"].min():
        return float(career_df.iloc[0][income_col])
    if age > career_df["年齢"].max():
        return float(career_df.iloc[-1][income_col])

    lower_age = career_df[career_df["年齢"] < age]["年齢"].max()
    upper_age = career_df[career_df["年齢"] > age]["年齢"].min()
    lower_income = float(career_df[career_df["年齢"] == lower_age].iloc[0][income_col])
    upper_income = float(career_df[career_df["年齢"] == upper_age].iloc[0][income_col])
    ratio = (age - lower_age) / (upper_age - lower_age)
    return lower_income + (upper_income - lower_income) * ratio


@st.cache_data(show_spinner=False)
def _build_scaled_career_projection(
    career_model_kind: str,
    current_age: int,
    retirement_age: int,
    base_income_yen: int,
) -> Dict[str, object]:
    career_df = putils.get_career_model(career_model_kind, to_yen=True)
    model_current_income = _interpolate_model_income(career_df, current_age, "推定年収(円)")
    scale_factor = base_income_yen / model_current_income if model_current_income > 0 else 1.0

    remaining_years = max(0, retirement_age - current_age)
    future_incomes = []
    for i in range(remaining_years):
        future_age = current_age + i
        model_income = _interpolate_model_income(career_df, future_age, "推定年収(円)")
        future_incomes.append(model_income * scale_factor)

    return {
        "career_df": career_df,
        "scale_factor": scale_factor,
        "future_incomes": future_incomes,
    }


def main() -> None:
    # ページ設定
    st.set_page_config(page_title="年金シミュレーター", page_icon="📊", layout="wide")
    st.title("📊 年金シミュレーター")
    st.caption("サンプルデータに基づくシミュレーション（高度機能を含む）")
    st.markdown("---")

    # 現在年齢をデータから推定
    try:
        current_age = int(putils.df["年齢"].max())
    except Exception:
        current_age = 30

    # サイドバー
    st.sidebar.header("📋 設定")
    # 動的最小値と既定値
    min_ret_age = max(55, current_age + 1)
    default_ret_age = max(min(65, current_age + 5), min_ret_age)

    # 既存セッション値の事前クランプ
    if "retirement_age" in st.session_state:
        try:
            _ra = int(st.session_state["retirement_age"])
        except Exception:
            _ra = default_ret_age
        st.session_state["retirement_age"] = max(min(_ra, 75), min_ret_age)
    if "pension_start_age" in st.session_state:
        try:
            _ps = int(st.session_state["pension_start_age"])
        except Exception:
            _ps = 65
        st.session_state["pension_start_age"] = max(min(_ps, 75), 60)
    # life_expectancy は pension_start_age に依存
    retirement_age = st.sidebar.number_input(
        "退職年齢",
        min_value=min_ret_age,
        max_value=75,
        value=default_ret_age,
        step=1,
        key="retirement_age",
    )
    pension_start_age = st.sidebar.number_input(
        "年金受給開始年齢", min_value=60, max_value=75, value=65, step=1, key="pension_start_age"
    )
    min_life = max(70, int(pension_start_age) + 1)
    default_life = max(85, min_life + 5)
    if "life_expectancy" in st.session_state:
        try:
            _le = int(st.session_state["life_expectancy"])
        except Exception:
            _le = default_life
        st.session_state["life_expectancy"] = max(min(_le, 120), min_life)
    life_expectancy = st.sidebar.number_input(
        "想定寿命",
        min_value=min_life,
        max_value=120,
        value=min(default_life, 120),
        step=1,
        key="life_expectancy",
    )
    st.sidebar.markdown("---")

    # キャリアモデル選択
    career_model_kind = st.sidebar.selectbox(
        "🎯 キャリアモデルを選択",
        ["default", "expanded"],
        index=0,
        help="default: 標準的な企業キャリア（30-60歳）/ expanded: より詳細なキャリアパス（25-60歳）",
        key="career_model_selector",
    )

    st.sidebar.markdown("---")
    base_income_man = st.sidebar.number_input(
        "現在の年収（万円）",
        min_value=200,
        max_value=2000,
        value=1150,
        step=10,
        key="base_income_man",
    )
    growth_rate_pct = st.sidebar.slider(
        "年収成長率（%）", min_value=0.0, max_value=10.0, value=3.0, step=0.1, key="growth_rate_pct"
    )

    base_income_yen = int(base_income_man * 10000)  # 万円→円
    growth_rate = float(growth_rate_pct) / 100.0

    # オブジェクト
    calculator = putils.PensionCalculator()

    # 開発者向け情報（どのモジュールがロードされているか可視化）
    with st.sidebar.expander("🛠️ 開発者情報", expanded=False):
        st.write("UI ファイル:", __file__)
        try:
            st.write("pension_utils:", putils.__file__)
        except Exception:
            st.write("pension_utils のパスを取得できませんでした")
        st.write("プロジェクトルート:", PROJECT_ROOT)
        st.caption(
            "この表示で、バックアップ側のモジュールが誤って読み込まれていないか確認できます。"
        )

    # タブ構成
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "🏠 ホーム",
            "💰 支払実績",
            "🎯 受給額試算",
            "🔮 将来予測",
            "⚖️ 損益分岐点",
            "🎯 最適化分析",
            "📋 計算方法",
        ]
    )

    with tab1:
        st.subheader("概要")
        st.info(
            "この画面は 高度版（損益分岐・最適化 含む）です。サイドバー下部の『🛠️ 開発者情報』でロード元パスを確認できます。",
            icon="✅",
        )

        # キャリアモデルの説明
        with st.expander("📈 キャリアモデルについて", expanded=False):
            st.write(f"**現在選択中**: {career_model_kind}モデル")

            try:
                current_model_df = _get_career_model_cached(career_model_kind, to_yen=False)
                if len(current_model_df) > 0:
                    st.markdown("**選択中モデルの内容**:")
                    for _, row in current_model_df.iterrows():
                        st.write(f"- {row['年齢']}歳: {row['役職']} ({row['推定年収(万円)']}万円)")
                else:
                    st.warning("キャリアモデルのデータを取得できませんでした。")
            except Exception as e:
                st.error(f"キャリアモデル取得エラー: {e}")

            st.markdown(
                """
            **キャリアモデル**は、年齢・役職・年収の関係を表すデータセットです。
            
            **利用可能モデル**:
            - **default**: 標準的な企業キャリア（30-60歳、8段階）
            - **expanded**: より詳細なキャリアパス（25-60歳、11段階）
            
            **用途**:
            - 🔮 将来予測タブ: 退職年齢までの年収推移予測
            - 📊 損益分岐・最適化タブ: 厚生年金納付額の詳細計算（料率18.3%）
            - 🎯 受給額試算タブ: 報酬比例部分の算出基準
            
            サイドバーで「🎯 キャリアモデルを選択」から切り替えできます。実際の計算には、「現在の年収」と「年収成長率」の設定値も併用されます。
            """
            )

        res = calculator.calculate_future_pension(retirement_age=int(retirement_age))
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("年間受給額（概算）", f"{res['年間受給額']:,.0f} 円")
        with c2:
            st.metric("月額受給額（概算）", f"{res['月額受給額']:,.0f} 円")
        with c3:
            st.metric("総納付額（実績）", f"{res['総納付額']:,.0f} 円")

    with tab2:
        st.subheader("📋 納付実績データ")
        st.caption(
            "表は編集できます。CSV/Excelからの取り込みやCSVダウンロードにも対応しています。保存するとCSVに書き出され、以後はその内容がSoTになります。"
        )
        with st.expander("📥 実績ファイルのインポート（CSV/Excel）"):
            up = st.file_uploader(
                "ファイルを選択",
                type=["csv", "xlsx", "xls"],
                accept_multiple_files=False,
                key="records_upload",
            )
            if up is not None:
                try:
                    if up.name.lower().endswith(".csv"):
                        df_in = pd.read_csv(up)
                    else:
                        df_in = pd.read_excel(up)
                    required = ["年度", "年齢", "加入制度", "加入月数", "納付額", "推定年収"]
                    missing = [c for c in required if c not in df_in.columns]
                    if missing:
                        st.error(f"欠落列があります: {missing}")
                    else:
                        st.success(f"読み込み成功: {up.name}（{len(df_in)}行）")
                        putils.df[:] = df_in.reindex(columns=putils.df.columns)
                        st.session_state["records_editor"] = putils.df.copy()
                except Exception as e:
                    st.error(f"読み込みに失敗しました: {e}")

        edited = st.data_editor(
            putils.df,
            num_rows="dynamic",
            width="content",
            hide_index=True,
            key="records_editor",
            column_order=["年度", "年齢", "加入制度", "お勤め先", "加入月数", "納付額", "推定年収"],
            column_config={
                "年度": st.column_config.NumberColumn(
                    "年度", min_value=1900, max_value=2100, step=1
                ),
                "年齢": st.column_config.NumberColumn("年齢", min_value=0, max_value=120, step=1),
                "加入制度": st.column_config.TextColumn("加入制度"),
                "お勤め先": st.column_config.TextColumn("お勤め先"),
                "加入月数": st.column_config.NumberColumn(
                    "加入月数", min_value=0, max_value=12, step=1
                ),
                "納付額": st.column_config.NumberColumn(
                    "納付額", min_value=0, step=1000, format="%,.0f 円"
                ),
                "推定年収": st.column_config.NumberColumn(
                    "推定年収", min_value=0, step=10000, format="%,.0f 円"
                ),
            },
        )
        csv_bytes = putils.df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📤 現在データをCSVでダウンロード",
            data=csv_bytes,
            file_name="pension_records.csv",
            mime="text/csv",
        )

        c_save, c_reload = st.columns([1, 1])
        with c_save:
            if st.button("💾 保存", type="primary", key="save_records_btn"):
                try:
                    putils.save_df(pd.DataFrame(edited))
                    st.success("保存しました。上部の数値やグラフも再計算されます。")
                except Exception as e:
                    st.error(f"保存に失敗しました: {e}")
        with c_reload:
            if st.button("🔄 再読込", key="reload_records_btn"):
                st.rerun()

        st.markdown("### 📈 年収推移（実績）")
        fig_income = go.Figure()
        fig_income.add_trace(
            go.Scatter(
                x=edited["年度"],
                y=edited["推定年収"],
                mode="lines+markers",
                name="年収",
                line=dict(color="blue"),
            )
        )
        fig_income.update_layout(
            title="年収（実績）", xaxis_title="年度", yaxis_title="年収（円）", height=360
        )
        st.plotly_chart(fig_income, config={"responsive": True})

        st.markdown("### 💰 納付額推移（実績）")
        fig_paid = go.Figure()
        fig_paid.add_trace(
            go.Bar(x=edited["年度"], y=edited["納付額"], name="納付額", marker_color="green")
        )
        fig_paid.update_layout(
            title="年間納付額（実績）", xaxis_title="年度", yaxis_title="金額（円）", height=360
        )
        st.plotly_chart(fig_paid, config={"responsive": True})

    with tab3:
        st.subheader("🎯 年金受給額の簡易試算")
        full_amount_yearly = 780_900  # 参考値
        kokumin_months_past = putils.paid_months_kokumin()
        add_months = max(0, (60 - min(int(retirement_age), 60)) * 12)
        kokumin_months_total = kokumin_months_past + add_months
        estimated_kokumin = full_amount_yearly * (kokumin_months_total / 480)

        # 将来予測の年収を取得（tab4と同じロジック）
        remaining_years = max(0, int(retirement_age) - int(current_age))
        projection = _build_scaled_career_projection(
            career_model_kind=career_model_kind,
            current_age=int(current_age),
            retirement_age=int(retirement_age),
            base_income_yen=base_income_yen,
        )
        career_df = projection["career_df"]
        scale_factor = projection["scale_factor"]
        future_incomes = projection["future_incomes"]

        # 将来予測を含めた年金受給額計算
        pension_res = calculator.calculate_future_pension(
            retirement_age=int(retirement_age),
            future_incomes=future_incomes if remaining_years > 0 else None,
            current_age=int(current_age)
        )
        estimated_kousei = max(0.0, pension_res["年間受給額"] - full_amount_yearly)

        def adj_rate(start_age: int) -> float:
            if start_age < 65:
                months = (65 - start_age) * 12
                return 1.0 - months * 0.004
            if start_age > 65:
                months = (start_age - 65) * 12
                return 1.0 + months * 0.007
            return 1.0

        adj = adj_rate(int(pension_start_age))
        kokumin_adj = estimated_kokumin * adj
        kousei_adj = estimated_kousei * adj
        total_annual = kokumin_adj + kousei_adj
        
        # 月額計算
        kokumin_monthly = kokumin_adj / 12
        kousei_monthly = kousei_adj / 12
        total_monthly = total_annual / 12

        st.markdown("#### 📊 年額受給額")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("国民年金（年額）", f"{kokumin_adj:,.0f} 円", delta=f"調整率 {adj:.1%}")
        with c2:
            st.metric("厚生年金（年額）", f"{kousei_adj:,.0f} 円")
        with c3:
            st.metric("合計（年額）", f"{total_annual:,.0f} 円")
        
        st.markdown("#### 💰 月額受給額")
        c4, c5, c6 = st.columns(3)
        with c4:
            st.metric("国民年金（月額）", f"{kokumin_monthly:,.0f} 円")
        with c5:
            st.metric("厚生年金（月額）", f"{kousei_monthly:,.0f} 円")
        with c6:
            st.metric("合計（月額）", f"{total_monthly:,.0f} 円", delta="年額の1/12")
        
        # 平均年収の内訳を表示
        with st.expander("📋 厚生年金計算の詳細", expanded=False):
            st.markdown("**平均年収の内訳**:")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("過去実績の平均年収", f"{pension_res['過去平均年収']:,.0f} 円")
            with col_b:
                if pension_res.get('将来平均年収'):
                    st.metric("将来予測の平均年収", f"{pension_res['将来平均年収']:,.0f} 円")
                else:
                    st.info("将来予測なし")
            with col_c:
                st.metric("加重平均年収", f"{pension_res['平均年収']:,.0f} 円", 
                         delta="厚生年金計算に使用")
            
            st.caption(f"加入月数: {pension_res['加入月数']:.0f}ヶ月 | キャリアモデル: {career_model_kind} | スケール係数: {scale_factor:.2f}倍")

        st.markdown("### 📈 年間受給額の推移（生涯）")
        years = list(range(int(pension_start_age), int(life_expectancy) + 1))
        annuals_man = [total_annual / 10000.0 for _ in years]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=annuals_man, mode="lines+markers", name="年間受給額"))
        fig.update_layout(
            title="年間受給額（万円）", xaxis_title="年齢", yaxis_title="金額（万円）", height=380
        )
        st.plotly_chart(fig, config={"responsive": True})

    with tab4:
        st.subheader("🔮 将来予測")
        remaining_years = max(0, int(retirement_age) - int(current_age))
        
        # キャリアモデルから将来年収を取得
        projection = _build_scaled_career_projection(
            career_model_kind=career_model_kind,
            current_age=int(current_age),
            retirement_age=int(retirement_age),
            base_income_yen=base_income_yen,
        )
        career_df = projection["career_df"]
        current_year = pd.Timestamp.now().year
        scale_factor = projection["scale_factor"]
        
        years_axis = []
        incomes = []
        
        for i in range(remaining_years):
            future_age = int(current_age) + i
            future_year = current_year + i
            
            # キャリアモデルから該当年齢の年収を取得
            model_income = _interpolate_model_income(career_df, future_age, "推定年収(円)")
            
            # スケール調整後の年収
            income = model_income * scale_factor
            
            years_axis.append(future_year)
            incomes.append(income)

        st.markdown("### 📈 推定年収（将来）")
        st.caption(f"使用中のキャリアモデル: **{career_model_kind}** | 現在年収: **{base_income_man:,.0f}万円** | スケール係数: **{scale_factor:.2f}倍**")
        
        if remaining_years > 0 and len(incomes) > 0:
            fig_f = go.Figure()
            fig_f.add_trace(
                go.Scatter(x=years_axis, y=incomes, mode="lines+markers", name="推定年収")
            )
            fig_f.update_layout(
                title="推定年収（円）", xaxis_title="年度", yaxis_title="年収（円）", height=360
            )
            st.plotly_chart(fig_f, config={"responsive": True})
            
            # 年収の詳細テーブル表示（役職付き）
            with st.expander("📋 年収詳細データ（キャリアモデル反映）", expanded=False):
                detail_data = []
                for i in range(len(years_axis)):
                    future_age = int(current_age) + i
                    matching_rows = career_df[career_df["年齢"] == future_age]
                    
                    if len(matching_rows) > 0:
                        position = matching_rows.iloc[0]["役職"]
                        is_model_value = "✓"
                    else:
                        position = "（補間値）"
                        is_model_value = "-"
                    
                    detail_data.append({
                        "年度": years_axis[i],
                        "年齢": future_age,
                        "役職": position,
                        "推定年収（円）": f"{int(incomes[i]):,}",
                        "モデル値": is_model_value
                    })
                
                income_detail_df = pd.DataFrame(detail_data)
                st.dataframe(income_detail_df, use_container_width=True, hide_index=True)
                st.caption("✓: キャリアモデルの値  -: 線形補間による推定値")
        else:
            st.info("将来年数が0年のため、年収予測は表示できません。")
        
        # キャリアモデルの全体像を表示
        with st.expander(f"📊 {career_model_kind}モデルの全体像", expanded=False):
            st.markdown("**キャリアモデルの定義データ**:")
            model_display_df = career_df.copy()
            model_display_df["推定年収（円）"] = model_display_df["推定年収(円)"].apply(lambda x: f"{int(x):,}")
            model_display_df = model_display_df[["年齢", "役職", "推定年収（円）"]]
            st.dataframe(model_display_df, use_container_width=True, hide_index=True)

        st.markdown("### 🏛️ 国民年金保険料（実績・予測）")
        years_actual, national_history, future_years_pension, future_fees = (
            putils.generate_national_pension_projection()
        )
        fig_p = go.Figure()
        fig_p.add_trace(
            go.Scatter(x=years_actual, y=national_history, mode="lines+markers", name="実績")
        )
        fig_p.add_trace(
            go.Scatter(
                x=future_years_pension,
                y=future_fees,
                mode="lines+markers",
                name="予測",
                line=dict(dash="dash"),
            )
        )
        fig_p.update_layout(
            title="国民年金月額保険料", xaxis_title="年度", yaxis_title="月額（円）", height=360
        )
        st.plotly_chart(fig_p, config={"responsive": True})

        st.markdown("---")
        st.caption(
            "注意: 本アプリは教育目的の簡易モデルです。実際の受給額は公式情報をご確認ください。"
        )

    with tab5:
        st.subheader("📊 損益分岐点・最適化分析")

        # 高度な損益分岐点分析機能を実装
        def calculate_detailed_breakeven_analysis():
            """より詳細な損益分岐点分析"""
            # 年齢範囲の設定
            plot_ages = list(range(20, int(life_expectancy) + 1))
            plot_payment_values = []
            plot_receive_values = []

            # キャリアモデルデータの取得
            try:
                career_model_df = _get_career_model_cached(career_model_kind, to_yen=False)
            except:
                career_model_df = pd.DataFrame()

            # 平均標準報酬月額を算出
            def calculate_average_salary():
                if len(career_model_df) == 0:
                    return 400000  # デフォルト値（年額）

                # 推定年収のカラム名を確認
                salary_col = None
                for col in career_model_df.columns:
                    if "推定年収" in col:
                        salary_col = col
                        break

                if salary_col is None:
                    return 400000

                try:
                    # 現在年齢から退職年齢までの年収を集計
                    relevant_salaries = []
                    for _, row in career_model_df.iterrows():
                        age = row.get("年齢", 0)
                        if current_age <= age <= int(retirement_age):
                            salary = float(row[salary_col]) * 10000  # 万円→円
                            relevant_salaries.append(salary)

                    if relevant_salaries:
                        return sum(relevant_salaries) / len(relevant_salaries)
                    else:
                        return 400000
                except:
                    return 400000

            avg_salary = calculate_average_salary()

            # 納付額と受給額の詳細計算
            for age in plot_ages:
                # 納付額の計算
                age_data = putils.df[putils.df["年齢"] == age]
                if not age_data.empty:
                    # 実績データ
                    plot_payment_values.append(age_data["納付額"].iloc[0])
                elif age < int(retirement_age):
                    # 将来推定納付額（より詳細）
                    if age >= 20:  # 20歳以降の納付
                        estimated_payment = min(
                            avg_salary * 0.183, 500000
                        )  # 厚生年金料率18.3%上限あり
                        plot_payment_values.append(estimated_payment)
                    else:
                        plot_payment_values.append(0)
                else:
                    plot_payment_values.append(0)

                # 受給額の計算
                if age >= int(pension_start_age):
                    # 調整率の詳細計算
                    if int(pension_start_age) < 65:
                        months_early = (65 - int(pension_start_age)) * 12
                        adjustment_rate = 1.0 - (months_early * 0.004)
                    elif int(pension_start_age) > 65:
                        months_late = (int(pension_start_age) - 65) * 12
                        adjustment_rate = 1.0 + (months_late * 0.007)
                    else:
                        adjustment_rate = 1.0

                    # 基礎年金と厚生年金の詳細算出
                    basic_pension = 780900 * (putils.paid_months_kokumin() / 480)

                    # 厚生年金の詳細計算（報酬比例部分）
                    try:
                        insured_months = putils.past_insured_months()
                        avg_monthly_salary = avg_salary / 12
                        earnings_related_pension = avg_monthly_salary * 0.005481 * insured_months
                    except:
                        earnings_related_pension = 0

                    annual_pension = (basic_pension + earnings_related_pension) * adjustment_rate
                    plot_receive_values.append(annual_pension)
                else:
                    plot_receive_values.append(0)

            return plot_ages, plot_payment_values, plot_receive_values

        # 詳細分析の実行
        ages, payments, receives = calculate_detailed_breakeven_analysis()

        # 累計計算
        cumulative_data = []
        cumulative_paid = 0
        cumulative_received = 0
        breakeven_age = None

        for age, payment, receive in zip(ages, payments, receives):
            cumulative_paid += payment
            cumulative_received += receive
            profit = cumulative_received - cumulative_paid

            cumulative_data.append(
                {
                    "年齢": age,
                    "年間納付額": payment,
                    "年間受給額": receive,
                    "累計納付額": cumulative_paid,
                    "累計受給額": cumulative_received,
                    "損益": profit,
                }
            )

            # 損益分岐点の判定
            if breakeven_age is None and age >= int(pension_start_age) and profit >= 0:
                breakeven_age = age

        # メトリクス表示
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "損益分岐点",
                f"{breakeven_age}歳" if breakeven_age else "到達せず",
                delta=(
                    f"受給開始から{breakeven_age - int(pension_start_age)}年"
                    if breakeven_age
                    else "寿命内で回収不可"
                ),
            )

        with col2:
            years_to_breakeven = breakeven_age - int(pension_start_age) if breakeven_age else None
            st.metric(
                "回収期間",
                f"{years_to_breakeven}年" if years_to_breakeven else "N/A",
                delta="受給開始からの年数",
            )

        with col3:
            investment_return_rate = 0
            if len(cumulative_data) > 0:
                final_data = cumulative_data[-1]
                if final_data["累計納付額"] > 0:
                    investment_return_rate = (
                        final_data["累計受給額"] / final_data["累計納付額"]
                    ) * 100

            st.metric("投資回収率", f"{investment_return_rate:.1f}%", delta="生涯受給額/生涯納付額")

        # 累計グラフの表示
        st.markdown("### 📈 損益分岐点推移グラフ")

        ages_plot = [data["年齢"] for data in cumulative_data]
        paid_amounts = [data["累計納付額"] / 10000 for data in cumulative_data]  # 万円単位
        received_amounts = [data["累計受給額"] / 10000 for data in cumulative_data]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=ages_plot,
                y=paid_amounts,
                mode="lines",
                name="累計納付額",
                line=dict(color="red", width=2),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=ages_plot,
                y=received_amounts,
                mode="lines",
                name="累計受給額",
                line=dict(color="blue", width=2),
            )
        )

        # 損益分岐点のマーカー
        if breakeven_age:
            breakeven_data = next(data for data in cumulative_data if data["年齢"] == breakeven_age)
            fig.add_trace(
                go.Scatter(
                    x=[breakeven_age],
                    y=[breakeven_data["累計受給額"] / 10000],
                    mode="markers",
                    name="損益分岐点",
                    marker=dict(size=15, color="green", symbol="star"),
                )
            )

        fig.update_layout(
            title="損益分岐点分析（詳細版）",
            xaxis_title="年齢",
            yaxis_title="金額（万円）",
            height=500,
            showlegend=True,
        )

        st.plotly_chart(fig, config={"responsive": True})

        # 最適受給開始年齢の簡易表示（現在の設定値のみ）
        st.markdown("### 🎯 設定に基づいた最適受給開始年齢分析")
        st.info(f"現在の受給開始年齢設定: **{int(pension_start_age)}歳**")
        
        # 現在の設定での受給額詳細
        current_start_age = int(pension_start_age)
        
        # 調整率の計算
        if current_start_age < 65:
            months_early = (65 - current_start_age) * 12
            current_adjustment_rate = 1.0 - (months_early * 0.004)
        elif current_start_age > 65:
            months_late = (current_start_age - 65) * 12
            current_adjustment_rate = 1.0 + (months_late * 0.007)
        else:
            current_adjustment_rate = 1.0
        
        # 受給額計算（tab3と同じロジック）
        current_annual = total_annual  # tab3で計算済み
        current_monthly = current_annual / 12
        
        col_opt1, col_opt2, col_opt3 = st.columns(3)
        with col_opt1:
            st.metric("最適受給開始年齢", f"{current_start_age}歳", delta=f"調整率 {current_adjustment_rate:.1%}")
        with col_opt2:
            st.metric("年間受給額", f"{current_annual:,.0f} 円")
        with col_opt3:
            st.metric("月額受給額", f"{current_monthly:,.0f} 円")
        
        # 詳細計算表の作成
        st.markdown("#### 📋 受給開始年齢の詳細計算")
        
        # 基礎データ
        basic_pension_base = 780900 * (putils.paid_months_kokumin() / 480)
        
        try:
            insured_months = putils.past_insured_months()
            # 将来予測を含めた平均年収を使用（tab3で計算済み）
            if pension_res.get('平均年収'):
                avg_salary = pension_res['平均年収']
            else:
                avg_salary = 4000000  # デフォルト
            earnings_related_base = (avg_salary / 12) * 0.005481 * insured_months
        except:
            earnings_related_base = 0
        
        annual_pension_base = basic_pension_base + earnings_related_base
        
        # 受給期間
        receiving_years = max(0, int(life_expectancy) - current_start_age)
        lifetime_total = current_annual * receiving_years
        
        # 詳細データ表示
        detail_data = {
            "項目": [
                "受給開始年齢",
                "調整率",
                "国民年金（年額）",
                "厚生年金（年額）",
                "合計（年額）",
                "合計（月額）",
                "受給期間",
                "生涯総受給額"
            ],
            "値": [
                f"{current_start_age}歳",
                f"{current_adjustment_rate:.1%}",
                f"{kokumin_adj:,.0f} 円",
                f"{kousei_adj:,.0f} 円",
                f"{current_annual:,.0f} 円",
                f"{current_monthly:,.0f} 円",
                f"{receiving_years}年",
                f"{lifetime_total/1_000_000:.1f} 百万円"
            ]
        }
        
        detail_df = pd.DataFrame(detail_data)
        st.dataframe(detail_df, use_container_width=True, hide_index=True)
        
        st.caption("💡 より詳細な最適化分析（複数の受給開始年齢の比較）は「🎯 最適化分析」タブをご覧ください")

    with tab6:
        st.subheader("🎯 最適化分析")
        st.markdown("様々なパラメータの範囲で最適な年金受給開始年齢を分析します")
        
        # パラメータ範囲の設定
        st.markdown("#### ⚙️ 分析範囲の設定")
        col_param1, col_param2, col_param3 = st.columns(3)
        
        with col_param1:
            st.markdown("**退職年齢の範囲**")
            retirement_min = max(55, int(retirement_age) - 5)
            retirement_max = min(75, int(retirement_age) + 5)
            st.caption(f"{retirement_min}歳 ～ {retirement_max}歳")
        
        with col_param2:
            st.markdown("**年金受給開始の範囲**")
            pension_start_min = 65
            pension_start_max = 75
            st.caption(f"{pension_start_min}歳 ～ {pension_start_max}歳")
        
        with col_param3:
            st.markdown("**想定寿命の範囲**")
            life_min = max(70, int(life_expectancy) - 5)
            life_max = min(120, int(life_expectancy) + 5)
            st.caption(f"{life_min}歳 ～ {life_max}歳")

        def calculate_optimal_start_age():
            """最適な受給開始年齢を計算（パラメータ範囲を考慮）"""
            candidates = list(range(pension_start_min, pension_start_max + 1))
            results = []
            
            # 将来予測の年収を取得（tab3と同じロジック）
            remaining_years = max(0, int(retirement_age) - int(current_age))
            projection = _build_scaled_career_projection(
                career_model_kind=career_model_kind,
                current_age=int(current_age),
                retirement_age=int(retirement_age),
                base_income_yen=base_income_yen,
            )
            future_incomes = projection["future_incomes"]
            
            # 将来予測を含めた年金受給額計算
            pension_calc_res = calculator.calculate_future_pension(
                retirement_age=int(retirement_age),
                future_incomes=future_incomes if remaining_years > 0 else None,
                current_age=int(current_age)
            )
            
            # 加重平均年収を使用
            avg_salary = pension_calc_res.get('平均年収', 4000000)

            for start_age in candidates:
                # 調整率の計算
                if start_age < 65:
                    months_early = (65 - start_age) * 12
                    adjustment_rate = 1.0 - (months_early * 0.004)
                elif start_age > 65:
                    months_late = (start_age - 65) * 12
                    adjustment_rate = 1.0 + (months_late * 0.007)
                else:
                    adjustment_rate = 1.0

                # 基本年金額の計算
                basic_pension = 780900 * (putils.paid_months_kokumin() / 480)
                try:
                    insured_months = putils.past_insured_months()
                    earnings_related = (avg_salary / 12) * 0.005481 * insured_months
                except:
                    earnings_related = 0

                annual_pension = (basic_pension + earnings_related) * adjustment_rate

                # 受給期間と生涯総額
                receiving_years = max(0, int(life_expectancy) - start_age)
                lifetime_total = annual_pension * receiving_years

                results.append(
                    {
                        "受給開始年齢": start_age,
                        "調整率": adjustment_rate,
                        "年間受給額": annual_pension,
                        "受給期間": receiving_years,
                        "生涯総受給額": lifetime_total,
                    }
                )

            return results

        optimization_results = calculate_optimal_start_age()

        if optimization_results:
            # 最適解の表示
            df_results = pd.DataFrame(optimization_results)
            best_result = df_results.loc[df_results["生涯総受給額"].idxmax()]

            st.markdown("### 🏆 最適化結果")
            
            opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4)

            with opt_col1:
                st.metric("最適受給開始年齢", f"{int(best_result['受給開始年齢'])}歳", 
                         delta="生涯総受給額最大")

            with opt_col2:
                st.metric("年間受給額", f"{best_result['年間受給額']:,.0f} 円")
            
            with opt_col3:
                best_monthly = best_result['年間受給額'] / 12
                st.metric("月額受給額", f"{best_monthly:,.0f} 円")

            with opt_col4:
                st.metric("調整率", f"{best_result['調整率']:.1%}")
            
            # 追加情報
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.metric("受給期間", f"{int(best_result['受給期間'])}年")
            with info_col2:
                st.metric("生涯総受給額", f"{best_result['生涯総受給額']/1_000_000:.1f} 百万円")

            # 結果テーブルの表示
            st.markdown("### 📋 受給開始年齢別比較表")

            df_display = df_results.copy()
            df_display["月額受給額"] = df_display["年間受給額"].map(lambda x: f"{x/12:,.0f} 円")
            df_display["調整率"] = df_display["調整率"].map(lambda x: f"{x:.1%}")
            df_display["年間受給額"] = df_display["年間受給額"].map(lambda x: f"{x:,.0f} 円")
            df_display["生涯総受給額"] = df_display["生涯総受給額"].map(
                lambda x: f"{x/1_000_000:.1f} 百万円"
            )
            df_display = df_display[["受給開始年齢", "調整率", "月額受給額", "年間受給額", "受給期間", "生涯総受給額"]]

            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # グラフ表示
            st.markdown("### 📊 生涯総受給額の比較")
            fig_opt = go.Figure()
            fig_opt.add_trace(
                go.Bar(
                    x=df_results["受給開始年齢"],
                    y=df_results["生涯総受給額"] / 1_000_000,
                    marker_color=["green" if age == best_result["受給開始年齢"] else "lightblue" 
                                 for age in df_results["受給開始年齢"]],
                    text=df_results["生涯総受給額"].apply(lambda x: f"{x/1_000_000:.1f}"),
                    textposition="auto"
                )
            )
            fig_opt.update_layout(
                title="受給開始年齢別の生涯総受給額",
                xaxis_title="受給開始年齢（歳）",
                yaxis_title="生涯総受給額（百万円）",
                height=400
            )
            st.plotly_chart(fig_opt, use_container_width=True)

    with tab7:
        st.subheader("📋 計算方法")
        st.markdown(
            """
            ### 現在の受給額算出（詳細版）
            - 国民年金（老齢基礎年金）: 満額 780,900 円/年（参考）× 納付月数/480
            - 厚生年金（報酬比例）: 平均標準報酬月額 × 5.481/1000 × 被保険者月数
            - 繰上げ/繰下げ調整: 月 -0.4% / +0.7% を適用

            ### 損益分岐点（高度版）
            - 年齢ごとに累計納付額と累計受給額を詳細計算
            - キャリアモデルデータを活用した将来納付額予測
            - 厚生年金料率18.3%を考慮した推定納付額
            - 受給開始年齢以降で損益が初めて0以上となる年齢を算出

            ### 最適受給開始年齢（詳細版）
            - 60〜75歳の各候補で生涯総受給額を詳細計算
            - 調整率、受給期間、基礎年金・厚生年金を個別算出
            - 最大生涯総受給額となる開始年齢を特定

            ### キャリアモデルの詳細
            **get_career_model()関数について**:
            
            本アプリでは、`pension_calc.core.pension_utils.get_career_model()`を使用してキャリアパスのサンプルデータを取得しています。
            
            **利用可能なモデル**:
            - `"default"`: 標準的な企業キャリア（30-60歳）
            - `"expanded"`: より詳細なキャリアパス（25-60歳）
            
            **defaultモデルの構成**:
            ```
            年齢 | 役職      | 推定年収
            30歳 | 指導職    | 850万円
            35歳 | 主任      | 1,150万円
            40歳 | 基幹職    | 1,280万円
            45歳 | 基幹職    | 1,380万円
            50歳 | 基幹職    | 1,430万円
            55歳 | 定年退職  | 1,480万円
            56歳 | 出向(60%) | 888万円
            60歳 | 完全退職  | 888万円
            ```
            
            **活用箇所**:
            1. **損益分岐・最適化タブ**: 年収から厚生年金納付額を算出（年収×18.3%）
            2. **将来予測タブ**: 退職年齢までの年収推移をグラフ表示
            3. **受給額試算タブ**: 報酬比例部分の計算に平均標準報酬月額として使用

            ### データ取得方法
            - 実績データ: pension_utils.df から年齢別納付実績を取得
            - 将来予測: get_career_model()による年収推定とpaid_months_kokumin()による加入月数
            - 保険料率: 厚生年金18.3%、基礎年金は年額定額制

            注意: 本分析は詳細なモデルですが、実際の年金計算では更に多くの要素（配偶者加給、在職老齢年金等）を考慮する必要があります。
            """
        )


# Streamlit アプリとして実行
main()
