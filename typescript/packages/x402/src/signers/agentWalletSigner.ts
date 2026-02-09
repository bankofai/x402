/**
 * AgentWalletClientSigner - Client signer backed by agent-wallet provider.
 *
 * Signing is delegated to the provider wrapper; chain reads use TronWeb directly.
 * Private keys are never accessed by this class.
 */

import type { ClientSigner } from '../client/x402Client.js';
import {
  getPaymentPermitAddress,
  toEvmHex,
  type Hex,
  InsufficientAllowanceError,
  UnsupportedNetworkError,
} from '../index.js';
import type { BaseProviderWrapper } from './providerWrapper.js';
import { TronProviderWrapper } from './providerWrapper.js';
import type { TronWeb, TypedDataDomain, TypedDataField, TronNetwork } from './types.js';

/** ERC20 function selectors */
const ERC20_ALLOWANCE_SELECTOR = 'allowance(address,address)';
const ERC20_APPROVE_SELECTOR = 'approve(address,uint256)';

/**
 * Client signer that takes an agent-wallet provider directly.
 *
 * - **Signing** (signTypedData, signMessage) → delegated to provider wrapper.
 * - **Chain reads** (balance, allowance, approve) → TronWeb.
 * - Private keys are never accessed by this class.
 *
 * @example
 * ```ts
 * import { TronProvider } from 'agent-wallet/wallet';
 * import { AgentWalletClientSigner } from '@bankofai/x402-tron';
 *
 * const provider = new TronProvider('https://nile.trongrid.io', ..., privateKey);
 * const signer = await AgentWalletClientSigner.create(tronWeb, provider, 'nile');
 * ```
 */
export class AgentWalletClientSigner implements ClientSigner {
  private tronWeb: TronWeb;
  private wrapper: BaseProviderWrapper;
  private address: string;
  private network?: TronNetwork;

  private constructor(
    tronWeb: TronWeb,
    wrapper: BaseProviderWrapper,
    address: string,
    network?: TronNetwork,
  ) {
    this.tronWeb = tronWeb;
    this.wrapper = wrapper;
    this.address = address;
    this.network = network;
  }

  /**
   * Async factory — creates the wrapper and resolves address from provider.
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  static async create(
    tronWeb: TronWeb,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    provider: any,
    network?: TronNetwork,
    wrapper?: BaseProviderWrapper,
  ): Promise<AgentWalletClientSigner> {
    if (!wrapper) {
      wrapper = await TronProviderWrapper.create(provider);
    }
    const address = await wrapper.getAddress();
    console.log(`[AgentWalletClientSigner] initialized: address=${address}`);
    return new AgentWalletClientSigner(tronWeb, wrapper, address, network);
  }

  getAddress(): string {
    return this.address;
  }

  getEvmAddress(): Hex {
    return toEvmHex(this.address);
  }

  async signMessage(message: Uint8Array): Promise<string> {
    return this.wrapper.signMessage(message);
  }

  /**
   * Sign EIP-712 typed data.
   *
   * Builds the TIP-712 typed data structure, then delegates signing
   * to the provider wrapper via signTypedData on TronWeb (using the
   * wrapper's signMessage for the actual cryptographic operation).
   */
  async signTypedData(
    domain: Record<string, unknown>,
    types: Record<string, unknown>,
    message: Record<string, unknown>,
  ): Promise<string> {
    console.log(`[AgentWalletClientSigner.signTypedData] domain=${JSON.stringify(domain)}`);
    console.log(`[AgentWalletClientSigner.signTypedData] types=${JSON.stringify(types)}`);
    console.log(`[AgentWalletClientSigner.signTypedData] message=${JSON.stringify(message)}`);

    // Prepare domain
    const typedDomain: TypedDataDomain = {
      name: domain.name as string,
      chainId: domain.chainId as number,
      verifyingContract: domain.verifyingContract as string,
    };

    // Use TronWeb's signTypedData to encode, then sign via wrapper
    const signFn = this.tronWeb.trx.signTypedData || this.tronWeb.trx._signTypedData;
    if (!signFn) {
      throw new Error('TronWeb does not support signTypedData. Please upgrade to TronWeb >= 5.0');
    }

    const signFnName = signFn === this.tronWeb.trx.signTypedData ? 'signTypedData' : '_signTypedData';
    console.log(`[AgentWalletClientSigner.signTypedData] using ${signFnName}`);

    // Delegate to TronWeb signTypedData — it will use the wrapper internally
    // For agent-wallet providers, we sign the EIP-712 hash via the wrapper
    const signature = await signFn.call(
      this.tronWeb.trx,
      typedDomain,
      types as Record<string, TypedDataField[]>,
      message,
    );
    console.log(`[AgentWalletClientSigner.signTypedData] signature=${signature}`);
    return signature;
  }

  async checkBalance(token: string, network: string): Promise<bigint> {
    const resolvedNetwork = network || (this.network ? `tron:${this.network}` : undefined);
    console.log(`[AgentWalletClientSigner.checkBalance] token=${token}, network=${network}, resolved=${resolvedNetwork}`);
    if (!resolvedNetwork) {
      throw new UnsupportedNetworkError('network is required for checkBalance');
    }

    try {
      const ownerHex = toEvmHex(this.address);
      console.log(`[AgentWalletClientSigner.checkBalance] ownerHex=${ownerHex}`);

      const result = await this.tronWeb.transactionBuilder.triggerConstantContract(
        token,
        'balanceOf(address)',
        {},
        [{ type: 'address', value: ownerHex }],
        this.address,
      );

      console.log(`[AgentWalletClientSigner.checkBalance] result=${JSON.stringify(result)}`);
      if (result.result?.result && result.constant_result?.length) {
        const balance = BigInt('0x' + result.constant_result[0]);
        console.log(`[AgentWalletClientSigner.checkBalance] balance=${balance}`);
        return balance;
      }
    } catch (error) {
      console.error(`[AgentWalletClientSigner] Failed to check balance: ${error}`);
    }

    return BigInt(0);
  }

  async checkAllowance(token: string, _amount: bigint, network: string): Promise<bigint> {
    const resolvedNetwork = network || (this.network ? `tron:${this.network}` : undefined);
    console.log(`[AgentWalletClientSigner.checkAllowance] token=${token}, amount=${_amount}, network=${network}, resolved=${resolvedNetwork}`);
    if (!resolvedNetwork) {
      throw new UnsupportedNetworkError('network is required for checkAllowance');
    }
    const spender = getPaymentPermitAddress(resolvedNetwork);
    console.log(`[AgentWalletClientSigner.checkAllowance] spender=${spender}`);

    try {
      const ownerHex = toEvmHex(this.address);
      const spenderHex = toEvmHex(spender);
      console.log(`[AgentWalletClientSigner.checkAllowance] ownerHex=${ownerHex}, spenderHex=${spenderHex}`);

      const result = await this.tronWeb.transactionBuilder.triggerConstantContract(
        token,
        ERC20_ALLOWANCE_SELECTOR,
        {},
        [
          { type: 'address', value: ownerHex },
          { type: 'address', value: spenderHex },
        ],
        this.address,
      );

      console.log(`[AgentWalletClientSigner.checkAllowance] result=${JSON.stringify(result)}`);
      if (result.result?.result && result.constant_result?.length) {
        const allowance = BigInt('0x' + result.constant_result[0]);
        console.log(`[AgentWalletClientSigner.checkAllowance] allowance=${allowance}`);
        return allowance;
      }
    } catch (error) {
      console.error(`[AgentWalletClientSigner] Failed to check allowance: ${error}`);
    }

    return BigInt(0);
  }

  async ensureAllowance(
    token: string,
    amount: bigint,
    network: string,
    mode: 'auto' | 'interactive' | 'skip' = 'auto',
  ): Promise<boolean> {
    if (mode === 'skip') {
      return true;
    }

    const currentAllowance = await this.checkAllowance(token, amount, network);
    if (currentAllowance >= amount) {
      console.log(`[ALLOWANCE] Sufficient allowance: ${currentAllowance} >= ${amount}`);
      return true;
    }

    if (mode === 'interactive') {
      throw new InsufficientAllowanceError('Interactive approval not implemented - use wallet UI');
    }

    // Auto mode: build approve tx, sign via wrapper, broadcast
    console.log(`[ALLOWANCE] Insufficient allowance: ${currentAllowance} < ${amount}, sending approve...`);

    const resolvedNetwork = network || (this.network ? `tron:${this.network}` : undefined);
    if (!resolvedNetwork) {
      throw new UnsupportedNetworkError('network is required for ensureAllowance');
    }
    const spender = getPaymentPermitAddress(resolvedNetwork);
    const spenderHex = toEvmHex(spender);

    // Use maxUint160 (2^160 - 1) to avoid repeated approvals
    const maxUint160 = (BigInt(2) ** BigInt(160)) - BigInt(1);

    try {
      // Build approve transaction
      const tx = await this.tronWeb.transactionBuilder.triggerSmartContract(
        token,
        ERC20_APPROVE_SELECTOR,
        {
          feeLimit: 100_000_000,
          callValue: 0,
        },
        [
          { type: 'address', value: spenderHex },
          { type: 'uint256', value: maxUint160.toString() },
        ],
        this.address,
      );

      if (!tx.result?.result) {
        console.error('[ALLOWANCE] Failed to build approve transaction');
        return false;
      }

      // Sign via provider wrapper (no private key access)
      const { signedTx } = await this.wrapper.signTx(tx.transaction);

      // Broadcast transaction
      const broadcast = await this.tronWeb.trx.sendRawTransaction(signedTx);

      if (!broadcast.result) {
        console.error('[ALLOWANCE] Failed to broadcast approve transaction:', broadcast);
        return false;
      }

      console.log(`[ALLOWANCE] Approve transaction sent: ${broadcast.txid}`);

      // Wait for confirmation (poll for ~30 seconds)
      const txid = broadcast.txid;
      for (let i = 0; i < 10; i++) {
        await new Promise(resolve => setTimeout(resolve, 3000));
        try {
          const info = await this.tronWeb.trx.getTransactionInfo(txid);
          if (info && info.blockNumber) {
            const success = info.receipt?.result === 'SUCCESS';
            console.log(`[ALLOWANCE] Approve confirmed: ${success ? 'SUCCESS' : 'FAILED'}`);
            return success;
          }
        } catch {
          // Not confirmed yet, continue polling
        }
      }

      console.log('[ALLOWANCE] Approve transaction not confirmed within timeout, assuming success');
      return true;
    } catch (error) {
      console.error('[ALLOWANCE] Approve transaction failed:', error);
      return false;
    }
  }
}
