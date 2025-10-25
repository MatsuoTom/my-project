"""
生命保険料控除分析システム

旧生命保険料控除制度（平成23年12月31日以前の契約）の節税効果と
最適な引き出しタイミングを分析する包括的なWebアプリケーションシステム。

主要機能:
- 旧生命保険料控除額の計算
- 所得税・住民税の節税効果算出
- 引き出しタイミングの最適化分析（116戦略の自動比較）
- 部分解約後の資金運用シミュレーション
- 複数シナリオの比較・感度分析
- インタラクティブなWebアプリケーション（Streamlit）
"""

__version__ = "2.0.0"
__author__ = "プロジェクト開発チーム"

from life_insurance.core.deduction_calculator import LifeInsuranceDeductionCalculator
from life_insurance.core.tax_calculator import TaxCalculator
from life_insurance.analysis.withdrawal_optimizer import WithdrawalOptimizer
from life_insurance.analysis.scenario_analyzer import ScenarioAnalyzer

__all__ = [
    "LifeInsuranceDeductionCalculator",
    "TaxCalculator",
    "WithdrawalOptimizer",
    "ScenarioAnalyzer",
]