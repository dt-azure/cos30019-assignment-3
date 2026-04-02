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

        for action in sorted(problem.actions(self.state)):
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

    def expand_simple(self, problem):
        children = []

        for action in sorted(problem.actions(self.state)):
            next_state = action
            if self.contains_state(next_state):
                continue

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

    def contains_state(self, state):
        node = self
        while node is not None:
            if node.state == state:
                return True
            node = node.parent

        return False


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


def uniform_cost_top_k_search(problem, top_k=5):
    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    start_node = SearchNode(state=problem.initial)
    frontier = []
    tie_breaker = count()
    solutions = []
    seen_paths = set()

    heappush(frontier, (0.0, next(tie_breaker), start_node))

    while frontier and len(solutions) < top_k:
        _, _, node = heappop(frontier)

        if problem.goal_test(node.state):
            path_signature = tuple(node.solution())
            if path_signature not in seen_paths:
                seen_paths.add(path_signature)
                solutions.append(node)
            continue

        for child in node.expand_simple(problem):
            heappush(
                frontier,
                (child.path_cost, next(tie_breaker), child),
            )

    return solutions


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
