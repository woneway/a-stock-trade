"""
游资常用数据服务
- 优先查询本地数据库
- 本地无数据或过期时调用 akshare 并自动存储
- 支持数据血缘追踪
"""
import hashlib
from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List
import pandas as pd
import logging
from sqlmodel import Session, select, delete, func

from app.database import engine
from app.models.data_lineage import DataLineage
from app.models.external_yz_common import (
    ExternalStockSpot,
    ExternalLimitUp,
    ExternalZtPool,
    ExternalIndividualFundFlow,
    ExternalSectorFundFlow,
    ExternalLhbDetail,
    ExternalLhbYytj,
    ExternalLhbYyb,
)

logger = logging.getLogger(__name__)


class CacheService:
    """通用数据缓存服务 - 支持本地缓存和数据血缘追踪"""

    # 缓存有效期（秒）
    SPOT_CACHE_TTL = 60        # 实时行情 60秒
    LIMIT_UP_CACHE_TTL = 300   # 涨停板 5分钟
    FUND_FLOW_CACHE_TTL = 300  # 资金流向 5分钟
    LHB_CACHE_TTL = 600        # 龙虎榜 10分钟

    # ==================== 通用缓存方法 ====================

    # 函数名到方法的映射
    QUERY_METHODS = {
        "stock_zh_a_spot_em": "_get_spot_from_local",
        "stock_zh_a_limit_up_em": "_get_limit_up_from_local",
        "stock_zt_pool_em": "_get_zt_pool_from_local",
        "stock_individual_fund_flow": "_get_fund_flow_from_local",
        "stock_sector_fund_flow_rank": "_get_sector_fund_flow_from_local",
        "stock_lhb_detail_em": "_get_lhb_detail_from_local",
        "stock_lhb_yytj_sina": "_get_lhb_yytj_from_local",
        "stock_lh_yyb_most": "_get_lhb_yyb_from_local",
    }

    SAVE_METHODS = {
        "stock_zh_a_spot_em": "_save_spot_to_local",
        "stock_zh_a_limit_up_em": "_save_limit_up_to_local",
        "stock_zt_pool_em": "_save_zt_pool_to_local",
        "stock_individual_fund_flow": "_save_fund_flow_to_local",
        "stock_sector_fund_flow_rank": "_save_sector_fund_flow_to_local",
        "stock_lhb_detail_em": "_save_lhb_detail_to_local",
        "stock_lhb_yytj_sina": "_save_lhb_yytj_to_local",
        "stock_lh_yyb_most": "_save_lhb_yyb_to_local",
    }

    # ==================== 接口配置 ====================
    # query_type 说明:
    # - realtime: 实时行情，每次都从 akshare 获取
    # - date: 按日期查询，需要 date 参数
    # - stock: 按股票查询，需要 stock 参数
    # - params: 自定义参数组合查询
    # - date_range: 日期范围查询
    # - latest: 无参数，返回最新一次数据
    CACHE_CONFIG = {
        "stock_zh_a_spot_em": {
            "model": ExternalStockSpot,
            "sync": False,
            "query_type": "realtime",
        },
        "stock_zh_a_limit_up_em": {
            "model": ExternalLimitUp,
            "sync": True,
            "query_type": "date",
            "date_param": "date",
        },
        "stock_zt_pool_em": {
            "model": ExternalZtPool,
            "sync": True,
            "query_type": "date",
            "date_param": "date",
        },
        "stock_individual_fund_flow": {
            "model": ExternalIndividualFundFlow,
            "sync": True,
            "query_type": "stock",
            "stock_param": "stock",
        },
        "stock_sector_fund_flow_rank": {
            "model": ExternalSectorFundFlow,
            "sync": True,
            "query_type": "params",
            "params": ["indicator", "sector_type"],
        },
        "stock_lhb_detail_em": {
            "model": ExternalLhbDetail,
            "sync": True,
            "query_type": "date_range",
            "date_params": ["start_date", "end_date"],
        },
        "stock_lhb_yytj_sina": {
            "model": ExternalLhbYytj,
            "sync": True,
            "query_type": "latest",
        },
        "stock_lh_yyb_most": {
            "model": ExternalLhbYyb,
            "sync": True,
            "query_type": "latest",
        },
    }

    # 字段中文映射
    COLUMN_ALIASES = {
        "stock_lh_yyb_most": {
            "broker_name": "营业部名称",
            "trade_date": "交易日期",
            "up_count": "上榜次数",
            "buy_count": "买入次数",
            "sell_count": "卖出次数",
            "buy_amount": "买入金额",
            "sell_amount": "卖出金额",
            "net_amount": "净买入金额",
            "win_rate": "胜率",
        },
        "stock_zh_a_limit_up_em": {
            "code": "代码",
            "name": "名称",
            "close_price": "收盘价",
            "change_pct": "涨跌幅",
            "reason": "涨停原因",
            "seal_amount": "封单金额",
            "seal_ratio": "封比",
            "open_count": "打开次数",
            "first_time": "首次涨停时间",
            "last_time": "最后涨停时间",
            "turnover_rate": "换手率",
            "market_cap": "总市值",
        },
        "stock_zt_pool_em": {
            "code": "代码",
            "name": "名称",
            "close_price": "收盘价",
            "change_pct": "涨跌幅",
            "reason": "涨停原因",
            "first_time": "首次涨停时间",
            "seal_amount": "封单金额",
            "turnover_rate": "换手率",
        },
        "stock_individual_fund_flow": {
            "code": "代码",
            "name": "名称",
            "trade_date": "日期",
            "net_main": "主力净流入",
            "net_super": "超大单净流入",
            "net_big": "大单净流入",
            "net_mid": "中单净流入",
            "net_small": "小单净流入",
            "ratio_main": "主力净流入占比",
        },
        "stock_sector_fund_flow_rank": {
            "sector_name": "板块名称",
            "trade_date": "交易日期",
            "net_inflow": "主力净流入",
            "change_pct": "涨跌幅",
            "turnover_rate": "换手率",
            "amount": "成交额",
            "rank": "排名",
        },
        "stock_lhb_detail_em": {
            "code": "代码",
            "name": "名称",
            "trade_date": "日期",
            "list_type": "上榜原因",
            "buy_amount": "龙虎榜买入金额",
            "sell_amount": "龙虎榜卖出金额",
            "net_amount": "龙虎榜净买入额",
        },
        "stock_lhb_yytj_sina": {
            "trader_name": "游资名称",
            "trade_date": "交易日期",
            "buy_count": "买入次数",
            "buy_amount": "买入金额",
            "buy_avg": "平均买入金额",
            "sell_count": "卖出次数",
            "sell_amount": "卖出金额",
        },
        "stock_zh_a_spot_em": {
            "code": "代码",
            "name": "名称",
            "latest_price": "最新价",
            "change": "涨跌额",
            "pct_chg": "涨跌幅",
            "volume": "成交量",
            "amount": "成交额",
            "amplitude": "振幅",
            "high": "最高",
            "low": "最低",
            "open_price": "今开",
            "pre_close": "昨收",
            "volume_ratio": "量比",
            "turnover_rate": "换手率",
            "pe": "市盈率",
            "pb": "市净率",
            "market_cap": "总市值",
            "circ_market_cap": "流通市值",
        },
    }

    @staticmethod
    def _get_column_aliases(func_name: str) -> Dict[str, str]:
        """获取字段中文映射"""
        return CacheService.COLUMN_ALIASES.get(func_name, {})

    # ==================== 数据血缘方法 ====================

    @staticmethod
    def _compute_params_hash(params: dict) -> str:
        """计算参数哈希"""
        # 将参数转换为字符串并排序，确保相同参数产生相同哈希
        param_str = "".join(f"{k}={v}" for k, v in sorted(params.items()))
        return hashlib.md5(param_str.encode()).hexdigest()[:16]

    @staticmethod
    def _get_lineage(func_name: str, params: dict) -> Optional[DataLineage]:
        """获取数据血缘记录"""
        params_hash = CacheService._compute_params_hash(params)
        with Session(engine) as session:
            lineage = session.exec(
                select(DataLineage).where(
                    DataLineage.func_name == func_name,
                    DataLineage.params_hash == params_hash,
                )
            ).first()
            return lineage

    @staticmethod
    def _update_lineage(
        func_name: str,
        params: dict,
        source: str,
        record_count: int,
    ):
        """更新数据血缘记录"""
        params_hash = CacheService._compute_params_hash(params)
        now = datetime.now()

        with Session(engine) as session:
            # 查找现有记录
            lineage = session.exec(
                select(DataLineage).where(
                    DataLineage.func_name == func_name,
                    DataLineage.params_hash == params_hash,
                )
            ).first()

            if lineage:
                # 更新现有记录
                lineage.source = source
                lineage.last_updated = now
                lineage.record_count = record_count
            else:
                # 创建新记录
                lineage = DataLineage(
                    func_name=func_name,
                    params_hash=params_hash,
                    source=source,
                    last_updated=now,
                    record_count=record_count,
                )
                session.add(lineage)

            session.commit()

    @staticmethod
    def get_lineage_info(func_name: str, params: dict) -> Dict[str, Any]:
        """获取数据血缘信息"""
        lineage = CacheService._get_lineage(func_name, params)
        if lineage:
            return {
                "func_name": lineage.func_name,
                "source": lineage.source,
                "last_updated": lineage.last_updated.isoformat() if lineage.last_updated else None,
                "record_count": lineage.record_count,
            }
        return {
            "func_name": func_name,
            "source": "unknown",
            "last_updated": None,
            "record_count": 0,
        }

    @staticmethod
    def _convert_to_chinese(data: List[Dict], func_name: str) -> Dict:
        """将数据转换为中文列名"""
        if not data:
            return {"data": data, "columns": []}

        column_aliases = CacheService._get_column_aliases(func_name)

        if column_aliases:
            # 转换 columns 为中文
            columns = [column_aliases.get(col, col) for col in data[0].keys()]
            # 转换每条数据
            converted_data = []
            for row in data:
                converted_row = {column_aliases.get(k, k): v for k, v in row.items()}
                converted_data.append(converted_row)
            return {"data": converted_data, "columns": columns}

        # 没有映射则使用原始列名
        columns = list(data[0].keys()) if data else []
        return {"data": data, "columns": columns}

    @staticmethod
    def query_from_local(func_name: str, params: dict) -> Optional[Dict]:
        """从本地查询数据，返回 {data, columns} 格式"""
        # 获取接口配置
        config = CacheService.CACHE_CONFIG.get(func_name)
        if not config:
            return None

        query_type = config.get("query_type")
        method_name = CacheService.QUERY_METHODS.get(func_name)
        if not method_name:
            return None

        method = getattr(CacheService, method_name, None)
        if not method:
            return None

        # 根据 query_type 调用不同的查询方法
        if query_type == "date":
            # 按日期查询
            date_param = config.get("date_param", "date")
            target_date = params.get(date_param)
            if target_date:
                target_date = datetime.strptime(target_date, "%Y%m%d").date()
            else:
                target_date = date.today()
            data = method(target_date)

        elif query_type == "stock":
            # 按股票查询
            stock_param = config.get("stock_param", "stock")
            stock_code = params.get(stock_param)
            if not stock_code:
                # 需要股票代码才能查询
                return None
            data = method(stock_code)

        elif query_type == "params":
            # 自定义参数组合
            query_params = config.get("params", [])
            query_args = [params.get(p) for p in query_params]
            data = method(*query_args) if all(query_args) else None

        elif query_type == "date_range":
            # 日期范围查询 - 返回最新数据
            data = method()

        elif query_type == "latest":
            # 无参数，返回最新数据
            data = method()

        elif query_type == "realtime":
            # 实时行情不缓存
            return None

        else:
            data = method()

        if not data:
            return None

        # 记录数据血缘 - 来自缓存
        record_count = len(data) if data else 0
        CacheService._update_lineage(func_name, params, "cache", record_count)

        # 获取字段中文映射并转换
        return CacheService._convert_to_chinese(data, func_name)

    @staticmethod
    def save_to_local(func_name: str, params: dict, result: dict):
        """保存数据到本地"""
        # 获取接口配置
        config = CacheService.CACHE_CONFIG.get(func_name)
        if not config or not config.get("sync"):
            return

        method_name = CacheService.SAVE_METHODS.get(func_name)
        if not method_name:
            return

        method = getattr(CacheService, method_name, None)
        if not method:
            return

        # 获取数据
        data = result.get("data", [])
        if not data:
            return

        df = pd.DataFrame(data)

        query_type = config.get("query_type")

        # 根据 query_type 调用不同的保存方法
        if query_type == "date":
            date_param = config.get("date_param", "date")
            target_date = params.get(date_param)
            if target_date:
                target_date = datetime.strptime(target_date, "%Y%m%d").date()
            else:
                target_date = date.today()
            method(df, target_date)

        elif query_type == "stock":
            stock_param = config.get("stock_param", "stock")
            stock_code = params.get(stock_param)
            if stock_code:
                method(df, stock_code)

        elif query_type == "params":
            query_params = config.get("params", [])
            query_args = [params.get(p) for p in query_params]
            method(df, *query_args) if all(query_args) else None

        elif query_type in ["date_range", "latest"]:
            # 日期范围或最新数据，直接保存
            method(df)

        # 记录数据血缘 - 来自 akshare
        record_count = len(data) if data else 0
        CacheService._update_lineage(func_name, params, "akshare", record_count)

    # ==================== A股实时行情 ====================

    @staticmethod
    def get_stock_spot(force_refresh: bool = False) -> List[Dict]:
        """获取A股实时行情 - 优先本地"""
        # 尝试从本地获取
        if not force_refresh:
            local_data = CacheService._get_spot_from_local()
            if local_data:
                logger.info(f"从本地获取实时行情 {len(local_data)} 条")
                return local_data

        # 从 akshare 获取并存储
        df = CacheService._fetch_spot_from_akshare()
        if df is None or df.empty:
            return []

        # 存储到本地
        CacheService._save_spot_to_local(df)
        return CacheService._convert_df_to_records(df)

    @staticmethod
    def _get_spot_from_local() -> Optional[List[Dict]]:
        """从本地获取实时行情"""
        try:
            with Session(engine) as session:
                # 获取最新交易日期的数据
                latest_date = session.exec(
                    select(ExternalStockSpot.trade_date)
                    .order_by(ExternalStockSpot.trade_date.desc())
                    .limit(1)
                ).first()

                if not latest_date:
                    return None

                # 检查是否在缓存时间内
                records = session.exec(
                    select(ExternalStockSpot).where(
                        ExternalStockSpot.trade_date == latest_date
                    )
                ).all()

                if records:
                    return [r.model_dump() for r in records]
        except Exception as e:
            logger.warning(f"从本地获取实时行情失败: {e}")
        return None

    @staticmethod
    def _fetch_spot_from_akshare() -> Optional[pd.DataFrame]:
        """从 akshare 获取实时行情"""
        import akshare as ak
        try:
            df = ak.stock_zh_a_spot_em()
            return df
        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return None

    @staticmethod
    def _save_spot_to_local(df: pd.DataFrame):
        """保存实时行情到本地"""
        try:
            trade_date = date.today()
            with Session(engine) as session:
                # 清空当日旧数据
                session.exec(
                    delete(ExternalStockSpot).where(
                        ExternalStockSpot.trade_date == trade_date
                    )
                )

                for _, row in df.iterrows():
                    record = ExternalStockSpot(
                        trade_date=trade_date,
                        code=str(row.get('代码', '')),
                        name=str(row.get('名称', '')),
                        latest_price=float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else None,
                        change=float(row.get('涨跌额', 0)) if pd.notna(row.get('涨跌额')) else None,
                        pct_chg=float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else None,
                        volume=float(row.get('成交量', 0)) if pd.notna(row.get('成交量')) else None,
                        amount=float(row.get('成交额', 0)) if pd.notna(row.get('成交额')) else None,
                        amplitude=float(row.get('振幅', 0)) if pd.notna(row.get('振幅')) else None,
                        high=float(row.get('最高', 0)) if pd.notna(row.get('最高')) else None,
                        low=float(row.get('最低', 0)) if pd.notna(row.get('最低')) else None,
                        open_price=float(row.get('今开', 0)) if pd.notna(row.get('今开')) else None,
                        pre_close=float(row.get('昨收', 0)) if pd.notna(row.get('昨收')) else None,
                        volume_ratio=float(row.get('量比', 0)) if pd.notna(row.get('量比')) else None,
                        turnover_rate=float(row.get('换手率', 0)) if pd.notna(row.get('换手率')) else None,
                        pe=float(row.get('市盈率-动态', 0)) if pd.notna(row.get('市盈率-动态')) else None,
                        pb=float(row.get('市净率', 0)) if pd.notna(row.get('市净率')) else None,
                        market_cap=float(row.get('总市值', 0)) if pd.notna(row.get('总市值')) else None,
                        circ_market_cap=float(row.get('流通市值', 0)) if pd.notna(row.get('流通市值')) else None,
                        update_time=datetime.now(),
                    )
                    session.add(record)

                session.commit()
                logger.info(f"已保存 {len(df)} 条实时行情到本地")
        except Exception as e:
            logger.error(f"保存实时行情失败: {e}")

    # ==================== 涨停板 ====================

    @staticmethod
    def get_limit_up(trade_date: Optional[str] = None, force_refresh: bool = False) -> List[Dict]:
        """获取涨停板数据"""
        if trade_date:
            target_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            target_date = date.today()

        # 尝试从本地获取
        if not force_refresh:
            local_data = CacheService._get_limit_up_from_local(target_date)
            if local_data:
                logger.info(f"从本地获取涨停板 {len(local_data)} 条")
                return local_data

        # 从 akshare 获取
        df = CacheService._fetch_limit_up_from_akshare(target_date)
        if df is None or df.empty:
            return []

        # 存储到本地
        CacheService._save_limit_up_to_local(df, target_date)
        return CacheService._convert_df_to_records(df)

    @staticmethod
    def _get_limit_up_from_local(target_date: date) -> Optional[List[Dict]]:
        """从本地获取涨停板"""
        try:
            with Session(engine) as session:
                records = session.exec(
                    select(ExternalLimitUp).where(
                        ExternalLimitUp.trade_date == target_date
                    )
                ).all()
                if records:
                    return [r.model_dump() for r in records]
        except Exception as e:
            logger.warning(f"从本地获取涨停板失败: {e}")
        return None

    @staticmethod
    def _fetch_limit_up_from_akshare(target_date: date) -> Optional[pd.DataFrame]:
        """从 akshare 获取涨停板"""
        import akshare as ak
        try:
            # 使用涨停股池作为涨停板数据
            df = ak.stock_zt_pool_em(date=target_date.strftime("%Y%m%d"))
            return df
        except Exception as e:
            logger.error(f"获取涨停板失败: {e}")
            return None

    @staticmethod
    def _save_limit_up_to_local(df: pd.DataFrame, target_date: date):
        """保存涨停板到本地"""
        try:
            if df is None or df.empty:
                logger.info("涨停板数据为空，跳过保存")
                return

            with Session(engine) as session:
                session.exec(
                    delete(ExternalLimitUp).where(
                        ExternalLimitUp.trade_date == target_date
                    )
                )

                for _, row in df.iterrows():
                    def get_val(key, default=0):
                        val = row.get(key)
                        if pd.isna(val):
                            return None
                        try:
                            return float(val)
                        except:
                            return default

                    record = ExternalLimitUp(
                        trade_date=target_date,
                        code=str(row.get('代码', '')) if pd.notna(row.get('代码')) else '',
                        name=str(row.get('名称', '')) if pd.notna(row.get('名称')) else '',
                        close_price=get_val('收盘价'),
                        change_pct=get_val('涨跌幅'),
                        reason=str(row.get('涨停原因', '')) if pd.notna(row.get('涨停原因')) else None,
                        seal_amount=get_val('封单金额'),
                        seal_ratio=get_val('封比'),
                        open_count=int(row.get('打开次数', 0)) if pd.notna(row.get('打开次数')) else None,
                        first_time=str(row.get('首次涨停时间', '')) if pd.notna(row.get('首次涨停时间')) else None,
                        last_time=str(row.get('最后涨停时间', '')) if pd.notna(row.get('最后涨停时间')) else None,
                        turnover_rate=get_val('换手率'),
                        market_cap=get_val('总市值'),
                    )
                    session.add(record)

                session.commit()
                logger.info(f"已保存 {len(df)} 条涨停板数据")
        except Exception as e:
            logger.error(f"保存涨停板失败: {e}")

    # ==================== 涨停板池 ====================

    @staticmethod
    def get_zt_pool(trade_date: Optional[str] = None, force_refresh: bool = False) -> List[Dict]:
        """获取涨停板池"""
        if trade_date:
            target_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            target_date = date.today()

        if not force_refresh:
            local_data = CacheService._get_zt_pool_from_local(target_date)
            if local_data:
                return local_data

        df = CacheService._fetch_zt_pool_from_akshare(target_date)
        if df is None or df.empty:
            return []

        CacheService._save_zt_pool_to_local(df, target_date)
        return CacheService._convert_df_to_records(df)

    @staticmethod
    def _get_zt_pool_from_local(target_date: date) -> Optional[List[Dict]]:
        try:
            with Session(engine) as session:
                records = session.exec(
                    select(ExternalZtPool).where(ExternalZtPool.trade_date == target_date)
                ).all()
                if records:
                    return [r.model_dump() for r in records]
        except Exception as e:
            logger.warning(f"从本地获取涨停板池失败: {e}")
        return None

    @staticmethod
    def _fetch_zt_pool_from_akshare(target_date: date) -> Optional[pd.DataFrame]:
        import akshare as ak
        try:
            df = ak.stock_zt_pool_em(date=target_date.strftime("%Y%m%d"))
            return df
        except Exception as e:
            logger.error(f"获取涨停板池失败: {e}")
            return None

    @staticmethod
    def _save_zt_pool_to_local(df: pd.DataFrame, target_date: date):
        try:
            if df is None or df.empty:
                logger.info("涨停板池数据为空，跳过保存")
                return

            with Session(engine) as session:
                session.exec(delete(ExternalZtPool).where(ExternalZtPool.trade_date == target_date))

                for _, row in df.iterrows():
                    def get_val(key, default=0):
                        val = row.get(key)
                        if pd.isna(val):
                            return None
                        try:
                            return float(val)
                        except:
                            return default

                    record = ExternalZtPool(
                        trade_date=target_date,
                        code=str(row.get('代码', '')) if pd.notna(row.get('代码')) else '',
                        name=str(row.get('名称', '')) if pd.notna(row.get('名称')) else '',
                        close_price=get_val('收盘价'),
                        change_pct=get_val('涨跌幅'),
                        reason=str(row.get('涨停原因', '')) if pd.notna(row.get('涨停原因')) else None,
                        first_time=str(row.get('首次涨停时间', '')) if pd.notna(row.get('首次涨停时间')) else None,
                        seal_amount=get_val('封单金额'),
                        turnover_rate=get_val('换手率'),
                    )
                    session.add(record)

                session.commit()
                logger.info(f"已保存 {len(df)} 条涨停板池数据")
        except Exception as e:
            logger.error(f"保存涨停板池失败: {e}")

    # ==================== 个股资金流向 ====================

    @staticmethod
    def get_individual_fund_flow(
        stock_code: str,
        market: str = "上海A股",
        force_refresh: bool = False
    ) -> List[Dict]:
        """获取个股资金流向"""
        # 尝试从本地获取
        if not force_refresh:
            local_data = CacheService._get_fund_flow_from_local(stock_code)
            if local_data:
                return local_data

        # 从 akshare 获取
        df = CacheService._fetch_fund_flow_from_akshare(stock_code, market)
        if df is None or df.empty:
            return []

        # 存储到本地
        CacheService._save_fund_flow_to_local(df, stock_code)
        return CacheService._convert_df_to_records(df)

    @staticmethod
    def _get_fund_flow_from_local(stock_code: str) -> Optional[List[Dict]]:
        try:
            with Session(engine) as session:
                records = session.exec(
                    select(ExternalIndividualFundFlow).where(
                        ExternalIndividualFundFlow.code == stock_code
                    ).order_by(ExternalIndividualFundFlow.trade_date.desc()).limit(10)
                ).all()
                if records:
                    return [r.model_dump() for r in records]
        except Exception as e:
            logger.warning(f"从本地获取资金流向失败: {e}")
        return None

    @staticmethod
    def _fetch_fund_flow_from_akshare(stock_code: str, market: str) -> Optional[pd.DataFrame]:
        import akshare as ak
        # 转换市场参数
        market_map = {
            "上海A股": "sh",
            "深圳A股": "sz",
            "sh": "sh",
            "sz": "sz",
        }
        ak_market = market_map.get(market, "sh")
        try:
            df = ak.stock_individual_fund_flow(stock=stock_code, market=ak_market)
            return df
        except Exception as e:
            logger.error(f"获取资金流向失败: {e}")
            return None

    @staticmethod
    def _save_fund_flow_to_local(df: pd.DataFrame, stock_code: str):
        try:
            with Session(engine) as session:
                # 删除该股票旧数据
                session.exec(
                    delete(ExternalIndividualFundFlow).where(
                        ExternalIndividualFundFlow.code == stock_code
                    )
                )

                for _, row in df.iterrows():
                    trade_date = row.get('日期')
                    if pd.isna(trade_date):
                        continue

                    # 处理列名兼容 - akshare返回的列名可能包含特殊字符
                    def get_val(key, default=0):
                        val = row.get(key)
                        if pd.isna(val):
                            return None
                        return float(val)

                    record = ExternalIndividualFundFlow(
                        trade_date=pd.to_datetime(trade_date).date(),
                        code=stock_code,
                        name=str(row.get('名称', '')) if pd.notna(row.get('名称')) else '',
                        net_main=get_val('主力净流入-净额'),
                        net_super=get_val('超大单净流入-净额'),
                        net_big=get_val('大单净流入-净额'),
                        net_mid=get_val('中单净流入-净额'),
                        net_small=get_val('小单净流入-净额'),
                        amount_main=get_val('主力成交额'),
                        amount_super=get_val('超大单成交额'),
                        amount_big=get_val('大单成交额'),
                        amount_mid=get_val('中单成交额'),
                        amount_small=get_val('小单成交额'),
                        ratio_main=get_val('主力净流入-净占比'),
                    )
                    session.add(record)

                session.commit()
                logger.info(f"已保存 {stock_code} 资金流向数据")
        except Exception as e:
            logger.error(f"保存资金流向失败: {e}")

    # ==================== 板块资金流向 ====================

    @staticmethod
    def get_sector_fund_flow(
        indicator: str = "今日",
        sector_type: str = "行业资金流",
        force_refresh: bool = False
    ) -> List[Dict]:
        """获取板块资金流向"""
        cache_key = f"sector_fund_flow_{indicator}_{sector_type}"

        if not force_refresh:
            local_data = CacheService._get_sector_fund_flow_from_local(indicator, sector_type)
            if local_data:
                return local_data

        df = CacheService._fetch_sector_fund_flow_from_akshare(indicator, sector_type)
        if df is None or df.empty:
            return []

        CacheService._save_sector_fund_flow_to_local(df, indicator, sector_type)
        return CacheService._convert_df_to_records(df)

    @staticmethod
    def _get_sector_fund_flow_from_local(indicator: str, sector_type: str) -> Optional[List[Dict]]:
        try:
            with Session(engine) as session:
                records = session.exec(
                    select(ExternalSectorFundFlow).where(
                        ExternalSectorFundFlow.indicator == indicator,
                        ExternalSectorFundFlow.sector_type == sector_type,
                    ).order_by(ExternalSectorFundFlow.rank.asc())
                ).all()
                if records:
                    return [r.model_dump() for r in records]
        except Exception as e:
            logger.warning(f"从本地获取板块资金流向失败: {e}")
        return None

    @staticmethod
    def _fetch_sector_fund_flow_from_akshare(indicator: str, sector_type: str) -> Optional[pd.DataFrame]:
        import akshare as ak
        try:
            if sector_type == "行业资金流":
                df = ak.stock_sector_fund_flow_rank(indicator=indicator)
            else:
                df = ak.stock_sector_fund_flow_rank(indicator=indicator)
            return df
        except Exception as e:
            logger.error(f"获取板块资金流向失败: {e}")
            return None

    @staticmethod
    def _save_sector_fund_flow_to_local(df: pd.DataFrame, indicator: str, sector_type: str):
        try:
            trade_date = date.today()
            with Session(engine) as session:
                session.exec(
                    delete(ExternalSectorFundFlow).where(
                        ExternalSectorFundFlow.indicator == indicator,
                        ExternalSectorFundFlow.sector_type == sector_type,
                    )
                )

                for idx, row in df.iterrows():
                    record = ExternalSectorFundFlow(
                        trade_date=trade_date,
                        indicator=indicator,
                        sector_type=sector_type,
                        sector_code=str(row.get('板块代码', '')),
                        sector_name=str(row.get('板块名称', '')),
                        net_inflow=float(row.get('主力净流入', 0)) if pd.notna(row.get('主力净流入')) else None,
                        net_inflow_main=float(row.get('主力净流入净额', 0)) if pd.notna(row.get('主力净流入净额')) else None,
                        change_pct=float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else None,
                        turnover_rate=float(row.get('换手率', 0)) if pd.notna(row.get('换手率')) else None,
                        amount=float(row.get('成交额', 0)) if pd.notna(row.get('成交额')) else None,
                        rank=idx + 1,
                    )
                    session.add(record)

                session.commit()
                logger.info(f"已保存 {len(df)} 条板块资金流向数据")
        except Exception as e:
            logger.error(f"保存板块资金流向失败: {e}")

    # ==================== 龙虎榜详情 ====================

    @staticmethod
    def get_lhb_detail(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        force_refresh: bool = False
    ) -> List[Dict]:
        """获取龙虎榜详情"""
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start = date.today() - timedelta(days=5)

        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end = date.today()

        if not force_refresh:
            local_data = CacheService._get_lhb_detail_from_local(start, end)
            if local_data:
                return local_data

        df = CacheService._fetch_lhb_detail_from_akshare(start, end)
        if df is None or df.empty:
            return []

        CacheService._save_lhb_detail_to_local(df)
        return CacheService._convert_df_to_records(df)

    @staticmethod
    def _get_lhb_detail_from_local(start: date, end: date) -> Optional[List[Dict]]:
        try:
            with Session(engine) as session:
                records = session.exec(
                    select(ExternalLhbDetail).where(
                        ExternalLhbDetail.trade_date >= start,
                        ExternalLhbDetail.trade_date <= end,
                    ).order_by(ExternalLhbDetail.trade_date.desc())
                ).all()
                if records:
                    return [r.model_dump() for r in records]
        except Exception as e:
            logger.warning(f"从本地获取龙虎榜详情失败: {e}")
        return None

    @staticmethod
    def _fetch_lhb_detail_from_akshare(start: date, end: date) -> Optional[pd.DataFrame]:
        import akshare as ak
        try:
            df = ak.stock_lhb_detail_em(start_date=start.strftime("%Y%m%d"), end_date=end.strftime("%Y%m%d"))
            return df
        except Exception as e:
            logger.error(f"获取龙虎榜详情失败: {e}")
            return None

    @staticmethod
    def _save_lhb_detail_to_local(df: pd.DataFrame):
        try:
            if df is None or df.empty:
                logger.info("龙虎榜详情数据为空，跳过保存")
                return

            with Session(engine) as session:
                for _, row in df.iterrows():
                    # 上榜日 is the trade date
                    trade_date = row.get('上榜日')
                    if pd.isna(trade_date):
                        continue

                    def get_val(key, default=0):
                        val = row.get(key)
                        if pd.isna(val):
                            return None
                        try:
                            return float(val)
                        except:
                            return default

                    record = ExternalLhbDetail(
                        trade_date=pd.to_datetime(trade_date).date() if isinstance(trade_date, str) else trade_date,
                        code=str(row.get('代码', '')) if pd.notna(row.get('代码')) else '',
                        name=str(row.get('名称', '')) if pd.notna(row.get('名称')) else '',
                        list_type=str(row.get('上榜原因', '')) if pd.notna(row.get('上榜原因')) else '',
                        buy_amount=get_val('龙虎榜买入额'),
                        sell_amount=get_val('龙虎榜卖出额'),
                        net_amount=get_val('龙虎榜净买额'),
                    )
                    session.add(record)

                session.commit()
                logger.info(f"已保存 {len(df)} 条龙虎榜详情数据")
        except Exception as e:
            logger.error(f"保存龙虎榜详情失败: {e}")

    # ==================== 龙虎榜游资追踪 ====================

    @staticmethod
    def get_lhb_yytj(force_refresh: bool = False) -> List[Dict]:
        """获取龙虎榜游资追踪"""
        if not force_refresh:
            local_data = CacheService._get_lhb_yytj_from_local()
            if local_data:
                return local_data

        df = CacheService._fetch_lhb_yytj_from_akshare()
        if df is None or df.empty:
            return []

        CacheService._save_lhb_yytj_to_local(df)
        return CacheService._convert_df_to_records(df)

    @staticmethod
    def _get_lhb_yytj_from_local() -> Optional[List[Dict]]:
        try:
            with Session(engine) as session:
                # 获取最新日期的数据
                latest_date = session.exec(
                    select(ExternalLhbYytj.trade_date).order_by(ExternalLhbYytj.trade_date.desc()).limit(1)
                ).first()

                if not latest_date:
                    return None

                records = session.exec(
                    select(ExternalLhbYytj)
                    .where(ExternalLhbYytj.trade_date == latest_date)
                ).all()
                if records:
                    return [r.model_dump() for r in records]
        except Exception as e:
            logger.warning(f"从本地获取游资追踪失败: {e}")
        return None

    @staticmethod
    def _fetch_lhb_yytj_from_akshare() -> Optional[pd.DataFrame]:
        import akshare as ak
        try:
            df = ak.stock_lhb_yytj_sina()
            return df
        except Exception as e:
            logger.error(f"获取游资追踪失败: {e}")
            return None

    @staticmethod
    def _save_lhb_yytj_to_local(df: pd.DataFrame):
        try:
            if df is None or df.empty:
                logger.info("游资追踪数据为空，跳过保存")
                return

            trade_date = date.today()
            with Session(engine) as session:
                session.exec(delete(ExternalLhbYytj).where(ExternalLhbYytj.trade_date == trade_date))

                for _, row in df.iterrows():
                    def get_val(key, default=0):
                        val = row.get(key)
                        if pd.isna(val):
                            return None
                        try:
                            return float(val)
                        except:
                            return default

                    def get_int(key, default=0):
                        val = row.get(key)
                        if pd.isna(val):
                            return None
                        try:
                            return int(val)
                        except:
                            return default

                    record = ExternalLhbYytj(
                        trade_date=trade_date,
                        trader_name=str(row.get('营业部名称', '')) if pd.notna(row.get('营业部名称')) else '',
                        buy_count=get_int('上榜次数'),
                        buy_amount=get_val('累积购买额'),
                        buy_avg=None,  # API doesn't provide average
                        sell_count=get_int('卖出席位数'),
                        sell_amount=get_val('累积卖出额'),
                    )
                    session.add(record)

                session.commit()
                logger.info(f"已保存 {len(df)} 条游资追踪数据")
        except Exception as e:
            logger.error(f"保存游资追踪失败: {e}")

    # ==================== 龙虎榜营业部 ====================

    @staticmethod
    def get_lhb_yyb(force_refresh: bool = False) -> List[Dict]:
        """获取龙虎榜营业部"""
        if not force_refresh:
            local_data = CacheService._get_lhb_yyb_from_local()
            if local_data:
                return local_data

        df = CacheService._fetch_lhb_yyb_from_akshare()
        if df is None or df.empty:
            return []

        CacheService._save_lhb_yyb_to_local(df)
        return CacheService._convert_df_to_records(df)

    @staticmethod
    def _get_lhb_yyb_from_local() -> Optional[List[Dict]]:
        try:
            with Session(engine) as session:
                # 获取最新日期的数据
                latest_date = session.exec(
                    select(ExternalLhbYyb.trade_date).order_by(ExternalLhbYyb.trade_date.desc()).limit(1)
                ).first()

                if not latest_date:
                    return None

                records = session.exec(
                    select(ExternalLhbYyb)
                    .where(ExternalLhbYyb.trade_date == latest_date)
                    .order_by(ExternalLhbYyb.up_count.desc())
                ).all()
                if records:
                    return [r.model_dump() for r in records]
        except Exception as e:
            logger.warning(f"从本地获取龙虎榜营业部失败: {e}")
        return None

    @staticmethod
    def _fetch_lhb_yyb_from_akshare() -> Optional[pd.DataFrame]:
        import akshare as ak
        try:
            df = ak.stock_lh_yyb_most()
            return df
        except Exception as e:
            logger.error(f"获取龙虎榜营业部失败: {e}")
            return None

    @staticmethod
    def _save_lhb_yyb_to_local(df: pd.DataFrame):
        try:
            if df is None or df.empty:
                logger.info("龙虎榜营业部数据为空，跳过保存")
                return

            trade_date = date.today()
            with Session(engine) as session:
                session.exec(delete(ExternalLhbYyb).where(ExternalLhbYyb.trade_date == trade_date))

                for _, row in df.iterrows():
                    def get_int(key, default=0):
                        val = row.get(key)
                        if pd.isna(val):
                            return None
                        try:
                            return int(val)
                        except:
                            return default

                    # 处理 "57.60亿" 格式的数字
                    def parse_amount(val):
                        if pd.isna(val):
                            return None
                        val_str = str(val)
                        try:
                            if '亿' in val_str:
                                return float(val_str.replace('亿', '')) * 100000000
                            elif '万' in val_str:
                                return float(val_str.replace('万', '')) * 10000
                            else:
                                return float(val_str)
                        except:
                            return None

                    record = ExternalLhbYyb(
                        trade_date=trade_date,
                        broker_name=str(row.get('营业部名称', '')) if pd.notna(row.get('营业部名称')) else '',
                        up_count=get_int('上榜次数'),
                        buy_count=get_int('买入席位数') if pd.notna(row.get('买入席位数')) else None,
                        sell_count=get_int('卖出席位数') if pd.notna(row.get('卖出席位数')) else None,
                        buy_amount=parse_amount(row.get('合计动用资金')),
                        sell_amount=None,  # API doesn't provide separate sell amount
                        net_amount=None,  # API doesn't provide net amount
                    )
                    session.add(record)

                session.commit()
                logger.info(f"已保存 {len(df)} 条龙虎榜营业部数据")
        except Exception as e:
            logger.error(f"保存龙虎榜营业部失败: {e}")

    # ==================== 工具方法 ====================

    @staticmethod
    def _convert_df_to_records(df: pd.DataFrame) -> List[Dict]:
        """将 DataFrame 转换为字典列表"""
        # 处理列名映射
        df_copy = df.copy()
        df_copy.columns = [str(c) for c in df_copy.columns]
        # 替换 NaN 值为 None
        df_copy = df_copy.replace({float('nan'): None, float('inf'): None, float('-inf'): None})
        return df_copy.to_dict('records')
