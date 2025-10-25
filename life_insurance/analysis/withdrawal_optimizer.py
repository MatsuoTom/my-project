"""
生命保険の引き出しタイミング最適化モジュール

満期時期、税制変更、年収変動を考慮した最適な引き出しタイミングを分析します。
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from life_insurance.core.deduction_calculator import LifeInsuranceDeductionCalculator
from life_insurance.core.tax_calculator import TaxCalculator


class WithdrawalOptimizer:
    """引き出しタイミング最適化クラス"""
    
    def __init__(self):
        """コンストラクタ"""
        self.deduction_calc = LifeInsuranceDeductionCalculator()
        self.tax_calc = TaxCalculator()
        self.current_year = datetime.now().year
    
    def calculate_policy_value(
        self,
        initial_premium: float,
        annual_premium: float,
        years: int,
        return_rate: float = 0.02
    ) -> Dict[str, float]:
        """
        保険の解約返戻金を計算
        
        Args:
            initial_premium: 初期保険料
            annual_premium: 年間保険料
            years: 経過年数
            return_rate: 想定運用利回り
            
        Returns:
            解約返戻金の詳細
        """
        total_premiums = initial_premium + (annual_premium * years)
        
        # 解約返戻金の計算（簡易的な複利計算）
        surrender_value = 0
        
        # 初期保険料の運用
        surrender_value += initial_premium * ((1 + return_rate) ** years)
        
        # 年間保険料の運用（年金終価計算）
        for year in range(1, years + 1):
            remaining_years = years - year + 1
            surrender_value += annual_premium * ((1 + return_rate) ** remaining_years)
        
        # 解約控除を考慮（経過年数により減少、10年で解約控除なし）
        surrender_deduction_rate = max(0, 0.1 - (years * 0.01))
        surrender_value *= (1 - surrender_deduction_rate)
        
        return {
            "経過年数": years,
            "払込保険料合計": total_premiums,
            "解約返戻金": surrender_value,
            "返戻率": surrender_value / total_premiums if total_premiums > 0 else 0,
            "利益": surrender_value - total_premiums,
            "解約控除率": surrender_deduction_rate
        }
    
    def calculate_total_benefit(
        self,
        annual_premium: float,
        taxable_income: float,
        withdrawal_year: int,
        policy_start_year: int,
        return_rate: float = 0.02
    ) -> Dict[str, float]:
        """
        総合的な利益を計算（節税効果 + 解約返戻金）
        
        Args:
            annual_premium: 年間保険料
            taxable_income: 課税所得
            withdrawal_year: 引き出し年
            policy_start_year: 保険開始年
            return_rate: 運用利回り
            
        Returns:
            総合利益の詳細
        """
        policy_years = withdrawal_year - policy_start_year
        
        # 節税効果の累計計算
        deduction_amount = self.deduction_calc.calculate_old_deduction(annual_premium)
        annual_savings = self.tax_calc.calculate_tax_savings(deduction_amount, taxable_income)
        total_tax_savings = annual_savings["合計節税額"] * policy_years
        
        # 解約返戻金計算
        policy_value = self.calculate_policy_value(annual_premium, annual_premium, policy_years, return_rate)
        
        # 解約所得税の計算（一時所得）
        profit = policy_value["利益"]
        taxable_profit = max(0, profit - 500000) / 2  # 一時所得の計算（50万円控除、1/2課税）
        
        withdrawal_tax = 0
        if taxable_profit > 0:
            withdrawal_tax_info = self.tax_calc.calculate_income_tax(taxable_income + taxable_profit)
            original_tax_info = self.tax_calc.calculate_income_tax(taxable_income)
            withdrawal_tax = withdrawal_tax_info["合計所得税"] - original_tax_info["合計所得税"]
        
        net_benefit = total_tax_savings + policy_value["解約返戻金"] - (annual_premium * policy_years) - withdrawal_tax
        
        return {
            "引き出し年": withdrawal_year,
            "保険期間": policy_years,
            "年間保険料": annual_premium,
            "払込保険料合計": annual_premium * policy_years,
            "累計節税効果": total_tax_savings,
            "解約返戻金": policy_value["解約返戻金"],
            "解約利益": profit,
            "一時所得課税対象": taxable_profit,
            "解約時所得税": withdrawal_tax,
            "純利益": net_benefit,
            "実質利回り": ((net_benefit + annual_premium * policy_years) / (annual_premium * policy_years)) ** (1/policy_years) - 1 if policy_years > 0 else 0
        }
    
    def optimize_withdrawal_timing(
        self,
        annual_premium: float,
        taxable_income: float,
        policy_start_year: int,
        max_years: int = 20,
        return_rate: float = 0.02
    ) -> Tuple[Dict[str, float], pd.DataFrame]:
        """
        最適な引き出しタイミングを分析
        
        Args:
            annual_premium: 年間保険料
            taxable_income: 課税所得
            policy_start_year: 保険開始年
            max_years: 最大分析年数
            return_rate: 運用利回り
            
        Returns:
            最適タイミングと全年度の分析結果
        """
        results = []
        best_result = None
        best_benefit = float('-inf')
        
        for years in range(1, max_years + 1):
            withdrawal_year = policy_start_year + years
            result = self.calculate_total_benefit(
                annual_premium, taxable_income, withdrawal_year, policy_start_year, return_rate
            )
            
            results.append(result)
            
            if result["純利益"] > best_benefit:
                best_benefit = result["純利益"]
                best_result = result.copy()
        
        df_results = pd.DataFrame(results)
        
        return best_result, df_results
    
    def analyze_income_scenarios(
        self,
        annual_premium: float,
        base_income: float,
        income_scenarios: List[Tuple[str, float]],
        policy_start_year: int,
        withdrawal_year: int,
        return_rate: float = 0.02
    ) -> pd.DataFrame:
        """
        異なる所得シナリオでの引き出し効果を比較
        
        Args:
            annual_premium: 年間保険料
            base_income: 基準所得
            income_scenarios: 所得シナリオ (名前, 所得) のタプルリスト
            policy_start_year: 保険開始年
            withdrawal_year: 引き出し年
            return_rate: 運用利回り
            
        Returns:
            シナリオ比較結果
        """
        results = []
        
        # 基準シナリオを追加
        all_scenarios = [("基準", base_income)] + income_scenarios
        
        for scenario_name, income in all_scenarios:
            result = self.calculate_total_benefit(
                annual_premium, income, withdrawal_year, policy_start_year, return_rate
            )
            
            results.append({
                "シナリオ": scenario_name,
                "課税所得": income,
                "保険期間": result["保険期間"],
                "累計節税効果": result["累計節税効果"],
                "解約返戻金": result["解約返戻金"],
                "解約時所得税": result["解約時所得税"],
                "純利益": result["純利益"],
                "実質利回り": f"{result['実質利回り']:.2%}"
            })
        
        return pd.DataFrame(results)
    
    def analyze_all_strategies(
        self,
        initial_premium: float,
        annual_premium: float,
        taxable_income: float,
        policy_start_year: int,
        interval_range: List[int],
        rate_range: List[float],
        full_withdrawal_years: List[int],
        switch_years: List[int],
        switch_rates: List[float],
        max_years: int = 20,
        return_rate: float = 0.02,
        withdrawal_reinvest_rate: float = 0.01
    ) -> pd.DataFrame:
        """
        複数の戦略（部分解約・全解約・乗り換え）を同時に分析してランキング化
        
        Args:
            initial_premium: 初期保険料
            annual_premium: 年間保険料
            taxable_income: 課税所得
            policy_start_year: 保険開始年
            interval_range: 部分解約の間隔リスト（年）
            rate_range: 部分解約の割合リスト（0.0～1.0）
            full_withdrawal_years: 全解約を検討する年数リスト
            switch_years: 乗り換えを検討する年数リスト
            switch_rates: 乗り換え時の手数料率リスト
            max_years: 最大分析年数
            return_rate: 運用利回り（保険内）
            withdrawal_reinvest_rate: 部分解約後の資金の再投資利回り（デフォルト1%: 預金想定）
            
        Returns:
            全戦略のランキングDataFrame
        """
        all_strategies = []
        
        # 1. 部分解約戦略（解約後は withdrawal_reinvest_rate で再投資）
        for interval in interval_range:
            for rate in rate_range:
                strategy_name = f"部分解約 (間隔{interval}年, 割合{rate*100:.0f}%)"
                net_benefit = self._calculate_partial_withdrawal_benefit(
                    annual_premium, taxable_income, policy_start_year, 
                    max_years, interval, rate, return_rate,
                    withdrawal_reinvest_rate=withdrawal_reinvest_rate
                )
                all_strategies.append({
                    "戦略タイプ": "部分解約",
                    "戦略名": strategy_name,
                    "間隔(年)": interval,
                    "解約割合": f"{rate*100:.0f}%",
                    "純利益(円)": net_benefit,
                    "パラメータ": f"間隔{interval}年/割合{rate*100:.0f}%"
                })
        
        # 2. 全解約戦略
        for year in full_withdrawal_years:
            strategy_name = f"全解約 ({year}年後)"
            result = self.calculate_total_benefit(
                annual_premium, taxable_income, 
                policy_start_year + year, policy_start_year, return_rate
            )
            all_strategies.append({
                "戦略タイプ": "全解約",
                "戦略名": strategy_name,
                "間隔(年)": year,
                "解約割合": "100%",
                "純利益(円)": result["純利益"],
                "パラメータ": f"{year}年後"
            })
        
        # 3. 乗り換え戦略
        for switch_year in switch_years:
            for switch_rate in switch_rates:
                strategy_name = f"乗り換え ({switch_year}年後, 手数料{switch_rate*100:.0f}%)"
                net_benefit = self._calculate_switch_benefit(
                    annual_premium, taxable_income, policy_start_year,
                    switch_year, switch_rate, max_years, return_rate
                )
                all_strategies.append({
                    "戦略タイプ": "乗り換え",
                    "戦略名": strategy_name,
                    "間隔(年)": switch_year,
                    "解約割合": "100%",
                    "純利益(円)": net_benefit,
                    "パラメータ": f"{switch_year}年後/手数料{switch_rate*100:.0f}%"
                })
        
        # DataFrameに変換してランキング化
        df = pd.DataFrame(all_strategies)
        df = df.sort_values("純利益(円)", ascending=False).reset_index(drop=True)
        df["ランク"] = df.index + 1
        
        # 列の順序を調整
        df = df[["ランク", "戦略タイプ", "戦略名", "純利益(円)", "間隔(年)", "解約割合", "パラメータ"]]
        
        return df
    
    def _calculate_partial_withdrawal_benefit(
        self,
        annual_premium: float,
        taxable_income: float,
        policy_start_year: int,
        max_years: int,
        interval: int,
        withdrawal_rate: float,
        return_rate: float,
        withdrawal_reinvest_rate: float = 0.01  # 解約後の再投資利回り（デフォルト1%: 預金想定）
    ) -> float:
        """
        部分解約戦略の純利益を計算
        
        解約後の資金運用シナリオ:
        - 部分解約した資金は withdrawal_reinvest_rate で再投資される
        - デフォルト1%: 普通預金・定期預金を想定
        - 0%: 手元保有（運用なし）
        - より高い利回り: 投資信託等での運用を想定
        
        Args:
            withdrawal_reinvest_rate: 解約後の資金の再投資利回り
        """
        total_paid = annual_premium * max_years
        total_tax_savings = 0
        withdrawn_funds = 0  # 解約済み資金の累積額（運用後）
        remaining_balance = 0
        
        # 年次シミュレーション
        for year in range(1, max_years + 1):
            # 節税効果
            deduction = self.deduction_calc.calculate_old_deduction(annual_premium)
            annual_savings = self.tax_calc.calculate_tax_savings(deduction, taxable_income)
            total_tax_savings += annual_savings["合計節税額"]
            
            # 既に解約した資金を再投資で運用（複利）
            if withdrawn_funds > 0:
                withdrawn_funds *= (1 + withdrawal_reinvest_rate)
            
            # 解約返戻金の累積（簡易計算）
            policy_value = self.calculate_policy_value(0, annual_premium, year, return_rate)
            remaining_balance = policy_value["解約返戻金"]
            
            # 部分解約実行
            if year % interval == 0:
                withdrawal_amount = remaining_balance * withdrawal_rate
                withdrawn_funds += withdrawal_amount  # 解約資金を再投資プールに追加
                remaining_balance -= withdrawal_amount
        
        # 最終残高も回収
        total_value = withdrawn_funds + remaining_balance
        
        # 純利益 = 総資産価値（保険残高 + 再投資資金） + 節税効果 - 払込保険料
        net_benefit = total_value + total_tax_savings - total_paid
        
        return net_benefit
    
    def _calculate_switch_benefit(
        self,
        annual_premium: float,
        taxable_income: float,
        policy_start_year: int,
        switch_year: int,
        switch_fee_rate: float,
        max_years: int,
        return_rate: float
    ) -> float:
        """乗り換え戦略の純利益を計算"""
        # 乗り換え前の利益
        before_switch = self.calculate_total_benefit(
            annual_premium, taxable_income,
            policy_start_year + switch_year, policy_start_year, return_rate
        )
        
        # 乗り換え手数料を差し引き
        switch_fee = before_switch["解約返戻金"] * switch_fee_rate
        net_after_switch = before_switch["解約返戻金"] - switch_fee
        
        # 乗り換え後の運用（残り期間）
        remaining_years = max_years - switch_year
        if remaining_years > 0:
            # 新商品での運用（簡易計算）
            new_policy_value = net_after_switch * ((1 + return_rate) ** remaining_years)
            
            # 乗り換え後の節税効果
            deduction = self.deduction_calc.calculate_old_deduction(annual_premium)
            annual_savings = self.tax_calc.calculate_tax_savings(deduction, taxable_income)
            additional_tax_savings = annual_savings["合計節税額"] * remaining_years
            
            total_benefit = (before_switch["累計節税効果"] + additional_tax_savings + 
                           new_policy_value - (annual_premium * max_years))
        else:
            total_benefit = before_switch["純利益"] - switch_fee
        
        return total_benefit
    
    def analyze_tax_reform_impact(
        self,
        annual_premium: float,
        taxable_income: float,
        policy_start_year: int,
        reform_year: int,
        new_deduction_limit: float,
        current_year: Optional[int] = None
    ) -> Dict[str, any]:
        """
        税制改正の影響を分析
        
        Args:
            annual_premium: 年間保険料
            taxable_income: 課税所得
            policy_start_year: 保険開始年
            reform_year: 税制改正年
            new_deduction_limit: 新控除上限額
            current_year: 現在年（Noneの場合は実際の現在年）
            
        Returns:
            税制改正影響の分析結果
        """
        if current_year is None:
            current_year = self.current_year
        
        # 改正前後の控除額比較
        old_deduction = self.deduction_calc.calculate_old_deduction(annual_premium)
        new_deduction = min(annual_premium, new_deduction_limit)
        
        # 改正前に引き出す場合
        years_before_reform = reform_year - current_year
        if years_before_reform > 0:
            before_reform_result = self.calculate_total_benefit(
                annual_premium, taxable_income, reform_year - 1, policy_start_year
            )
        else:
            before_reform_result = None
        
        # 改正後も継続する場合の影響
        years_after_reform = 5  # 改正後5年間の影響を見る
        after_reform_impact = []
        
        for year_offset in range(1, years_after_reform + 1):
            withdrawal_year = reform_year + year_offset
            policy_years = withdrawal_year - policy_start_year
            
            # 改正前年数での旧制度節税効果
            old_system_years = min(policy_years, reform_year - policy_start_year)
            old_system_savings = 0
            if old_system_years > 0:
                old_annual_savings = self.tax_calc.calculate_tax_savings(old_deduction, taxable_income)
                old_system_savings = old_annual_savings["合計節税額"] * old_system_years
            
            # 改正後年数での新制度節税効果
            new_system_years = policy_years - old_system_years
            new_system_savings = 0
            if new_system_years > 0:
                new_annual_savings = self.tax_calc.calculate_tax_savings(new_deduction, taxable_income)
                new_system_savings = new_annual_savings["合計節税額"] * new_system_years
            
            total_savings = old_system_savings + new_system_savings
            
            # 解約返戻金等の計算
            policy_value = self.calculate_policy_value(0, annual_premium, policy_years)
            
            after_reform_impact.append({
                "引き出し年": withdrawal_year,
                "保険期間": policy_years,
                "旧制度適用年数": old_system_years,
                "新制度適用年数": new_system_years,
                "旧制度節税効果": old_system_savings,
                "新制度節税効果": new_system_savings,
                "総節税効果": total_savings,
                "解約返戻金": policy_value["解約返戻金"],
                "節税効果減少額": (old_deduction - new_deduction) * new_system_years * self.tax_calc.get_income_tax_rate(taxable_income)
            })
        
        return {
            "改正年": reform_year,
            "旧控除上限": old_deduction,
            "新控除上限": new_deduction,
            "年間影響額": (old_deduction - new_deduction) * self.tax_calc.get_income_tax_rate(taxable_income),
            "改正前引き出し": before_reform_result,
            "改正後継続影響": pd.DataFrame(after_reform_impact)
        }


def main():
    """デモンストレーション用のメイン関数"""
    optimizer = WithdrawalOptimizer()
    
    print("=== 引き出しタイミング最適化デモ ===")
    
    # 基本パラメータ
    annual_premium = 100000  # 年間10万円
    taxable_income = 5000000  # 課税所得500万円
    policy_start_year = 2020
    
    # 最適タイミング分析
    print("\n1. 最適引き出しタイミング分析:")
    best_timing, all_results = optimizer.optimize_withdrawal_timing(
        annual_premium, taxable_income, policy_start_year, 15
    )
    
    print(f"最適引き出しタイミング: {best_timing['引き出し年']}年 ({best_timing['保険期間']}年後)")
    print(f"純利益: {best_timing['純利益']:,.0f}円")
    print(f"実質利回り: {best_timing['実質利回り']:.2%}")
    
    # 所得シナリオ比較
    print("\n2. 所得シナリオ別比較:")
    income_scenarios = [
        ("低所得", 3000000),
        ("高所得", 8000000),
        ("超高所得", 12000000)
    ]
    
    scenario_results = optimizer.analyze_income_scenarios(
        annual_premium, taxable_income, income_scenarios, 
        policy_start_year, policy_start_year + 10
    )
    
    print(scenario_results[["シナリオ", "課税所得", "累計節税効果", "純利益", "実質利回り"]].to_string(index=False))
    
    # 税制改正影響分析
    print("\n3. 税制改正影響分析:")
    reform_impact = optimizer.analyze_tax_reform_impact(
        annual_premium, taxable_income, policy_start_year,
        reform_year=2027, new_deduction_limit=30000
    )
    
    print(f"改正年: {reform_impact['改正年']}")
    print(f"控除額変化: {reform_impact['旧控除上限']:,}円 → {reform_impact['新控除上限']:,}円")
    print(f"年間影響額: {reform_impact['年間影響額']:,.0f}円")


if __name__ == "__main__":
    main()