def detect_levels(close, order=10):
    """
    Detect support and resistance levels based on local minima and maxima.
    """
    levels = []
    prices = close.values
    idx = close.index

    for i in range(order, len(prices) - order):
        window = prices[i - order:i + order + 1]

        # Resistance = local peak
        if prices[i] == max(window):
            levels.append(("resistance", idx[i], prices[i]))

        # Support = local dip
        if prices[i] == min(window):
            levels.append(("support", idx[i], prices[i]))

    return levels
