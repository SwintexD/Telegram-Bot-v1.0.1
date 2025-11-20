from source.dialog.BaseDialog import BaseDialog
from source.model.Chat import Chat

class CloneDialog(BaseDialog):
    async def get_config(self):
        """Get clone configuration from user.
        
        Returns:
            tuple: (source_chat, destination_chat) or None if cancelled
        """
        while True:
            self.clear()
            
            chats = Chat.read()
            if not chats:
                self.console.print("[yellow]No chats found. Please run 'List Chats' first.[/yellow]")
                return None

            # Select Source
            source_index = await self.list_chats_terminal(chats, "SOURCE (Copy from)")
            if source_index == -1:
                return None
            source_chat = chats[source_index]
            
            # Select Destination
            dest_index = await self.list_chats_terminal(chats, f"DESTINATION (Paste to, copying from {source_chat.title})")
            if dest_index == -1:
                continue # Go back to start of loop (re-select source)
                
            dest_chat = chats[dest_index]
            
            # Confirm
            confirm = await self.show_options(
                f"Confirm cloning from '{source_chat.title}' to '{dest_chat.title}'?",
                [
                    {"name": "Yes, start cloning", "value": "yes"},
                    {"name": "No, re-select", "value": "no"},
                    {"name": "Cancel", "value": "cancel"}
                ]
            )
            
            if confirm == "yes":
                return source_chat, dest_chat
            elif confirm == "cancel":
                return None
            # If no, loop repeats

