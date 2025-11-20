from source.dialog.BaseDialog import BaseDialog
from source.model.Chat import Chat

class ExportDialog(BaseDialog):
    async def get_config(self):
        """Get export configuration from user.
        
        Returns:
            tuple: (chat, format_type) or None if cancelled
        """
        self.clear()
        
        # Ensure we have chats to list (this relies on chats.json being populated)
        # If empty, the user might need to run "List Chats" first.
        chats = Chat.read()
        if not chats:
            self.console.print("[yellow]No chats found. Please run 'List Chats' first.[/yellow]")
            return None

        chat_index = await self.list_chats_terminal(chats, "chat to export")
        if chat_index == -1:
            return None
            
        selected_chat = chats[chat_index]
        
        format_options = [
            {"name": "JSON (Complete data)", "value": "json"},
            {"name": "Text (Readable)", "value": "txt"},
            {"name": "↩ Back to Menu", "value": "back"}
        ]
        
        format_type = await self.show_options("Select export format:", format_options)
        
        if format_type == "back":
            return None
            
        return selected_chat, format_type
