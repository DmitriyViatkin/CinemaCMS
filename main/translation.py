from modeltranslation.translator import register, TranslationOptions

from main.models import MainPaiges, PaigesNews, PaigesCinema, Promotion

@register(MainPaiges)
class MainPaigesTranslationOptions(TranslationOptions):
    fields = ('SEO_text', 'phone_1', 'phone_2',)


# Опции перевода для модели Promotion
@register(Promotion)
class PromotionTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)



@register(PaigesNews)
class PaigesNewsTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)



@register(PaigesCinema)
class PaigesCinemaTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)
