import random

def generate_random_matrix():
    # Ask user for matrix size
    n = int(input("Enter the matrix size n (for n x n): "))

    # Generate random integers from 1 to 9
    matrix = [[random.randint(1, 9) for _ in range(n)] for _ in range(n)]

    # Write to matrix.txt with comma-separated values
    with open("matrix.txt", "w") as f:
        for row in matrix:
            f.write(", ".join(map(str, row)) + "\n")

    print(f"\n✅ Random {n}x{n} matrix saved to matrix.txt (values 1–9).")
    print("Example output:\n")
    for row in matrix:
        print(", ".join(map(str, row)))


if __name__ == "__main__":
    generate_random_matrix()