import numpy as np
import pandas as pd
from typing import Dict, List, Any
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler


class WhiskyClusterer:
    """
    Class for clustering whiskies based on their features
    Used for advanced recommendation techniques
    """
    
    def __init__(self, n_clusters: int = 8):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.pca = PCA(n_components=2)
        self.feature_scaler = MinMaxScaler()
        self.is_fitted = False
        
    def fit(self, bottles_df: pd.DataFrame):
        """
        Fit the clustering model to the bottles dataset
        
        Args:
            bottles_df: DataFrame containing bottle features
        """
        # Extract features for clustering
        feature_columns = self._get_feature_columns(bottles_df)
        
        if not feature_columns:
            raise ValueError("No suitable feature columns found for clustering")
        
        # Prepare features for clustering
        features = self._prepare_features(bottles_df, feature_columns)
        
        # Fit the KMeans model
        self.kmeans.fit(features)
        
        # Fit PCA for visualization
        self.pca.fit(features)
        
        self.is_fitted = True
        return self
    
    def predict_cluster(self, bottle: Dict[str, Any]) -> int:
        """
        Predict the cluster for a new bottle
        
        Args:
            bottle: Dictionary containing bottle data
            
        Returns:
            Cluster index
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted yet. Call fit() first.")
            
        bottle_df = pd.DataFrame([bottle])
        feature_columns = self._get_feature_columns(bottle_df)
        features = self._prepare_features(bottle_df, feature_columns)
        
        return self.kmeans.predict(features)[0]
    
    def get_cluster_representatives(self, bottles_df: pd.DataFrame, top_n: int = 5) -> Dict[int, List[str]]:
        """
        Get representative bottles for each cluster
        
        Args:
            bottles_df: DataFrame containing bottle data
            top_n: Number of representatives to return per cluster
            
        Returns:
            Dictionary mapping cluster indices to lists of bottle IDs
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted yet. Call fit() first.")
            
        feature_columns = self._get_feature_columns(bottles_df)
        features = self._prepare_features(bottles_df, feature_columns)
        
        # Get cluster centers
        centers = self.kmeans.cluster_centers_
        
        # Assign clusters to bottles
        bottles_df['cluster'] = self.kmeans.predict(features)
        
        # Find representatives (closest to cluster centers)
        representatives = {}
        
        for i in range(self.n_clusters):
            cluster_bottles = bottles_df[bottles_df['cluster'] == i]
            
            if len(cluster_bottles) == 0:
                representatives[i] = []
                continue
                
            cluster_features = self._prepare_features(cluster_bottles, feature_columns)
            
            # Calculate distances to center
            distances = np.linalg.norm(cluster_features - centers[i], axis=1)
            
            # Get top_n closest bottles
            closest_indices = distances.argsort()[:top_n]
            closest_bottle_ids = cluster_bottles.iloc[closest_indices]['bottle_id'].tolist()
            
            representatives[i] = closest_bottle_ids
            
        return representatives
    
    def _get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """Extract appropriate feature columns for clustering"""
        numerical_features = ['price', 'age', 'abv', 'rating']
        categorical_features = ['region', 'style', 'category']
        
        # Get available numerical features
        available_numerical = [col for col in numerical_features if col in df.columns]
        
        # Get available one-hot encoded categorical features
        available_categorical = []
        for cat in categorical_features:
            cat_columns = [col for col in df.columns if col.startswith(f"{cat}_")]
            available_categorical.extend(cat_columns)
            
        # Get available flavor profile features
        flavor_features = [col for col in df.columns if col.startswith('flavor_')]
        
        return available_numerical + available_categorical + flavor_features
    
    def _prepare_features(self, df: pd.DataFrame, feature_columns: List[str]) -> np.ndarray:
        """Prepare and scale features for clustering"""
        features = df[feature_columns].fillna(0).values
        
        if features.shape[0] > 0:
            if not self.is_fitted:
                self.feature_scaler.fit(features)
            
            features = self.feature_scaler.transform(features)
            
        return features


class CollaborativeFilteringModel:
    """
    Simple collaborative filtering model for whisky recommendations
    Uses user-bottle interaction data for recommendations
    """
    
    def __init__(self):
        self.user_profiles = {}
        self.bottle_vectors = {}
        self.bottle_similarity_matrix = None
        self.bottles_df = None
        
    def fit(self, user_bottle_interactions: List[Dict[str, Any]], bottles_df: pd.DataFrame):
        """
        Fit the collaborative filtering model
        
        Args:
            user_bottle_interactions: List of user-bottle interactions (ratings, additions to bar)
            bottles_df: DataFrame containing bottle information
        """
        self.bottles_df = bottles_df
        
        # Create user profiles (which bottles they have)
        for interaction in user_bottle_interactions:
            username = interaction['username']
            bottle_id = interaction['bottle_id']
            rating = interaction.get('rating', 5.0)  # Default positive rating
            
            if username not in self.user_profiles:
                self.user_profiles[username] = {}
                
            self.user_profiles[username][bottle_id] = rating
        
        # Create bottle feature vectors (for content-based recommendations)
        feature_columns = self._get_feature_columns(bottles_df)
        for _, bottle in bottles_df.iterrows():
            bottle_id = bottle['bottle_id']
            self.bottle_vectors[bottle_id] = bottle[feature_columns].fillna(0).values
            
        # Calculate bottle similarity matrix
        self._calculate_bottle_similarities()
        
        return self
    
    def get_recommendations(self, username: str, count: int = 5) -> List[str]:
        """
        Get bottle recommendations for a user
        
        Args:
            username: Username to get recommendations for
            count: Number of recommendations to return
            
        Returns:
            List of recommended bottle IDs
        """
        if username not in self.user_profiles:
            # New user, return popular bottles
            return self._get_popular_bottles(count)
            
        user_bottles = set(self.user_profiles[username].keys())
        
        # Calculate recommendation scores for each bottle
        recommendations = {}
        
        for bottle_id in self.bottle_vectors:
            if bottle_id in user_bottles:
                continue  # Skip bottles the user already has
                
            # Calculate recommendation score based on similar bottles
            score = 0
            for user_bottle_id in user_bottles:
                if user_bottle_id in self.bottle_vectors:
                    similarity = self._get_bottle_similarity(user_bottle_id, bottle_id)
                    rating = self.user_profiles[username][user_bottle_id]
                    score += similarity * rating
                    
            recommendations[bottle_id] = score
            
        # Sort by score and return top recommendations
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [bottle_id for bottle_id, _ in sorted_recs[:count]]
    
    def _calculate_bottle_similarities(self):
        """Calculate similarity matrix between all bottles"""
        bottle_ids = list(self.bottle_vectors.keys())
        n_bottles = len(bottle_ids)
        
        # Create feature matrix
        feature_matrix = np.zeros((n_bottles, len(next(iter(self.bottle_vectors.values())))))
        for i, bottle_id in enumerate(bottle_ids):
            feature_matrix[i] = self.bottle_vectors[bottle_id]
            
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(feature_matrix)
        
        # Store as dictionary for quick lookup
        self.bottle_similarity_matrix = {}
        for i, bottle_id1 in enumerate(bottle_ids):
            self.bottle_similarity_matrix[bottle_id1] = {}
            for j, bottle_id2 in enumerate(bottle_ids):
                self.bottle_similarity_matrix[bottle_id1][bottle_id2] = similarity_matrix[i, j]
    
    def _get_bottle_similarity(self, bottle_id1: str, bottle_id2: str) -> float:
        """Get similarity between two bottles"""
        if bottle_id1 not in self.bottle_similarity_matrix or bottle_id2 not in self.bottle_similarity_matrix[bottle_id1]:
            # Calculate similarity directly if not in matrix
            if bottle_id1 in self.bottle_vectors and bottle_id2 in self.bottle_vectors:
                vec1 = self.bottle_vectors[bottle_id1].reshape(1, -1)
                vec2 = self.bottle_vectors[bottle_id2].reshape(1, -1)
                return cosine_similarity(vec1, vec2)[0, 0]
            return 0.0
        
        return self.bottle_similarity_matrix[bottle_id1][bottle_id2]
    
    def _get_popular_bottles(self, count: int = 5) -> List[str]:
        """Get popular bottles for new users"""
        if self.bottles_df is None or len(self.bottles_df) == 0:
            return []
            
        # Sort by rating
        if 'rating' in self.bottles_df.columns:
            top_bottles = self.bottles_df.sort_values('rating', ascending=False).head(count)
            return top_bottles['bottle_id'].tolist()
            
        # If no rating, just return first bottles
        return self.bottles_df.head(count)['bottle_id'].tolist()
    
    def _get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """Get feature columns for bottle vectors"""
        numerical_features = ['price', 'age', 'abv', 'rating']
        available_numerical = [col for col in numerical_features if col in df.columns]
        
        # Get flavor profile features
        flavor_features = [col for col in df.columns if col.startswith('flavor_')]
        
        # Get one-hot encoded categorical features
        categorical_features = []
        for prefix in ['region_', 'style_', 'country_', 'category_']:
            categorical_features.extend([col for col in df.columns if col.startswith(prefix)])
            
        return available_numerical + flavor_features + categorical_features