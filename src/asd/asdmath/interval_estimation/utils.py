def find_intervals_indices(mask):
    starts, ends = [], []

    for i in range(1, len(mask)):
        if not mask[i - 1] and mask[i]:
            starts.append(i)
        if mask[i - 1] and not mask[i]:
            ends.append(i - 1)

    if mask[0]:
        starts.insert(0, 0)
    if mask[-1]:
        ends.append(len(mask) - 1)

    return starts, ends
