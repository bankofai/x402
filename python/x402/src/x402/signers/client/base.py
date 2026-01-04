"""
客户端签名器基础接口
"""

from abc import ABC, abstractmethod
from typing import Any


class ClientSigner(ABC):
    """
    客户端签名器的抽象基类

    负责签名消息和管理授权额度
    """

    @abstractmethod
    def get_address(self) -> str:
        """获取签名器的账户地址"""
        pass

    @abstractmethod
    async def sign_message(self, message: bytes) -> str:
        """
        签名原始消息

        Args:
            message: 原始消息字节

        Returns:
            签名字符串（十六进制）
        """
        pass

    @abstractmethod
    async def sign_typed_data(
        self,
        domain: dict[str, Any],
        types: dict[str, Any],
        message: dict[str, Any],
    ) -> str:
        """
        签名类型化数据（EIP-712）

        Args:
            domain: EIP-712 域
            types: 类型定义
            message: 要签名的消息

        Returns:
            签名字符串（十六进制）
        """
        pass

    @abstractmethod
    async def check_allowance(
        self,
        token: str,
        amount: int,
        network: str,
    ) -> int:
        """
        检查代币授权额度

        Args:
            token: 代币合约地址
            amount: 所需金额
            network: 网络标识符

        Returns:
            当前授权额度
        """
        pass

    @abstractmethod
    async def ensure_allowance(
        self,
        token: str,
        amount: int,
        network: str,
        mode: str = "auto",
    ) -> bool:
        """
        确保有足够的授权额度

        Args:
            token: 代币合约地址
            amount: 所需金额
            network: 网络标识符
            mode: 授权模式（auto、interactive、skip）

        Returns:
            如果授权额度足够则返回 True
        """
        pass
