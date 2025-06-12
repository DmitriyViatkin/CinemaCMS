from modeltranslation.translator import  register, TranslationOptions, translator

from main.models import  MainPaiges, PaigesNews, PaigesCinema,Promotion




# Опции перевода для модели MainPaiges
@register(MainPaiges)
class MainPaigesTranslationOptions(TranslationOptions):
    fields = ('SEO_text', 'phone_1', 'phone_2',)


# Опции перевода для модели Promotion
@register(Promotion)
class PromotionTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)


# Опции перевода для модели PaigesNews
@register(PaigesNews)
class PaigesNewsTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)


# Опции перевода для модели PaigesCinema
@register(PaigesCinema)
class PaigesCinemaTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)


