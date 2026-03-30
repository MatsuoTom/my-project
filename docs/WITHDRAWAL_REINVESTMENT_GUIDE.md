# 部分解約と再投資ガイド

> このファイルの目的: life_insurance の部分解約戦略で、解約金がどのように再投資されるかを現行実装ベースで説明する。

最終更新: 2026年03月30日  
位置づけ: 現行機能ガイド  
実行コマンドの正本: [README.md](README.md)

## 概要

life_insurance の部分解約戦略は、保険残高の一部を一定間隔で解約し、その手取り資金を再投資または現金保有として扱うシミュレーションです。

現行の中心ロジックは [life_insurance/analysis/insurance_calculator.py](life_insurance/analysis/insurance_calculator.py) の `calculate_partial_withdrawal_value()` にあります。

## いまの計算モデル

現行実装では、次の流れで月次シミュレーションを行います。

1. 毎月の保険料を積み立てる
2. 保険残高に運用利回りを反映する
3. 残高手数料を差し引く
4. 再投資残高があれば月次複利で増減させる
5. 指定年に達したら部分解約を行う
6. 解約手数料と一時所得ベースの解約課税を差し引く
7. 手取り額を再投資残高へ加える
8. 期間終了時に残りの保険を最終解約し、必要なら再投資課税も反映する

### 主な入力パラメータ

- `withdrawal_interval`: 何年ごとに部分解約するか
- `withdrawal_ratio`: 1 回あたりに残高の何割を解約するか
- `withdrawal_fee_rate`: 解約時手数料率
- `taxable_income`: 一時所得計算に使う課税所得
- `reinvestment_plan`: 再投資先の条件

### 主な出力

- `insurance_value`: 最終的な保険側の手取り額
- `reinvestment_value`: 再投資側の手取り額
- `withdrawal_tax`: 部分解約と最終解約で発生した税額
- `reinvestment_tax`: 再投資側の課税額
- `net_value`: 保険と再投資を合算した最終手取り額
- `tax_benefit`: 生命保険料控除による節税効果

## UI で選べる再投資先

現行 UI では [life_insurance/ui/streamlit_app.py](life_insurance/ui/streamlit_app.py) の部分解約戦略画面から、次の選択肢を使います。

- `投資信託`
- `現金保有`
- `混合（50%-50%）`
- `NISA枠活用`

実装上の扱いは次の通りです。

- `現金保有`: 再投資利回りを 0 として扱う
- `投資信託`: 再投資利回りを固定値で与える
- `混合（50%-50%）`: 中間的な固定値で与える
- `NISA枠活用`: 再投資自体は行うが、再投資課税を非課税扱いにする

補足:

- 現行 UI の再投資先は説明用のプリセットです
- 任意利回りの細かい指定はコア関数では可能ですが、UI では固定プリセットを内部変換して使っています
- 古い文書にあった `預金 1% / 投資信託 3% / 5%` という整理は、現行 UI の選択肢とは一致しません

## NISA の扱い

[life_insurance/models/fund_plan.py](life_insurance/models/fund_plan.py) の `use_nisa` が `True` の場合、再投資側の最終課税を 0 として扱います。

現行テストでも次を確認しています。

- [life_insurance/tests/test_insurance_calculator_core.py](life_insurance/tests/test_insurance_calculator_core.py): NISA 利用時は `reinvestment_tax == 0.0`
- [life_insurance/tests/test_insurance_calculator_core.py](life_insurance/tests/test_insurance_calculator_core.py): 非課税でない場合より `net_value` が大きくなる

## 現行 UI の操作導線

1. [life_insurance/ui/streamlit_app.py](life_insurance/ui/streamlit_app.py) の統合アプリを開く
2. 部分解約戦略セクションへ移動する
3. `解約間隔（年）` を選ぶ
4. `1回あたりの解約割合` を設定する
5. `解約金の再投資先` を選ぶ
6. `解約手数料率` と `課税所得` を入力する
7. `部分解約戦略を計算` を実行する

画面上では、解約スケジュール、残存割合、累積解約割合、試算結果を確認できます。

## 実装上の注意点

- [life_insurance/models/insurance_plan.py](life_insurance/models/insurance_plan.py) では `withdrawal_fee_rate` の初期値が 1% です
- [life_insurance/analysis/insurance_calculator.py](life_insurance/analysis/insurance_calculator.py) では最終解約時にも課税計算を行います
- 再投資課税は現行実装では推定利益率ベースの簡略モデルです
- `reinvestment_plan=None` の場合は、再投資なしの現金保有として扱われます

## テスト観点

部分解約と再投資の主要な保証は次のテストで見ます。

- [life_insurance/tests/test_insurance_calculator_core.py](life_insurance/tests/test_insurance_calculator_core.py): 基本的な部分解約計算
- [life_insurance/tests/test_insurance_calculator_core.py](life_insurance/tests/test_insurance_calculator_core.py): NISA 再投資の非課税差分
- [life_insurance/tests/test_insurance_calculator_core.py](life_insurance/tests/test_insurance_calculator_core.py): 再投資なしケース
- [life_insurance/tests/test_models.py](life_insurance/tests/test_models.py): `FundPlan` と `InsurancePlan` の妥当性

## 関連ドキュメント

- [docs/LIFE_INSURANCE_STRUCTURE.md](docs/LIFE_INSURANCE_STRUCTURE.md): 生命保険モジュール全体構成
- [docs/INDEX.md](docs/INDEX.md): docs の入口
- [docs/FEATURE_COMPARISON.md](docs/FEATURE_COMPARISON.md): 残る比較系ドキュメント
