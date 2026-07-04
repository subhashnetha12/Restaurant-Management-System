from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app2', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kot',
            name='status',
            field=models.CharField(
                choices=[
                    ('Pending', 'Pending'),
                    ('Preparing', 'Preparing'),
                    ('Ready', 'Ready'),
                    ('Served', 'Served'),
                    ('Cancelled', 'Cancelled'),
                ],
                default='Pending',
                max_length=50,
            ),
        ),
    ]
