import os
import time
import asyncio
import hashlib
import logging
from typing import Optional, List

from telethon import TelegramClient
from telethon.tl.custom import Message

from source.utils.Constants import MEDIA_FOLDER_PATH
from source.model.ForwardConfig import ForwardConfig

# try HistoryService (if exists) for persistence; fallback to memory
try:
    from source.service.HistoryService import HistoryService
except Exception:
    HistoryService = None


class MessageForwardService:
    """Service for handling message forwarding and sending operations."""

    def __init__(self, client: TelegramClient):
        """Initialize the message forward service.
        
        Args:
            client: Telegram client instance
        """
        self.client = client

        self._dedup_cache = {}  # fingerprint -> timestamp

        self._history_service = HistoryService() if HistoryService else None

        # rate limiting: last send timestamp por destination_id
        # key = destination_id (int) -> last_sent_timestamp (float)
        self._last_sent = {}

    async def forward_message(self, destination_id: int, message: Message, reply_to: Optional[int] = None) -> Optional[Message]:
        try:
            if message.forward is not None:
                return await self.client.forward_messages(destination_id, message)

            media_path = None
            try:
                if message.media:
                    media_path = await self._download_media(message)
                
                text = message.text or ''
                
                if media_path:
                    return await self.client.send_file(
                        destination_id,
                        media_path,
                        caption=text,
                        reply_to=reply_to
                    )
                else:
                    return await self.client.send_message(
                        destination_id,
                        text,
                        reply_to=reply_to
                    )
            finally:
                if media_path:
                    self._delete_media(media_path)

        except Exception as e:
            print(f"Error sending message: {e}")
            return None

    async def forward_album(
        self,
        destination_id: int,
        messages: List[Message],
        caption: str,
        reply_to: Optional[int] = None
    ) -> Optional[List[Message]]:
        media_paths = []
        try:
            media_paths = await self._download_album_media(messages)
            return await self.client.send_file(
                destination_id,
                media_paths,
                caption=caption,
                reply_to=reply_to
            )
        except Exception as e:
            print(f"Error forwarding album: {e}")
            return None
        finally:
            self._cleanup_media(media_paths)

    async def _download_media(self, message: Message) -> Optional[str]:
        try:
            os.makedirs(MEDIA_FOLDER_PATH, exist_ok=True)
            return await self.client.download_media(message, file=MEDIA_FOLDER_PATH)
        except Exception as e:
            print(f"Error downloading media: {e}")
            return None

    async def _download_album_media(self, messages: List[Message]) -> List[str]:
        media_paths = []
        for message in messages:
            if message.media:
                path = await self._download_media(message)
                if path:
                    media_paths.append(path)
        return media_paths

    @staticmethod
    def _delete_media(media_path: str) -> None:
        try:
            os.remove(media_path)
        except Exception as e:
            print(f"Error deleting media file {media_path}: {e}")

    @staticmethod
    def _cleanup_media(media_paths: List[str]) -> None:
        for path in media_paths:
            MessageForwardService._delete_media(path)

    def filter_message(self, message_text: str, forward_config: ForwardConfig) -> bool:
        """
        Returns True if the message should be forwarded, False otherwise.
        Logic:
         - If exclude_keywords exist and any match -> block (False)
         - If include_keywords exist and any match -> allow (True)
         - If include_keywords is empty -> allow (unless excluded)
        Supports regex and case-insensitive search. Regex failures fall back to literal search.
        """
        text = message_text or ""
        if forward_config._matches_any(text, forward_config.exclude_keywords):
            return False
        if forward_config.include_keywords:
            return forward_config._matches_any(text, forward_config.include_keywords)
        return True

    def _fingerprint(self, message) -> str:
        """
        Gera fingerprint simples baseada em texto, ids de mídia e remetente.
        Ajuste conforme os atributos reais do objeto 'message' no projeto.
        """
        parts = []
        text = getattr(message, "text", "") or ""
        parts.append(text)
        try:
            if hasattr(message, "photo") and message.photo:
                parts.append("photo:" + ",".join([getattr(p, "file_unique_id", str(getattr(p, "file_id", ""))) for p in message.photo]))
            if hasattr(message, "document") and getattr(message, "document", None):
                doc = message.document
                parts.append("doc:" + getattr(doc, "file_unique_id", str(getattr(doc, "file_id", ""))))
            if hasattr(message, "video") and getattr(message, "video", None):
                vid = message.video
                parts.append("video:" + getattr(vid, "file_unique_id", str(getattr(vid, "file_id", ""))))
            # sender/chat ids (retratos seguros de possíveis atributos do telethon)
            sender_id = getattr(message, "sender_id", None) \
                        or getattr(getattr(message, "from_user", None), "id", None) \
                        or getattr(getattr(message, "sender", None), "id", None) \
                        or ""
            chat_id = getattr(message, "chat_id", None) \
                      or getattr(getattr(message, "chat", None), "id", None) \
                      or ""
            parts.append("from:" + str(sender_id))
            parts.append("chat:" + str(chat_id))
        except Exception:
            parts.append(str(getattr(message, "message_id", "")))
        raw = "|".join(parts)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _is_duplicate(self, fingerprint: str, ttl: int) -> bool:
        now = time.time()
        if self._history_service:
            try:
                if hasattr(self._history_service, "exists"):
                    return self._history_service.exists(fingerprint, ttl)
                if hasattr(self._history_service, "is_recent"):
                    return self._history_service.is_recent(fingerprint, ttl)
            except Exception:
                logging.exception("HistoryService check failed; fallback to memory dedup.")
        # fallback in-memory
        ts = self._dedup_cache.get(fingerprint)
        if ts and (now - ts) <= ttl:
            return True
        return False

    def _record_fingerprint(self, fingerprint: str):
        now = time.time()
        if self._history_service:
            try:
                if hasattr(self._history_service, "record"):
                    self._history_service.record(fingerprint)
                    return
            except Exception:
                logging.exception("HistoryService record failed; recording to memory.")
        # fallback in-memory
        self._dedup_cache[fingerprint] = now

    async def _enforce_rate_limit(self, destination_id: int, forward_config: ForwardConfig) -> None:
        """
        If rate limiting is enabled in forward_config, ensure at least
        forward_config.min_interval_seconds passed since last send to destination_id.
        This function will await for the remaining time if necessary.
        """
        if not getattr(forward_config, "rate_limit_enabled", False):
            return
        min_interval = float(getattr(forward_config, "min_interval_seconds", 1.0))
        now = time.time()
        last = self._last_sent.get(destination_id)
        if last is None:
            self._last_sent[destination_id] = now
            return
        elapsed = now - last
        if elapsed >= min_interval:
            self._last_sent[destination_id] = now
            return
        wait = min_interval - elapsed
        logging.info(f"Rate limit: sleeping {wait:.2f}s before sending to {destination_id}")
        # await sleep so we don't exceed rate limits
        await asyncio.sleep(wait)
        # record the send time after waiting
        self._last_sent[destination_id] = time.time()

    async def forward_message_if_allowed(self, destination_id: int, message, forward_config: ForwardConfig, reply_to: Optional[int] = None, *args, **kwargs):
        text = getattr(message, "text", "") or ""

        if hasattr(self, "filter_message") and not self.filter_message(text, forward_config):
            try:
                logging.info("Message blocked by keyword filter")
            except Exception:
                pass
            return None

        # deduplicação
        if getattr(forward_config, "deduplicate", False):
            fp = self._fingerprint(message)
            if self._is_duplicate(fp, getattr(forward_config, "dedup_ttl_seconds", 3600)):
                logging.info("Duplicate message detected; skipping forward")
                return None
            self._record_fingerprint(fp)

        # enforce rate limit per-destination (may await)
        try:
            await self._enforce_rate_limit(destination_id, forward_config)
        except Exception:
            logging.exception("Rate limit enforcement failed; proceeding to send")

        # ...existing forwarding logic...
        try:
            return await self.forward_message(destination_id, message, reply_to=reply_to)
        except Exception as e:
            logging.exception("Erro ao encaminhar mensagem no forward_message_if_allowed")
            return None
