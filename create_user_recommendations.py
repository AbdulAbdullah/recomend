import json
import random
import datetime
import math
from decimal import Decimal

def get_recommendation_reason(spirit_type, price, brand, name, popularity):
    """Generate a meaningful recommendation reason based on the product attributes."""
    
    # Base reasons by spirit type
    spirit_reasons = {
        "Bourbon": [
            "Based on your preference for bourbon, you'll enjoy this smooth, well-balanced expression.",
            "This bourbon offers excellent value with rich caramel and vanilla notes you tend to enjoy.",
            "As a bourbon enthusiast, you'll appreciate the oak-forward profile of this selection."
        ],
        "Whisky": [
            "This whisky aligns with your preference for complex, aged spirits.",
            "Given your interest in whisky, this expression offers a unique flavor profile worth exploring.",
            "This whisky complements your collection with its distinctive character."
        ],
        "Canadian Whisky": [
            "Based on your collection, this Canadian whisky will expand your horizons with its smooth profile.",
            "This Canadian whisky offers an approachable yet complex experience you'll appreciate.",
            "Your preference for nuanced whisky makes this Canadian expression a great fit."
        ],
        "Gin": [
            "The botanical profile of this gin matches your preference for aromatic spirits.",
            "This gin offers a balanced juniper character that complements your collection.",
            "Based on your interest in craft spirits, this gin's unique botanicals will appeal to you."
        ]
    }
    
    # Generic spirit reason if specific type not found
    if spirit_type not in spirit_reasons:
        spirit_reasons[spirit_type] = [
            f"This {spirit_type.lower()} matches your preference for quality spirits.",
            f"Based on your collection, you'll enjoy this {spirit_type.lower()} expression.",
            f"This {spirit_type.lower()} offers excellent value and complements your tastes."
        ]
    
    # Price-based reasons
    if price is None:
        price_reason = ""
    elif price < 40:
        price_reason = "It's an affordable daily option that doesn't compromise on quality."
    elif price < 80:
        price_reason = "It offers excellent quality at a mid-range price point."
    elif price < 150:
        price_reason = "This premium selection is worth the investment for special occasions."
    else:
        price_reason = "This high-end expression represents the pinnacle of craftsmanship."
    
    # Popularity-based comment
    if popularity is None or popularity < 10:
        popularity_comment = "It's a hidden gem that's not widely known."
    elif popularity < 100:
        popularity_comment = "It has a growing following among enthusiasts."
    elif popularity < 1000:
        popularity_comment = "It's well-regarded in the community."
    else:
        popularity_comment = "It's extremely popular for good reason."
    
    # Combine reasons
    spirit_reason = random.choice(spirit_reasons[spirit_type])
    
    # Build complete reason
    reason_parts = [spirit_reason]
    if price_reason:
        reason_parts.append(price_reason)
    reason_parts.append(f"{brand}'s {name} is crafted with attention to detail. {popularity_comment}")
    
    return " ".join(reason_parts)

def calculate_score(fill_percentage, popularity):
    """Calculate a recommendation score based on fill percentage and popularity."""
    # Base score from fill percentage (users tend to fill bottles they like)
    if fill_percentage is None:
        base_score = 0.7  # Default if fill percentage is not available
    else:
        base_score = 0.5 + (fill_percentage / 200)  # 0.5 to 1.0 based on fill
    
    # Adjust with popularity (if available)
    popularity_factor = 0
    if popularity is not None and popularity > 0:
        # Log scale for popularity to avoid extreme values
        popularity_factor = min(0.3, math.log10(popularity + 1) / 10)
    
    final_score = min(0.99, base_score + popularity_factor)
    return round(final_score, 2)

def get_bottle_by_product_id(product_id, bottles_by_id):
    """Find a bottle in our database that matches the product ID from username.json"""
    # Convert product_id to string for comparison
    product_id_str = str(product_id)
    
    # Direct lookup by bottle_id
    if product_id_str in bottles_by_id:
        return bottles_by_id[product_id_str]
    
    # If we can't find a direct match, return None
    return None

def load_bottles_from_json(filename='fixed_bottles.json'):
    """Load bottles from a JSON file and create a lookup dictionary by bottle_id"""
    bottles_by_id = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            bottle_data = json.load(f)
            for bottle in bottle_data:
                if 'fields' in bottle and 'bottle_id' in bottle['fields']:
                    bottle_id = bottle['fields']['bottle_id']
                    bottles_by_id[bottle_id] = bottle
        print(f"Loaded {len(bottles_by_id)} bottles from {filename}")
        
        # Print some sample bottle IDs for debugging
        sample_ids = list(bottles_by_id.keys())[:5]
        print(f"Sample bottle IDs: {sample_ids}")
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        bottles_by_id = {}  # Empty dict if all else fails
        
    return bottles_by_id

def main():
    # Input and output files
    input_file = 'username.json'
    output_file = 'user_recommendations.json'
    
    try:
        # Load bottles from fixed_bottles.json
        bottles_by_id = load_bottles_from_json()
        
        # Read the username.json file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create UserRecommendation fixtures
        fixtures = []
        valid_count = 0
        skipped_count = 0
        
        for i, entry in enumerate(data, 1):
            try:
                # Extract data
                username = entry.get('user', {}).get('user_name', 'unknown_user')
                product = entry.get('product', {})
                product_id = product.get('id')
                
                if not product_id:
                    print(f"Skipping entry {i}: No product ID found")
                    skipped_count += 1
                    continue
                
                # Find matching bottle in our database
                bottle = get_bottle_by_product_id(str(product_id), bottles_by_id)
                if not bottle:
                    print(f"Skipping entry {i}: No matching bottle found for product ID '{product_id}'")
                    skipped_count += 1
                    continue
                
                # Get the correct bottle ID from the JSON dictionary
                bottle_pk = bottle.get('pk')
                bottle_id_str = bottle.get('fields', {}).get('bottle_id')
                
                # Get additional data
                fill_percentage = entry.get('fill_percentage')
                popularity = product.get('popularity')
                created_at = entry.get('created_at')
                
                # Get product details for reason generation
                spirit_type = product.get('spirit', 'Spirit')
                price = product.get('average_msrp')
                brand = product.get('brand', '')
                name = product.get('name', '')
                
                # Calculate score
                score = calculate_score(fill_percentage, popularity)
                
                # Generate recommendation reason
                reason = get_recommendation_reason(spirit_type, price, brand, name, popularity)
                
                # Create fixture entry
                fixture_entry = {
                    "model": "api.userrecommendation",
                    "pk": valid_count + 1,  # Reindex to ensure sequential PKs
                    "fields": {
                        "username": username,
                        "bottle": bottle_pk,  # Foreign key to Bottle model by ID
                        "score": score,
                        "reason": reason,
                        "created_at": created_at or datetime.datetime.now().isoformat()
                    }
                }
                fixtures.append(fixture_entry)
                valid_count += 1
                print(f"Added recommendation for {username} and bottle {bottle_id_str}")
                
            except Exception as e:
                print(f"Error processing entry {i}: {str(e)}")
                continue
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fixtures, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created {valid_count} UserRecommendation fixtures (skipped {skipped_count} entries).")
        print(f"Output saved to {output_file}")
        print(f"You can load the fixture using: python manage.py loaddata {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

