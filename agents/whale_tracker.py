"""
Orin.LAB · Whale Tracker
Monitor large Solana wallet movements and alert on significant transactions.
"""

from __future__ import annotations

import asyncio
import httpx
from dataclasses import dataclass
from typing import Callable, Awaitable, Optional
from utils.logger import get_logger
from utils.helpers import format_price, shorten_address, sol_explorer_url

logger = get_logger("whale_tracker")

SOLANA_RPC = "https://api.mainnet-beta.solana.com"
JUPITER_PRICE_API = "https://price.jup.ag/v6/price"
SOL_MINT = "So11111111111111111111111111111111111111112"

# Minimum USD value to trigger a whale alert
WHALE_THRESHOLD_USD = 50_000

KNOWN_WHALES: dict[str, str] = {
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Jump Crypto",
    "FWznbcNXWQuHTawe9RxvQ2LdCENssh12dsznf4RiouN5": "Alameda (dormant)",
    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Binance Hot Wallet",
}


@dataclass
class WhaleAlert:
    wallet: str
    label: str
    signature: str
    sol_amount: float
    usd_value: float
    direction: str          # "IN" or "OUT"
    message: str


WhaleHandler = Callable[[WhaleAlert], Awaitable[None]]


def _sol_price() -> float:
    try:
        resp = httpx.get(f"{JUPITER_PRICE_API}?ids={SOL_MINT}", timeout=8)
        resp.raise_for_status()
        return float(resp.json()["data"].get(SOL_MINT, {}).get("price", 0))
    except Exception:
        return 0.0


def _get_signatures(wallet: str, limit: int = 10) -> list[dict]:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [wallet, {"limit": limit}],
    }
    try:
        resp = httpx.post(SOLANA_RPC, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json().get("result", [])
    except Exception as exc:
        logger.warning(f"getSignaturesForAddress failed for {wallet}: {exc}")
        return []


def _get_transaction(sig: str) -> Optional[dict]:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [sig, {"encoding": "json", "maxSupportedTransactionVersion": 0}],
    }
    try:
        resp = httpx.post(SOLANA_RPC, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json().get("result")
    except Exception:
        return None


def _parse_sol_change(tx: dict, wallet: str) -> Optional[float]:
    """Return net SOL change (lamports→SOL) for wallet in this tx."""
    try:
        accounts = tx["transaction"]["message"]["accountKeys"]
        pre = tx["meta"]["preBalances"]
        post = tx["meta"]["postBalances"]
        for i, acc in enumerate(accounts):
            addr = acc if isinstance(acc, str) else acc.get("pubkey", "")
            if addr == wallet:
                return (post[i] - pre[i]) / 1e9
    except Exception:
        pass
    return None


class WhaleTracker:
    """
    Polls a list of whale wallets for new large transactions.
    Fires registered async handlers when a whale alert is detected.
    """

    def __init__(
        self,
        wallets: Optional[dict[str, str]] = None,
        threshold_usd: float = WHALE_THRESHOLD_USD,
        poll_interval: float = 60.0,
    ):
        self.wallets = wallets or KNOWN_WHALES
        self.threshold_usd = threshold_usd
        self.poll_interval = poll_interval
        self._seen_sigs: set[str] = set()
        self._handlers: list[WhaleHandler] = []
        self._running = False

    def register(self, handler: WhaleHandler) -> None:
        self._handlers.append(handler)

    async def _fire(self, alert: WhaleAlert) -> None:
        for handler in self._handlers:
            try:
                await handler(alert)
            except Exception as exc:
                logger.error(f"Whale handler error: {exc}")

    def add_wallet(self, address: str, label: str = "Unknown") -> None:
        self.wallets[address] = label
        logger.info(f"Watching wallet: {label} ({shorten_address(address)})")

    async def check_wallet(self, wallet: str, label: str, sol_price: float) -> list[WhaleAlert]:
        alerts = []
        sigs = await asyncio.get_event_loop().run_in_executor(
            None, _get_signatures, wallet, 5
        )
        for entry in sigs:
            sig = entry.get("signature", "")
            if sig in self._seen_sigs or entry.get("err"):
                continue
            self._seen_sigs.add(sig)

            tx = await asyncio.get_event_loop().run_in_executor(
                None, _get_transaction, sig
            )
            if not tx:
                continue

            change = _parse_sol_change(tx, wallet)
            if change is None:
                continue

            usd_value = abs(change) * sol_price
            if usd_value < self.threshold_usd:
                continue

            direction = "IN" if change > 0 else "OUT"
            short = shorten_address(wallet)
            alert = WhaleAlert(
                wallet=wallet,
                label=label,
                signature=sig,
                sol_amount=abs(change),
                usd_value=usd_value,
                direction=direction,
                message=(
                    f"🐋 *Whale Alert — {label}*\n"
                    f"`{short}` moved *{abs(change):,.1f} SOL* "
                    f"(~{format_price(usd_value, 0)}) {direction}\n"
                    f"[View tx]({sol_explorer_url(sig)})"
                ),
            )
            await self._fire(alert)
            alerts.append(alert)
            logger.info(f"Whale alert: {label} {direction} {abs(change):.1f} SOL (${usd_value:,.0f})")

        return alerts

    async def run(self) -> None:
        self._running = True
        logger.info(f"WhaleTracker started — watching {len(self.wallets)} wallets")
        while self._running:
            sol_price = await asyncio.get_event_loop().run_in_executor(None, _sol_price)
            tasks = [
                self.check_wallet(addr, label, sol_price)
                for addr, label in self.wallets.items()
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(self.poll_interval)

    def stop(self) -> None:
        self._running = False