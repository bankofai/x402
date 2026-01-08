"""
X402Facilitator - x402 协议的核心支付处理器
"""

from typing import Any, Protocol

from x402.types import (
    PaymentPayload,
    PaymentRequirements,
    VerifyResponse,
    SettleResponse,
    SupportedResponse,
    SupportedKind,
    FeeQuoteResponse,
)


class FacilitatorMechanism(Protocol):
    """中间层机制接口"""

    def scheme(self) -> str:
        """获取支付方案名称"""
        ...

    async def fee_quote(
        self,
        accept: PaymentRequirements,
        context: dict[str, Any] | None = None,
    ) -> FeeQuoteResponse:
        """计算费用报价"""
        ...

    async def verify(
        self,
        payload: PaymentPayload,
        requirements: PaymentRequirements,
    ) -> VerifyResponse:
        """验证支付签名"""
        ...

    async def settle(
        self,
        payload: PaymentPayload,
        requirements: PaymentRequirements,
    ) -> SettleResponse:
        """执行支付结算"""
        ...


class X402Facilitator:
    """
    x402 协议的核心支付处理器。

    管理支付机制并协调验证/结算。
    """

    def __init__(self) -> None:
        self._mechanisms: dict[str, dict[str, FacilitatorMechanism]] = {}

    def register(
        self,
        networks: list[str],
        mechanism: FacilitatorMechanism,
    ) -> "X402Facilitator":
        """
        为多个网络注册支付机制。

        参数:
            networks: 网络标识符列表
            mechanism: 中间层机制实例

        返回:
            self 以支持链式调用
        """
        scheme = mechanism.scheme()
        for network in networks:
            if network not in self._mechanisms:
                self._mechanisms[network] = {}
            self._mechanisms[network][scheme] = mechanism
        return self

    def supported(self) -> SupportedResponse:
        """
        返回支持的网络/方案组合

        Returns:
            包含所有支持能力的 SupportedResponse
        """
        kinds: list[SupportedKind] = []
        for network, schemes in self._mechanisms.items():
            for scheme in schemes:
                kinds.append(
                    SupportedKind(
                        x402Version=2,
                        scheme=scheme,
                        network=network,
                    )
                )
        return SupportedResponse(kinds=kinds)

    async def fee_quote(
        self,
        accept: PaymentRequirements,
        context: dict[str, Any] | None = None,
    ) -> FeeQuoteResponse:
        """
        计算支付要求的费用报价

        Args:
            accept: 支付要求
            context: 可选的支付上下文

        Returns:
            包含费用信息的 FeeQuoteResponse
        """
        mechanism = self._find_mechanism(accept.network, accept.scheme)
        if mechanism is None:
            raise ValueError(
                f"No mechanism for network={accept.network}, scheme={accept.scheme}"
            )
        return await mechanism.fee_quote(accept, context)

    async def verify(
        self,
        payload: PaymentPayload,
        requirements: PaymentRequirements,
    ) -> VerifyResponse:
        """
        验证支付签名和有效性。

        参数:
            payload: 来自客户端的支付载荷
            requirements: 支付要求

        返回:
            VerifyResponse
        """
        mechanism = self._find_mechanism(requirements.network, requirements.scheme)
        if mechanism is None:
            return VerifyResponse(
                isValid=False,
                invalidReason=f"unsupported_network_scheme: {requirements.network}/{requirements.scheme}",
            )
        return await mechanism.verify(payload, requirements)

    async def settle(
        self,
        payload: PaymentPayload,
        requirements: PaymentRequirements,
    ) -> SettleResponse:
        """
        执行支付结算。

        参数:
            payload: 来自客户端的支付载荷
            requirements: 支付要求

        返回:
            包含 tx_hash 的 SettleResponse
        """
        mechanism = self._find_mechanism(requirements.network, requirements.scheme)
        if mechanism is None:
            return SettleResponse(
                success=False,
                errorReason=f"unsupported_network_scheme: {requirements.network}/{requirements.scheme}",
            )
        return await mechanism.settle(payload, requirements)

    def _find_mechanism(
        self, network: str, scheme: str
    ) -> FacilitatorMechanism | None:
        """查找网络和方案对应的机制"""
        network_mechanisms = self._mechanisms.get(network)
        if network_mechanisms is None:
            return None
        return network_mechanisms.get(scheme)
