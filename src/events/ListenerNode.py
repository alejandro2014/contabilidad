class ListenerNode:
    def __init__(self, node_id, pool):
        self.node_id = node_id
        self.pool = pool
        self.pool.delete_node(node_id)
        self.pool.add_node(self)

    def send_event(self, node_id, event_id, data = None):
        return self.pool.send_event(node_id, event_id, data)

    def __str__(self):
        return '<ListenerNode ' + self.node_id + '>'
