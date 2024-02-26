import pandas as pd
import re
from datetime import datetime


def clean_product_name(product_name):
    # Remove unwanted characters from the product name using regular expressions
    return re.sub(r'[\"\'\[\]/,()!?:;«»–]', '', product_name).lower()


# Example usage:
# extract_file_data_2022(r'D:\Downloads\Там._база_2022_г.3_2.xls', 123)  # Replace 123 with the actual file_id value
def extract_file_data_2022(file_name, file_id):
    print('keldi 2022')
    file_id_ = file_id
    from basic_app.models import Model1, Mark, DATA22
    df = pd.read_excel(file_name, sheet_name=0)
    data = df.values
    result = Model1.objects.values('model_name', 'mark__mark_name')
    for item in range(len(data)):
        if item >= 2:
            mode = str(data[item][0]).split(' ')[0]
            date = (str(data[item][1]).split('/'))[1].replace('.', '-')  # 2022-01-01
            product_name_ = data[item][7]
            # product_name = clean_product_name(str(product_name_)).lower()
            product_count = data[item][9]
            if pd.isna(product_count) or product_count == 'nan':
                product_count = 0
            country = data[item][13]
            cost = data[item][11]
            if ' тягач ' in str(product_name_).lower():
                continue
            if 'грузовой' in str(product_name_).lower() or 'фургон' in str(product_name_).lower():
                continue
            try:
                cost = str(cost).split(',')[0]
            except:
                cost = data[item][11]
            if product_count == 0 or cost == 0:
                continue
            if (float(str(cost).replace(' ', '')) / float(product_count)) < 6000:
                continue
            for model_info in result:
                model_name = str(model_info['model_name'])
                mark_name = str(model_info['mark__mark_name'])
                try:
                    if f" {model_name.lower()} " in product_name_.lower() and \
                            (
                                    'car model' in product_name_.lower() or
                                    'aвтомобиль' in product_name_.lower() or
                                    'Автомобиль ' in product_name_ or
                                    'Автомобили' in product_name_ or
                                    'Автомобили легковые' in product_name_ or
                                    ' Автомобиль новый легковой' in product_name_ or
                                    'Автомобили модели' in product_name_ or

                                    'Автомобили модель' in product_name_ or
                                    'Автомобиль  электрический' in product_name_ or
                                    'Автотранспорт' in product_name_ or
                                    'Автотранспорт марки' in product_name_ or
                                    'Автотранспорт туристического класса' in product_name_ or
                                    'Автомобиль марки' in product_name_ or
                                    'Автомобиль бренд' in product_name_ or
                                    'Автомобили бренд' in product_name_ or
                                    'Автомобили марки' in product_name_ or
                                    'Автомобили маркa' in product_name_ or
                                    'Автомобиль маркa' in product_name_ or
                                    'Автомобиль легковой,' in product_name_ or
                                    'Автомобиль новый легковой ' in product_name_ or
                                    'Автомобиль легковой' in product_name_ or
                                    'Автомобиль легковой марки' in product_name_ or
                                    'Автомобиль электрический' in product_name_ or
                                    'автомашина марки' in product_name_ or
                                    'А/м  легковой' in product_name_ or
                                    'А/м легковой' in product_name_ or
                                    'А/м новый легковой марки' in product_name_ or
                                    'А/м туристического класса' in product_name_ or

                                    'Новый легковой автомобилб' in product_name_ or
                                    'Новый легковой автомобиль ' in product_name_ or
                                    'Новый легковой автомобиль' in product_name_ or
                                    'Новый автомобиль с электрическим' in product_name_ or
                                    'Автомобиль с электрическим' in product_name_ or
                                    'Новый автомобиль' in product_name_ or
                                    'Новый электромобиль' in product_name_ or
                                    'Новый автотранспорт' in product_name_ or
                                    'Легковой' in product_name_ or
                                    'Легковой электрический автомобиль ' in product_name_ or
                                    'Легковой электрический автомобиль' in product_name_ or
                                    'Леговой автомобиль' in product_name_ or
                                    'Легковой автомобиль ' in product_name_ or

                                    'Электромобиль,' in product_name_ or
                                    'Электромобиль ' in product_name_ or
                                    'Электромобиль марки ' in product_name_ or
                                    'Электромобиль марки' in product_name_ or
                                    'Электромобиль легковой' in product_name_ or
                                    'Электрмобиль марки ' in product_name_ or
                                    'Электромобиль марки' in product_name_ or
                                    'Электромобиль ' in product_name_ or
                                    'Электромобил' in product_name_ or
                                    'электрический' in product_name_ or
                                    'электроавтомобиль' in product_name_ or
                                    'ELECTRIC CAR/Легковой автомобиль,' in product_name_ or
                                    'Electric car/Электромобиль' in product_name_ or
                                    'Electric' in product_name_ or
                                    'Electric Car' in product_name_ or
                                    'New Electric vehicle' in product_name_ or
                                    'Электрокар' in product_name_ or

                                    'Легковой автомобиль' in product_name_ or
                                    'Легковой автомобиль,' in product_name_ or
                                    'Легковой автомобиль марки' in product_name_ or
                                    'Легковые автомобил,' in product_name_ or
                                    'легковой автомобиль' in product_name_ or
                                    'Легковой электрический' in product_name_ or
                                    'Легковые автомобиль' in product_name_ or
                                    'Легковой электромобиль' in product_name_ or

                                    'А/м легковой' in product_name_ or
                                    'Б/У автомобиль с электрическим' in product_name_ or
                                    'Микроавтобус' in product_name_
                            ):
                        date_obj = datetime.strptime(date, "%d-%m-%Y").date()
                        try:
                            model_instance = Model1.objects.filter(model_name=model_name).first()
                            mark_instance = Mark.objects.filter(mark_name=mark_name).first()
                            if model_instance and mark_instance:
                                # if model_name.lower() == 'malibu':
                                #     print(model_name, '\n', product_name.lower(),
                                #           '\nsoni-->', product_count, '\n')
                                data22_instance = DATA22.objects.create(
                                    time=datetime.now(),
                                    file_id_id=file_id_,
                                    sana=date_obj,
                                    model=model_instance,
                                    mark=mark_instance,
                                    country=country,
                                    count=product_count,
                                    mode=mode,
                                    cost=cost
                                )
                                data22_instance.save()
                                break
                            else:
                                print('Model1 or Mark instance not found.')
                        except Exception as e:
                            print('Error:', str(e))
                            continue
                except:
                    continue
