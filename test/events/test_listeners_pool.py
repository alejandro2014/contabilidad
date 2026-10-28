import unittest

import shiboken6
from PySide6.QtCore import QObject

from src.events.ListenerNode import ListenerNode
from src.events.ListenersPool import ListenersPool

class FakeNode(QObject, ListenerNode):
    def __init__(self, node_id, pool):
        super(FakeNode, self).__init__()
        ListenerNode.__init__(self, node_id, pool)

        self.received = []

    def without_info(self):
        self.received.append(None)
        return 'done'

    def with_info(self, info):
        self.received.append(info)
        return info * 2

class ListenersPoolTestCase(unittest.TestCase):
    def setUp(self):
        self.pool = ListenersPool()

    def test__send_event__calls_the_method_of_the_node(self):
        node = FakeNode('table', self.pool)

        self.assertEqual('done', self.pool.send_event('table', 'without_info'))
        self.assertEqual(4, self.pool.send_event('table', 'with_info', 2))
        self.assertEqual([ None, 2 ], node.received)

    def test__send_event__falsy_info_is_sent(self):
        # Only None means "no info": 0, '' or [] are real values
        node = FakeNode('table', self.pool)

        self.pool.send_event('table', 'with_info', 0)

        self.assertEqual([ 0 ], node.received)

    def test__send_event__unknown_node(self):
        self.assertIsNone(self.pool.send_event('missing', 'without_info'))

    def test__new_node_replaces_the_one_with_the_same_id(self):
        old_node = FakeNode('table', self.pool)
        new_node = FakeNode('table', self.pool)

        self.pool.send_event('table', 'without_info')

        self.assertEqual([], old_node.received)
        self.assertEqual([ None ], new_node.received)
        self.assertEqual(1, len(self.pool.nodes))

    def test__deleted_qt_node_is_removed(self):
        # The Qt object of a node is deleted when its screen is replaced
        node = FakeNode('table', self.pool)
        shiboken6.delete(node)

        self.assertIsNone(self.pool.send_event('table', 'without_info'))
        self.assertEqual([], self.pool.nodes)

    def test__delete_node(self):
        FakeNode('table', self.pool)
        FakeNode('chart', self.pool)

        self.pool.delete_node('table')

        self.assertEqual([ 'chart' ], [ n.node_id for n in self.pool.nodes ])
