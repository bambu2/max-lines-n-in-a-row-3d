# 空心立方体井字棋对弈程序

这是一个基于 Python 的空心立方体井字棋对弈程序，棋盘中心位置被移除，包含 5 种不同强度的算法，支持多种对弈模式。

## 运行方式

### 环境要求

- Python 3.10+
- 依赖库：`tqdm`

### 安装依赖

```bash
uv install
```

### 运行程序

```bash
python main.py
```

### 运行特定模式

```python
from src.run_in_order import run_in_order, Order

# 运行弱算法先手模式
run_in_order(Order.WEAK_FIRST, verbose=False)

# 运行强算法先手模式
run_in_order(Order.STRONG_FIRST, verbose=False)

# 运行同算法自对弈模式
run_in_order(Order.SAME_LEVEL, verbose=False)
```

### 详细模式

设置 `verbose=True` 可以打印每局的详细信息：

```python
run_in_order(Order.WEAK_FIRST, verbose=True)
```

## 游戏规则

### 棋盘结构

- 3 层 × 3 行 × 3 列 = 27 个位置
- 中心位置 (1,1,1) 即索引 13 被禁止使用
- 实际可用位置：26 个

### 玩家标记

- `·`: 空位
- `X`: 先手玩家（玩家A）
- `O`: 后手玩家（玩家B）
- `✦`: 禁止使用的中心位置

### 胜负判定

- 完成一条线（3 个连续同色棋子）得 1 分
- 线的类型包括：X轴方向、Y轴方向、Z轴方向、对角线、跨层对角线、体对角线
- **不含中心位置的线才有效**
- 游戏结束时得分高者获胜，得分相同为平局

## 算法

程序实现了 5 种不同强度的算法，按强度从弱到强排序：

### 1. 随机策略 (Random)

- 从合法位置中随机选择
- 最简单的策略，无任何决策逻辑
- 用于基准测试

### 2. 贪心策略 (Greedy)

- 选择能立即形成最多线的位置
- 包含基本防守逻辑（优先阻止对手成线）
- 评分规则：进攻得分 × 10 + 防守得分 × 5

### 3. 高级启发式策略 (Advanced)

- 使用评估函数评估每个位置的潜力
- 综合进攻得分、防守得分和位置加成
- 支持多步预判（识别差一步完成线的威胁）

### 4. 极小极大策略 (Minimax)

- 使用带 alpha-beta 剪枝的 minimax 算法
- 搜索深度为 4 层
- 从玩家 1 视角评估，正数有利于玩家 1

### 5. 蒙特卡洛树搜索 (MCTS)

- 使用 UCT（Upper Confidence Bound for Trees）算法进行节点选择
- 默认迭代 500 次
- 包含选择、扩展、模拟、回传四个阶段

## 对弈模式

程序支持三种对弈模式：

| 模式           | 说明                       | 对局数                              |
| -------------- | -------------------------- | ----------------------------------- |
| `WEAK_FIRST`   | 较弱算法先手，较强算法后手 | 100                                 |
| `STRONG_FIRST` | 较强算法先手，较弱算法后手 | 100                                 |
| `SAME_LEVEL`   | 同一种算法自对弈           | 随机vs随机: 10000，Minimax/MCTS: 10 |

## 统计结果

程序会输出以下统计信息：

### 胜负统计

- 先手胜场数及胜率
- 后手胜场数及胜率
- 平局数及平局率

### 连线数统计

- 先手连线数：最高、最低、平均值
- 后手连线数：最高、最低、平均值
- 平均连线数差

### 耗时统计

- 平均每局耗时
- 总耗时

## 项目结构

``` text
hollow-cube-tic-tac-toe/
├── .python-version          # Python 版本配置
├── main.py                  # 程序入口
├── pyproject.toml           # 项目配置
├── uv.lock                  # 依赖锁文件
├── README.md                # 项目文档
├── assets/                   # 模型文件（Blender）
│   ├── advanced.blend
│   ├── greedy.blend
│   └── minimax.blend
└── src/                     # 源代码目录
    ├── state_and_stat.py    # 游戏状态和统计模块
    ├── run_in_order.py      # 对弈顺序控制模块
    ├── utils.py             # 工具函数
    ├── __init__.py
    └── algorithms/          # AI算法模块
        ├── random.py        # 随机策略
        ├── greedy.py        # 贪心策略
        ├── advanced.py      # 高级启发式策略
        ├── minimax.py       # 极小极大策略（带alpha-beta剪枝）
        └── mcts.py          # 蒙特卡洛树搜索策略
        ├── __init__.py
```

## 代码说明

### 核心模块

#### `state_and_stat.py`

- `GameState`: 游戏状态管理类，包含棋盘、得分、落子历史等
- `Stat`: 对局统计数据类，记录胜负次数、得分、耗时等
- `get_stat()`: 运行多局对弈并收集统计信息

#### `run_in_order.py`

- `Order`: 对弈顺序枚举（WEAK_FIRST, STRONG_FIRST, SAME_LEVEL）
- `run_in_order()`: 按指定顺序运行所有算法对弈
- `run()`: 执行一组对弈并打印统计结果

#### `utils.py`

- `xyz_to_idx()`: 将三维坐标转换为一维索引
- `idx_to_xyz()`: 将一维索引转换为三维坐标
- `rate_to_percentage()`: 将比率转换为百分比字符串

### 算法接口

所有策略函数遵循统一接口：

```python
def get_move_xxx(state: GameState, player: int) -> int | None:
    """
    获取最优走法。
    
    Args:
        state: 当前游戏状态
        player: 当前玩家（1或-1）
    
    Returns:
        int | None: 选中的位置索引，如果没有合法位置则返回None
    """
```

## 扩展说明

### 添加新算法

在 `src/algorithms/` 目录下创建新文件，实现策略函数，并在 `__init__.py` 中导出：

```python
# src/algorithms/my_algorithm.py
from src.state_and_stat import GameState


def get_move_my_algorithm(state: GameState, player: int) -> int | None:
    # 实现你的算法逻辑
    pass
```

```python
# src/algorithms/__init__.py
from src.algorithms.my_algorithm import get_move_my_algorithm

__all__ = [
    # ... 其他算法
    "get_move_my_algorithm",
]
```

### 调整对弈顺序

在 `src/run_in_order.py` 中的 `run_in_order()` 函数里调整算法列表顺序：

```python
fn_list = [
    get_move_random,
    get_move_greedy,
    get_move_advanced,
    get_move_minimax,
    get_move_mcts,
    # 添加新算法
    get_move_my_algorithm,
]
```

## License

MIT License
