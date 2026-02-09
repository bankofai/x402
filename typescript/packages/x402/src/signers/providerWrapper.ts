/**
 * Provider wrapper — thin delegation to agent-wallet's BaseProvider interface.
 *
 * The provider only provides address query and signing.
 * Chain reads (balance, allowance, contract calls) are handled by the signers
 * themselves via TronWeb.
 *
 * Interface:
 *   getAddress() -> string
 *   signTx(unsignedTx) -> { signedTx: unknown; signature?: string }
 *   signMessage(message: Uint8Array) -> string
 */

/**
 * Abstract wrapper mirroring agent-wallet's BaseProvider interface.
 *
 * The provider only handles:
 * - **Address**: `getAddress()`
 * - **Signing**: `signTx()`, `signMessage()`
 *
 * All chain reads (balance, allowance, contract calls, tx receipts) are
 * performed by the signers via a separate TronWeb client.
 */
export interface BaseProviderWrapper {
  /** Get the wallet address (TRON base58check). */
  getAddress(): Promise<string>;

  /** Sign an unsigned transaction and return the signed result. */
  signTx(unsignedTx: unknown): Promise<{ signedTx: unknown; signature?: string }>;

  /** Sign a raw message (e.g. EIP-712 hash). Returns hex-encoded signature. */
  signMessage(message: Uint8Array): Promise<string>;
}

/**
 * Wrapper for agent-wallet's TronProvider.
 *
 * @example
 * ```ts
 * import { TronProvider } from 'agent-wallet/wallet';
 * const provider = new TronProvider(...);
 * const wrapper = await TronProviderWrapper.create(provider);
 * ```
 */
export class TronProviderWrapper implements BaseProviderWrapper {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private provider: any;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private constructor(provider: any) {
    this.provider = provider;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  static async create(provider: any): Promise<TronProviderWrapper> {
    console.log(`[TronProviderWrapper.create] creating wrapper`);
    const wrapper = new TronProviderWrapper(provider);
    // Validate that the provider can return an address
    const addr = await wrapper.getAddress();
    console.log(`[TronProviderWrapper.create] validated address=${addr}`);
    return wrapper;
  }

  async getAddress(): Promise<string> {
    const info = await this.provider.getAccountInfo();
    console.log(`[TronProviderWrapper.getAddress] accountInfo=${JSON.stringify(info)}`);
    const address = info?.address;
    if (!address) {
      throw new Error('Provider returned no address from getAccountInfo()');
    }
    return address as string;
  }

  async signTx(unsignedTx: unknown): Promise<{ signedTx: unknown; signature?: string }> {
    console.log(`[TronProviderWrapper.signTx] unsignedTx=${JSON.stringify(unsignedTx)}`);
    const result = await this.provider.signTx(unsignedTx);
    console.log(`[TronProviderWrapper.signTx] result keys=${Object.keys(result)}`);
    return {
      signedTx: result.signed_tx ?? result.signedTx,
      signature: result.signature,
    };
  }

  async signMessage(message: Uint8Array): Promise<string> {
    console.log(`[TronProviderWrapper.signMessage] message length=${message.length}`);
    const sigHex: string = await this.provider.signMessage(message);
    console.log(`[TronProviderWrapper.signMessage] raw sigHex=${sigHex}`);
    // Normalize v value: some providers return v=0/1,
    // but Ethereum ecrecover and Solidity expect v=27/28.
    const raw = hexToBytes(sigHex);
    if (raw.length === 65 && raw[64] < 27) {
      raw[64] += 27;
      const normalized = bytesToHex(raw);
      console.log(`[TronProviderWrapper.signMessage] normalized v: ${raw[64] - 27} -> ${raw[64]}, sig=${normalized}`);
      return normalized;
    }
    return sigHex;
  }
}

/** Convert hex string to Uint8Array */
function hexToBytes(hex: string): Uint8Array {
  const clean = hex.startsWith('0x') ? hex.slice(2) : hex;
  const bytes = new Uint8Array(clean.length / 2);
  for (let i = 0; i < bytes.length; i++) {
    bytes[i] = parseInt(clean.substring(i * 2, i * 2 + 2), 16);
  }
  return bytes;
}

/** Convert Uint8Array to hex string (no 0x prefix) */
function bytesToHex(bytes: Uint8Array): string {
  return Array.from(bytes)
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}
