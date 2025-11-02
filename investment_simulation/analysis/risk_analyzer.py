"""
リスク分析モジュール

最大ドローダウン、ボラティリティ、シャープレシオなどのリスク指標を計算
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import plotly.graph_objects as go


class RiskAnalyzer:
    """
    投資リスクを分析するクラス
    """
    
    def __init__(self, parsed_data: pd.DataFrame):
        """
        Args:
            parsed_data: パース済みデータ
        """
        self.data = parsed_data.copy()
        self.data = self.data.sort_values('発生日').reset_index(drop=True)
    
    def calculate_max_drawdown(self) -> Dict:
        """
        最大ドローダウンを計算
        
        Returns:
            Dict: 最大ドローダウン情報
        """
        # 評価額の推移
        values = self.data['評価金額'].values
        dates = self.data['発生日'].values
        
        if len(values) == 0:
            return {}
        
        # 累積最大値
        cummax = np.maximum.accumulate(values)
        
        # ドローダウン（%）
        drawdown = (values - cummax) / cummax * 100
        
        # 最大ドローダウン
        max_dd_idx = np.argmin(drawdown)
        max_dd = drawdown[max_dd_idx]
        max_dd_date = dates[max_dd_idx]
        
        # ピークの日付
        peak_idx = np.argmax(cummax[:max_dd_idx+1]) if max_dd_idx > 0 else 0
        peak_date = dates[peak_idx]
        peak_value = cummax[peak_idx]
        
        # 回復日（もしあれば）
        recovery_idx = None
        if max_dd_idx < len(values) - 1:
            for i in range(max_dd_idx + 1, len(values)):
                if values[i] >= peak_value:
                    recovery_idx = i
                    break
        
        recovery_date = dates[recovery_idx] if recovery_idx is not None else None
        
        # Timestamp型に変換してから日数計算
        if recovery_date is not None:
            recovery_days = (pd.Timestamp(recovery_date) - pd.Timestamp(max_dd_date)).days
        else:
            recovery_days = None
        
        return {
            '最大ドローダウン率': max_dd,
            '最大ドローダウン日': max_dd_date,
            'ピーク日': peak_date,
            'ピーク評価額': peak_value,
            '最低評価額': values[max_dd_idx],
            '回復日': recovery_date,
            '回復期間_日数': recovery_days,
            'ドローダウン系列': drawdown.tolist(),
            '日付系列': dates.tolist()
        }
    
    def calculate_volatility(self) -> Dict:
        """
        ボラティリティ（価格変動率）を計算
        
        Returns:
            Dict: ボラティリティ情報
        """
        # 基準価額の日次リターン
        prices = self.data['当日基準価額'].values
        
        if len(prices) < 2:
            return {}
        
        # 日次リターン
        returns = np.diff(prices) / prices[:-1]
        
        # 統計量
        daily_volatility = np.std(returns) * 100
        annual_volatility = daily_volatility * np.sqrt(252)  # 年率換算（営業日ベース）
        
        # リターンの分布
        return_stats = pd.Series(returns).describe()
        
        return {
            '日次ボラティリティ': daily_volatility,
            '年率ボラティリティ': annual_volatility,
            '平均日次リターン': np.mean(returns) * 100,
            '最大日次リターン': np.max(returns) * 100,
            '最小日次リターン': np.min(returns) * 100,
            'リターン統計': return_stats.to_dict(),
            '日次リターン系列': returns.tolist()
        }
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.001) -> float:
        """
        シャープレシオを計算（簡易版）
        
        Args:
            risk_free_rate: 無リスク金利（年率、デフォルト0.1%）
            
        Returns:
            float: シャープレシオ
        """
        vol_info = self.calculate_volatility()
        
        if not vol_info or vol_info['年率ボラティリティ'] == 0:
            return 0.0
        
        # 最初と最後の評価額からリターンを計算
        if len(self.data) < 2:
            return 0.0
        
        initial_value = self.data['評価金額'].iloc[0]
        final_value = self.data['評価金額'].iloc[-1]
        
        if initial_value == 0:
            return 0.0
        
        # 保有期間
        days = (self.data['発生日'].iloc[-1] - self.data['発生日'].iloc[0]).days
        years = days / 365.25
        
        if years == 0:
            return 0.0
        
        # 年率リターン
        annual_return = ((final_value / initial_value) ** (1 / years) - 1) * 100
        
        # シャープレシオ
        sharpe = (annual_return - risk_free_rate * 100) / vol_info['年率ボラティリティ']
        
        return sharpe
    
    def calculate_var(self, confidence_level: float = 0.95) -> Dict:
        """
        VaR (Value at Risk) を計算
        
        Args:
            confidence_level: 信頼水準（デフォルト95%）
            
        Returns:
            Dict: VaR情報
        """
        vol_info = self.calculate_volatility()
        
        if not vol_info:
            return {}
        
        returns = np.array(vol_info['日次リターン系列'])
        
        # ヒストリカルVaR
        var_percentile = (1 - confidence_level) * 100
        historical_var = np.percentile(returns, var_percentile) * 100
        
        # パラメトリックVaR（正規分布を仮定）
        # scipyなしで近似的に計算（95%信頼水準 → z=1.645, 99% → z=2.326）
        z_score_map = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}
        z_score = z_score_map.get(confidence_level, 1.645)
        parametric_var = (np.mean(returns) + z_score * np.std(returns)) * 100
        
        # 現在の評価額に対するVaR金額
        current_value = self.data['評価金額'].iloc[-1]
        var_amount_historical = current_value * historical_var / 100
        var_amount_parametric = current_value * parametric_var / 100
        
        return {
            '信頼水準': confidence_level,
            'ヒストリカルVaR_率': historical_var,
            'ヒストリカルVaR_金額': var_amount_historical,
            'パラメトリックVaR_率': parametric_var,
            'パラメトリックVaR_金額': var_amount_parametric,
            '現在評価額': current_value
        }
    
    def analyze_downside_risk(self) -> Dict:
        """
        下方リスクを分析
        
        Returns:
            Dict: 下方リスク情報
        """
        vol_info = self.calculate_volatility()
        
        if not vol_info:
            return {}
        
        returns = np.array(vol_info['日次リターン系列'])
        
        # 下方偏差（マイナスリターンのみの標準偏差）
        negative_returns = returns[returns < 0]
        downside_deviation = np.std(negative_returns) if len(negative_returns) > 0 else 0
        
        # 下方リスク（年率換算）
        annual_downside_risk = downside_deviation * np.sqrt(252) * 100
        
        # マイナスリターンの頻度
        negative_days = len(negative_returns)
        total_days = len(returns)
        negative_frequency = (negative_days / total_days) * 100 if total_days > 0 else 0
        
        return {
            '下方偏差_日次': downside_deviation * 100,
            '下方偏差_年率': annual_downside_risk,
            'マイナスリターン頻度': negative_frequency,
            'マイナスリターン日数': negative_days,
            '総日数': total_days,
            '平均マイナスリターン': np.mean(negative_returns) * 100 if len(negative_returns) > 0 else 0
        }
    
    def plot_drawdown(self) -> go.Figure:
        """
        ドローダウンをプロット
        
        Returns:
            go.Figure: グラフオブジェクト
        """
        dd_info = self.calculate_max_drawdown()
        
        if not dd_info:
            return go.Figure()
        
        fig = go.Figure()
        
        # ドローダウン
        fig.add_trace(go.Scatter(
            x=dd_info['日付系列'],
            y=dd_info['ドローダウン系列'],
            mode='lines',
            name='ドローダウン',
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.2)',
            line=dict(color='red', width=2)
        ))
        
        # 最大ドローダウン地点をマーク
        fig.add_trace(go.Scatter(
            x=[dd_info['最大ドローダウン日']],
            y=[dd_info['最大ドローダウン率']],
            mode='markers',
            name='最大DD',
            marker=dict(color='darkred', size=15, symbol='x')
        ))
        
        fig.update_layout(
            title=f'ドローダウン推移（最大: {dd_info["最大ドローダウン率"]:.2f}%）',
            xaxis_title='日付',
            yaxis_title='ドローダウン（%）',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def plot_return_distribution(self) -> go.Figure:
        """
        リターン分布をプロット
        
        Returns:
            go.Figure: グラフオブジェクト
        """
        vol_info = self.calculate_volatility()
        
        if not vol_info:
            return go.Figure()
        
        returns = np.array(vol_info['日次リターン系列']) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=returns,
            nbinsx=50,
            name='リターン分布',
            marker_color='lightblue',
            opacity=0.7
        ))
        
        fig.update_layout(
            title='日次リターン分布',
            xaxis_title='日次リターン（%）',
            yaxis_title='頻度',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def plot_rolling_volatility(self, window: int = 30) -> go.Figure:
        """
        ローリングボラティリティをプロット
        
        Args:
            window: ウィンドウサイズ（日数）
            
        Returns:
            go.Figure: グラフオブジェクト
        """
        prices = self.data['当日基準価額'].values
        dates = self.data['発生日'].values
        
        if len(prices) < window:
            return go.Figure()
        
        # 日次リターン
        returns = np.diff(prices) / prices[:-1]
        
        # ローリングボラティリティ
        rolling_vol = pd.Series(returns).rolling(window=window).std() * np.sqrt(252) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates[window:],
            y=rolling_vol[window:],
            mode='lines',
            name=f'{window}日ローリングボラティリティ',
            line=dict(color='purple', width=2)
        ))
        
        fig.update_layout(
            title=f'{window}日ローリングボラティリティ（年率）',
            xaxis_title='日付',
            yaxis_title='ボラティリティ（%）',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
