from django.db import migrations, models
from django.core.validators import RegexValidator


def populate_cnpj(apps, schema_editor):
    Loja = apps.get_model('loja_app', 'Loja')
    for index, loja in enumerate(Loja.objects.all(), start=1):
        if not loja.cnpj_loja:
            loja.cnpj_loja = f"00.000.000/0000-{index:02d}"
            loja.save(update_fields=['cnpj_loja'])


def unpopulate_cnpj(apps, schema_editor):
    Loja = apps.get_model('loja_app', 'Loja')
    Loja.objects.update(cnpj_loja=None)


class Migration(migrations.Migration):

    dependencies = [
        ('loja_app', '0008_venda_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='loja',
            name='cnpj_loja',
            field=models.CharField(
                max_length=18,
                null=True,
                unique=True,
                validators=[
                    RegexValidator(
                        message='Informe um CNPJ válido no formato 00.000.000/0000-00.',
                        regex='^\\d{2}\\.\\d{3}\\.\\d{3}/\\d{4}-\\d{2}$'
                    )
                ],
                verbose_name='CNPJ da Loja',
            ),
        ),
        migrations.RunPython(populate_cnpj, reverse_code=unpopulate_cnpj),
        migrations.AlterField(
            model_name='loja',
            name='cnpj_loja',
            field=models.CharField(
                max_length=18,
                unique=True,
                validators=[
                    RegexValidator(
                        message='Informe um CNPJ válido no formato 00.000.000/0000-00.',
                        regex='^\\d{2}\\.\\d{3}\\.\\d{3}/\\d{4}-\\d{2}$'
                    )
                ],
                verbose_name='CNPJ da Loja',
            ),
        ),
    ]
