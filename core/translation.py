from .models import Cinemas, Halls
from modeltranslation.translator import  register, TranslationOptions, translator


@register(Halls)
class HallsTranslationOptions(TranslationOptions):
    fields = ('title',
    'description',
   )

@register(Cinemas)

class CinemasTranslationOptions(TranslationOptions):
        fields = ('title',
                  'description',
                  'conditions',
                  'city',
                   )