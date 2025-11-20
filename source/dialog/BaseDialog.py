from InquirerPy import inquirer
from source.utils.Console import Terminal
from rich.markup import render

class BaseDialog:
    def __init__(self):
        self.console = Terminal.console

    async def show_options(self, message, options):
        return await inquirer.select(message=message, choices=options).execute_async()

    async def show_checkbox(self, message, options):
        """Show multi-select checkbox."""
        return await inquirer.checkbox(
            message=message,
            choices=options,
            cycle=False,
            transformer=lambda result: f"{len(result)} selected"
        ).execute_async()

    async def show_input(self, message):
        """Show text input."""
        return await inquirer.text(message=message).execute_async()

    def clear(self):
        self.console.clear()

    async def list_chats_terminal(self, chats, type_label):
        """Shows a list of chats for selection."""
        options = [{"name": "↩ Back to Menu", "value": "-1"}]
        
        for i, chat in enumerate(chats):
            options.append({
                "name": chat.get_plain_display_name(),
                "value": str(i)
            })

        choice = await self.show_options(f"Select {type_label} channel", options)
        return int(choice)

    async def select_multiple_chats(self, chats, message="Select chats:"):
        """Shows a list of chats for multi-selection."""
        options = []
        for i, chat in enumerate(chats):
            options.append({
                "name": chat.get_plain_display_name(),
                "value": chat
            })
            
        return await self.show_checkbox(message, options)
