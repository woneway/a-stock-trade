"""
AKShare Service
"""
from typing import Any, Dict, Optional

import app.provider.akshare as akshare_provider


# 获取 provider/akshare 中所有可导出的函数
AKSHARE_FUNCTIONS = {
    name: getattr(akshare_provider, name)
    for name in akshare_provider.__all__
}


class AkshareService:
    """AKShare 服务"""

    @staticmethod
    def list_functions() -> list:
        """列出所有可用的AKShare函数"""
        return list(AKSHARE_FUNCTIONS.keys())

    @staticmethod
    def call_function(function_name: str, **kwargs: Any) -> Any:
        """调用 AKShare 函数"""
        if function_name not in AKSHARE_FUNCTIONS:
            raise ValueError(f"函数 {function_name} 不存在")

        func = AKSHARE_FUNCTIONS[function_name]
        params = {k: v for k, v in kwargs.items() if v is not None}
        return func(**params)

    @staticmethod
    def call_function_with_params(function_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """通过参数字典调用 AKShare 函数"""
        if function_name not in AKSHARE_FUNCTIONS:
            raise ValueError(f"函数 {function_name} 不存在")

        func = AKSHARE_FUNCTIONS[function_name]
        params = params or {}
        return func(**params)
