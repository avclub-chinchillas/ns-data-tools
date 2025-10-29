import pandas as pd
import argparse
import csv
from constants import WELCOME_MESSAGE

def remove_duplicates(input_file, output_file, column_name, delimiter=','):
    """
    Remove rows from a CSV file where values in the specified column are duplicated.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to save the output CSV file
        column_name (str): Name of the column to check for duplicates
        delimiter (str): CSV delimiter character (default: ',')
    """
    try:
        # Read the CSV file with specified delimiter and error handling
        df = pd.read_csv(input_file, 
                        delimiter=delimiter,
                        on_bad_lines='warn',  # Warn about problematic lines
                        encoding='utf-8',     # Specify encoding
                        engine='python',      # Use Python engine for better error handling
                        quoting=csv.QUOTE_MINIMAL,  # Handle quotes appropriately
                        escapechar='\\')      # Handle escaped characters
        
        # Check if the column exists in the dataframe
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the CSV file")
        
        # Keep only the first occurrence of each value in the specified column
        df_cleaned = df.drop_duplicates(subset=[column_name], keep='first')
        
        # Save the cleaned data to a new CSV file
        df_cleaned.to_csv(output_file, index=False)
        
        # Print statistics
        total_rows = len(df)
        remaining_rows = len(df_cleaned)
        removed_rows = total_rows - remaining_rows
        print(f"Total rows in original file: {total_rows}")
        print(f"Rows after removing duplicates: {remaining_rows}")
        print(f"Number of rows removed: {removed_rows}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Remove rows with duplicate values in a specified column from a CSV file.')
    parser.add_argument('input_file', help='Path to the input CSV file')
    parser.add_argument('output_file', help='Path to save the output CSV file')
    parser.add_argument('column_name', help='Name of the column to check for duplicates')
    parser.add_argument('-d', '--delimiter', default=',', 
                      help='CSV delimiter character (default: comma)')
    
    # Parse arguments
    args = parser.parse_args()
    
    print(WELCOME_MESSAGE)
    # Call the function to remove duplicates
    remove_duplicates(args.input_file, args.output_file, args.column_name, args.delimiter)

if __name__ == "__main__":
    main()
