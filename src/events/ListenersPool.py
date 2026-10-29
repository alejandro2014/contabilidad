import shiboken6

from src.logger import get_logger

logger = get_logger(__name__)

class ListenersPool:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def find_node(self, node_id):
        return next((node for node in self.nodes if node.node_id == node_id), None)

    def delete_node(self, node_id):
        node = self.find_node(node_id)

        if node == None:
            logger.warning(f'The node {node_id} cannot be deleted from the listeners pool, it does not exist')
            return

        self.nodes.remove(node)

    def send_event(self, node_id, event_id, info = None):
        node = self.find_node(node_id)

        # The Qt object of the node is deleted when its screen is replaced
        if node != None and not shiboken6.isValid(node):
            self.nodes.remove(node)
            node = None

        if node == None:
            logger.warning(f"The event {node_id}.{event_id} is lost, the node {node_id} doesn't exist")
            return None

        if info is not None:
            return getattr(node, event_id)(info)

        return getattr(node, event_id)()
