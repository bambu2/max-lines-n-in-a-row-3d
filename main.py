from src.set_ai_order import set_ai_order
from src.set_ai_order import Order


def main():
    print("Hello from tic-tac-toe-3x3x3-without-the-center-cell!")
    set_ai_order(Order.SAME_LEVEL, verbose=False)


if __name__ == "__main__":
    main()
