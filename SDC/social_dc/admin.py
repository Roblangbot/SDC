from django.contrib import admin
from .models import RedTable, BlueTable, GrayTable, BeigeTable, BrownTable, WhiteTable, OrangeTable, YellowTable, SizeTable, ColorTable
from .models import OrderTable, ProductTable, PriceTable, SalesTable, StatusTable, DeliveryTable, CustomerTable

# Register your models here.
admin.site.register(RedTable)
admin.site.register(BlueTable)
admin.site.register(GrayTable)
admin.site.register(BeigeTable)
admin.site.register(BrownTable)
admin.site.register(WhiteTable)
admin.site.register(OrangeTable)
admin.site.register(YellowTable)
admin.site.register(SizeTable)
admin.site.register(ColorTable)
admin.site.register(OrderTable)
admin.site.register(ProductTable)
admin.site.register(PriceTable)
admin.site.register(SalesTable)
admin.site.register(StatusTable)
admin.site.register(DeliveryTable)
admin.site.register(CustomerTable)
