/**
 * KeyProvider - abstraction for private key management.
 *
 * Any key management backend (agent-wallet, HSM, etc.)
 * can be used with x402 signers by implementing this interface.
 */

/** Minimal interface that a key management backend must satisfy. */
export interface KeyProvider {
  /** Return the TRON base58check address. */
  getAddress(): string;
  /** Return the hex-encoded private key (without 0x prefix). */
  getPrivateKey(): string;
}
