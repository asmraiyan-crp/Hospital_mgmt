def solve_knapsack(resources, max_capacity):
    """
    0/1 Knapsack Algorithm with Item Expansion.
    
    Args:
        resources: List of Resource objects (Django models)
        max_capacity: Integer capacity limit
        
    Returns:
        selected_items: List of Resource objects chosen
        total_value: Total priority score
    """
    # 1. Expand resources based on quantity
    # If we have Item A with quantity 2, we create [Item A, Item A]
    expanded_items = []
    for r in resources:
        count = r.quantity if r.quantity else 1
        for _ in range(count):
            # We simply append the resource 'count' times. 
            # We do NOT modify r.volume here.
            expanded_items.append(r)

    n = len(expanded_items)
    # DP Table: rows = items, cols = capacity 0 to max_capacity
    dp = [[0 for _ in range(max_capacity + 1)] for _ in range(n + 1)]

    # 2. Build DP Table
    for i in range(1, n + 1):
        item = expanded_items[i-1]
        w = item.volume
        v = item.priority_score
        
        for cap in range(1, max_capacity + 1):
            if w <= cap:
                # Max of: (value of this item + value of remaining space) OR (value without this item)
                dp[i][cap] = max(v + dp[i-1][cap - w], dp[i-1][cap])
            else:
                dp[i][cap] = dp[i-1][cap]

    # 3. Backtrack to find selected items
    selected_items = []
    remaining_cap = max_capacity
    
    for i in range(n, 0, -1):
        if dp[i][remaining_cap] != dp[i-1][remaining_cap]:
            item = expanded_items[i-1]
            selected_items.append(item)
            remaining_cap -= item.volume

    total_value = dp[n][max_capacity]
    return selected_items, total_value