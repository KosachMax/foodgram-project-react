# Generated by Django 4.2.6 on 2023-10-10 20:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_ingredientinrecipe_amount_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientinrecipe',
            options={'ordering': ('-id',), 'verbose_name': 'Ингредиент для рецепта', 'verbose_name_plural': 'Ингредиенты для рецептов'},
        ),
    ]
