import os
import numpy as np

def load_board_until_ok(default_name="matrix.txt"):
    """
    Keep asking for a filename until we can read a valid square integer matrix.
    Tries 'matrix.txt' first; on failure, prompts the user repeatedly.
    """
    tried_default = False

    while True:
        # Try the default once; afterwards, prompt the user
        if not tried_default:
            candidate = default_name
            tried_default = True
        else:
            name = input("Enter board filename (.txt optional): ").strip()
            if not name:
                print("Please enter a filename.\n")
                continue
            root, ext = os.path.splitext(name)
            candidate = name if ext else name + ".txt"

        try:
            return open_file(candidate)
        except (FileNotFoundError, ValueError, OSError) as e:
            print(f"{type(e).__name__}: {e}")
            print("Let's try again.\n")


def open_file(name):
    """
    Read a text file containing comma-separated integers per line
    and return a square NumPy matrix (dtype=int).

    Raises:
      - FileNotFoundError
      - ValueError (for non-numeric data, inconsistent rows, non-square, empty)
      - OSError (other I/O issues)
    """
    # Accept absolute or relative path
    input_file_name = name if os.path.isabs(name) else os.path.join(os.getcwd(), name)

    matrix_values = []

    with open(input_file_name, 'rt') as input_file:  # rt = read text
        for line_number, line in enumerate(input_file, start=1):
            stripped = line.strip()
            if not stripped:               # skip empty lines
                continue
            parts = stripped.split(',')
            row = []
            for value in parts:
                value = value.strip()
                try:
                    row.append(int(value))
                except ValueError:
                    raise ValueError(f"Non-numeric value '{value}' on line {line_number}.")
            matrix_values.append(row)

    if not matrix_values:
        raise ValueError("The file is empty.")

    row_length = len(matrix_values[0])

    # Ensure all rows have the same length
    if any(len(row) != row_length for row in matrix_values):
        raise ValueError("Rows have inconsistent lengths.")

    # Ensure the matrix is square
    if len(matrix_values) != row_length:
        raise ValueError("Matrix is not square (requires N×N).")
    # Build NumPy array
    return np.array(matrix_values, dtype=object)
