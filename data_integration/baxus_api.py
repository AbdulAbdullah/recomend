import requests
import json
from typing import Dict, Any, List
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class BaxusAPI:
    """Client for interacting with the BAXUS API"""
    
    def __init__(self):
        self.base_url = settings.BAXUS_API_BASE_URL
        self.api_key = settings.BAXUS_API_KEY
        
    def get_user_bar(self, username: str) -> Dict[str, Any]:
        """
        Retrieve user's bar data from BAXUS API
        
        Args:
            username: BAXUS username
            
        Returns:
            Dictionary containing user's bottles and wishlist
        """
        endpoint = f"{self.base_url}/bar/user/{username}"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=5)  # Add timeout
            response.raise_for_status()
            
            data = response.json()
            
            # Handle case where response is a list
            if isinstance(data, list):
                bottles = self._normalize_bottles(data)
                return {
                    'bottles': bottles,
                    'wishlist': []
                }
            
            # Handle case where response is a dictionary
            bottles = self._normalize_bottles(data.get('bottles', []))
            wishlist = self._normalize_bottles(data.get('wishlist', []))
            return {
                'bottles': bottles,
                'wishlist': wishlist
            }
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch user bar data from BAXUS API: {str(e)}")
            
            # Always return a valid data structure, even when the API call fails
            return {
                'bottles': [],
                'wishlist': []
            }
    
    def _normalize_bottles(self, bottles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure all bottles have required fields with default values"""
        normalized = []
        for bottle in bottles:
            normalized_bottle = {
                'bottle_id': bottle.get('bottle_id', ''),
                'name': bottle.get('name', ''),
                'brand': bottle.get('brand', ''),
                'region': bottle.get('region', ''),
                'style': bottle.get('style', ''),
                'country': bottle.get('country', ''),
                'price': float(bottle.get('price', 0.0)),
                'age': int(bottle.get('age', 0)),
                'abv': float(bottle.get('abv', 0.0)),
                'rating': float(bottle.get('rating', 3.0)),
                'flavor_profile': bottle.get('flavor_profile', {})
            }
            normalized.append(normalized_bottle)
        return normalized
    
    def _get_sample_user_bar(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return sample user bar data for development/testing"""
        return {
            'bottles': [
                {
                    'bottle_id': 'glenfiddich-12',
                    'name': 'Glenfiddich 12 Year Old',
                    'brand': 'Glenfiddich',
                    'region': 'Speyside',
                    'style': 'Single Malt',
                    'country': 'Scotland',
                    'price': 45.99,
                    'age': 12,
                    'abv': 40.0,
                    'rating': 4.2,
                    'flavor_profile': {
                        'fruity': 0.8,
                        'sweet': 0.7,
                        'floral': 0.5,
                        'oak': 0.4
                    }
                },
                {
                    'bottle_id': 'macallan-12',
                    'name': 'The Macallan 12 Year Old Sherry Oak',
                    'brand': 'The Macallan',
                    'region': 'Speyside',
                    'style': 'Single Malt',
                    'country': 'Scotland',
                    'price': 75.99,
                    'age': 12,
                    'abv': 43.0,
                    'rating': 4.5,
                    'flavor_profile': {
                        'sherry': 0.9,
                        'oak': 0.7,
                        'dried_fruit': 0.8,
                        'spice': 0.6
                    }
                },
                {
                    'bottle_id': 'lagavulin-16',
                    'name': 'Lagavulin 16 Year Old',
                    'brand': 'Lagavulin',
                    'region': 'Islay',
                    'style': 'Single Malt',
                    'country': 'Scotland',
                    'price': 89.99,
                    'age': 16,
                    'abv': 43.0,
                    'rating': 4.7,
                    'flavor_profile': {
                        'smoky': 0.9,
                        'peaty': 0.9,
                        'seaweed': 0.7,
                        'medicinal': 0.6
                    }
                }
            ],
            'wishlist': [
                {
                    'bottle_id': 'ardbeg-10',
                    'name': 'Ardbeg 10 Year Old',
                    'brand': 'Ardbeg',
                    'region': 'Islay',
                    'style': 'Single Malt',
                    'country': 'Scotland',
                    'price': 54.99,
                    'age': 10,
                    'abv': 46.0,
                    'rating': 4.6
                }
            ]
        }