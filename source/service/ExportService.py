import os
import json
import datetime
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel
from source.utils.Constants import EXPORT_FOLDER_PATH
from source.utils.Console import Terminal

class ExportService:
    def __init__(self, client: TelegramClient):
        self.client = client
        self.console = Terminal.console

    async def export_chat(self, chat_id: int, format_type: str = 'json', limit: int = None):
        """Exports chat history to a file."""
        try:
            chat = await self.client.get_entity(chat_id)
            chat_name = getattr(chat, 'title', getattr(chat, 'username', str(chat_id))) or str(chat_id)
            
            # Sanitize filename
            safe_name = "".join([c for c in chat_name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs(EXPORT_FOLDER_PATH, exist_ok=True)
            
            filename = f"{EXPORT_FOLDER_PATH}/{safe_name}_{timestamp}.{format_type}"
            
            messages = []
            self.console.print(f"[cyan]Starting export for {chat_name}...[/cyan]")
            
            count = 0
            async for message in self.client.iter_messages(chat, limit=limit):
                msg_data = {
                    "id": message.id,
                    "date": message.date.isoformat(),
                    "sender_id": message.sender_id,
                    "text": message.text,
                    "reply_to_msg_id": message.reply_to_msg_id,
                    "media": bool(message.media)
                }
                messages.append(msg_data)
                count += 1
                if count % 100 == 0:
                    print(f"Fetched {count} messages...", end='\r')

            if format_type == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, ensure_ascii=False, indent=4)
            elif format_type == 'txt':
                with open(filename, 'w', encoding='utf-8') as f:
                    for msg in messages:
                        sender = msg['sender_id'] or "Unknown"
                        date = msg['date']
                        text = msg['text'] or "[Media/Empty]"
                        f.write(f"[{date}] {sender}: {text}\n")
            
            self.console.print(f"\n[bold green]Export completed! saved to {filename}[/bold green]")
            return filename

        except Exception as e:
            self.console.print(f"[bold red]Error exporting chat: {e}[/bold red]")
            return None

