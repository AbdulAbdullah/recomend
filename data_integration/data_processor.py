import os
import json
import pandas as pd
from typing import List, Dict, Any
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and manage whisky bottle data"""
    
    def __init__(self):
        self.bottles_path = settings.BOTTLE_DATA_PATH
    
    def load_bottles(self) -> List[Dict[str, Any]]:
        """
        Load bottles data from file
        
        Returns:
            List of bottle dictionaries
        """
        if not os.path.exists(self.bottles_path):
            logger.error(f"Bottle data file not found at {self.bottles_path}")
            return []
            
        try:
            with open(self.bottles_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading bottle data: {str(e)}")
            return []
    
    def save_bottles(self, bottles: List[Dict[str, Any]]) -> bool:
        """
        Save bottles data to file
        
        Args:
            bottles: List of bottle dictionaries
            
        Returns:
            Boolean indicating success
        """
        try:
            os.makedirs(os.path.dirname(self.bottles_path), exist_ok=True)
            
            with open(self.bottles_path, 'w') as f:
                json.dump(bottles, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error saving bottle data: {str(e)}")
            return False
    
    def get_bottle_by_id(self, bottle_id: str) -> Dict[str, Any]:
        """
        Get bottle data by ID
        
        Args:
            bottle_id: ID of the bottle to retrieve
            
        Returns:
            Bottle dictionary or empty dict if not found
        """
        bottles = self.load_bottles()
        
        for bottle in bottles:
            if bottle.get('bottle_id') == bottle_id:
                return bottle
                
        return {}
    
    def get_bottles_by_criteria(
        self, 
        region: str = None,
        style: str = None,
        min_price: float = None,
        max_price: float = None,
        min_age: int = None,
        max_age: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get bottles matching specified criteria
        
        Args:
            region: Filter by region
            style: Filter by style
            min_price: Minimum price
            max_price: Maximum price
            min_age: Minimum age
            max_age: Maximum age
            
        Returns:
            List of matching bottle dictionaries
        """
        bottles = self.load_bottles()
        
        # Apply filters
        filtered_bottles = []
        for bottle in bottles:
            # Region filter
            if region and bottle.get('region') != region:
                continue
                
            # Style filter
            if style and bottle.get('style') != style:
                continue
                
            # Price filters
            price = bottle.get('price')
            if price:
                if min_price is not None and float(price) < min_price:
                    continue
                if max_price is not None and float(price) > max_price:
                    continue
                    
            # Age filters
            age = bottle.get('age')
            if age:
                if min_age is not None and int(age) < min_age:
                    continue
                if max_age is not None and int(age) > max_age:
                    continue
                    
            filtered_bottles.append(bottle)
            
        return filtered_bottles
    
    def extract_unique_values(self, field: str) -> List[str]:
        """
        Extract all unique values for a specific field
        
        Args:
            field: Field to extract unique values from
            
        Returns:
            List of unique values
        """
        bottles = self.load_bottles()
        
        values = set()
        for bottle in bottles:
            if field in bottle and bottle[field]:
                values.add(bottle[field])
                
        return sorted(list(values))
    
    def get_price_range(self) -> Dict[str, float]:
        """
        Get price range information from the bottle dataset
        
        Returns:
            Dictionary with min, max, avg prices
        """
        bottles = self.load_bottles()
        
        prices = [float(bottle['price']) for bottle in bottles if 'price' in bottle and bottle['price']]
        
        if not prices:
            return {'min': 0, 'max': 0, 'avg': 0}
            
        return {
            'min': min(prices),
            'max': max(prices),
            'avg': sum(prices) / len(prices)
        }