import os

from pydantic_settings import BaseSettings

# from max_lines_n_in_a_row_3d.utils import coord_to_idx

DEBUG = os.getenv("DEBUG", "false").lower() == "true"


class Settings(BaseSettings):
    greater_matches: int = 10000
    default_matches: int = 100
    lesser_matches: int = 10

    layer_count: int = 3
    row_count: int = 3
    column_count: int = 3
    total_cells: int = layer_count * row_count * column_count
    forbidden_coords: list[tuple[int, int, int]] = [(1, 1, 1)]
    forbidden_indexes: list[int] = [
        13
        # coord_to_idx(x, y, z) for x, y, z in forbidden_coords
    ]
    move_limit: int = total_cells - len(forbidden_indexes)


settings = Settings()
