from src.single_ai_test import single_ai_test
from src.multiple_ai_test import multiple_ai_test


def main():
    print("Hello from tic-tac-toe-3x3x3-without-the-center-cell!")

    single_ai_test(verbose=False)

    # multiple_ai_test(weak_first=True)


if __name__ == "__main__":
    main()
