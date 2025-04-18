import json
import os

def convert_bottles_for_api():
    """
    Converts fixed_bottles.json Django fixture to a format usable by the API,
    saving the result to data/bottles.json
    """
    
    input_file = 'fixed_bottles.json'
    output_dir = 'data'
    output_file = os.path.join(output_dir, 'bottles.json')
    
    try:
        # Read the Django fixture
        with open(input_file, 'r', encoding='utf-8') as f:
            bottles_fixture = json.load(f)
        
        # Create a dictionary with bottle_id as keys
        bottles_dict = {}
        
        for bottle in bottles_fixture:
            if 'fields' in bottle:
                fields = bottle['fields']
                bottle_id = fields.get('bottle_id')
                
                if bottle_id:
                    # Create a clean copy of the bottle data without Django-specific fields
                    bottle_data = {
                        'id': bottle_id,  # Include ID as a field too
                        'name': fields.get('name', ''),
                        'brand': fields.get('brand') or '',
                        'region': fields.get('region') or '',
                        'country': fields.get('country') or '',
                        'style': fields.get('style') or '',
                        'category': fields.get('category') or '',
                        'price': fields.get('price'),
                        'age': fields.get('age'),
                        'abv': fields.get('abv'),
                        'rating': fields.get('rating'),
                        'description': fields.get('description') or '',
                        # Include any additional fields needed by the API
                    }
                    
                    # Clean up None values
                    for key, value in list(bottle_data.items()):
                        if value is None:
                            bottle_data[key] = ''
                    
                    # Add to dictionary with bottle_id as key
                    bottles_dict[bottle_id] = bottle_data
        
        # Make sure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(bottles_dict, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully converted {len(bottles_dict)} bottles to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: File '{input_file}' is not valid JSON.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    convert_bottles_for_api()

