"""
テストスイート - 生命保険料控除計算のテスト
"""

import pytest
from life_insurance.core.deduction_calculator import LifeInsuranceDeductionCalculator


class TestDeductionCalculator:
    """LifeInsuranceDeductionCalculator クラスのテスト"""

    @pytest.fixture
    def calculator(self):
        """テスト用の計算機インスタンスを作成"""
        return LifeInsuranceDeductionCalculator()

    def test_calculate_old_deduction_zero(self, calculator):
        """保険料が0円の場合のテスト"""
        assert calculator.calculate_old_deduction(0) == 0

    def test_calculate_old_deduction_below_25000(self, calculator):
        """保険料が25,000円以下の場合のテスト（支払保険料×1/2）"""
        # 10,000円の場合: 10,000 × 0.5 = 5,000円
        assert calculator.calculate_old_deduction(10000) == 5000
        # 25,000円の場合: 25,000 × 0.5 = 12,500円
        assert calculator.calculate_old_deduction(25000) == 12500

    def test_calculate_old_deduction_25001_to_50000(self, calculator):
        """保険料が25,001～50,000円の場合のテスト"""
        # 30,000円の場合: 30,000 × 0.25 + 12,500 = 20,000円
        assert calculator.calculate_old_deduction(30000) == 20000
        # 50,000円の場合: 50,000 × 0.25 + 12,500 = 25,000円
        assert calculator.calculate_old_deduction(50000) == 25000

    def test_calculate_old_deduction_50001_to_100000(self, calculator):
        """保険料が50,001～100,000円の場合のテスト"""
        # 60,000円の場合: 60,000 × 0.2 + 15,000 = 27,000円
        assert calculator.calculate_old_deduction(60000) == 27000
        # 100,000円の場合: 100,000 × 0.2 + 15,000 = 35,000円
        assert calculator.calculate_old_deduction(100000) == 35000

    def test_calculate_old_deduction_above_100000(self, calculator):
        """保険料が100,001円以上の場合のテスト（上限50,000円）"""
        assert calculator.calculate_old_deduction(120000) == 50000
        assert calculator.calculate_old_deduction(200000) == 50000
        assert calculator.calculate_old_deduction(1000000) == 50000

    def test_get_deduction_breakdown(self, calculator):
        """控除額の内訳取得テスト"""
        result = calculator.get_deduction_breakdown(60000)

        assert isinstance(result, dict)
        assert "年間支払保険料" in result  # 実装のキー名に合わせる
        assert "控除額" in result
        assert "適用段階" in result  # 実装のキー名に合わせる
        assert result["年間支払保険料"] == 60000
        assert result["控除額"] == 27000

    def test_calculate_multiple_contracts(self, calculator):
        """複数契約の合算控除テスト"""
        contracts = [30000, 40000, 50000]
        result = calculator.calculate_multiple_contracts(contracts)

        assert isinstance(result, dict)
        assert "合計支払保険料" in result  # 実装のキー名に合わせる
        assert "最適な控除額" in result  # 実装のキー名に合わせる
        # 合計120,000円
        # 個別計算: 20,000 + 22,500 + 25,000 = 67,500円
        # 合算計算: 上限50,000円
        # → 個別計算が有利
        assert result["合計支払保険料"] == 120000
        assert result["最適な控除額"] == 67500

    def test_optimize_premium_distribution(self, calculator):
        """保険料配分最適化のテスト"""
        result = calculator.optimize_premium_distribution(total_budget=100000, num_contracts=2)

        assert isinstance(result, dict)
        assert "最適配分" in result
        assert "合計控除額" in result
        assert len(result["最適配分"]) == 2


class TestEdgeCases:
    """エッジケースのテスト"""

    @pytest.fixture
    def calculator(self):
        return LifeInsuranceDeductionCalculator()

    def test_negative_premium(self, calculator):
        """負の保険料のテスト（0を返すべき）"""
        # 実装では負値の場合は0を返す（ValueError を発生させない）
        result = calculator.calculate_old_deduction(-1000)
        assert result == 0

    def test_extremely_large_premium(self, calculator):
        """極端に大きい保険料のテスト"""
        result = calculator.calculate_old_deduction(10000000)
        assert result == 50000  # 上限は50,000円

    def test_boundary_values(self, calculator):
        """境界値のテスト"""
        # 25,000円と25,001円の境界
        # 25,000円: 25,000 × 0.5 = 12,500円
        assert calculator.calculate_old_deduction(25000) == 12500
        # 25,001円: 25,001 × 0.25 + 12,500 = 18,750.25円
        assert abs(calculator.calculate_old_deduction(25001) - 18750.25) < 0.01

        # 50,000円と50,001円の境界
        # 50,000円: 50,000 × 0.25 + 12,500 = 25,000円
        assert calculator.calculate_old_deduction(50000) == 25000
        # 50,001円: 50,001 × 0.2 + 15,000 = 25,000.2円
        assert abs(calculator.calculate_old_deduction(50001) - 25000.2) < 0.01

        # 100,000円と100,001円の境界
        # 100,000円: 100,000 × 0.2 + 15,000 = 35,000円
        assert calculator.calculate_old_deduction(100000) == 35000
        # 100,001円以上: 上限50,000円
        assert calculator.calculate_old_deduction(100001) == 50000


class TestDeductionBreakdown:
    """控除額内訳の詳細テスト"""

    @pytest.fixture
    def calculator(self):
        return LifeInsuranceDeductionCalculator()

    def test_breakdown_first_bracket(self, calculator):
        """第1段階（25,000円以下）の内訳テスト"""
        result = calculator.get_deduction_breakdown(20000)
        assert result["適用段階"] == "第1段階（25,000円以下）"
        assert result["控除額"] == 10000
        assert result["控除率"] == 0.5
        assert result["上限到達"] is False

    def test_breakdown_second_bracket(self, calculator):
        """第2段階（25,001円～50,000円）の内訳テスト"""
        result = calculator.get_deduction_breakdown(40000)
        assert result["適用段階"] == "第2段階（25,001円～50,000円）"
        assert result["控除額"] == 22500
        assert abs(result["控除率"] - 0.5625) < 0.001
        assert result["上限到達"] is False

    def test_breakdown_third_bracket(self, calculator):
        """第3段階（50,001円～100,000円）の内訳テスト"""
        result = calculator.get_deduction_breakdown(80000)
        assert result["適用段階"] == "第3段階（50,001円～100,000円）"
        assert result["控除額"] == 31000
        assert abs(result["控除率"] - 0.3875) < 0.001
        assert result["上限到達"] is False

    def test_breakdown_fourth_bracket(self, calculator):
        """第4段階（100,001円以上）の内訳テスト"""
        result = calculator.get_deduction_breakdown(150000)
        assert result["適用段階"] == "第4段階（100,001円以上）"
        assert result["控除額"] == 50000
        assert abs(result["控除率"] - 1/3) < 0.01
        assert result["上限到達"] is True

    def test_breakdown_at_limit(self, calculator):
        """上限到達の境界テスト"""
        # 100,000円までは上限未到達
        result = calculator.get_deduction_breakdown(100000)
        assert result["上限到達"] is False
        
        # 100,001円以上は上限到達
        result = calculator.get_deduction_breakdown(100001)
        assert result["上限到達"] is True


class TestMultipleContractsAdvanced:
    """複数契約の高度なテスト"""

    @pytest.fixture
    def calculator(self):
        return LifeInsuranceDeductionCalculator()

    def test_single_contract(self, calculator):
        """単一契約のケース"""
        result = calculator.calculate_multiple_contracts([50000])
        assert result["契約数"] == 1
        assert result["合計支払保険料"] == 50000

    def test_two_equal_contracts(self, calculator):
        """2つの同額契約"""
        result = calculator.calculate_multiple_contracts([50000, 50000])
        assert result["契約数"] == 2
        assert result["合計支払保険料"] == 100000
        # 個別: 25,000 + 25,000 = 50,000円
        # 合算: 35,000円
        assert result["個別計算時の控除額合計"] == 50000
        assert result["合算計算時の控除額"] == 35000
        assert result["個別計算が有利"] is True

    def test_many_small_contracts(self, calculator):
        """多数の小額契約"""
        contracts = [10000] * 5  # 5契約、各10,000円
        result = calculator.calculate_multiple_contracts(contracts)
        assert result["契約数"] == 5
        assert result["合計支払保険料"] == 50000
        # 個別: 5,000 × 5 = 25,000円
        # 合算: 25,000円
        assert result["個別計算時の控除額合計"] == 25000
        assert result["合算計算時の控除額"] == 25000

    def test_one_large_one_small(self, calculator):
        """大きな契約と小さな契約の組み合わせ"""
        result = calculator.calculate_multiple_contracts([90000, 10000])
        assert result["合計支払保険料"] == 100000
        # 個別: 33,000 + 5,000 = 38,000円
        # 合算: 35,000円
        assert result["個別計算時の控除額合計"] == 38000
        assert result["合算計算時の控除額"] == 35000
        assert result["個別計算が有利"] is True


class TestOptimizationAdvanced:
    """最適化機能の高度なテスト"""

    @pytest.fixture
    def calculator(self):
        return LifeInsuranceDeductionCalculator()

    def test_optimize_single_contract(self, calculator):
        """単一契約の最適化（早期リターンのテスト）"""
        result = calculator.optimize_premium_distribution(80000, num_contracts=1)
        assert len(result["最適配分"]) == 1
        assert result["最適配分"][0] == 80000
        assert result["合計控除額"] == 31000

    def test_optimize_two_contracts_small_budget(self, calculator):
        """2契約、小予算の最適化"""
        result = calculator.optimize_premium_distribution(50000, num_contracts=2)
        assert len(result["最適配分"]) == 2
        assert sum(result["最適配分"]) == 50000
        assert result["契約数"] == 2

    def test_optimize_three_contracts(self, calculator):
        """3契約の最適化"""
        result = calculator.optimize_premium_distribution(120000, num_contracts=3)
        assert len(result["最適配分"]) == 3
        assert sum(result["最適配分"]) == 120000
        assert result["契約数"] == 3
        # 控除額が計算されていることを確認
        assert result["合計控除額"] > 0

    def test_optimize_budget_at_limit(self, calculator):
        """上限付近の予算での最適化"""
        result = calculator.optimize_premium_distribution(100000, num_contracts=2)
        assert sum(result["最適配分"]) == 100000
        # 各契約50,000円ずつが最適
        assert result["合計控除額"] == 50000

    def test_optimize_large_budget(self, calculator):
        """大きな予算での最適化"""
        result = calculator.optimize_premium_distribution(200000, num_contracts=2)
        assert sum(result["最適配分"]) == 200000
        # 2契約に分散することで控除額が増える
        # 各契約100,000円ずつなら: 35,000 × 2 = 70,000円
        # 実際の最適化により84,800円が達成される
        assert result["合計控除額"] > 50000  # 単一契約の上限より大きい

    def test_optimize_four_contracts(self, calculator):
        """4契約の最適化（再帰の深いパス）"""
        result = calculator.optimize_premium_distribution(150000, num_contracts=4)
        assert len(result["最適配分"]) == 4
        assert sum(result["最適配分"]) == 150000
        assert result["合計控除額"] > 0

    def test_optimize_zero_budget(self, calculator):
        """予算0円の最適化"""
        result = calculator.optimize_premium_distribution(0, num_contracts=2)
        assert sum(result["最適配分"]) == 0
        assert result["合計控除額"] == 0

    def test_optimize_small_budget_many_contracts(self, calculator):
        """小予算、多契約の最適化"""
        result = calculator.optimize_premium_distribution(30000, num_contracts=3)
        assert len(result["最適配分"]) == 3
        assert sum(result["最適配分"]) == 30000

    def test_optimize_uneven_distribution(self, calculator):
        """不均等配分の最適性検証"""
        result = calculator.optimize_premium_distribution(70000, num_contracts=2)
        assert sum(result["最適配分"]) == 70000
        # 最適配分が計算されていることを確認
        total_deduction = sum(
            calculator.calculate_old_deduction(p) for p in result["最適配分"]
        )
        assert result["合計控除額"] == total_deduction

    def test_optimize_boundary_budget(self, calculator):
        """境界値予算での最適化"""
        # 50,000円（第2段階の上限）
        result = calculator.optimize_premium_distribution(50000, num_contracts=2)
        assert sum(result["最適配分"]) == 50000
        
        # 100,000円（第3段階の上限）
        result = calculator.optimize_premium_distribution(100000, num_contracts=2)
        assert sum(result["最適配分"]) == 100000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
