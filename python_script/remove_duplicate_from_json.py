import json
import argparse

def remove_duplicate_keys(input_json, output_json):
    # Read the JSON file with Arabic encoding support
    with open(input_json, 'r', encoding='utf-8') as json_input:
        data = json.load(json_input)

    # Create a dictionary to store unique key-value pairs
    unique_data = {}
    for key, value in data.items():
        unique_data[key] = value

    # Write the unique data to the output file
    with open(output_json, 'w', encoding='utf-8') as json_output:
        json.dump(unique_data, json_output, ensure_ascii=False, indent=4)

    print(f'Duplicate keys removed. Unique JSON data saved to {output_json}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove duplicate keys from JSON file, keeping the last occurrence.')
    parser.add_argument('input_json', help='Input JSON file (ملف JSON الإدخال)')
    parser.add_argument('output_json', help='Output JSON file (ملف JSON الإخراج)')

    args = parser.parse_args()

    remove_duplicate_keys(args.input_json, args.output_json)
