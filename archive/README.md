# archive ディレクトリ運用方針

> このファイルの目的: archive 配下を履歴参照専用として運用するための入口を提供する。

このディレクトリは、現行運用の正本ではない補助資料や一時退避物を保管する場所です。

## 置いてよいもの

- 旧版 README や退避した文書
- 一時的に参照したいレポートや出力物
- 手元検証用の補助スクリプト

## 置かないもの

- 現行仕様の正本
- 日常運用で参照する手順書
- 継続的に更新する計画書や進捗管理文書

## 正本の配置先

- 現行仕様・運用ガイド: [docs/INDEX.md](docs/INDEX.md)
- リファクタリング計画・履歴: [REFACTORING/INDEX.md](REFACTORING/INDEX.md)

## 現在の archive 内容

詳細な分類は [archive/INVENTORY.md](archive/INVENTORY.md) を参照します。

- `README_old.md`: 旧ルート README の履歴参照
- `README_old_backup.md`: 旧 README の別版（履歴参照）

## 運用ルール

1. `archive/` に置いた文書は原則として履歴参照用とする。
2. 現行で使う文書は `docs/` に移す。
3. バックアップを作る場合は `backup_YYYYMMDD_HHMMSS/` 形式を使う。
4. ローカル専用の一時ファイルは Git 追跡対象にしない。
5. `archive/` 配下へ新しい運用手順の正本を書かない。
