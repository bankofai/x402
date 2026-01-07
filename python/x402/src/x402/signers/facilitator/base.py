"""
Facilitator 签名器基础接口
"""

from abc import ABC, abstractmethod
from typing import Any


class FacilitatorSigner(ABC):
    """
    Facilitator 签名器的抽象基类

    负责验证签名和执行链上交易
    """

    @abstractmethod
    def get_address(self) -> str:
        """获取 facilitator 的账户地址"""
        pass

    @abstractmethod
    async def verify_typed_data(
        self,
        address: str,
        domain: dict[str, Any],
        types: dict[str, Any],
        message: dict[str, Any],
        signature: str,
    ) -> bool:
        """
        验证 EIP-712 类型化数据签名

        Args:
            address: 预期的签名者地址
            domain: EIP-712 域
            types: 类型定义
            message: 已签名的消息
            signature: 要验证的签名

        Returns:
            如果签名有效则返回 True
        """
        pass

    @abstractmethod
    async def write_contract(
        self,
        contract_address: str,
        abi: str,
        method: str,
        args: list[Any],
    ) -> str | None:
        """
        执行合约写入交易

        Args:
            contract_address: 合约地址
            abi: 合约 ABI（JSON 字符串）
            method: 方法名称
            args: 方法参数

        Returns:
            交易哈希，失败则返回 None
        """
        pass

    @abstractmethod
    async def wait_for_transaction_receipt(
        self,
        tx_hash: str,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """
        等待交易确认

        Args:
            tx_hash: 交易哈希
            timeout: 超时时间（秒）

        Returns:
            交易回执
        """
        pass
