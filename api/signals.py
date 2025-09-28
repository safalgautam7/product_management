from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from api.models import Product

@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    """
    Invalidate cached product list whenever a Product is created, updated, or deleted.
    """
    pattern = "*product_list*"
    deleted = cache.delete_pattern(pattern)
    print(f"Cleared Product Cache (pattern={pattern}, deleted={deleted})")
