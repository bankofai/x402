/**
 * Adapter that bridges agent-wallet providers to the KeyProvider interface.
 */

import type { KeyProvider } from './keyProvider.js';

/**
 * Adapt agent-wallet's TronProvider (or FlashProvider) to KeyProvider.
 *
 * Reads `address` and `tronWeb.defaultPrivateKey` from the provider.
 *
 * Normally you don't use this directly — `AgentWalletClientSigner`
 * wraps it automatically:
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
export class TronProviderAdapter implements KeyProvider {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private provider: any;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  constructor(provider: any) {
    this.provider = provider;
  }

  getAddress(): string {
    const addr = this.provider.address;
    if (!addr) {
      throw new Error('Provider has no address (private key not set?)');
    }
    return addr as string;
  }

  getPrivateKey(): string {
    const pk: string | undefined = this.provider.tronWeb?.defaultPrivateKey;
    if (!pk) {
      throw new Error('Provider has no private key');
    }
    return pk.startsWith('0x') ? pk.slice(2) : pk;
  }
}
