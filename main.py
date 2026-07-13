from src.run_in_order import run_in_order, Order


def main():
    print("Hello from tic-tac-toe-3x3x3-without-the-center-cell!")
    # run_in_order(Order.WEAK_FIRST,verbose=False)
    # run_in_order(Order.STRONG_FIRST,verbose=False)
    run_in_order(Order.SAME_LEVEL, verbose=False)


if __name__ == "__main__":
    main()
