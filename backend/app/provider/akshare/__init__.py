# AKShare 数据接口提供者
# 股票基础
from app.provider.akshare.stock_basic import (
    get_stock_info_a_code_name,
    get_stock_individual_info_em,
)

# 龙虎榜
from app.provider.akshare.lhb import (
    get_lhb_detail_em,
    get_lhb_yybph_em,
    get_lhb_stock_statistic_em,
    get_lhb_stock_detail_em,
)

# 历史行情
from app.provider.akshare.stock_kline import (
    get_stock_zh_a_hist,
)

# 分时数据
from app.provider.akshare.stock_minute import (
    get_stock_zh_a_hist_min_em,
)

# 资金流向
from app.provider.akshare.fund_flow import (
    get_market_fund_flow,
    get_sector_fund_flow_rank,
    get_individual_fund_flow_rank,
    get_individual_fund_flow,
)

# 涨停板
from app.provider.akshare.zt_pool import (
    get_zt_pool_em,
    get_zt_pool_previous_em,
    get_zt_pool_dtgc_em,
    get_zt_pool_zbgc_em,
)

# 融资融券
from app.provider.akshare.margin import (
    get_margin_sse,
    get_margin_szse,
    get_margin_account_info,
)

# 大宗交易
from app.provider.akshare.dzjy import (
    get_dzjy_mrmx,
    get_dzjy_mrtj,
)

# 热点数据
from app.provider.akshare.hot import (
    get_market_activity_legu,
    get_a_high_low_statistics,
    get_hot_rank_em,
)

__all__ = [
    # 股票基础
    "get_stock_info_a_code_name",
    "get_stock_individual_info_em",
    # 龙虎榜
    "get_lhb_detail_em",
    "get_lhb_yybph_em",
    "get_lhb_stock_statistic_em",
    "get_lhb_stock_detail_em",
    # 历史行情
    "get_stock_zh_a_hist",
    # 分时数据
    "get_stock_zh_a_hist_min_em",
    # 资金流向
    "get_market_fund_flow",
    "get_sector_fund_flow_rank",
    "get_individual_fund_flow_rank",
    "get_individual_fund_flow",
    # 涨停板
    "get_zt_pool_em",
    "get_zt_pool_previous_em",
    "get_zt_pool_dtgc_em",
    "get_zt_pool_zbgc_em",
    # 融资融券
    "get_margin_sse",
    "get_margin_szse",
    "get_margin_account_info",
    # 大宗交易
    "get_dzjy_mrmx",
    "get_dzjy_mrtj",
    # 热点数据
    "get_market_activity_legu",
    "get_a_high_low_statistics",
    "get_hot_rank_em",
]
