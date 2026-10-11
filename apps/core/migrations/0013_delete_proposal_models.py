from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_delete_aboutfaq_delete_aboutmission_delete_aboutpre_and_more'),
    ]

    operations = [
        migrations.DeleteModel(name='ProposalStat'),
        migrations.DeleteModel(name='ProposalProblem'),
        migrations.DeleteModel(name='ProposalService'),
        migrations.DeleteModel(name='Proposal'),
    ]
