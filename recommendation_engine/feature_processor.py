import pandas as pd
import numpy as np
from typing import Dict, List, Any
from sklearn.preprocessing import MinMaxScaler


class FeatureProcessor:
    """Process and normalize whisky bottle features for recommendation"""
    
    def __init__(self):
        self.categorical_features = ['region', 'style', 'country', 'category']
        self.numerical_features = ['price', 'age', 'abv', 'rating']
        self.flavor_features = []  # Will be dynamically populated
        
    def process_bottles(self, bottles: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Process bottle data into a feature matrix
        
        Args:
            bottles: List of bottle data
            
        Returns:
            DataFrame with processed features
        """
        df = pd.DataFrame(bottles)
        
        # Process categorical features
        for feature in self.categorical_features:
            if feature in df.columns:
                df[feature] = df[feature].fillna('Unknown')
                dummies = pd.get_dummies(df[feature], prefix=feature)
                df = pd.concat([df, dummies], axis=1)
        
        # Process numerical features
        for feature in self.numerical_features:
            if feature in df.columns:
                df[feature] = df[feature].fillna(df[feature].median())
                # Normalize numerical features
                scaler = MinMaxScaler()
                df[feature] = scaler.fit_transform(df[[feature]])
        
        # Process flavor profiles
        if 'flavor_profile' in df.columns:
            df = self._process_flavor_profiles(df)
        
        # Drop original categorical columns and non-feature columns
        columns_to_drop = self.categorical_features + ['name', 'brand', 'description']
        columns_to_drop = [c for c in columns_to_drop if c in df.columns]
        
        # Ensure bottle_id is preserved
        bottle_ids = df['bottle_id'].copy() if 'bottle_id' in df.columns else None
        
        df = df.drop(columns=columns_to_drop, errors='ignore')
        
        # Add bottle_id back if it was present
        if bottle_ids is not None:
            df['bottle_id'] = bottle_ids
            
        return df
    
    def _process_flavor_profiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process flavor profile JSON into separate feature columns"""
        # Extract all unique flavor dimensions
        all_flavors = set()
        for profile in df['flavor_profile'].dropna():
            if isinstance(profile, dict):
                all_flavors.update(profile.keys())
        
        self.flavor_features = list(all_flavors)
        
        # Create columns for each flavor dimension
        for flavor in self.flavor_features:
            df[f'flavor_{flavor}'] = df['flavor_profile'].apply(
                lambda x: float(x.get(flavor, 0)) if isinstance(x, dict) else 0
            )
        
        return df