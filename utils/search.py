from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count


@dataclass
class SearchNode:
    state: int
    parent: "SearchNode | None" = None
    action: int | None = None
    path_cost: float = 0.0

    def expand(self, problem):
        children = []

        for action in problem.actions(self.state):
            next_state = action
            next_cost = problem.path_cost(self.path_cost, self.state, action, next_state)
            children.append(
                SearchNode(
                    state=next_state,
                    parent=self,
                    action=action,
                    path_cost=next_cost,
                )
            )

        return children

    def path(self):
        node = self
        nodes = []

        while node is not None:
            nodes.append(node)
            node = node.parent

        return list(reversed(nodes))

    def solution(self):
        return [node.state for node in self.path()]


def astar_search(problem):
    return best_first_graph_search(
        problem,
        priority_function=lambda node: node.path_cost + problem.h(node),
    )


def uniform_cost_search(problem):
    return best_first_graph_search(
        problem,
        priority_function=lambda node: node.path_cost,
    )


def best_first_graph_search(problem, priority_function):
    start_node = SearchNode(state=problem.initial)

    if problem.goal_test(start_node.state):
        return start_node

    frontier = []
    tie_breaker = count()
    best_path_costs = {start_node.state: 0.0}

    heappush(
        frontier,
        (priority_function(start_node), next(tie_breaker), start_node),
    )

    while frontier:
        _, _, node = heappop(frontier)

        if node.path_cost > best_path_costs.get(node.state, float("inf")):
            continue

        if problem.goal_test(node.state):
            return node

        for child in node.expand(problem):
            best_known_cost = best_path_costs.get(child.state, float("inf"))
            if child.path_cost >= best_known_cost:
                continue

            best_path_costs[child.state] = child.path_cost
            heappush(
                frontier,
                (priority_function(child), next(tie_breaker), child),
            )

    return None


def extract_path_states(goal_node):
    return goal_node.solution()

