# archive 棚卸し一覧

> このファイルの目的: archive 配下の履歴参照物を分類し、現行 docs との境界を明確にする。

最終更新: 2026年03月30日

## 分類ルール

- 履歴参照: 過去時点の README、レポート、退避資料
- 補助スクリプト: 通常運用の正本ではない補助用途のスクリプト
- 一時出力: 必要時のみ参照する静的出力

## 一覧

| ファイル | 区分 | 扱い |
|---|---|---|
| `README.md` | 現行入口 | archive の運用方針を示す入口 |
| `README_old.md` | 履歴参照 | 旧ルート README。現行手順の正本として使わない |
| `README_old_backup.md` | 履歴参照 | 旧ルート README の別版。差分確認結果を踏まえ保持 |

## 保持判定（2026-03-30）

### 保持推奨

- `README.md`: archive の入口として必要
- `INVENTORY.md`: 境界管理の基準として必要
- `README_old.md`: 旧 README の履歴参照として保持価値あり
- `README_old_backup.md`: `README_old.md` とは別内容のため保持

### 削除候補

- 現時点の候補なし（主要な不要物は削除済み）

### 判定根拠

- `README_old.md` と `README_old_backup.md` は差分が大きく、単純重複ではなかった
- `bandit_report.json` と `backup.py` は現行 docs / コードから直接参照されず、削除しても導線に影響しないことを確認
- 正本導線は [docs/INDEX.md](docs/INDEX.md) と [REFACTORING/INDEX.md](REFACTORING/INDEX.md) で担保済み

## 境界ルール

- 現行仕様・運用ガイドは [docs/INDEX.md](docs/INDEX.md) を正本とする
- リファクタリングの計画・進捗・履歴は [REFACTORING/INDEX.md](REFACTORING/INDEX.md) を正本とする
- archive 配下の内容を更新した場合でも、現行仕様の変更は docs 側へ反映する
- archive 配下の文書へ新しい実行手順を書き足さない
