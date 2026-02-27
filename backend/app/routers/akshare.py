"""
AKShare 通用接口测试路由
支持动态调用 provider/akshare 中的所有函数
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel

import app.provider.akshare as akshare_provider

router = APIRouter(prefix="/akshare", tags=["AKShare"])

# 获取 provider/akshare 中所有可导出的函数
AKSHARE_FUNCTIONS = {
    name: getattr(akshare_provider, name)
    for name in akshare_provider.__all__
}


class GenericCallRequest(BaseModel):
    """通用调用请求"""
    function: str = Query(..., description="函数名称")
    params: Optional[Dict[str, Any]] = Query(None, description="函数参数")


@router.get("/")
async def list_functions():
    """列出所有可用的AKShare函数"""
    return {
        "functions": list(AKSHARE_FUNCTIONS.keys()),
        "count": len(AKSHARE_FUNCTIONS)
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
    if function_name not in AKSHARE_FUNCTIONS:
        return {"error": f"函数 {function_name} 不存在", "available_functions": list(AKSHARE_FUNCTIONS.keys())}

    func = AKSHARE_FUNCTIONS[function_name]

    try:
        # 过滤掉None值
        params = {k: v for k, v in kwargs.items() if v is not None}
        result = func(**params)

        # 转换为可序列化的格式
        if hasattr(result, '__iter__'):
            return list(result)
        return result

    except Exception as e:
        return {"error": str(e), "function": function_name}


@router.post("/call")
async def call_function_post(request: GenericCallRequest):
    """
    POST 方式调用接口

    请求体:
    {
        "function": "get_stock_info_a_code_name",
        "params": {}
    }
    """
    if request.function not in AKSHARE_FUNCTIONS:
        return {"error": f"函数 {request.function} 不存在", "available_functions": list(AKSHARE_FUNCTIONS.keys())}

    func = AKSHARE_FUNCTIONS[request.function]

    try:
        params = request.params or {}
        result = func(**params)

        if hasattr(result, '__iter__'):
            return list(result)
        return result

    except Exception as e:
        return {"error": str(e), "function": request.function}
