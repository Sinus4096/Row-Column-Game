import os
import numpy as np

def load_board_until_ok(default_name="boards/board.txt"):
    """ The `fileReading` module safely loads and validates the initial game board matrix from a text file.

        The primary function, `load_board_until_ok`, repeatedly prompts the user for a
        filename until a valid file containing a square matrix of integers is successfully
        read. It first attempts to load a default file (`boards/board.txt`).

        The core file parsing and validation logic resides in `open_file`, which checks for:
        1. File existence;
        2. Square dimensions;
        3. Consistent row lengths;
        4. Numeric data (integers) in every cell.

        Upon success, it returns the data as a NumPy array for use by the main `GameHandler`.
        """

    tried_default = False   # track whether the default file has already been attempted

    while True:
        #try the default once; afterwards, prompt the user
        if not tried_default:
            candidate = default_name # first attempt uses the predetermined default file
            tried_default = True
        else:
            # ask the user for a filename if default failed
            name = input("Enter board filename (.txt optional): ").strip()
            if not name:
                print("Please enter a filename.\n")
                continue

            # allow input without .txt by adding extension if missing
            root, ext = os.path.splitext(name)
            candidate = name if ext else name + ".txt"

        try:
            # attempt to load and validate the selected file
            return open_file(candidate)
        except (FileNotFoundError, ValueError, OSError) as e:
            # print the exact error type and message for debugging clarity
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
    #accept absolute or relative path
    # if the user gives a relative filename, prepend current working directory
    input_file_name = name if os.path.isabs(name) else os.path.join(os.getcwd(), name)

    matrix_values = [] # store parsed rows before converting to numpy array

    with open(input_file_name, 'rt') as input_file:  # rt = read text
        for line_number, line in enumerate(input_file, start=1):
            stripped = line.strip()
            if not stripped: # skip empty lines
                continue

            #support two common formats: comma-separated or whitespace-separated
            if ',' in stripped: parts = stripped.split(',')
            else: parts = stripped.split()

            row = []
            for value in parts:
                value = value.strip()
                try:
                    row.append(int(value))   # ensure each entry is a valid integer
                except ValueError:
                    raise ValueError(f"Non-numeric value '{value}' on line {line_number}.")
            matrix_values.append(row)

    if not matrix_values:
        raise ValueError("The file is empty.")   # no usable data found

    row_length = len(matrix_values[0])  #reference length from the first row

    #ensure all rows have the same length
    if any(len(row) != row_length for row in matrix_values):
        raise ValueError("Rows have inconsistent lengths.")

    # ensure the matrix is square
    if len(matrix_values) != row_length:
        raise ValueError("Matrix is not square (requires N×N).")

    # Build NumPy array (dtype=object preserves formatting for game use)
    return np.array(matrix_values, dtype=object)
