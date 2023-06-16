from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    discription = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories/', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)
