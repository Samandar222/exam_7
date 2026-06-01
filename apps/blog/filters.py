import django_filters
from .models import Post


class PostFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category__id')
    category_name = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains'
    )
    created_at = django_filters.DateFilter(field_name='created_at__date')
    created_after = django_filters.DateFilter(
        field_name='created_at__date',
        lookup_expr='gte'
    )
    created_before = django_filters.DateFilter(
        field_name='created_at__date',
        lookup_expr='lte'
    )
    author = django_filters.CharFilter(
        field_name='author__username',
        lookup_expr='icontains'
    )

    class Meta:
        model = Post
        fields = ['category', 'category_name', 'author']
