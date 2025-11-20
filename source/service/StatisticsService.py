import os
import json
from source.utils.Console import Terminal
from source.model.Chat import Chat
from source.model.ForwardConfig import ForwardConfig
from source.utils.Constants import MEDIA_FOLDER_PATH, CHAT_FILE_PATH, FORWARD_CONFIG_FILE_PATH

class StatisticsService:
    def __init__(self):
        self.console = Terminal.console

    def get_directory_size(self, path):
        """Returns size of directory in MB."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0

    async def show_statistics(self, client):
        """Collects and displays statistics."""
        self.console.clear()
        self.console.print("[bold cyan]📊 Bot Statistics[/bold cyan]\n")

        # User Info
        try:
            me = await client.get_me()
            name = f"{me.first_name} {me.last_name if me.last_name else ''}".strip()
            self.console.print(f"[bold]User:[/bold] {name} [dim](ID: {me.id})[/dim]")
            self.console.print(f"[bold]Phone:[/bold] {me.phone}")
            self.console.print("─" * 30)
        except Exception as e:
            self.console.print(f"[red]Could not fetch user info: {e}[/red]")

        # Chats Stats
        try:
            if os.path.exists(CHAT_FILE_PATH):
                chats = Chat.read()
                total_chats = len(chats)
                channels = len([c for c in chats if c.type == "Channel"])
                groups = len([c for c in chats if c.type == "Group"])
                users = len([c for c in chats if c.type == "User"])
                
                self.console.print(f"[bold]Total Cached Chats:[/bold] {total_chats}")
                self.console.print(f"  • Channels: {channels}")
                self.console.print(f"  • Groups: {groups}")
                self.console.print(f"  • Users: {users}")
            else:
                self.console.print("[yellow]No cached chats found.[/yellow]")
        except Exception:
            self.console.print("[red]Error reading chat stats.[/red]")

        # Forward Config Stats
        try:
            if os.path.exists(FORWARD_CONFIG_FILE_PATH):
                configs = ForwardConfig.read()
                self.console.print(f"\n[bold]Active Forward Rules:[/bold] {len(configs)}")
            else:
                self.console.print("\n[bold]Active Forward Rules:[/bold] 0")
        except Exception:
             self.console.print("[red]Error reading forward config.[/red]")

        # Storage Stats
        media_size = self.get_directory_size(MEDIA_FOLDER_PATH)
        self.console.print(f"\n[bold]Media Storage:[/bold] {media_size:.2f} MB")
        
        self.console.print("\nPress Enter to return to menu...")
        input()

