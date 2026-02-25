#!/usr/bin/env python3
"""
策略初始化脚本
创建经过验证的游资策略
"""
import urllib.request
import json
import ssl

API_URL = "http://localhost:8000/api/strategies"

# 经过验证的游资策略
STRATEGIES = [
    {
        "name": "龙头战法",
        "description": "赵老哥风格 - 只做市场最高板，二板定龙头，三板成妖。适合情绪发酵期和高潮期。",
        "trade_mode": "打板",
        "mode_description": "只做市场最高板，二板接力或三板确认，龙头战法核心是买在分歧卖在一致",
        "position_rising": 60.0,
        "position_consolidation": 30.0,
        "position_decline": 0.0,
        "position_chaos": 20.0,
        "stock_selection_logic": "1.必须是主流板块的龙头股 2.板块内涨停数量最多 3.有游资席位买入配合 4.市场最高连板",
        "watch_signals": "龙头,连板,最高板,主流板块",
        "entry_condition": "1.涨停瞬间买入 2.换手率5-15% 3.封板时间越早越好 4.板块效应强",
        "timing_pattern": "打板",
        "exit_condition": "1.次日不涨停卖出 2.跌破5日线卖出 3.出现明显头部形态卖出",
        "position_condition": "1.龙头断板立即卖出 2.板块退潮立即卖出",
        "min_turnover_rate": 5.0,
        "max_turnover_rate": 15.0,
        "min_volume_ratio": 2.0,
        "min_market_cap": 30.0,
        "max_market_cap": 300.0,
        "min_price": 5.0,
        "max_price": 80.0,
        "limit_up_days": 2,
        "min_amplitude": 5.0,
        "max_amplitude": 12.0,
        "min_consecutive_limit": 2,
        "min_circulating_market_cap": 30.0,
        "max_circulating_market_cap": 200.0,
        "sentiment_cycle": "发酵期,高潮期",
        "market_condition": "上升周期",
        "take_profit_1": 7.0,
        "take_profit_2": 15.0,
        "trailing_stop": 5.0,
        "max_daily_loss": -5.0,
        "stop_loss": -6.0,
        "position_size": 20.0,
        "max_positions": 3,
        "min_single_position": 10.0,
        "max_single_position": 25.0,
        "win_rate_target": 40.0,
        "discipline": {
            "only_mode": True,
            "no_forcing": True,
            "cut_loss": True,
            "ignore_rumors": True,
            "stay_focused": True,
            "notes": "只做最高板，不做跟风，不做杂毛"
        }
    },
    {
        "name": "首板战法",
        "description": "打首板模式 - 板块内首个涨停股，讲究板块效应和换手充分。适合启动期和发酵期。",
        "trade_mode": "打板",
        "mode_description": "只做板块内第一个涨停的股票，需要板块内至少3只以上涨停配合",
        "position_rising": 50.0,
        "position_consolidation": 40.0,
        "position_decline": 0.0,
        "position_chaos": 20.0,
        "stock_selection_logic": "1.板块首次涨停 2.换手充分3-10% 3.量比1.5以上 4.流通市值50-200亿",
        "watch_signals": "首板,板块效应,换手充分",
        "entry_condition": "1.涨停瞬间买入 2.换手率3-10% 3.量比>1.5 4.板块有3只以上涨停",
        "timing_pattern": "打板",
        "exit_condition": "1.次日不涨停卖出 2.跌破前一日涨停价卖出 3.炸板立即卖出",
        "position_condition": "1.板块效应消失卖出 2.出现亏钱效应卖出",
        "min_turnover_rate": 3.0,
        "max_turnover_rate": 10.0,
        "min_volume_ratio": 1.5,
        "min_market_cap": 50.0,
        "max_market_cap": 200.0,
        "min_price": 5.0,
        "max_price": 50.0,
        "limit_up_days": 1,
        "min_amplitude": 5.0,
        "max_amplitude": 10.0,
        "min_consecutive_limit": 1,
        "min_circulating_market_cap": 50.0,
        "max_circulating_market_cap": 200.0,
        "sentiment_cycle": "启动期,发酵期",
        "market_condition": "上升周期,震荡周期",
        "take_profit_1": 5.0,
        "take_profit_2": 10.0,
        "trailing_stop": 3.0,
        "max_daily_loss": -4.0,
        "stop_loss": -5.0,
        "position_size": 15.0,
        "max_positions": 3,
        "min_single_position": 8.0,
        "max_single_position": 20.0,
        "win_rate_target": 35.0,
        "discipline": {
            "only_mode": True,
            "no_forcing": True,
            "cut_loss": True,
            "ignore_rumors": True,
            "stay_focused": True,
            "notes": "只做首板，不做二板以上的接力"
        }
    },
    {
        "name": "低吸战法",
        "description": "乔帮主风格 - 强势股回调到均线支撑处低吸，讲究均线支撑和缩量企稳。",
        "trade_mode": "低吸",
        "mode_description": "强势股回调到重要均线（10日/20日均线）处低吸，反弹卖出",
        "position_rising": 40.0,
        "position_consolidation": 50.0,
        "position_decline": 10.0,
        "position_chaos": 30.0,
        "stock_selection_logic": "1.前期有过涨停 2.回调到重要均线 3.缩量企稳 4.有题材支撑",
        "watch_signals": "回调,均线支撑,缩量,强势股",
        "entry_condition": "1.回调到10日/20日均线 2.缩量企稳（量比<1） 3.有止跌信号",
        "timing_pattern": "低吸",
        "exit_condition": "1.达到5%止盈 2.跌破均线止损 3.出现放量下跌卖出",
        "position_condition": "1.跌破20日线必须卖出 2.放量下跌必须卖出",
        "min_turnover_rate": 1.0,
        "max_turnover_rate": 5.0,
        "min_volume_ratio": 0.5,
        "max_volume_ratio": 1.0,
        "min_market_cap": 20.0,
        "max_market_cap": 500.0,
        "min_price": 5.0,
        "max_price": 100.0,
        "limit_up_days": 1,
        "min_amplitude": 3.0,
        "max_amplitude": 8.0,
        "ma_days": "10,20,60",
        "min_circulating_market_cap": 20.0,
        "max_circulating_market_cap": 300.0,
        "sentiment_cycle": "启动期,发酵期,混沌期",
        "market_condition": "震荡周期",
        "take_profit_1": 5.0,
        "take_profit_2": 10.0,
        "trailing_stop": 3.0,
        "max_daily_loss": -3.0,
        "stop_loss": -5.0,
        "position_size": 20.0,
        "max_positions": 3,
        "min_single_position": 10.0,
        "max_single_position": 25.0,
        "win_rate_target": 50.0,
        "discipline": {
            "only_mode": True,
            "no_forcing": True,
            "cut_loss": True,
            "ignore_rumors": True,
            "stay_focused": True,
            "notes": "只低吸回调股，不追涨"
        }
    },
    {
        "name": "竞价战法",
        "description": "炒股养家风格 - 集合竞价买入，看好的股票直接竞价挂单。适合龙头股的一字板抢筹。",
        "trade_mode": "竞价",
        "mode_description": "集合竞价阶段直接挂单买入，看好直接上，不犹豫",
        "position_rising": 50.0,
        "position_consolidation": 30.0,
        "position_decline": 0.0,
        "position_chaos": 20.0,
        "stock_selection_logic": "1.必须是龙头股或有龙头潜力 2.板块效应明显 3.有重大利好或题材 4.市场情绪好",
        "watch_signals": "竞价,抢筹,龙头,利好",
        "entry_condition": "1.高开3-7% 2.竞价量价配合 3.板块效应强 4.有抢筹迹象",
        "timing_pattern": "竞价",
        "exit_condition": "1.次日不涨停卖出 2.跌破开盘价卖出 3.出现放量长上影卖出",
        "position_condition": "1.竞价不及预期立即放弃 2.板块退潮立即卖出",
        "min_turnover_rate": 2.0,
        "max_turnover_rate": 8.0,
        "min_volume_ratio": 1.5,
        "min_market_cap": 30.0,
        "max_market_cap": 300.0,
        "min_price": 5.0,
        "max_price": 80.0,
        "limit_up_days": 1,
        "min_amplitude": 3.0,
        "max_amplitude": 10.0,
        "min_consecutive_limit": 1,
        "min_circulating_market_cap": 30.0,
        "max_circulating_market_cap": 200.0,
        "sentiment_cycle": "启动期,发酵期,高潮期",
        "market_condition": "上升周期",
        "take_profit_1": 5.0,
        "take_profit_2": 10.0,
        "trailing_stop": 3.0,
        "max_daily_loss": -4.0,
        "stop_loss": -5.0,
        "position_size": 20.0,
        "max_positions": 3,
        "min_single_position": 10.0,
        "max_single_position": 30.0,
        "win_rate_target": 45.0,
        "discipline": {
            "only_mode": True,
            "no_forcing": True,
            "cut_loss": True,
            "ignore_rumors": True,
            "stay_focused": True,
            "notes": "竞价要果断，不符合预期立即撤单"
        }
    },
    {
        "name": "趋势低吸",
        "description": "趋势股低吸模式 - 沿着20日均线上涨的趋势股，回调到均线处低吸。适合趋势行情。",
        "trade_mode": "低吸",
        "mode_description": "趋势股回调到20日均线处低吸，沿着5日线持有，跌破20日线卖出",
        "position_rising": 50.0,
        "position_consolidation": 40.0,
        "position_decline": 10.0,
        "position_chaos": 20.0,
        "stock_selection_logic": "1.20日均线向上 2.涨幅超过30% 3.有板块效应 4.基本面有支撑",
        "watch_signals": "趋势,回调,均线支撑,20日线",
        "entry_condition": "1.回调到20日均线 2.缩量企稳 3.有止跌信号 4.均线向上",
        "timing_pattern": "低吸",
        "exit_condition": "1.跌破20日线卖出 2.达到20%止盈 3.放量跌破5日线卖出",
        "position_condition": "1.跌破20日线必须卖出 2.出现明显头部卖出",
        "min_turnover_rate": 1.0,
        "max_turnover_rate": 8.0,
        "min_volume_ratio": 0.5,
        "max_volume_ratio": 1.5,
        "min_market_cap": 50.0,
        "max_market_cap": 1000.0,
        "min_price": 10.0,
        "max_price": 200.0,
        "limit_up_days": 0,
        "min_amplitude": 3.0,
        "max_amplitude": 10.0,
        "ma_days": "5,20,60",
        "min_circulating_market_cap": 50.0,
        "max_circulating_market_cap": 800.0,
        "sentiment_cycle": "发酵期,高潮期,混沌期",
        "market_condition": "上升周期,震荡周期",
        "take_profit_1": 10.0,
        "take_profit_2": 20.0,
        "trailing_stop": 8.0,
        "max_daily_loss": -5.0,
        "stop_loss": -7.0,
        "position_size": 25.0,
        "max_positions": 3,
        "min_single_position": 15.0,
        "max_single_position": 30.0,
        "win_rate_target": 55.0,
        "discipline": {
            "only_mode": True,
            "no_forcing": True,
            "cut_loss": True,
            "ignore_rumors": True,
            "stay_focused": True,
            "notes": "只做上升趋势，跌破20日线无条件卖出"
        }
    },
    {
        "name": "反包战法",
        "description": "涨停次日反包模式 - 前一天涨停被砸，次日反包涨停的股票。讲究N型反包形态。",
        "trade_mode": "半路",
        "mode_description": "前日炸板或冲高回落，次日反包涨停买入，是强势股的一种介入方式",
        "position_rising": 40.0,
        "position_consolidation": 30.0,
        "position_decline": 0.0,
        "position_chaos": 15.0,
        "stock_selection_logic": "1.前一天炸板或冲高回落 2.有板块效应 3.有资金回流 4.形态保持完好",
        "watch_signals": "反包,N型,炸板,资金回流",
        "entry_condition": "1.竞价高开或平开 2.快速拉升 3.突破前一天高点 4.换手充分",
        "timing_pattern": "半路",
        "exit_condition": "1.次日不涨停卖出 2.跌破反包阳线实体 3.出现放量长上影",
        "position_condition": "1.反包失败立即卖出 2.板块退潮卖出",
        "min_turnover_rate": 3.0,
        "max_turnover_rate": 12.0,
        "min_volume_ratio": 2.0,
        "min_market_cap": 30.0,
        "max_market_cap": 200.0,
        "min_price": 5.0,
        "max_price": 60.0,
        "limit_up_days": 1,
        "min_amplitude": 8.0,
        "max_amplitude": 15.0,
        "min_consecutive_limit": 1,
        "min_circulating_market_cap": 30.0,
        "max_circulating_market_cap": 150.0,
        "sentiment_cycle": "发酵期,高潮期",
        "market_condition": "上升周期",
        "take_profit_1": 7.0,
        "take_profit_2": 15.0,
        "trailing_stop": 5.0,
        "max_daily_loss": -5.0,
        "stop_loss": -6.0,
        "position_size": 15.0,
        "max_positions": 2,
        "min_single_position": 8.0,
        "max_single_position": 20.0,
        "win_rate_target": 35.0,
        "discipline": {
            "only_mode": True,
            "no_forcing": True,
            "cut_loss": True,
            "ignore_rumors": True,
            "stay_focused": True,
            "notes": "只做强势股反包，不做弱势股"
        }
    }
]


def make_request(method, url, data=None):
    """发送HTTP请求"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {"Content-Type": "application/json"}

    if method == "GET":
        req = urllib.request.Request(url, headers=headers)
    else:
        json_data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=json_data, headers=headers)
        req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, context=ctx) as response:
        return json.loads(response.read().decode())


def main():
    # 1. 获取现有策略
    print("=" * 50)
    print("获取现有策略...")
    try:
        existing = make_request("GET", API_URL)
        print(f"现有策略数量: {len(existing)}")

        # 2. 删除现有策略
        print("\n删除现有策略...")
        for s in existing:
            delete_url = f"{API_URL}/{s['id']}"
            try:
                # DELETE方法
                req = urllib.request.Request(delete_url, method='DELETE')
                with urllib.request.urlopen(req, context=ctx) as response:
                    print(f"  - 删除: {s['name']}")
            except Exception as e:
                print(f"  - 删除失败: {s['name']} - {e}")
    except Exception as e:
        print(f"获取策略失败: {e}")

    # 3. 创建新策略
    print("\n创建新策略...")
    for strategy in STRATEGIES:
        result = make_request("POST", API_URL, strategy)
        print(f"  + 创建: {result['name']} (ID: {result['id']})")

    print("\n" + "=" * 50)
    print("策略初始化完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
