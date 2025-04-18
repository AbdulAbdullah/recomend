import pandas as pd
import numpy as np
from typing import Dict, List, Any

class CollectionAnalyzer:
    """Analyzes a user's whisky collection to extract preferences"""
    
    def __init__(self):
        self.preference_weights = {
            'region': 0.25,
            'style': 0.25,
            'price_range': 0.15,
            'age': 0.15,
            'flavor_profile': 0.20
        }
    
    def analyze_collection(self, bottles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes the user's collection to extract preferences
        
        Args:
            bottles: List of bottle data from the user's collection
            
        Returns:
            Dictionary containing user preference profile
        """
        if not bottles:
            return {
                'regions': {},
                'styles': {},
                'price_range': {'min': 0, 'max': 0, 'avg': 0},
                'age_preference': {'min': 0, 'max': 0, 'avg': 0},
                'flavor_profile': {},
                'top_characteristics': []
            }
        
        df = pd.DataFrame(bottles)
        
        # Extract region preferences
        region_counts = self._extract_region_preferences(df)
        
        # Extract style preferences
        style_counts = self._extract_style_preferences(df)
        
        # Extract price range preferences
        price_range = self._extract_price_range(df)
        
        # Extract age preferences
        age_preference = self._extract_age_preference(df)
        
        # Extract flavor profile preferences
        flavor_profile = self._extract_flavor_profile(df)
        
        # Identify top characteristics
        top_characteristics = self._identify_top_characteristics(
            region_counts, style_counts, flavor_profile
        )
        
        return {
            'regions': region_counts,
            'styles': style_counts,
            'price_range': price_range,
            'age_preference': age_preference,
            'flavor_profile': flavor_profile,
            'top_characteristics': top_characteristics
        }
    
    def _extract_region_preferences(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract region preferences with normalized weights"""
        if 'region' not in df.columns or df['region'].isna().all():
            return {}
            
        region_counts = df['region'].value_counts(normalize=True).to_dict()
        return region_counts
    
    def _extract_style_preferences(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract style preferences with normalized weights"""
        if 'style' not in df.columns or df['style'].isna().all():
            return {}
            
        style_counts = df['style'].value_counts(normalize=True).to_dict()
        return style_counts
    
    def _extract_price_range(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract price range preferences"""
        if 'price' not in df.columns or df['price'].isna().all():
            return {'min': 0, 'max': 0, 'avg': 0}
            
        prices = df['price'].dropna()
        if len(prices) == 0:
            return {'min': 0, 'max': 0, 'avg': 0}
            
        return {
            'min': float(prices.min()),
            'max': float(prices.max()),
            'avg': float(prices.mean())
        }
    
    def _extract_age_preference(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract age statement preferences"""
        if 'age' not in df.columns or df['age'].isna().all():
            return {'min': 0, 'max': 0, 'avg': 0}
            
        ages = df['age'].dropna()
        if len(ages) == 0:
            return {'min': 0, 'max': 0, 'avg': 0}
            
        return {
            'min': float(ages.min()),
            'max': float(ages.max()),
            'avg': float(ages.mean())
        }
    
    def _extract_flavor_profile(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract flavor profile preferences"""
        if 'flavor_profile' not in df.columns or df['flavor_profile'].isna().all():
            return {}
        
        # Combine flavor profiles from all bottles
        combined_profile = {}
        valid_profiles = [fp for fp in df['flavor_profile'] if isinstance(fp, dict)]
        
        if not valid_profiles:
            return {}
            
        for profile in valid_profiles:
            for flavor, intensity in profile.items():
                if flavor in combined_profile:
                    combined_profile[flavor] += float(intensity)
                else:
                    combined_profile[flavor] = float(intensity)
        
        # Normalize the combined profile
        total = sum(combined_profile.values())
        if total > 0:
            combined_profile = {k: v/total for k, v in combined_profile.items()}
            
        return combined_profile
    
    def _identify_top_characteristics(
        self, 
        regions: Dict[str, float], 
        styles: Dict[str, float], 
        flavors: Dict[str, float],
        top_n: int = 5
    ) -> List[str]:
        """Identify top characteristics from the collection"""
        characteristics = []
        
        # Add top regions
        if regions:
            top_regions = sorted(regions.items(), key=lambda x: x[1], reverse=True)[:2]
            characteristics.extend([f"Region: {r[0]}" for r in top_regions])
        
        # Add top styles
        if styles:
            top_styles = sorted(styles.items(), key=lambda x: x[1], reverse=True)[:2]
            characteristics.extend([f"Style: {s[0]}" for s in top_styles])
        
        # Add top flavors
        if flavors:
            top_flavors = sorted(flavors.items(), key=lambda x: x[1], reverse=True)[:3]
            characteristics.extend([f"Flavor: {f[0]}" for f in top_flavors])
        
        return characteristics[:top_n]