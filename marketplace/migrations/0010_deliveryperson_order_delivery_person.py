from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0009_orderitem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryPerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=15)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deliveries', to='marketplace.deliveryperson'),
        ),
    ]