import os
os.environ['NO_PROXY'] = '*'

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
import akshare as ak
import pandas as pd
import numpy as np
import requests

try:
    import baostock as bs
    BAOSTOCK_AVAILABLE = True
except ImportError:
    BAOSTOCK_AVAILABLE = False

requests.adapters.DEFAULT_RETRIES = 5

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    stock_code: str
    stock_name: str
    start_date: str
    end_date: str
    initial_cash: float = 100000.0
    strategy_params: Optional[dict] = None


class BacktestResult(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


def get_stock_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取A股历史数据，优先使用akshare，失败则使用baostock"""
    for attempt_source in ['akshare', 'baostock']:
        try:
            if attempt_source == 'akshare':
                symbol = 'sh' + stock_code if stock_code.startswith('6') else 'sz' + stock_code
                df = ak.stock_zh_a_daily(
                    symbol=symbol,
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', ''),
                    adjust="qfq"
                )

                if df is None or df.empty:
                    continue

                df = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
                df = df.sort_values('date').reset_index(drop=True)

                df['open'] = df['open'].astype(float)
                df['close'] = df['close'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['volume'] = df['volume'].astype(float)

                return df

            elif attempt_source == 'baostock' and BAOSTOCK_AVAILABLE:
                lg = bs.login()
                if lg.error_code != '0':
                    continue

                bs_code = 'sh.' + stock_code if stock_code.startswith('6') else 'sz.' + stock_code
                rs = bs.query_history_k_data_plus(
                    bs_code,
                    "date,open,high,low,close,volume",
                    start_date=start_date,
                    end_date=end_date,
                    frequency="d",
                    adjustflag="2"
                )

                data_list = []
                while rs.error_code == '0' and rs.next():
                    data_list.append(rs.get_row_data())
                bs.logout()

                if not data_list:
                    continue

                df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                df = df[df['close'].notna() & (df['close'] != '')]

                if df.empty:
                    continue

                df['open'] = df['open'].astype(float)
                df['close'] = df['close'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['volume'] = df['volume'].astype(float)
                df['date'] = pd.to_datetime(df['date'])

                return df

        except Exception as e:
            print(f"{attempt_source}获取数据失败: {e}, 尝试其他数据源...")
            continue

    print("所有数据源均失败，使用模拟数据")
    return generate_mock_data(stock_code, start_date, end_date)


def generate_mock_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """生成模拟数据用于测试"""
    import random
    from datetime import datetime, timedelta

    random.seed(hash(stock_code) % 10000)

    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    base_price = 50.0
    if stock_code == '600519':
        base_price = 1600.0
    elif stock_code == '000001':
        base_price = 12.0
    elif stock_code == '300750':
        base_price = 180.0

    dates = []
    current_date = start
    while current_date <= end:
        if current_date.weekday() < 5:
            dates.append(current_date)
        current_date += timedelta(days=1)

    data = []
    price = base_price
    for d in dates:
        change = random.uniform(-0.03, 0.035)
        price = price * (1 + change)
        open_price = price * (1 + random.uniform(-0.01, 0.01))
        high_price = max(price, open_price) * (1 + random.uniform(0, 0.02))
        low_price = min(price, open_price) * (1 - random.uniform(0, 0.02))
        volume = random.randint(1000000, 50000000)

        data.append({
            'date': d,
            'open': round(open_price, 2),
            'close': round(price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'volume': volume
        })

    df = pd.DataFrame(data)
    return df


def run_double_ma_backtest(df: pd.DataFrame, initial_cash: float, fast_period: int = 5, slow_period: int = 20):
    """双均线策略回测"""
    df = df.copy()

    df['fast_ma'] = df['close'].rolling(window=fast_period).mean()
    df['slow_ma'] = df['close'].rolling(window=slow_period).mean()

    position = 0
    cash = initial_cash
    trades = []
    equity_curve = []
    holdings = []

    for i in range(slow_period, len(df)):
        date_str = df.iloc[i]['date'].strftime('%Y-%m-%d')
        close = df.iloc[i]['close']
        prev_fast = df.iloc[i-1]['fast_ma']
        prev_slow = df.iloc[i-1]['slow_ma']
        curr_fast = df.iloc[i]['fast_ma']
        curr_slow = df.iloc[i]['slow_ma']

        if pd.isna(curr_fast) or pd.isna(curr_slow):
            equity = cash + position * close
            equity_curve.append({'date': date_str, 'equity': round(equity, 2), 'return_pct': round((equity - initial_cash) / initial_cash * 100, 2)})
            holdings.append({'date': date_str, 'position': position, 'price': close})
            continue

        if prev_fast <= prev_slow and curr_fast > curr_slow and position == 0:
            shares = int(cash / close * 0.95)
            if shares > 0:
                cost = shares * close
                cash -= cost
                position = shares
                trades.append({'date': date_str, 'action': '买入', 'price': close, 'size': shares, 'amount': cost, 'pnl': 0})

        elif prev_fast >= prev_slow and curr_fast < curr_slow and position > 0:
            proceeds = position * close
            cash += proceeds
            trades.append({'date': date_str, 'action': '卖出', 'price': close, 'size': position, 'amount': proceeds, 'pnl': 0})
            position = 0

        equity = cash + position * close
        equity_curve.append({'date': date_str, 'equity': round(equity, 2), 'return_pct': round((equity - initial_cash) / initial_cash * 100, 2)})
        holdings.append({'date': date_str, 'position': position, 'price': close})

    if position > 0:
        final_price = df.iloc[-1]['close']
        proceeds = position * final_price
        cash += proceeds

    final_value = cash

    for trade in trades:
        if trade['action'] == '卖出':
            buy_trade = None
            for t in trades:
                if t['action'] == '买入' and t['date'] <= trade['date'] and t.get('pnl', 0) == 0:
                    buy_trade = t
                    break
            if buy_trade:
                trade['pnl'] = (trade['price'] - buy_trade['price']) * trade['size']

    return final_value, trades, equity_curve


def run_macd_backtest(df: pd.DataFrame, initial_cash: float, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD策略回测"""
    df = df.copy()

    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    df['macd'] = ema_fast - ema_slow
    df['signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
    df['histogram'] = df['macd'] - df['signal']

    position = 0
    cash = initial_cash
    trades = []
    equity_curve = []

    for i in range(35, len(df)):
        date_str = df.iloc[i]['date'].strftime('%Y-%m-%d')
        close = df.iloc[i]['close']
        prev_hist = df.iloc[i-1]['histogram']
        curr_hist = df.iloc[i]['histogram']

        if pd.isna(curr_hist):
            equity = cash + position * close
            equity_curve.append({'date': date_str, 'equity': round(equity, 2), 'return_pct': round((equity - initial_cash) / initial_cash * 100, 2)})
            continue

        if prev_hist <= 0 and curr_hist > 0 and position == 0:
            shares = int(cash / close * 0.95)
            if shares > 0:
                cost = shares * close
                cash -= cost
                position = shares
                trades.append({'date': date_str, 'action': '买入', 'price': close, 'size': shares, 'amount': cost, 'pnl': 0})

        elif prev_hist >= 0 and curr_hist < 0 and position > 0:
            proceeds = position * close
            cash += proceeds
            trades.append({'date': date_str, 'action': '卖出', 'price': close, 'size': position, 'amount': proceeds, 'pnl': 0})
            position = 0

        equity = cash + position * close
        equity_curve.append({'date': date_str, 'equity': round(equity, 2), 'return_pct': round((equity - initial_cash) / initial_cash * 100, 2)})

    if position > 0:
        final_price = df.iloc[-1]['close']
        proceeds = position * final_price
        cash += proceeds

    final_value = cash

    for trade in trades:
        if trade['action'] == '卖出':
            buy_trade = None
            for t in trades:
                if t['action'] == '买入' and t['date'] <= trade['date'] and t.get('pnl', 0) == 0:
                    buy_trade = t
                    break
            if buy_trade:
                trade['pnl'] = (trade['price'] - buy_trade['price']) * trade['size']

    return final_value, trades, equity_curve


def run_rsi_backtest(df: pd.DataFrame, initial_cash: float, period: int = 14, lower: int = 30, upper: int = 70):
    """RSI策略回测"""
    df = df.copy()

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    position = 0
    cash = initial_cash
    trades = []
    equity_curve = []

    for i in range(period + 5, len(df)):
        date_str = df.iloc[i]['date'].strftime('%Y-%m-%d')
        close = df.iloc[i]['close']
        prev_rsi = df.iloc[i-1]['rsi']
        curr_rsi = df.iloc[i]['rsi']

        if pd.isna(curr_rsi):
            equity = cash + position * close
            equity_curve.append({'date': date_str, 'equity': round(equity, 2), 'return_pct': round((equity - initial_cash) / initial_cash * 100, 2)})
            continue

        if prev_rsi < lower and curr_rsi >= lower and position == 0:
            shares = int(cash / close * 0.95)
            if shares > 0:
                cost = shares * close
                cash -= cost
                position = shares
                trades.append({'date': date_str, 'action': '买入', 'price': close, 'size': shares, 'amount': cost, 'pnl': 0})

        elif prev_rsi > upper and curr_rsi <= upper and position > 0:
            proceeds = position * close
            cash += proceeds
            trades.append({'date': date_str, 'action': '卖出', 'price': close, 'size': position, 'amount': proceeds, 'pnl': 0})
            position = 0

        equity = cash + position * close
        equity_curve.append({'date': date_str, 'equity': round(equity, 2), 'return_pct': round((equity - initial_cash) / initial_cash * 100, 2)})

    if position > 0:
        final_price = df.iloc[-1]['close']
        proceeds = position * final_price
        cash += proceeds

    final_value = cash

    for trade in trades:
        if trade['action'] == '卖出':
            buy_trade = None
            for t in trades:
                if t['action'] == '买入' and t['date'] <= trade['date'] and t.get('pnl', 0) == 0:
                    buy_trade = t
                    break
            if buy_trade:
                trade['pnl'] = (trade['price'] - buy_trade['price']) * trade['size']

    return final_value, trades, equity_curve


def calculate_metrics(equity_curve: list, trades: list, initial_cash: float) -> dict:
    """计算回测指标"""
    if not equity_curve or len(equity_curve) < 2:
        return {
            'total_return': 0,
            'annual_return': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'max_drawdown_pct': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_win': 0,
            'avg_loss': 0,
        }

    equity = pd.Series([e['equity'] for e in equity_curve])

    returns = equity.pct_change().dropna()

    total_return = (equity.iloc[-1] - initial_cash) / initial_cash

    days = len(equity_curve)
    years = days / 252
    annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    sharpe_ratio = 0
    if len(returns) > 1 and returns.std() > 0:
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)

    cummax = equity.cummax()
    drawdown = (equity - cummax) / cummax
    max_drawdown = (cummax - equity).max()
    max_drawdown_pct = abs(drawdown.min()) * 100 if drawdown.min() < 0 else 0

    winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
    losing_trades = [t for t in trades if t.get('pnl', 0) < 0]

    win_rate = len(winning_trades) / len(trades) * 100 if trades else 0

    total_wins = sum([t.get('pnl', 0) for t in winning_trades])
    total_losses = abs(sum([t.get('pnl', 0) for t in losing_trades]))
    profit_factor = total_wins / total_losses if total_losses > 0 else 0

    avg_win = total_wins / len(winning_trades) if winning_trades else 0
    avg_loss = total_losses / len(losing_trades) if losing_trades else 0

    return {
        'total_return': round(total_return * 100, 2),
        'annual_return': round(annual_return * 100, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'max_drawdown': round(max_drawdown, 2),
        'max_drawdown_pct': round(max_drawdown_pct, 2),
        'win_rate': round(win_rate, 2),
        'profit_factor': round(profit_factor, 2),
        'total_trades': len(trades),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
    }


@router.post("/run", response_model=BacktestResult)
async def run_backtest(request: BacktestRequest):
    """运行回测"""
    try:
        stock_code = request.stock_code
        start_date = request.start_date
        end_date = request.end_date
        initial_cash = request.initial_cash

        if stock_code == '999999' or not stock_code:
            return BacktestResult(success=False, message="无效的股票代码")

        from datetime import datetime
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        if end_dt < start_dt:
            start_date, end_date = end_date, start_date

        df = get_stock_data(stock_code, start_date, end_date)

        if len(df) < 30:
            raise ValueError(f"数据量太少，需要至少30个交易日，当前{len(df)}个")

        strategy_type = request.strategy_params.get('type', 'double_ma') if request.strategy_params and request.strategy_params.get('type') else 'double_ma'

        if strategy_type == 'macd':
            fast = request.strategy_params.get('period_me1', 12)
            slow = request.strategy_params.get('period_me2', 26)
            signal = request.strategy_params.get('period_signal', 9)
            final_value, trades, equity_curve = run_macd_backtest(df, initial_cash, fast, slow, signal)
        elif strategy_type == 'rsi':
            period = request.strategy_params.get('period', 14)
            lower = request.strategy_params.get('lower', 30)
            upper = request.strategy_params.get('upper', 70)
            final_value, trades, equity_curve = run_rsi_backtest(df, initial_cash, period, lower, upper)
        else:
            fast_period = request.strategy_params.get('fast_period', 5) if request.strategy_params else 5
            slow_period = request.strategy_params.get('slow_period', 20) if request.strategy_params else 20
            final_value, trades, equity_curve = run_double_ma_backtest(df, initial_cash, fast_period, slow_period)

        stats = calculate_metrics(equity_curve, trades, initial_cash)

        return BacktestResult(
            success=True,
            data={
                'stock_code': stock_code,
                'stock_name': request.stock_name,
                'start_date': start_date,
                'end_date': end_date,
                'initial_cash': initial_cash,
                'final_value': round(final_value, 2),
                'stats': stats,
                'equity_curve': equity_curve,
                'trades': trades[:50],
            }
        )

    except Exception as e:
        return BacktestResult(
            success=False,
            message=str(e)
        )


@router.get("/strategies")
async def get_backtest_strategies():
    """获取可用的回测策略"""
    return {
        'strategies': [
            {
                'id': 'double_ma',
                'name': '双均线策略',
                'description': '快速均线上穿慢速均线买入，下穿卖出',
                'params': [
                    {'name': 'fast_period', 'label': '快速均线周期', 'type': 'number', 'default': 5},
                    {'name': 'slow_period', 'label': '慢速均线周期', 'type': 'number', 'default': 20},
                ]
            },
            {
                'id': 'macd',
                'name': 'MACD策略',
                'description': 'MACD金叉买入，死叉卖出',
                'params': [
                    {'name': 'period_me1', 'label': '快线周期', 'type': 'number', 'default': 12},
                    {'name': 'period_me2', 'label': '慢线周期', 'type': 'number', 'default': 26},
                    {'name': 'period_signal', 'label': '信号线周期', 'type': 'number', 'default': 9},
                ]
            },
            {
                'id': 'rsi',
                'name': 'RSI策略',
                'description': 'RSI低于30买入，高于70卖出',
                'params': [
                    {'name': 'period', 'label': 'RSI周期', 'type': 'number', 'default': 14},
                    {'name': 'upper', 'label': '超买阈值', 'type': 'number', 'default': 70},
                    {'name': 'lower', 'label': '超卖阈值', 'type': 'number', 'default': 30},
                ]
            },
        ]
    }


@router.get("/stock-filter")
async def filter_stocks(
    min_volume: float = 100000000,
    max_market_cap: float = 500000000000
):
    """筛选股票：成交量大于指定值，市值小于指定值"""
    import time
    import requests
    
    PROXIES = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
    
    results = []
    data_source = None
    
    # Method 1: Try East Money API directly with proxy
    try:
        session = requests.Session()
        session.proxies = PROXIES
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        
        # Fetch in batches
        for page in range(1, 6):
            url = 'https://push2.eastmoney.com/api/qt/clist/get'
            params = {
                'pn': page,
                'pz': 500,
                'po': 1,
                'np': 1,
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',
                'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
                'fields': 'f2,f3,f12,f14,f84,f116'
            }
            
            resp = session.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('data') and data['data'].get('diff'):
                    batch = data['data']['diff']
                    for s in batch:
                        vol = s.get('f84', 0) or 0
                        cap = s.get('f116', 0) or 0
                        if vol >= min_volume and cap <= max_market_cap:
                            results.append({
                                'code': s.get('f12'),
                                'name': s.get('f14'),
                                'price': s.get('f2'),
                                'change_pct': s.get('f3'),
                                'volume': vol,
                                'volume_display': f"{vol/100000000:.1f}亿",
                                'market_cap': cap,
                                'market_cap_display': f"{cap/100000000:.0f}亿",
                                'turnover_rate': 0,
                            })
                    
                    if len(batch) < 500:
                        break
                else:
                    break
            else:
                break
            
            time.sleep(0.3)
        
        if results:
            data_source = "eastmoney"
            results.sort(key=lambda x: x['volume'], reverse=True)
            results = results[:200]
            
    except Exception as e:
        print(f"East Money API failed: {e}")
    
    # Method 2: Try akshare
    if not results:
        try:
            df = ak.stock_zh_a_spot_em()
            data_source = "akshare"
            
            df = df[['代码', '名称', '最新价', '涨跌幅', '成交量', '总市值']].copy()
            
            def parse_volume(vol):
                if pd.isna(vol):
                    return 0
                if isinstance(vol, (int, float)):
                    return float(vol)
                vol_str = str(vol).strip()
                if '万' in vol_str:
                    return float(vol_str.replace('万', '')) * 10000
                elif '亿' in vol_str:
                    return float(vol_str.replace('亿', '')) * 100000000
                return 0
            
            def parse_market_cap(cap):
                if pd.isna(cap):
                    return 0
                if isinstance(cap, (int, float)):
                    return float(cap)
                cap_str = str(cap).strip()
                if '亿' in cap_str:
                    return float(cap_str.replace('亿', '')) * 100000000
                elif '兆' in cap_str:
                    return float(cap_str.replace('兆', '')) * 1000000000000
                return 0
            
            df['volume_num'] = df['成交量'].apply(parse_volume)
            df['market_cap_num'] = df['总市值'].apply(parse_market_cap)
            
            filtered = df[(df['volume_num'] >= min_volume) & (df['market_cap_num'] <= max_market_cap)]
            filtered = filtered.sort_values('volume_num', ascending=False).head(200)
            
            for _, row in filtered.iterrows():
                results.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': row['最新价'] if pd.notna(row['最新价']) else 0,
                    'change_pct': row['涨跌幅'] if pd.notna(row['涨跌幅']) else 0,
                    'volume': row['volume_num'],
                    'volume_display': row['成交量'],
                    'market_cap': row['market_cap_num'],
                    'market_cap_display': row['总市值'],
                    'turnover_rate': 0,
                })
                
        except Exception as e:
            print(f"akshare failed: {e}")
    
    # If no data source worked, return error
    if not results:
        return {
            "success": False,
            "message": "无法获取实时股票数据，请检查网络连接或代理设置。当前支持 East Money API 和 akshare。",
            "filters": {"min_volume": min_volume, "max_market_cap": max_market_cap},
            "stocks": [],
            "data_source": None
        }
    
    return {
        "success": True,
        "total_count": len(results),
        "filters": {"min_volume": min_volume, "max_market_cap": max_market_cap},
        "stocks": results,
        "data_source": data_source,
        "note": f"数据来源: {data_source}"
    }
