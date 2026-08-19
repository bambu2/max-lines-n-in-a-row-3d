from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False

    greater_matches: int = 10000
    default_matches: int = 100
    less_matches: int = 10

    layers: int = 3
    rows: int = 3
    columns: int = 3
    total_cells: int = layers * rows * columns
    forbidden_coords: list[tuple[int, int, int]] = [(1, 1, 1)]
    forbidden_indexes: list[int] = [13]
    move_limit: int = total_cells - len(forbidden_indexes)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
