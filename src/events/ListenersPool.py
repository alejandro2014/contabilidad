class ListenersPool:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        print('[INFO] Added node with node_id = ' + node.node_id + ' to the listeners pool')
        self.nodes.append(node)

    def delete_node(self, node_id):
        #TODO Can it be replaced?
        for i in range(len(self.nodes)):
            current_node = self.nodes[i]

            if current_node.node_id == node_id:
                self.nodes.remove(current_node)
                return

        print('[INFO] The node with node_id = ' + node_id + ' cannot be deleted from the listeners pool, it does not exist')

    def send_event(self, node_id, event_id, info = None):
        node = None

        print("[INFO] Received event " + node_id + '.' + event_id)

        #TODO Replace with filter
        for n in self.nodes:
            if n.node_id == node_id:
                node = n
                break

        if node == None:
            print("[ERROR] The node " + node_id + " doesn't exist")
            return None

        if info:
            return getattr(node, event_id)(info)

        getattr(node, event_id)()
