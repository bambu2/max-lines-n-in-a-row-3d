from max_lines_n_in_a_row_3d.config import settings


def coord_to_idx(layer: int, row: int, col: int) -> int:
    return layer * (settings.columns * settings.rows) + row * settings.columns + col


def idx_to_coord(idx: int) -> tuple[int, int, int]:
    layer = idx // (settings.columns * settings.rows)
    row = (idx % (settings.columns * settings.rows)) // settings.columns
    col = idx % settings.columns
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
