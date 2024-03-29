# Generated by Django 3.0.7 on 2021-03-14 21:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fqdn', models.CharField(help_text="Virtual mailbox domains, fully qualified.  Ex: 'example.org'.", max_length=256, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MailUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.SlugField(help_text="Virtual mail domain user address or LHS.  Ex: 'johnsmith'.", max_length=96)),
                ('salt', models.CharField(blank=True, help_text='Random password salt.', max_length=96)),
                ('shadigest', models.CharField(blank=True, help_text='Base64 encoding of SHA1 digest:Base64(sha1(password + salt) + salt).', max_length=256)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Domain')),
            ],
            options={
                'unique_together': {('username', 'domain')},
            },
        ),
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(help_text='Fully qualified alias address of destination address.  May be non-local. Ex: john@example.org', max_length=256)),
                ('destination', models.EmailField(help_text='Fully qualified destination mailbox address.  May be non-local. Ex: jeff@example.com.', max_length=256)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('domain', models.ForeignKey(help_text='Domain owning the alias.', on_delete=django.db.models.deletion.CASCADE, to='accounts.Domain')),
            ],
            options={
                'unique_together': {('source', 'destination')},
            },
        ),
    ]
