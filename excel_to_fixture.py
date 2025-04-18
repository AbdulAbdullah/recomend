#!/usr/bin/env python
import argparse
import json
import os
import sys

import pandas as pd


def convert_excel_to_fixture(excel_file, model_name, app_name, output_file=None, id_field=None):
    """
    Convert Excel file to Django fixture format
    
    Args:
        excel_file (str): Path to Excel file
        model_name (str): Django model name
        app_name (str): Django app name
        output_file (str, optional): Output JSON file path. Defaults to None.
        id_field (str, optional): Field to use as primary key. Defaults to None.
    
    Returns:
        str: Path to the output JSON file
    """
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict(orient='records')
        
        # Create fixture
        fixture = []
        for i, item in enumerate(data, 1):
            # Clean data - remove NaN values and convert to appropriate Python types
            fields = {}
            for key, value in item.items():
                if pd.isna(value):
                    continue
                elif isinstance(value, pd.Timestamp):
                    fields[key] = value.isoformat()
                else:
                    fields[key] = value
            
            # Determine the primary key
            pk = i
            if id_field and id_field in fields:
                pk = fields[id_field]
            
            # Create fixture item
            fixture_item = {
                "model": f"{app_name}.{model_name.lower()}",
                "pk": pk,
                "fields": fields
            }
            fixture.append(fixture_item)
        
        # Determine output filename if not provided
        if not output_file:
            base_name = os.path.splitext(os.path.basename(excel_file))[0]
            output_file = f"{base_name}_fixture.json"
        
        # Write to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fixture, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully converted '{excel_file}' to Django fixture: '{output_file}'")
        return output_file
    
    except FileNotFoundError:
        print(f"Error: File '{excel_file}' not found.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: File '{excel_file}' is empty.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Convert Excel file to Django fixture format')
    parser.add_argument('excel_file', help='Path to Excel file')
    parser.add_argument('--model', required=True, help='Django model name')
    parser.add_argument('--app', required=True, help='Django app name')
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--id-field', help='Field to use as primary key')
    
    args = parser.parse_args()
    
    output_file = convert_excel_to_fixture(
        args.excel_file, 
        args.model, 
        args.app, 
        args.output, 
        args.id_field
    )
    
    print(f"You can now load the fixture using:")
    print(f"python manage.py loaddata {output_file}")


if __name__ == '__main__':
    main()

