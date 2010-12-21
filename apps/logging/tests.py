# -*- coding: utf-8 -*-

import unittest

from apps.logging.documents import LogEntry
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
        LogEntry.objects.delete()
        
    def test_mongo_entry(self):
        self.cleanUp()
        
        self.assertEqual(LogEntry.objects.count(), 0)


        # debug
        logger = logging.getLogger('test_logger_debug')
        logger.debug('debug message')
        self.assertEqual(LogEntry.objects.filter(levelnum=logging.DEBUG).count(), 1)
        
        message = LogEntry.objects.filter(levelnum=logging.DEBUG)[0]
        self.assertEqual(message.levelnum, 10)
        self.assertEqual(message.logger_name, "test_logger_debug")
        self.assertEqual(message.levelname, "DEBUG")

        self.assertEqual(LogEntry.objects.count(), 1)
        
        # info
        logger = logging.getLogger('test_logger_info')
        logger.info('info message')
        self.assertEqual(LogEntry.objects.filter(levelnum=logging.INFO).count(), 1)
        
        message = LogEntry.objects.filter(levelnum=logging.INFO)[0]
        self.assertEqual(message.levelnum, 20)
        self.assertEqual(message.logger_name, "test_logger_info")
        self.assertEqual(message.levelname, "INFO")
        
        self.assertEqual(LogEntry.objects.count(), 2)        
        
        # warning
        logger = logging.getLogger('test_logger_warning')
        logger.warning('warning message')
        self.assertEqual(LogEntry.objects.filter(levelnum=logging.WARNING).count(), 1)
        
        message = LogEntry.objects.filter(levelnum=logging.WARNING)[0]
        self.assertEqual(message.levelnum, 30)
        self.assertEqual(message.logger_name, "test_logger_warning")
        self.assertEqual(message.levelname, "WARNING")
        
        # error
        self.assertEqual(LogEntry.objects.count(), 3)        
    
        logger = logging.getLogger('test_logger_error')
        logger.error('error message')
        self.assertEqual(LogEntry.objects.filter(levelnum=logging.ERROR).count(), 1)
        
        message = LogEntry.objects.filter(levelnum=logging.ERROR)[0]
        self.assertEqual(message.levelnum, 40)
        self.assertEqual(message.logger_name, "test_logger_error")
        self.assertEqual(message.levelname, "ERROR")
        
        self.assertEqual(LogEntry.objects.count(), 4)        
        
        # critical
        logger = logging.getLogger('test_logger_critical')
        logger.critical('critical message')
        self.assertEqual(LogEntry.objects.filter(levelnum=logging.CRITICAL).count(), 1)
        
        message = LogEntry.objects.filter(levelnum=logging.CRITICAL)[0]
        self.assertEqual(message.levelnum, 50)
        self.assertEqual(message.logger_name, "test_logger_critical")
        self.assertEqual(message.levelname, "CRITICAL")
        
        
        self.assertEqual(LogEntry.objects.count(), 5)        
