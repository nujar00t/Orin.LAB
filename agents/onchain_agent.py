"""
Orin.LAB · On-chain Agent
Monitor Solana wallets, transactions, and on-chain activity.
"""

import os
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box

console = Console()

RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

KNOWN_WALLETS = {
    "Jump Trading":    "3oSE59Y4jBGCFpFuzpuK5UWrfNn3TaAPWmyMzrxWnYpC",
    "Alameda (old)":  "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
}


def rpc_call(method: str, params: list) -> dict:
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    try:
        resp = httpx.post(RPC_URL, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json().get("result", {})
    except Exception as e:
        return {"error": str(e)}


def get_balance(address: str) -> float:
    result = rpc_call("getBalance", [address])
    if isinstance(result, dict) and "value" in result:
        return result["value"] / 1e9
    return 0.0


def get_recent_transactions(address: str, limit: int = 5) -> list:
    result = rpc_call("getSignaturesForAddress", [address, {"limit": limit}])
    if isinstance(result, list):
        return result
    return []


def get_token_accounts(address: str) -> list:
    result = rpc_call("getTokenAccountsByOwner", [
        address,
        {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
        {"encoding": "jsonParsed"}
    ])
    if isinstance(result, dict) and "value" in result:
        return result["value"]
    return []


def run():
    console.print(Panel.fit(
        "[bold cyan]Orin.LAB[/bold cyan] · [green]On-chain Agent[/green]\n"
        "[dim]Solana wallet and transaction monitor[/dim]",
        border_style="cyan"
    ))

    while True:
        console.print("\n[bold]Options:[/bold]")
        console.print("  [cyan]1[/cyan] Check wallet balance")
        console.print("  [cyan]2[/cyan] View recent transactions")
        console.print("  [cyan]3[/cyan] Monitor known wallets")
        console.print("  [cyan]q[/cyan] Quit")

        choice = Prompt.ask("\nChoose", choices=["1", "2", "3", "q"])

        if choice == "q":
            break

        elif choice == "1":
            address = Prompt.ask("Wallet address")
            with console.status("[dim]Fetching balance...[/dim]", spinner="dots"):
                balance = get_balance(address)
            console.print(f"\n[bold cyan]Balance:[/bold cyan] {balance:.4f} SOL")

        elif choice == "2":
            address = Prompt.ask("Wallet address")
            with console.status("[dim]Fetching transactions...[/dim]", spinner="dots"):
                txs = get_recent_transactions(address)

            if not txs:
                console.print("[dim]No recent transactions found.[/dim]")
            else:
                table = Table(title="Recent Transactions", border_style="cyan", box=box.ROUNDED)
                table.add_column("Signature", style="dim", width=20)
                table.add_column("Slot", justify="right")
                table.add_column("Status")

                for tx in txs:
                    sig = tx.get("signature", "")[:20] + "..."
                    slot = str(tx.get("slot", ""))
                    err = tx.get("err")
                    status = "[red]Failed[/red]" if err else "[green]Success[/green]"
                    table.add_row(sig, slot, status)

                console.print(table)

        elif choice == "3":
            table = Table(title="Known Wallets", border_style="cyan", box=box.ROUNDED)
            table.add_column("Label", style="cyan")
            table.add_column("Address", style="dim")
            table.add_column("Balance (SOL)", justify="right")

            for label, address in KNOWN_WALLETS.items():
                with console.status(f"[dim]Checking {label}...[/dim]", spinner="dots"):
                    balance = get_balance(address)
                table.add_row(label, address[:16] + "...", f"{balance:.2f}")

            console.print(table)
