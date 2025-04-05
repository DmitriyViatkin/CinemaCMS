from django.contrib import admin

from .models import  Cinemas, Tickets, Seats, Sessions, Movies, Halls
# Register your models here.


admin.site.register(Movies)
admin.site.register(Cinemas)
admin.site.register(Halls)
admin.site.register(Seats)
admin.site.register(Tickets)
admin.site.register(Sessions)

