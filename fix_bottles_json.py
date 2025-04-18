import json
import os
import decimal
from decimal import Decimal

# Load the generated JSON file
input_file = 'bottles.json'
output_file = 'fixed_bottles.json'

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Process each bottle entry
    fixed_data = []
    for entry in data:
        # Create a new entry with correct field mappings
        new_entry = {
            "model": "api.bottle",
            "pk": entry["pk"]  # Keep the same primary key
        }
        
        # Extract fields from the original entry
        fields = entry.get("fields", {})
        
        # Map fields according to the Bottle model structure
        new_fields = {
            "bottle_id": str(fields.get("id", "")),
            "name": fields.get("name", ""),
            "brand": None,  # Not in the Excel data
            "region": None,  # Not in the Excel data
            "country": None,  # Not in the Excel data
            "style": None,  # Not in the Excel data
            "category": fields.get("spirit_type"),
            "price": float(fields.get("avg_msrp", 0)) if fields.get("avg_msrp") is not None else None,
            "age": None,  # Not in the Excel data
            "abv": float(fields.get("abv", 0)) if fields.get("abv") is not None else None,
            "rating": (float(fields.get("total_score", 0)) / 10000) if fields.get("total_score") is not None else None,
            "flavor_profile": None,  # Not in the Excel data
            "description": None,  # Not in the Excel data
        }
        
        # Add the new fields to the entry
        new_entry["fields"] = new_fields
        fixed_data.append(new_entry)
    
    # Write the fixed data to a new JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully modified {input_file} to match Bottle model structure.")
    print(f"Fixed file saved as: {output_file}")
    print(f"You can now load the fixture using: python manage.py loaddata {output_file}")

except FileNotFoundError:
    print(f"Error: File '{input_file}' not found.")
except json.JSONDecodeError:
    print(f"Error: File '{input_file}' is not valid JSON.")
except Exception as e:
    print(f"Error: {str(e)}")

