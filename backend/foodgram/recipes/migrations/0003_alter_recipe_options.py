# Generated by Django 4.1 on 2022-09-07 06:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_remove_recipe_is_favorited_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('name',)},
        ),
    ]
