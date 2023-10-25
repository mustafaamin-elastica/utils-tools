import json
import argparse

def find_difference(json1, json2, output_json1, output_json2):
    # Read the first JSON file with Arabic encoding support
    with open(json1, 'r', encoding='utf-8') as file1:
        data1 = json.load(file1)

    # Read the second JSON file with Arabic encoding support
    with open(json2, 'r', encoding='utf-8') as file2:
        data2 = json.load(file2)

    # Find keys that are in the first JSON but not in the second
    difference1 = {key: value for key, value in data1.items() if key not in data2}

    # Find keys that are in the second JSON but not in the first
    difference2 = {key: value for key, value in data2.items() if key not in data1}

    # Write the differences to the output JSON files
    with open(output_json1, 'w', encoding='utf-8') as output_file1:
        json.dump(difference1, output_file1, ensure_ascii=False, indent=4)

    with open(output_json2, 'w', encoding='utf-8') as output_file2:
        json.dump(difference2, output_file2, ensure_ascii=False, indent=4)

    print(f'Differences found. Result JSON data saved to {output_json1} and {output_json2}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find the differences between two JSON files.')
    parser.add_argument('json1', help='First JSON file (الملف JSON الأول)')
    parser.add_argument('json2', help='Second JSON file (الملف JSON الثاني)')
    parser.add_argument('output_json1', help='Output JSON file for keys in the first JSON (ملف JSON الإخراج للمفاتيح في الملف الأول)')
    parser.add_argument('output_json2', help='Output JSON file for keys in the second JSON (ملف JSON الإخراج للمفاتيح في الملف الثاني)')

    args = parser.parse_args()

    find_difference(args.json1, args.json2, args.output_json1, args.output_json2)
