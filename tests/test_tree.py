from __future__ import absolute_import, unicode_literals

import copy
import random

import pytest

from binarytree import Node, build, tree, bst, heap
from binarytree import get_parent_node, merge_trees
from binarytree.exceptions import (
    NodeValueError,
    NodeIndexError,
    NodeTypeError,
    NodeModifyError,
    NodeNotFoundError,
    TreeHeightError,
    NodeReferenceError,
)
from tests.utils import (
    builtin_print,
    pprint_default,
    pprint_with_index
)

REPETITIONS = 20


@pytest.mark.order1
def test_node_set_attributes():
    root = Node(1)
    assert root.left is None
    assert root.right is None
    assert root.value == 1
    assert repr(root) == 'Node(1)'

    left_child = Node(2)
    root.left = left_child
    assert root.left is left_child
    assert root.right is None
    assert root.value == 1
    assert root.left.left is None
    assert root.left.right is None
    assert root.left.value == 2
    assert repr(left_child) == 'Node(2)'

    right_child = Node(3)
    root.right = right_child
    assert root.left is left_child
    assert root.right is right_child
    assert root.value == 1
    assert root.right.left is None
    assert root.right.right is None
    assert root.right.value == 3
    assert repr(right_child) == 'Node(3)'

    last_node = Node(4)
    left_child.right = last_node
    assert root.left.right is last_node
    assert root.left.right.value == 4
    assert repr(last_node) == 'Node(4)'

    with pytest.raises(NodeValueError) as err:
        # noinspection PyTypeChecker
        Node('this_is_not_an_integer')
    assert str(err.value) == 'node value must be a number'

    with pytest.raises(NodeTypeError) as err:
        # noinspection PyTypeChecker
        Node(1, 'this_is_not_a_node')
    assert str(err.value) == 'left child must be a Node instance'

    with pytest.raises(NodeTypeError) as err:
        # noinspection PyTypeChecker
        Node(1, Node(1), 'this_is_not_a_node')
    assert str(err.value) == 'right child must be a Node instance'

    with pytest.raises(NodeValueError) as err:
        root.value = 'this_is_not_an_integer'
    assert root.value == 1
    assert str(err.value) == 'node value must be a number'

    with pytest.raises(NodeTypeError) as err:
        root.left = 'this_is_not_a_node'
    assert root.left is left_child
    assert str(err.value) == 'left child must be a Node instance'

    with pytest.raises(NodeTypeError) as err:
        root.right = 'this_is_not_a_node'
    assert root.right is right_child
    assert str(err.value) == 'right child must be a Node instance'


@pytest.mark.order2
def test_tree_build():
    root = build([])
    assert root is None

    root = build([1])
    assert root.value == 1
    assert root.left is None
    assert root.right is None

    root = build([1, 2])
    assert root.value == 1
    assert root.left.value == 2
    assert root.right is None

    root = build([1, 2, 3])
    assert root.value == 1
    assert root.left.value == 2
    assert root.right.value == 3
    assert root.left.left is None
    assert root.left.right is None
    assert root.right.left is None
    assert root.right.right is None

    root = build([1, 2, 3, None, 4])
    assert root.value == 1
    assert root.left.value == 2
    assert root.right.value == 3
    assert root.left.left is None
    assert root.left.right.value == 4
    assert root.right.left is None
    assert root.right.right is None
    assert root.left.right.left is None
    assert root.left.right.right is None

    with pytest.raises(NodeNotFoundError) as err:
        build([None, 1, 2])
    assert str(err.value) == 'parent node missing at index 0'

    with pytest.raises(NodeNotFoundError) as err:
        build([1, None, 2, 3, 4])
    assert str(err.value) == 'parent node missing at index 1'


@pytest.mark.order3
def test_tree_get_node():
    root = Node(1)
    root.left = Node(2)
    root.right = Node(3)
    root.left.left = Node(4)
    root.left.right = Node(5)
    root.left.right.left = Node(6)

    assert root[0] is root
    assert root[1] is root.left
    assert root[2] is root.right
    assert root[3] is root.left.left
    assert root[4] is root.left.right
    assert root[9] is root.left.right.left

    for index in [5, 6, 7, 8, 10]:
        with pytest.raises(NodeNotFoundError) as err:
            assert root[index]
        assert str(err.value) == 'node missing at index {}'.format(index)

    with pytest.raises(NodeIndexError) as err:
        assert root[-1]
    assert str(err.value) == 'node index must be a non-negative int'


@pytest.mark.order4
def test_tree_set_node():
    root = Node(1)
    root.left = Node(2)
    root.right = Node(3)
    root.left.left = Node(4)
    root.left.right = Node(5)
    root.left.right.left = Node(6)

    new_node_1 = Node(7)
    new_node_2 = Node(8)
    new_node_3 = Node(9)

    with pytest.raises(NodeModifyError) as err:
        root[0] = new_node_1
    assert str(err.value) == 'cannot modify the root node'

    with pytest.raises(NodeIndexError) as err:
        root[-1] = new_node_1
    assert str(err.value) == 'node index must be a non-negative int'

    with pytest.raises(NodeNotFoundError) as err:
        root[100] = new_node_1
    assert str(err.value) == 'parent node missing at index 49'

    root[10] = new_node_1
    assert root.value == 1
    assert root.left.value == 2
    assert root.right.value == 3
    assert root.left.left.value == 4
    assert root.left.right.value == 5
    assert root.left.right.left.value == 6
    assert root.left.right.right is new_node_1

    root[4] = new_node_2
    assert root.value == 1
    assert root.left.value == 2
    assert root.right.value == 3
    assert root.left.left.value == 4
    assert root.left.right.value == 8
    assert root.left.right.left is None
    assert root.left.right.right is None

    root[1] = new_node_3
    root[2] = new_node_2
    assert root.left is new_node_3
    assert root.right is new_node_2


@pytest.mark.order5
def test_tree_del_node():
    root = Node(1)
    root.left = Node(2)
    root.right = Node(3)
    root.left.left = Node(4)
    root.left.right = Node(5)
    root.left.right.left = Node(6)

    with pytest.raises(NodeModifyError) as err:
        del root[0]
    assert str(err.value) == 'cannot delete the root node'

    with pytest.raises(NodeIndexError) as err:
        del root[-1]
    assert str(err.value) == 'node index must be a non-negative int'

    with pytest.raises(NodeNotFoundError) as err:
        del root[10]
    assert str(err.value) == 'no node to delete at index 10'

    with pytest.raises(NodeNotFoundError) as err:
        del root[100]
    assert str(err.value) == 'no node to delete at index 100'

    del root[3]
    assert root.left.left is None
    assert root.left.value == 2
    assert root.left.right.value == 5
    assert root.left.right.right is None
    assert root.left.right.left.value == 6
    assert root.left.right.left.left is None
    assert root.left.right.left.right is None
    assert root.right.value == 3
    assert root.right.left is None
    assert root.right.right is None
    assert root.size == 5

    del root[2]
    assert root.left.left is None
    assert root.left.value == 2
    assert root.left.right.value == 5
    assert root.left.right.right is None
    assert root.left.right.left.value == 6
    assert root.left.right.left.left is None
    assert root.left.right.left.right is None
    assert root.right is None
    assert root.size == 4

    del root[4]
    assert root.left.left is None
    assert root.left.right is None
    assert root.right is None
    assert root.size == 2

    del root[1]
    assert root.left is None
    assert root.right is None
    assert root.size == 1


@pytest.mark.order6
def test_tree_print_no_index():
    for printer in [builtin_print, pprint_default]:
        lines = printer([1])
        assert lines == ['1']
        lines = printer([1, 2])
        assert lines == ['  1',
                         ' /',
                         '2']
        lines = printer([1, None, 3])
        assert lines == ['1',
                         ' \\',
                         '  3']
        lines = printer([1, 2, 3])
        assert lines == ['  1',
                         ' / \\',
                         '2   3']
        lines = printer([1, 2, 3, None, 5])
        assert lines == ['  __1',
                         ' /   \\',
                         '2     3',
                         ' \\',
                         '  5']
        lines = printer([1, 2, 3, None, 5, 6])
        assert lines == ['  __1__',
                         ' /     \\',
                         '2       3',
                         ' \\     /',
                         '  5   6']
        lines = printer([1, 2, 3, None, 5, 6, 7])
        assert lines == ['  __1__',
                         ' /     \\',
                         '2       3',
                         ' \\     / \\',
                         '  5   6   7']
        lines = printer([1, 2, 3, 8, 5, 6, 7])
        assert lines == ['    __1__',
                         '   /     \\',
                         '  2       3',
                         ' / \\     / \\',
                         '8   5   6   7']


@pytest.mark.order7
def test_tree_print_with_index():
    lines = pprint_with_index([1])
    assert lines == ['0:1']
    lines = pprint_with_index([1, 2])
    assert lines == ['   _0:1',
                     '  /',
                     '1:2']
    lines = pprint_with_index([1, None, 3])
    assert lines == ['0:1_',
                     '    \\',
                     '    2:3']
    lines = pprint_with_index([1, 2, 3])
    assert lines == ['   _0:1_',
                     '  /     \\',
                     '1:2     2:3']
    lines = pprint_with_index([1, 2, 3, None, 5])
    assert lines == ['   _____0:1_',
                     '  /         \\',
                     '1:2_        2:3',
                     '    \\',
                     '    4:5']
    lines = pprint_with_index([1, 2, 3, None, 5, 6])
    assert lines == ['   _____0:1_____',
                     '  /             \\',
                     '1:2_           _2:3',
                     '    \\         /',
                     '    4:5     5:6']
    lines = pprint_with_index([1, 2, 3, None, 5, 6, 7])
    assert lines == ['   _____0:1_____',
                     '  /             \\',
                     '1:2_           _2:3_',
                     '    \\         /     \\',
                     '    4:5     5:6     6:7']
    lines = pprint_with_index([1, 2, 3, 8, 5, 6, 7])
    assert lines == ['       _____0:1_____',
                     '      /             \\',
                     '   _1:2_           _2:3_',
                     '  /     \\         /     \\',
                     '3:8     4:5     5:6     6:7']


@pytest.mark.order8
def test_tree_validate():

    class TestNode(Node):
        def __setattr__(self, attr, value):
            object.__setattr__(self, attr, value)

    root = Node(1)
    root.validate()  # Should pass

    root = Node(1)
    root.left = Node(2)
    root.validate()  # Should pass

    root = Node(1)
    root.left = Node(2)
    root.right = Node(3)
    root.validate()  # Should pass

    root = Node(1)
    root.left = Node(2)
    root.right = Node(3)
    root.left.left = Node(4)
    root.left.right = Node(5)
    root.left.right.left = Node(6)
    root.validate()  # Should pass

    root = TestNode(1)
    root.left = 'not_a_node'
    with pytest.raises(NodeTypeError) as err:
        root.validate()
    assert str(err.value) == 'invalid node instance at index 1'

    root = TestNode(1)
    root.right = TestNode(2)
    root.right.value = 'not_an_integer'
    with pytest.raises(NodeValueError) as err:
        root.validate()
    assert str(err.value) == 'invalid node value at index 2'

    root = TestNode(1)
    root.left = TestNode(2)
    root.left.right = root
    with pytest.raises(NodeReferenceError) as err:
        root.validate()
    assert str(err.value) == 'cyclic node reference at index 4'


@pytest.mark.order9
def test_tree_properties():
    root = Node(1)
    assert root.properties == {
        'height': 0,
        'is_balanced': True,
        'is_bst': True,
        'is_complete': True,
        'is_max_heap': True,
        'is_min_heap': True,
        'is_perfect': True,
        'is_strict': True,
        'is_symmetric': True,
        'leaf_count': 1,
        'max_leaf_depth': 0,
        'max_node_value': 1,
        'min_leaf_depth': 0,
        'min_node_value': 1,
        'size': 1
    }
    assert root.height == 0
    assert root.is_balanced is True
    assert root.is_bst is True
    assert root.is_complete is True
    assert root.is_max_heap is True
    assert root.is_min_heap is True
    assert root.is_perfect is True
    assert root.is_strict is True
    assert root.is_symmetric is True
    assert root.leaf_count == 1
    assert root.max_leaf_depth == 0
    assert root.max_node_value == 1
    assert root.min_leaf_depth == 0
    assert root.min_node_value == 1
    assert root.size == len(root) == 1

    root.left = Node(2)
    assert root.properties == {
        'height': 1,
        'is_balanced': True,
        'is_bst': False,
        'is_complete': True,
        'is_max_heap': False,
        'is_min_heap': True,
        'is_perfect': False,
        'is_strict': False,
        'is_symmetric': False,
        'leaf_count': 1,
        'max_leaf_depth': 1,
        'max_node_value': 2,
        'min_leaf_depth': 1,
        'min_node_value': 1,
        'size': 2
    }
    assert root.height == 1
    assert root.is_balanced is True
    assert root.is_bst is False
    assert root.is_complete is True
    assert root.is_max_heap is False
    assert root.is_min_heap is True
    assert root.is_perfect is False
    assert root.is_strict is False
    assert root.is_symmetric is False
    assert root.leaf_count == 1
    assert root.max_leaf_depth == 1
    assert root.max_node_value == 2
    assert root.min_leaf_depth == 1
    assert root.min_node_value == 1
    assert root.size == len(root) == 2

    root.right = Node(3)
    assert root.properties == {
        'height': 1,
        'is_balanced': True,
        'is_bst': False,
        'is_complete': True,
        'is_max_heap': False,
        'is_min_heap': True,
        'is_perfect': True,
        'is_strict': True,
        'is_symmetric': False,
        'leaf_count': 2,
        'max_leaf_depth': 1,
        'max_node_value': 3,
        'min_leaf_depth': 1,
        'min_node_value': 1,
        'size': 3
    }
    assert root.height == 1
    assert root.is_balanced is True
    assert root.is_bst is False
    assert root.is_complete is True
    assert root.is_max_heap is False
    assert root.is_min_heap is True
    assert root.is_perfect is True
    assert root.is_strict is True
    assert root.is_symmetric is False
    assert root.leaf_count == 2
    assert root.max_leaf_depth == 1
    assert root.max_node_value == 3
    assert root.min_leaf_depth == 1
    assert root.min_node_value == 1
    assert root.size == len(root) == 3

    root.left.left = Node(4)
    assert root.properties == {
        'height': 2,
        'is_balanced': True,
        'is_bst': False,
        'is_complete': True,
        'is_max_heap': False,
        'is_min_heap': True,
        'is_perfect': False,
        'is_strict': False,
        'is_symmetric': False,
        'leaf_count': 2,
        'max_leaf_depth': 2,
        'max_node_value': 4,
        'min_leaf_depth': 1,
        'min_node_value': 1,
        'size': 4
    }
    assert root.height == 2
    assert root.is_balanced is True
    assert root.is_bst is False
    assert root.is_complete is True
    assert root.is_max_heap is False
    assert root.is_min_heap is True
    assert root.is_perfect is False
    assert root.is_strict is False
    assert root.is_symmetric is False
    assert root.leaf_count == 2
    assert root.max_leaf_depth == 2
    assert root.max_node_value == 4
    assert root.min_leaf_depth == 1
    assert root.min_node_value == 1
    assert root.size == len(root) == 4

    root.right.left = Node(5)
    assert root.properties == {
        'height': 2,
        'is_balanced': True,
        'is_bst': False,
        'is_complete': False,
        'is_max_heap': False,
        'is_min_heap': False,
        'is_perfect': False,
        'is_strict': False,
        'is_symmetric': False,
        'leaf_count': 2,
        'max_leaf_depth': 2,
        'max_node_value': 5,
        'min_leaf_depth': 2,
        'min_node_value': 1,
        'size': 5
    }
    assert root.height == 2
    assert root.is_balanced is True
    assert root.is_bst is False
    assert root.is_complete is False
    assert root.is_max_heap is False
    assert root.is_min_heap is False
    assert root.is_perfect is False
    assert root.is_strict is False
    assert root.is_symmetric is False
    assert root.leaf_count == 2
    assert root.max_leaf_depth == 2
    assert root.max_node_value == 5
    assert root.min_leaf_depth == 2
    assert root.min_node_value == 1
    assert root.size == len(root) == 5

    root.right.left.left = Node(6)
    assert root.properties == {
        'height': 3,
        'is_balanced': False,
        'is_bst': False,
        'is_complete': False,
        'is_max_heap': False,
        'is_min_heap': False,
        'is_perfect': False,
        'is_strict': False,
        'is_symmetric': False,
        'leaf_count': 2,
        'max_leaf_depth': 3,
        'max_node_value': 6,
        'min_leaf_depth': 2,
        'min_node_value': 1,
        'size': 6
    }
    assert root.height == 3
    assert root.is_balanced is False
    assert root.is_bst is False
    assert root.is_complete is False
    assert root.is_max_heap is False
    assert root.is_min_heap is False
    assert root.is_perfect is False
    assert root.is_strict is False
    assert root.is_symmetric is False
    assert root.leaf_count == 2
    assert root.max_leaf_depth == 3
    assert root.max_node_value == 6
    assert root.min_leaf_depth == 2
    assert root.min_node_value == 1
    assert root.size == len(root) == 6

    root.left.left.left = Node(7)
    assert root.properties == {
        'height': 3,
        'is_balanced': False,
        'is_bst': False,
        'is_complete': False,
        'is_max_heap': False,
        'is_min_heap': False,
        'is_perfect': False,
        'is_strict': False,
        'is_symmetric': False,
        'leaf_count': 2,
        'max_leaf_depth': 3,
        'max_node_value': 7,
        'min_leaf_depth': 3,
        'min_node_value': 1,
        'size': 7
    }
    assert root.height == 3
    assert root.is_balanced is False
    assert root.is_bst is False
    assert root.is_complete is False
    assert root.is_max_heap is False
    assert root.is_min_heap is False
    assert root.is_perfect is False
    assert root.is_strict is False
    assert root.is_symmetric is False
    assert root.leaf_count == 2
    assert root.max_leaf_depth == 3
    assert root.max_node_value == 7
    assert root.min_leaf_depth == 3
    assert root.min_node_value == 1
    assert root.size == len(root) == 7


@pytest.mark.order10
def test_tree_traversal():
    n1 = Node(1)
    assert n1.levels == [[n1]]
    assert n1.leaves == [n1]
    assert n1.inorder == [n1]
    assert n1.preorder == [n1]
    assert n1.postorder == [n1]
    assert n1.levelorder == [n1]

    n2 = Node(2)
    n1.left = n2
    assert n1.levels == [[n1], [n2]]
    assert n1.leaves == [n2]
    assert n1.inorder == [n2, n1]
    assert n1.preorder == [n1, n2]
    assert n1.postorder == [n2, n1]
    assert n1.levelorder == [n1, n2]

    n3 = Node(3)
    n1.right = n3
    assert n1.levels == [[n1], [n2, n3]]
    assert n1.leaves == [n2, n3]
    assert n1.inorder == [n2, n1, n3]
    assert n1.preorder == [n1, n2, n3]
    assert n1.postorder == [n2, n3, n1]
    assert n1.levelorder == [n1, n2, n3]

    n4 = Node(4)
    n5 = Node(5)
    n2.left = n4
    n2.right = n5

    assert n1.levels == [[n1], [n2, n3], [n4, n5]]
    assert n1.leaves == [n3, n4, n5]
    assert n1.inorder == [n4, n2, n5, n1, n3]
    assert n1.preorder == [n1, n2, n4, n5, n3]
    assert n1.postorder == [n4, n5, n2, n3, n1]
    assert n1.levelorder == [n1, n2, n3, n4, n5]


def test_tree_list_representation():
    root = Node(1)
    assert root.values == [1]

    root.right = Node(3)
    assert root.values == [1, None, 3]

    root.left = Node(2)
    assert root.values == [1, 2, 3]

    root.right.left = Node(4)
    assert root.values == [1, 2, 3, None, None, 4]

    root.right.right = Node(5)
    assert root.values == [1, 2, 3, None, None, 4, 5]

    root.left.left = Node(6)
    assert root.values == [1, 2, 3, 6, None, 4, 5]

    root.left.right = Node(7)
    assert root.values == [1, 2, 3, 6, 7, 4, 5]


@pytest.mark.order11
def test_tree_generation():
    for invalid_height in ['foo', -1, None]:
        with pytest.raises(TreeHeightError) as err:
            tree(height=invalid_height)
        assert str(err.value) == 'height must be an int between 0 - 9'

    root = tree(height=0)
    root.validate()
    assert root.height == 0
    assert root.left is None
    assert root.right is None
    assert isinstance(root.value, int)

    for _ in range(REPETITIONS):
        random_height = random.randint(1, 9)
        root = tree(random_height)
        root.validate()
        assert root.height == random_height

    for _ in range(REPETITIONS):
        random_height = random.randint(1, 9)
        root = tree(random_height, is_perfect=True)
        root.validate()
        assert root.height == random_height
        assert root.is_perfect is True
        assert root.is_balanced is True
        assert root.is_strict is True


@pytest.mark.order12
def test_bst_generation():
    for invalid_height in ['foo', -1, None]:
        with pytest.raises(TreeHeightError) as err:
            bst(height=invalid_height)
        assert str(err.value) == 'height must be an int between 0 - 9'

    root = bst(height=0)
    root.validate()
    assert root.height == 0
    assert root.left is None
    assert root.right is None
    assert isinstance(root.value, int)

    for _ in range(REPETITIONS):
        random_height = random.randint(1, 9)
        root = bst(random_height)
        root.validate()
        assert root.is_bst is True
        assert root.height == random_height

    for _ in range(REPETITIONS):
        random_height = random.randint(1, 9)
        root = bst(random_height, is_perfect=True)
        root.validate()
        assert root.height == random_height

        if not root.is_bst:
            print(root)
            raise Exception('boo')

        assert root.is_bst is True
        assert root.is_perfect is True
        assert root.is_balanced is True
        assert root.is_strict is True


@pytest.mark.order13
def test_heap_generation():
    for invalid_height in ['foo', -1, None]:
        with pytest.raises(TreeHeightError) as err:
            heap(height=invalid_height)
        assert str(err.value) == 'height must be an int between 0 - 9'

    root = heap(height=0)
    root.validate()
    assert root.height == 0
    assert root.left is None
    assert root.right is None
    assert isinstance(root.value, int)

    for _ in range(REPETITIONS):
        random_height = random.randint(1, 9)
        root = heap(random_height, is_max=True)
        root.validate()
        assert root.is_max_heap is True
        assert root.is_min_heap is False
        assert root.height == random_height

    for _ in range(REPETITIONS):
        random_height = random.randint(1, 9)
        root = heap(random_height, is_max=False)
        root.validate()
        assert root.is_max_heap is False
        assert root.is_min_heap is True
        assert root.height == random_height

    for _ in range(REPETITIONS):
        random_height = random.randint(1, 9)
        root = heap(random_height, is_perfect=True)
        root.validate()
        assert root.is_max_heap is True
        assert root.is_min_heap is False
        assert root.is_perfect is True
        assert root.is_balanced is True
        assert root.is_strict is True
        assert root.height == random_height


@pytest.mark.order13
def test_heap_float_values():
    root = Node(1.0)
    root.left = Node(0.5)
    root.right = Node(1.5)

    assert root.height == 1
    assert root.is_balanced is True
    assert root.is_bst is True
    assert root.is_complete is True
    assert root.is_max_heap is False
    assert root.is_min_heap is False
    assert root.is_perfect is True
    assert root.is_strict is True
    assert root.leaf_count == 2
    assert root.max_leaf_depth == 1
    assert root.max_node_value == 1.5
    assert root.min_leaf_depth == 1
    assert root.min_node_value == 0.5
    assert root.size == 3

    for printer in [builtin_print, pprint_default]:
        lines = printer([1.0])
        assert lines == ['1.0']
        lines = printer([1.0, 2.0])
        assert lines == ['   _1.0',
                         '  /',
                         '2.0']
        lines = printer([1.0, None, 3.0])
        assert lines == ['1.0_',
                         '    \\',
                         '    3.0']
        lines = printer([1.0, 2.0, 3.0])
        assert lines == ['   _1.0_',
                         '  /     \\',
                         '2.0     3.0']
        lines = printer([1.0, 2.0, 3.0, None, 5.0])
        assert lines == ['   _____1.0_',
                         '  /         \\',
                         '2.0_        3.0',
                         '    \\',
                         '    5.0']

    for builder in [tree, bst, heap]:
        for _ in range(REPETITIONS):
            root = builder()
            root_copy = copy.deepcopy(root)

            for node in root:
                node.value += 0.1

            assert root.height == root_copy.height
            assert root.is_balanced == root_copy.is_balanced
            assert root.is_bst == root_copy.is_bst
            assert root.is_complete == root_copy.is_complete
            assert root.is_max_heap == root_copy.is_max_heap
            assert root.is_min_heap == root_copy.is_min_heap
            assert root.is_perfect == root_copy.is_perfect
            assert root.is_strict == root_copy.is_strict
            assert root.is_symmetric == root_copy.is_symmetric
            assert root.leaf_count == root_copy.leaf_count
            assert root.max_leaf_depth == root_copy.max_leaf_depth
            assert root.max_node_value == root_copy.max_node_value + 0.1
            assert root.min_leaf_depth == root_copy.min_leaf_depth
            assert root.min_node_value == root_copy.min_node_value + 0.1
            assert root.size == root_copy.size


@pytest.mark.order14
def test_get_parent_node():
    root = Node(0)
    root.left = Node(1)
    root.right = Node(2)
    root.left.left = Node(3)
    root.right.right = Node(4)
    assert get_parent_node(root, root.left.left) == root.left
    assert get_parent_node(root, root.left) == root
    assert get_parent_node(root, root) is None
    assert get_parent_node(root, root.right.right) == root.right
    assert get_parent_node(root, root.right) == root
    assert get_parent_node(root, Node(5)) is None
    assert get_parent_node(None, root.left) is None
    assert get_parent_node(root, None) is None


@pytest.mark.order15
def test_merge_trees():
    root = Node(1)
    root.left = Node(3)
    root.right = Node(4)
    root.left.right = Node(2)
    root.right.left = Node(3)
    tree = Node(3)
    tree.left = Node(1)
    tree.right = Node(2)
    tree.left.left = Node(5)
    tree.left.right = Node(3)
    mtree = Node(4)
    mtree.left = Node(4)
    mtree.right = Node(6)
    mtree.left.left = Node(5)
    mtree.left.right = Node(5)
    mtree.right.left = Node(3)
    assert merge_trees(root, None) == root
    assert merge_trees(None, tree) == tree
    assert merge_trees(root, tree).value == mtree.value
    assert merge_trees(root, tree).left.value == mtree.left.value
    assert merge_trees(root, tree).right.value == mtree.right.value
    assert merge_trees(root, tree).left.left.value == mtree.left.left.value
    assert merge_trees(root, tree).left.right.value == mtree.left.right.value
    assert merge_trees(root, tree).right.left.value == mtree.right.left.value
