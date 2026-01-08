"""
FacilitatorClient - 与 facilitator 服务通信的客户端
"""

from typing import Any

import httpx

from x402.types import (
    PaymentPayload,
    PaymentRequirements,
    VerifyResponse,
    SettleResponse,
    SupportedResponse,
    FeeQuoteResponse,
)


class FacilitatorClient:
    """
    与 facilitator 服务通信的客户端

    处理 verify、settle、fee quote 和 supported 查询
    """

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str] | None = None,
        facilitator_id: str | None = None,
    ) -> None:
        """
        初始化 facilitator 客户端

        Args:
            base_url: Facilitator 服务基础 URL
            headers: 自定义 HTTP 头（例如 Authorization）
            facilitator_id: 此 facilitator 的唯一标识符
        """
        self._base_url = base_url.rstrip("/")
        self._headers = headers or {}
        self.facilitator_id = facilitator_id or base_url
        self._http_client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """获取或创建 HTTP 客户端"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._headers,
                timeout=30.0,
            )
        return self._http_client

    async def close(self) -> None:
        """关闭 HTTP 客户端"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def supported(self) -> SupportedResponse:
        """
        查询 facilitator 支持的能力

        Returns:
            包含支持的网络/方案的 SupportedResponse
        """
        client = await self._get_client()
        response = await client.get("/supported")
        response.raise_for_status()
        return SupportedResponse(**response.json())

    async def fee_quote(
        self,
        accept: PaymentRequirements,
        context: dict[str, Any] | None = None,
    ) -> FeeQuoteResponse:
        """
        查询支付要求的费用报价

        Args:
            accept: 支付要求
            context: 可选的支付上下文

        Returns:
            包含费用信息的 FeeQuoteResponse
        """
        client = await self._get_client()
        payload = {
            "accept": accept.model_dump(by_alias=True),
        }
        if context:
            payload["paymentPermitContext"] = context

        response = await client.post("/fee/quote", json=payload)
        response.raise_for_status()
        return FeeQuoteResponse(**response.json())

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
        client = await self._get_client()
        request_body = {
            "paymentPayload": payload.model_dump(by_alias=True),
            "paymentRequirements": requirements.model_dump(by_alias=True),
        }

        response = await client.post("/verify", json=request_body)
        response.raise_for_status()
        return VerifyResponse(**response.json())

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
        client = await self._get_client()
        request_body = {
            "paymentPayload": payload.model_dump(by_alias=True),
            "paymentRequirements": requirements.model_dump(by_alias=True),
        }

        response = await client.post("/settle", json=request_body)
        response.raise_for_status()
        return SettleResponse(**response.json())
