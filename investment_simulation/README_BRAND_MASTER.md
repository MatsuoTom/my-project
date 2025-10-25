# NISA投資シミュレーション — 銘柄マスタ管理機能

## 🎯 概要

NISA投資シミュレーションに**銘柄マスタ管理機能**を追加しました。これにより、銘柄・投資方法・証券会社を事前登録し、データ入力時に選択できるようになります。

## ✨ 主要機能

### 1️⃣ 銘柄マスタ管理
- **銘柄の登録・編集・削除**
  - 銘柄コード（ティッカーシンボル等）
  - 銘柄名
  - カテゴリ（ETF、投資信託、個別株、債券、その他）
  - 地域（米国、日本、全世界、先進国、新興国、その他）

- **フィルタ機能**
  - カテゴリ別表示
  - 地域別表示

- **表示形式**
  - `コード: 銘柄名` 形式でUI表示
  - データ編集可能なテーブルビュー

### 2️⃣ 投資方法マスタ
- デフォルト: 新規購入、積立、スポット購入、配当再投資
- カスタム投資方法の追加・削除

### 3️⃣ 証券会社マスタ
- デフォルト: SBI証券、楽天証券、マネックス証券、松井証券、auカブコム証券
- カスタム証券会社の追加・削除

### 4️⃣ データ永続化
- JSON形式でマスタデータを保存
- `investment_simulation/data/brand_master.json`
- アプリ再起動時も設定を保持

### 5️⃣ 既存データ自動インポート
- 初回起動時に既存の投資データから銘柄・投資方法・証券会社を自動抽出してマスタに登録

## 📦 デフォルトマスタデータ

### 銘柄（8種類）
| コード | 銘柄名 | カテゴリ | 地域 |
|--------|--------|----------|------|
| VTI | Vanguard Total Stock Market ETF | ETF | 米国 |
| VOO | Vanguard S&P 500 ETF | ETF | 米国 |
| VT | Vanguard Total World Stock ETF | ETF | 全世界 |
| 1655 | iシェアーズ S&P500米国株ETF | ETF | 米国 |
| 2558 | MAXIS米国株式(S&P500)上場投信 | ETF | 米国 |
| emaxis-slim-sp500 | eMAXIS Slim 米国株式(S&P500) | 投資信託 | 米国 |
| emaxis-slim-allcountry | eMAXIS Slim 全世界株式(オール・カントリー) | 投資信託 | 全世界 |
| 楽天VTI | 楽天・全米株式インデックス・ファンド | 投資信託 | 米国 |

### 投資方法（4種類）
- 新規購入
- 積立
- スポット購入
- 配当再投資

### 証券会社（5社）
- SBI証券
- 楽天証券
- マネックス証券
- 松井証券
- auカブコム証券

## 🚀 使い方

### 1. アプリ起動
```powershell
python scripts/run_investment_app.py
```
または
```powershell
streamlit run investment_simulation/ui/streamlit_app.py --server.port=8512
```

### 2. マスタ管理
1. **「🔧 マスタ管理」タブ**を開く
2. サブタブから管理したい項目を選択
   - 🏷️ 銘柄マスタ
   - 📈 投資方法
   - 🏦 証券会社

### 3. 銘柄の追加
1. 「➕ 新規銘柄登録」を展開
2. 必要情報を入力
   - 銘柄コード（必須）
   - 銘柄名（必須）
   - カテゴリ
   - 地域
3. 「銘柄を追加」ボタンをクリック

### 4. データ入力時の選択
1. **「📝 銘柄登録・データ管理」タブ**を開く
2. 「➕ 新規データ追加」セクションで
   - **銘柄入力方法**: 「マスタから選択」を選択
   - プルダウンから登録済み銘柄を選択
3. 同様に投資方法・証券会社も選択可能

### 5. マスタのリセット
1. 「🔧 マスタ管理」タブ下部
2. 「⚠️ マスタデータのリセット」を展開
3. 「デフォルトにリセット」をクリック

## 🧪 テスト

### テスト実行
```powershell
pytest investment_simulation/tests/test_brand_master.py -v
```

### テストカバレッジ
- **33件のテストケース、100%パス**
- カバー内容:
  - 初期化
  - CRUD操作（追加、更新、削除、検索）
  - フィルタ機能
  - 永続化
  - 一括インポート
  - データ検証

## 📂 ファイル構成

```
investment_simulation/
├── core/
│   ├── brand_master.py          # 銘柄マスタ管理モジュール（430行）
│   └── nisa_utils.py            # NISA計算ユーティリティ
├── data/
│   ├── brand_master.json        # マスタデータ（自動生成）
│   └── nisa_monthly_data.csv    # 月次投資データ
├── tests/
│   ├── __init__.py
│   └── test_brand_master.py     # テストスイート（33件）
└── ui/
    └── streamlit_app.py         # UI（マスタ管理タブ追加）
```

## 🔧 API仕様

### BrandMasterクラス

```python
from investment_simulation.core.brand_master import get_brand_master

# シングルトンインスタンス取得
master = get_brand_master()

# 銘柄管理
master.add_brand("AAPL", "Apple Inc.", "個別株", "米国")
master.update_brand("AAPL", name="Apple Corp.")
master.delete_brand("AAPL")
brands = master.get_brands(category="ETF", region="米国")
brand = master.find_brand_by_code("AAPL")

# 投資方法管理
master.add_method("カスタム投資方法")
master.delete_method("カスタム投資方法")
methods = master.get_methods()

# 証券会社管理
master.add_broker("カスタム証券")
master.delete_broker("カスタム証券")
brokers = master.get_brokers()

# 一括インポート
import pandas as pd
df = pd.DataFrame({...})
result = master.import_from_dataframe(df)

# リセット
master.reset_to_default()
```

## 📝 変更履歴

### v0.2.0-nisa-brand-master (2025-10-25)
- ✨ 銘柄マスタ管理機能追加
- ✨ 投資方法・証券会社マスタ管理
- ✨ UI統合（マスタから選択入力）
- ✨ JSON永続化
- ✅ 33件のテスト（100%パス）
- 📚 デフォルトマスタデータ追加

## 🎓 次のステップ

### 推奨カスタマイズ
1. **銘柄の追加**
   - 自分が保有している銘柄を追加
   - カテゴリ・地域を適切に設定

2. **投資方法の追加**
   - 「ボーナス購入」「リバランス」等、自分の投資スタイルに合わせた方法を追加

3. **証券会社の追加**
   - 利用している証券会社を追加

### 今後の機能拡張アイデア
- 銘柄の一括インポート（CSVファイル）
- 銘柄情報のAPI連携（リアルタイム価格取得）
- カテゴリ・地域の動的追加
- 銘柄のお気に入り機能
- 銘柄別パフォーマンス分析

## 💡 ヒント

- **マスタから選択 vs 手動入力**
  - 繰り返し使う銘柄 → マスタに登録
  - 一時的な銘柄 → 手動入力

- **既存データの活用**
  - 初回起動時に既存データから自動的にマスタに追加される
  - 必要に応じて編集・整理

- **データの永続化**
  - マスタデータは `investment_simulation/data/brand_master.json` に保存
  - バックアップを取ることを推奨

## 🐛 トラブルシューティング

### マスタデータが読み込まれない
```powershell
# マスタファイルを削除して再生成
rm investment_simulation/data/brand_master.json
# アプリ再起動でデフォルトデータが生成される
```

### テストが失敗する
```powershell
# 依存パッケージの再インストール
pip install -r requirements.txt
# キャッシュクリア
pytest --cache-clear
```

## 📄 ライセンス

このプロジェクトの一部として、同じライセンスが適用されます。
