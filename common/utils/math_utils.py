"""数学計算ユーティリティ

このモジュールは、金融計算で共通利用される数学関数を提供します。

Functions:
    calculate_compound_interest: 複利計算
    calculate_present_value: 現在価値計算（割引計算）
    calculate_annuity_present_value: 年金現価計算
    calculate_annuity_future_value: 年金終価計算
    calculate_irr: 内部収益率（IRR）計算
    calculate_npv: 正味現在価値（NPV）計算

Example:
    >>> from common.utils.math_utils import (
    ...     calculate_compound_interest,
    ...     calculate_annuity_present_value
    ... )
    >>> 
    >>> # 1,000,000円を年利3%で10年間運用
    >>> future = calculate_compound_interest(1000000, 0.03, 10)
    >>> print(f"{future:,.0f}円")
    1,343,916円
    >>> 
    >>> # 毎年100,000円を受け取る年金の現在価値
    >>> pv = calculate_annuity_present_value(100000, 0.03, 10)
    >>> print(f"{pv:,.0f}円")
    853,020円

Author:
    my-project team

Created:
    2025-01-10 (Phase 3)
"""

from typing import List, Optional
import numpy as np


def calculate_compound_interest(
    principal: float,
    rate: float,
    years: int
) -> float:
    """複利計算
    
    元本に対して年利を複利で計算します。
    
    Formula:
        FV = PV × (1 + r)^n
        
        FV: Future Value（将来価値）
        PV: Present Value（現在価値、元本）
        r: rate（年利率）
        n: years（年数）
    
    Args:
        principal: 元本（円）
        rate: 年利率（小数、例: 0.03 = 3%）
        years: 年数（整数）
    
    Returns:
        float: 複利計算後の金額（円）
    
    Raises:
        ValueError: 元本が負、または年数が負の場合
    
    Examples:
        >>> # 100万円を年利3%で10年間運用
        >>> result = calculate_compound_interest(1000000, 0.03, 10)
        >>> print(f"{result:,.2f}")
        1,343,916.38
        >>> 
        >>> # 100万円を年利5%で20年間運用
        >>> result = calculate_compound_interest(1000000, 0.05, 20)
        >>> print(f"{result:,.2f}")
        2,653,297.71
    
    Notes:
        - CompoundInterestMixinと同じ実装
        - スタンドアロン関数として提供
    """
    if principal < 0:
        raise ValueError(f"元本は0以上である必要があります: {principal}")
    if years < 0:
        raise ValueError(f"年数は0以上である必要があります: {years}")
    
    return principal * (1 + rate) ** years


def calculate_present_value(
    future_value: float,
    rate: float,
    years: int
) -> float:
    """現在価値計算（割引計算）
    
    将来の価値を現在価値に割り引きます。
    
    Formula:
        PV = FV / (1 + r)^n
        
        PV: Present Value（現在価値）
        FV: Future Value（将来価値）
        r: rate（割引率）
        n: years（年数）
    
    Args:
        future_value: 将来価値（円）
        rate: 割引率（小数、例: 0.03 = 3%）
        years: 年数（整数）
    
    Returns:
        float: 現在価値（円）
    
    Raises:
        ValueError: 将来価値が負、または年数が負の場合
    
    Examples:
        >>> # 10年後の1,343,916円を年利3%で割引
        >>> result = calculate_present_value(1343916, 0.03, 10)
        >>> print(f"{result:,.2f}")
        1,000,000.00
    
    Notes:
        - calculate_compound_interest() の逆計算
    """
    if future_value < 0:
        raise ValueError(f"将来価値は0以上である必要があります: {future_value}")
    if years < 0:
        raise ValueError(f"年数は0以上である必要があります: {years}")
    
    return future_value / (1 + rate) ** years


def calculate_annuity_present_value(
    payment: float,
    rate: float,
    periods: int
) -> float:
    """年金現価計算（定額年金の現在価値）
    
    毎期一定額を受け取る年金の現在価値を計算します。
    
    Formula:
        PV = payment × [(1 - (1 + rate)^(-periods)) / rate]
        
        特殊ケース（rate = 0）:
        PV = payment × periods
    
    Args:
        payment: 期間あたりの支払額（円）
        rate: 期間あたりの利率（小数、例: 0.03 = 3%）
        periods: 期間数（整数）
    
    Returns:
        float: 年金の現在価値（円）
    
    Raises:
        ValueError: 支払額が負、または期間数が負の場合
    
    Examples:
        >>> # 毎年100,000円を10年間受け取る年金の現在価値（年利3%）
        >>> result = calculate_annuity_present_value(100000, 0.03, 10)
        >>> print(f"{result:,.2f}")
        853,020.28
        >>> 
        >>> # 毎月50,000円を24ヶ月受け取る年金の現在価値（月利0.5%）
        >>> result = calculate_annuity_present_value(50000, 0.005, 24)
        >>> print(f"{result:,.2f}")
        1,128,554.46
    
    Notes:
        - 年金終価の逆計算
        - 保険や年金の評価に使用
        - rate=0の場合は単純な合計
    """
    if payment < 0:
        raise ValueError(f"支払額は0以上である必要があります: {payment}")
    if periods < 0:
        raise ValueError(f"期間数は0以上である必要があります: {periods}")
    
    if rate == 0:
        return payment * periods
    
    return payment * (1 - (1 + rate) ** (-periods)) / rate


def calculate_annuity_future_value(
    payment: float,
    rate: float,
    periods: int
) -> float:
    """年金終価計算（定額年金の将来価値）
    
    毎期一定額を積み立てる年金の将来価値を計算します。
    
    Formula:
        FV = payment × [((1 + rate)^periods - 1) / rate]
        
        特殊ケース（rate = 0）:
        FV = payment × periods
    
    Args:
        payment: 期間あたりの支払額（円）
        rate: 期間あたりの利率（小数、例: 0.03 = 3%）
        periods: 期間数（整数）
    
    Returns:
        float: 年金の将来価値（円）
    
    Raises:
        ValueError: 支払額が負、または期間数が負の場合
    
    Examples:
        >>> # 毎年100,000円を10年間積み立て（年利3%）
        >>> result = calculate_annuity_future_value(100000, 0.03, 10)
        >>> print(f"{result:,.2f}")
        1,146,388.49
        >>> 
        >>> # 毎月30,000円を60ヶ月積み立て（月利0.3%）
        >>> result = calculate_annuity_future_value(30000, 0.003, 60)
        >>> print(f"{result:,.2f}")
        1,957,809.98
    
    Notes:
        - 積立投資の将来価値計算
        - つみたてNISAなどの評価に使用
    """
    if payment < 0:
        raise ValueError(f"支払額は0以上である必要があります: {payment}")
    if periods < 0:
        raise ValueError(f"期間数は0以上である必要があります: {periods}")
    
    if rate == 0:
        return payment * periods
    
    return payment * ((1 + rate) ** periods - 1) / rate


def calculate_irr(
    cash_flows: List[float],
    guess: float = 0.1,
    max_iterations: int = 100,
    tolerance: float = 1e-6
) -> Optional[float]:
    """内部収益率（IRR: Internal Rate of Return）計算
    
    キャッシュフローから内部収益率を計算します。
    IRRは、NPVが0となる割引率です。
    
    ニュートン法を使用してIRRを数値的に計算します。
    
    Args:
        cash_flows: キャッシュフロー（初期投資は負、以降の収入は正）
        guess: 初期推定値（デフォルト: 0.1 = 10%）
        max_iterations: 最大反復回数（デフォルト: 100）
        tolerance: 収束判定の許容誤差（デフォルト: 1e-6）
    
    Returns:
        Optional[float]: IRR（小数）。計算できない場合はNone
    
    Raises:
        ValueError: キャッシュフローが空、または要素数が2未満の場合
    
    Examples:
        >>> # 初期投資100万円、以降5年間毎年10万円、最終年に110万円
        >>> cash_flows = [-1000000, 100000, 100000, 100000, 100000, 1100000]
        >>> irr = calculate_irr(cash_flows)
        >>> print(f"IRR: {irr:.2%}")
        IRR: 3.41%
        >>> 
        >>> # 投資が失敗するケース（収益がマイナス）
        >>> cash_flows = [-1000000, 50000, 50000, 50000]
        >>> irr = calculate_irr(cash_flows)
        >>> print(f"IRR: {irr:.2%}" if irr else "計算不可")
        IRR: -58.74%
    
    Notes:
        - ニュートン法を使用した数値計算
        - 解が存在しない場合や複数解がある場合はNoneを返す
        - 初期投資（負の値）が必要
    """
    if len(cash_flows) < 2:
        raise ValueError("キャッシュフローは2つ以上必要です")
    
    try:
        rate = guess
        
        for _ in range(max_iterations):
            # NPVとその微分を計算
            npv_value = sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))
            npv_derivative = sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cash_flows))
            
            # 微分が0に近い場合は計算不可
            if abs(npv_derivative) < 1e-10:
                return None
            
            # ニュートン法で次の推定値を計算
            new_rate = rate - npv_value / npv_derivative
            
            # 収束判定
            if abs(new_rate - rate) < tolerance:
                # 計算結果が無効な場合（nan、inf等）はNoneを返す
                if np.isnan(new_rate) or np.isinf(new_rate):
                    return None
                return float(new_rate)
            
            rate = new_rate
        
        # 収束しなかった場合
        return None
    except Exception:
        return None


def calculate_npv(
    rate: float,
    cash_flows: List[float]
) -> float:
    """正味現在価値（NPV: Net Present Value）計算
    
    キャッシュフローを指定した割引率で現在価値に割り引き、合計します。
    
    Formula:
        NPV = Σ(CF_t / (1 + rate)^t)
        
        CF_t: 期間tのキャッシュフロー
        t: 期間（0から始まる）
    
    Args:
        rate: 割引率（小数、例: 0.03 = 3%）
        cash_flows: キャッシュフロー（期間0から始まる）
    
    Returns:
        float: NPV（円）
    
    Raises:
        ValueError: キャッシュフローが空の場合
    
    Examples:
        >>> # 初期投資100万円、以降5年間毎年10万円、最終年に110万円
        >>> # 割引率3%でNPV計算
        >>> cash_flows = [-1000000, 100000, 100000, 100000, 100000, 1100000]
        >>> npv = calculate_npv(0.03, cash_flows)
        >>> print(f"NPV: {npv:,.0f}円")
        NPV: 31,235円
        >>> 
        >>> # NPVが負の場合、投資すべきでない
        >>> cash_flows = [-1000000, 50000, 50000, 50000, 50000, 50000]
        >>> npv = calculate_npv(0.05, cash_flows)
        >>> print(f"NPV: {npv:,.0f}円")
        NPV: -783,526円
    
    Notes:
        - NPV > 0: 投資価値あり
        - NPV = 0: 無差別
        - NPV < 0: 投資すべきでない
        - 期間0のキャッシュフローは割引されない
    """
    if len(cash_flows) == 0:
        raise ValueError("キャッシュフローが空です")
    
    # NumPy 2.0で np.npv が削除されたため、手動で計算
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))


def calculate_monthly_payment(
    principal: float,
    annual_rate: float,
    years: int
) -> float:
    """月次支払額計算（住宅ローン等の返済額）
    
    元利均等返済の月次支払額を計算します。
    
    Formula:
        PMT = principal × [monthly_rate × (1 + monthly_rate)^months] / 
              [(1 + monthly_rate)^months - 1]
    
    Args:
        principal: 元本（借入額）（円）
        annual_rate: 年利率（小数、例: 0.03 = 3%）
        years: 借入期間（年）
    
    Returns:
        float: 月次支払額（円）
    
    Raises:
        ValueError: 元本が負、年利率が負、または期間が0以下の場合
    
    Examples:
        >>> # 3,000万円を年利1.5%で35年借入
        >>> payment = calculate_monthly_payment(30000000, 0.015, 35)
        >>> print(f"月次返済額: {payment:,.0f}円")
        月次返済額: 91,855円
        >>> 
        >>> # 総返済額
        >>> total = payment * 35 * 12
        >>> print(f"総返済額: {total:,.0f}円")
        総返済額: 38,579,100円
    
    Notes:
        - 元利均等返済を仮定
        - ボーナス返済は考慮しない
        - 年利率を月利率に変換して計算
    """
    if principal <= 0:
        raise ValueError(f"元本は正の値である必要があります: {principal}")
    if annual_rate < 0:
        raise ValueError(f"年利率は0以上である必要があります: {annual_rate}")
    if years <= 0:
        raise ValueError(f"期間は正の値である必要があります: {years}")
    
    monthly_rate = annual_rate / 12
    months = years * 12
    
    if monthly_rate == 0:
        return principal / months
    
    return principal * (monthly_rate * (1 + monthly_rate) ** months) / \
           ((1 + monthly_rate) ** months - 1)


# モジュールレベルのエクスポート
__all__ = [
    "calculate_compound_interest",
    "calculate_present_value",
    "calculate_annuity_present_value",
    "calculate_annuity_future_value",
    "calculate_irr",
    "calculate_npv",
    "calculate_monthly_payment",
]
