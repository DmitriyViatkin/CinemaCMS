from django.contrib import admin
from  .models import  Block_SEO, Picture, Promotion, PaigesCinema, Contact,Banners, Gallery, Cross_banner, MainPaiges, PaigesNews



admin.site.register(Block_SEO)
@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'image_type', 'gallery__title', 'image', )


# Реєстрація моделі Gallery
@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title',) # Виводимо назву галереї у списку Галерей
admin.site.register(PaigesCinema)
admin.site.register(Promotion)
admin.site.register(Contact)
admin.site.register(Banners)
admin.site.register(Cross_banner)
admin.site.register(MainPaiges)
admin.site.register(PaigesNews)



