# 生命保険モジュール構成

> このファイルの目的: life_insurance パッケージの現行構成と責務分担を把握するための参照を提供する。

最終更新: 2026年03月30日  
位置づけ: 現行構成の説明書  
実行コマンドの正本: [README.md](README.md)

## 概要

life_insurance は、旧生命保険料控除を前提にした計算ロジック、比較分析、Streamlit UI をまとめた独立ドメインです。

- core: 控除額と税額の基礎計算
- analysis: 保険価値試算、解約・乗り換え・シナリオ分析
- models: 入出力データの dataclass 群
- ui: Streamlit 画面
- utils: UI から使う補助計算
- tests: モジュール単位の pytest

## 現行ディレクトリ構成

```text
life_insurance/
├── __init__.py
├── config.py
├── analysis/
│   ├── __init__.py
│   ├── insurance_calculator.py
│   ├── scenario_analyzer.py
│   └── withdrawal_optimizer.py
├── core/
│   ├── __init__.py
│   ├── deduction_calculator.py
│   └── tax_calculator.py
├── models/
│   ├── __init__.py
│   ├── calculation_result.py
│   ├── fund_plan.py
│   └── insurance_plan.py
├── tests/
│   ├── __init__.py
│   ├── test_deduction.py
│   ├── test_insurance_calculator_core.py
│   ├── test_models.py
│   ├── test_optimizer.py
│   ├── test_scenario_analyzer.py
│   ├── test_tax.py
│   └── test_tax_helpers.py
├── ui/
│   ├── __init__.py
│   ├── comparison_app.py
│   └── streamlit_app.py
└── utils/
    ├── __init__.py
    └── tax_helpers.py
```

## 役割分担

### パッケージ公開面

- [life_insurance/__init__.py](life_insurance/__init__.py): LifeInsuranceDeductionCalculator、TaxCalculator、WithdrawalOptimizer、ScenarioAnalyzer を外部公開
- [life_insurance/config.py](life_insurance/config.py): 税率テーブル、控除上限、利回り、UI 表示用定数を集約

### 基礎計算

- [life_insurance/core/deduction_calculator.py](life_insurance/core/deduction_calculator.py): 旧制度の控除額計算、複数契約集約、保険料配分最適化
- [life_insurance/core/tax_calculator.py](life_insurance/core/tax_calculator.py): 所得税率判定、所得税計算、控除による節税額試算

### 高度分析

- [life_insurance/analysis/insurance_calculator.py](life_insurance/analysis/insurance_calculator.py): 保険継続、部分解約、乗り換え、投資比較の中核計算
- [life_insurance/analysis/withdrawal_optimizer.py](life_insurance/analysis/withdrawal_optimizer.py): 解約タイミングや複数戦略の比較ロジック
- [life_insurance/analysis/scenario_analyzer.py](life_insurance/analysis/scenario_analyzer.py): 感度分析、シナリオ比較、モンテカルロ分析

### データモデル

- [life_insurance/models/insurance_plan.py](life_insurance/models/insurance_plan.py): 保険条件の入力モデル
- [life_insurance/models/fund_plan.py](life_insurance/models/fund_plan.py): 比較対象ファンドの入力モデル
- [life_insurance/models/calculation_result.py](life_insurance/models/calculation_result.py): 保険計算・乗り換え・比較結果の出力モデル

### UI

- [life_insurance/ui/streamlit_app.py](life_insurance/ui/streamlit_app.py): 生命保険分析の統合 UI
- [life_insurance/ui/comparison_app.py](life_insurance/ui/comparison_app.py): 保険と投資信託の比較に特化した UI

### 補助ロジック

- [life_insurance/utils/tax_helpers.py](life_insurance/utils/tax_helpers.py): UI から使う税額・節税計算の薄いヘルパー層

## 実装上の見方

- UI 変更時は、まず core / analysis / models に既存ロジックがあるか確認する
- 新しい入力パラメータを増やす場合は models と tests を先に追従させる
- 税率やしきい値を変える場合は config を起点に確認する
- 実行手順はこの文書では重複記載せず、[README.md](README.md) を正本とする

## テスト対応

life_insurance 配下には専用の pytest 群があります。現時点で主要な観点は次の通りです。

- [life_insurance/tests/test_deduction.py](life_insurance/tests/test_deduction.py): 控除額テーブル、境界値、複数契約、配分最適化
- [life_insurance/tests/test_tax.py](life_insurance/tests/test_tax.py): 所得税計算と節税額
- [life_insurance/tests/test_insurance_calculator_core.py](life_insurance/tests/test_insurance_calculator_core.py): 保険試算、部分解約、乗り換え、比較、損益分岐
- [life_insurance/tests/test_models.py](life_insurance/tests/test_models.py): dataclass の妥当性と変換
- [life_insurance/tests/test_optimizer.py](life_insurance/tests/test_optimizer.py): 解約戦略の分析
- [life_insurance/tests/test_scenario_analyzer.py](life_insurance/tests/test_scenario_analyzer.py): シナリオ分析
- [life_insurance/tests/test_tax_helpers.py](life_insurance/tests/test_tax_helpers.py): UI 補助ヘルパー

## 関連ドキュメント

- [docs/INDEX.md](docs/INDEX.md): docs の入口
- [docs/PROGRESS.md](docs/PROGRESS.md): 現行進捗
- [docs/WITHDRAWAL_REINVESTMENT_GUIDE.md](docs/WITHDRAWAL_REINVESTMENT_GUIDE.md): 解約再投資の機能ガイド
- [docs/FEATURE_COMPARISON.md](docs/FEATURE_COMPARISON.md): 他機能との比較メモ
