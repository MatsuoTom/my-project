"""
車両維持費管理アプリ起動スクリプト
"""

import subprocess
import sys


def main():
    """Streamlitアプリを起動"""
    print("🚗 車両維持費管理アプリを起動しています...")
    
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "vehicle_finance/ui/streamlit_app.py",
                "--server.port=8509",
                "--browser.serverAddress=localhost",
            ],
            check=True,
        )
    except KeyboardInterrupt:
        print("\n✅ アプリを終了しました")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
