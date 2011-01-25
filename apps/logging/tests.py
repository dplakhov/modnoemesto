# -*- coding: utf-8 -*-

import unittest

from apps.logging.models import LogEntry
import logging

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


class MongoLoggerTest(unittest.TestCase):

    def setUp(self):
        self.cleanUp()
    
    def tearDown(self):
        self.cleanUp()
    
    def cleanUp(self):
        LogEntry.objects()._collection.drop()

    def test_mongo_entry(self):
        self.assertEqual(LogEntry.objects.count(), 0)

        # debug
        logger = logging.getLogger('test_mongo_logger')
        logger.debug('debug message')
        self.assertEqual(LogEntry.objects.filter(levelnum=logging.DEBUG).count(), 1)
        
        message = LogEntry.objects.filter(levelnum=logging.DEBUG)[0]
        self.assertEqual(message.levelnum, 10)
        self.assertEqual(message.logger_name, "test_mongo_logger")
        self.assertEqual(message.levelname, "DEBUG")

        self.assertEqual(LogEntry.objects.count(), 1)
        
