'''
Mathematical utilities for the Analisi Statistica dei Dati notes.
'''

def find_intervals(mask):
    '''
    Find the start and end indices of contiguous True values in a boolean array.
    '''

    starts = []
    ends = []
    for i in range(1, len(mask)):
        if not mask[i-1] and mask[i]:
            starts.append(i)
        if mask[i-1] and not mask[i]:
            ends.append(i-1)
    if mask[0]:
        starts.insert(0, 0)
    if mask[-1]:
        ends.append(len(mask)-1)

    return starts, ends
