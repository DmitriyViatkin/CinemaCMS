
from core.date import ( seo_block_cinema_data_list, cinema_data_list, gallery, picture_data_movies_list, seo_block_movies_data_list,
       movies_data_list, picture_data_cinema_list, seo_block_pages_data_list,seo_block_pages_data_list,
    paiges_cinema_data_list,        picture_data_pages_list,)
from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime

from django.core.files import File
import os
from main.models import Block_SEO, Gallery, Picture, PaigesCinema
from movie.models import Movies
from core.models import Cinemas, Halls, Sessions, Seats, Tickets





class Command(BaseCommand):
    help = "Load specific data for Cinemas, Movies, Pages (PaigesCinema), etc."

    def _get_static_file_path(self, relative_path):

        for static_dir in settings.STATICFILES_DIRS:
            full_path = os.path.join(static_dir, relative_path)
            if os.path.exists(full_path):
                return full_path
        return None

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting data loading..."))


        self.stdout.write(self.style.SUCCESS("Creating Block_SEO objects..."))
        created_seo_blocks = {}
        all_seo_data_lists = (
            seo_block_cinema_data_list +
            seo_block_movies_data_list +
            seo_block_pages_data_list
        )
        for seo_data in all_seo_data_lists:
            seo_obj, created = Block_SEO.objects.get_or_create(
                seo_url=seo_data['seo_url'],
                defaults=seo_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created Block_SEO: {seo_obj.title_seo} (ID: {seo_obj.id})"))
            else:
                self.stdout.write(self.style.WARNING(f"  Block_SEO already exists: {seo_obj.title_seo} (ID: {seo_obj.id}). Using existing."))
            created_seo_blocks[seo_data['title_seo']] = seo_obj


        self.stdout.write(self.style.SUCCESS("Creating Movies, their Galleries, and Pictures..."))
        for movie_data in movies_data_list:
            seo_obj_for_movie = created_seo_blocks.get(movie_data['seo_block_title_seo'])
            if not seo_obj_for_movie:
                self.stdout.write(self.style.ERROR(f"  Block_SEO for movie '{movie_data['title']}' not found. Skipping movie creation."))
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
                    'gallery': None,
                }
            )
            if not created_movie:
                self.stdout.write(self.style.WARNING(f"  Movie '{movie_obj.title}' already exists. Updating its gallery/pictures."))

            new_movie_gallery = Gallery.objects.create()
            movie_obj.gallery = new_movie_gallery
            movie_obj.save()
            self.stdout.write(self.style.SUCCESS(f"  Created/Updated Movie: {movie_obj.title} (ID: {movie_obj.id}) with new Gallery (ID: {new_movie_gallery.id})"))

            pictures_for_movie = picture_data_movies_list.get(movie_data['title'])
            if pictures_for_movie:
                self.stdout.write(self.style.SUCCESS(f"  Adding pictures to Gallery {new_movie_gallery.id} for {movie_obj.title} (from static files)..."))
                for pic_data in pictures_for_movie:
                    image_path_in_static = pic_data['image_path']
                    image_type = pic_data['image_type']
                    full_static_image_path = self._get_static_file_path(image_path_in_static)
                    if full_static_image_path:
                        with open(full_static_image_path, 'rb') as f:
                            picture_obj, created_pic = Picture.objects.get_or_create(
                                gallery=new_movie_gallery,
                                image_type=image_type,
                                defaults={'image': File(f, name=os.path.basename(image_path_in_static))}
                            )
                            if created_pic:
                                self.stdout.write(self.style.SUCCESS(f"    Added picture '{image_path_in_static}' from static to gallery {new_movie_gallery.id}."))
                            else:
                                self.stdout.write(self.style.WARNING(f"    Picture '{image_path_in_static}' already exists (same gallery, type). Skipping."))
                    else:
                        self.stdout.write(self.style.ERROR(f"    Static image file not found at any STATICFILES_DIRS for: {image_path_in_static}. Skipping picture creation."))
            else:
                self.stdout.write(self.style.WARNING(f"  No picture data found for movie '{movie_obj.title}'."))



        self.stdout.write(self.style.SUCCESS("\nCreating Cinemas, their Galleries, and Pictures..."))
        for cinema_data in cinema_data_list:
            seo_obj_for_cinema = created_seo_blocks.get(cinema_data['title'])
            if not seo_obj_for_cinema:
                self.stdout.write(self.style.ERROR(f"  Block_SEO for cinema '{cinema_data['title']}' not found. Skipping cinema creation."))
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
                self.stdout.write(self.style.WARNING(f"  Cinema '{cinema_obj.title}' already exists. Updating its gallery/pictures."))

            new_cinema_gallery = Gallery.objects.create()
            cinema_obj.gallery = new_cinema_gallery
            cinema_obj.save()
            self.stdout.write(self.style.SUCCESS(f"  Created/Updated Cinema: {cinema_obj.title} (ID: {cinema_obj.id}) with new Gallery (ID: {new_cinema_gallery.id})"))

            pictures_for_cinema = picture_data_cinema_list.get(cinema_data['title'])
            if pictures_for_cinema:
                self.stdout.write(self.style.SUCCESS(f"  Adding pictures to Gallery {new_cinema_gallery.id} for {cinema_obj.title} (from static files)..."))
                for pic_data in pictures_for_cinema:
                    image_path_in_static = pic_data['image_path']
                    image_type = pic_data['image_type']
                    full_static_image_path = self._get_static_file_path(image_path_in_static)
                    if full_static_image_path:
                        with open(full_static_image_path, 'rb') as f:
                            picture_obj, created_pic = Picture.objects.get_or_create(
                                gallery=new_cinema_gallery,
                                image_type=image_type,
                                defaults={'image': File(f, name=os.path.basename(image_path_in_static))}
                            )
                            if created_pic:
                                self.stdout.write(self.style.SUCCESS(f"    Added picture '{image_path_in_static}' from static to gallery {new_cinema_gallery.id}."))
                            else:
                                self.stdout.write(self.style.WARNING(f"    Picture '{image_path_in_static}' already exists (same gallery, type). Skipping."))
                    else:
                        self.stdout.write(self.style.ERROR(f"    Static image file not found at any STATICFILES_DIRS for: {image_path_in_static}. Skipping picture creation."))
            else:
                self.stdout.write(self.style.WARNING(f"  No picture data found for cinema '{cinema_obj.title}'."))

        # ---  PaigesCinema и их Gallery/Picture ---
        self.stdout.write(self.style.SUCCESS("\nCreating PaigesCinema objects (pages like Advertisement, Kids Room, VIP Hall, etc.) and their Galleries/Pictures..."))

        for page_data in paiges_cinema_data_list:
            seo_obj_for_page = created_seo_blocks.get(page_data['seo_block_title_seo'])
            if not seo_obj_for_page:
                self.stdout.write(self.style.ERROR(f"  Block_SEO for PaigesCinema '{page_data['title']}' not found. Skipping creation."))
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
                self.stdout.write(self.style.WARNING(f"  PaigesCinema '{page_obj.title}' already exists. Updating its gallery/pictures."))

            new_page_gallery = Gallery.objects.create()
            page_obj.gallery = new_page_gallery
            page_obj.save()
            self.stdout.write(self.style.SUCCESS(f"  Created/Updated PaigesCinema: {page_obj.title} (ID: {page_obj.id}) with new Gallery (ID: {new_page_gallery.id})"))

            pictures_for_page = picture_data_pages_list.get(page_data['title'])
            if pictures_for_page:
                self.stdout.write(self.style.SUCCESS(f"  Adding pictures to Gallery {new_page_gallery.id} for {page_obj.title} (from static files)..."))
                for pic_data in pictures_for_page:
                    image_path_in_static = pic_data['image_path']
                    image_type = pic_data['image_type']
                    full_static_image_path = self._get_static_file_path(image_path_in_static)
                    if full_static_image_path:
                        with open(full_static_image_path, 'rb') as f:
                            picture_obj, created_pic = Picture.objects.get_or_create(
                                gallery=new_page_gallery,
                                image_type=image_type,
                                defaults={'image': File(f, name=os.path.basename(image_path_in_static))}
                            )
                            if created_pic:
                                self.stdout.write(self.style.SUCCESS(f"    Added picture '{image_path_in_static}' from static to gallery {new_page_gallery.id}."))
                            else:
                                self.stdout.write(self.style.WARNING(f"    Picture '{image_path_in_static}' already exists (same gallery, type). Skipping."))
                    else:
                        self.stdout.write(self.style.ERROR(f"    Static image file not found at any STATICFILES_DIRS for: {image_path_in_static}. Skipping picture creation."))
            else:
                self.stdout.write(self.style.WARNING(f"  No picture data found for PaigesCinema '{page_obj.title}'."))
