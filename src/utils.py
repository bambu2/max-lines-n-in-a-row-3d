def coord_to_idx(layer: int, row: int, col: int) -> int:
    """
    将三维坐标 (layer, row, col) 转换为一维索引。

    3x3x3 棋盘的索引映射：
    - layer: 0-2（层）
    - row: 0-2（行）
    - col: 0-2（列）

    索引计算方式：layer * 9 + row * 3 + col
    范围：0-26，其中 13 为被禁止的中心位置

    Args:
        layer: 层数（0-2）
        row: 行号（0-2）
        col: 列号（0-2）

    Returns:
        int: 一维索引（0-26）
    """
    return layer * 9 + row * 3 + col


def idx_to_coord(idx: int) -> tuple[int, int, int]:
    """
    将一维索引转换为三维坐标 (layer, row, col)。

    Args:
        idx: 一维索引（0-26）

    Returns:
        tuple[int, int, int]: (layer, row, col) 三维坐标
    """
    layer = idx // 9
    row = (idx % 9) // 3
    col = idx % 3
    return layer, row, col


def rate_to_percentage(rate: float) -> str:
    """
    将比率转换为百分比字符串。

    Args:
        rate: 比率值（0-1）

    Returns:
        str: 百分比字符串，保留一位小数，如 "67.5%"
    """
    return f"{rate * 100:.1f}%"
