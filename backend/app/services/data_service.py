"""
统一数据服务层
- stock_info, stock_kline, stock_kline_minute: 查询数据库
- 其他方法: 直接调用 provider/akshare 接口
"""
from typing import List, Optional, Any
from datetime import date, datetime, timedelta
import pymysql
from sqlmodel import Session, select

from app.models.stock_info import StockInfo
from app.models.stock_kline import StockKline
from app.models.stock_kline_minute import StockKlineMinute

# astock 数据库连接配置
ASTOCK_DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 13306,
    'user': 'root',
    'password': 'asset123456',
    'database': 'astock',
    'charset': 'utf8mb4'
}


def _get_astock_conn():
    """获取astock数据库连接"""
    return pymysql.connect(**ASTOCK_DB_CONFIG)


class DataService:
    """统一数据服务"""

    # ============ 数据库查询方法 ============

    @staticmethod
    def stock_info(code: str = None, limit: int = 100) -> List[StockInfo]:
        """
        查询股票基本信息

        Args:
            code: 股票代码，不传则返回所有
            limit: 返回数量限制

        Returns:
            股票信息列表
        """
        conn = _get_astock_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        if code:
            cursor.execute("SELECT * FROM stock_info WHERE code = %s LIMIT %s", (code, limit))
        else:
            cursor.execute("SELECT * FROM stock_info LIMIT %s", (limit,))

        results = cursor.fetchall()
        conn.close()

        return [StockInfo(**r) for r in results]

    @staticmethod
    def stock_kline(
        stock_code: str,
        start_date: str = None,
        end_date: str = None,
        limit: int = 1000
    ) -> List[StockKline]:
        """
        查询日K线数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期，格式 YYYYMMDD
            end_date: 结束日期，格式 YYYYMMDD
            limit: 返回数量限制

        Returns:
            K线数据列表
        """
        conn = _get_astock_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        query = "SELECT * FROM stock_kline WHERE stock_code = %s"
        params = [stock_code]

        if start_date:
            query += " AND trade_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND trade_date <= %s"
            params.append(end_date)

        query += " ORDER BY trade_date DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return [StockKline(**r) for r in results]

    @staticmethod
    def stock_kline_minute(
        stock_code: str,
        trade_date: str = None,
        limit: int = 1000
    ) -> List[StockKlineMinute]:
        """
        查询分时数据

        Args:
            stock_code: 股票代码
            trade_date: 交易日期，格式 YYYYMMDD
            limit: 返回数量限制

        Returns:
            分时数据列表
        """
        conn = _get_astock_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        query = "SELECT * FROM stock_kline_minute WHERE stock_code = %s"
        params = [stock_code]

        if trade_date:
            query += " AND trade_date = %s"
            params.append(trade_date)

        query += " ORDER BY time_minute ASC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return [StockKlineMinute(**r) for r in results]

    # ============ AKShare 接口方法 ============

    @staticmethod
    def get_stock_info_a_code_name() -> List[Any]:
        """
        获取股票代码名称映射

        Returns:
            股票代码列表
        """
        from app.provider.akshare import get_stock_info_a_code_name
        return get_stock_info_a_code_name()

    @staticmethod
    def get_stock_individual_info_em(symbol: str) -> List[Any]:
        """
        获取个股基本信息

        Args:
            symbol: 股票代码

        Returns:
            个股信息
        """
        from app.provider.akshare import get_stock_individual_info_em
        return get_stock_individual_info_em(symbol=symbol)

    @staticmethod
    def get_lhb_detail_em(start_date: str, end_date: str) -> List[Any]:
        """
        获取龙虎榜详情

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            龙虎榜详情列表
        """
        from app.provider.akshare import get_lhb_detail_em
        return get_lhb_detail_em(start_date=start_date, end_date=end_date)

    @staticmethod
    def get_lhb_yybph_em(symbol: str = "近一月") -> List[Any]:
        """
        获取营业部排行

        Args:
            symbol: 统计周期

        Returns:
            营业部排行列表
        """
        from app.provider.akshare import get_lhb_yybph_em
        return get_lhb_yybph_em(symbol=symbol)

    @staticmethod
    def get_lhb_stock_statistic_em(symbol: str = "近一月") -> List[Any]:
        """
        获取个股上榜统计

        Args:
            symbol: 统计周期

        Returns:
            个股上榜统计列表
        """
        from app.provider.akshare import get_lhb_stock_statistic_em
        return get_lhb_stock_statistic_em(symbol=symbol)

    @staticmethod
    def get_lhb_stock_detail_em(symbol: str, date: str, flag: str = "买入") -> List[Any]:
        """
        获取个股龙虎榜详情

        Args:
            symbol: 股票代码
            date: 日期
            flag: 类型

        Returns:
            龙虎榜详情列表
        """
        from app.provider.akshare import get_lhb_stock_detail_em
        return get_lhb_stock_detail_em(symbol=symbol, date=date, flag=flag)

    @staticmethod
    def get_stock_zh_a_hist(
        symbol: str,
        start_date: str,
        end_date: str,
        period: str = "daily",
        adjust: str = ""
    ) -> List[Any]:
        """
        获取日K线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 周期
            adjust: 复权类型

        Returns:
            K线数据列表
        """
        from app.provider.akshare import get_stock_zh_a_hist
        return get_stock_zh_a_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust
        )

    @staticmethod
    def get_stock_zh_a_hist_min_em(
        symbol: str,
        period: str = "5",
        start_date: str = None,
        end_date: str = None
    ) -> List[Any]:
        """
        获取分时K线数据

        Args:
            symbol: 股票代码
            period: 周期
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            分时数据列表
        """
        from app.provider.akshare import get_stock_zh_a_hist_min_em
        return get_stock_zh_a_hist_min_em(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    def get_market_fund_flow() -> List[Any]:
        """
        获取大盘资金流向

        Returns:
            资金流向列表
        """
        from app.provider.akshare import get_market_fund_flow
        return get_market_fund_flow()

    @staticmethod
    def get_sector_fund_flow_rank(
        indicator: str = "今日",
        sector_type: str = "行业资金流"
    ) -> List[Any]:
        """
        获取板块资金流排名

        Args:
            indicator: 时间范围
            sector_type: 板块类型

        Returns:
            板块资金流列表
        """
        from app.provider.akshare import get_sector_fund_flow_rank
        return get_sector_fund_flow_rank(indicator=indicator, sector_type=sector_type)

    @staticmethod
    def get_individual_fund_flow_rank(indicator: str = "今日") -> List[Any]:
        """
        获取个股资金流排名

        Args:
            indicator: 时间范围

        Returns:
            个股资金流列表
        """
        from app.provider.akshare import get_individual_fund_flow_rank
        return get_individual_fund_flow_rank(indicator=indicator)

    @staticmethod
    def get_individual_fund_flow(stock: str, market: str = "sz") -> List[Any]:
        """
        获取个股资金流向

        Args:
            stock: 股票代码
            market: 市场

        Returns:
            资金流列表
        """
        from app.provider.akshare import get_individual_fund_flow
        return get_individual_fund_flow(stock=stock, market=market)

    @staticmethod
    def get_zt_pool_em(date: str) -> List[Any]:
        """
        获取涨停股池

        Args:
            date: 日期

        Returns:
            涨停股列表
        """
        from app.provider.akshare import get_zt_pool_em
        return get_zt_pool_em(date=date)

    @staticmethod
    def get_zt_pool_previous_em(date: str) -> List[Any]:
        """
        获取昨日涨停

        Args:
            date: 日期

        Returns:
            昨日涨停列表
        """
        from app.provider.akshare import get_zt_pool_previous_em
        return get_zt_pool_previous_em(date=date)

    @staticmethod
    def get_zt_pool_dtgc_em(date: str) -> List[Any]:
        """
        获取跌停股池

        Args:
            date: 日期

        Returns:
            跌停股列表
        """
        from app.provider.akshare import get_zt_pool_dtgc_em
        return get_zt_pool_dtgc_em(date=date)

    @staticmethod
    def get_zt_pool_zbgc_em(date: str) -> List[Any]:
        """
        获取炸板股池

        Args:
            date: 日期

        Returns:
            炸板股列表
        """
        from app.provider.akshare import get_zt_pool_zbgc_em
        return get_zt_pool_zbgc_em(date=date)

    @staticmethod
    def get_margin_sse(start_date: str, end_date: str) -> List[Any]:
        """
        获取上交所融资融券

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            融资融券列表
        """
        from app.provider.akshare import get_margin_sse
        return get_margin_sse(start_date=start_date, end_date=end_date)

    @staticmethod
    def get_margin_szse(date: str) -> List[Any]:
        """
        获取深交所融资融券

        Args:
            date: 日期

        Returns:
            融资融券列表
        """
        from app.provider.akshare import get_margin_szse
        return get_margin_szse(date=date)

    @staticmethod
    def get_margin_account_info() -> List[Any]:
        """
        获取两融账户统计

        Returns:
            两融账户统计列表
        """
        from app.provider.akshare import get_margin_account_info
        return get_margin_account_info()

    @staticmethod
    def get_dzjy_mrmx(symbol: str, start_date: str, end_date: str) -> List[Any]:
        """
        获取大宗交易明细

        Args:
            symbol: 类型
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            大宗交易列表
        """
        from app.provider.akshare import get_dzjy_mrmx
        return get_dzjy_mrmx(symbol=symbol, start_date=start_date, end_date=end_date)

    @staticmethod
    def get_dzjy_mrtj(start_date: str, end_date: str) -> List[Any]:
        """
        获取大宗交易统计

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            大宗交易统计列表
        """
        from app.provider.akshare import get_dzjy_mrtj
        return get_dzjy_mrtj(start_date=start_date, end_date=end_date)

    @staticmethod
    def get_market_activity_legu() -> List[Any]:
        """
        获取赚钱效应分析

        Returns:
            赚钱效应列表
        """
        from app.provider.akshare import get_market_activity_legu
        return get_market_activity_legu()

    @staticmethod
    def get_a_high_low_statistics(symbol: str = "all") -> List[Any]:
        """
        获取创新高/新低

        Args:
            symbol: 市场

        Returns:
            创新高/新低列表
        """
        from app.provider.akshare import get_a_high_low_statistics
        return get_a_high_low_statistics(symbol=symbol)

    @staticmethod
    def get_hot_rank_em() -> List[Any]:
        """
        获取股票热度排名

        Returns:
            热度排名列表
        """
        from app.provider.akshare import get_hot_rank_em
        return get_hot_rank_em()
