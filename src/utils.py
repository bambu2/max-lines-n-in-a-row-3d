
def xyz_to_idx(layer, row, col):
    return layer * 9 + row * 3 + col


def idx_to_xyz(idx):
    layer = idx // 9
    row = (idx % 9) // 3
    col = idx % 3
    return layer, row, col


def rate_to_percentage(rate: float) -> str:
    return f"{rate * 100:.1f}%"



