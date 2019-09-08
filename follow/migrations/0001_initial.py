# Generated by Django 2.2.3 on 2019-09-08 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('target_article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='follow_article', to='articles.Article')),
                ('target_company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='follow_company', to='companies.Company')),
            ],
        ),
    ]
