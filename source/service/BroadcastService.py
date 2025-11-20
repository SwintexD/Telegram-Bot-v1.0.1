import asyncio
from telethon import TelegramClient
from source.utils.Console import Terminal
from source.model.Chat import Chat

class BroadcastService:
    def __init__(self, client: TelegramClient):
        self.client = client
        self.console = Terminal.console

    async def send_broadcast(self, chats: list[Chat], message_text: str):
        """Sends a message to multiple chats."""
        if not chats:
            self.console.print("[yellow]No chats selected.[/yellow]")
            return

        self.console.print(f"[bold cyan]Starting broadcast to {len(chats)} chats...[/bold cyan]")
        
        success_count = 0
        fail_count = 0

        for chat in chats:
            try:
                self.console.print(f"Sending to [blue]{chat.title}[/blue]...")
                await self.client.send_message(chat.id, message_text)
                success_count += 1
                # Small delay to avoid flood limits
                await asyncio.sleep(1) 
            except Exception as e:
                self.console.print(f"[red]Failed to send to {chat.title}: {e}[/red]")
                fail_count += 1
        
        self.console.print("\n[bold]Broadcast Report:[/bold]")
        self.console.print(f"[green]Success: {success_count}[/green]")
        if fail_count > 0:
            self.console.print(f"[red]Failed: {fail_count}[/red]")
        self.console.print("─" * 30)

