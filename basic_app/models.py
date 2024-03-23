from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

from utils.extract_data2 import extract_file_data_2022
from utils.extract_data2016 import extract_file_data_2016
from utils.extract_data_2019 import extract_file_data_2019
from utils.extract_data_2020 import extract_file_data_2020
from utils.extract_data_2023 import extract_file_data_2023
from utils.extract_file_data_2021 import extract_file_data_2021


# Create your models here.
class Upload_File(models.Model):
    file = models.FileField(upload_to='files/')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'upload_file2021'
        verbose_name_plural = 'upload_file2021'


@receiver(post_save, sender=Upload_File)
def upload_file2_post_save(sender, instance, created, **kwargs):
    if created and instance.file:
        extract_file_data_2021(file_name=instance.file.path, file_id=instance.id)
        return {'status': 'ok'}


class Upload_File2(models.Model):
    file = models.FileField(upload_to='files2/')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'upload_file22'
        verbose_name_plural = 'upload_file2022'


@receiver(post_save, sender=Upload_File2)
def upload_file2_post_save(sender, instance, created, **kwargs):
    if created and instance.file:
        print(instance.file.path)
        extract_file_data_2022(file_name=instance.file.path, file_id=instance.id)
        return {'status': 'ok'}


class Mark(models.Model):
    mark_name = models.CharField(max_length=100)

    def __str__(self):
        return self.mark_name

    class Meta:
        db_table = 'mark'
        verbose_name_plural = 'marks'


class Model1(models.Model):
    model_name = models.CharField(max_length=100)
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE, related_name='models')

    def __str__(self):
        return f"{self.model_name}  {self.mark}  {self.id}"

    class Meta:
        db_table = 'model1'
        verbose_name_plural = 'models'


class DATA21(models.Model):
    time = models.DateTimeField(auto_created=True, default=datetime.datetime.now, verbose_name='data yaratilgan vaqti')
    file_id = models.ForeignKey(Upload_File, on_delete=models.CASCADE, null=True, blank=True)
    sana = models.DateField(null=True, blank=True)
    model = models.ForeignKey(Model1, on_delete=models.CASCADE, related_name='data21')
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE)
    product_count = models.PositiveIntegerField(default=0)
    mode = models.CharField(max_length=20, null=True)
    cost = models.FloatField(default=0)

    def __str__(self):
        return f"2021 - {self.mark}, {self.model}, {self.product_count}, {self.cost} file_id: {self.file_id}"

    class Meta:
        db_table = 'data2021'
        verbose_name_plural = 'data2021'


class DATA22(models.Model):
    time = models.DateTimeField(auto_created=True, verbose_name='data yaratilgan vaqti', null=True, blank=True)
    file_id = models.ForeignKey(Upload_File2, on_delete=models.CASCADE, null=True, blank=True)
    sana = models.DateField(null=True, blank=True)
    model = models.ForeignKey(Model1, on_delete=models.CASCADE, related_name='data22')
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=0)
    mode = models.CharField(max_length=20, null=True)
    cost = models.FloatField(default=0)

    def __str__(self):
        return f"2022 - {self.mark.mark_name}, {self.model.model_name}, {self.count}, {self.cost}"

    class Meta:
        db_table = 'data2022'
        verbose_name_plural = 'data2022'


class Upload_File3(models.Model):
    file = models.FileField(upload_to='files3/')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'upload_file2020'
        verbose_name_plural = 'upload_file2020'


@receiver(post_save, sender=Upload_File3)
def upload_file3_post_save(sender, instance, created, **kwargs):
    if created and instance.file:
        extract_file_data_2020(file_name=instance.file.path, file_id=instance.id)
        return {'status': 'ok'}


class Data20(models.Model):
    time = models.DateField(auto_created=True, default=datetime.date.today, verbose_name='data yaratilgan vaqt')
    file_id = models.ForeignKey(Upload_File3, on_delete=models.CASCADE, null=True, blank=True)
    sana = models.DateField(null=True, blank=True)
    model = models.ForeignKey(Model1, on_delete=models.CASCADE, related_name='data20')
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE)
    country = models.CharField(max_length=255)
    count = models.PositiveIntegerField(default=0)
    mode = models.CharField(max_length=20, null=True)
    cost = models.FloatField(default=0)

    def __str__(self):
        return f"2020 - {self.model}, {self.count}, {self.cost}"

    class Meta:
        db_table = 'data2020'
        verbose_name_plural = 'data2020'


class Upload_File4(models.Model):
    file = models.FileField(upload_to='files4/')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'upload_file_2016'
        verbose_name_plural = 'upload_file_2016'


@receiver(post_save, sender=Upload_File4)
def upload_file4_post_save(sender, instance, created, **kwargs):
    if created and instance.file:
        extract_file_data_2016(file_name=instance.file.path, file_id=instance.id)

        return {'status': 'ok'}


class Upload_File5(models.Model):
    file = models.FileField(upload_to='files5/')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'upload_file2019'
        verbose_name_plural = 'upload_file2019'


@receiver(post_save, sender=Upload_File5)
def upload_file5_post_save(sender, instance, created, **kwargs):
    if created and instance.file:
        extract_file_data_2019(file_name=instance.file.path, file_id=instance.id)
        return {'status': 'ok'}


class Data19(models.Model):
    mode = models.CharField(max_length=20, null=True)
    time = models.DateField(auto_created=True, default=datetime.date.today, verbose_name='yaratilgan vaqt')
    file_id = models.ForeignKey(Upload_File5, on_delete=models.CASCADE, null=True, blank=True)
    sana = models.DateField(null=True, blank=True)
    model = models.ForeignKey(Model1, on_delete=models.CASCADE, related_name='data19')
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE)
    country = models.CharField(max_length=255, null=True)
    count = models.PositiveIntegerField(default=0)
    cost = models.FloatField(default=0)

    def __str__(self):
        return f"2019 - {self.model}, {self.count}, {self.cost}"

    class Meta:
        db_table = "data2019"
        verbose_name_plural = 'data2019'


class Data16(models.Model):
    time = models.DateField(auto_created=True, default=datetime.date.today, verbose_name='data yaratilgan vaqt')
    file_id = models.ForeignKey(Upload_File4, on_delete=models.CASCADE)
    sana = models.DateField(default=datetime.date.today,  null=False)
    model = models.ForeignKey(Model1, on_delete=models.CASCADE)
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE)
    country = models.CharField(max_length=255)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"2016-2017 - {self.model}, {self.count}"

    class Meta:
        db_table = 'data2016'
        verbose_name_plural = 'data2016'


class Upload_File6(models.Model):
    file = models.FileField(upload_to='files6/')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'upload_file2023'
        verbose_name_plural = 'upload_file2023'


@receiver(post_save, sender=Upload_File6)
def upload_file6_post_save(sender, instance, created, **kwargs):
    if created and instance.file:
        extract_file_data_2023(file_name=instance.file.path, file_id=instance.id)
        return {'status': 'ok'}


class Data23(models.Model):
    mode = models.CharField(max_length=20, null=True)
    time = models.DateField(auto_created=True, default=datetime.date.today, verbose_name='yaratilgan vaqt')
    file_id = models.ForeignKey(Upload_File6, on_delete=models.CASCADE, null=True, blank=True)
    sana = models.DateField(null=True, blank=True)
    model = models.ForeignKey(Model1, on_delete=models.CASCADE, related_name='data23')
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE)
    country = models.CharField(max_length=255, null=True)
    count = models.PositiveIntegerField(default=0)
    cost = models.FloatField(default=0)

    def __str__(self):
        return f"2023 - {self.model}, {self.count}, {self.cost}"

    class Meta:
        db_table = "data2023"
        verbose_name_plural = 'data2023'


class ManufacturedYear(models.Model):
    year = models.CharField(max_length=4)

    def __str__(self):
        return self.year

    class Meta:
        db_table = 'manufactured_year'
        verbose_name_plural = 'manufactured_year'


class ManufactureImages(models.Model):
    manufacture_image = models.ImageField(upload_to='manufacture_images/')

    def get_image_url(self):
        return self.manufacture_image.url

    def __str__(self):
        return self.manufacture_image.name

    class Meta:
        db_table = 'manufacture_images'


class Manufacture(models.Model):
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE)
    model = models.ForeignKey(Model1, on_delete=models.CASCADE)
    manufactured_year = models.ForeignKey(ManufacturedYear, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    image = models.ForeignKey(ManufactureImages, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.mark}, {self.model}, {self.manufactured_year}, {self.count}"

    class Meta:
        db_table = 'manufacture'
        verbose_name_plural = 'manufacture'

class Images(models.Model):
    image = models.ImageField(upload_to='images/')
    mark_name_for_image = models.ForeignKey(Mark, on_delete=models.CASCADE, null=True)

    def get_image_url(self):
        return self.image.url

    def __str__(self):
        return self.image.name

    class Meta:
        db_table = 'images'
        verbose_name_plural = 'images'
