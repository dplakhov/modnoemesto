# -*- coding: utf-8 -*-

class MessageLimitExceeded(Exception):
    pass

class SentMessageLimitExceeded(MessageLimitExceeded):
    pass

class IncomingMessageLimitExceeded(MessageLimitExceeded):
    pass