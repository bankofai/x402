/**
 * AgentWalletClientSigner - Client signer backed by agent-wallet provider.
 *
 * Accepts an agent-wallet TronProvider or FlashProvider and extracts
 * the private key via TronProviderAdapter.
 */

import type { ClientSigner } from '../client/x402Client.js';
import { TronClientSigner } from './signer.js';
import type { TronWeb, TronNetwork } from './types.js';
import { TronProviderAdapter } from './adapter.js';

/**
 * Client signer that takes an agent-wallet provider directly.
 *
 * @example
 * ```ts
 * import { TronProvider } from 'agent-wallet/wallet';
 * import { AgentWalletClientSigner } from '@bankofai/x402-tron';
 *
 * const provider = new TronProvider('https://nile.trongrid.io', ..., privateKey);
 * const signer = new AgentWalletClientSigner(tronWeb, provider, 'nile');
 * ```
 */
export class AgentWalletClientSigner implements ClientSigner {
  private inner: TronClientSigner;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  constructor(tronWeb: TronWeb, provider: any, network?: TronNetwork) {
    const adapter = new TronProviderAdapter(provider);
    this.inner = TronClientSigner.withPrivateKey(
      tronWeb,
      adapter.getPrivateKey(),
      network,
    );
  }

  getAddress(): string {
    return this.inner.getAddress();
  }

  getEvmAddress() {
    return this.inner.getEvmAddress();
  }

  signMessage(message: Uint8Array): Promise<string> {
    return this.inner.signMessage(message);
  }

  signTypedData(
    domain: Record<string, unknown>,
    types: Record<string, unknown>,
    message: Record<string, unknown>,
  ): Promise<string> {
    return this.inner.signTypedData(domain, types, message);
  }

  checkBalance(token: string, network: string): Promise<bigint> {
    return this.inner.checkBalance(token, network);
  }

  checkAllowance(
    token: string,
    amount: bigint,
    network: string,
  ): Promise<bigint> {
    return this.inner.checkAllowance(token, amount, network);
  }

  ensureAllowance(
    token: string,
    amount: bigint,
    network: string,
    mode?: 'auto' | 'interactive' | 'skip',
  ): Promise<boolean> {
    return this.inner.ensureAllowance(token, amount, network, mode);
  }
}
