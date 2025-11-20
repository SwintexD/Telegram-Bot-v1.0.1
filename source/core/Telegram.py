import os
import telethon
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerEmpty
from source.utils.Console import Terminal

from source.model.Chat import Chat
from source.service.Forward import Forward
from source.utils.Constants import SESSION_PREFIX_PATH, MEDIA_FOLDER_PATH
from source.service.ChatService import ChatService
from source.service.MessageService import MessageService
from source.service.ExportService import ExportService
from source.service.BroadcastService import BroadcastService
from source.service.StatisticsService import StatisticsService
from source.model.ForwardConfig import ForwardConfig


class Telegram:
    def __init__(self, credentials):
        """Initialize the Telegram client with credentials."""
        self.credentials = credentials
        self.client = TelegramClient(
            SESSION_PREFIX_PATH + credentials.phone_number,
            credentials.api_id,
            credentials.api_hash
        )
        self._is_connected = False
        self.console = Terminal.console

        # Initialize services
        self.chat_service = ChatService(self.console)
        self.message_service = MessageService(self.client, self.console)
        self.message_service.chat_service = self.chat_service
        self.export_service = ExportService(self.client)
        self.broadcast_service = BroadcastService(self.client)
        self.statistics_service = StatisticsService()

    @classmethod
    async def create(cls, credentials):
        """Factory method to create and connect a Telegram instance."""
        instance = cls(credentials)
        await instance.connect()
        return instance

    async def connect(self):
        """Connect to Telegram if not already connected."""
        if not self._is_connected:
            try:
                if not self.client.is_connected():
                    await self.client.connect()
                if not await self.client.is_user_authorized():
                    await self.client.start(self.credentials.phone_number)
                self._is_connected = True
            except ConnectionError as e:
                self._is_connected = False
                raise ConnectionError(f"Failed to connect to Telegram: {e}")

    async def disconnect(self):
        """Safely disconnects the client."""
        if self._is_connected and self.client:
            try:
                await self.client.disconnect()
            finally:
                self._is_connected = False

    async def get_me(self):
        """Gets the current user's information."""
        return await self.client.get_me()

    async def list_chats(self):
        """Lists and saves all available chats."""
        chats = await self.client.get_dialogs()
        chat_list = Chat.write(chats)
        
        # Print chat information
        self.console.print("\n[bold blue]Available Chats:[/]")
        for chat_dict in chat_list:
            chat = Chat(**chat_dict)
            self.console.print(chat.get_display_name())


    async def delete(self, ignore_chats):
        """Deletes user's messages from all groups except ignored ones."""
        me = await self.get_me()
        ignored_ids = [chat.id for chat in ignore_chats]

        async for dialog in self.client.iter_dialogs():
            if not self._should_process_dialog(dialog, me.id, ignored_ids):
                continue

            await self.message_service.delete_messages_from_dialog(dialog, me.id)

    async def find_user(self, config):
        """Finds and downloads messages from a specific user.
        
        Args:
            config: tuple containing (wanted_user, message_limit)
        """
        wanted_user, message_limit = config
        if not wanted_user:
            return
        
        me = await self.get_me()
        
        # Create the user entity with the access hash
        wanted_user_entity = telethon.tl.types.User(
            id=wanted_user.id,
            access_hash=wanted_user.access_hash,
            username=wanted_user.username
        )

        async for dialog in self.client.iter_dialogs():
            chat = dialog.entity
            try:
                if chat.id == me.id and wanted_user.id != me.id:
                    continue

                if isinstance(chat, telethon.tl.types.User):
                    continue

                await self.message_service.process_user_messages(chat, wanted_user_entity, message_limit)

            except Exception as e:
                print(f"Error processing dialog: {e}")

    async def start_forward_live(self, forward_config):
        """Starts live message forwarding."""
        forward = Forward(self.client, forward_config)
        forward.add_events()
        await self.client.run_until_disconnected()

    async def past_forward(self, forward_config):
        """Forwards historical messages."""
        forward = Forward(self.client, forward_config)
        await forward.history_handler()

    async def export_chat_history(self, config):
        """Exports chat history to a file.
        
        Args:
            config: tuple containing (chat_object, format_type)
        """
        if not config:
            return
            
        chat, format_type = config
        await self.export_service.export_chat(chat.id, format_type)

    async def broadcast_message(self, config):
        """Broadcasts a message to multiple chats.
        
        Args:
            config: tuple containing (chat_objects, message_text)
        """
        if not config:
            return
            
        chats, message_text = config
        await self.broadcast_service.send_broadcast(chats, message_text)

    async def clone_channel(self, config):
        """Clones messages from one channel to another.
        
        Args:
            config: tuple containing (source_chat, dest_chat)
        """
        if not config:
            return
            
        source, destination = config
        
        # Create a temporary ForwardConfig
        fw_conf = ForwardConfig()
        fw_conf.sourceID = source.id
        fw_conf.sourceName = source.title
        fw_conf.destinationID = destination.id
        fw_conf.destinationName = destination.title
        
        # Reuse the Forward service logic
        forward = Forward(self.client, {source.id: fw_conf})
        
        self.console.print(f"[bold green]Starting clone from {source.title} to {destination.title}...[/bold green]")
        await forward.history_handler()
        self.console.print("[bold green]Clone completed![/bold green]")

    async def show_statistics(self):
        """Shows bot statistics."""
        await self.statistics_service.show_statistics(self.client)

    async def download_media(self, message):
        """Downloads media from a message."""
        os.makedirs(MEDIA_FOLDER_PATH, exist_ok=True)
        return await self.client.download_media(message, file=MEDIA_FOLDER_PATH)

    def _should_process_dialog(self, dialog, my_id, ignored_ids):
        """Determines if a dialog should be processed for deletion."""
        if not dialog.is_group:
            return False
        if dialog.id == my_id or dialog.id in ignored_ids:
            return False
        return True
