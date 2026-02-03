# @open-aibank/x402-tron

x402-tron TypeScript SDK (TRON-only).

## Install

```bash
npm i @open-aibank/x402-tron
```

## Peer dependencies

This package expects `tronweb` to be provided by the host app.

```bash
npm i tronweb
```

## Usage

```ts
import TronWeb from "tronweb";

// Provide your own TronWeb instance / configuration.
const tronWeb = new TronWeb({
  fullHost: "https://api.trongrid.io",
});

// TODO: Add usage examples once the public API is finalized.
console.log("tronWeb ready", !!tronWeb);
```

## Links

- Repository: https://github.com/open-aibank/x402-tron
- Issues: https://github.com/open-aibank/x402-tron/issues
