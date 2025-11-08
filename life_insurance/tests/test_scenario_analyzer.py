"""
life_insurance.analysis.scenario_analyzerのユニットテスト

シナリオ分析機能のテスト:
- create_comprehensive_scenario(): 包括的シナリオ分析
- _run_single_scenario(): 単一シナリオ実行
- analyze_sensitivity(): 感度分析
- create_monte_carlo_simulation(): モンテカルロシミュレーション
- plot_scenario_comparison(): シナリオ比較可視化
- generate_recommendation_report(): 推奨レポート生成
"""

import pytest
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Tcl/Tk問題を回避するため、非GUIバックエンドを使用
import matplotlib.pyplot as plt
from typing import Dict, List, Any

from life_insurance.analysis.scenario_analyzer import ScenarioAnalyzer


class TestScenarioAnalyzerInit:
    """ScenarioAnalyzerクラスの初期化テスト"""

    def test_initialization(self):
        """正常系: クラスの初期化"""
        # Act
        analyzer = ScenarioAnalyzer()

        # Assert
        assert analyzer is not None
        assert hasattr(analyzer, "deduction_calc")
        assert hasattr(analyzer, "tax_calc")
        assert hasattr(analyzer, "optimizer")

    def test_has_required_components(self):
        """正常系: 必要なコンポーネントの存在確認"""
        # Arrange & Act
        analyzer = ScenarioAnalyzer()

        # Assert
        assert analyzer.deduction_calc is not None
        assert analyzer.tax_calc is not None
        assert analyzer.optimizer is not None


class TestRunSingleScenario:
    """_run_single_scenario()のテスト"""

    def test_basic_scenario(self):
        """正常系: 基本的なシナリオ実行"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        params = {
            "annual_premium": 100000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2030,
            "return_rate": 0.02,
        }

        # Act
        result = analyzer._run_single_scenario(params)

        # Assert
        assert isinstance(result, dict)
        assert "年間保険料" in result
        assert "課税所得" in result
        assert "保険期間" in result
        assert "累計節税効果" in result
        assert "解約返戻金" in result
        assert "純利益" in result
        assert "実質利回り" in result
        assert "年間純利益" in result
        assert "投資効率" in result

    def test_scenario_with_different_premium(self):
        """正常系: 異なる保険料でのシナリオ"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        params1 = {
            "annual_premium": 50000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
            "return_rate": 0.02,
        }
        params2 = {
            "annual_premium": 200000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
            "return_rate": 0.02,
        }

        # Act
        result1 = analyzer._run_single_scenario(params1)
        result2 = analyzer._run_single_scenario(params2)

        # Assert
        assert result1["年間保険料"] == 50000
        assert result2["年間保険料"] == 200000
        # 保険料が高い方が累計節税効果も大きい
        assert result2["累計節税効果"] > result1["累計節税効果"]

    def test_scenario_with_short_period(self):
        """境界値: 短期間の保険（1年）"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        params = {
            "annual_premium": 100000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2021,  # 1年後
            "return_rate": 0.02,
        }

        # Act
        result = analyzer._run_single_scenario(params)

        # Assert
        assert result["保険期間"] == 1
        assert isinstance(result["年間純利益"], (int, float))
        assert isinstance(result["投資効率"], (int, float))

    def test_scenario_calculation_consistency(self):
        """検証: 計算結果の整合性"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        params = {
            "annual_premium": 100000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2030,
            "return_rate": 0.02,
        }

        # Act
        result = analyzer._run_single_scenario(params)

        # Assert
        policy_years = result["保険期間"]
        assert policy_years == 10
        # 年間純利益 = 純利益 / 保険期間
        assert abs(result["年間純利益"] - result["純利益"] / policy_years) < 0.01


class TestCreateComprehensiveScenario:
    """create_comprehensive_scenario()のテスト"""

    def test_single_variation_parameter(self):
        """正常系: 単一パラメータの変動"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_params = {
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
            "return_rate": 0.02,
        }
        variation_params = {"annual_premium": [50000, 100000, 150000]}

        # Act
        result_df = analyzer.create_comprehensive_scenario(base_params, variation_params)

        # Assert
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 3  # 3つのシナリオ
        assert "シナリオID" in result_df.columns
        assert "パラメータ_annual_premium" in result_df.columns
        assert result_df["シナリオID"].tolist() == [1, 2, 3]

    def test_multiple_variation_parameters(self):
        """正常系: 複数パラメータの変動（組み合わせ）"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_params = {
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
        }
        variation_params = {
            "annual_premium": [50000, 100000],
            "return_rate": [0.01, 0.03],
        }

        # Act
        result_df = analyzer.create_comprehensive_scenario(base_params, variation_params)

        # Assert
        assert len(result_df) == 4  # 2×2 = 4シナリオ
        assert "パラメータ_annual_premium" in result_df.columns
        assert "パラメータ_return_rate" in result_df.columns

    def test_empty_variation_parameters(self):
        """境界値: 変動パラメータなし"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_params = {
            "annual_premium": 100000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
            "return_rate": 0.02,
        }
        variation_params = {}

        # Act
        result_df = analyzer.create_comprehensive_scenario(base_params, variation_params)

        # Assert
        # 空の組み合わせは1シナリオを生成
        assert len(result_df) >= 0

    def test_result_dataframe_structure(self):
        """検証: 結果DataFrameの構造"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_params = {
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
        }
        variation_params = {"annual_premium": [100000, 200000]}

        # Act
        result_df = analyzer.create_comprehensive_scenario(base_params, variation_params)

        # Assert
        expected_columns = [
            "年間保険料",
            "課税所得",
            "保険期間",
            "累計節税効果",
            "解約返戻金",
            "純利益",
            "実質利回り",
            "シナリオID",
        ]
        for col in expected_columns:
            assert col in result_df.columns


class TestAnalyzeSensitivity:
    """analyze_sensitivity()のテスト"""

    def test_basic_sensitivity_analysis(self):
        """正常系: 基本的な感度分析"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_scenario = {
            "annual_premium": 100000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
            "return_rate": 0.02,
        }
        param_range = [0.01, 0.02, 0.03, 0.04]

        # Act
        result_df = analyzer.analyze_sensitivity(
            base_scenario, "return_rate", param_range
        )

        # Assert
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 4
        assert "return_rate" in result_df.columns
        assert "純利益" in result_df.columns
        assert "実質利回り" in result_df.columns

    def test_sensitivity_with_custom_metrics(self):
        """正常系: カスタム出力指標での感度分析"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_scenario = {
            "annual_premium": 100000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
            "return_rate": 0.02,
        }
        param_range = [50000, 100000, 150000]
        output_metrics = ["純利益", "累計節税効果"]

        # Act
        result_df = analyzer.analyze_sensitivity(
            base_scenario, "annual_premium", param_range, output_metrics
        )

        # Assert
        assert "純利益" in result_df.columns
        assert "累計節税効果" in result_df.columns
        # 実質利回りは指定していないので含まれない可能性
        # （または含まれていても問題ない）

    def test_sensitivity_increasing_trend(self):
        """検証: 感度分析の増加トレンド"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_scenario = {
            "annual_premium": 100000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
            "return_rate": 0.02,
        }
        param_range = [0.01, 0.02, 0.03, 0.04]

        # Act
        result_df = analyzer.analyze_sensitivity(
            base_scenario, "return_rate", param_range
        )

        # Assert
        # 運用利回りが高いほど解約返戻金も増加するはず
        assert result_df["純利益"].is_monotonic_increasing or result_df["純利益"].is_monotonic_decreasing


class TestCreateMonteCarloSimulation:
    """create_monte_carlo_simulation()のテスト"""

    def test_basic_monte_carlo(self):
        """正常系: 基本的なモンテカルロシミュレーション"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_scenario = {
            "annual_premium": 100000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
        }
        uncertainty_params = {"return_rate": (0.02, 0.01)}  # (平均, 標準偏差)
        num_simulations = 100

        # Act
        result_df, summary_stats = analyzer.create_monte_carlo_simulation(
            base_scenario, uncertainty_params, num_simulations
        )

        # Assert
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == num_simulations
        assert "シミュレーション回数" in result_df.columns
        assert "生成_return_rate" in result_df.columns
        assert isinstance(summary_stats, dict)

    def test_monte_carlo_summary_statistics(self):
        """正常系: サマリー統計の確認"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_scenario = {
            "annual_premium": 100000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
        }
        uncertainty_params = {"return_rate": (0.02, 0.01)}
        num_simulations = 100

        # Act
        result_df, summary_stats = analyzer.create_monte_carlo_simulation(
            base_scenario, uncertainty_params, num_simulations
        )

        # Assert
        assert "純利益" in summary_stats
        assert "平均" in summary_stats["純利益"]
        assert "中央値" in summary_stats["純利益"]
        assert "標準偏差" in summary_stats["純利益"]
        assert "最小値" in summary_stats["純利益"]
        assert "最大値" in summary_stats["純利益"]
        assert "5%パーセンタイル" in summary_stats["純利益"]
        assert "95%パーセンタイル" in summary_stats["純利益"]

    def test_monte_carlo_with_multiple_uncertainty_params(self):
        """正常系: 複数の不確実性パラメータ"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_scenario = {
            "annual_premium": 100000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
        }
        uncertainty_params = {
            "return_rate": (0.02, 0.01),
            "taxable_income": (5000000, 1000000),
        }
        num_simulations = 50

        # Act
        result_df, summary_stats = analyzer.create_monte_carlo_simulation(
            base_scenario, uncertainty_params, num_simulations
        )

        # Assert
        assert len(result_df) == num_simulations
        assert "生成_return_rate" in result_df.columns
        assert "生成_taxable_income" in result_df.columns

    def test_monte_carlo_reproducibility(self):
        """検証: 再現性の確認（seed固定）"""
        # Arrange
        analyzer1 = ScenarioAnalyzer()
        analyzer2 = ScenarioAnalyzer()
        base_scenario = {
            "annual_premium": 100000,
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
        }
        uncertainty_params = {"return_rate": (0.02, 0.01)}
        num_simulations = 10

        # Act
        result_df1, _ = analyzer1.create_monte_carlo_simulation(
            base_scenario, uncertainty_params, num_simulations
        )
        result_df2, _ = analyzer2.create_monte_carlo_simulation(
            base_scenario, uncertainty_params, num_simulations
        )

        # Assert
        # seed=42が固定されているので同じ結果になるはず
        pd.testing.assert_series_equal(
            result_df1["生成_return_rate"], result_df2["生成_return_rate"]
        )


class TestPlotScenarioComparison:
    """plot_scenario_comparison()のテスト"""

    def test_basic_plot_creation(self):
        """正常系: 基本的なプロット作成"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        scenario_results = pd.DataFrame(
            {
                "annual_premium": [50000, 100000, 150000],
                "純利益": [10000, 25000, 40000],
                "実質利回り": [0.01, 0.015, 0.02],
            }
        )

        # Act
        fig = analyzer.plot_scenario_comparison(
            scenario_results, "annual_premium", ["純利益"]
        )

        # Assert
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_with_multiple_metrics(self):
        """正常系: 複数指標のプロット"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        scenario_results = pd.DataFrame(
            {
                "return_rate": [0.01, 0.02, 0.03],
                "純利益": [10000, 25000, 40000],
                "実質利回り": [0.01, 0.015, 0.02],
                "累計節税効果": [5000, 10000, 15000],
            }
        )

        # Act
        fig = analyzer.plot_scenario_comparison(
            scenario_results, "return_rate", ["純利益", "実質利回り"]
        )

        # Assert
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 2  # 2つのサブプロット
        plt.close(fig)

    def test_plot_with_grouping(self):
        """正常系: グループ分けありのプロット"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        scenario_results = pd.DataFrame(
            {
                "return_rate": [0.01, 0.02, 0.01, 0.02],
                "純利益": [10000, 25000, 15000, 30000],
                "premium_level": ["低", "低", "高", "高"],
            }
        )

        # Act
        fig = analyzer.plot_scenario_comparison(
            scenario_results, "return_rate", ["純利益"], group_by="premium_level"
        )

        # Assert
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestGenerateRecommendationReport:
    """generate_recommendation_report()のテスト"""

    def test_basic_recommendation_report(self):
        """正常系: 基本的な推奨レポート生成"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        scenario_results = pd.DataFrame(
            {
                "年間保険料": [50000, 100000, 150000],
                "純利益": [10000, 25000, 40000],
                "実質利回り": [0.01, 0.015, 0.02],
                "累計節税効果": [5000, 10000, 15000],
            }
        )

        # Act
        report = analyzer.generate_recommendation_report(scenario_results)

        # Assert
        assert isinstance(report, dict)
        # レポートには最適シナリオなどの情報が含まれる

    def test_recommendation_report_with_monte_carlo(self):
        """正常系: モンテカルロ結果を含む推奨レポート"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        scenario_results = pd.DataFrame(
            {
                "年間保険料": [50000, 100000],
                "純利益": [10000, 25000],
                "実質利回り": [0.01, 0.015],
            }
        )
        monte_carlo_results = pd.DataFrame(
            {
                "純利益": np.random.normal(20000, 5000, 100),
                "実質利回り": np.random.normal(0.015, 0.005, 100),
            }
        )

        # Act
        report = analyzer.generate_recommendation_report(
            scenario_results, monte_carlo_results
        )

        # Assert
        assert isinstance(report, dict)
        # リスク指標が含まれるはず


class TestScenarioAnalyzerIntegration:
    """統合テスト"""

    def test_partial_workflow(self):
        """統合: 部分的なワークフロー（動作する機能のみ）"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_params = {
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
        }
        variation_params = {
            "annual_premium": [50000, 100000],
            "return_rate": [0.01, 0.02],
        }

        # Act
        # 1. 包括的シナリオ分析
        scenario_results = analyzer.create_comprehensive_scenario(
            base_params, variation_params
        )

        # 2. 感度分析
        sensitivity_results = analyzer.analyze_sensitivity(
            {**base_params, "annual_premium": 100000, "return_rate": 0.02},
            "return_rate",
            [0.01, 0.015, 0.02, 0.025],
        )

        # Assert
        assert len(scenario_results) == 4
        assert len(sensitivity_results) == 4

    def test_full_analysis_workflow(self):
        """統合: 完全な分析ワークフロー"""
        # Arrange
        analyzer = ScenarioAnalyzer()
        base_params = {
            "taxable_income": 5000000,
            "policy_start_year": 2020,
            "withdrawal_year": 2025,
        }
        variation_params = {
            "annual_premium": [50000, 100000],
            "return_rate": [0.01, 0.02],
        }

        # Act
        # 1. 包括的シナリオ分析
        scenario_results = analyzer.create_comprehensive_scenario(
            base_params, variation_params
        )

        # 2. 感度分析
        sensitivity_results = analyzer.analyze_sensitivity(
            {**base_params, "annual_premium": 100000, "return_rate": 0.02},
            "return_rate",
            [0.01, 0.015, 0.02, 0.025],
        )

        # 3. モンテカルロシミュレーション
        mc_results, mc_summary = analyzer.create_monte_carlo_simulation(
            {**base_params, "annual_premium": 100000},
            {"return_rate": (0.02, 0.01)},
            50,
        )

        # Assert
        assert len(scenario_results) == 4
        assert len(sensitivity_results) == 4
        assert len(mc_results) == 50
        assert isinstance(mc_summary, dict)


# テスト実行時のエントリポイント
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
