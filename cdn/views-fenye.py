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
from django.db.models.aggregates import Count

#包装csrf请求，避免django认为其实跨站攻击脚本
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import random
import xlwt,datetime
from xlwt import *
import json

from .models import Nodeinfo



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
    limit = 15  # 每页显示的记录数

    after_range_num = 2        #当前页前显示5页
    befor_range_num = 2       #当前页后显示4页
    page_range=()

    querysets_data = Nodeinfo.objects.all().order_by('id')
    paginator = Paginator(querysets_data, limit)  # 实例化一个分页对象
    page = request.GET.get('page')  # 获取页码
    try:
        querysets_data = paginator.page(page)  # 获取某页对应的记录

        if int(page) >= after_range_num:
            page_range = paginator.page_range[int(page)-after_range_num:int(page)+befor_range_num]
        else:
            page_range = paginator.page_range[0:int(page)+befor_range_num]
        #print('>>>>>>',page_range)

    except PageNotAnInteger:  # 如果页码不是个整数
        querysets_data = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        querysets_data = paginator.page(paginator.num_pages)  # 取最后一页的记录
    return render_to_response('curd.html', {'data': querysets_data,'field_name':filed_name,'page_range':page_range})


# 显示一条数据
def search(request):
    field_obj = Nodeinfo._meta.fields  # 获取字段对象
    filed_name = [field_obj[i].verbose_name for i in range(len(field_obj))]  # 所有字段中文名组成列表  ['ID', '主机名', 'IP地址', '省份', '城市', '运营商', '代理商', 'VIP地址']
    filed_name = filed_name[1:]  # 去除第一个ID
    q = request.GET['q'];
    if id == "":  # 若无输入，则转移到query查询所有
        return HttpResponseRedirect("/index")
    #bb = Nodeinfo.objects.filter(id=id)  # 通过id 过滤结果
    bb = Nodeinfo.objects.filter(Q(name__icontains=q)|Q(ip_address__icontains=q)|Q(province__icontains=q)|Q(city__icontains=q)|Q(isp__icontains=q))#通过主机名或者ip查询
    return render_to_response('curd.html', {'data': bb,'field_name':filed_name})

#显示首页数据
def home(request):
    city_list=[]
    prov_list=[]
    #city_dic={}
    #prov_dic={}
    
    service=Nodeinfo.objects.all()
    city=list(Nodeinfo.objects.all().values('city'))
    province=list(Nodeinfo.objects.all().values('province'))
    #info=Nodeinfo.objects.all().values('province','city','isp')
    info=list(Nodeinfo.objects.values('province','city','isp').annotate(count=Count('province')))
    
    
    for i in city:
        city_list.append(i['city'])
    for i in province:
        prov_list.append(i['province'])
    s_count = len(service)
    c_count = len(set(city_list))
    p_count = len(set(prov_list))
    data = {'s_count':s_count,'p_count':p_count,'c_count':c_count}
    #for item in set(city_list):
    #    city_dic[item]=city_list.count(item)
    #for item in set(prov_list):
    #    prov_dic[item]=prov_list.count(item)
    #print(city_dic,prov_dic)
    
    return render(request, 'homepage.html',{'data':data,'info':info})

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
        v6 = request.POST['v6']
        province = request.POST['province']
        city = request.POST['city']
        isp = request.POST['isp']
        agent = request.POST['machineagent']
        vip = request.POST['vip']
        content = request.POST['content']
        print(dict(request.POST))
        obj = Nodeinfo()
        if len(id) > 0:
            print("id不是null")
            obj.id = id;
        obj.name = hostname
        obj.ip_address = ip
        obj.v6 = v6
        obj.province = province
        obj.city = city
        obj.isp = isp
        obj.machineagent = agent
        obj.vip = vip
        obj.content = content
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

#写数据到excle中
def wite_to_excel(n,head_data,records,download_path):
    #获取时间戳
    timestr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # 工作表
    wbk = xlwt.Workbook()
    sheet1 = wbk.add_sheet('sheet1',cell_overwrite_ok=True)
    #写入表头
    for filed in range(0,len(head_data)):
        sheet1.write(0,filed,head_data[filed],excel_head_style())
    #写入数据记录
    for row in range(1,n+1):
        for col in range(0,len(head_data)):
            sheet1.write(row,col,records[row-1][col],excel_record_style())
            #设置默认单元格宽度
            sheet1.col(col).width = 256*15

    file = '/livecdn'+timestr +'.xls'
    wbk.save(download_path+file)
    return download_path+file

# 定义导出文件表头格式
def excel_head_style():
    # 创建一个样式
    style = XFStyle()
    #设置背景色
    pattern = Pattern()
    pattern.pattern = Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = Style.colour_map['light_green']  # 设置单元格背景色
    style.pattern = pattern
    # 设置字体
    font0 = xlwt.Font()
    font0.name = u'微软雅黑'
    font0.bold = True
    font0.colour_index = 0
    font0.height = 240
    style.font = font0
    #设置文字位置
    alignment = xlwt.Alignment()  # 设置字体在单元格的位置
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # 水平方向
    alignment.vert = xlwt.Alignment.VERT_CENTER  # 竖直方向
    style.alignment = alignment
    # 设置边框
    borders = xlwt.Borders()  # Create borders
    borders.left = xlwt.Borders.THIN  # 添加边框-虚线边框
    borders.right = xlwt.Borders.THIN  # 添加边框-虚线边框
    borders.top = xlwt.Borders.THIN  # 添加边框-虚线边框
    borders.bottom = xlwt.Borders.THIN  # 添加边框-虚线边框
    style.borders = borders

    return style

# 定义导出文件记录格式
def excel_record_style():
    # 创建一个样式
    style = XFStyle()
    #设置字体
    font0 = xlwt.Font()
    font0.name = u'微软雅黑'
    font0.bold = False
    font0.colour_index = 0
    font0.height = 200
    style.font = font0
    #设置文字位置
    alignment = xlwt.Alignment()  # 设置字体在单元格的位置
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # 水平方向
    alignment.vert = xlwt.Alignment.VERT_CENTER  # 竖直方向
    style.alignment = alignment
    # 设置边框
    borders = xlwt.Borders()  # Create borders
    borders.left = xlwt.Borders.THIN  # 添加边框-虚线边框
    borders.right = xlwt.Borders.THIN  # 添加边框-虚线边框
    borders.top = xlwt.Borders.THIN  # 添加边框-虚线边框
    borders.bottom = xlwt.Borders.THIN  # 添加边框-虚线边框
    style.borders = borders

    return style

#查询所有数据并写到download目录
def exportall(request):
    querysets_data = Nodeinfo.objects.all()
    n = len(querysets_data)
    #表头
    head_data =['主机名', 'IP地址','V6地址', '省份', '城市', '运营商', '代理商', 'VIP地址','备注']
    #查询数据库数据
    records = []#[['EACNCTC_BJJ_BJJ01_LCAH002', '101.254.240.86', '北京', '北京', '电信', '高升', None], ['EACNCTC_GDY_DGY03_LCAH001', '121.12.104.234', '广东', '东莞', '电信', '资拓', 'None']]
    for data in querysets_data:
        name= data.name
        ip = data.ip_address
        v6 = data.v6
        province = data.province
        city = data.city
        isp = data.isp
        machineagent = data.machineagent
        vip = data.vip
        content = data.content
        record = []
        record.append(name)
        record.append(ip)
        record.append(v6)
        record.append(province)
        record.append(city)
        record.append(isp)
        record.append(machineagent)
        record.append(vip)
        record.append(content)
        records.append(record)
    download_path = 'download'

    filename = wite_to_excel(n, head_data, records, download_path)
    result = {'status':True,'download_url':filename}
    return HttpResponse(json.dumps(result))



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



