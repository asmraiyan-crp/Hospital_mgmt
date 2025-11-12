from core.models import Resource

def knapsack(resources, max_capacity):
    
    n = len(resources)
    dp = [[0 for _ in range(max_capacity + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        weight = resources[i-1].volume
        value = resources[i-1].priority_score
        for w in range(1, max_capacity + 1):
            if weight <= w:
                dp[i][w] = max(value + dp[i-1][w - weight], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]

    selected_items = []
    w = max_capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected_items.append(resources[i-1])
            w -= resources[i-1].volume

    total_value = dp[n][max_capacity]
    return selected_items, total_value


def run_knapsack(max_capacity):
    
    resources = list(Resource.objects.filter(volume__gt=0))

    selected, total_value = knapsack(resources, max_capacity)

    print(f"Max capacity: {max_capacity}")
    print(f"Total utility value: {total_value}")
    print("\nSelected Resources for Ambulance Kit:")
    for item in selected:
        print(f" - {item.name} (Qty: {item.volume}, Score: {item.priority_score})")

    return selected, total_value
