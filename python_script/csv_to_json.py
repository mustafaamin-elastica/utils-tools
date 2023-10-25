import csv
import json
import argparse

# Create command-line argument parser
parser = argparse.ArgumentParser(description='Convert CSV to JSON with key-value pairs')
parser.add_argument('input_csv', help='Input CSV file')
parser.add_argument('output_json', help='Output JSON file')

# Parse command-line arguments
args = parser.parse_args()

# Read the CSV file and convert it to JSON with proper encoding
data = {}

with open(args.input_csv, 'r', encoding='utf-8') as csv_input:
    csv_reader = csv.reader(csv_input)
    for row in csv_reader:
        data[row[0]] = row[1]

# Write the JSON data to the specified output file with proper encoding
with open(args.output_json, 'w', encoding='utf-8') as json_output:
    json.dump(data, json_output, ensure_ascii=False, indent=4)

print(f'Conversion complete. JSON data saved to {args.output_json}')