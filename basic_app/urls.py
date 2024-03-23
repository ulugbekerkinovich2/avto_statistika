from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from basic_app.views2 import MarkSummaryView, MarkSearchView, UploadFile, ModelCountByMonthView2021, \
    ModelCountByMonthView2022, ModelSearchByMonth, DashboardYearsStatisticsView, \
    DashboardByYearly, DashboardTopMarks, ModelCountByMonthView2019, ModelCountByMonthView2023
from .views import ListFile, ListFile2, ListData21, ListData22, ListMark, ListModel1, ListMarks22, ListMarks21, \
    ListMarks16
from .views3 import ListMarks23, ListMarks19

urlpatterns = [
    # path('file_2021/', ListFile.as_view()),  # file yuklash uchun
    # path('file_2022/', ListFile2.as_view()),  # file yuklash uchun
    # path('data21/', ListData21.as_view()),  # filedan kelgan data
    # path('data22/', ListData22.as_view()),  # filedan kelgan data
    # path('data_marks/', ListMark.as_view()),
    # path('data_models/', ListModel1.as_view()),

    # path('statis21_when_get_models_by_id/', ListData21Statistics.as_view()),
    # path('statis22_when_get_models_by_id/', ListData22Statistics.as_view()),

    # path('only_models22/', ListModel22.as_view()),
    # path('only_models21/', ListModel21.as_view()),
    # path('new_statistics21/', DailyModel21CountView.as_view()),
    # path('new_statistics22/', DailyModel22CountView.as_view()),
    # path('statistika19-20/', DailyModel20CountView.as_view())

]

urlpatterns += [
    path('marks/', MarkSummaryView.as_view()),  # TODO  , 2020 yildagi full data
    path('only_marks23/', ListMarks23.as_view()),
    path('only_marks22/', ListMarks22.as_view()),
    path('only_marks21/', ListMarks21.as_view()),
    path('only_marks19/', ListMarks19.as_view()),
    path('only_marks16/', ListMarks16.as_view()),
    path('search/', MarkSearchView.as_view()),  # TODO /?mark_id=Chevrolet by id
    # path('file3/', UploadFile.as_view()),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# TODO next version

urlpatterns += [
    path('model_search2019/', ModelCountByMonthView2019.as_view()),  # TODO /?model_name=Captiva by month 2020
    path('model_search2020/', ModelSearchByMonth.as_view()),  # TODO /?model_name=Captiva by month 2020
    path('model_search2021/', ModelCountByMonthView2021.as_view()),  # TODO /?mark_name=Chevrolet
    path('model_search2022/', ModelCountByMonthView2022.as_view()),  # TODO /?mark_name=Dodge,
    path('model_search2023/', ModelCountByMonthView2023.as_view()),  # TODO /?mark_name=Dodge,

    path('dashboard/', DashboardYearsStatisticsView.as_view()),
    path('yearly/', DashboardByYearly.as_view()),
    path('dashboard/top_marks/', DashboardTopMarks.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
