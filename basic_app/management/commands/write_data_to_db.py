import json
import os
import django
from datetime import datetime
from django.core.files import File
from django.core.management.base import BaseCommand
from basic_app.models import Mark, Model1, Data19, Data20, DATA21, DATA22, Data23, Upload_File5, Upload_File4, Upload_File6
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')  # Adjust 'avto.settings' to your project's settings
django.setup()
# # Function to insert data from JSON to the database
# class Command(BaseCommand):
#     def handle():
#         # Open and load the JSON file
#         with open('/Users/jurakulovamadinabonu/Library/CloudStorage/OneDrive-Personal/Documents/python_projects/ulov/avto_statistika/utils/result.json', 'r', encoding='utf-8') as file:
#             data = json.load(file)
        
#         for item in data:
#             mark_name = item['mark_name']
#             year = item['year']
#             date = datetime.strptime(item['date'], '%Y-%m-%d').date()
#             model_name = item['model_name']
#             cost_of_model = item['cost_of_model']
#             count_of_model = item['count_of_model']
            
#             # Ensure Mark uniqueness
#             mark, created = Mark.objects.get_or_create(mark_name=mark_name)
            
#             # Ensure Model1 uniqueness within the scope of a Mark
#             model, created = Model1.objects.get_or_create(model_name=model_name, mark=mark)
            
#             # Create or update instances for each year
#             if year == 2019:
#                 Data19.objects.create(
#                     sana=date,
#                     model=model,
#                     mark=mark,
#                     count=count_of_model,
#                     cost=cost_of_model
#                     # Add additional fields as necessary
#                 )
#             elif year == 2020:
#                 Data20.objects.create(
#                     sana=date,
#                     model=model,
#                     mark=mark,
#                     count=count_of_model,
#                     cost=cost_of_model
#                     # Add additional fields as necessary
#                 )
#             elif year == 2021:
#                 DATA21.objects.create(
#                     sana=date,
#                     model=model,
#                     mark=mark,
#                     product_count=count_of_model,
#                     cost=cost_of_model
#                 )
#             elif year == 2022:
#                 DATA22.objects.create(
#                     sana=date,
#                     model=model,
#                     mark=mark,
#                     count=count_of_model,
#                     cost=cost_of_model
#                 )
#             elif year == 2023:
#                 Data23.objects.create(
#                     sana=date,
#                     model=model,
#                     mark=mark,
#                     count=count_of_model,
#                     cost=cost_of_model
#                 )

# # Call the function to start inserting data
# # insert_data_from_json()
class Command(BaseCommand):
    help = 'Inserts data from JSON file into the database.'

    def handle(self, *args, **options):
        file_path = '/var/www/workers/avto/avto_statistika/utils/new_structure_result1.json'

        # Open and load the JSON file
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            data = json.load(file)
        
        for item in data:
            mark_name = item['mark_name']
            year = item['year']
            # date = datetime.strptime(item['date'], '%Y-%m-%d').date()
            # date = None
            model_name = item['model_name']
            cost_of_model = item['cost_of_model']
            count_of_model = item['count_of_model']
            
            # Ensure Mark uniqueness
            mark, created = Mark.objects.get_or_create(mark_name=mark_name)
            
            # Ensure Model1 uniqueness within the scope of a Mark
            model, created = Model1.objects.get_or_create(model_name=model_name, mark=mark)
            
            # Based on the year, create the corresponding data model instance
            if year == 2019:
                Data19.objects.create(model=model, mark=mark, count=count_of_model, cost=cost_of_model)
            elif year == 2020:
                Data20.objects.create(model=model, mark=mark, count=count_of_model, cost=cost_of_model)
            elif year == 2021:
                DATA21.objects.create(model=model, mark=mark, product_count=count_of_model, cost=cost_of_model)
            elif year == 2022:
                DATA22.objects.create(model=model, mark=mark, count=count_of_model, cost=cost_of_model)
            elif year == 2023:
                Data23.objects.create(model=model, mark=mark, count=count_of_model, cost=cost_of_model)

        self.stdout.write(self.style.SUCCESS('Successfully inserted data from JSON.'))
