import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings

from .analyzer import CollectionAnalyzer
from .feature_processor import FeatureProcessor
from data_integration.baxus_api import BaxusAPI
from data_integration.data_processor import DataProcessor


class WhiskyRecommender:
    """Core recommendation engine for Bob"""
    
    def __init__(self):
        self.analyzer = CollectionAnalyzer()
        self.feature_processor = FeatureProcessor()
        self.baxus_api = BaxusAPI()
        self.data_processor = DataProcessor()
        
        # Load the bottle dataset
        self.bottles_df = self._load_bottle_data()
    
    def _load_bottle_data(self) -> pd.DataFrame:
        """Load and preprocess the bottle dataset"""
        bottle_path = settings.BOTTLE_DATA_PATH
        
        if not os.path.exists(bottle_path):
            raise FileNotFoundError(f"Bottle data file not found at {bottle_path}")
        
        with open(bottle_path, 'r') as f:
            bottles = json.load(f)
        
        return pd.DataFrame(bottles)
    
    def get_recommendations(
        self, 
        username: str, 
        count: int = 5, 
        include_reasoning: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized bottle recommendations for a user
        
        Args:
            username: BAXUS username
            count: Number of recommendations to return
            include_reasoning: Whether to include reasoning for recommendations
            
        Returns:
            List of recommended bottles with reasoning
        """
        # Get user's bar data
        user_bar = self.baxus_api.get_user_bar(username)
        user_bottles = user_bar.get('bottles', [])
        
        if not user_bottles:
            return self._get_default_recommendations(username, count, include_reasoning)
        
        # Get user's wishlist
        wishlist_bottles = user_bar.get('wishlist', [])
        wishlist_ids = [b['bottle_id'] for b in wishlist_bottles]
        
        # Process user's collection to extract preferences
        user_preferences = self.analyzer.analyze_collection(user_bottles)
        
        # Get user's bottle IDs to exclude from recommendations
        user_bottle_ids = [b['bottle_id'] for b in user_bottles]
        
        # Get candidate bottles (exclude user's bottles and wishlist)
        candidate_bottles = self.bottles_df[
            ~self.bottles_df['bottle_id'].isin(user_bottle_ids + wishlist_ids)
        ]
        
        if len(candidate_bottles) == 0:
            return self._get_default_recommendations(username, count, include_reasoning)
        
        # Process features for similarity calculation
        user_features_df = self.feature_processor.process_bottles(user_bottles)
        candidate_features_df = self.feature_processor.process_bottles(candidate_bottles.to_dict('records'))
        
        # Calculate similarity scores
        recommendations = self._calculate_recommendations(
            user_features_df, candidate_features_df, user_preferences, count
        )
        
        # Add reasoning if requested
        if include_reasoning:
            recommendations = self._add_recommendation_reasoning(
                recommendations, user_preferences
            )
        
        return recommendations
    
    def _calculate_recommendations(
        self,
        user_features_df: pd.DataFrame,
        candidate_features_df: pd.DataFrame,
        user_preferences: Dict[str, Any],
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Calculate similarity scores and select top recommendations"""
        # Feature columns to use for similarity calculation (exclude bottle_id)
        feature_columns = [col for col in user_features_df.columns if col != 'bottle_id']
        
        # Calculate average user feature vector
        user_vector = user_features_df[feature_columns].mean(axis=0).values.reshape(1, -1)
        
        # Ensure candidate features have the same columns
        candidate_features = candidate_features_df[
            [col for col in feature_columns if col in candidate_features_df.columns]
        ].values
        
        # Fill in missing columns with zeros
        if candidate_features.shape[1] < len(feature_columns):
            padding = np.zeros((candidate_features.shape[0], 
                               len(feature_columns) - candidate_features.shape[1]))
            candidate_features = np.hstack((candidate_features, padding))
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(user_vector, candidate_features).flatten()
        
        # Apply price range filtering
        # Apply price range filtering
        price_range = user_preferences['price_range']
        price_factor = 1.0
        if price_range['avg'] > 0:
            price_min = max(0, price_range['avg'] * 0.7)  # 30% below average
            price_max = price_range['avg'] * 1.5  # 50% above average
            
            # Apply price factor to similarity scores
            prices = candidate_features_df['price'].values if 'price' in candidate_features_df.columns else np.ones(len(candidate_features_df))
            for i, price in enumerate(prices):
                if price < price_min or price > price_max:
                    # Reduce similarity score for bottles outside price range
                    similarity_scores[i] *= 0.7  # 30% penalty
        
        # Get top recommendations
        top_indices = similarity_scores.argsort()[-count*2:][::-1]  # Get more than needed for diversity
        
        # Get bottle data for top recommendations
        recommendations = []
        candidate_bottle_ids = candidate_features_df['bottle_id'].values
        
        for i, idx in enumerate(top_indices):
            if i >= count:
                break
                
            bottle_id = candidate_bottle_ids[idx]
            bottle = self.bottles_df[self.bottles_df['bottle_id'] == bottle_id].iloc[0].to_dict()
            
            recommendations.append({
                'bottle_id': bottle_id,
                'name': bottle['name'],
                'brand': bottle.get('brand', ''),
                'region': bottle.get('region', ''),
                'style': bottle.get('style', ''),
                'price': float(bottle.get('price', 0)),
                'age': int(bottle.get('age', 0)) if bottle.get('age') else None,
                'score': float(similarity_scores[idx]),
                'abv': float(bottle.get('abv', 0)) if bottle.get('abv') else None,
                'flavor_profile': bottle.get('flavor_profile', {}),
                'description': bottle.get('description', '')
            })
        
        return recommendations
    
    def _add_recommendation_reasoning(
        self,
        recommendations: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Add reasoning for each recommendation based on user preferences"""
        for rec in recommendations:
            reasons = []
            
            # Match on region
            if rec['region'] and user_preferences['regions'].get(rec['region'], 0) > 0.1:
                reasons.append(f"Matches your preference for {rec['region']} whiskies")
            
            # Match on style
            if rec['style'] and user_preferences['styles'].get(rec['style'], 0) > 0.1:
                reasons.append(f"Aligns with your interest in {rec['style']} whiskies")
            
            # Match on price point
            price_range = user_preferences['price_range']
            if price_range['avg'] > 0 and rec['price'] > 0:
                price_ratio = rec['price'] / price_range['avg']
                if 0.8 <= price_ratio <= 1.2:
                    reasons.append("Similar price point to your collection")
                elif price_ratio < 0.8:
                    reasons.append("Great value compared to your collection")
                elif price_ratio <= 1.5:
                    reasons.append("Premium option within your price range")
            
            # Match on age
            age_pref = user_preferences['age_preference']
            if age_pref['avg'] > 0 and rec['age']:
                if abs(rec['age'] - age_pref['avg']) <= 3:
                    reasons.append(f"Age statement ({rec['age']} years) similar to your collection")
                elif rec['age'] > age_pref['avg'] + 3:
                    reasons.append(f"More mature expression ({rec['age']} years) than your average")
            
            # Match on flavor profile
            flavor_matches = []
            user_flavors = user_preferences['flavor_profile']
            bottle_flavors = rec['flavor_profile'] or {}
            
            for flavor, user_score in user_flavors.items():
                if user_score > 0.1 and flavor in bottle_flavors and bottle_flavors[flavor] > 0.5:
                    flavor_matches.append(flavor)
            
            if flavor_matches:
                if len(flavor_matches) == 1:
                    reasons.append(f"Matches your preference for {flavor_matches[0]} notes")
                else:
                    flavors_text = ", ".join(flavor_matches[:-1]) + " and " + flavor_matches[-1]
                    reasons.append(f"Shares flavor notes you enjoy: {flavors_text}")
            
            # If no specific reasons found, provide generic reasoning
            if not reasons:
                reasons.append("Complements your current collection")
                
                # Check for diversification
                if rec['region'] and not user_preferences['regions'].get(rec['region'], 0) > 0:
                    reasons.append(f"Diversifies your collection with a {rec['region']} whisky")
                    
                if rec['style'] and not user_preferences['styles'].get(rec['style'], 0) > 0:
                    reasons.append(f"Adds variety with a {rec['style']} style")
            
            reason_text = ". ".join(reasons)
            rec['reason'] = reason_text
            
        return recommendations
    
    def _get_default_recommendations(
        self, 
        username: str, 
        count: int = 5,
        include_reasoning: bool = True
    ) -> List[Dict[str, Any]]:
        """Provide default recommendations for new users with no collection"""
        # Select highly-rated, popular bottles across different regions and styles
        top_bottles = self.bottles_df.sort_values('rating', ascending=False).head(count*3)
        
        # Ensure diversity in recommendations
        regions = set()
        styles = set()
        recommendations = []
        
        for _, bottle in top_bottles.iterrows():
            if len(recommendations) >= count:
                break
                
            # Skip if we already have a bottle from this region and style
            region = bottle.get('region', '')
            style = bottle.get('style', '')
            
            if (region in regions and style in styles) and len(recommendations) > count/2:
                continue
                
            regions.add(region)
            styles.add(style)
            
            bottle_dict = bottle.to_dict()
            
            recommendations.append({
                'bottle_id': bottle_dict['bottle_id'],
                'name': bottle_dict['name'],
                'brand': bottle_dict.get('brand', ''),
                'region': bottle_dict.get('region', ''),
                'style': bottle_dict.get('style', ''),
                'price': float(bottle_dict.get('price', 0)),
                'age': int(bottle_dict.get('age', 0)) if bottle_dict.get('age') else None,
                'score': 0.95,  # High default score for top bottles
                'abv': float(bottle_dict.get('abv', 0)) if bottle_dict.get('abv') else None,
                'flavor_profile': bottle_dict.get('flavor_profile', {}),
                'description': bottle_dict.get('description', '')
            })
        
        # Add generic reasoning for new users
        if include_reasoning:
            for i, rec in enumerate(recommendations):
                if i == 0:
                    rec['reason'] = f"A highly-rated {rec['region']} whisky perfect for starting your collection"
                elif i == 1:
                    rec['reason'] = f"An excellent {rec['style']} style that's widely appreciated by whisky enthusiasts"
                elif i == 2:
                    rec['reason'] = f"A versatile {rec['region']} whisky that showcases classic characteristics"
                else:
                    rec['reason'] = f"A distinguished bottle that represents the best of {rec['region']} whisky"
        
        return recommendations