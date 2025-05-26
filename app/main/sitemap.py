from django.contrib.sitemaps import Sitemap
from .models import Review
from django.urls import reverse

class ReviewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Review.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1.0

    def items(self):
        return ['home', 'all_reviews']

    def location(self, item):
        return reverse(item)