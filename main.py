#!/usr/bin/env python
"""
金融分析ツール統合ランチャー

生命保険分析と年金シミュレーションの2つのプロジェクトを統合管理
"""

import os
import sys
import subprocess
from pathlib import Path

def show_header():
    """ヘッダー表示"""
    print("=" * 60)
    print("🏦 金融分析ツール統合ランチャー")
    print("=" * 60)
    print()

def show_menu():
    """メニュー表示"""
    print("📋 利用可能なプロジェクト:")
    print()
    print("1️⃣  生命保険分析ツール")
    print("   📊 生命保険料控除の分析")
    print("   💰 投資信託との比較分析")
    print("   🎯 引き出しタイミング最適化")
    print()
    print("2️⃣  年金シミュレーションツール")
    print("   📈 年金受給額の試算")
    print("   📊 納付実績の分析")
    print("   💰 損益分岐点の計算")
    print()
    print("3️⃣  NISA投資シミュレーションツール")
    print("   💰 月次投資データの管理")
    print("   📊 リスク・リターン分析")
    print("   🔮 将来予測シミュレーション")
    print()
    print("4️⃣  車両維持費年間計画システム")
    print("   🚗 年間維持費の計画管理")
    print("   📝 実績入力と計画比較")
    print("   📈 長期コストシミュレーション")
    print()
    print("5️⃣  プロジェクト情報表示")
    print("6️⃣  終了")
    print()

def launch_life_insurance():
    """生命保険分析ツールを起動"""
    print("🚀 生命保険分析ツールを起動中...")
    print("=" * 50)
    
    app_path = Path(__file__).parent / "life_insurance" / "ui" / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"❌ エラー: アプリファイルが見つかりません: {app_path}")
        return False
    
    try:
        project_root = Path(__file__).parent
        env = os.environ.copy()
        # このプロジェクトを最優先で import させる
        env["PYTHONPATH"] = str(project_root)
        cmd = [
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            str(app_path),
            "--server.port=8507",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ]
        
        print("💡 ブラウザでアプリケーションが開きます")
        print("   URL: http://localhost:8507")
        print("⏹️  停止するには Ctrl+C を押してください")
        print("=" * 50)
        
        subprocess.run(cmd, env=env, cwd=str(project_root))
        return True
        
    except KeyboardInterrupt:
        print("\n👋 生命保険分析ツールを停止しました")
        return True
    except FileNotFoundError:
        print("❌ エラー: Streamlitがインストールされていません")
        print("   インストール方法: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

def launch_pension():
    """年金シミュレーションツールを起動"""
    print("🚀 年金シミュレーションツールを起動中...")
    print("=" * 50)
    
    app_path = Path(__file__).parent / "pension_calc" / "ui" / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"❌ エラー: アプリファイルが見つかりません: {app_path}")
        return False
    
    try:
        project_root = Path(__file__).parent
        env = os.environ.copy()
        # このプロジェクトを最優先で import させる
        env["PYTHONPATH"] = str(project_root)
        cmd = [
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            str(app_path),
            "--server.port=8508",
            "--server.address=localhost", 
            "--browser.gatherUsageStats=false"
        ]
        
        print("💡 ブラウザでアプリケーションが開きます")
        print("   URL: http://localhost:8508")
        print("⏹️  停止するには Ctrl+C を押してください")
        print("=" * 50)
        
        subprocess.run(cmd, env=env, cwd=str(project_root))
        return True
        
    except KeyboardInterrupt:
        print("\n👋 年金シミュレーションツールを停止しました")
        return True
    except FileNotFoundError:
        print("❌ エラー: Streamlitがインストールされていません")
        print("   インストール方法: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

def launch_investment():
    """NISA投資シミュレーションツールを起動"""
    print("🚀 NISA投資シミュレーションツールを起動中...")
    print("=" * 50)
    
    app_path = Path(__file__).parent / "investment_simulation" / "ui" / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"❌ エラー: アプリファイルが見つかりません: {app_path}")
        return False
    
    try:
        project_root = Path(__file__).parent
        env = os.environ.copy()
        # このプロジェクトを最優先で import させる
        env["PYTHONPATH"] = str(project_root)
        cmd = [
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            str(app_path),
            "--server.port=8512",
            "--server.address=localhost", 
            "--browser.gatherUsageStats=false"
        ]
        
        print("💡 ブラウザでアプリケーションが開きます")
        print("   URL: http://localhost:8512")
        print("⏹️  停止するには Ctrl+C を押してください")
        print("=" * 50)
        
        subprocess.run(cmd, env=env, cwd=str(project_root))
        return True
        
    except KeyboardInterrupt:
        print("\n👋 NISA投資シミュレーションツールを停止しました")
        return True
    except FileNotFoundError:
        print("❌ エラー: Streamlitがインストールされていません")
        print("   インストール方法: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

def launch_vehicle_finance():
    """車両維持費年間計画システムの起動"""
    print("\n🚗 車両維持費年間計画システムを起動します")
    print("=" * 50)
    
    app_path = Path(__file__).parent / "vehicle_finance" / "ui" / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"❌ エラー: アプリファイルが見つかりません: {app_path}")
        return False
    
    try:
        project_root = Path(__file__).parent
        env = os.environ.copy()
        # このプロジェクトを最優先で import させる
        env["PYTHONPATH"] = str(project_root)
        cmd = [
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            str(app_path),
            "--server.port=8509",
            "--server.address=localhost", 
            "--browser.gatherUsageStats=false"
        ]
        
        print("💡 ブラウザでアプリケーションが開きます")
        print("   URL: http://localhost:8509")
        print("⏹️  停止するには Ctrl+C を押してください")
        print("=" * 50)
        
        subprocess.run(cmd, env=env, cwd=str(project_root))
        return True
        
    except KeyboardInterrupt:
        print("\n👋 車両維持費年間計画システムを停止しました")
        return True
    except FileNotFoundError:
        print("❌ エラー: Streamlitがインストールされていません")
        print("   インストール方法: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

def show_project_info():
    """プロジェクト情報を表示"""
    print("📋 プロジェクト情報")
    print("=" * 50)
    print()
    print("🏗️  プロジェクト構造:")
    print("my-project/")
    print("├── life_insurance/          # 生命保険分析")
    print("│   ├── core/                # コア計算機能")
    print("│   ├── analysis/            # 分析ロジック")
    print("│   ├── ui/                  # Streamlit UI")
    print("│   └── tests/               # テスト")
    print("├── pension_calc/            # 年金シミュレーション")
    print("│   ├── core/                # コア計算機能")
    print("│   ├── analysis/            # 分析ロジック")
    print("│   ├── ui/                  # Streamlit UI")
    print("│   └── data/                # データ")
    print("├── investment_simulation/   # NISA投資シミュレーション")
    print("│   ├── core/                # コア計算機能")
    print("│   ├── analysis/            # 分析ロジック")
    print("│   ├── ui/                  # Streamlit UI")
    print("│   └── data/                # データ")
    print("├── vehicle_finance/         # 車両維持費年間計画")
    print("│   ├── core/                # コア計算機能")
    print("│   ├── data/                # データモデル")
    print("│   ├── ui/                  # Streamlit UI")
    print("│   └── tests/               # テスト")
    print("├── main.py                  # 統合ランチャー")
    print("└── README.md                # プロジェクト説明")
    print()
    print("🛠️  個別起動コマンド:")
    print("生命保険: python run_life_insurance_app.py")
    print("年金:     python run_pension_app.py")
    print("投資:     python run_investment_app.py")
    print("車両:     python run_vehicle_app.py")
    print()
    print("📦 必要パッケージ:")
    print("streamlit, pandas, plotly, numpy, matplotlib")
    print()

def main():
    """メイン関数"""
    while True:
        show_header()
        show_menu()
        
        try:
            choice = input("選択してください (1-6): ").strip()
            print()
            
            if choice == "1":
                if not launch_life_insurance():
                    input("\nEnterキーを押して続行...")
                
            elif choice == "2":
                if not launch_pension():
                    input("\nEnterキーを押して続行...")
                
            elif choice == "3":
                if not launch_investment():
                    input("\nEnterキーを押して続行...")
                
            elif choice == "4":
                if not launch_vehicle_finance():
                    input("\nEnterキーを押して続行...")
                
            elif choice == "5":
                show_project_info()
                input("\nEnterキーを押して続行...")
                # 実行コマンド（PowerShell）: & .venv/Scripts/python.exe main.py
            elif choice == "6":
                print("👋 金融分析ツールを終了します")
                break
                
            else:
                print("❌ 無効な選択です。1-6の数字を入力してください。")
                input("\nEnterキーを押して続行...")
        
        except KeyboardInterrupt:
            print("\n\n👋 金融分析ツールを終了します")
            break
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            input("\nEnterキーを押して続行...")

if __name__ == "__main__":
    main()