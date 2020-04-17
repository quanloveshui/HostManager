from django.shortcuts import render,redirect

# Create your views here.
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.template.context import RequestContext
# 添加Django自带的分页插件 paginator
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import  login_required

#包装csrf请求，避免django认为其实跨站攻击脚本
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import random

from .models import Student,Nodeinfo



# Bootstrap 测试
# def test(request):
#     return render(request, 'index.html')







# 查询所有，并分页显示
@login_required
def query(request):
    field_obj = Nodeinfo._meta.fields #获取字段对象
    field_list = [field_obj[i].name for i in range(len(field_obj))]  # 所有字段名组成列表
    field_list = field_list[1:]
    filed_name = [field_obj[i].verbose_name for i in range(len(field_obj))]  # 所有字段中文名组成列表  ['ID', '主机名', 'IP地址', '省份', '城市', '运营商', '代理商', 'VIP地址']
    filed_name = filed_name[1:]#去除第一个ID
    dic = dict(zip(field_list,filed_name))
    limit = 3  # 每页显示的记录数
    querysets_data = Nodeinfo.objects.all()
    paginator = Paginator(querysets_data, limit)  # 实例化一个分页对象
    page = request.GET.get('page')  # 获取页码
    try:
        querysets_data = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        querysets_data = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        querysets_data = paginator.page(paginator.num_pages)  # 取最后一页的记录
    return render_to_response('curd.html', {'data': querysets_data,'field_name':filed_name})


# 显示一条数据
def search(request):
    field_obj = Nodeinfo._meta.fields  # 获取字段对象
    filed_name = [field_obj[i].verbose_name for i in range(len(field_obj))]  # 所有字段中文名组成列表  ['ID', '主机名', 'IP地址', '省份', '城市', '运营商', '代理商', 'VIP地址']
    filed_name = filed_name[1:]  # 去除第一个ID
    q = request.GET['q'];
    if id == "":  # 若无输入，则转移到query查询所有
        return HttpResponseRedirect("/index")
    #bb = Nodeinfo.objects.filter(id=id)  # 通过id 过滤结果
    bb = Nodeinfo.objects.filter(Q(name__icontains=q)|Q(ip_address__icontains=q))#通过主机名或者ip查询
    return render_to_response('curd.html', {'data': bb,'field_name':filed_name})

# 添加保存数据
@csrf_exempt
def add(request):
    field_obj = Nodeinfo._meta.fields  # 获取字段对象
    field_list = [field_obj[i].name for i in range(len(field_obj))]  # 所有字段名组成列表
    field_list = field_list[1:]
    filed_name = [field_obj[i].verbose_name for i in range(len(field_obj))]  # 所有字段中文名组成列表  ['ID', '主机名', 'IP地址', '省份', '城市', '运营商', '代理商', 'VIP地址']
    filed_name = filed_name[1:]  # 去除第一个ID
    dic = dict(zip(field_list, filed_name))
    if request.method == 'POST':
    # c={} POST方式获取
        id = request.POST['id']
        hostname = request.POST['name']
        ip = request.POST['ip_address']
        province = request.POST['province']
        city = request.POST['city']
        isp = request.POST['isp']
        agent = request.POST['machineagent']
        vip = request.POST['vip']
        print(dict(request.POST))
        obj = Nodeinfo()
        if len(id) > 0:
            print("id不是null")
            obj.id = id;
        obj.name = hostname
        obj.ip_address = ip
        obj.province = province
        obj.city = city
        obj.isp = isp
        obj.machineagent = agent
        obj.vip = vip
        obj.save()

        return HttpResponseRedirect("/index")  # 转移执行query刷新操作
    return render(request, 'add.html', {'data':dic})

# 更新一条数据
def update(request):
    id = request.GET['id'];
    olddata = Nodeinfo.objects.get(id=id)  # 得到具体数据，与filter输出返回类型不同
    return render_to_response('update.html', {'data': olddata})


# 删除数据
def delByID(request):
    id = request.GET['id'];
    bb = Nodeinfo.objects.get(id=id)
    bb.delete()
    return HttpResponseRedirect("/index")


# 删除所选数据
def delSelect(request):
    arr = request.GET['arr']
    blist = "(" + arr + ")"  # 根据列表构建元组
    #print('>>>>>>>',blist)
    Nodeinfo.objects.extra(where=['id IN ' + str(blist) + '']).delete()

    return HttpResponse("delect success")



#登录
def acc_login(request):
    error_msg = ''
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        #仅认证
        user = authenticate(username=username, password=password)
        if user:
            #print("passed authencation", user)
            #认证通过后登录
            login(request, user)
            return redirect(request.GET.get('next', '/index'))
        else:
            error_msg = "Wrong username or password!"
    return render(request, 'login.html', {'error_msg': error_msg})


#登出
def acc_logout(request):
    logout(request)
    return redirect("/login/")



