"""
参数优化 Service
"""
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
import itertools
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd


@dataclass
class OptimizationResult:
    """优化结果"""
    params: Dict[str, Any]
    metrics: Dict[str, float]
    rank: int


class ParameterOptimizer:
    """策略参数优化器"""

    def __init__(
        self,
        param_grid: Dict[str, List[Any]],
        objective: str = "sharpe_ratio",
        maximize: bool = True
    ):
        self.param_grid = param_grid
        self.objective = objective
        self.maximize = maximize
        self.results: List[OptimizationResult] = []

    def _generate_param_combinations(self, method: str = "grid", n_iter: int = 50) -> List[Dict[str, Any]]:
        """生成参数组合"""
        if method == "grid":
            keys = list(self.param_grid.keys())
            combinations = list(itertools.product(*[self.param_grid[k] for k in keys]))
            return [dict(zip(keys, combo)) for combo in combinations]
        elif method == "random":
            combinations = []
            for _ in range(n_iter):
                combo = {
                    key: random.choice(values)
                    for key, values in self.param_grid.items()
                }
                combinations.append(combo)
            return combinations
        return []

    def _evaluate_params(
        self,
        params: Dict[str, Any],
        backtest_func: Callable,
        df: pd.DataFrame,
        initial_capital: float = 100000
    ) -> Dict[str, float]:
        """评估参数组合"""
        try:
            result = backtest_func(df, **params)
            return {
                "total_return": result.get("total_return", 0),
                "annual_return": result.get("annual_return", 0),
                "sharpe_ratio": result.get("sharpe_ratio", 0),
                "max_drawdown": result.get("max_drawdown", 0),
                "win_rate": result.get("win_rate", 0),
                "total_trades": result.get("total_trades", 0),
                "final_value": result.get("final_value", initial_capital),
            }
        except Exception as e:
            return {
                "total_return": -999,
                "annual_return": -999,
                "sharpe_ratio": -999,
                "max_drawdown": 100,
                "win_rate": 0,
                "total_trades": 0,
                "final_value": 0,
            }

    def optimize(
        self,
        backtest_func: Callable,
        df: pd.DataFrame,
        method: str = "grid",
        n_iter: int = 50,
        initial_capital: float = 100000,
        n_jobs: int = 4
    ) -> List[OptimizationResult]:
        """执行参数优化"""
        combinations = self._generate_param_combinations(method, n_iter)
        self.results = []

        if self.objective in ["max_drawdown"]:
            reverse = False
        else:
            reverse = self.maximize

        with ThreadPoolExecutor(max_workers=n_jobs) as executor:
            futures = {
                executor.submit(
                    self._evaluate_params,
                    params,
                    backtest_func,
                    df,
                    initial_capital
                ): params
                for params in combinations
            }

            results_with_params = []
            for future in as_completed(futures):
                params = futures[future]
                try:
                    metrics = future.result()
                    results_with_params.append((params, metrics))
                except Exception as e:
                    results_with_params.append((params, {
                        "total_return": -999,
                        "sharpe_ratio": -999,
                        "max_drawdown": 100,
                    }))

        results_with_params.sort(
            key=lambda x: x[1].get(self.objective, 0),
            reverse=reverse
        )

        for rank, (params, metrics) in enumerate(results_with_params, 1):
            self.results.append(OptimizationResult(
                params=params,
                metrics=metrics,
                rank=rank
            ))

        return self.results

    def get_top_n(self, n: int = 10) -> List[OptimizationResult]:
        """获取Top N结果"""
        return self.results[:n]

    def get_best(self) -> OptimizationResult:
        """获取最佳结果"""
        return self.results[0] if self.results else None

    def summary(self) -> Dict[str, Any]:
        """生成优化摘要"""
        if not self.results:
            return {}

        best = self.results[0]
        return {
            "best_params": best.params,
            "best_metrics": best.metrics,
            "total_combinations": len(self.results),
            "objective": self.objective,
            "top_10": [
                {
                    "rank": r.rank,
                    "params": r.params,
                    "metrics": {k: round(v, 2) for k, v in r.metrics.items()}
                }
                for r in self.results[:10]
            ]
        }
