"""
AKShare 接口单元测试
"""
import pytest
from datetime import datetime, timedelta


class TestStockBasic:
    """股票基础接口测试"""

    def test_get_stock_info_a_code_name(self):
        """测试获取股票代码列表"""
        from app.provider.akshare import get_stock_info_a_code_name
        result = get_stock_info_a_code_name()
        assert isinstance(result, list)
        assert len(result) > 0
        # 验证返回数据结构 - Pydantic 对象
        assert hasattr(result[0], 'code')
        assert hasattr(result[0], 'name')

    def test_get_stock_individual_info_em(self):
        """测试获取个股信息"""
        from app.provider.akshare import get_stock_individual_info_em
        result = get_stock_individual_info_em(symbol="000001")
        assert isinstance(result, list)
        assert len(result) > 0
        # 验证返回数据结构 - Pydantic 对象
        assert hasattr(result[0], 'item')
        assert hasattr(result[0], 'value')


class TestLhb:
    """龙虎榜接口测试"""

    def test_get_lhb_detail_em(self):
        """测试获取龙虎榜详情"""
        from app.provider.akshare import get_lhb_detail_em
        # 使用近期的日期
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
        result = get_lhb_detail_em(start_date=start_date, end_date=end_date)
        assert isinstance(result, list)

    def test_get_lhb_yybph_em(self):
        """测试获取营业部排行"""
        from app.provider.akshare import get_lhb_yybph_em
        result = get_lhb_yybph_em(symbol="近一月")
        assert isinstance(result, list)

    def test_get_lhb_stock_statistic_em(self):
        """测试获取个股上榜统计"""
        from app.provider.akshare import get_lhb_stock_statistic_em
        result = get_lhb_stock_statistic_em(symbol="近一月")
        assert isinstance(result, list)


class TestStockKline:
    """历史行情接口测试"""

    def test_get_stock_zh_a_hist(self):
        """测试获取日K线数据"""
        from app.provider.akshare import get_stock_zh_a_hist
        result = get_stock_zh_a_hist(
            symbol="000001",
            start_date="20240101",
            end_date="20240110"
        )
        assert isinstance(result, list)
        # 验证返回数据结构 - Pydantic 对象
        if len(result) > 0:
            assert hasattr(result[0], '日期') or hasattr(result[0], 'date')


class TestStockMinute:
    """分时数据接口测试"""

    def test_get_stock_zh_a_hist_min_em(self):
        """测试获取分时数据"""
        from app.provider.akshare import get_stock_zh_a_hist_min_em
        result = get_stock_zh_a_hist_min_em(
            symbol="000001",
            period="5"
        )
        assert isinstance(result, list)


class TestFundFlow:
    """资金流向接口测试"""

    def test_get_market_fund_flow(self):
        """测试获取大盘资金流向"""
        from app.provider.akshare import get_market_fund_flow
        result = get_market_fund_flow()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_sector_fund_flow_rank(self):
        """测试获取板块资金流排名"""
        from app.provider.akshare import get_sector_fund_flow_rank
        result = get_sector_fund_flow_rank(
            indicator="今日",
            sector_type="行业资金流"
        )
        assert isinstance(result, list)

    def test_get_individual_fund_flow_rank(self):
        """测试获取个股资金流排名"""
        from app.provider.akshare import get_individual_fund_flow_rank
        result = get_individual_fund_flow_rank(indicator="今日")
        assert isinstance(result, list)

    def test_get_individual_fund_flow(self):
        """测试获取个股资金流"""
        from app.provider.akshare import get_individual_fund_flow
        result = get_individual_fund_flow(stock="000001", market="sz")
        assert isinstance(result, list)


class TestZtPool:
    """涨停板接口测试"""

    def test_get_zt_pool_em(self):
        """测试获取涨停股池"""
        from app.provider.akshare import get_zt_pool_em
        # 使用近期日期
        date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        result = get_zt_pool_em(date=date)
        assert isinstance(result, list)

    def test_get_zt_pool_previous_em(self):
        """测试获取昨日涨停股池"""
        from app.provider.akshare import get_zt_pool_previous_em
        date = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")
        result = get_zt_pool_previous_em(date=date)
        assert isinstance(result, list)

    def test_get_zt_pool_dtgc_em(self):
        """测试获取跌停股池"""
        from app.provider.akshare import get_zt_pool_dtgc_em
        date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        result = get_zt_pool_dtgc_em(date=date)
        assert isinstance(result, list)


class TestMargin:
    """融资融券接口测试"""

    def test_get_margin_sse(self):
        """测试获取上交所融资融券"""
        from app.provider.akshare import get_margin_sse
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        result = get_margin_sse(start_date=start_date, end_date=end_date)
        assert isinstance(result, list)

    def test_get_margin_szse(self):
        """测试获取深交所融资融券"""
        from app.provider.akshare import get_margin_szse
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        result = get_margin_szse(start_date=start_date, end_date=end_date)
        assert isinstance(result, list)

    def test_get_margin_account_info(self):
        """测试获取两融账户统计"""
        from app.provider.akshare import get_margin_account_info
        result = get_margin_account_info()
        assert isinstance(result, list)


class TestDzjy:
    """大宗交易接口测试"""

    def test_get_dzjy_mrmx(self):
        """测试获取大宗交易明细"""
        from app.provider.akshare import get_dzjy_mrmx
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
        result = get_dzjy_mrmx(
            symbol="A股",
            start_date=start_date,
            end_date=end_date
        )
        assert isinstance(result, list)

    def test_get_dzjy_mrtj(self):
        """测试获取大宗交易统计"""
        from app.provider.akshare import get_dzjy_mrtj
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
        result = get_dzjy_mrtj(start_date=start_date, end_date=end_date)
        assert isinstance(result, list)


class TestBoard:
    """行业板块接口测试"""

    def test_get_board_concept_name_em(self):
        """测试获取概念板块"""
        from app.provider.akshare import get_board_concept_name_em
        result = get_board_concept_name_em()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_board_industry_name_em(self):
        """测试获取行业板块"""
        from app.provider.akshare import get_board_industry_name_em
        result = get_board_industry_name_em()
        assert isinstance(result, list)
        assert len(result) > 0


class TestHot:
    """热点数据接口测试"""

    def test_get_market_activity_legu(self):
        """测试获取赚钱效应"""
        from app.provider.akshare import get_market_activity_legu
        result = get_market_activity_legu()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_a_high_low_statistics(self):
        """测试获取创新高/新低"""
        from app.provider.akshare import get_a_high_low_statistics
        result = get_a_high_low_statistics(symbol="all")
        assert isinstance(result, list)

    def test_get_hot_rank_em(self):
        """测试获取热度排名"""
        from app.provider.akshare import get_hot_rank_em
        result = get_hot_rank_em()
        assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
