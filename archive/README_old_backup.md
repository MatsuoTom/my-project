# 金融分析ツール統合プロジェクト

このプロジェクトは生命保険分析と年金シミュレーションの2つの金融分析ツールを統合したものです。

## 🏗️ プロジェクト構造

```
my-project/
├── life_insurance/              # 生命保険分析プロジェクト
│   ├── core/                    # コア計算機能
│   │   ├── tax_calculator.py    # 税額計算
│   │   └── deduction_calculator.py # 控除計算
│   ├── analysis/                # 分析ロジック
│   │   ├── scenario_analyzer.py # シナリオ分析
│   │   └── withdrawal_optimizer.py # 引き出し最適化
│   ├── ui/                      # ユーザーインターフェース
│   │   ├── streamlit_app.py     # メインアプリ
│   │   └── comparison_app.py    # 比較分析
│   └── tests/                   # テスト
├── pension_calc/                # 年金シミュレーションプロジェクト
│   ├── core/                    # コア計算機能
│   │   └── pension_utils.py     # 年金計算ユーティリティ
│   ├── analysis/                # 分析ロジック
│   │   └── national_pension.py  # 国民年金分析
│   ├── ui/                      # ユーザーインターフェース
│   │   └── streamlit_app.py     # 年金分析アプリ
│   └── data/                    # データファイル
├── tests/                       # 統合テスト
├── main.py                      # 統合ランチャー
├── pyproject.toml              # 依存関係管理
└── README.md                   # このファイル
```

## 🚀 クイックスタート

### 統合ランチャーを使用（推奨）

```bash
python main.py
```

メニューからプロジェクトを選択して起動できます。

### 個別起動

#### 生命保険分析ツール
```bash
python scripts/run_life_insurance_app.py
# または
streamlit run life_insurance/ui/streamlit_app.py --server.port=8507
```

#### 年金シミュレーションツール
```bash
python scripts/run_pension_app.py
# または
streamlit run pension_calc/ui/streamlit_app.py --server.port=8508
```

## 📊 機能概要

### 生命保険分析ツール
- **生命保険料控除分析**: 各種控除額の計算と最適化
- **投資信託比較**: 生命保険と投資信託の収益性比較
- **引き出しタイミング最適化**: 部分解約戦略の自動提案
- **詳細シミュレーション**: 手数料、税金を考慮した実損益計算

### 年金シミュレーションツール
- **年金試算**: 将来の年金受給額計算
- **納付実績分析**: 過去の納付状況の可視化
- **損益分析**: 納付額と受給額の比較
- **将来予測**: ライフプラン別の年金シミュレーション

## 🛠️ 開発環境セットアップ

### 必要な環境
- Python 3.12以上
- 推奨IDE: VS Code

### 依存パッケージのインストール

```bash
# 基本パッケージ
pip install streamlit pandas plotly numpy matplotlib seaborn

# 追加パッケージ
pip install openpyxl yfinance

# または pyproject.toml から一括インストール
pip install -r requirements.txt
```

### 仮想環境の使用（推奨）

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境の有効化
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# 依存関係インストール
pip install streamlit pandas plotly numpy matplotlib seaborn openpyxl yfinance
```

## 💡 使用方法

### 1. 統合ランチャーから起動

```bash
python main.py
```

対話型メニューから使いたいツールを選択します。

### 2. 個別プロジェクトの直接起動

各プロジェクトを個別に起動することも可能です：

```bash
# 生命保険分析
python scripts/run_life_insurance_app.py

# 年金シミュレーション  
python scripts/run_pension_app.py
```

### 3. ポート設定

複数のStreamlitアプリを同時に起動する場合は、異なるポートを指定してください：

```bash
streamlit run life_insurance/ui/streamlit_app.py --server.port=8507
streamlit run pension_calc/ui/streamlit_app.py --server.port=8508
```

### 4. 比較アプリ（オプション）

```bash
streamlit run life_insurance/ui/comparison_app.py --server.port=8510
```

## 🧪 テスト実行

```bash
# 全体テスト
python -m pytest tests/

# 個別プロジェクトのテスト
python -m pytest life_insurance/tests/
python -m pytest pension_calc/tests/
```

## 📈 主な計算機能

### 生命保険分析
- 生命保険料控除額計算
- 実質利回り計算
- 部分解約シミュレーション
- 投資信託との比較分析

### 年金計算
- 国民年金・厚生年金の受給額計算
- 納付月数・金額の管理
- 将来受給額の予測
- 損益分岐点分析

## 🔧 カスタマイズ

### 計算パラメーターの変更
各プロジェクトの設定ファイルで、税率や手数料率などのパラメーターを調整できます。

### UI のカスタマイズ
Streamlitアプリのレイアウトや表示項目は、各 `streamlit_app.py` ファイルで変更可能です。

## 📄 ライセンス

このプロジェクトは個人利用目的で作成されています。

## 🤝 コントリビューション

改善提案やバグ報告は歓迎します。

## 📞 サポート

質問や問題がある場合は、各プロジェクトのコードコメントや計算ロジックを参照してください。