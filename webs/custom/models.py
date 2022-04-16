from django.db import models
from django.utils.html import format_html


#######################################################################################
# Create your models here.
class McnSync(models.Model):
    sync_identity = models.CharField(max_length=20, verbose_name="同步标识")
    sync_name = models.CharField(unique=True, max_length=20, verbose_name="同步名称")
    sync_url = models.URLField(max_length=250, verbose_name="同步地址")
    sync_limit = models.IntegerField(default=1000, verbose_name="同步数量/次")

    type_choices = ((1, '审核'), (2, '作品'), (3, '快速'), (4, '账号'))
    sync_type = models.SmallIntegerField(
        default=0, verbose_name="同步类型",
        help_text="0未知/1审核/2快速/3正常", choices=type_choices)
    active_choices = ((0, '否'), (1, '是'))
    sync_active = models.SmallIntegerField(
        default=0, verbose_name="是否开启同步",
        help_text="0否/1是", choices=active_choices)

    def sync_status(self):
        if self.sync_active == 1:
            ret = "yes"
        else:
            ret = "no"
        return format_html(
            "<img src='/static/admin/img/icon-{}.svg', alt='True'>",
            ret,
        )
    sync_status.short_description = '同步启用'

    class Meta:
        db_table = 'mcn_sync'
        verbose_name = "同步列表"
        verbose_name_plural = verbose_name
        unique_together = (("sync_identity", "sync_url"))

    def __str__(self):
        return self.sync_name


class McnPlat(models.Model):
    id = models.SmallIntegerField(primary_key=True, verbose_name="平台ID")
    plat_identity = models.CharField(max_length=20, verbose_name="平台标识")
    plat_name = models.CharField(max_length=20, verbose_name="平台名称")

    class Meta:
        db_table = 'mcn_plat'
        verbose_name = "平台列表"
        verbose_name_plural = verbose_name
        unique_together = (("plat_identity", "plat_name", ), )

    def __str__(self):
        return self.plat_name


#######################################################################################
class McnAccount(models.Model):
    mcn_plat = models.ForeignKey(
        "McnPlat", on_delete=models.CASCADE, verbose_name="平台ID")
    account_identity = models.CharField(max_length=50, verbose_name="账号标识")
    username = models.CharField(blank=True, max_length=50, verbose_name="账号名称")
    password = models.CharField(blank=True, max_length=50, verbose_name="账号密码")
    cookies = models.TextField(default="{}", blank=True, verbose_name="账号缓存")

    class Meta:
        db_table = 'mcn_account'
        verbose_name = "账户列表"
        verbose_name_plural = verbose_name
        unique_together = (("mcn_plat", "account_identity", "username"))

    def __str__(self):
        return f"{self.mcn_plat}{self.account_identity}--{self.username}"


class McnMachine(models.Model):
    machine_name = models.CharField(
        unique=True, max_length=50, verbose_name="机器名称")
    machine_host = models.GenericIPAddressField(
        default="127.0.0.1", verbose_name="机器地址")

    class Meta:
        db_table = 'mcn_machine'
        verbose_name = "机器列表"
        verbose_name_plural = verbose_name
        unique_together = (("machine_host",))

    def __str__(self):
        return self.machine_name


class McnRun(models.Model):
    mcn_machine = models.ForeignKey(
        "McnMachine", on_delete=models.CASCADE, verbose_name="机器ID")
    mcn_account = models.ForeignKey(
        "McnAccount", on_delete=models.CASCADE, verbose_name="账户ID")
    active_choices = ((0, '停用'), (1, '启用'))
    active = models.SmallIntegerField(
        default=1, verbose_name="是否启用运行", choices=active_choices)

    def active_status(self):
        if self.active == 1:
            ret = "yes"
        else:
            ret = "no"

        # User.objects.filter(pk=ps.pk).update(is_expired=ret)
        return format_html(
            "<img src='/static/admin/img/icon-{}.svg', alt='True'>",
            ret,
        )
    active_status.short_description = '运行启用'

    class Meta:
        db_table = 'mcn_run'
        verbose_name = "运行列表"
        verbose_name_plural = verbose_name
        unique_together = (("mcn_machine", "mcn_account"))

    def __str__(self):
        return f"{self.mcn_machine}--{self.mcn_account}"
