from django.conf.urls import url,include
from cdn import views
from django.views.static import serve
from django.conf import settings

urlpatterns = [

    #url(r'^test/', views.test),
    #url(r'^show$',views.show,name='show'),
    url(r'^login/',views.acc_login ),
    url(r'^logout/',views.acc_logout,name="logout" ),
	url(r'^home$',views.home,name='home'),
    #显示所有数据
    url(r'^index$',views.query,name='query'),
    #根据条件查询数据
    url(r'^search$',views.search,name='search'),
    #添加数据
    url(r'^add$',views.add,name='add'),
    #删除数据根据id
    url(r'delete$',views.delByID,name='delByID'),
    #批量删除所选数据
    url(r'^delSelect$',views.delSelect,name='delSelect'),
    #更新数据，根据id
    url(r'update$',views.update,name='update'),
    url(r'exportall$',views.exportall,name='export_all_excel'),
    #url(r'download$',views.download,name='download'),
   url(r'download/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT})


]