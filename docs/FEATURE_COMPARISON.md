# 機能比較

> このファイルの目的: 現行リポジトリに含まれる主要ドメインの役割と比較軸を整理する。

最終更新: 2026年03月30日  
位置づけ: 現行比較メモ  
比較対象時点: 2026年03月30日時点の main ワークスペース

## 概要

このリポジトリは単一アプリではなく、複数の金融ドメインを横断する構成です。ここでは、現行の主要4ドメインを比較します。

- life_insurance: 生命保険料控除と解約・再投資分析
- pension_calc: 年金納付実績と受給見込み分析
- investment_simulation: NISA を中心とした投資シミュレーション
- vehicle_finance: 車両維持費の計画と実績管理

## ドメイン比較

| ドメイン | 主目的 | 主な UI | 主なデータ/モデル | テスト状況 |
|---|---|---|---|---|
| `life_insurance` | 生命保険控除、解約、再投資、比較分析 | Streamlit 統合 UI + 比較 UI | `InsurancePlan`, `FundPlan`, `InsuranceResult` | 専用 tests あり |
| `pension_calc` | 年金納付実績、受給額試算、損益分岐分析 | Streamlit UI | `pension_utils.py` の DataFrame と計算関数 | 主にルート tests から検証 |
| `investment_simulation` | NISA 投資の実績管理と将来分析 | Streamlit UI | brand master、月次データ、分析ロジック | 専用 tests あり |
| `vehicle_finance` | 車両維持費計画、保存データ管理、長期コスト把握 | Streamlit UI | `data/` 配下の計画データと core ロジック | 専用 tests あり |

## 構成上の違い

| 観点 | life_insurance | pension_calc | investment_simulation | vehicle_finance |
|---|---|---|---|---|
| コア計算の分離 | `core/`, `analysis/`, `models/` に分離 | `core/pension_utils.py` に集約が強い | `core/`, `analysis/`, `ui/` に分離 | `core/`, `ui/`, `data/` 中心 |
| UI の性質 | 比較・戦略分析が多い | 実績入力と受給額説明が中心 | 実績編集とブランド分析が中心 | 計画入力と保存データ運用が中心 |
| 永続化の比重 | 低め | CSV 編集・保存あり | 月次データ・ブランド管理あり | ローカル saved plans 運用あり |
| docs での補助資料 | 機能構成と再投資ガイドあり | README / docs / root tests 参照が中心 | 実行サマリー系が多い | README とローカル運用ルールが重要 |

## 利用シーン別の見分け方

| やりたいこと | 参照先 |
|---|---|
| 保険を続けるか、途中解約して再投資するか比べたい | [life_insurance/ui/streamlit_app.py](life_insurance/ui/streamlit_app.py) |
| 年金の支払実績から将来受給額を試算したい | [pension_calc/ui/streamlit_app.py](pension_calc/ui/streamlit_app.py) |
| 投資信託や NISA の実績を入力して分析したい | [investment_simulation/ui/streamlit_app.py](investment_simulation/ui/streamlit_app.py) |
| 車両の年間維持費を計画・保存したい | [vehicle_finance/ui/streamlit_app.py](vehicle_finance/ui/streamlit_app.py) |
| アプリを統合メニューから起動したい | [main.py](main.py) |

## 開発時の使い分け

- ドメイン固有の仕様を見るときは、それぞれのパッケージ配下を読む
- 共通の起動方法は [README.md](README.md) を見る
- 現行 docs の入口は [docs/INDEX.md](docs/INDEX.md) を使う
- 計画や過去の経緯は [REFACTORING/INDEX.md](REFACTORING/INDEX.md) を使う

## 補足

- 旧版の「復元フォルダとの比較」は履歴としての意味はありますが、現行 docs の比較文書としては役割が薄いため、このファイルは現行ワークスペース内比較に置き換えました
- 比較対象時点が変わった場合は、この文書の更新日と比較対象時点を先に更新する
