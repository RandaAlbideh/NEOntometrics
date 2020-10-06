# Generated by Django 3.1.1 on 2020-09-22 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0007_auto_20200922_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metrics',
            name='Absolutebreadth',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Absolutedepth',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Absoluteleafcardinality',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Absoluterootcardinality',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Absolutesiblingcardinality',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Annotationassertionaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Annotationaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Annotationpropertydomainaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Annotationpropertyrangeaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Asymmetricobjectpropertyaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Attributeclassratio',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Attributerichness',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Averagebreadth',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Averagedepth',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Averagenumberofpaths',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Averagepopulation',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Axiomclassratio',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Axioms',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Classassertionaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Classcount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Classrelationratio',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Classrichness',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='DataPropertyrangeaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Datapropertyassertionaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Datapropertycount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Datapropertydomainaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Differentindividualsaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Disjointclassesaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Disjointdatapropertiesaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Disjointobjectpropertiesaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Equivalenceratio',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Equivalentclassesaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Equivalentdatapropertiesaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Equivalentobjectpropertiesaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Functionaldatapropertyaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Functionalobjectpropertiesaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='GCICount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='HiddenGCICount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Individualcount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Inheritancerichness',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Inverseobjectpropertiesaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Inverserelationsratio',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Irreflexiveobjectpropertyaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Logicalaxiomscount',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Maximalbreadth',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Maximaldepth',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Negativedatapropertyassertionaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Objectpropertyassertionaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Objectpropertycount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Objectpropertydomainaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Propertiescount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Ratioofleaffanoutness',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Ratioofsiblingfanoutness',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Reflexiveobjectpropertyaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Relationshiprichness',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Sameindividualsaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='SubClassOfaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='SubDataPropertyOfaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='SubObjectPropertyOfaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='SubPropertyChainOfaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Symmetricobjectpropertyaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Tangledness',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Totalclassescount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Totaldatapropertiescount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Totalindividualscount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Totalnumberofpaths',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Totalobjectpropertiescount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='Transitiveobjectpropertyaxiomscount',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
