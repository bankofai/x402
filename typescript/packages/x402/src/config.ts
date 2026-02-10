/**
 * Network configuration for x402 protocol
 * Centralized configuration for contract addresses and chain IDs
 */

import { UnsupportedNetworkError } from './errors.js';

/** Chain IDs for supported networks */
export const CHAIN_IDS: Record<string, number> = {
  // TRON networks
  'tron:mainnet': 728126428,   // 0x2b6653dc
  'tron:shasta': 2494104990,   // 0x94a9059e
  'tron:nile': 3448148188,     // 0xcd8690dc
};

/** PaymentPermit contract addresses */
export const PAYMENT_PERMIT_ADDRESSES: Record<string, string> = {
  'tron:mainnet': 'TT8rEWbCoNX7vpEUauxb7rWJsTgs8vDLAn',
  'tron:shasta': 'TR2XninQ3jsvRRLGTifFyUHTBysffooUjt',
  'tron:nile': 'TFxDcGvS7zfQrS1YzcCMp673ta2NHHzsiH',
};

/** Zero address for TRON */
export const TRON_ZERO_ADDRESS = 'T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb';

/** Zero address for EVM */
export const EVM_ZERO_ADDRESS = '0x0000000000000000000000000000000000000000';

/**
 * Get chain ID for network
 */
export function getChainId(network: string): number {
  // EVM networks encode chain ID directly in the identifier
  if (network.startsWith('eip155:')) {
    const id = parseInt(network.split(':')[1], 10);
    if (isNaN(id)) {
      throw new UnsupportedNetworkError(`Invalid EVM network: ${network}`);
    }
    return id;
  }

  const chainId = CHAIN_IDS[network];
  if (chainId === undefined) {
    throw new UnsupportedNetworkError(`Unsupported network: ${network}`);
  }
  return chainId;
}

/**
 * Get PaymentPermit contract address for network
 */
export function getPaymentPermitAddress(network: string): string {
  const addr = PAYMENT_PERMIT_ADDRESSES[network];
  if (addr) return addr;
  // EVM fallback: zero address (not yet deployed)
  if (network.startsWith('eip155:')) return EVM_ZERO_ADDRESS;
  return TRON_ZERO_ADDRESS;
}

/**
 * Check if network is TRON
 */
export function isTronNetwork(network: string): boolean {
  return network.startsWith('tron:');
}

/**
 * Check if network is EVM
 */
export function isEvmNetwork(network: string): boolean {
  return network.startsWith('eip155:');
}

/**
 * Get zero address for network
 */
export function getZeroAddress(network: string): string {
  if (isEvmNetwork(network)) return EVM_ZERO_ADDRESS;
  if (isTronNetwork(network)) return TRON_ZERO_ADDRESS;
  throw new UnsupportedNetworkError(`Unsupported network: ${network}`);
}
