"""
投資信託比較アプリ - 起動スクリプト

生命保険と投資信託の比較に特化したアプリを起動します。

使用方法:
    python scripts/run_comparison_app.py

または直接:
    streamlit run life_insurance/ui/comparison_app.py
"""

import subprocess
import sys
from pathlib import Path


def main():
    """投資信託比較アプリを起動"""
    # プロジェクトルートからの相対パス
    app_path = Path(__file__).parent.parent / "life_insurance" / "ui" / "comparison_app.py"
    
    if not app_path.exists():
        print(f"エラー: アプリケーションファイルが見つかりません: {app_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("⚖️  生命保険 vs 投資信託 比較分析アプリ")
    print("=" * 60)
    print(f"アプリを起動しています: {app_path}")
    print("ブラウザが自動的に開きます...")
    print("終了するには Ctrl+C を押してください")
    print("=" * 60)
    
    # Streamlitアプリを起動（別ポートを使用）
    try:
        subprocess.run([
            "streamlit", "run",
            str(app_path),
            "--server.port=8502",
            "--server.headless=false"
        ])
    except KeyboardInterrupt:
        print("\n\nアプリケーションを終了しています...")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
