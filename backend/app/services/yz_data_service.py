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

    @staticmethod
    def query_from_local(func_name: str, params: dict) -> Optional[List[Dict]]:
        """从本地查询数据"""
        method_name = YzDataService.QUERY_METHODS.get(func_name)
        if not method_name:
            return None

        method = getattr(YzDataService, method_name, None)
        if not method:
            return None

        # 根据函数类型调用不同的查询方法
        if func_name == "stock_individual_fund_flow":
            stock_code = params.get("stock")
            if stock_code:
                return method(stock_code)
        elif func_name in ["stock_zh_a_limit_up_em", "stock_zt_pool_em"]:
            # 使用日期参数或今天
            from datetime import date
            target_date = params.get("date")
            if target_date:
                from datetime import datetime
                target_date = datetime.strptime(target_date, "%Y%m%d").date()
            else:
                target_date = date.today()
            return method(target_date)
        elif func_name == "stock_sector_fund_flow_rank":
            indicator = params.get("indicator", "今日")
            sector_type = params.get("sector_type", "行业资金流")
            return method(indicator, sector_type)

        # 默认调用无参数方法
        return method()

    @staticmethod
    def save_to_local(func_name: str, params: dict, result: dict):
        """保存数据到本地"""
        method_name = YzDataService.SAVE_METHODS.get(func_name)
        if not method_name:
            return

        method = getattr(YzDataService, method_name, None)
        if not method:
            return

        # 获取数据
        data = result.get("data", [])
        if not data:
            return

        import pandas as pd
        df = pd.DataFrame(data)

        # 根据函数类型调用不同的保存方法
        if func_name == "stock_individual_fund_flow":
            stock_code = params.get("stock")
            if stock_code:
                method(df, stock_code)
        elif func_name in ["stock_zh_a_limit_up_em", "stock_zt_pool_em"]:
            target_date = params.get("date")
            if target_date:
                from datetime import datetime
                target_date = datetime.strptime(target_date, "%Y%m%d").date()
            else:
                from datetime import date
                target_date = date.today()
            method(df, target_date)
        elif func_name == "stock_sector_fund_flow_rank":
            indicator = params.get("indicator", "今日")
            sector_type = params.get("sector_type", "行业资金流")
            method(df, indicator, sector_type)
        elif func_name == "stock_lhb_detail_em":
            method(df)
        elif func_name == "stock_lhb_yytj_sina":
            method(df)
        elif func_name == "stock_lh_yyb_most":
            method(df)

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
            df = ak.stock_zh_a_limit_up_em(date=target_date.strftime("%Y%m%d"))
            return df
        except Exception as e:
            logger.error(f"获取涨停板失败: {e}")
            return None

    @staticmethod
    def _save_limit_up_to_local(df: pd.DataFrame, target_date: date):
        """保存涨停板到本地"""
        try:
            with Session(engine) as session:
                session.exec(
                    delete(ExternalLimitUp).where(
                        ExternalLimitUp.trade_date == target_date
                    )
                )

                for _, row in df.iterrows():
                    record = ExternalLimitUp(
                        trade_date=target_date,
                        code=str(row.get('代码', '')),
                        name=str(row.get('名称', '')),
                        close_price=float(row.get('收盘价', 0)) if pd.notna(row.get('收盘价')) else None,
                        change_pct=float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else None,
                        reason=str(row.get('涨停原因', '')) if pd.notna(row.get('涨停原因')) else None,
                        seal_amount=float(row.get('封单金额', 0)) if pd.notna(row.get('封单金额')) else None,
                        seal_ratio=float(row.get('封比', 0)) if pd.notna(row.get('封比')) else None,
                        open_count=int(row.get('打开次数', 0)) if pd.notna(row.get('打开次数')) else None,
                        first_time=str(row.get('首次涨停时间', '')) if pd.notna(row.get('首次涨停时间')) else None,
                        last_time=str(row.get('最后涨停时间', '')) if pd.notna(row.get('最后涨停时间')) else None,
                        turnover_rate=float(row.get('换手率', 0)) if pd.notna(row.get('换手率')) else None,
                        market_cap=float(row.get('总市值', 0)) if pd.notna(row.get('总市值')) else None,
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
            with Session(engine) as session:
                session.exec(delete(ExternalZtPool).where(ExternalZtPool.trade_date == target_date))

                for _, row in df.iterrows():
                    record = ExternalZtPool(
                        trade_date=target_date,
                        code=str(row.get('代码', '')),
                        name=str(row.get('名称', '')),
                        close_price=float(row.get('收盘价', 0)) if pd.notna(row.get('收盘价')) else None,
                        change_pct=float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else None,
                        reason=str(row.get('涨停原因', '')) if pd.notna(row.get('涨停原因')) else None,
                        first_time=str(row.get('首次涨停时间', '')) if pd.notna(row.get('首次涨停时间')) else None,
                        seal_amount=float(row.get('封单金额', 0)) if pd.notna(row.get('封单金额')) else None,
                        turnover_rate=float(row.get('换手率', 0)) if pd.notna(row.get('换手率')) else None,
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
        try:
            df = ak.stock_individual_fund_flow(stock=stock_code, market=market)
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

                    record = ExternalIndividualFundFlow(
                        trade_date=pd.to_datetime(trade_date).date(),
                        code=stock_code,
                        name=str(row.get('名称', '')),
                        net_main=float(row.get('主力净流入', 0)) if pd.notna(row.get('主力净流入')) else None,
                        net_super=float(row.get('超大单净流入', 0)) if pd.notna(row.get('超大单净流入')) else None,
                        net_big=float(row.get('大单净流入', 0)) if pd.notna(row.get('大单净流入')) else None,
                        net_mid=float(row.get('中单净流入', 0)) if pd.notna(row.get('中单净流入')) else None,
                        net_small=float(row.get('小单净流入', 0)) if pd.notna(row.get('小单净流入')) else None,
                        amount_main=float(row.get('主力成交额', 0)) if pd.notna(row.get('主力成交额')) else None,
                        amount_super=float(row.get('超大单成交额', 0)) if pd.notna(row.get('超大单成交额')) else None,
                        amount_big=float(row.get('大单成交额', 0)) if pd.notna(row.get('大单成交额')) else None,
                        amount_mid=float(row.get('中单成交额', 0)) if pd.notna(row.get('中单成交额')) else None,
                        amount_small=float(row.get('小单成交额', 0)) if pd.notna(row.get('小单成交额')) else None,
                        ratio_main=float(row.get('主力净流入占比', 0)) if pd.notna(row.get('主力净流入占比')) else None,
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
            with Session(engine) as session:
                for _, row in df.iterrows():
                    trade_date = row.get('日期')
                    if pd.isna(trade_date):
                        continue

                    record = ExternalLhbDetail(
                        trade_date=pd.to_datetime(trade_date).date(),
                        code=str(row.get('代码', '')),
                        name=str(row.get('名称', '')),
                        list_type=str(row.get('上榜原因', '')),
                        buy_amount=float(row.get('龙虎榜买入金额', 0)) if pd.notna(row.get('龙虎榜买入金额')) else None,
                        sell_amount=float(row.get('龙虎榜卖出金额', 0)) if pd.notna(row.get('龙虎榜卖出金额')) else None,
                        net_amount=float(row.get('龙虎榜净买入额', 0)) if pd.notna(row.get('龙虎榜净买入额')) else None,
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
            trade_date = date.today()
            with Session(engine) as session:
                session.exec(delete(ExternalLhbYytj).where(ExternalLhbYytj.trade_date == trade_date))

                for _, row in df.iterrows():
                    record = ExternalLhbYytj(
                        trade_date=trade_date,
                        trader_name=str(row.get('游资名称', '')),
                        buy_count=int(row.get('买入次数', 0)) if pd.notna(row.get('买入次数')) else None,
                        buy_amount=float(row.get('买入金额', 0)) if pd.notna(row.get('买入金额')) else None,
                        buy_avg=float(row.get('平均买入金额', 0)) if pd.notna(row.get('平均买入金额')) else None,
                        sell_count=int(row.get('卖出次数', 0)) if pd.notna(row.get('卖出次数')) else None,
                        sell_amount=float(row.get('卖出金额', 0)) if pd.notna(row.get('卖出金额')) else None,
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
            trade_date = date.today()
            with Session(engine) as session:
                session.exec(delete(ExternalLhbYyb).where(ExternalLhbYyb.trade_date == trade_date))

                for _, row in df.iterrows():
                    record = ExternalLhbYyb(
                        trade_date=trade_date,
                        broker_name=str(row.get('营业部名称', '')),
                        up_count=int(row.get('上榜次数', 0)) if pd.notna(row.get('上榜次数')) else None,
                        buy_count=int(row.get('买入次数', 0)) if pd.notna(row.get('买入次数')) else None,
                        sell_count=int(row.get('卖出次数', 0)) if pd.notna(row.get('卖出次数')) else None,
                        buy_amount=float(row.get('买入金额', 0)) if pd.notna(row.get('买入金额')) else None,
                        sell_amount=float(row.get('卖出金额', 0)) if pd.notna(row.get('卖出金额')) else None,
                        net_amount=float(row.get('净买入金额', 0)) if pd.notna(row.get('净买入金额')) else None,
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
        return df_copy.to_dict('records')
