"""
Facilitator 机制基础接口
"""

from abc import ABC, abstractmethod
from typing import Any

from x402.types import (
    PaymentPayload,
    PaymentRequirements,
    VerifyResponse,
    SettleResponse,
    FeeQuoteResponse,
)


class FacilitatorMechanism(ABC):
    """
    Facilitator 支付机制的抽象基类

    负责验证签名和执行结算
    """

    @abstractmethod
    def scheme(self) -> str:
        """获取支付方案名称"""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def verify(
        self,
        payload: PaymentPayload,
        requirements: PaymentRequirements,
    ) -> VerifyResponse:
        """
        验证支付签名（不执行链上交易）

        Args:
            payload: 来自客户端的支付载荷
            requirements: 支付要求

        Returns:
            VerifyResponse
        """
        pass

    @abstractmethod
    async def settle(
        self,
        payload: PaymentPayload,
        requirements: PaymentRequirements,
    ) -> SettleResponse:
        """
        执行支付结算（链上交易）

        Args:
            payload: 来自客户端的支付载荷
            requirements: 支付要求

        Returns:
            包含 tx_hash 的 SettleResponse
        """
        pass
