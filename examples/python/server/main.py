import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from x402.server import X402Server
from x402.fastapi import x402_protected

load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

app = FastAPI()
server = X402Server()

@app.get("/protected")
@x402_protected(
    server=server,
    price="0.001 USDT",
    network=os.getenv("TRON_NETWORK", "tron:shasta"),
    pay_to=os.getenv("TRON_PAYEE_ADDRESS", "")
)
async def protected_endpoint():
    return {"message": "Success"}
