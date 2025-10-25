# 金融分析ツール統合プロジェクト# 金融分析ツール統合プロジェクト



このプロジェクトは生命保険分析と年金シミュレーションの2つの金融分析ツールを統合したものです。特に年金シミュレーターは高度な損益分岐・最適化分析機能を搭載し、データ編集・永続化機能も完備しています。このプロジェクトは生命保険分析と年金シミュレーションの2つの金融分析ツールを統合したものです。



## 🚀 新機能ハイライト## 🏗️ プロジェクト構造



- **📊 高度な損益分岐・最適化分析**: キャリアモデル連携による詳細計算```

- **🎯 キャリアモデル選択**: デフォルト・拡張モデルを選択可能my-project/

- **💾 データ編集・永続化**: CSV保存・読込・Excel取込・リアルタイム編集├── life_insurance/              # 生命保険分析プロジェクト

- **📈 インタラクティブなタブUI**: 一覧性の高いタブベース設計│   ├── core/                    # コア計算機能

- **🔧 統合ランチャー**: 両アプリを統一的に起動│   │   ├── tax_calculator.py    # 税額計算

│   │   └── deduction_calculator.py # 控除計算

## 🏗️ プロジェクト構造│   ├── analysis/                # 分析ロジック

│   │   ├── scenario_analyzer.py # シナリオ分析

```│   │   └── withdrawal_optimizer.py # 引き出し最適化

my-project/│   ├── ui/                      # ユーザーインターフェース

├── .github/                     # プロジェクト設定・指示書│   │   ├── streamlit_app.py     # メインアプリ

├── life_insurance/              # 生命保険分析プロジェクト│   │   └── comparison_app.py    # 比較分析

│   ├── core/                    # コア計算機能│   └── tests/                   # テスト

│   │   ├── tax_calculator.py    # 税額計算├── pension_calc/                # 年金シミュレーションプロジェクト

│   │   └── deduction_calculator.py # 控除計算│   ├── core/                    # コア計算機能

│   ├── analysis/                # 分析ロジック│   │   └── pension_utils.py     # 年金計算ユーティリティ

│   │   ├── scenario_analyzer.py # シナリオ分析│   ├── analysis/                # 分析ロジック

│   │   └── withdrawal_optimizer.py # 引き出し最適化│   │   └── national_pension.py  # 国民年金分析

│   ├── ui/                      # ユーザーインターフェース│   ├── ui/                      # ユーザーインターフェース

│   │   ├── streamlit_app.py     # メインアプリ│   │   └── streamlit_app.py     # 年金分析アプリ

│   │   └── comparison_app.py    # 比較分析│   └── data/                    # データファイル

│   └── tests/                   # テスト├── tests/                       # 統合テスト

├── pension_calc/                # 年金シミュレーションプロジェクト（高度版）├── main.py                      # 統合ランチャー

│   ├── core/                    # コア計算機能├── pyproject.toml              # 依存関係管理

│   │   └── pension_utils.py     # 年金計算・データ永続化・キャリアモデル└── README.md                   # このファイル

│   ├── analysis/                # 分析ロジック```

│   │   └── national_pension.py  # 国民年金分析

│   ├── ui/                      # ユーザーインターフェース## 🚀 クイックスタート

│   │   └── streamlit_app.py     # 年金分析アプリ（タブベース・高機能版）

│   └── data/                    # データファイル・CSV保存先### 統合ランチャーを使用（推奨）

├── scripts/                     # 起動スクリプト

│   ├── run_life_insurance_app.py # 生命保険アプリ起動```bash

│   └── run_pension_app.py       # 年金アプリ起動（ポート自動調整）python main.py

├── tests/                       # 統合テスト```

├── main.py                      # 統合ランチャー

├── pyproject.toml              # 依存関係管理メニューからプロジェクトを選択して起動できます。

├── FEATURE_COMPARISON.md       # 機能比較ドキュメント

└── README.md                   # このファイル### 個別起動

```

#### 生命保険分析ツール

## 🚀 クイックスタート```bash

python scripts/run_life_insurance_app.py

### 統合ランチャーを使用（推奨）# または

streamlit run life_insurance/ui/streamlit_app.py --server.port=8507

```bash```

python main.py

```#### 年金シミュレーションツール

```bash

メニューからプロジェクトを選択して起動できます。python scripts/run_pension_app.py

# または

### 個別起動streamlit run pension_calc/ui/streamlit_app.py --server.port=8508

```

#### 生命保険分析ツール

```bash## 📊 機能概要

python scripts/run_life_insurance_app.py

# または### 生命保険分析ツール

streamlit run life_insurance/ui/streamlit_app.py --server.port=8507- **生命保険料控除分析**: 各種控除額の計算と最適化

```- **投資信託比較**: 生命保険と投資信託の収益性比較

- **引き出しタイミング最適化**: 部分解約戦略の自動提案

#### 年金シミュレーションツール（高度版）- **詳細シミュレーション**: 手数料、税金を考慮した実損益計算

```bash

python scripts/run_pension_app.py### 年金シミュレーションツール

# または- **年金試算**: 将来の年金受給額計算

streamlit run pension_calc/ui/streamlit_app.py --server.port=8508- **納付実績分析**: 過去の納付状況の可視化

```- **損益分析**: 納付額と受給額の比較

- **将来予測**: ライフプラン別の年金シミュレーション

## 📊 機能概要

## 🛠️ 開発環境セットアップ

### 生命保険分析ツール

- **生命保険料控除分析**: 各種控除額の計算と最適化### 必要な環境

- **投資信託比較**: 生命保険と投資信託の収益性比較- Python 3.12以上

- **引き出しタイミング最適化**: 部分解約戦略の自動提案- 推奨IDE: VS Code

- **詳細シミュレーション**: 手数料、税金を考慮した実損益計算

### 依存パッケージのインストール

### 年金シミュレーションツール（高度版）

```bash

#### コア機能# 基本パッケージ

- **🏠 ホーム**: 基本情報とキャリアモデル説明pip install streamlit pandas plotly numpy matplotlib seaborn

- **💰 支払実績**: インタラクティブなデータ編集・CSV保存・Excel取込

- **🎯 受給額試算**: 繰上げ・繰下げ受給を考慮した詳細試算# 追加パッケージ

- **🔮 将来予測**: 年収推移・保険料予測の可視化pip install openpyxl yfinance

- **📊 損益分岐・最適化**: 高度な分析機能（詳細版）

- **📋 計算方法**: 詳細な計算ロジックの説明# または pyproject.toml から一括インストール

pip install -r requirements.txt

#### 高度機能```

- **キャリアモデル選択**: 

  - `default`: 標準的な企業キャリア（30-60歳、8段階）### 仮想環境の使用（推奨）

  - `expanded`: 詳細なキャリアパス（25-60歳、11段階）

- **損益分岐・最適化分析**: ```bash

  - キャリアモデル連携による詳細納付額計算# 仮想環境作成

  - 厚生年金料率18.3%を考慮python -m venv venv

  - 最適受給開始年齢の自動算出

  - 投資回収率・生涯総受給額の比較# 仮想環境の有効化

- **データ永続化**: # Windows PowerShell

  - CSV形式での保存・読込.\venv\Scripts\Activate.ps1

  - Excel（.xlsx/.xls）ファイルの取込

  - リアルタイム編集機能# 依存関係インストール

  - データダウンロードpip install streamlit pandas plotly numpy matplotlib seaborn openpyxl yfinance

```

## 🛠️ 開発環境セットアップ

## 💡 使用方法

### 必要な環境

- Python 3.12以上### 1. 統合ランチャーから起動

- 推奨IDE: VS Code

```bash

### 依存パッケージのインストールpython main.py

```

```bash

# 基本パッケージ対話型メニューから使いたいツールを選択します。

pip install streamlit pandas plotly numpy matplotlib seaborn

### 2. 個別プロジェクトの直接起動

# 追加パッケージ

pip install openpyxl yfinance各プロジェクトを個別に起動することも可能です：



# または pyproject.toml から一括インストール```bash

pip install -e .# 生命保険分析

```python scripts/run_life_insurance_app.py



### 仮想環境の使用（推奨）# 年金シミュレーション  

python scripts/run_pension_app.py

```bash```

# 仮想環境作成

python -m venv .venv### 3. ポート設定



# 仮想環境の有効化複数のStreamlitアプリを同時に起動する場合は、異なるポートを指定してください：

# Windows PowerShell

.\.venv\Scripts\Activate.ps1```bash

streamlit run life_insurance/ui/streamlit_app.py --server.port=8507

# 依存関係インストールstreamlit run pension_calc/ui/streamlit_app.py --server.port=8508

pip install streamlit pandas plotly numpy matplotlib seaborn openpyxl yfinance```

```

### 4. 比較アプリ（オプション）

## 💡 使用方法

```bash

### 1. 統合ランチャーから起動streamlit run life_insurance/ui/comparison_app.py --server.port=8510

```

```bash

python main.py## 🧪 テスト実行

```

```bash

対話型メニューから使いたいツールを選択します。# 全体テスト

python -m pytest tests/

### 2. 個別プロジェクトの直接起動

# 個別プロジェクトのテスト

各プロジェクトを個別に起動することも可能です：python -m pytest life_insurance/tests/

python -m pytest pension_calc/tests/

```bash```

# 生命保険分析

python scripts/run_life_insurance_app.py## 📈 主な計算機能



# 年金シミュレーション（ポート自動調整機能付き）### 生命保険分析

python scripts/run_pension_app.py --port 8510- 生命保険料控除額計算

```- 実質利回り計算

- 部分解約シミュレーション

### 3. 年金シミュレーターの詳細操作- 投資信託との比較分析



#### キャリアモデルの選択### 年金計算

1. サイドバーの「🎯 キャリアモデルを選択」で`default`または`expanded`を選択- 国民年金・厚生年金の受給額計算

2. ホームタブの「📈 キャリアモデルについて」で詳細を確認- 納付月数・金額の管理

- 将来受給額の予測

#### データの編集・保存- 損益分岐点分析

1. 「💰 支払実績」タブでデータを直接編集

2. 「💾 保存」ボタンでCSVに永続化## 🔧 カスタマイズ

3. 「📥 実績ファイルのインポート」でCSV/Excelファイルを取込

### 計算パラメーターの変更

#### 高度分析の活用各プロジェクトの設定ファイルで、税率や手数料率などのパラメーターを調整できます。

1. 「📊 損益分岐・最適化」タブで詳細分析

2. 損益分岐点・最適受給開始年齢・投資回収率を確認### UI のカスタマイズ

3. インタラクティブなグラフで推移を可視化Streamlitアプリのレイアウトや表示項目は、各 `streamlit_app.py` ファイルで変更可能です。



## 🧪 テスト実行## 📄 ライセンス



```bashこのプロジェクトは個人利用目的で作成されています。

# 全体テスト

python -m pytest tests/## 🤝 コントリビューション



# 個別プロジェクトのテスト改善提案やバグ報告は歓迎します。

python -m pytest life_insurance/tests/

python -m pytest pension_calc/tests/## 📞 サポート

```

質問や問題がある場合は、各プロジェクトのコードコメントや計算ロジックを参照してください。
## 📈 主な計算機能

### 生命保険分析
- 生命保険料控除額計算
- 実質利回り計算
- 部分解約シミュレーション
- 投資信託との比較分析

### 年金計算（高度版）
- **基礎年金・厚生年金の詳細計算**: 調整率・報酬比例部分を考慮
- **キャリアモデル連携**: 年齢・役職・年収に基づく将来納付額予測
- **損益分岐点分析**: 累計納付額と累計受給額の詳細推移
- **最適化分析**: 生涯総受給額を最大化する受給開始年齢の算出
- **データ永続化**: CSV形式での実績データ管理

## 🔧 カスタマイズ

### キャリアモデルの調整
`pension_calc/core/pension_utils.py`の`get_career_model()`関数で、年齢・役職・年収の設定を変更可能。

### 計算パラメーターの変更
各プロジェクトの設定ファイルで、税率や手数料率などのパラメーターを調整できます。

### UIのカスタマイズ
Streamlitアプリのレイアウトや表示項目は、各`streamlit_app.py`ファイルで変更可能です。

## 📊 技術仕様

### 年金シミュレーター（高度版）の特徴
- **タブベースUI**: 6つの専門タブによる機能分離
- **リアルタイム計算**: パラメーター変更時の即座な再計算
- **データ永続化**: pandas DataFrameのCSV保存・読込
- **キャリアモデル**: 企業キャリアパスの標準化されたデータセット
- **高精度計算**: 厚生年金料率18.3%、調整率0.4%/0.7%を正確に適用

### 対応データ形式
- **入力**: CSV、Excel（.xlsx/.xls）
- **出力**: CSV、インタラクティブグラフ（Plotly）
- **データ構造**: 年度・年齢・加入制度・お勤め先・加入月数・納付額・推定年収

## 📄 ライセンス

このプロジェクトは個人利用目的で作成されています。

## 🤝 コントリビューション

改善提案やバグ報告は歓迎します。`FEATURE_COMPARISON.md`に詳細な機能比較を記載しています。

## 📞 サポート

質問や問題がある場合は、以下を参照してください：
- 各プロジェクトのコードコメント
- `📋 計算方法`タブの詳細説明
- `🛠️ 開発者情報`サイドバーでのデバッグ情報

## 🗂️ 関連ドキュメント

- `FEATURE_COMPARISON.md`: 詳細な機能比較と統合状況
- `.github/copilot-instructions.md`: AI作業指示書（開発者向け）

## 📝 データ編集の使い方

1. アプリを起動（例: `python main.py` または `streamlit run ...`）
2. 「データ編集」タブまたは「月次データ管理」画面に移動
3. 編集テーブル（data_editor）が表示されます
4. 編集したいセル（銘柄・投資方法・証券会社・備考など）をクリックして直接修正
5. 編集後は「保存」ボタン（または「更新」ボタン）があればクリック
6. 変更内容は即座に反映され、グラフや分析も自動更新されます

- 一括登録の場合は、空欄以外の行のみまとめて登録されます
- 編集内容はCSVとしてエクスポート可能です