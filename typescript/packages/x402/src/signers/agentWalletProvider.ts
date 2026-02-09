/**
 * Helpers for constructing agent-wallet providers without direct wallet imports.
 */

export interface TronProviderOptions {
  fullNode?: string;
  solidityNode?: string;
  eventServer?: string;
  privateKey?: string;
  keystore?: {
    path?: string;
  } | unknown;
}

export async function createTronProvider(options: TronProviderOptions = {}): Promise<any> {
  // @ts-ignore agent-wallet is an optional dependency
  const { TronProvider } = await import('agent-wallet/wallet');
  const provider = new TronProvider(options);
  await provider.init();
  return provider;
}
