
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """

    if board.legal_actions(state) and node.untried_actions:
        return node

    chosen_action = choice(list(node.child_nodes.keys()))
    print(chosen_action)
    chosen_node = node.child_nodes[chosen_action]

    leaf_node = traverse_nodes(chosen_node, board, state, identity)
    return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The parent node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    chosen_action = choice(node.untried_actions)
    new_board_state = board.next_state(state, chosen_action)
    new_legal_actions = board.legal_actions(new_board_state)
    new_node = MCTSNode(parent=node, parent_action = chosen_action, action_list = new_legal_actions)

    node.child_nodes[chosen_action] = new_node
    node.untried_actions.remove(chosen_action)

    return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """

    if board.is_ended(state):
        win_state = board.points_values(state)
        return win_state

    chosen_action = choice(board.legal_actions(state))
    new_board_state = board.next_state(state, chosen_action)
    win_state = rollout(board, new_board_state)

    return win_state


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """

    current_node = node

    while current_node.parent is not None:
        current_node.visits += 1
        if won == 1:
            current_node.wins += 1

        print('New Wins:')
        print(current_node.wins)
        print('\nNew Visits:')
        print(current_node.visits)

        current_node = current_node.parent

    print('\nRoot Node Reached')
    current_node.visits += 1

    if won == 1:
        current_node.wins += 1

    print('Root Wins:')
    print(current_node.wins)
    print('\nRoot Visits:')
    print(current_node.visits)

    pass


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        node_to_expand = traverse_nodes(node, board, sampled_game, identity_of_bot)
        new_child_node = expand_leaf(node_to_expand, board, sampled_game)
        action_to_sim = new_child_node.parent_action
        board_state_to_sim = board.next_state(sampled_game, action_to_sim)
        result_of_action = rollout(board, board_state_to_sim)

        if identity_of_bot == 1:
            win_loss_result = result_of_action[1]
            print('Player 1:')
            print(win_loss_result)
        else:
            win_loss_result = result_of_action[2]
            print('Player 2:')
            print(win_loss_result)

        if win_loss_result == 1:
            print('Win!')
        elif win_loss_result == -1:
            print('Loss!')
        else:
            print('Draw!')

        backpropagate(new_child_node, win_loss_result)


    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_action_winrate = 0
    best_node = None

    print(root_node.untried_actions)

    for action in root_node.child_nodes.values():
        current_action_winrate = action.wins / action.visits
        print(current_action_winrate)

        if current_action_winrate > best_action_winrate:
            best_node = action
            best_action_winrate = current_action_winrate

    print(best_node)
    return best_node.parent_action
