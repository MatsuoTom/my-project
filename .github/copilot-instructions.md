<!-- .github/copilot-instructions.md: Project-specific guidance for AI coding agents -->
# my-project — AI 作業指示（簡潔版）

このリポジトリは日本向けの年金シミュレーション小型プロジェクトです。AI エージェントは下記の「実際に存在するパターン」と「注意点」に従って作業してください。

- 主要なファイル
  - `pension_utils.py` — 実測データ（`records`）と計算ユーティリティ（`build_paid_years`, `estimate_income_by_company_growth`, `paid_months_kokumin`, `past_insured_months`）。ここがデータの単一真実源（SoT）です。
  - `financial_asset.py` — Streamlit ベースの主な UI。`pension_utils.df` を直接参照して描画・計算を行っています。
  - `financial_kokumin.py` — 補助的な分析/プロットのスクリプト（未完成のセルやプレースホルダ変数あり）。
  - `main.py` — 最小のエントリポイント（現在は簡易的なメッセージ出力のみ）。
  - `pyproject.toml` — 依存関係リスト（例: streamlit, pandas, matplotlib, numpy 等）。

- データと命名規約（重要）
  - DataFrame のカラム名は日本語（例: `年度`, `年齢`, `加入制度`, `加入月数`, `納付額`）。文字列比較は日本語文字列を直接使うコードが多いので、変更時は文字列リテラルを壊さないこと。
  - `pension_utils.df` が計算ロジックの入力になっているため、UI 側（`financial_asset.py`）を修正する場合でも、まず `pension_utils.py` にある関数を再利用または拡張してください。

- 実行／デバッグの要点
  - Streamlit アプリの起動: PowerShell で

    > Activate your venv first, then:

    streamlit run financial_asset.py

  - 単純なスクリプト実行: `python main.py`
  - Python バージョン: `pyproject.toml` によれば >= 3.12 を想定。
  - 依存パッケージをローカルに入れるには（例）: `pip install streamlit pandas matplotlib numpy plotly seaborn openpyxl yfinance`

- コードベースで見つかった注意点（手を入れるときの具体指示）
  - `financial_asset.py` に重複したブロック、未定義変数（例: `future_years`, `future_monthly_fees`, `national_pension_fee_history`, `total_paid_national_actual`）や重複した出力行が存在します。変更やリファクタを行う前に未定義変数を検索し、どのファイルで値を用意するか設計してください。
  - UI（Streamlit）のサイドバーで多数の副作用的計算がモジュールインポート時に走る構造です。テスト可能にするには計算ロジックを関数化して `pension_utils.py` に移すことを推奨します。
  - フォント指定（`plt.rcParams['font.family'] = 'Meiryo'`）など環境依存の設定があるため、Windows 以外の環境で描画を確認する際は注意してください。

- 変更／PR のチェックリスト（具体的）
  - 変更はまず `pension_utils.py` の関数に集約する。UI (`financial_asset.py`) はそれら関数を呼ぶ薄い層にする。
  - DataFrame の日本語カラム名を変更する場合は、該当するすべての参照箇所（ファイル全体）を grep で更新する。
  - Streamlit の UI を編集する際は、`streamlit run financial_asset.py` で手元で表示を確認する。
  - 依存パッケージを追加したら `pyproject.toml` に明示的に追記する。

- 典型的なリクエスト例（AI が答えるべき具体的な振る舞い）
  - 「`estimated_kokumin` の計算を `pension_utils.py` に移して単体テストを書いて」→ データ形状（カラム名）を引数にする純粋関数を作り、`pension_utils.py` に追加し、`financial_asset.py` はその関数を呼ぶように差し替える。
  - 「UI の年齢プロットに注釈を追加してほしい」→ `financial_asset.py` の描画直前のリスト（`plot_ages`, `plot_payment_values`）を変更するのみ。未定義変数がないか確認。

- 探すべきキーワード／ファイル片（作業時のお役立ち）
  - 関数: `build_paid_years`, `estimate_income_by_company_growth`, `paid_months_kokumin`, `past_insured_months`
  - DataFrame カラム: `年度`, `年齢`, `加入制度`, `加入月数`, `納付額`, `推定年収`
  - 問題になりやすい未定義名: `future_years`, `future_monthly_fees`, `national_pension_fee_history`, `total_paid_national_actual`

- 最後に
  - このファイルを元にまず小さな変更（例: 未定義変数の所在を確認してドキュメント化）を提案してください。不要な大規模リファクタは避け、まず「実行可能な Streamlit が壊れない」ことを優先します。

フィードバック: ここで不足している箇所（例えばよく使う開発コマンドや追加のデータソース）があれば教えてください。追記・修正して再生成します。
