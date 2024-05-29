import requests
def calculate_percentage():
    urls = [
        {"year": 2019, "url": "https://dev.misterdev.uz/only_marks19/"},
        {"year": 2020, "url": "https://dev.misterdev.uz/marks/"},
        {"year": 2021, "url": "https://dev.misterdev.uz/only_marks21/"},
        {"year": 2022, "url": "https://dev.misterdev.uz/only_marks22/"},
        {"year": 2023, "url": "https://dev.misterdev.uz/only_marks23/"}
    ]

    data = []

    # Ma'lumotlarni yuklab olish
    for item in urls:
        response = requests.get(item["url"])
        if response.status_code == 200:
            json_data = response.json()
            # Bo'shliqlarni olib tashlash uchun .replace() metodidan foydalanamiz
            models = int(str(json_data['all_count_of_models']).replace(" ", "").replace('.', ''))
            vehicles = int(str(json_data['all_count_of_vehicles']).replace(" ", "").replace('.', ''))
            # Agar son o'nlik son bo'lsa va verguldan foydalanilsa, avval vergulni nuqtaga o'zgartiramiz, keyin float() orqali o'qiymiz
            costs = float(str(json_data['all_sum_of_costs_vehicle']).replace(" ", "").replace(",", ".").replace('.', ''))
            
            data.append({
                'year': item["year"],
                'models': models,
                'vehicles': vehicles,
                'costs': costs
            })

    # Foizdagi o'zgarishlarni hisoblash va yangi massivga saqlash
    percentage_changes = []

    for i in range(1, len(data)):
        prev_year_data = data[i-1]
        current_year_data = data[i]
        
        model_change = ((current_year_data['models'] - prev_year_data['models']) / prev_year_data['models']) * 100 if prev_year_data['models'] else 0
        vehicle_change = ((current_year_data['vehicles'] - prev_year_data['vehicles']) / prev_year_data['vehicles']) * 100 if prev_year_data['vehicles'] else 0
        cost_change = ((current_year_data['costs'] - prev_year_data['costs']) / prev_year_data['costs']) * 100 if prev_year_data['costs'] else 0
        
        percentage_changes.append({
            'year_range': f"{current_year_data['year']}",
            'model_change_percent': round(model_change, 2),
            'vehicle_change_percent': round(vehicle_change, 2),
            'cost_change_percent': round(cost_change, 2)
        })
    return percentage_changes
    # Natijalarni ko'rish
    # for change in percentage_changes:
    #     print(change)
print(calculate_percentage())