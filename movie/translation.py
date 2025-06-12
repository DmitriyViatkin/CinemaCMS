from .models import Movies
from modeltranslation.translator import  register, TranslationOptions

@register(Movies)
class MoviesTranslationOptions(TranslationOptions):
    fields = (

        'title',
        'description',
        'relise_date',
        'age_limit',

    )