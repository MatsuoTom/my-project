"""
税金・控除計算の共通ヘルパー関数

このモジュールは、プロジェクト全体で繰り返し使われる
税金計算・控除計算ロジックを一元化します。

使用例:
    >>> from life_insurance.utils.tax_helpers import get_tax_helper
    >>> helper = get_tax_helper()
    >>> result = helper.calculate_annual_tax_savings(120000, 5000000)
    >>> print(f"年間節税額: {result['total_savings']}円")
"""

from typing import Dict
from life_insurance.core import LifeInsuranceDeductionCalculator, TaxCalculator


class TaxDeductionHelper:
    """
    控除・節税計算のヘルパークラス
    
    生命保険料控除額と節税額を計算するための
    統合インターフェースを提供します。
    
    Attributes:
        deduction_calc: 控除額計算機
        tax_calc: 税額計算機
    """
    
    def __init__(self):
        """
        ヘルパーを初期化
        
        内部で LifeInsuranceDeductionCalculator と
        TaxCalculator のインスタンスを作成します。
        """
        self.deduction_calc = LifeInsuranceDeductionCalculator()
        self.tax_calc = TaxCalculator()
    
    def calculate_annual_tax_savings(
        self, 
        annual_premium: float, 
        taxable_income: float = 5_000_000
    ) -> Dict[str, float]:
        """
        年間保険料から節税額を一括計算
        
        生命保険料控除額を計算し、それに基づく
        所得税・住民税の節税額を算出します。
        
        Args:
            annual_premium: 年間保険料（円）
            taxable_income: 課税所得（円）。デフォルトは500万円
        
        Returns:
            dict: 以下のキーを持つ辞書
                - 'deduction' (float): 控除額（円）
                - 'income_tax_savings' (float): 所得税節税額（円）
                - 'resident_tax_savings' (float): 住民税節税額（円）
                - 'total_savings' (float): 合計節税額（円）
        
        Raises:
            ValueError: annual_premium が負の場合
        
        Examples:
            >>> helper = TaxDeductionHelper()
            >>> result = helper.calculate_annual_tax_savings(120000, 5000000)
            >>> result['total_savings']
            12500.0
            
            >>> # 課税所得を省略した場合（デフォルト500万円）
            >>> result = helper.calculate_annual_tax_savings(80000)
            >>> result['deduction']
            40000.0
        """
        if annual_premium < 0:
            raise ValueError("年間保険料は0以上である必要があります")
        
        # 控除額計算
        deduction = self.deduction_calc.calculate_old_deduction(annual_premium)
        
        # 税額計算
        tax_result = self.tax_calc.calculate_tax_savings(deduction, taxable_income)
        
        return {
            'deduction': deduction,
            'income_tax_savings': tax_result['所得税節税額'],
            'resident_tax_savings': tax_result['住民税節税額'],
            'total_savings': tax_result['合計節税額']
        }
    
    def calculate_total_tax_savings_over_years(
        self,
        annual_premium: float,
        years: int,
        taxable_income: float = 5_000_000
    ) -> float:
        """
        複数年の節税額合計を計算
        
        毎年同じ保険料を支払った場合の
        節税額の累計を計算します。
        
        Args:
            annual_premium: 年間保険料（円）
            years: 年数
            taxable_income: 課税所得（円）。デフォルトは500万円
        
        Returns:
            float: 合計節税額（円）
        
        Raises:
            ValueError: years が0以下の場合
        
        Examples:
            >>> helper = TaxDeductionHelper()
            >>> # 年間12万円の保険料を20年間支払った場合
            >>> total = helper.calculate_total_tax_savings_over_years(120000, 20)
            >>> total
            250000.0
        """
        if years <= 0:
            raise ValueError("年数は1以上である必要があります")
        
        annual_result = self.calculate_annual_tax_savings(annual_premium, taxable_income)
        return annual_result['total_savings'] * years
    
    def calculate_monthly_premium_for_max_deduction(self) -> float:
        """
        控除額を最大化する月額保険料を計算
        
        旧生命保険料控除の上限（年間10万円）に達する
        最適な月額保険料を返します。
        
        Returns:
            float: 最適な月額保険料（円）
        
        Examples:
            >>> helper = TaxDeductionHelper()
            >>> helper.calculate_monthly_premium_for_max_deduction()
            8333.333333333334
        """
        # 旧生命保険料控除の上限は年間10万円で達成
        optimal_annual = 100_000
        return optimal_annual / 12
    
    def compare_premium_scenarios(
        self,
        premium_options: list[float],
        taxable_income: float = 5_000_000
    ) -> Dict[float, Dict[str, float]]:
        """
        複数の保険料オプションを比較
        
        異なる保険料での節税効果を一括計算し、
        比較可能な形式で返します。
        
        Args:
            premium_options: 年間保険料のリスト（円）
            taxable_income: 課税所得（円）
        
        Returns:
            dict: 保険料をキーとし、節税額の辞書を値とする辞書
        
        Examples:
            >>> helper = TaxDeductionHelper()
            >>> options = [60000, 100000, 150000]
            >>> results = helper.compare_premium_scenarios(options)
            >>> results[100000]['total_savings']
            12500.0
        """
        results = {}
        for premium in premium_options:
            results[premium] = self.calculate_annual_tax_savings(
                premium, taxable_income
            )
        return results


# シングルトンインスタンス（UIから簡単に使える）
_helper_instance = None


def get_tax_helper() -> TaxDeductionHelper:
    """
    税金ヘルパーのシングルトンインスタンスを取得
    
    複数回呼び出しても同じインスタンスが返されるため、
    初期化コストを最小化できます。
    
    Returns:
        TaxDeductionHelper: ヘルパーインスタンス
    
    Examples:
        >>> from life_insurance.utils.tax_helpers import get_tax_helper
        >>> helper1 = get_tax_helper()
        >>> helper2 = get_tax_helper()
        >>> helper1 is helper2
        True
    """
    global _helper_instance
    if _helper_instance is None:
        _helper_instance = TaxDeductionHelper()
    return _helper_instance


def reset_tax_helper() -> None:
    """
    シングルトンインスタンスをリセット（テスト用）
    
    主にテスト時に使用します。
    通常のアプリケーションコードでは使用しないでください。
    
    Examples:
        >>> from life_insurance.utils.tax_helpers import reset_tax_helper
        >>> reset_tax_helper()  # テストのクリーンアップ
    """
    global _helper_instance
    _helper_instance = None
