from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from .models import McnSync, McnPlat, McnAccount, McnMachine, McnRun


admin.site.site_title = 'MCN数据采集'
admin.site.site_header = '采集管理系统'


# Register your models here.
@admin.register(McnSync)
class McnSyncAdmin(admin.ModelAdmin):
    fieldsets = (
        ('同步基本信息', {
            'fields': ('sync_identity', 'sync_name', 'sync_url'),
            'classes': ('wide', 'extrapretty'),
        }),
        ('同步基本配置', {
            'fields': ('sync_limit', 'sync_type', 'sync_active'),
            'classes': ('wide', 'extrapretty'),
        }),
    )
    list_display = ('sync_identity', 'sync_name', 'sync_url', 'sync_limit',
                    'sync_type', 'sync_status')
    list_display_links = ('sync_identity', 'sync_name')
    list_per_page = 20
    ordering = ('id',)
    list_filter = ('sync_type', 'sync_active')      # 过滤器
    search_fields = ('sync_identity', 'sync_name')                    # 搜索字段
    actions = ['sync_button']         # 自定义按钮

    def sync_button(self, request, queryset):
        query_list = queryset.values("id", "sync_active")
        for i in query_list:
            if i['sync_active']:
                queryset.filter(id=i['id']).update(sync_active=0)
            else:
                queryset.filter(id=i['id']).update(sync_active=1)
        self.message_user(request, "启用切换成功")

    sync_button.short_description = '启用切换'
    sync_button.icon = 'fas el-icon-check'
    sync_button.type = 'success'
    # active_button.style = 'color:black;'
    # # 给按钮增加确认
    # active_button.confirm = '你是否执意要点击这个按钮？'
    # # 链接按钮，action_type 0=当前页内打开，1=新tab打开，2=浏览器tab打开
    # active_button.action_type = 1
    # active_button.action_url = 'http://www.baidu.com'


@admin.register(McnPlat)
class McnPlatAdmin(admin.ModelAdmin):
    fieldsets = (
        ('平台详情', {
            'fields': ('id', 'plat_identity', 'plat_name'),
            'classes': ('wide', 'extrapretty'),
        }),
    )
    list_display = ('id', 'plat_identity', 'plat_name')
    list_display_links = ('plat_identity', 'plat_name')
    list_per_page = 20
    ordering = ('id',)
    list_filter = ('id',)
    search_fields = ('plat_identity', 'plat_name')


@admin.register(McnAccount)
class McnAccountAdmin(admin.ModelAdmin):
    fieldsets = (
        ('账号详情', {
            'fields': ('mcn_plat', 'account_identity', 'username',
                       'password', 'cookies'),
            'classes': ('wide', 'extrapretty'),
        }),
    )
    list_display = ('mcn_plat', 'account_identity', 'username', 'password')
    list_display_links = ('mcn_plat', 'account_identity')
    list_per_page = 20
    ordering = ('mcn_plat',)
    list_filter = ("mcn_plat",)
    search_fields = ('account_identity', 'username')


@admin.register(McnMachine)
class McnMachineAdmin(admin.ModelAdmin):
    fieldsets = (
        ('机器详情', {
            'fields': ('machine_name', 'machine_host'),
            'classes': ('wide', 'extrapretty'),
        }),
    )
    list_display = ('machine_name', 'machine_host')
    list_display_links = ('machine_name',)
    list_per_page = 20
    ordering = ('id',)
    search_fields = ('machine_name',)


@admin.register(McnRun)
class McnRunAdmin(admin.ModelAdmin):
    fieldsets = (
        ('运行详情', {
            'fields': ('mcn_machine', 'mcn_account', 'active'),
            'classes': ('wide', 'extrapretty'),
        }),
    )
    list_display = ('mcn_machine', 'mcn_account', 'active_status')
    list_display_links = ('mcn_machine', 'mcn_account')
    list_per_page = 20
    ordering = ('mcn_machine', 'mcn_account')
    list_filter = ('active',)
    search_fields = ('mcn_machine__machine_name', 'mcn_account__mcn_plat__plat_name')

    def active_button(self, request, queryset):
        query_list = queryset.values("id", "active")
        for i in query_list:
            if i['active']:
                queryset.filter(id=i['id']).update(active=0)
            else:
                queryset.filter(id=i['id']).update(active=1)
        self.message_user(request, "启用切换成功")

    actions = ['active_button', ]
    active_button.short_description = '启用切换'
    # # 指定按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    active_button.icon = 'fas el-icon-check'
    active_button.type = 'success'
