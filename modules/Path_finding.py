import math
import heapq

def cost(a, layer_nodes, layer, weight=1.0):
    lat1, lon1 = a
    dists = []
    for lat2, lon2 in layer_nodes:
        dist = math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)
        dists.append(dist)

    base_cost = min(dists)

    return base_cost * (1 + layer * weight)


def shortest_path(tree, weight=0.2, mode="min"):
    """
    tree: [[(lat, lon)], [(lat, lon), ...], ..., [(lat, lon)]]
    시작층 → 마지막층 최소 비용 경로 탐색
    weight: 층 가중치 (크면 깊을수록 코스트가 더 커짐)
    mode  : cost 계산 방식 ("min", "avg", "sum")
    """
    n_layers = len(tree)
    start = (0, 0)   # (layer, index)
    goal_layer = n_layers - 1

    # (누적 비용, layer, idx, 경로)
    pq: list[tuple[float, int, int, list]] = [(0, start[0], start[1], [tree[start[0]][start[1]]])]
    visited = set()

    while pq:
        total_cost, layer, idx, path = heapq.heappop(pq)

        # 목표 도달
        if layer == goal_layer:
            return path

        if (layer, idx) in visited:
            continue
        visited.add((layer, idx))

        current = tree[layer][idx]

        # 앞쪽 레벨로 이동
        if layer + 1 < n_layers:
            next_layer_nodes = tree[layer + 1]
            for j, next_node in enumerate(next_layer_nodes):
                c = cost(current, next_layer_nodes, layer, weight)
                heapq.heappush(pq, (total_cost + c, layer + 1, j, path + [next_node]))

        # 뒤쪽 레벨로 이동 (옵션)
        if layer - 1 >= 0:
            prev_layer_nodes = tree[layer - 1]
            for j, prev_node in enumerate(prev_layer_nodes):
                c = cost(current, prev_layer_nodes, layer, weight)
                heapq.heappush(pq, (total_cost + c, layer - 1, j, path + [prev_node]))

    return None  # 경로 없음
