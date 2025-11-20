import json
import os.path
from typing import List, Optional
import re

from source.model.Chat import Chat
from source.utils.Constants import FORWARD_CONFIG_FILE_PATH
from source.dialog.BaseDialog import BaseDialog


class ForwardConfig:

    def __init__(self, *args, include_keywords: Optional[List[str]] = None, exclude_keywords: Optional[List[str]] = None,
                 deduplicate: bool = True, dedup_ttl_seconds: int = 3600,
                 rate_limit_enabled: bool = False, min_interval_seconds: float = 1.0, **kwargs):
        self.sourceID = None
        self.sourceName = None
        self.destinationID = None
        self.destinationName = None
        # word/regex need import (if eempty -> all include)
        self.include_keywords = include_keywords or []
        # word/regex that message blocked
        self.exclude_keywords = exclude_keywords or []
        # dup message (byfingerprint)
        self.deduplicate = deduplicate
        # TTL (seconds) consider dup message
        self.dedup_ttl_seconds = dedup_ttl_seconds

        # Rate limiting settings (disabled by default)
        # If enabled, the forward service will wait at least min_interval_seconds
        # between sends to the same destination.
        self.rate_limit_enabled = rate_limit_enabled
        self.min_interval_seconds = float(min_interval_seconds)

    @staticmethod
    def write(forward_config_list):
        forwardList = []
        for _ in forward_config_list:
            forwardList.append(_.__dict__)
        with open(FORWARD_CONFIG_FILE_PATH, "w") as file:
            json.dump(forwardList, file, indent=4)

    @staticmethod
    def read():
        with open(FORWARD_CONFIG_FILE_PATH, "r") as file:
            data = json.load(file)
            return [ForwardConfig(**forwardConfig) for forwardConfig in data]

    @staticmethod
    async def scan():
        chat = Chat()
        chats = chat.read()
        forwardConfigList = []
        dialog = BaseDialog()
        
        while True:
            forwardConfig = ForwardConfig()
            sourceChoice = await dialog.list_chats_terminal(chats, "source")
            if sourceChoice == -1:
                break
            source = chats[sourceChoice]
            forwardConfig.sourceID = source.id
            forwardConfig.sourceName = source.title

            destinationChoice = await dialog.list_chats_terminal(chats, "destination")
            destination = chats[destinationChoice]
            forwardConfig.destinationID = destination.id
            forwardConfig.destinationName = destination.title

            forwardConfigList.append(forwardConfig)
        ForwardConfig.write(forwardConfigList)
        return forwardConfigList

    @staticmethod
    async def get_all(is_saved=True):
        if is_saved and os.path.exists(FORWARD_CONFIG_FILE_PATH):
            return ForwardConfig.read()
        else:
            return await ForwardConfig.scan()

    def __repr__(self):
        return f'sourceName= "{self.sourceName}", destinationName= "{self.destinationName}"'

    # simple utility for test/regex
    def _matches_any(self, text: str, patterns: List[str]) -> bool:
        if not patterns:
            return False
        for p in patterns:
            try:
                if re.search(p, text, re.IGNORECASE):
                    return True
            except re.error:
                # if not regex working, search
                if p.lower() in text.lower():
                    return True
        return False
