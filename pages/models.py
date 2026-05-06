# models.py
from django.db import models
from django.core.exceptions import ValidationError

class HomePage(models.Model):
    main_title = models.CharField(max_length=200, verbose_name='عنوان اصلی')
    second_title = models.CharField(max_length=200, verbose_name='عنوان دوم')
    text = models.TextField(verbose_name='متن معرفی')

    class Meta:
        verbose_name = 'محتوای صفحه اصلی'
        verbose_name_plural = 'محتوای صفحه اصلی'

    def save(self, *args, **kwargs):
        if not self.pk and HomePage.objects.exists():
            raise ValidationError('فقط یک رکورد مجاز است')
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.main_title
