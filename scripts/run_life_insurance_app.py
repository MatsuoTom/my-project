#!/usr/bin/env python
"""
生命保険料控除分析システム - メインアプリ起動スクリプト

旧生命保険料控除制度の節税効果と最適な引き出しタイミングを分析する
Webアプリケーションを起動します。

使用方法:
    python scripts/run_life_insurance_app.py

または:
    python -m scripts.run_life_insurance_app

機能:
- 基本控除計算
- 引き出しタイミング最適化
- 複数戦略の自動比較（116戦略）
- 部分解約後の資金運用シミュレーション

バージョン: 2.0.0
最終更新: 2025-10-18
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """メインアプリケーションを起動"""
    print("=" * 60)
    print("💰 生命保険料控除分析システム v2.0")
    print("=" * 60)

    # プロジェクトルートとアプリパスの取得
    project_root = Path(__file__).resolve().parents[1]
    app_path = project_root / "life_insurance" / "ui" / "streamlit_app.py"

    # アプリファイルの存在確認
    if not app_path.exists():
        print(f"❌ エラー: アプリケーションファイルが見つかりません")
        print(f"   パス: {app_path}")
        return 1

    # 環境変数の設定（Pythonパスにプロジェクトルートを追加）
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root)

    # Streamlit起動コマンド
    cmd = [
        sys.executable, "-m", "streamlit", "run", str(app_path),
        "--server.port=8507",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false"
    ]

    print("✅ アプリケーションを起動しています...")
    print(f"� プロジェクトルート: {project_root}")
    print(f"📄 アプリファイル: {app_path}")
    print("🌐 ブラウザでアプリが開きます: http://localhost:8507")
    print("⏹️  停止するには Ctrl+C を押してください")
    print("=" * 60)

    try:
        # 作業ディレクトリをプロジェクトルートに変更
        os.chdir(project_root)
        subprocess.run(cmd, env=env)
        return 0
    except KeyboardInterrupt:
        print("\n\n👋 アプリケーションを停止しました")
        return 0
    except FileNotFoundError:
        print("❌ エラー: Streamlit が見つかりません")
        print("   インストール: pip install streamlit")
        return 1
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
