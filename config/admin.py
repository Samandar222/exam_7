from django.contrib import admin

from exam_7.apps.blog.models import Post

admin.site.site_header = "Blog API Admin"
admin.site.site_title = "Blog API"
admin.site.index_title = "Welcome Admin"
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title',)
    list_filter = ('created_at',)