"""
X402Client - x402 协议的核心支付客户端
"""

from typing import Any, Callable, Protocol

from x402.types import (
    PaymentPayload,
    PaymentPermitContext,
    PaymentRequirements,
)


class ClientMechanism(Protocol):
    """客户端机制接口"""

    def scheme(self) -> str:
        """获取支付方案名称"""
        ...

    async def create_payment_payload(
        self,
        requirements: PaymentRequirements,
        resource: str,
        extensions: dict[str, Any] | None = None,
    ) -> PaymentPayload:
        """创建支付载荷"""
        ...


PaymentRequirementsSelector = Callable[[list[PaymentRequirements]], PaymentRequirements]


class PaymentRequirementsFilter:
    """选择支付要求的过滤选项"""

    def __init__(
        self,
        scheme: str | None = None,
        network: str | None = None,
        max_amount: str | None = None,
    ):
        self.scheme = scheme
        self.network = network
        self.max_amount = max_amount


class MechanismEntry:
    """已注册的机制条目"""

    def __init__(self, pattern: str, mechanism: ClientMechanism, priority: int):
        self.pattern = pattern
        self.mechanism = mechanism
        self.priority = priority


class X402Client:
    """
    x402 协议的核心支付客户端。

    管理支付机制注册表并协调支付流程。
    """

    def __init__(self) -> None:
        self._mechanisms: list[MechanismEntry] = []

    def register(self, network_pattern: str, mechanism: ClientMechanism) -> "X402Client":
        """
        为网络模式注册支付机制。

        参数:
            network_pattern: 网络模式（例如 "eip155:*", "tron:shasta"）
            mechanism: 支付机制实例

        返回:
            self 以支持链式调用
        """
        priority = self._calculate_priority(network_pattern)
        self._mechanisms.append(MechanismEntry(network_pattern, mechanism, priority))
        self._mechanisms.sort(key=lambda e: e.priority, reverse=True)
        return self

    def select_payment_requirements(
        self,
        accepts: list[PaymentRequirements],
        filters: PaymentRequirementsFilter | None = None,
    ) -> PaymentRequirements:
        """
        从可用选项中选择支付要求。

        参数:
            accepts: 可用的支付要求
            filters: 可选过滤器

        返回:
            选定的支付要求

        异常:
            ValueError: 未找到支持的支付要求
        """
        candidates = list(accepts)

        if filters:
            if filters.scheme:
                candidates = [r for r in candidates if r.scheme == filters.scheme]
            if filters.network:
                candidates = [r for r in candidates if r.network == filters.network]
            if filters.max_amount:
                max_val = int(filters.max_amount)
                candidates = [r for r in candidates if int(r.amount) <= max_val]

        candidates = [r for r in candidates if self._find_mechanism(r.network) is not None]

        if not candidates:
            raise ValueError("No supported payment requirements found")

        return candidates[0]

    async def create_payment_payload(
        self,
        requirements: PaymentRequirements,
        resource: str,
        extensions: dict[str, Any] | None = None,
    ) -> PaymentPayload:
        """
        为给定要求创建支付载荷。

        参数:
            requirements: 选定的支付要求
            resource: 资源 URL
            extensions: 可选扩展

        返回:
            支付载荷
        """
        mechanism = self._find_mechanism(requirements.network)
        if mechanism is None:
            raise ValueError(f"No mechanism registered for network: {requirements.network}")

        return await mechanism.create_payment_payload(requirements, resource, extensions)

    async def handle_payment(
        self,
        accepts: list[PaymentRequirements],
        resource: str,
        extensions: dict[str, Any] | None = None,
        selector: PaymentRequirementsSelector | None = None,
    ) -> PaymentPayload:
        """
        处理需要支付的响应。

        参数:
            accepts: 可用的支付要求
            resource: 资源 URL
            extensions: 可选扩展
            selector: 可选自定义选择器

        返回:
            支付载荷
        """
        if selector:
            requirements = selector(accepts)
        else:
            requirements = self.select_payment_requirements(accepts)

        return await self.create_payment_payload(requirements, resource, extensions)

    def _find_mechanism(self, network: str) -> ClientMechanism | None:
        """查找网络的机制"""
        for entry in self._mechanisms:
            if self._match_pattern(entry.pattern, network):
                return entry.mechanism
        return None

    def _match_pattern(self, pattern: str, network: str) -> bool:
        """将网络与模式匹配"""
        if pattern == network:
            return True
        if pattern.endswith(":*"):
            prefix = pattern[:-1]
            return network.startswith(prefix)
        return False

    def _calculate_priority(self, pattern: str) -> int:
        """计算模式的优先级（更具体 = 更高优先级）"""
        if pattern.endswith(":*"):
            return 1
        return 10
