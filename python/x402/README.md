# tvm-x402

Python SDK for the x402 payment protocol (TRON-only).

## Installation

```bash
pip install tvm-x402
```

Optional extras:

```bash
pip install "tvm-x402[tron]"
pip install "tvm-x402[fastapi]"
pip install "tvm-x402[flask]"
pip install "tvm-x402[all]"
```

## Quick Start

```python
from x402.clients import X402Client

client = X402Client()
```

If you want automatic handling of HTTP 402 responses, use `X402HttpClient`:

```python
import httpx

from x402.clients import X402Client, X402HttpClient

x402_client = X402Client()
http_client = httpx.AsyncClient()
client = X402HttpClient(http_client=http_client, x402_client=x402_client)
```

## Links

- Repository: https://github.com/sun-protocol/tvm-x402
- Issues: https://github.com/sun-protocol/tvm-x402/issues
