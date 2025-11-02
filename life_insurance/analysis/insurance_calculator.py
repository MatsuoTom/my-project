"""
保険価値計算の統合エンジン

このモジュールは生命保険の価値計算を一元化し、
重複コードを削減するための統合エンジンを提供します。

Phase 1で作成したtax_helperと連携して、
保険価値計算、節税効果、手数料計算などを統一的に処理します。

Phase 3: 共通基盤（common/）を利用して重複コードを削減
"""

from typing import Tuple, Optional
from life_insurance.models import InsurancePlan, FundPlan, InsuranceResult
from life_insurance.utils.tax_helpers import get_tax_helper
from life_insurance.core.tax_calculator import TaxCalculator
from common.calculators.base_calculator import BaseFinancialCalculator, CompoundInterestMixin
from common.utils.math_utils import calculate_annuity_future_value


class InsuranceCalculator(BaseFinancialCalculator, CompoundInterestMixin):
    """
    生命保険価値計算の統合エンジン
    
    Phase 2で実装された統合計算エンジン。
    Phase 3で共通基盤（BaseFinancialCalculator, CompoundInterestMixin）を継承。
    保険価値計算の重複を削減し、一元化された計算ロジックを提供。
    
    Attributes:
        tax_helper: 税金計算ヘルパー（Phase 1で実装）
        tax_calculator: 所得税計算機
    
    Examples:
        >>> calculator = InsuranceCalculator()
        >>> plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
        >>> result = calculator.calculate_simple_value(plan)
        >>> print(f"保険価値: {result.insurance_value:,.0f}円")
    """
    
    def __init__(self):
        """初期化"""
        super().__init__()  # BaseFinancialCalculator の初期化
        self.tax_helper = get_tax_helper()
        self.tax_calculator = TaxCalculator()
    
    def calculate(self, *args, **kwargs):
        """
        BaseFinancialCalculator の抽象メソッド実装
        
        保険計算は複数のメソッドに分かれているため、
        このメソッドは calculate_simple_value を呼び出します。
        """
        return self.calculate_simple_value(*args, **kwargs)
    
    def validate_inputs(self, plan: InsurancePlan) -> bool:
        """
        入力値の検証
        
        Args:
            plan: 保険プラン
            
        Returns:
            bool: 検証結果
            
        Raises:
            ValueError: 不正な入力値の場合
        """
        if plan.monthly_premium <= 0:
            raise ValueError("月額保険料は正の値である必要があります")
        if plan.investment_period <= 0:
            raise ValueError("運用期間は正の値である必要があります")
        if plan.annual_rate < 0:
            raise ValueError("年率は0以上である必要があります")
        if plan.fee_rate < 0 or plan.fee_rate >= 1:
            raise ValueError("手数料率は0以上1未満である必要があります")
        
        return True
    
    # ==========================================
    # ヘルパーメソッド（内部使用）
    # ==========================================
    
    # _calculate_compound_interest は削除（common.utils.math_utils.calculate_annuity_future_value を使用）
    
    def _calculate_fees(
        self,
        plan: InsurancePlan,
        insurance_value: float,
        total_months: int
    ) -> Tuple[float, float]:
        """
        手数料計算（積立手数料 + 残高手数料）
        
        生命保険の手数料を2種類計算します：
        1. 積立手数料: 毎月の保険料に対して課される手数料
        2. 残高手数料: 保険残高に対して毎月課される手数料
        
        Args:
            plan: 保険プラン
            insurance_value: 保険価値（残高、円）
            total_months: 総月数
            
        Returns:
            (積立手数料合計, 残高手数料合計) のタプル（円）
            
        Examples:
            >>> calc = InsuranceCalculator()
            >>> plan = InsurancePlan(
            ...     monthly_premium=30000,
            ...     annual_rate=2.0,
            ...     investment_period=20,
            ...     fee_rate=0.013,
            ...     balance_fee_rate=0.00008
            ... )
            >>> insurance_value = 8000000
            >>> total_months = 240
            >>> setup_fee, balance_fee = calc._calculate_fees(plan, insurance_value, total_months)
            >>> print(f"積立手数料: {setup_fee:,.0f}円")
            積立手数料: 93,600円
            >>> print(f"残高手数料: {balance_fee:,.0f}円")
            残高手数料: 153,600円
            
        Notes:
            - 積立手数料は月額保険料 × 手数料率 × 総月数
            - 残高手数料は保険価値 × 残高手数料率 × 総月数
            - 実際の計算では月次複利の影響で若干の誤差が生じる可能性がある
        """
        # 積立手数料（月額保険料に対する手数料）
        setup_fee = plan.monthly_premium * plan.fee_rate * total_months
        
        # 残高手数料（保険残高に対する手数料）
        balance_fee = insurance_value * plan.balance_fee_rate * total_months
        
        return setup_fee, balance_fee
    
    def _calculate_tax_benefit(
        self,
        annual_premium: float,
        period: int,
        taxable_income: float
    ) -> float:
        """
        税制優遇効果計算
        
        生命保険料控除による節税効果を計算します。
        Phase 1で実装したtax_helperを利用します。
        
        Args:
            annual_premium: 年間保険料（円）
            period: 期間（年）
            taxable_income: 課税所得（円）
            
        Returns:
            累計節税額（円）
            
        Examples:
            >>> calc = InsuranceCalculator()
            >>> annual_premium = 360000  # 月3万円 × 12
            >>> period = 20
            >>> taxable_income = 5000000
            >>> tax_savings = calc._calculate_tax_benefit(annual_premium, period, taxable_income)
            >>> print(f"累計節税額: {tax_savings:,.0f}円")
            累計節税額: 480,000円
            
        Notes:
            - tax_helperはPhase 1で実装済み
            - 旧生命保険料控除を使用（控除上限: 50,000円）
            - 実際の節税額は所得税率と住民税率により変動
        """
        tax_result = self.tax_helper.calculate_annual_tax_savings(annual_premium, taxable_income)
        return tax_result['total_savings'] * period
    
    def _calculate_surrender_deduction(
        self,
        surrender_value: float,
        years: int
    ) -> float:
        """
        解約控除計算
        
        保険解約時の控除額を計算します。
        経過年数に応じて控除率が減少します。
        
        Args:
            surrender_value: 解約返戻金（控除前、円）
            years: 経過年数
            
        Returns:
            解約控除額（円）
            
        Examples:
            >>> calc = InsuranceCalculator()
            >>> surrender_value = 7500000
            >>> years = 5
            >>> deduction = calc._calculate_surrender_deduction(surrender_value, years)
            >>> print(f"解約控除額: {deduction:,.0f}円")
            解約控除額: 375,000円  # 5% (10% - 5年×1%)
            
        Notes:
            - 初年度: 10%控除
            - 毎年1%ずつ減少
            - 10年以降: 控除なし（0%）
            - 控除率 = max(0, 10% - 経過年数%)
        """
        # 控除率: 10%から毎年1%減少（最小0%）
        deduction_rate = max(0, 0.1 - (years * 0.01))
        return surrender_value * deduction_rate
    
    def _calculate_withdrawal_tax(
        self,
        profit: float,
        taxable_income: float
    ) -> float:
        """
        解約時の一時所得課税計算
        
        保険解約時の利益に対する一時所得税を計算します。
        一時所得の特別控除（50万円）と1/2課税を考慮します。
        
        Args:
            profit: 解約利益（解約返戻金 - 払込保険料、円）
            taxable_income: 課税所得（円）
            
        Returns:
            解約時所得税額（円）
            
        Examples:
            >>> calc = InsuranceCalculator()
            >>> profit = 800000  # 80万円の利益
            >>> taxable_income = 5000000
            >>> tax = calc._calculate_withdrawal_tax(profit, taxable_income)
            >>> print(f"解約時所得税: {tax:,.0f}円")
            解約時所得税: 30,000円  # (80万 - 50万) × 1/2 = 15万円が課税対象
            
        Notes:
            - 一時所得の特別控除: 50万円
            - 課税対象額 = (利益 - 50万円) × 1/2
            - 利益が50万円以下の場合は非課税
            - 総合課税として所得税・住民税を計算
        """
        # 一時所得の計算（50万円特別控除、1/2課税）
        taxable_profit = max(0, profit - 500000) / 2
        
        if taxable_profit > 0:
            # 一時所得を含む場合と含まない場合の所得税差額を計算
            with_profit_tax = self.tax_calculator.calculate_income_tax(taxable_income + taxable_profit)
            original_tax = self.tax_calculator.calculate_income_tax(taxable_income)
            return with_profit_tax["合計所得税"] - original_tax["合計所得税"]
        
        return 0.0
    
    # ==========================================
    # コアメソッド（公開API）
    # ==========================================
    
    def calculate_simple_value(
        self,
        plan: InsurancePlan,
        taxable_income: float = 5000000
    ) -> InsuranceResult:
        """
        単純継続の保険価値計算
        
        保険を継続した場合の最終価値を計算します。
        手数料、節税効果、解約控除を考慮した実質的な価値を算出します。
        
        Args:
            plan: 保険プラン
            taxable_income: 課税所得（円、デフォルト: 500万円）
            
        Returns:
            InsuranceResult: 計算結果（保険価値、手数料、節税効果等）
            
        Examples:
            >>> calculator = InsuranceCalculator()
            >>> plan = InsurancePlan(
            ...     monthly_premium=30000,
            ...     annual_rate=2.0,
            ...     investment_period=20
            ... )
            >>> result = calculator.calculate_simple_value(plan)
            >>> print(f"保険価値: {result.insurance_value:,.0f}円")
            保険価値: 8,732,145円
            >>> print(f"実質利回り: {result.actual_return_rate:.2f}%")
            実質利回り: 1.23%
            
        Notes:
            - 月次複利計算を使用
            - 手数料は積立手数料と残高手数料の2種類
            - 節税効果は生命保険料控除を適用
            - 解約控除は経過年数により減少（最大10%）
        """
        total_months = plan.investment_period * 12
        monthly_rate = plan.annual_rate / 100 / 12
        
        # 1. 手数料控除後の月次積立額
        net_monthly_premium = plan.monthly_premium * (1 - plan.fee_rate)
        
        # 2. 複利積立計算（手数料控除後）- 共通基盤を使用
        gross_value = calculate_annuity_future_value(
            payment=net_monthly_premium,
            rate=monthly_rate,
            periods=total_months
        )
        
        # 3. 残高手数料の計算
        # 注: 簡略化のため、最終残高に対する総手数料として計算
        setup_fee, balance_fee = self._calculate_fees(plan, gross_value, total_months)
        
        # 残高手数料を複利計算で控除（簡略モデル）
        # 実際は月次で控除されるが、ここでは総額で近似
        insurance_value = gross_value * (1 - plan.balance_fee_rate * total_months)
        
        # 4. 節税効果計算
        annual_premium = plan.monthly_premium * 12
        tax_benefit = self._calculate_tax_benefit(
            annual_premium,
            plan.investment_period,
            taxable_income
        )
        
        # 5. 総支払額
        total_paid = plan.monthly_premium * total_months
        
        # 6. 解約控除（満期時の控除率は0だが、中途解約の参考値）
        surrender_deduction = self._calculate_surrender_deduction(
            insurance_value,
            plan.investment_period
        )
        
        # 7. 解約返戻金（控除後）
        final_surrender_value = insurance_value - surrender_deduction
        
        # 8. 利益と課税
        profit = final_surrender_value - total_paid
        withdrawal_tax = self._calculate_withdrawal_tax(profit, taxable_income)
        
        # 9. 手取り額
        net_value = final_surrender_value - withdrawal_tax
        
        # 10. 実質利回り計算
        if total_paid > 0:
            total_return_rate = ((net_value + tax_benefit) / total_paid - 1) * 100
            actual_return_rate = (((net_value + tax_benefit) / total_paid) ** (1 / plan.investment_period) - 1) * 100
        else:
            total_return_rate = 0.0
            actual_return_rate = 0.0
        
        return InsuranceResult(
            insurance_value=insurance_value,
            total_paid=total_paid,
            total_fees=setup_fee + balance_fee,
            tax_savings=tax_benefit,
            net_value=net_value,
            return_rate=actual_return_rate,
            # 拡張フィールド
            setup_fee=setup_fee,
            balance_fee=balance_fee,
            tax_benefit=tax_benefit,
            surrender_value=final_surrender_value,
            withdrawal_tax=withdrawal_tax,
            total_return_rate=total_return_rate,
            actual_return_rate=actual_return_rate
        )
    
    def calculate_partial_withdrawal_value(
        self,
        plan: InsurancePlan,
        withdrawal_ratio: float,
        withdrawal_interval: int,
        reinvestment_plan: Optional[FundPlan] = None,
        taxable_income: float = 5000000
    ) -> InsuranceResult:
        """
        部分解約戦略の価値計算
        
        定期的に一部を解約し、解約金を再投資する戦略の価値を計算します。
        月次シミュレーションにより、時系列での価値変動を追跡します。
        
        Args:
            plan: 保険プラン
            withdrawal_ratio: 解約割合（例: 0.3 = 30%）
            withdrawal_interval: 解約間隔（年）
            reinvestment_plan: 再投資プラン（Noneの場合は現金保有）
            taxable_income: 課税所得（円）
            
        Returns:
            InsuranceResult: 計算結果（保険残高+再投資残高の合計）
            
        Examples:
            >>> calculator = InsuranceCalculator()
            >>> plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
            >>> fund = FundPlan(reinvestment_rate=5.0)
            >>> result = calculator.calculate_partial_withdrawal_value(
            ...     plan, withdrawal_ratio=0.3, withdrawal_interval=5, reinvestment_plan=fund
            ... )
            >>> print(f"総資産: {result.insurance_value + result.reinvestment_value:,.0f}円")
            
        Notes:
            - 月次シミュレーションで精密な計算
            - 各解約時に一時所得税を計算
            - 再投資は投資信託またはNISA枠を想定
            - 解約手数料とキャピタルゲイン税も考慮
        """
        total_months = plan.investment_period * 12
        monthly_rate = plan.annual_rate / 100 / 12
        
        # 初期値
        insurance_balance = 0.0
        reinvestment_balance = 0.0
        total_paid = 0.0
        total_insurance_fees = 0.0
        total_withdrawal_tax = 0.0
        total_reinvestment_tax = 0.0
        
        # 月次シミュレーション
        for month in range(1, total_months + 1):
            # 1. 保険料積立
            premium_fee = plan.monthly_premium * plan.fee_rate
            net_premium = plan.monthly_premium - premium_fee
            total_insurance_fees += premium_fee
            total_paid += plan.monthly_premium
            
            # 2. 保険残高の運用
            insurance_balance = (insurance_balance + net_premium) * (1 + monthly_rate)
            
            # 3. 残高手数料
            balance_fee = insurance_balance * plan.balance_fee_rate
            insurance_balance -= balance_fee
            total_insurance_fees += balance_fee
            
            # 4. 再投資の運用（月次複利）
            if reinvestment_plan:
                monthly_reinvestment_rate = reinvestment_plan.reinvestment_rate / 100 / 12
                reinvestment_balance *= (1 + monthly_reinvestment_rate)
            
            # 5. 部分解約判定
            if month % (withdrawal_interval * 12) == 0 and month < total_months:
                # 解約額計算
                withdrawal_amount = insurance_balance * withdrawal_ratio
                withdrawal_fee = withdrawal_amount * plan.withdrawal_fee_rate
                net_withdrawal = withdrawal_amount - withdrawal_fee
                
                # 解約所得税（一時所得）
                paid_for_withdrawn = total_paid * withdrawal_ratio
                profit = net_withdrawal - paid_for_withdrawn
                withdrawal_tax = self._calculate_withdrawal_tax(profit, taxable_income)
                total_withdrawal_tax += withdrawal_tax
                
                # 再投資へ移動
                reinvestment_addition = net_withdrawal - withdrawal_tax
                if reinvestment_plan and reinvestment_plan.use_nisa and reinvestment_addition <= 1200000:
                    # NISA枠利用（非課税）
                    reinvestment_balance += reinvestment_addition
                else:
                    # 通常の投資信託（課税対象）
                    reinvestment_balance += reinvestment_addition
                
                # 保険残高を更新
                insurance_balance *= (1 - withdrawal_ratio)
                total_paid *= (1 - withdrawal_ratio)
        
        # 最終的な解約（残りの保険を全額解約）
        final_surrender_deduction = self._calculate_surrender_deduction(
            insurance_balance,
            plan.investment_period
        )
        final_surrender_value = insurance_balance - final_surrender_deduction
        final_profit = final_surrender_value - total_paid
        final_withdrawal_tax = self._calculate_withdrawal_tax(final_profit, taxable_income)
        total_withdrawal_tax += final_withdrawal_tax
        
        # 再投資のキャピタルゲイン課税
        if reinvestment_plan and not reinvestment_plan.use_nisa:
            reinvestment_profit = reinvestment_balance * 0.3  # 推定利益率30%
            capital_gains_tax = reinvestment_profit * 0.20315  # 20.315%課税
            total_reinvestment_tax = capital_gains_tax
        else:
            total_reinvestment_tax = 0.0
        
        # 手取り額
        net_insurance = final_surrender_value - final_withdrawal_tax
        net_reinvestment = reinvestment_balance - total_reinvestment_tax
        total_net_value = net_insurance + net_reinvestment
        
        # 節税効果
        annual_premium = plan.monthly_premium * 12
        tax_benefit = self._calculate_tax_benefit(
            annual_premium,
            plan.investment_period,
            taxable_income
        )
        
        # 実質利回り
        total_paid_overall = plan.monthly_premium * total_months
        if total_paid_overall > 0:
            total_return_rate = ((total_net_value + tax_benefit) / total_paid_overall - 1) * 100
            actual_return_rate = (((total_net_value + tax_benefit) / total_paid_overall) ** (1 / plan.investment_period) - 1) * 100
        else:
            total_return_rate = 0.0
            actual_return_rate = 0.0
        
        return InsuranceResult(
            insurance_value=net_insurance,
            total_paid=total_paid_overall,
            total_fees=total_insurance_fees,
            tax_savings=tax_benefit,
            net_value=total_net_value,
            return_rate=actual_return_rate,
            # 拡張フィールド
            reinvestment_value=net_reinvestment,
            setup_fee=total_insurance_fees - (insurance_balance * plan.balance_fee_rate * total_months),
            balance_fee=insurance_balance * plan.balance_fee_rate * total_months,
            tax_benefit=tax_benefit,
            surrender_value=final_surrender_value,
            withdrawal_tax=total_withdrawal_tax,
            reinvestment_tax=total_reinvestment_tax,
            total_return_rate=total_return_rate,
            actual_return_rate=actual_return_rate
        )
    
    def calculate_switching_value(
        self,
        plan: InsurancePlan,
        switching_year: int,
        fund_plan: FundPlan,
        taxable_income: float = 5000000
    ) -> InsuranceResult:
        """
        乗り換え戦略の価値計算
        
        保険を途中解約して投資信託に乗り換える戦略の価値を計算します。
        2段階計算（保険期間→投資信託期間）を実施します。
        
        Args:
            plan: 保険プラン
            switching_year: 乗り換え年（何年目に解約するか）
            fund_plan: 投資信託プラン
            taxable_income: 課税所得（円）
            
        Returns:
            InsuranceResult: 計算結果（乗り換え後の最終価値）
            
        Examples:
            >>> calculator = InsuranceCalculator()
            >>> plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
            >>> fund = FundPlan(reinvestment_rate=5.0, use_nisa=True)
            >>> result = calculator.calculate_switching_value(plan, switching_year=10, fund_plan=fund)
            >>> print(f"最終資産: {result.net_value:,.0f}円")
            
        Notes:
            - Phase 1: 保険で積立（switching_yearまで）
            - Phase 2: 解約金を投資信託で運用（残り期間）
            - 解約控除と一時所得税を考慮
            - NISA枠利用で運用益非課税の選択可能
        """
        # Phase 1: 保険期間（switching_yearまで）
        switching_months = switching_year * 12
        monthly_rate = plan.annual_rate / 100 / 12
        
        insurance_balance = 0.0
        total_paid = 0.0
        total_insurance_fees = 0.0
        
        for month in range(1, switching_months + 1):
            # 保険料積立
            premium_fee = plan.monthly_premium * plan.fee_rate
            net_premium = plan.monthly_premium - premium_fee
            total_insurance_fees += premium_fee
            total_paid += plan.monthly_premium
            
            # 保険残高の運用
            insurance_balance = (insurance_balance + net_premium) * (1 + monthly_rate)
            
            # 残高手数料
            balance_fee = insurance_balance * plan.balance_fee_rate
            insurance_balance -= balance_fee
            total_insurance_fees += balance_fee
        
        # 解約時の控除と税金
        surrender_deduction = self._calculate_surrender_deduction(insurance_balance, switching_year)
        surrender_value = insurance_balance - surrender_deduction
        profit = surrender_value - total_paid
        withdrawal_tax = self._calculate_withdrawal_tax(profit, taxable_income)
        net_surrender = surrender_value - withdrawal_tax
        
        # Phase 2: 投資信託期間（残り期間）
        remaining_years = plan.investment_period - switching_year
        remaining_months = remaining_years * 12
        fund_monthly_rate = fund_plan.reinvestment_rate / 100 / 12
        
        # 解約金を一括投資 + 月次積立
        fund_balance = net_surrender
        for month in range(1, remaining_months + 1):
            # 既存資産の運用
            fund_balance *= (1 + fund_monthly_rate)
            
            # 月次積立（保険料と同額を投資信託に）
            fund_balance += plan.monthly_premium
            total_paid += plan.monthly_premium
        
        # 投資信託の課税（キャピタルゲイン）
        if fund_plan.use_nisa:
            # NISA枠: 非課税
            reinvestment_tax = 0.0
            net_fund_value = fund_balance
        else:
            # 通常: 20.315%課税
            fund_profit = fund_balance - (net_surrender + plan.monthly_premium * remaining_months)
            reinvestment_tax = fund_profit * 0.20315
            net_fund_value = fund_balance - reinvestment_tax
        
        # 節税効果（保険期間のみ）
        annual_premium = plan.monthly_premium * 12
        tax_benefit = self._calculate_tax_benefit(
            annual_premium,
            switching_year,
            taxable_income
        )
        
        # 実質利回り
        total_paid_overall = plan.monthly_premium * plan.investment_period * 12
        if total_paid_overall > 0:
            total_return_rate = ((net_fund_value + tax_benefit) / total_paid_overall - 1) * 100
            actual_return_rate = (((net_fund_value + tax_benefit) / total_paid_overall) ** (1 / plan.investment_period) - 1) * 100
        else:
            total_return_rate = 0.0
            actual_return_rate = 0.0
        
        return InsuranceResult(
            insurance_value=0.0,  # 最終的に保険は解約済み
            total_paid=total_paid_overall,
            total_fees=total_insurance_fees,
            tax_savings=tax_benefit,
            net_value=net_fund_value,
            return_rate=actual_return_rate,
            # 拡張フィールド
            reinvestment_value=net_fund_value,
            setup_fee=total_insurance_fees,
            balance_fee=0.0,
            tax_benefit=tax_benefit,
            surrender_value=surrender_value,
            withdrawal_tax=withdrawal_tax,
            reinvestment_tax=reinvestment_tax,
            total_return_rate=total_return_rate,
            actual_return_rate=actual_return_rate
        )
    
    def calculate_total_benefit(
        self,
        plan: InsurancePlan,
        taxable_income: float = 5000000
    ) -> dict:
        """
        総合利益の詳細計算
        
        保険の総合的な利益を詳細に分解して計算します。
        節税効果、運用益、手数料、税金のすべてを可視化します。
        
        Args:
            plan: 保険プラン
            taxable_income: 課税所得（円）
            
        Returns:
            dict: 詳細な利益分解
                - gross_benefit: 総利益（税引前）
                - tax_benefit: 節税効果
                - investment_gain: 運用益
                - total_fees: 総手数料
                - total_tax: 総税金
                - net_benefit: 純利益（手取り）
                - benefit_breakdown: 利益の内訳
                
        Examples:
            >>> calculator = InsuranceCalculator()
            >>> plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
            >>> benefit = calculator.calculate_total_benefit(plan)
            >>> print(f"純利益: {benefit['net_benefit']:,.0f}円")
            >>> print(f"実質利回り: {benefit['actual_return_rate']:.2f}%")
        """
        result = self.calculate_simple_value(plan, taxable_income)
        
        # 利益の分解
        gross_benefit = result.insurance_value - result.total_paid
        investment_gain = result.insurance_value - result.total_paid
        net_benefit = result.net_value - result.total_paid + result.tax_benefit
        
        return {
            'gross_benefit': gross_benefit,
            'tax_benefit': result.tax_benefit,
            'investment_gain': investment_gain,
            'total_fees': result.total_fees,
            'total_tax': result.withdrawal_tax,
            'net_benefit': net_benefit,
            'actual_return_rate': result.actual_return_rate,
            'benefit_breakdown': {
                '運用益': investment_gain,
                '節税効果': result.tax_benefit,
                '手数料': -result.total_fees,
                '税金': -result.withdrawal_tax,
                '純利益': net_benefit
            }
        }
    
    def calculate_comparison(
        self,
        plan: InsurancePlan,
        fund_plan: FundPlan,
        taxable_income: float = 5000000
    ) -> dict:
        """
        保険と投資信託の包括的比較
        
        保険単純継続、投資信託単純運用、乗り換え戦略の3パターンを比較します。
        各戦略の最終価値、実質利回り、リスクを算出します。
        
        Args:
            plan: 保険プラン
            fund_plan: 投資信託プラン
            taxable_income: 課税所得（円）
            
        Returns:
            dict: 比較結果
                - insurance_only: 保険単純継続の結果
                - fund_only: 投資信託のみの結果
                - switching: 乗り換え戦略の結果（複数年）
                - recommendation: 推奨戦略
                
        Examples:
            >>> calculator = InsuranceCalculator()
            >>> plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
            >>> fund = FundPlan(reinvestment_rate=5.0, use_nisa=True)
            >>> comparison = calculator.calculate_comparison(plan, fund)
            >>> print(f"推奨: {comparison['recommendation']['strategy']}")
            >>> print(f"期待リターン: {comparison['recommendation']['expected_value']:,.0f}円")
        """
        # 1. 保険単純継続
        insurance_result = self.calculate_simple_value(plan, taxable_income)
        
        # 2. 投資信託のみ（保険料と同額を投資信託に）
        total_months = plan.investment_period * 12
        fund_monthly_rate = fund_plan.reinvestment_rate / 100 / 12
        
        fund_balance = 0.0
        for month in range(1, total_months + 1):
            fund_balance = (fund_balance + plan.monthly_premium) * (1 + fund_monthly_rate)
        
        total_paid = plan.monthly_premium * total_months
        
        # 投資信託の課税
        if fund_plan.use_nisa:
            fund_tax = 0.0
            net_fund = fund_balance
        else:
            fund_profit = fund_balance - total_paid
            fund_tax = fund_profit * 0.20315
            net_fund = fund_balance - fund_tax
        
        fund_return_rate = ((net_fund / total_paid) ** (1 / plan.investment_period) - 1) * 100
        
        # 3. 乗り換え戦略（5年、10年、15年で比較）
        switching_results = {}
        for year in [5, 10, 15]:
            if year < plan.investment_period:
                switch_result = self.calculate_switching_value(plan, year, fund_plan, taxable_income)
                switching_results[f'{year}年目'] = {
                    'net_value': switch_result.net_value,
                    'return_rate': switch_result.actual_return_rate,
                    'tax_benefit': switch_result.tax_benefit
                }
        
        # 4. 推奨戦略の決定
        strategies = {
            '保険継続': insurance_result.net_value + insurance_result.tax_benefit,
            '投資信託のみ': net_fund
        }
        
        for year, data in switching_results.items():
            strategies[f'乗り換え({year})'] = data['net_value'] + data['tax_benefit']
        
        best_strategy = max(strategies, key=strategies.get)
        best_value = strategies[best_strategy]
        
        return {
            'insurance_only': {
                'net_value': insurance_result.net_value,
                'tax_benefit': insurance_result.tax_benefit,
                'total_value': insurance_result.net_value + insurance_result.tax_benefit,
                'return_rate': insurance_result.actual_return_rate
            },
            'fund_only': {
                'net_value': net_fund,
                'tax_benefit': 0.0,
                'total_value': net_fund,
                'return_rate': fund_return_rate
            },
            'switching': switching_results,
            'recommendation': {
                'strategy': best_strategy,
                'expected_value': best_value,
                'advantage_over_insurance': best_value - strategies['保険継続'],
                'advantage_over_fund': best_value - strategies['投資信託のみ']
            }
        }
    
    def calculate_breakeven_year(
        self,
        plan: InsurancePlan,
        taxable_income: float = 5000000
    ) -> dict:
        """
        元本回収年の計算
        
        保険の元本（総支払額）を回収できる年を計算します。
        年次シミュレーションにより、各年の解約価値を追跡します。
        
        Args:
            plan: 保険プラン
            taxable_income: 課税所得（円）
            
        Returns:
            dict: 元本回収分析
                - breakeven_year: 元本回収年（見つからない場合は None）
                - yearly_values: 各年の解約価値
                - breakeven_value: 元本回収時の価値
                
        Examples:
            >>> calculator = InsuranceCalculator()
            >>> plan = InsurancePlan(monthly_premium=30000, annual_rate=2.0, investment_period=20)
            >>> breakeven = calculator.calculate_breakeven_year(plan)
            >>> if breakeven['breakeven_year']:
            ...     print(f"元本回収: {breakeven['breakeven_year']}年目")
            ... else:
            ...     print("元本回収不可")
            
        Notes:
            - 最大30年までシミュレーション
            - 各年の解約価値 = 保険残高 - 解約控除 - 税金
            - 節税効果も考慮した実質的な元本回収年を算出
        """
        monthly_rate = plan.annual_rate / 100 / 12
        max_years = min(plan.investment_period, 30)
        
        yearly_values = []
        breakeven_year = None
        breakeven_value = None
        
        for year in range(1, max_years + 1):
            months = year * 12
            
            # 保険残高の計算
            insurance_balance = 0.0
            total_paid = 0.0
            total_fees = 0.0
            
            for month in range(1, months + 1):
                premium_fee = plan.monthly_premium * plan.fee_rate
                net_premium = plan.monthly_premium - premium_fee
                total_fees += premium_fee
                total_paid += plan.monthly_premium
                
                insurance_balance = (insurance_balance + net_premium) * (1 + monthly_rate)
                
                balance_fee = insurance_balance * plan.balance_fee_rate
                insurance_balance -= balance_fee
                total_fees += balance_fee
            
            # 解約価値の計算
            surrender_deduction = self._calculate_surrender_deduction(insurance_balance, year)
            surrender_value = insurance_balance - surrender_deduction
            profit = surrender_value - total_paid
            withdrawal_tax = self._calculate_withdrawal_tax(profit, taxable_income)
            net_value = surrender_value - withdrawal_tax
            
            # 節税効果
            annual_premium = plan.monthly_premium * 12
            tax_benefit = self._calculate_tax_benefit(annual_premium, year, taxable_income)
            
            # 実質的な価値（節税効果込み）
            total_value = net_value + tax_benefit
            
            yearly_values.append({
                'year': year,
                'total_paid': total_paid,
                'surrender_value': surrender_value,
                'net_value': net_value,
                'tax_benefit': tax_benefit,
                'total_value': total_value,
                'breakeven': total_value >= total_paid
            })
            
            # 元本回収年の判定
            if breakeven_year is None and total_value >= total_paid:
                breakeven_year = year
                breakeven_value = total_value
        
        return {
            'breakeven_year': breakeven_year,
            'breakeven_value': breakeven_value,
            'yearly_values': yearly_values,
            'total_paid_at_end': plan.monthly_premium * plan.investment_period * 12,
            'breakeven_ratio': breakeven_value / (plan.monthly_premium * breakeven_year * 12) if breakeven_year else None
        }
