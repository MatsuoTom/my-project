# Streamlit Cloud デプロイガイド

このドキュメントは、my-projectのStreamlitアプリをStreamlit Cloudにデプロイする方法を説明します。

## 📋 前提条件

### 必須

- [x] GitHubアカウント
- [x] GitHubリポジトリ（https://github.com/MatsuoTom/my-project）
- [ ] Streamlit Cloudアカウント（https://streamlit.io/cloud）

### デプロイ可能なアプリ

このプロジェクトには3つのStreamlitアプリがあります：

1. **生命保険分析ツール**: `life_insurance/ui/streamlit_app.py`
2. **年金シミュレーター**: `pension_calc/ui/streamlit_app.py`
3. **投資シミュレーター**: `investment_simulation/ui/streamlit_app.py`（開発中）

## 🚀 デプロイ手順

### Step 1: Streamlit Cloudアカウント作成

1. https://streamlit.io/cloud にアクセス
2. 「Sign up」をクリック
3. GitHubアカウントで認証
4. 必要な権限を許可

### Step 2: アプリのデプロイ

#### 2.1 生命保険分析ツールのデプロイ

1. Streamlit Cloudダッシュボードで「New app」をクリック
2. 以下の情報を入力：
   - **Repository**: `MatsuoTom/my-project`
   - **Branch**: `main`
   - **Main file path**: `life_insurance/ui/streamlit_app.py`
   - **App URL**: `my-project-life-insurance`（任意）

3. 「Advanced settings」（オプション）:
   - **Python version**: 3.12
   - **Secrets**: 必要に応じて環境変数を設定

4. 「Deploy」をクリック

#### 2.2 年金シミュレーターのデプロイ

同様の手順で、以下の設定でデプロイ：

- **Repository**: `MatsuoTom/my-project`
- **Branch**: `main`
- **Main file path**: `pension_calc/ui/streamlit_app.py`
- **App URL**: `my-project-pension`（任意）

#### 2.3 投資シミュレーターのデプロイ（準備中）

開発完了後、以下の設定でデプロイ：

- **Repository**: `MatsuoTom/my-project`
- **Branch**: `main`
- **Main file path**: `investment_simulation/ui/streamlit_app.py`
- **App URL**: `my-project-investment`（任意）

### Step 3: デプロイの確認

1. デプロイが完了するまで待機（通常2-5分）
2. ログを確認してエラーがないことを確認
3. アプリのURLにアクセスして動作確認

## 📦 必要なファイル

### requirements.txt

プロジェクトルートに配置済み：

```txt
streamlit>=1.50.0
pandas>=2.3.2
numpy>=2.3.3
matplotlib>=3.10.6
plotly>=6.3.0
seaborn>=0.13.2
openpyxl>=3.1.5
yfinance>=0.2.66
```

### .streamlit/config.toml

Streamlit設定ファイル（プロジェクトルートに配置済み）：

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"
```

## 🔧 トラブルシューティング

### エラー1: モジュールが見つからない

**症状**: `ModuleNotFoundError: No module named 'xxxx'`

**解決策**:
1. `requirements.txt`に不足しているモジュールを追加
2. Streamlit Cloudでアプリを再起動

### エラー2: Pythonバージョンの不一致

**症状**: `Python version 3.xx is not supported`

**解決策**:
1. Advanced settingsでPython version を 3.12 に設定
2. アプリを再デプロイ

### エラー3: ファイルパスが見つからない

**症状**: `FileNotFoundError: [Errno 2] No such file or directory`

**解決策**:
1. 絶対パスではなく相対パスを使用
2. `Path(__file__).parent` を使用してルートディレクトリを取得

### エラー4: データファイルが見つからない

**症状**: CSVファイルやJSONファイルが読み込めない

**解決策**:
1. データファイルをGitリポジトリにコミット
2. `.gitignore`でデータファイルが除外されていないか確認

## 📊 デプロイ後の管理

### アプリの更新

1. ローカルで変更をコミット・プッシュ
   ```powershell
   git add .
   git commit -m "feat: 機能追加"
   git push origin main
   ```

2. Streamlit Cloudが自動的に変更を検出してデプロイ
   - 自動デプロイが有効な場合（デフォルト）
   - 手動デプロイの場合は「Reboot app」をクリック

### アプリの停止・削除

1. Streamlit Cloudダッシュボードにアクセス
2. アプリを選択
3. 「Settings」→「Delete app」

### ログの確認

1. Streamlit Cloudダッシュボードでアプリを選択
2. 「Logs」タブでリアルタイムログを確認
3. エラーやパフォーマンス問題をデバッグ

## 🔒 セキュリティ設定

### Secrets管理

機密情報（APIキー、パスワードなど）はSecretsで管理：

1. アプリの「Settings」→「Secrets」
2. TOML形式でSecretsを追加：
   ```toml
   api_key = "your-api-key"
   database_url = "your-database-url"
   ```

3. アプリ内でSecretsにアクセス：
   ```python
   import streamlit as st
   api_key = st.secrets["api_key"]
   ```

### プライベートリポジトリ

- プライベートリポジトリでも無料でデプロイ可能
- GitHubの権限設定でアクセスを制限

## 📈 パフォーマンス最適化

### キャッシュの活用

```python
import streamlit as st

@st.cache_data
def load_data():
    # データ読み込みをキャッシュ
    return pd.read_csv("data.csv")

@st.cache_resource
def load_model():
    # モデル読み込みをキャッシュ
    return load_ml_model()
```

### リソース制限

Streamlit Cloudの無料プランの制限：

- **CPU**: 1 core
- **メモリ**: 1 GB RAM
- **ストレージ**: 1 GB
- **アプリ数**: 無制限（パブリックアプリ）

大規模データや複雑な計算を行う場合は、有料プランを検討してください。

## 📱 カスタムドメイン（有料プラン）

1. Streamlit Cloudの有料プラン（Team/Enterprise）に加入
2. 「Settings」→「Custom domain」
3. DNSレコードを設定
4. カスタムドメインでアクセス可能に

## 🔄 自動デプロイの無効化

自動デプロイを無効化する場合：

1. アプリの「Settings」→「Advanced settings」
2. 「Auto-deploy」をオフに設定
3. 手動で「Reboot app」をクリックしてデプロイ

## 📞 サポート

### Streamlit Cloud サポート

- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)

### プロジェクト固有の問題

- GitHubリポジトリのIssuesで報告
- `.github/copilot-instructions.md`を参照

## 📝 デプロイチェックリスト

### デプロイ前

- [ ] `requirements.txt`が最新
- [ ] `.streamlit/config.toml`が設定済み
- [ ] ローカルでアプリが正常に動作
- [ ] データファイルがGitにコミット済み
- [ ] Secretsが必要な場合は準備完了

### デプロイ中

- [ ] Streamlit Cloudアカウント作成
- [ ] GitHubリポジトリと連携
- [ ] アプリ設定を入力
- [ ] Advanced settingsを確認
- [ ] デプロイを開始

### デプロイ後

- [ ] デプロイログを確認
- [ ] アプリのURLにアクセス
- [ ] 全機能が正常に動作することを確認
- [ ] パフォーマンスをチェック
- [ ] README.mdにデプロイURLを追加

## 🌐 デプロイ済みURL（例）

デプロイ後、以下のようなURLが割り当てられます：

- **生命保険分析**: https://my-project-life-insurance.streamlit.app
- **年金シミュレーター**: https://my-project-pension.streamlit.app
- **投資シミュレーター**: https://my-project-investment.streamlit.app

README.mdにこれらのURLを追加してください。

---

**作成日**: 2025年11月8日  
**Phase**: 5（CI/CD構築）  
**ステータス**: デプロイ準備完了
