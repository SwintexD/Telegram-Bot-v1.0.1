from source.dialog.BaseDialog import BaseDialog
from source.model.Chat import Chat

class BroadcastDialog(BaseDialog):
    async def get_config(self):
        """Get broadcast configuration from user.
        
        Returns:
            tuple: (selected_chats, message_text) or None if cancelled
        """
        while True:
            self.clear()
            
            chats = Chat.read()
            if not chats:
                self.console.print("[yellow]No chats found. Please run 'List Chats' first.[/yellow]")
                return None

            selected_chats = await self.select_multiple_chats(chats, "Select destination chats (Space to select, Enter to confirm):")
            
            if not selected_chats:
                # If no chats selected, assume cancellation/back
                return None
                
            message_text = await self.show_input("Enter message to broadcast (or type 'BACK' to re-select chats):")
            
            if not message_text:
                self.console.print("[yellow]Message cannot be empty.[/yellow]")
                await asyncio.sleep(1)
                continue
                
            if message_text.strip().upper() == 'BACK':
                continue
                
            return selected_chats, message_text
