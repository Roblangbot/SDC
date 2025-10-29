# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone
from datetime import timedelta


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


class BarangayTable(models.Model):
    barangayid = models.AutoField(db_column='barangayID', primary_key=True)  # Field name made lowercase.
    barangay_name = models.CharField(max_length=255)
    cityid = models.ForeignKey('CityMunicipalityTable', models.DO_NOTHING, db_column='cityID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'barangay_table'


class CityMunicipalityTable(models.Model):
    cityid = models.AutoField(db_column='cityID', primary_key=True)  # Field name made lowercase.
    city_name = models.CharField(max_length=255)
    provinceid = models.ForeignKey('ProvinceTable', models.DO_NOTHING, db_column='provinceID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'city_municipality_table'


class ColorTable(models.Model):
    colorid = models.AutoField(db_column='colorID', primary_key=True)  # Field name made lowercase.
    colorname = models.CharField(db_column='colorName', max_length=99)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'color_table'
    
    def __str__(self):
        return self.colorname


class CountryTable(models.Model):
    countryid = models.AutoField(db_column='countryID', primary_key=True)  # Field name made lowercase.
    country_name = models.CharField(max_length=999)

    class Meta:
        managed = False
        db_table = 'country_table'


class CustomerTable(models.Model):
    customerid = models.AutoField(db_column='CustomerID', primary_key=True)  # Field name made lowercase.
    firstname = models.CharField(db_column='firstName', max_length=99)  # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=99)  # Field name made lowercase.
    contactno = models.CharField(db_column='contactNo', max_length=45)  # Field name made lowercase.
    email = models.CharField(max_length=999)

    class Meta:
        managed = False
        db_table = 'customer_table'

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


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
    
    def __str__(self):
        return self.itemstat


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
    salesid = models.ForeignKey('SalesTable', models.DO_NOTHING, db_column='salesID')  # Field name made lowercase.
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

    def __str__(self):
        return self.status

class PendingOrder(models.Model):
    customerid = models.ForeignKey(CustomerTable, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    order_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'pending_order_table'

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

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
        
    def __str__(self):
        return f"{self.prodnameid} - {self.colorid} - ${self.priceid}"


class ProvinceTable(models.Model):
    provinceid = models.AutoField(db_column='provinceID', primary_key=True)  # Field name made lowercase.
    province_name = models.CharField(max_length=255)
    regionid = models.ForeignKey('RegionTable', models.DO_NOTHING, db_column='regionID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'province_table'


class RegionTable(models.Model):
    regionid = models.AutoField(db_column='regionID', primary_key=True)  # Field name made lowercase.
    region_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'region_table'


class SalesAddressTable(models.Model):
    sales_addressid = models.AutoField(db_column='sales_addressID', primary_key=True)  # Field name made lowercase.
    salesid = models.ForeignKey('SalesTable', models.DO_NOTHING, db_column='salesID')  # Field name made lowercase.
    full_address = models.CharField(max_length=999)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    delivery_instructions = models.TextField(blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sales_address_table'


class SalesTable(models.Model):
    salesid = models.AutoField(db_column='salesID', primary_key=True)  # Field name made lowercase.
    ordernumber = models.CharField(db_column='orderNumber', max_length=999)  # Field name made lowercase.
    customerid = models.ForeignKey(CustomerTable, models.DO_NOTHING, db_column='customerID')  # Field name made lowercase.
    total_price = models.IntegerField()
    itemstatusid = models.ForeignKey(ItemStatusTable, models.DO_NOTHING, db_column='itemStatusID')  # Field name made lowercase.
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
