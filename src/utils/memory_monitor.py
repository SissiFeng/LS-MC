import psutil
import os
from typing import Dict
import logging

class MemoryMonitor:
    """Memory usage monitoring tool"""

    def __init__(self):
        self.logger = logging.getLogger('MemoryMonitor')
        self.process = psutil.Process(os.getpid())

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        memory_info = self.process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # RSS in MB
            'vms': memory_info.vms / 1024 / 1024,  # VMS in MB
            'percent': self.process.memory_percent()
        }

    def log_memory_usage(self, tag: str = ''):
        """Log current memory usage"""
        usage = self.get_memory_usage()
        self.logger.info(
            f"Memory usage {tag}: "
            f"RSS={usage['rss']:.1f}MB, "
            f"VMS={usage['vms']:.1f}MB, "
            f"Percent={usage['percent']:.1f}%"
        ) 