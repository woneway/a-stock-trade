"""
游资常用数据服务
- 优先查询本地数据库
- 本地无数据或过期时调用 akshare 并自动存储
"""
from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List
import pandas as pd
import logging
from sqlmodel import Session, select, delete, func

from app.database import engine
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


class YzDataService:
    """游资数据服务 - 本地缓存优先"""

    # 缓存有效期（秒）
    SPOT_CACHE_TTL = 60        # 实时行情 60秒
    LIMIT_UP_CACHE_TTL = 300   # 涨停板 5分钟
    FUND_FLOW_CACHE_TTL = 300  # 资金流向 5分钟
    LHB_CACHE_TTL = 600        # 龙虎榜 10分钟

    # ==================== A股实时行情 ====================

    @staticmethod
    def get_stock_spot(force_refresh: bool = False) -> List[Dict]:
        """获取A股实时行情 - 优先本地"""
        # 尝试从本地获取
        if not force_refresh:
            local_data = YzDataService._get_spot_from_local()
            if local_data:
                logger.info(f"从本地获取实时行情 {len(local_data)} 条")
                return local_data

        # 从 akshare 获取并存储
        df = YzDataService._fetch_spot_from_akshare()
        if df is None or df.empty:
            return []

        # 存储到本地
        YzDataService._save_spot_to_local(df)
        return YzDataService._convert_df_to_records(df)

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
            local_data = YzDataService._get_limit_up_from_local(target_date)
            if local_data:
                logger.info(f"从本地获取涨停板 {len(local_data)} 条")
                return local_data

        # 从 akshare 获取
        df = YzDataService._fetch_limit_up_from_akshare(target_date)
        if df is None or df.empty:
            return []

        # 存储到本地
        YzDataService._save_limit_up_to_local(df, target_date)
        return YzDataService._convert_df_to_records(df)

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
            local_data = YzDataService._get_zt_pool_from_local(target_date)
            if local_data:
                return local_data

        df = YzDataService._fetch_zt_pool_from_akshare(target_date)
        if df is None or df.empty:
            return []

        YzDataService._save_zt_pool_to_local(df, target_date)
        return YzDataService._convert_df_to_records(df)

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
            local_data = YzDataService._get_fund_flow_from_local(stock_code)
            if local_data:
                return local_data

        # 从 akshare 获取
        df = YzDataService._fetch_fund_flow_from_akshare(stock_code, market)
        if df is None or df.empty:
            return []

        # 存储到本地
        YzDataService._save_fund_flow_to_local(df, stock_code)
        return YzDataService._convert_df_to_records(df)

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
            local_data = YzDataService._get_sector_fund_flow_from_local(indicator, sector_type)
            if local_data:
                return local_data

        df = YzDataService._fetch_sector_fund_flow_from_akshare(indicator, sector_type)
        if df is None or df.empty:
            return []

        YzDataService._save_sector_fund_flow_to_local(df, indicator, sector_type)
        return YzDataService._convert_df_to_records(df)

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
            local_data = YzDataService._get_lhb_detail_from_local(start, end)
            if local_data:
                return local_data

        df = YzDataService._fetch_lhb_detail_from_akshare(start, end)
        if df is None or df.empty:
            return []

        YzDataService._save_lhb_detail_to_local(df)
        return YzDataService._convert_df_to_records(df)

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
            local_data = YzDataService._get_lhb_yytj_from_local()
            if local_data:
                return local_data

        df = YzDataService._fetch_lhb_yytj_from_akshare()
        if df is None or df.empty:
            return []

        YzDataService._save_lhb_yytj_to_local(df)
        return YzDataService._convert_df_to_records(df)

    @staticmethod
    def _get_lhb_yytj_from_local() -> Optional[List[Dict]]:
        try:
            with Session(engine) as session:
                records = session.exec(
                    select(ExternalLhbYytj).order_by(ExternalLhbYytj.trade_date.desc())
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
            local_data = YzDataService._get_lhb_yyb_from_local()
            if local_data:
                return local_data

        df = YzDataService._fetch_lhb_yyb_from_akshare()
        if df is None or df.empty:
            return []

        YzDataService._save_lhb_yyb_to_local(df)
        return YzDataService._convert_df_to_records(df)

    @staticmethod
    def _get_lhb_yyb_from_local() -> Optional[List[Dict]]:
        try:
            with Session(engine) as session:
                records = session.exec(
                    select(ExternalLhbYyb).order_by(ExternalLhbYyb.up_count.desc()).limit(100)
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
