from django.contrib import admin
from  .models import  Block_SEO, Picture, Promotion, PaigesCinema, Contact,Banners,   Cross_Banner, MainPaiges, PaigesNews



admin.site.register(Block_SEO)
@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'image_type',    'image', )


# Реєстрація моделі Gallery


admin.site.register(PaigesCinema)
admin.site.register(Promotion)
admin.site.register(Contact)
admin.site.register(Banners)
admin.site.register(Cross_Banner)
admin.site.register(MainPaiges)
admin.site.register(PaigesNews)



