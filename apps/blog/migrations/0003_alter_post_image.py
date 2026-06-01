from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_post_options_alter_category_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name='comments',
                to='blog.post'
            ),
        ),
        migrations.AlterField(
            model_name='like',
            name='post',
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name='likes',
                to='blog.post'
            ),
        ),
    ]
