# -*- coding: utf-8 -*-

import unittest

from apps.logging.documents import LogEntry
import logging

class MongoLoggerTest(unittest.TestCase):

    def setUp(self):
        self.cleanUp()
    
    def tearDown(self):
        pass
    
    def cleanUp(self):
        LogEntry.objects.delete()
        
    def test_mongo_entry(self):
        logger = logging.getLogger('test_logger')
        self.assertEqual(LogEntry.objects.count(), 0)
        
        msg = 'test log message'
        logger.info(msg)
        self.assertNotEqual(LogEntry.objects.count(), 1)
        
