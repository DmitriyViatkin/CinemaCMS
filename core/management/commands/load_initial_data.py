from django.conf import settings
from django.core.management.base import BaseCommand

from datetime import timedelta, datetime
from django.core.files import File
import os
from main.models import Block_SEO, Gallery, Picture, PaigesCinema, Contact, Banners,Cross_Banner, News
from movie.models import Movies
from core.models import Cinemas, Halls, Sessions, Seats, Tickets

from core.date import (
    seo_block_cinema_data_list,
    seo_block_movies_data_list,
    seo_block_pages_data_list,
    movies_data_list,
    picture_data_movies_list,
    cinema_data_list,
    picture_data_cinema_list,
    paiges_cinema_data_list,
    picture_data_pages_list,
    contact_data_list,  # Убедитесь, что contact_data_list определен в core.date
    picture_data_contact_list,
    seo_block_contact_data_list ,
    picture_data_banners_list, picture_data_news_list , banner_news_list,
cross_banner_list, picture_data_ross_banner_list)


class Command(BaseCommand):
    help = "Load initial data including SEO blocks, Movies, Cinemas, Pages, Contacts and related Pictures."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting data loading..."))

        self.stdout.write(self.style.SUCCESS("Creating Block_SEO objects..."))
        created_seo_blocks = {}
        all_seo_data_lists = (
                seo_block_cinema_data_list +
                seo_block_movies_data_list +
                seo_block_pages_data_list +
                seo_block_contact_data_list
        )
        for seo_data in all_seo_data_lists:
            # Ищем по seo_url, так как это уникальное поле
            seo_obj, created = Block_SEO.objects.get_or_create(
                seo_url=seo_data['seo_url'],
                defaults=seo_data  # Используем все данные как значения по умолчанию
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created Block_SEO: {seo_obj.title_seo} (ID: {seo_obj.id})"))
            else:
                self.stdout.write(self.style.WARNING(
                    f"  Block_SEO already exists: {seo_obj.title_seo} (ID: {seo_obj.id}). Using existing."))

            # Сохраняем объекты SEO-блоков в словаре по title_seo и seo_url
            created_seo_blocks[seo_data['title_seo']] = seo_obj
            created_seo_blocks[seo_data['seo_url']] = seo_obj  # Это может быть полезно для поиска

        self.stdout.write(self.style.SUCCESS("Creating Movies, their Galleries, and Pictures..."))
        for movie_data in movies_data_list:
            seo_obj_for_movie = created_seo_blocks.get(movie_data['seo_block_title_seo'])
            if not seo_obj_for_movie:
                self.stdout.write(self.style.ERROR(
                    f"  Block_SEO for movie '{movie_data['title']}' not found (key: '{movie_data['seo_block_title_seo']}'). Skipping movie creation."))
                continue

            movie_obj, created_movie = Movies.objects.get_or_create(
                title=movie_data['title'],
                defaults={
                    'seo_block': seo_obj_for_movie,
                    'genre': movie_data['genre'],
                    'url_trailer': movie_data['url_trailer'],
                    'description': movie_data['description'],
                    'description_ru': movie_data.get('description_ru', ''),
                    'description_uk': movie_data.get('description_uk', ''),
                    'relise_date': movie_data['relise_date'],
                    'age_limit': movie_data['age_limit'],
                    'is_2d': movie_data['is_2d'],
                    'is_3d': movie_data['is_3d'],
                    'is_imax': movie_data['is_imax'],
                    'gallery': None,  # Галерея будет создана или обновлена ниже
                }
            )

            # Если объект уже существовал, обновим его поля (кроме галереи, которую мы обновим отдельно)
            if not created_movie:
                self.stdout.write(self.style.WARNING(f"  Movie '{movie_obj.title}' already exists. Updating its data."))
                movie_obj.seo_block = seo_obj_for_movie
                movie_obj.genre = movie_data['genre']
                movie_obj.url_trailer = movie_data['url_trailer']
                movie_obj.description = movie_data['description']
                movie_obj.description_ru = movie_data.get('description_ru', '')
                movie_obj.description_uk = movie_data.get('description_uk', '')
                movie_obj.relise_date = movie_data['relise_date']
                movie_obj.age_limit = movie_data['age_limit']
                movie_obj.is_2d = movie_data['is_2d']
                movie_obj.is_3d = movie_data['is_3d']
                movie_obj.is_imax = movie_data['is_imax']
                movie_obj.save()

            # Создаем новую галерею или получаем существующую для фильма
            # Если фильм уже существует и имеет галерею, используем её
            if movie_obj.gallery:
                current_movie_gallery = movie_obj.gallery
                self.stdout.write(self.style.WARNING(
                    f"  Movie '{movie_obj.title}' already has a gallery (ID: {current_movie_gallery.id}). Reusing it."))
            else:
                current_movie_gallery = Gallery.objects.create()
                movie_obj.gallery = current_movie_gallery
                movie_obj.save()
                self.stdout.write(self.style.SUCCESS(
                    f"  Created new Gallery (ID: {current_movie_gallery.id}) for Movie: {movie_obj.title}"))

            self.stdout.write(self.style.SUCCESS(
                f"  Processed Movie: {movie_obj.title} (ID: {movie_obj.id}) with Gallery (ID: {current_movie_gallery.id})"))

            pictures_for_movie = picture_data_movies_list.get(movie_data['title'])
            if pictures_for_movie:
                self.stdout.write(self.style.SUCCESS(
                    f"  Adding pictures to Gallery {current_movie_gallery.id} for {movie_obj.title} (from static files)..."))
                for pic_data in pictures_for_movie:
                    image_path_in_static = pic_data['image_path']
                    image_type = pic_data['image_type']
                    full_static_image_path = self._get_static_file_path(image_path_in_static)
                    if full_static_image_path:
                        with open(full_static_image_path, 'rb') as f:
                            # Проверяем, существует ли картинка с таким типом в этой галерее
                            picture_obj, created_pic = Picture.objects.get_or_create(
                                gallery=current_movie_gallery,
                                image_type=image_type,
                                defaults={'image': File(f, name=os.path.basename(image_path_in_static))}
                            )
                            if created_pic:
                                self.stdout.write(self.style.SUCCESS(
                                    f"    Added picture '{image_path_in_static}' from static to gallery {current_movie_gallery.id}."))
                            else:
                                self.stdout.write(self.style.WARNING(
                                    f"    Picture '{image_path_in_static}' already exists (same gallery, type). Skipping."))
                    else:
                        self.stdout.write(self.style.ERROR(
                            f"    Static image file not found at any STATICFILES_DIRS for: {image_path_in_static}. Skipping picture creation."))
            else:
                self.stdout.write(self.style.WARNING(f"  No picture data found for movie '{movie_obj.title}'."))

        self.stdout.write(self.style.SUCCESS("\nCreating Cinemas, their Galleries, and Pictures..."))
        for cinema_data in cinema_data_list:
            # Для кинотеатров, ключ SEO-блока - это обычно их title
            seo_obj_for_cinema = created_seo_blocks.get(cinema_data['title'])
            if not seo_obj_for_cinema:
                self.stdout.write(self.style.ERROR(
                    f"  Block_SEO for cinema '{cinema_data['title']}' not found (key: '{cinema_data['title']}'). Skipping cinema creation."))
                continue

            cinema_obj, created_cinema = Cinemas.objects.get_or_create(
                title=cinema_data['title'],
                defaults={
                    'seo_block': seo_obj_for_cinema,
                    'description': cinema_data['description'],
                    'description_ru': cinema_data.get('description_ru', ''),
                    'description_uk': cinema_data.get('description_uk', ''),
                    'conditions': cinema_data['conditions'],
                    'conditions_ru': cinema_data.get('conditions_ru', ''),
                    'conditions_uk': cinema_data.get('conditions_uk', ''),
                    'city': cinema_data['city'],
                    'city_ru': cinema_data.get('city_ru', ''),
                    'city_uk': cinema_data.get('city_uk', ''),
                    'gallery': None,
                    'date': cinema_data['date']
                }
            )

            if not created_cinema:
                self.stdout.write(
                    self.style.WARNING(f"  Cinema '{cinema_obj.title}' already exists. Updating its data."))
                cinema_obj.seo_block = seo_obj_for_cinema
                cinema_obj.description = cinema_data['description']
                cinema_obj.description_ru = cinema_data.get('description_ru', '')
                cinema_obj.description_uk = cinema_data.get('description_uk', '')
                cinema_obj.conditions = cinema_data['conditions']
                cinema_obj.conditions_ru = cinema_data.get('conditions_ru', '')
                cinema_obj.conditions_uk = cinema_data.get('conditions_uk', '')
                cinema_obj.city = cinema_data['city']
                cinema_obj.city_ru = cinema_data.get('city_ru', '')
                cinema_obj.city_uk = cinema_data.get('city_uk', '')
                cinema_obj.date = cinema_data['date']
                cinema_obj.save()

            # Создаем новую галерею или получаем существующую для кинотеатра
            if cinema_obj.gallery:
                current_cinema_gallery = cinema_obj.gallery
                self.stdout.write(self.style.WARNING(
                    f"  Cinema '{cinema_obj.title}' already has a gallery (ID: {current_cinema_gallery.id}). Reusing it."))
            else:
                current_cinema_gallery = Gallery.objects.create()
                cinema_obj.gallery = current_cinema_gallery
                cinema_obj.save()
                self.stdout.write(self.style.SUCCESS(
                    f"  Created new Gallery (ID: {current_cinema_gallery.id}) for Cinema: {cinema_obj.title}"))

            self.stdout.write(self.style.SUCCESS(
                f"  Processed Cinema: {cinema_obj.title} (ID: {cinema_obj.id}) with Gallery (ID: {current_cinema_gallery.id})"))

            pictures_for_cinema = picture_data_cinema_list.get(cinema_data['title'])
            if pictures_for_cinema:
                self.stdout.write(self.style.SUCCESS(
                    f"  Adding pictures to Gallery {current_cinema_gallery.id} for {cinema_obj.title} (from static files)..."))
                for pic_data in pictures_for_cinema:
                    image_path_in_static = pic_data['image_path']
                    image_type = pic_data['image_type']
                    full_static_image_path = self._get_static_file_path(image_path_in_static)
                    if full_static_image_path:
                        with open(full_static_image_path, 'rb') as f:
                            picture_obj, created_pic = Picture.objects.get_or_create(
                                gallery=current_cinema_gallery,
                                image_type=image_type,
                                defaults={'image': File(f, name=os.path.basename(image_path_in_static))}
                            )
                            if created_pic:
                                self.stdout.write(self.style.SUCCESS(
                                    f"    Added picture '{image_path_in_static}' from static to gallery {current_cinema_gallery.id}."))
                            else:
                                self.stdout.write(self.style.WARNING(
                                    f"    Picture '{image_path_in_static}' already exists (same gallery, type). Skipping."))
                    else:
                        self.stdout.write(self.style.ERROR(
                            f"    Static image file not found at any STATICFILES_DIRS for: {image_path_in_static}. Skipping picture creation."))
            else:
                self.stdout.write(self.style.WARNING(f"  No picture data found for cinema '{cinema_obj.title}'."))

        # --- PaigesCinema и их Gallery/Picture ---
        self.stdout.write(self.style.SUCCESS(
            "\nCreating PaigesCinema objects (pages like Advertisement, Kids Room, VIP Hall, etc.) and their Galleries/Pictures..."))

        for page_data in paiges_cinema_data_list:
            seo_obj_for_page = created_seo_blocks.get(page_data['seo_block_title_seo'])
            if not seo_obj_for_page:
                self.stdout.write(self.style.ERROR(
                    f"  Block_SEO for PaigesCinema '{page_data['title']}' not found (key: '{page_data['seo_block_title_seo']}'). Skipping creation."))
                continue

            page_obj, created_page = PaigesCinema.objects.get_or_create(
                title=page_data['title'],
                defaults={
                    'seo_block': seo_obj_for_page,
                    'description': page_data['description'],
                    'description_ru': page_data.get('description_ru', ''),
                    'description_uk': page_data.get('description_uk', ''),
                    'date': page_data['date'],
                    'is_active': page_data['is_active'],
                    'gallery': None,
                }
            )

            if not created_page:
                self.stdout.write(
                    self.style.WARNING(f"  PaigesCinema '{page_obj.title}' already exists. Updating its data."))
                page_obj.seo_block = seo_obj_for_page
                page_obj.description = page_data['description']
                page_obj.description_ru = page_data.get('description_ru', '')
                page_obj.description_uk = page_data.get('description_uk', '')
                page_obj.date = page_data['date']
                page_obj.is_active = page_data['is_active']
                page_obj.save()

            # Создаем новую галерею или получаем существующую для страницы
            if page_obj.gallery:
                current_page_gallery = page_obj.gallery
                self.stdout.write(self.style.WARNING(
                    f"  PaigesCinema '{page_obj.title}' already has a gallery (ID: {current_page_gallery.id}). Reusing it."))
            else:
                current_page_gallery = Gallery.objects.create()
                page_obj.gallery = current_page_gallery
                page_obj.save()
                self.stdout.write(self.style.SUCCESS(
                    f"  Created new Gallery (ID: {current_page_gallery.id}) for PaigesCinema: {page_obj.title}"))

            self.stdout.write(self.style.SUCCESS(
                f"  Processed PaigesCinema: {page_obj.title} (ID: {page_obj.id}) with Gallery (ID: {current_page_gallery.id})"))

            pictures_for_page = picture_data_pages_list.get(page_data['title'])
            if pictures_for_page:
                self.stdout.write(self.style.SUCCESS(
                    f"  Adding pictures to Gallery {current_page_gallery.id} for {page_obj.title} (from static files)..."))
                for pic_data in pictures_for_page:
                    image_path_in_static = pic_data['image_path']
                    image_type = pic_data['image_type']
                    full_static_image_path = self._get_static_file_path(image_path_in_static)
                    if full_static_image_path:
                        with open(full_static_image_path, 'rb') as f:
                            picture_obj, created_pic = Picture.objects.get_or_create(
                                gallery=current_page_gallery,
                                image_type=image_type,
                                defaults={'image': File(f, name=os.path.basename(image_path_in_static))}
                            )
                            if created_pic:
                                self.stdout.write(self.style.SUCCESS(
                                    f"    Added picture '{image_path_in_static}' from static to gallery {current_page_gallery.id}."))
                            else:
                                self.stdout.write(self.style.WARNING(
                                    f"    Picture '{image_path_in_static}' already exists (same gallery, type). Skipping."))
                    else:
                        self.stdout.write(self.style.ERROR(
                            f"    Static image file not found at any STATICFILES_DIRS for: {image_path_in_static}. Skipping picture creation."))
            else:
                self.stdout.write(self.style.WARNING(f"  No picture data found for PaigesCinema '{page_obj.title}'."))

        # --- Contacts ---
        self.stdout.write(self.style.SUCCESS("\nCreating Contact objects and their Galleries/Pictures..."))

        # Получаем уже созданный SEO-блок для контактов из словаря created_seo_blocks
        # Используем seo_url для поиска, так как он уникален
        seo_block_contact_url = seo_block_contact_data_list[0]['seo_url']
        seo_block_contact = created_seo_blocks.get(seo_block_contact_url)

        if not seo_block_contact:
            self.stdout.write(self.style.ERROR(
                f"  Block_SEO for Contacts (URL: '{seo_block_contact_url}') not found. Skipping Contact creation."))
            return  # Выходим, если базовый SEO-блок не найден

        for contact_data in contact_data_list:
            contact_obj, created_contact = Contact.objects.get_or_create(
                title=contact_data['title'],
                defaults={
                    'address': contact_data['address'],
                    'latitude': contact_data['latitude'],
                    'longitude': contact_data['longitude'],
                    'phone_number': contact_data['phone_number'],  # Добавлено: phone_number в defaults
                    'gallery': None,  # Галерея будет создана или обновлена ниже
                    'seo_block': seo_block_contact
                }
            )

            if not created_contact:
                self.stdout.write(self.style.WARNING(
                    f"  Contact '{contact_obj.title}' already exists. Updating its data and SEO."))
                contact_obj.address = contact_data['address']
                contact_obj.latitude = contact_data['latitude']
                contact_obj.longitude = contact_data['longitude']
                contact_obj.phone_number = contact_data['phone_number']  # Добавлено: обновление phone_number
                contact_obj.seo_block = seo_block_contact
                contact_obj.save()

            # Создаем новую галерею или получаем существующую для контакта
            if contact_obj.gallery:
                current_contact_gallery = contact_obj.gallery
                self.stdout.write(self.style.WARNING(
                    f"  Contact '{contact_obj.title}' already has a gallery (ID: {current_contact_gallery.id}). Reusing it."))
            else:
                current_contact_gallery = Gallery.objects.create()
                contact_obj.gallery = current_contact_gallery
                contact_obj.save()
                self.stdout.write(self.style.SUCCESS(
                    f"  Created new Gallery (ID: {current_contact_gallery.id}) for Contact: {contact_obj.title}"))

            self.stdout.write(self.style.SUCCESS(
                f"  Processed Contact: {contact_obj.title} (ID: {contact_obj.id}) with Gallery (ID: {current_contact_gallery.id})"))

            # Загружаем изображения для контакта
            pictures_for_contact = picture_data_contact_list.get(contact_data['title'])
            if pictures_for_contact:
                self.stdout.write(self.style.SUCCESS(
                    f"  Adding pictures to Gallery {current_contact_gallery.id} for {contact_obj.title} (from static files)..."))
                for pic_data in pictures_for_contact:
                    path = self._get_static_file_path(pic_data['image_path'])
                    if path:
                        with open(path, 'rb') as f:
                            picture_obj, created_pic = Picture.objects.get_or_create(
                                gallery=current_contact_gallery,
                                image_type=pic_data['image_type'],
                                defaults={'image': File(f, name=os.path.basename(pic_data['image_path']))}
                            )
                            if created_pic:
                                self.stdout.write(self.style.SUCCESS(
                                    f"    Added picture: {pic_data['image_path']} ({pic_data['image_type']}) to gallery {current_contact_gallery.id}"))
                            else:
                                self.stdout.write(self.style.WARNING(
                                    f"    Picture: {pic_data['image_path']} ({pic_data['image_type']}) already exists in gallery {current_contact_gallery.id}. Skipping."))
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"    Static image file not found at: {pic_data['image_path']}. Skipping picture creation."))
            else:
                self.stdout.write(self.style.WARNING(f"  No picture data found for Contact '{contact_obj.title}'."))

        self.stdout.write(self.style.SUCCESS("\n== Creating gallery for banners and adding pictures... =="))

        # Галерея для звичайних банерів
        banner_gallery = Gallery.objects.create()

        pictures_for_banners = picture_data_banners_list.get('Галерея для нових банерів')

        if pictures_for_banners:
            for pic_data in pictures_for_banners:
                image_path = pic_data['image_path'].lstrip('/')  # Убираем начальный слэш
                image_type = pic_data['image_type']
                full_path = self._get_static_file_path(image_path)

                if not full_path:
                    self.stdout.write(self.style.ERROR(f"      Not found: {image_path}. Skipping."))
                    continue

                with open(full_path, 'rb') as f:
                    picture_obj, created_pic = Picture.objects.get_or_create(
                        gallery=banner_gallery,
                        image_type=image_type,
                        defaults={'image': File(f, name=os.path.basename(image_path))}
                    )

                if created_pic:
                    self.stdout.write(self.style.SUCCESS(f"      Added: {image_path}"))
                else:
                    self.stdout.write(self.style.WARNING(f"      Already exists: {image_path}. Skipping."))
        else:
            self.stdout.write(self.style.WARNING("    No pictures found for this gallery."))

        # === Галерея для новин ===
        self.stdout.write(self.style.SUCCESS("\n== Creating gallery for news banners and adding pictures... =="))

        news_gallery = Gallery.objects.create()

        pictures_for_news = picture_data_news_list.get('Галерея для нових банерів')

        if pictures_for_news:
            for i, pic_data in enumerate(pictures_for_news):
                image_path = pic_data['image_path'].lstrip('/')
                image_type = pic_data['image_type']
                full_path = self._get_static_file_path(image_path)

                if not full_path:
                    self.stdout.write(self.style.ERROR(f"      Not found: {image_path}. Skipping."))
                    continue

                with open(full_path, 'rb') as f:
                    picture_obj, created_pic = Picture.objects.get_or_create(
                        gallery=news_gallery,
                        image_type=image_type,
                        defaults={'image': File(f, name=os.path.basename(image_path))}
                    )

                if created_pic:
                    self.stdout.write(self.style.SUCCESS(f"      Added: {image_path}"))
                else:
                    self.stdout.write(self.style.WARNING(f"      Already exists: {image_path}. Skipping."))

                if i < len(banner_news_list):
                    banner_data = banner_news_list[i]
                    News.objects.create(
                        gallery=news_gallery,

                        url=banner_data['url'],
                        scroll_speed=timedelta(seconds=banner_data['scroll_speed']),
                        is_active=banner_data['is_active']
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"      Created News with URL '{banner_data['url']}' and scroll speed {banner_data['scroll_speed']}."))

        else:
            self.stdout.write(self.style.WARNING("    No pictures found for news gallery."))

        # === Галерея для cross banners ===
        self.stdout.write(self.style.SUCCESS("\n== Creating gallery for cross banners and adding pictures... =="))

        cross_gallery = Gallery.objects.create()

        pictures_for_cross = picture_data_ross_banner_list.get('Галерея для нових банерів')

        if pictures_for_cross:
            for i, pic_data in enumerate(pictures_for_cross):
                image_path = pic_data['image_path'].lstrip('/')
                image_type = pic_data['image_type']
                full_path = self._get_static_file_path(image_path)

                if not full_path:
                    self.stdout.write(self.style.ERROR(f"      Not found: {image_path}. Skipping."))
                    continue

                with open(full_path, 'rb') as f:
                    picture_obj, created = Picture.objects.get_or_create(
                        gallery=cross_gallery,
                        image_type=image_type,
                        defaults={'image': File(f, name=os.path.basename(image_path))}
                    )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"      Added: {image_path}"))
                else:
                    self.stdout.write(self.style.WARNING(f"      Already exists: {image_path}. Skipping."))

                if i < len(cross_banner_list):
                    banner_data = cross_banner_list[i]
                    Cross_Banner.objects.create(
                        gallery=cross_gallery,

                        type=banner_data['type']
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"      Created Cross_Banner with type '{banner_data['type']}'."))

        else:
            self.stdout.write(self.style.WARNING("    No pictures found for cross banner gallery."))

        self.stdout.write(self.style.SUCCESS("=== load_initial_data completed ==="))

    def _get_static_file_path(self, image_path: str):

        from django.conf import settings
        import os

        for static_dir in settings.STATICFILES_DIRS:
            full_path = os.path.join(static_dir, image_path)
            if os.path.exists(full_path):
                return full_path
        return None

