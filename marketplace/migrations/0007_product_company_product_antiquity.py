from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_order_razorpay_order_id_order_razorpay_payment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='company',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AddField(
            model_name='product',
            name='antiquity',
            field=models.PositiveIntegerField(default=0, help_text='Age of the item in years'),
        ),
    ]