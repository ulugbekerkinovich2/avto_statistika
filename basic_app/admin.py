from django.contrib import admin
#from django.contrib.admin import AutocompleteFilter

from basic_app import models

# Register your models here.
admin.site.register(models.Upload_File)
admin.site.register(models.Upload_File2)
admin.site.register(models.Upload_File3)
admin.site.register(models.Upload_File4)
admin.site.register(models.Upload_File5)
admin.site.register(models.Upload_File6)


class Model1Admin(admin.ModelAdmin):
    search_fields = ['model_name', 'mark__mark_name']
    list_filter = ['model_name']
    sortable_by = ['file_id']
    list_per_page = 10
    list_display = ['id', 'model_name', 'mark']
    search_fields = ['model_name', 'mark_name']

admin.site.register(models.Model1, Model1Admin)


class MarkAdmin(admin.ModelAdmin):
    #search_fields = ['mark_name']
    list_filter = ['mark_name']
    sortable_by = ['mark_name']
    list_per_page = 10
    list_display = ['id', 'mark_name']
    search_fields = ['models__model_name', 'mark_name']

admin.site.register(models.Mark, MarkAdmin)


class Data21Admin(admin.ModelAdmin):
    search_fields = ['time']
    search_help_text = "Search by time"  # Fix the attribute name
    list_filter = ['file_id', 'mark', 'model__model_name']  # Fix the attribute name for sorting
    list_per_page = 10
    list_display = ['mark', 'model', 'product_count']
    search_fields = ['model_name', 'mark_name']

admin.site.register(models.DATA21, Data21Admin)


class Data22Admin(admin.ModelAdmin):
    search_fields = ['time']
    search_help_text = "Search by time"  # Fix the attribute name
    list_filter = ['file_id', 'mark', 'model']  # Fix the attribute name for sorting
    list_per_page = 20
    list_display = ['cost', 'file_id', 'mark', 'model', 'country', 'count']
    search_fields = ['model_name', 'mark_name']

admin.site.register(models.DATA22, Data22Admin)


class Data19Admin(admin.ModelAdmin):
    search_fields = ['time']
    search_help_text = "Search by time"
    list_filter = ['file_id', 'mark', 'model']
    list_per_page = 20
    list_display = ['cost', 'file_id', 'mark', 'model', 'country', 'count']
    search_fields = ['model_name', 'mark_name']

admin.site.register(models.Data19, Data19Admin)


class Data23Admin(admin.ModelAdmin):
    search_fields = ['time']
    search_help_text = "Search by time"
    list_filter = ['file_id', 'mark', 'model']
    list_per_page = 20
    list_display = ['cost', 'file_id', 'mark', 'model', 'country', 'count']
    search_fields = ['model__model_name', 'mark__mark_name']

admin.site.register(models.Data23, Data23Admin)


class Data20(admin.ModelAdmin):
    search_fields = ['time']
    search_help_text = "Search by time"  # Fix the attribute name
    list_filter = ['file_id', 'mark', 'model', 'mode']  # Fix the attribute name for sorting
    list_per_page = 20
    list_display = ['mark', 'model', 'count', 'mode', 'cost']
    autocomplete_fields = ['mark', 'model']
    search_fields = ['model_name', 'mark_name']
admin.site.register(models.Data20, Data20)


class ManufactureAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_filter = ['model']
    search_fields = ('model__model_name', 'model__mark__mark_name')
    list_display = ['model', "manufactured_year", 'mark', 'count']
    search_fields = ['model', 'mark']
#    autocomplete_fields = ['mark', 'model']
admin.site.register(models.Manufacture, ManufactureAdmin)


class ManufacturedYear(admin.ModelAdmin):
    pass


admin.site.register(models.ManufacturedYear, ManufacturedYear)


class ManufactureedImages(admin.ModelAdmin):
    pass


admin.site.register(models.ManufactureImages, ManufactureedImages)


class Data16Admin(admin.ModelAdmin):
    list_display = ['mark', 'model', 'count', 'country']
    list_filter = ['mark', 'model']
    search_fields = ['mark__mark_name', 'model__model_name']
    list_per_page = 20
   

admin.site.register(models.Data16, Data16Admin)


class ImagesAdmin(admin.ModelAdmin):
    list_display = ['mark_name_for_image', 'image']
    list_per_page = 50
    search_fields = ['mark_name_for_image__mark_name']
    autocomplete_fields = ['mark_name_for_image']


admin.site.register(models.Images, ImagesAdmin)
