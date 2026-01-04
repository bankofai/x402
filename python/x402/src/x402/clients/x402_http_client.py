"""
X402HttpClient - 具有自动 402 支付处理的 HTTP 客户端适配器
"""

from typing import Any

import httpx

from x402.clients.x402_client import X402Client, PaymentRequirementsSelector
from x402.encoding import decode_payment_payload, encode_payment_payload
from x402.types import PaymentPayload, PaymentRequired


PAYMENT_SIGNATURE_HEADER = "PAYMENT-SIGNATURE"
PAYMENT_REQUIRED_HEADER = "PAYMENT-REQUIRED"
PAYMENT_RESPONSE_HEADER = "PAYMENT-RESPONSE"


class X402HttpClient:
    """
    具有自动 402 支付处理的 HTTP 客户端适配器。

    封装 httpx.AsyncClient 以自动处理 402 需要支付响应。
    """

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        x402_client: X402Client,
        selector: PaymentRequirementsSelector | None = None,
    ) -> None:
        """
        初始化 HTTP 客户端适配器。

        参数:
            http_client: httpx.AsyncClient 实例
            x402_client: X402Client 实例
            selector: 自定义支付要求选择器（可选）
        """
        self._http_client = http_client
        self._x402_client = x402_client
        self._selector = selector

    async def request_with_payment(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        发起具有自动 402 支付处理的 HTTP 请求。

        参数:
            method: HTTP 方法（GET、POST 等）
            url: 请求 URL
            **kwargs: 额外的 httpx 请求参数

        返回:
            httpx.Response

        流程:
            1. 发送原始请求
            2. 如果是 402，解析 PaymentRequired
            3. 创建支付载荷
            4. 使用 PAYMENT-SIGNATURE 头重试
        """
        response = await self._http_client.request(method, url, **kwargs)

        if response.status_code != 402:
            return response

        payment_required = self._parse_payment_required(response)
        if payment_required is None:
            return response

        extensions_dict = None
        if payment_required.extensions:
            extensions_dict = payment_required.extensions.model_dump(by_alias=True)

        payment_payload = await self._x402_client.handle_payment(
            payment_required.accepts,
            url,
            extensions_dict,
            self._selector,
        )

        return await self._retry_with_payment(method, url, payment_payload, kwargs)

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """带支付处理的 GET 请求"""
        return await self.request_with_payment("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """带支付处理的 POST 请求"""
        return await self.request_with_payment("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """带支付处理的 PUT 请求"""
        return await self.request_with_payment("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """带支付处理的 DELETE 请求"""
        return await self.request_with_payment("DELETE", url, **kwargs)

    def _parse_payment_required(self, response: httpx.Response) -> PaymentRequired | None:
        """从 402 响应解析 PaymentRequired"""
        header_value = response.headers.get(PAYMENT_REQUIRED_HEADER)
        if header_value:
            try:
                return decode_payment_payload(header_value, PaymentRequired)
            except Exception:
                pass

        try:
            body = response.json()
            if "accepts" in body and isinstance(body["accepts"], list):
                return PaymentRequired(**body)
        except Exception:
            pass

        return None

    async def _retry_with_payment(
        self,
        method: str,
        url: str,
        payment_payload: PaymentPayload,
        kwargs: dict[str, Any],
    ) -> httpx.Response:
        """使用支付载荷重试请求"""
        encoded_payload = encode_payment_payload(payment_payload)

        headers = dict(kwargs.get("headers", {}))
        headers[PAYMENT_SIGNATURE_HEADER] = encoded_payload
        kwargs["headers"] = headers

        return await self._http_client.request(method, url, **kwargs)
