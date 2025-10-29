import csv
import argparse
from constants import WELCOME_MESSAGE

def remove_blanks(input_file, output_file):
    """
    Remove blank rows from a CSV file.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to save the output CSV file
    """
    with open(input_file, 'r', newline='') as infile, \
        open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            # Check if the row is not entirely empty (e.g., contains non-whitespace characters)
            if any(field.strip() for field in row):
                writer.writerow(row)

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Remove blank rows from a CSV file.')
    parser.add_argument('input_file', help='Path to the input CSV file')
    parser.add_argument('output_file', help='Path to save the output CSV file')

    # Parse arguments
    args = parser.parse_args()

    print(WELCOME_MESSAGE)
    # Call the function to remove blank rows
    remove_blanks(args.input_file, args.output_file)

if __name__ == "__main__":
    main()