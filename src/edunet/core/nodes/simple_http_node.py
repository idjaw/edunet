import logging

from core.nodes.node import Node
from core.networking.listeners.listener import Listener

logger = logging.getLogger(__name__)


class SimpleHTTPNode(Node):
    def __init__(self, listener: Listener):
        super().__init__(listener)
        self.machine_started = False

    def start(self):
        logger.info("Starting Machine and services")
        if not self.machine_started:
            self.machine_started = True
            logger.info("Machine has been started")
            self.listener.start()
            logger.info("Service has been started")
        else:
            logger.info("Machine already started. Nothing to do")

    def stop(self):
        logger.info("Stopping services and machine")
        if self.machine_started:
            self.listener.stop()
            logger.info("Service stopped")
            self.machine_started = False
            logger.info("Machine stopped")
        else:
            logger.info("Machine already stopped. Nothing to do")
