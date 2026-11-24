"""自定义异常层次结构（v2.0）。"""

from __future__ import annotations


class WealthRadarError(Exception):
    """wealth-radar-ai 基础异常。"""


class ConfigValidationError(WealthRadarError):
    """配置文件或持仓快照校验失败。"""


class DataFeedError(WealthRadarError):
    """外部行情、基金、公告或新闻数据获取失败。"""


class MissingDependencyError(WealthRadarError):
    """运行所需的可选外部依赖未安装。"""


class AuditGateError(WealthRadarError):
    """审计结论提交格式或门禁输入校验失败。"""


class PersistenceError(WealthRadarError):
    """状态、持仓或审计记录持久化失败。"""
