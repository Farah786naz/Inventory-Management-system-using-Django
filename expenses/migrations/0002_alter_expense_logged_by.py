from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='logged_by',
            field=models.ForeignKey(blank=True, db_column='logged_by', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses_logged', to='users.user'),
        ),
    ]