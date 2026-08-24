from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0008_chatmessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='marketplace.order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='marketplace.product')),
            ],
        ),
    ]