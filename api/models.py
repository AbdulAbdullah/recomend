from django.db import models

class Bottle(models.Model):
    """Model representing a whisky bottle in the system"""
    bottle_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    style = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    abv = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    flavor_profile = models.JSONField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.bottle_id})"
    
    class Meta:
        indexes = [
            models.Index(fields=['bottle_id']),
            models.Index(fields=['region']),
            models.Index(fields=['style']),
            models.Index(fields=['price']),
        ]


class UserRecommendation(models.Model):
    """Model to store recommendation history"""
    username = models.CharField(max_length=255)
    bottle = models.ForeignKey(Bottle, on_delete=models.CASCADE)
    score = models.FloatField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recommendation for {self.username}: {self.bottle.name}"
    
    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['created_at']),
        ]