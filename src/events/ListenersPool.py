import shiboken6

from src.logger import get_logger

logger = get_logger(__name__)

class ListenersPool:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def delete_node(self, node_id):
        #TODO Can it be replaced?
        for i in range(len(self.nodes)):
            current_node = self.nodes[i]

            if current_node.node_id == node_id:
                self.nodes.remove(current_node)
                return

        logger.warning(f'The node {node_id} cannot be deleted from the listeners pool, it does not exist')

    def send_event(self, node_id, event_id, info = None):
        node = None

        #TODO Replace with filter
        for n in self.nodes:
            if n.node_id == node_id:
                node = n
                break

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
