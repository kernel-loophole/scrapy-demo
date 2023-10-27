import json
def format(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    merged_data = {}
    for item in data:
        category = item.get("CategoryTitle")

        if category not in merged_data:
            merged_data[category] = item
        else:
            existing_item = merged_data[category]
            existing_subcategories = existing_item.get("Subcategories", [])
            new_subcategories = item.get("Subcategories", [])

            # Merge the subcategories
            merged_subcategories = existing_subcategories + new_subcategories
            existing_item["Subcategories"] = merged_subcategories

    merged_data_list = list(merged_data.values())
    
    with open('final_data.json', 'w') as merged_json_file:
        json.dump(merged_data_list, merged_json_file, indent=4)

