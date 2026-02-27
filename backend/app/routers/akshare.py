"""
AKShare 通用接口测试路由
支持动态调用 provider/akshare 中的所有函数
"""
from typing import Any, Optional
from fastapi import APIRouter, Query

from app.services.akshare_service import AkshareService

router = APIRouter(prefix="/akshare", tags=["AKShare"])


@router.get("/")
async def list_functions():
    """列出所有可用的AKShare函数"""
    functions = AkshareService.list_functions()
    return {
        "functions": functions,
        "count": len(functions)
    }


@router.get("/functions/{function_name}")
async def call_function(
    function_name: str,
    **kwargs: Any
):
    """
    通用调用接口

    示例:
    - GET /akshare/functions/get_stock_info_a_code_name
    - GET /akshare/functions/get_lhb_detail?start_date=20260201&end_date=20260210
    - GET /akshare/functions/get_zt_pool?date=20260226
    """
    try:
        result = AkshareService.call_function(function_name, **kwargs)
        if hasattr(result, '__iter__'):
            return list(result)
        return result
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e), "function": function_name}


@router.post("/call")
async def call_function_post(
    function: str = Query(..., description="函数名称"),
    params: Optional[dict] = Query(None, description="函数参数"),
):
    """
    POST 方式调用接口

    示例:
    {
        "function": "get_stock_info_a_code_name",
        "params": {}
    }
    """
    try:
        result = AkshareService.call_function_with_params(function, params)
        if hasattr(result, '__iter__'):
            return list(result)
        return result
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e), "function": function}
