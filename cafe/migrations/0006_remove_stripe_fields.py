# Generated migration to remove Stripe-related fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cafe', '0005_update_delivery_fee'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='stripe_payment_id',
        ),
    ]