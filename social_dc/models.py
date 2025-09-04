# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class ColorTable(models.Model):
    colorid = models.AutoField(db_column='colorID', primary_key=True)  # Field name made lowercase.
    colorname = models.CharField(db_column='colorName', max_length=99)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'color_table'

    def __str__(self):
        return self.colorname 


class CustomerTable(models.Model):
    customerid = models.AutoField(db_column='CustomerID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=45)  # Field name made lowercase.
    contactno_field = models.CharField(db_column='ContactNo.', max_length=45)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'customer_table'


class DeliveryTable(models.Model):
    deliveryid = models.AutoField(db_column='deliveryID', primary_key=True)  # Field name made lowercase.
    salesid = models.IntegerField(db_column='salesID')  # Field name made lowercase.
    statusid = models.ForeignKey('StatusTable', models.DO_NOTHING, db_column='statusID')  # Field name made lowercase.
    date = models.DateField()
    time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'delivery_table'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class ItemStatusTable(models.Model):
    itemstatusid = models.AutoField(db_column='itemStatusID', primary_key=True)  # Field name made lowercase.
    itemstat = models.CharField(db_column='itemStat', max_length=99)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'item status table'


class MonthyreportTable(models.Model):
    monthlyreportid = models.IntegerField(db_column='monthlyreportID', primary_key=True)  # Field name made lowercase.
    days = models.IntegerField()
    weeks = models.IntegerField()
    months = models.IntegerField()
    revenue = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'monthyreport_table'


class OrderTable(models.Model):
    orderid = models.AutoField(db_column='orderID', primary_key=True)  # Field name made lowercase.
    salesid = models.ForeignKey('SalesTable', models.DO_NOTHING, db_column='salesID')  # Field name made lowercase.
    sizeid = models.ForeignKey('SizeTable', models.DO_NOTHING, db_column='sizeID')  # Field name made lowercase.
    productid = models.ForeignKey('ProductTable', models.DO_NOTHING, db_column='productID')  # Field name made lowercase.
    priceid = models.ForeignKey('PriceTable', models.DO_NOTHING, db_column='priceID')  # Field name made lowercase.
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'order_table'


class PaymentTable(models.Model):
    paymentid = models.AutoField(db_column='paymentID', primary_key=True)  # Field name made lowercase.
    paystatid = models.ForeignKey('PaystatTable', models.DO_NOTHING, db_column='paystatID')  # Field name made lowercase.
    mop = models.CharField(db_column='MOP', max_length=99)  # Field name made lowercase.
    date = models.DateField(db_column='Date')  # Field name made lowercase.
    time = models.TimeField(db_column='Time')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'payment_table'


class PaystatTable(models.Model):
    paystatid = models.AutoField(db_column='paystatID', primary_key=True)  # Field name made lowercase.
    status = models.CharField(max_length=99)

    class Meta:
        managed = False
        db_table = 'paystat_table'


class PriceTable(models.Model):
    priceid = models.IntegerField(db_column='priceID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=45)
    amount = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'price_table'

    def __str__(self):
        return str(self.amount)


class ProdNameTable(models.Model):
    prodnameid = models.AutoField(db_column='prodNameId', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=999, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prod_name_table'

    def __str__(self):
        return self.name 


class ProductTable(models.Model):
    productid = models.AutoField(db_column='productID', primary_key=True)  # Field name made lowercase.
    colorid = models.ForeignKey(ColorTable, models.DO_NOTHING, db_column='colorID')  # Field name made lowercase.
    prodnameid = models.ForeignKey(ProdNameTable, models.DO_NOTHING, db_column='prodNameID')  # Field name made lowercase.
    priceid = models.ForeignKey(PriceTable, models.DO_NOTHING, db_column='priceID')  # Field name made lowercase.
    productimage = models.CharField(db_column='productImage', max_length=999)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'product_table'


class SalesTable(models.Model):
    salesid = models.AutoField(db_column='salesID', primary_key=True)  # Field name made lowercase.
    customerid = models.ForeignKey(CustomerTable, models.DO_NOTHING, db_column='customerID')  # Field name made lowercase.
    total_price = models.IntegerField()
    itemstatusid = models.ForeignKey(ItemStatusTable, models.DO_NOTHING, db_column='itemStatusID')  # Field name made lowercase.
    paymentid = models.ForeignKey(PaymentTable, models.DO_NOTHING, db_column='PaymentID')  # Field name made lowercase.
    sales_date = models.DateField(blank=True, null=True)
    sales_time = models.TimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sales_table'


class SizeTable(models.Model):
    sizeid = models.AutoField(db_column='sizeID', primary_key=True)  # Field name made lowercase.
    size = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'size_table'


class StatusTable(models.Model):
    statusid = models.IntegerField(db_column='statusID', primary_key=True)  # Field name made lowercase.
    status = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'status_table'
