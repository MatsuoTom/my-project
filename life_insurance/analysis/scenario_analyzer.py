"""
シナリオ分析モジュール

複数の条件設定による総合的なシナリオ分析を提供します。
"""

from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from life_insurance.core.deduction_calculator import LifeInsuranceDeductionCalculator
from life_insurance.core.tax_calculator import TaxCalculator
from life_insurance.analysis.withdrawal_optimizer import WithdrawalOptimizer


class ScenarioAnalyzer:
    """シナリオ分析クラス"""

    def __init__(self):
        """コンストラクタ"""
        self.deduction_calc = LifeInsuranceDeductionCalculator()
        self.tax_calc = TaxCalculator()
        self.optimizer = WithdrawalOptimizer()

        # 日本語フォント設定
        plt.rcParams["font.family"] = ["Meiryo", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False

    def create_comprehensive_scenario(
        self, base_params: Dict[str, Any], variation_params: Dict[str, List[Any]]
    ) -> pd.DataFrame:
        """
        包括的なシナリオ分析を実行

        Args:
            base_params: 基本パラメータ
            variation_params: 変動パラメータ

        Returns:
            全シナリオの分析結果
        """
        results = []
        scenario_count = 0

        # パラメータの組み合わせを生成
        param_names = list(variation_params.keys())
        param_values = list(variation_params.values())

        # 全組み合わせを生成
        import itertools

        for combination in itertools.product(*param_values):
            scenario_count += 1
            params = base_params.copy()

            # パラメータを更新
            for i, param_name in enumerate(param_names):
                params[param_name] = combination[i]

            # シナリオ実行
            result = self._run_single_scenario(params)
            result["シナリオID"] = scenario_count

            # パラメータ情報を追加
            for param_name, value in zip(param_names, combination):
                result[f"パラメータ_{param_name}"] = value

            results.append(result)

        return pd.DataFrame(results)

    def _run_single_scenario(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        単一シナリオの実行

        Args:
            params: シナリオパラメータ

        Returns:
            シナリオ実行結果
        """
        annual_premium = params.get("annual_premium", 100000)
        taxable_income = params.get("taxable_income", 5000000)
        policy_start_year = params.get("policy_start_year", 2020)
        withdrawal_year = params.get("withdrawal_year", 2030)
        return_rate = params.get("return_rate", 0.02)

        # 基本的な利益計算
        result = self.optimizer.calculate_total_benefit(
            annual_premium, taxable_income, withdrawal_year, policy_start_year, return_rate
        )

        # 追加の分析指標
        policy_years = withdrawal_year - policy_start_year
        annual_net_benefit = result["純利益"] / policy_years if policy_years > 0 else 0

        return {
            "年間保険料": annual_premium,
            "課税所得": taxable_income,
            "保険期間": policy_years,
            "累計節税効果": result["累計節税効果"],
            "解約返戻金": result["解約返戻金"],
            "純利益": result["純利益"],
            "実質利回り": result["実質利回り"],
            "年間純利益": annual_net_benefit,
            "投資効率": (
                result["純利益"] / (annual_premium * policy_years)
                if (annual_premium * policy_years) > 0
                else 0
            ),
        }

    def analyze_sensitivity(
        self,
        base_scenario: Dict[str, Any],
        sensitivity_param: str,
        param_range: List[float],
        output_metrics: List[str] = None,
    ) -> pd.DataFrame:
        """
        感度分析を実行

        Args:
            base_scenario: 基本シナリオ
            sensitivity_param: 感度分析対象パラメータ
            param_range: パラメータの変動範囲
            output_metrics: 出力指標（Noneの場合はデフォルト）

        Returns:
            感度分析結果
        """
        if output_metrics is None:
            output_metrics = ["純利益", "実質利回り", "累計節税効果"]

        results = []

        for param_value in param_range:
            scenario = base_scenario.copy()
            scenario[sensitivity_param] = param_value

            result = self._run_single_scenario(scenario)
            result[sensitivity_param] = param_value

            # 必要な指標のみを抽出
            filtered_result = {sensitivity_param: param_value}
            for metric in output_metrics:
                if metric in result:
                    filtered_result[metric] = result[metric]

            results.append(filtered_result)

        return pd.DataFrame(results)

    def create_monte_carlo_simulation(
        self,
        base_scenario: Dict[str, Any],
        uncertainty_params: Dict[str, Tuple[float, float]],
        num_simulations: int = 1000,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        モンテカルロシミュレーション

        Args:
            base_scenario: 基本シナリオ
            uncertainty_params: 不確実性パラメータ (パラメータ名: (平均, 標準偏差))
            num_simulations: シミュレーション回数

        Returns:
            シミュレーション結果とサマリー統計
        """
        results = []
        np.random.seed(42)  # 再現性のため

        for sim in range(num_simulations):
            scenario = base_scenario.copy()

            # 不確実性パラメータをランダム生成
            for param_name, (mean, std) in uncertainty_params.items():
                if param_name == "return_rate":
                    # 運用利回りは正規分布、負の値を避ける
                    value = max(0, np.random.normal(mean, std))
                elif param_name == "taxable_income":
                    # 所得は対数正規分布
                    value = np.random.lognormal(np.log(mean), std / mean)
                else:
                    # その他は正規分布
                    value = np.random.normal(mean, std)

                scenario[param_name] = value

            # シナリオ実行
            result = self._run_single_scenario(scenario)
            result["シミュレーション回数"] = sim + 1

            # 生成されたパラメータ値も保存
            for param_name in uncertainty_params.keys():
                result[f"生成_{param_name}"] = scenario[param_name]

            results.append(result)

        df_results = pd.DataFrame(results)

        # サマリー統計の計算
        summary_stats = {}
        key_metrics = ["純利益", "実質利回り", "累計節税効果"]

        for metric in key_metrics:
            if metric in df_results.columns:
                summary_stats[metric] = {
                    "平均": df_results[metric].mean(),
                    "中央値": df_results[metric].median(),
                    "標準偏差": df_results[metric].std(),
                    "最小値": df_results[metric].min(),
                    "最大値": df_results[metric].max(),
                    "5%パーセンタイル": df_results[metric].quantile(0.05),
                    "95%パーセンタイル": df_results[metric].quantile(0.95),
                }

        return df_results, summary_stats

    def plot_scenario_comparison(
        self,
        scenario_results: pd.DataFrame,
        x_param: str,
        y_metrics: List[str],
        group_by: Optional[str] = None,
    ) -> plt.Figure:
        """
        シナリオ比較の可視化

        Args:
            scenario_results: シナリオ分析結果
            x_param: X軸パラメータ
            y_metrics: Y軸指標リスト
            group_by: グループ分けパラメータ

        Returns:
            matplotlib図オブジェクト
        """
        n_metrics = len(y_metrics)
        fig, axes = plt.subplots(n_metrics, 1, figsize=(12, 4 * n_metrics))

        if n_metrics == 1:
            axes = [axes]

        for i, metric in enumerate(y_metrics):
            ax = axes[i]

            if group_by and group_by in scenario_results.columns:
                # グループ別プロット
                for group_value in scenario_results[group_by].unique():
                    data = scenario_results[scenario_results[group_by] == group_value]
                    ax.plot(
                        data[x_param], data[metric], marker="o", label=f"{group_by}={group_value}"
                    )
                ax.legend()
            else:
                # 単純プロット
                ax.plot(
                    scenario_results[x_param], scenario_results[metric], marker="o", linewidth=2
                )

            ax.set_xlabel(x_param)
            ax.set_ylabel(metric)
            ax.set_title(f"{metric} vs {x_param}")
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def generate_recommendation_report(
        self, scenario_results: pd.DataFrame, monte_carlo_results: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        推奨レポートの生成

        Args:
            scenario_results: シナリオ分析結果
            monte_carlo_results: モンテカルロシミュレーション結果

        Returns:
            推奨レポート
        """
        # 最適シナリオの特定
        best_scenario = scenario_results.loc[scenario_results["純利益"].idxmax()]

        # リスク分析
        risk_metrics = {}
        if monte_carlo_results is not None:
            risk_metrics = {
                "純利益_負の確率": (monte_carlo_results["純利益"] < 0).mean(),
                "純利益_VaR_5%": monte_carlo_results["純利益"].quantile(0.05),
                "実質利回り_負の確率": (monte_carlo_results["実質利回り"] < 0).mean(),
            }

        # 感度が高いパラメータの特定
        sensitive_params = []
        correlation_threshold = 0.5

        for col in scenario_results.columns:
            if col.startswith("パラメータ_"):
                param_name = col.replace("パラメータ_", "")
                correlation = scenario_results[col].corr(scenario_results["純利益"])
                if abs(correlation) > correlation_threshold:
                    sensitive_params.append(
                        {
                            "パラメータ": param_name,
                            "相関係数": correlation,
                            "影響度": "高" if abs(correlation) > 0.7 else "中",
                        }
                    )

        return {
            "最適シナリオ": best_scenario.to_dict(),
            "リスク指標": risk_metrics,
            "感度の高いパラメータ": sensitive_params,
            "推奨アクション": self._generate_recommendations(
                best_scenario, risk_metrics, sensitive_params
            ),
        }

    def _generate_recommendations(
        self,
        best_scenario: pd.Series,
        risk_metrics: Dict[str, float],
        sensitive_params: List[Dict[str, Any]],
    ) -> List[str]:
        """
        推奨アクション生成
        """
        recommendations = []

        # 基本推奨
        if best_scenario["純利益"] > 0:
            recommendations.append(f"最適保険期間は{best_scenario['保険期間']:.0f}年です。")
            recommendations.append(f"期待純利益は{best_scenario['純利益']:,.0f}円です。")
        else:
            recommendations.append("現在の条件では生命保険料控除による利益が期待できません。")

        # リスクベース推奨
        if risk_metrics:
            if risk_metrics.get("純利益_負の確率", 0) > 0.2:
                recommendations.append(
                    "純利益が負になる確率が20%を超えています。リスク許容度を再検討してください。"
                )

            var_5 = risk_metrics.get("純利益_VaR_5%")
            if var_5 and var_5 < -100000:
                recommendations.append(
                    f"最悪ケース（5%確率）で{abs(var_5):,.0f}円の損失リスクがあります。"
                )

        # 感度ベース推奨
        for param in sensitive_params:
            if param["パラメータ"] == "return_rate":
                recommendations.append(
                    "運用利回りが結果に大きく影響します。保守的な想定を検討してください。"
                )
            elif param["パラメータ"] == "taxable_income":
                recommendations.append(
                    "所得水準の変動が大きく影響します。将来の所得見通しを慎重に検討してください。"
                )

        return recommendations


def main():
    """デモンストレーション用のメイン関数"""
    analyzer = ScenarioAnalyzer()

    print("=== シナリオ分析デモ ===")

    # 基本パラメータ設定
    base_params = {
        "annual_premium": 100000,
        "taxable_income": 5000000,
        "policy_start_year": 2020,
        "withdrawal_year": 2030,
        "return_rate": 0.02,
    }

    # 変動パラメータ設定
    variation_params = {
        "annual_premium": [50000, 100000, 150000],
        "taxable_income": [3000000, 5000000, 8000000],
        "return_rate": [0.01, 0.02, 0.03],
    }

    print("\n1. 包括的シナリオ分析:")
    scenario_results = analyzer.create_comprehensive_scenario(base_params, variation_params)

    # 上位5シナリオを表示
    top_scenarios = scenario_results.nlargest(5, "純利益")
    print("純利益上位5シナリオ:")
    print(
        top_scenarios[
            [
                "シナリオID",
                "パラメータ_annual_premium",
                "パラメータ_taxable_income",
                "パラメータ_return_rate",
                "純利益",
                "実質利回り",
            ]
        ].to_string(index=False)
    )

    print("\n2. 感度分析:")
    sensitivity_result = analyzer.analyze_sensitivity(
        base_params, "annual_premium", [50000, 75000, 100000, 125000, 150000]
    )
    print("年間保険料による感度分析:")
    print(sensitivity_result.to_string(index=False))

    print("\n3. 推奨レポート:")
    report = analyzer.generate_recommendation_report(scenario_results)
    print("推奨アクション:")
    for i, action in enumerate(report["推奨アクション"], 1):
        print(f"{i}. {action}")


if __name__ == "__main__":
    main()
