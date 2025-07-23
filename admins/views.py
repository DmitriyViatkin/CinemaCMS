from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from django.views.generic.list import ListView
from movie.models import Movies
from users.models import User,Email_campaing,Tamplate_email
from django.utils.decorators import method_decorator
from django.db.models import Prefetch
from datetime import timedelta
from django.db.models.functions import TruncMonth
from main.models import Gallery, Banners, Cross_Banner, News, PaigesNews, Promotion, PaigesCinema, MainPaiges, Contact, Block_SEO
from core.models import Cinemas, Halls, Sessions, Seats, Tickets
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import (PaigesNewsForm,PaigesCinemaForm,BlockSEOForm, MovieForm, PictureFormSet, GalleryForm, CinemaForm,
                    HallsForm,  TicketForm,SeatForm, MainPaigesForm,PromotionForm,  BannersFormSet,
                    NewsFormSet, PictureForm, UserForm, SessionFormSet , Picture, EmailCampaignForm,  CrossBannerForm , ContactFormSet)
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from .send_email import send_campaign_email
from os.path import basename
from .tasks import send_campaign_emails_task
from django.urls import reverse
import os
from django.contrib import messages
from django.core.files.base import ContentFile
@staff_member_required
def email_campaign_create(request, campaign_id=None):
    campaign_instance = None
    is_edit = False
    current_task_id = None #
    if campaign_id:
        campaign_instance = get_object_or_404(Email_campaing, pk=campaign_id)
        is_edit = True

    if request.method == 'POST':
        form = EmailCampaignForm(request.POST, request.FILES, instance=campaign_instance)



        if form.is_valid():
            email_campaign = form.save(commit=False)


            new_template_file = form.cleaned_data.get('new_template_file')
            existing_template_obj = form.cleaned_data.get('template')

            if new_template_file:
                file_name = new_template_file.name
                try:
                    template_obj = Tamplate_email.objects.get(template_file__icontains=file_name)
                    template_obj.template_file.save(file_name, new_template_file, save=True)

                except Tamplate_email.DoesNotExist:
                    template_obj = Tamplate_email()
                    template_obj.template_file.save(file_name, new_template_file, save=True)

                email_campaign.template = template_obj
            elif existing_template_obj:
                email_campaign.template = existing_template_obj

            else:
                email_campaign.template = None


            email_campaign.save()

            # --- Логика выбора получателей ---
            recipient_mode = form.cleaned_data.get('recipient_mode')
            selected_user_ids = form.cleaned_data.get('users', [])

            if recipient_mode == "selected":
                if selected_user_ids:

                    users_to_set = User.objects.filter(id__in=selected_user_ids)
                    email_campaign.users.set(users_to_set)
                else:

                    email_campaign.users.clear()
            elif recipient_mode == "all":

                all_active_users = User.objects.filter(is_active=True)
                email_campaign.users.set(all_active_users)


            email_campaign.save()

            # --- Отправка email ---
            final_users_queryset = email_campaign.users.all()
            recipient_email_list = list(
                final_users_queryset.filter(email__isnull=False).values_list('email', flat=True))

            if recipient_email_list:
                email_campaign.status = 'sending'
                email_campaign.save()  # сначала сохраняем статус

                task = send_campaign_emails_task.delay(email_campaign.id, recipient_email_list)
                return redirect(f"{reverse('email_campaign_create')}?task_id={task.task_id}")

            else:

                email_campaign.status = 'sent'
                email_campaign.save()
                # Если нет получателей, можно просто перенаправить на список или ту же страницу без task_id
                return redirect('email_campaign_list') # или redirect('email_campaign_create')


        else:  # Форма невалидна


            templates = Tamplate_email.objects.order_by('-id')[:5]
            for template_item in templates:
                template_item.short_name = basename(template_item.template_file.name)

            raw_user_ids_str = request.POST.get('users', '')
            selected_user_ids_for_template = [int(uid.strip()) for uid in raw_user_ids_str.split(',') if
                                              uid.strip().isdigit()]


            current_task_id = request.GET.get('task_id')

            context = {
                'form': form,
                'templates': templates,
                'campaign': campaign_instance,
                'is_edit': is_edit,
                'title': 'Редагувати Email Кампанію' if is_edit else 'Створити Email Кампанію',
                'selected_user_ids_for_template': selected_user_ids_for_template,
                'task_id': current_task_id,
            }
            return render(request, 'admin/email_campaigns/email_campaign_form.html', context)

    else:  # GET-запрос
        form = EmailCampaignForm(instance=campaign_instance)


        selected_user_ids_for_template = []

        if is_edit and campaign_instance.users.exists():
            if 'recipient_mode' in form.fields:
                form.fields['recipient_mode'].initial = 'selected'
            selected_user_ids_for_template = list(campaign_instance.users.all().values_list('pk', flat=True))
        else:
            if 'recipient_mode' in form.fields:
                form.fields['recipient_mode'].initial = 'all'

        if campaign_instance and campaign_instance.template:
            if 'template' in form.fields:
                form.fields['template'].initial = campaign_instance.template.pk




        current_task_id = request.GET.get('task_id')

    templates = Tamplate_email.objects.order_by('-id')[:5]
    for template_item in templates:
        template_item.short_name = basename(template_item.template_file.name)

    context = {
        'form': form,
        'templates': templates,
        'campaign': campaign_instance,
        'is_edit': is_edit,
        'title': 'Редагувати Email Кампанію' if is_edit else 'Створити Email Кампанію',
        'selected_user_ids_for_template': selected_user_ids_for_template,
        'task_id': current_task_id,
    }

    return render(request, 'admin/email_campaigns/email_campaign_form.html', context)



def campaign_list(request):
    campaigns = Email_campaing.objects.all().order_by('-created_at')
    return render(request, 'admin/email_campaigns/campaign_list.html', {'campaigns': campaigns})



@staff_member_required
def email_campaign_delete(request, campaign_id):
    """
    Видалення Email кампанії.
    """
    campaign = get_object_or_404(Email_campaing, pk=campaign_id)
    if request.method == 'POST':
        campaign.delete()

        return redirect('email_campaign_list')

    # Якщо це GET-запит (наприклад, для сторінки підтвердження видалення)
    context = {
        'campaign': campaign,
        'title': f'Видалити Email кампанію #{campaign.id}'
    }
    return render(request, 'admin/email_campaigns/email_campaign_confirm_delete.html', context)

@staff_member_required
def index(request):
    user_count = User.objects.count()
    ticket_count = Tickets.objects.count()
    movie_count = Movies.objects.count()

    today = timezone.now().date()  # Получаем текущую дату без времени
    date_from = today - timedelta(days=30)

    # --- График общих продаж по дням (уже оптимизирован) ---
    ticket_sales = (
        Tickets.objects
        .filter(session__date__range=(date_from, today))
        .values('session__date')
        .annotate(count=Count('id'))
        .order_by('session__date')
    )

    chart_labels = [item['session__date'].strftime('%Y-%m-%d') for item in ticket_sales]
    chart_data = [item['count'] for item in ticket_sales]


    cinemas_data = {cinema.id: cinema.title for cinema in Cinemas.objects.all()}


    all_dates = [date_from + timedelta(days=i) for i in range(31)]
    chart_days = [d.strftime('%Y-%m-%d') for d in all_dates]  # Для вашего контекста


    aggregated_sales = (
        Tickets.objects
        .filter(session__date__range=(date_from, today))
        .values(
            'session__cinema_id',  # ID кинотеатра
            'session__date'  # Дата сессии
        )
        .annotate(
            tickets_count=Count('id')  # Подсчет билетов
        )
        .order_by(
            'session__cinema_id',
            'session__date'
        )
    )


    cinema_sales = {title: [0] * 31 for title in cinemas_data.values()}
    temp_cinema_daily_counts = {cinema_id: {d: 0 for d in all_dates} for cinema_id in cinemas_data.keys()}

    for item in aggregated_sales:
        cinema_id = item['session__cinema_id']
        session_date = item['session__date']
        count = item['tickets_count']

        if cinema_id in temp_cinema_daily_counts and session_date in temp_cinema_daily_counts[cinema_id]:
            temp_cinema_daily_counts[cinema_id][session_date] = count

    # Переносим данные в final cinema_sales в нужном порядке
    for cinema_id, daily_data in temp_cinema_daily_counts.items():
        cinema_title = cinemas_data[cinema_id]
        daily_counts_ordered = [daily_data[d] for d in all_dates]
        cinema_sales[cinema_title] = daily_counts_ordered


    knob_data = {
        'category1': 5,
        'category2': 10,
        'category3': 20,
    }
    year_ago = today - timedelta(days=365)

    monthly_sales = (
        Tickets.objects
        .filter(session__date__gte=year_ago)
        .annotate(month=TruncMonth('session__date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    monthly_labels = [item['month'].strftime('%Y-%m') for item in monthly_sales]
    monthly_data = [item['count'] for item in monthly_sales]

    context = {
        'monthly_labels': monthly_labels,
        'monthly_data': monthly_data,
        'user_count': user_count,
        'ticket_count': ticket_count,
        'movie_count': movie_count,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'cinema_sales': cinema_sales,
        'chart_days': chart_days,
        'knob_data': knob_data,
    }

    return render(request, 'admin/index.html', context)



@staff_member_required
def new_contacts(request):
    seo_instance = Block_SEO.objects.filter(id=1).first()
    if not seo_instance:
        seo_instance = Block_SEO.objects.create(title="Контакты SEO", description="SEO описание для страницы контактов")

    if request.method == 'POST':
        block_seo_form = BlockSEOForm(request.POST, instance=seo_instance)
        formset = ContactFormSet(request.POST, request.FILES, queryset=Contact.objects.filter(seo_block=seo_instance))

        if formset.is_valid() and block_seo_form.is_valid():
            try:
                block_seo = block_seo_form.save()

                for form in formset:
                    if form.is_valid():
                        if form.cleaned_data.get('DELETE') and not form.instance.pk:
                            continue

                        contact = form.save(commit=False)
                        contact.seo_block = block_seo
                        if not contact.gallery:
                            gallery = Gallery.objects.create()
                            contact.gallery = gallery
                        contact_picture = form.cleaned_data.get('contact_picture')
                        print("contact_picture in cleaned_data:", contact_picture)
                        contact.save()

                for form in formset.deleted_forms:
                    if form.instance.pk:
                        if form.instance.gallery:
                            form.instance.gallery.delete()
                        form.instance.delete()

                return redirect('con')

            except Exception as e:
                print(f"Ошибка при сохранении контактов: {e}")
                raise e

    else:
        block_seo_form = BlockSEOForm(instance=seo_instance)
        formset = ContactFormSet(queryset=Contact.objects.filter(seo_block=seo_instance))

    return render(request, 'admin/paige_list/new_contacts.html', {
        'formset': formset,
        'block_seo_form': block_seo_form
    })


@staff_member_required
def movie_list(request):
    movies_list = Movies.objects.all().select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type="main_picture"),
            to_attr='main_pictures_prefetched'
        )
    ).order_by('title')

    paginator = Paginator(movies_list, 10)

    page = request.GET.get('page')
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)


    for movie in movies:

        if movie.gallery and movie.gallery.main_pictures_prefetched:

            movie.main_picture = movie.gallery.main_pictures_prefetched[0]
        else:
            movie.main_picture = None

    context = {'movies': movies}
    return render(request, 'admin/movies_lists/movies_lists.html', context)

@staff_member_required
def add_movie(request, movie_id=None):
    movie_instance = None
    block_seo_instance = None
    gallery_instance = None

    current_main_picture_object = None

    if movie_id:
        movie_instance = get_object_or_404(Movies, pk=movie_id)
        block_seo_instance = movie_instance.seo_block
        gallery_instance = movie_instance.gallery

        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()
            movie_instance.gallery = gallery_instance
            movie_instance.save()

        current_main_picture_object = gallery_instance.pictures.filter(image_type='main_picture').first()

    if gallery_instance is None:
        gallery_instance = Gallery.objects.create()

    if request.method=='POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        movie_form = MovieForm(request.POST, instance=movie_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)

        picture_formset = PictureFormSet(
            request.POST,
            request.FILES,
            queryset=Picture.objects.filter(gallery=gallery_instance).exclude(pk=current_main_picture_object.pk) if current_main_picture_object else Picture.objects.filter(gallery=gallery_instance),
            prefix='pictures', initial=[{'image_type': 'gallery_image'}]
        )

        main_picture_form = PictureForm(request.POST, request.FILES, instance=current_main_picture_object, prefix='main_picture_form')

        if f'{main_picture_form.prefix}-image_type' not in request.POST:
            main_picture_form.data = main_picture_form.data.copy()
            main_picture_form.data[f'{main_picture_form.prefix}-image_type'] = 'main_picture'

        if f'{main_picture_form.prefix}-gallery' not in request.POST and gallery_instance.pk:
            main_picture_form.data = main_picture_form.data.copy()
            main_picture_form.data[f'{main_picture_form.prefix}-gallery'] = gallery_instance.pk

        if (block_seo_form.is_valid() and
                movie_form.is_valid() and
                gallery_form.is_valid() and
                picture_formset.is_valid() and  #
                main_picture_form.is_valid()):

            block_seo = block_seo_form.save()
            gallery = gallery_form.save()

            movie = movie_form.save(commit=False)
            movie.seo_block = block_seo
            movie.gallery = gallery
            movie.save()

            if main_picture_form.cleaned_data.get('image'):
                main_picture = main_picture_form.save(commit=False)
                main_picture.gallery = gallery
                main_picture.image_type = 'main_picture'
                main_picture.save()

                if current_main_picture_object and current_main_picture_object.pk!=main_picture.pk:
                    current_main_picture_object.delete()

            elif main_picture_form.cleaned_data.get('DELETE') and current_main_picture_object:
                current_main_picture_object.delete()

            instances = picture_formset.save(commit=False)
            for picture in instances:
                if not picture.pk:
                    picture.gallery = gallery
                    if not picture.image_type:
                        picture.image_type = 'gallery_image'
                picture.save()

            for picture in picture_formset.deleted_objects:
                picture.delete()

            return redirect('movie_list')

        else:



            return render(request, 'admin/movies_lists/add_movies.html', {
                'block_seo_form': block_seo_form,
                'movie_form': movie_form,
                'gallery_form': gallery_form,
                'picture_formset': picture_formset,
                'main_picture_form': main_picture_form,
                'movie': movie_instance,
                'is_edit': movie_instance is not None,
            })


    else:
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        movie_form = MovieForm(instance=movie_instance)
        gallery_form = GalleryForm(instance=gallery_instance)

        picture_formset = PictureFormSet(
            queryset=Picture.objects.filter(gallery=gallery_instance).exclude(pk=current_main_picture_object.pk)
            if current_main_picture_object else Picture.objects.filter(gallery=gallery_instance),
            prefix='pictures'
        )

        main_picture_form = PictureForm(
            instance=current_main_picture_object,
            prefix='main_picture_form',
            initial={'image_type': 'main_picture'}
        )

    return render(request, 'admin/movies_lists/add_movies.html', {
        'block_seo_form': block_seo_form,
        'movie_form': movie_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'main_picture_form': main_picture_form,
        'movie': movie_instance,
        'is_edit': movie_instance is not None,
    })


@staff_member_required
def delete_movie(request, pk):
    movie = get_object_or_404(Movies, pk=pk)
    movie.delete()
    return redirect('movie_list')

@staff_member_required
def cinema_list(request):
    cinemas_list = Cinemas.objects.select_related('gallery','seo_block' ).prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='logo'),
            to_attr='logos'
        )
    ).order_by('title')
    paginator = Paginator(cinemas_list, 10)
    page_number = request.GET.get('page')
    cinemas = paginator.get_page(page_number)
    return render(request, 'admin/cinema/cinema_list.html', {'cinemas': cinemas})

@staff_member_required
def add_cinema_create(request, cinema_id=None):
    cinema_instance = None
    block_seo_instance = None
    gallery_instance = None
    halls = []

    current_main_picture_object = None
    current_logo_picture_object = None

    if cinema_id:
        cinema_instance = get_object_or_404(Cinemas, pk=cinema_id)
        block_seo_instance = cinema_instance.seo_block
        gallery_instance = cinema_instance.gallery
        halls = Halls.objects.filter(cinema=cinema_instance).order_by('title')

        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()
            cinema_instance.gallery = gallery_instance
            cinema_instance.save()

        if gallery_instance:
            current_main_picture_object = gallery_instance.pictures.filter(image_type='main_picture').first()
            current_logo_picture_object = gallery_instance.pictures.filter(image_type='logo').first()

    if request.method == 'POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        cinema_form = CinemaForm(request.POST, instance=cinema_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)

        banner_form = PictureForm(request.POST, request.FILES, instance=current_main_picture_object, prefix='banner_form')
        logo_form = PictureForm(request.POST, request.FILES, instance=current_logo_picture_object, prefix='logo_form')

        picture_queryset_for_formset = Picture.objects.none()
        if gallery_instance:
            picture_queryset_for_formset = gallery_instance.pictures.exclude(
                image_type__in=['main_picture', 'logo']
            ).order_by('pk')

        picture_formset = PictureFormSet(
            request.POST, request.FILES,
            queryset=picture_queryset_for_formset,
            prefix='pictures'
        )

        if (block_seo_form.is_valid() and cinema_form.is_valid() and gallery_form.is_valid() and
                picture_formset.is_valid() and banner_form.is_valid() and logo_form.is_valid()):

            block_seo = block_seo_form.save()
            gallery = gallery_form.save()

            cinema = cinema_form.save(commit=False)
            cinema.seo_block = block_seo
            cinema.gallery = gallery
            cinema.save()

            # Обробка банера
            if banner_form.cleaned_data.get('image'):
                banner_picture = banner_form.save(commit=False)
                banner_picture.gallery = gallery
                banner_picture.image_type = 'main_picture'
                banner_picture.save()
                if current_main_picture_object and current_main_picture_object.pk != banner_picture.pk:
                    current_main_picture_object.delete()
            elif banner_form.cleaned_data.get('DELETE') and current_main_picture_object:
                current_main_picture_object.delete()

            # Обробка лого
            if logo_form.cleaned_data.get('image'):
                logo_picture = logo_form.save(commit=False)
                logo_picture.gallery = gallery
                logo_picture.image_type = 'logo'
                logo_picture.save()
                if current_logo_picture_object and current_logo_picture_object.pk != logo_picture.pk:
                    current_logo_picture_object.delete()
            elif logo_form.cleaned_data.get('DELETE') and current_logo_picture_object:
                current_logo_picture_object.delete()

            # Збереження formset
            instances_gallery = picture_formset.save(commit=False)
            for pic_instance in instances_gallery:
                if not pic_instance.pk:
                    pic_instance.gallery = gallery
                    if not pic_instance.image_type:
                        pic_instance.image_type = 'gallery_image'
                pic_instance.save()

            for picture_to_delete in picture_formset.deleted_objects:
                picture_to_delete.delete()

            return redirect('cinema_lists')

        else:


            return render(request, 'admin/cinema/add_cinema.html', {
                'block_seo_form': block_seo_form,
                'cinema_form': cinema_form,
                'gallery_form': gallery_form,
                'picture_formset': picture_formset,
                'banner_form': banner_form,
                'logo_form': logo_form,
                'cinema': cinema_instance,
                'halls': halls,
                'is_edit': cinema_instance is not None,
            })

    else:
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        cinema_form = CinemaForm(instance=cinema_instance)
        gallery_form = GalleryForm(instance=gallery_instance)

        picture_queryset_for_formset = Picture.objects.none()
        if gallery_instance:
            picture_queryset_for_formset = gallery_instance.pictures.exclude(
                image_type__in=['main_picture', 'logo']
            ).order_by('pk')

        picture_formset = PictureFormSet(queryset=picture_queryset_for_formset, prefix='pictures')

        banner_form = PictureForm(
            instance=current_main_picture_object,
            prefix='banner_form',
            initial={'image_type': 'main_picture'}
        )
        logo_form = PictureForm(
            instance=current_logo_picture_object,
            prefix='logo_form',
            initial={'image_type': 'logo'}
        )

    return render(request, 'admin/cinema/add_cinema.html', {
        'block_seo_form': block_seo_form,
        'cinema_form': cinema_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'banner_form': banner_form,
        'logo_form': logo_form,
        'cinema': cinema_instance,
        'halls': halls,
        'is_edit': cinema_instance is not None,
    })


@staff_member_required
def delete_cinema(request, pk):
    cinema = get_object_or_404(Cinemas, pk=pk)
    cinema.delete()
    return redirect('cinema_lists')

@staff_member_required
def halls_list(request):

        halls_list = Halls.objects.all()

        paginator = Paginator(halls_list, 10)
        page = request.GET.get('page')
        try:
            halls = paginator.page(page)
        except PageNotAnInteger:
            halls = paginator.page(1)
        except EmptyPage:
            halls = paginator.page(paginator.num_pages)

        context = {'halls': halls}
        return render(request, 'admin/halls/halls_lists.html', context)

@staff_member_required
def add_halls_create(request, cinema_pk, halls_id=None):
    cinema_instance = get_object_or_404(Cinemas, pk=cinema_pk)
    halls_instance = None
    block_seo_instance = None
    gallery_instance = None
    current_main_picture_object = None

    if halls_id:
        halls_instance = get_object_or_404(Halls, pk=halls_id, cinema=cinema_instance)
        block_seo_instance = halls_instance.seo_block
        gallery_instance = halls_instance.gallery

        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()
            halls_instance.gallery = gallery_instance
            halls_instance.save()

        current_main_picture_object = gallery_instance.pictures.filter(
            image_type='main_picture'
        ).first()

    if request.method == 'POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        halls_form = HallsForm(request.POST, request.FILES, instance=halls_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)
        banner_form = PictureForm(
            request.POST, request.FILES,
            instance=current_main_picture_object,
            prefix='banner_form'
        )


        picture_formset = PictureFormSet(
            request.POST, request.FILES,
            prefix='pictures'
        )

        if (block_seo_form.is_valid() and
            halls_form.is_valid() and
            gallery_form.is_valid() and
            picture_formset.is_valid() and
            banner_form.is_valid()
        ):
            block_seo = block_seo_form.save()
            gallery = gallery_form.save()

            halls = halls_form.save(commit=False)
            halls.seo_block = block_seo
            halls.gallery = gallery
            halls.cinema = cinema_instance
            halls.save()

            # Обробка головного зображення (банера)
            if banner_form.cleaned_data.get('image'):
                banner_picture = banner_form.save(commit=False)
                banner_picture.gallery = gallery
                banner_picture.image_type = 'main_picture'
                banner_picture.save()

                if current_main_picture_object and current_main_picture_object.pk != banner_picture.pk:
                    current_main_picture_object.delete()

            elif banner_form.cleaned_data.get('DELETE') and current_main_picture_object:
                current_main_picture_object.delete()

            # Обробка formset (галерея)
            instances_gallery = picture_formset.save(commit=False)
            for pic_instance in instances_gallery:
                if not pic_instance.pk:
                    pic_instance.gallery = gallery
                    if not pic_instance.image_type:
                        pic_instance.image_type = 'gallery_image'
                pic_instance.save()

            for picture_to_delete in picture_formset.deleted_objects:
                picture_to_delete.delete()

            return redirect('add_cinema_edit', cinema_id=cinema_pk)



    else:
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        halls_form = HallsForm(instance=halls_instance)
        gallery_form = GalleryForm(instance=gallery_instance)

        picture_queryset_for_formset = Picture.objects.none()
        if gallery_instance:
            picture_queryset_for_formset = gallery_instance.pictures.filter(
                image_type__in=['gallery_image', 'gallery']
            ).order_by('pk')

        picture_formset = PictureFormSet(
            queryset=picture_queryset_for_formset,
            prefix='pictures'
        )

        banner_form = PictureForm(
            instance=current_main_picture_object,
            prefix='banner_form',
            initial={'image_type': 'main_picture'}
        )

    return render(request, 'admin/halls/add_halls.html', {
        'block_seo_form': block_seo_form,
        'halls_form': halls_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'banner_form': banner_form,
        'halls': halls_instance,
        'cinema': cinema_instance,
        'is_edit': halls_instance is not None,
    })

@staff_member_required
def delete_halls(request, pk):
    hall_to_delete = get_object_or_404(Halls, pk=pk)
    cinema_id = hall_to_delete.cinema.pk
    hall_to_delete.delete()

    return redirect('add_cinema_edit', cinema_id=cinema_id)

def add_banners(request):

    banner_queryset = Banners.objects.select_related('gallery').prefetch_related(
        Prefetch('gallery__pictures', queryset=Picture.objects.filter(image_type='main_picture'))
    )
    banner_formset = BannersFormSet(
        request.POST or None,
        request.FILES or None,
        queryset=banner_queryset,
        prefix='top_banners'
    )

    news_queryset = News.objects.select_related('gallery').prefetch_related(
        Prefetch('gallery__pictures', queryset=Picture.objects.filter(image_type='main_picture'))
    )
    news_formset = NewsFormSet(
        request.POST or None,
        request.FILES or None,
        queryset=news_queryset,
        prefix='news'
    )


    cross_banner_instance = Cross_Banner.objects.select_related('gallery').prefetch_related(
        Prefetch('gallery__pictures', queryset=Picture.objects.all())
    ).first()

    cross_banner_form = CrossBannerForm(
        request.POST or None,
        request.FILES or None,
        instance=cross_banner_instance,
        prefix='cross_banner'
    )


    cross_banner_image_url = None
    if cross_banner_instance and cross_banner_instance.gallery:

        picture = next((p for p in cross_banner_instance.gallery.pictures.all() if p.image), None)
        if picture:
            cross_banner_image_url = picture.image.url

    if request.method == 'POST':
        which_form = request.POST.get("which_form_is_it")

        if which_form == "this_is_form_banner":
            if banner_formset.is_valid():
                pictures_data = []

                for form in banner_formset.forms:
                    if not form.cleaned_data:
                        continue

                    banner = form.instance
                    main_picture_file = form.cleaned_data.get('main_picture')

                    # 🛡 Збережемо копію вмісту файлу, щоб не втратити
                    if main_picture_file:
                        file_copy = ContentFile(main_picture_file.read())
                        file_copy.name = main_picture_file.name
                        pictures_data.append((banner, file_copy))
                    else:
                        pictures_data.append((banner, None))

                banner_formset.save()

                for banner, main_picture_file in pictures_data:
                    if banner and not banner.gallery:
                        banner.gallery = Gallery.objects.create()
                        banner.save()

                    if banner.gallery and main_picture_file:
                        picture = Picture.objects.filter(
                            gallery=banner.gallery, image_type='main_picture'
                        ).first()

                        if not picture:
                            picture = Picture(gallery=banner.gallery, image_type='main_picture')

                        picture.image = main_picture_file
                        picture.save()
                return redirect('add_banners')


        elif which_form == "this_is_form_cross_banner":

            if cross_banner_form.is_valid():

                cross_banner = cross_banner_form.save(commit=False)

                if not cross_banner.gallery:
                    cross_banner.gallery = Gallery.objects.create()

                cross_banner.save()
                picture = Picture.objects.filter(gallery=cross_banner.gallery).first()

                if not picture:
                    picture = Picture(gallery=cross_banner.gallery)

                # Обработка загруженного файла изображения

                image_file = request.FILES.get('cross_banner-image')

                if image_file:
                    picture.image = image_file
                    picture.image_type = 'gallery'
                    picture.save()
                    image_mime_type = image_file.content_type
                    file_extension = os.path.splitext(image_file.name)[1]
                return redirect('add_banners')


        elif which_form == "this_is_form_news":

            if news_formset.is_valid():

                pictures_data = []

                for form in news_formset.forms:

                    if not form.cleaned_data:
                        continue

                    news = form.instance

                    main_picture_file = form.cleaned_data.get('main_picture')

                    # 🛡 Безпечне копіювання файлу

                    if main_picture_file:

                        file_copy = ContentFile(main_picture_file.read())

                        file_copy.name = main_picture_file.name

                        pictures_data.append((news, file_copy))

                    else:

                        pictures_data.append((news, None))

                news_formset.save()

                for news, main_picture_file in pictures_data:

                    if news and not news.gallery:
                        news.gallery = Gallery.objects.create()

                        news.save()

                    if news.gallery and main_picture_file:

                        picture = Picture.objects.filter(

                            gallery=news.gallery, image_type='main_picture'

                        ).first()

                        if not picture:
                            picture = Picture(gallery=news.gallery, image_type='main_picture')

                        picture.image = main_picture_file

                        picture.save()

                return redirect('add_banners')


    def get_main_picture_url(gallery):
        if gallery and hasattr(gallery, 'pictures'):

            picture = next((p for p in gallery.pictures.all() if p.image), None)
            if picture:
                return picture.image.url
        return None


    form_data = [{'form': form, 'image_url': get_main_picture_url(form.instance.gallery)} for form in banner_formset.forms]
    news_form_data = [{'form': form, 'image_url': get_main_picture_url(form.instance.gallery)} for form in news_formset.forms]

    return render(request, 'admin/banner/add_banner.html', {
        'formset': banner_formset,
        'form_data': form_data,
        'cross_banner_form': cross_banner_form,
        'cross_banner_image_url': cross_banner_image_url, # Передаємо попередньо обчислений URL
        'news_formset': news_formset,
        'news_form_data': news_form_data,
    })


@staff_member_required
def delete_banners(request, banners_id):
     banner = get_object_or_404(Banners, pk=banners_id)
     if request.method == 'POST':
         banner.delete()

     return redirect('banners')

@method_decorator(staff_member_required, name='dispatch')
class User_List_generic(ListView):
    model=User
    paginate_by = 50
    context_object_name = 'users'
    template_name = 'admin/user/user_lists.html'
    def get_queryset(self):
        queryset=super().get_queryset()
        return queryset
    def get_context_data( self, **kwargs ):
        context=super().get_context_data(**kwargs)
        return context



@staff_member_required
def add_user(request, user_id=None):
    user_instance = None
    is_edit = False

    if user_id:

        user_instance = get_object_or_404(User, pk=user_id)
        is_edit = True


    if request.method == 'POST':

        form = UserForm(request.POST, instance=user_instance)


        if form.is_valid():

            form.save()

            return redirect('users')

    else:
        form = UserForm(instance=user_instance)
    return render(request, 'admin/user/add_user.html', {
        'form': form,
        'user_instance': user_instance,
        'is_edit': is_edit,
    })

@staff_member_required
def delete_user(request, users_id):
    user = get_object_or_404(User, pk=users_id)

    if request.method == 'POST':
        user.delete()
        return redirect('users')
    else: #
        return redirect('users')

@staff_member_required
def news_paige(request):
    news_list_all = PaigesNews.objects.all()
    paginator = Paginator(news_list_all, 10)
    page_number = request.GET.get('page')

    try:
        news_page = paginator.page(page_number)
    except PageNotAnInteger:
        news_page = paginator.page(1)
    except EmptyPage:
        news_page = paginator.page(paginator.num_pages)
    context = {'news': news_page}
    return render(request, 'admin/news_paige/news_lists.html', context)

@staff_member_required
def news_paige_add(request, news_id=None):
    news_instance = None
    block_seo_instance = None
    gallery_instance = None

    current_main_picture_object = None

    if news_id:
        news_instance = get_object_or_404(PaigesNews, pk=news_id)
        block_seo_instance = news_instance.seo_block
        gallery_instance = news_instance.gallery

        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()
            news_instance.gallery = gallery_instance
            news_instance.save()


        current_main_picture_object = gallery_instance.pictures.filter(image_type='main_picture').first()


    if gallery_instance is None:
        gallery_instance = Gallery.objects.create()  # Создаем новую галерею


    if request.method=='POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        news_form = PaigesNewsForm(request.POST, instance=news_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)

        # Для modelformset_factory, queryset нужен и для POST (чтобы Django знал, какие объекты обновлять)
        picture_formset = PictureFormSet(
            request.POST,
            request.FILES,
            queryset=Picture.objects.filter(gallery=gallery_instance).exclude(pk=current_main_picture_object.pk) if current_main_picture_object else Picture.objects.filter(gallery=gallery_instance),
            prefix='pictures', initial=[{'image_type': 'gallery_image'}]
        )

        main_picture_form = PictureForm(request.POST, request.FILES, instance=current_main_picture_object, prefix='main_picture_form')


        if f'{main_picture_form.prefix}-image_type' not in request.POST:
            main_picture_form.data = main_picture_form.data.copy()
            main_picture_form.data[f'{main_picture_form.prefix}-image_type'] = 'main_picture'

        if f'{main_picture_form.prefix}-gallery' not in request.POST and gallery_instance.pk:
            main_picture_form.data = main_picture_form.data.copy()
            main_picture_form.data[f'{main_picture_form.prefix}-gallery'] = gallery_instance.pk



        if (block_seo_form.is_valid() and
                news_form.is_valid() and
                gallery_form.is_valid() and
                picture_formset.is_valid() and  #
                main_picture_form.is_valid()):

            block_seo_saved = block_seo_form.save()
            gallery_saved = gallery_form.save()

            news_saved = news_form.save(commit=False)
            news_saved.seo_block = block_seo_saved
            news_saved.gallery = gallery_saved
            news_saved.save()


            if main_picture_form.cleaned_data.get('image'):
                main_picture_saved = main_picture_form.save(commit=False)
                main_picture_saved.gallery = gallery_saved
                main_picture_saved.image_type = 'main_picture'
                main_picture_saved.save()

                if current_main_picture_object and current_main_picture_object.pk!=main_picture_saved.pk:
                    current_main_picture_object.delete()

            elif main_picture_form.cleaned_data.get('DELETE') and current_main_picture_object:
                current_main_picture_object.delete()


            instances = picture_formset.save(commit=False)
            for picture in instances:
                if not picture.pk:
                    picture.gallery = gallery_saved
                    if not picture.image_type:
                        picture.image_type = 'gallery_image'
                picture.save()


            for picture in picture_formset.deleted_objects:
                picture.delete()

            return redirect('news')

        else:



            return render(request, 'admin/news_paige/add_news.html', {
                'block_seo_form': block_seo_form,
                'news_form': news_form,
                'gallery_form': gallery_form,
                'picture_formset': picture_formset,
                'main_picture_form': main_picture_form,
                'news': news_instance,
                'is_edit': news_instance is not None,
            })


    else:
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        news_form = PaigesNewsForm(instance=news_instance)
        gallery_form = GalleryForm(instance=gallery_instance)


        picture_formset = PictureFormSet(
            queryset=Picture.objects.filter(gallery=gallery_instance).exclude(pk=current_main_picture_object.pk) if current_main_picture_object else Picture.objects.filter(gallery=gallery_instance),
            prefix='pictures'
        )

        main_picture_form = PictureForm(
            instance=current_main_picture_object,
            prefix='main_picture_form',
            initial={'image_type': 'main_picture'}  # Initial для новой формы главной картинки
        )

    return render(request, 'admin/news_paige/add_news.html', {
        'block_seo_form': block_seo_form,
        'news_form': news_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'main_picture_form': main_picture_form,
        'news': news_instance,
        'is_edit': news_instance is not None,
    })


@staff_member_required
def news_paige_delete(request, news_id):
    news = get_object_or_404(PaigesNews, pk=news_id)
    if request.method=='POST':
        news.delete()

    return redirect('news')

@staff_member_required
def promotion_paige(request):
    promotion_list_all = Promotion.objects.all().order_by('-date')
    paginator = Paginator(promotion_list_all, 10)
    page_number = request.GET.get('page')
    print(promotion_list_all)

    try:
        promotion_page = paginator.page(page_number)
    except PageNotAnInteger:
        promotion_page = paginator.page(1)
    except EmptyPage:
        promotion_page = paginator.page(paginator.num_pages)
    context = {'promotions': promotion_page}
    return render(request, 'admin/promotion/promotion_list.html', context)

@staff_member_required
def promotion_paige_add(request, promotion_id=None):
    promotion_instance = None
    block_seo_instance = None
    gallery_instance = None
    current_main_picture_object = None

    # Отримання існуючої акції
    if promotion_id:
        promotion_instance = get_object_or_404(Promotion, pk=promotion_id)
        block_seo_instance = promotion_instance.seo_block
        gallery_instance = promotion_instance.gallery

    # Створення галереї, якщо відсутня
    if not gallery_instance:
        gallery_instance = Gallery.objects.create()
        if promotion_instance:
            promotion_instance.gallery = gallery_instance
            promotion_instance.save()

    # Отримання головного зображення
    current_main_picture_object = gallery_instance.pictures.filter(image_type='main_picture').first()

    if request.method == 'POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        promotion_form = PromotionForm(request.POST, instance=promotion_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)

        picture_queryset = gallery_instance.pictures.exclude(pk=current_main_picture_object.pk) if current_main_picture_object else gallery_instance.pictures.all()

        picture_formset = PictureFormSet(
            request.POST,
            request.FILES,
            queryset=picture_queryset,
            prefix='pictures'
        )

        main_picture_form = PictureForm(
            request.POST,
            request.FILES,
            instance=current_main_picture_object,
            prefix='main_picture_form'
        )

        # Встановлюємо image_type вручну, якщо не передано
        if f'{main_picture_form.prefix}-image_type' not in request.POST:
            main_picture_form.data = main_picture_form.data.copy()
            main_picture_form.data[f'{main_picture_form.prefix}-image_type'] = 'main_picture'

        # Прив'язуємо галерею, якщо не передано
        if f'{main_picture_form.prefix}-gallery' not in request.POST and gallery_instance.pk:
            main_picture_form.data = main_picture_form.data.copy()
            main_picture_form.data[f'{main_picture_form.prefix}-gallery'] = gallery_instance.pk

        if (block_seo_form.is_valid() and
            promotion_form.is_valid() and
            gallery_form.is_valid() and
            picture_formset.is_valid() and
            main_picture_form.is_valid()):

            block_seo_saved = block_seo_form.save()
            gallery_saved = gallery_form.save()

            promotion_saved = promotion_form.save(commit=False)
            promotion_saved.seo_block = block_seo_saved
            promotion_saved.gallery = gallery_saved
            promotion_saved.save()

            # Збереження головного зображення
            if main_picture_form.cleaned_data.get('image'):
                main_picture_saved = main_picture_form.save(commit=False)
                main_picture_saved.gallery = gallery_saved
                main_picture_saved.image_type = 'main_picture'
                main_picture_saved.save()

                if current_main_picture_object and current_main_picture_object.pk != main_picture_saved.pk:
                    current_main_picture_object.delete()
            elif main_picture_form.cleaned_data.get('DELETE') and current_main_picture_object:
                current_main_picture_object.delete()

            # Збереження решти зображень
            instances = picture_formset.save(commit=False)
            for picture in instances:
                if not picture.pk:
                    picture.gallery = gallery_saved
                    if not picture.image_type:
                        picture.image_type = 'gallery_image'
                picture.save()

            for picture in picture_formset.deleted_objects:
                picture.delete()

            return redirect('promotion')



    else:
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        promotion_form = PromotionForm(instance=promotion_instance)
        gallery_form = GalleryForm(instance=gallery_instance)

        picture_queryset = gallery_instance.pictures.exclude(pk=current_main_picture_object.pk) if current_main_picture_object else gallery_instance.pictures.all()

        picture_formset = PictureFormSet(
            queryset=picture_queryset,
            prefix='pictures'
        )

        main_picture_form = PictureForm(
            instance=current_main_picture_object,
            prefix='main_picture_form',
            initial={'image_type': 'main_picture'}
        )

    return render(request, 'admin/promotion/add_promotion.html', {
        'block_seo_form': block_seo_form,
        'promotion_form': promotion_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'main_picture_form': main_picture_form,
        'promotion': promotion_instance,
        'is_edit': promotion_instance is not None,
    })

@staff_member_required
def promotion_paige_delete(request, promotion_id):
    promotion = get_object_or_404(Promotion, pk=promotion_id)
    if request.method=='POST':
        promotion.delete()

    return redirect('promotion')


# Viev Paige

@staff_member_required
def paige(request):
    paige_list_all = PaigesCinema.objects.all()
    paginator = Paginator(paige_list_all, 10)
    page_number = request.GET.get('page')

    try:
        paige_page = paginator.page(page_number)
    except PageNotAnInteger:

        paige_page = paginator.page(1)
    except EmptyPage:

        paige_page = paginator.page(paginator.num_pages)

    main_paige_data = MainPaiges.objects.first()

    contact_data = Contact.objects.first()

    context = {
        'paiges': paige_page,
        'main_paige': main_paige_data,
        'contact': contact_data,
    }
    return render(request, 'admin/paige_list/paige_lists.html', context)

@staff_member_required
def  main_paige (request, paige_id=None):
    paige_instance = None
    block_seo_instance = None

    if paige_id:
        paige_instance = get_object_or_404(MainPaiges, pk=paige_id)
        block_seo_instance = paige_instance.seo_block

    if request.method=='POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        paige_form = MainPaigesForm(request.POST, instance=paige_instance)

        if  block_seo_form.is_valid() and paige_form.is_valid()  :

            block_seo  = block_seo_form.save()
            paige = paige_form.save(commit=False)
            paige.seo_block = block_seo
            paige.save()
            return redirect('paige')

        else:


            return render(request, 'admin/paige_list/main_paige.html', {
                'block_seo_form': block_seo_form,
                'paige_form': paige_form,
                'is_edit': paige_instance is not None,
            })


    else:
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        paige_form = MainPaigesForm(instance=paige_instance)



    return render(request,  'admin/paige_list/main_paige.html', {
        'block_seo_form': block_seo_form,
        'paige_form': paige_form,

        'is_edit': paige_instance is not None,
    })

@staff_member_required
def  paige_add (request, paige_id=None):
    print(f"DEBUG: Entering paige_add view. paige_id: {paige_id}")

    paige_instance = None
    block_seo_instance = None
    gallery_instance = None

    current_main_picture_object = None

    if paige_id:
        print(f"DEBUG: paige_id provided: {paige_id}. Attempting to fetch instances.")
        try:
            paige_instance = get_object_or_404(PaigesCinema, pk=paige_id)
            block_seo_instance = paige_instance.seo_block
            gallery_instance = paige_instance.gallery
            print(
                f"DEBUG: Found paige_instance: {paige_instance.pk}, seo_block: {block_seo_instance.pk if block_seo_instance else 'None'}, gallery: {gallery_instance.pk if gallery_instance else 'None'}")

            if gallery_instance is None:
                print("DEBUG: paige_instance has no gallery. Creating one.")
                gallery_instance = Gallery.objects.create()
                paige_instance.gallery = gallery_instance
                paige_instance.save()
                messages.info(request, "A new gallery was created and linked to this page.")
                print(f"DEBUG: New gallery created and linked: {gallery_instance.pk}")

            current_main_picture_object = gallery_instance.pictures.filter(image_type='main_picture').first()
            print(
                f"DEBUG: current_main_picture_object: {current_main_picture_object.pk if current_main_picture_object else 'None'}")
        except Exception as e:
            print(f"DEBUG: Error fetching instances for paige_id {paige_id}: {e}")
            messages.error(request, f"Error loading page for editing: {e}")
            return redirect('paige')  # Redirect to avoid further errors

    if gallery_instance is None:
        print("DEBUG: No gallery instance found or provided. Creating a new one.")
        gallery_instance = Gallery.objects.create()  # Создаем новую галерею
        messages.info(request, "A new gallery was initialized for this new page.")
        print(f"DEBUG: Created new gallery: {gallery_instance.pk}")

    if request.method == 'POST':
        print("DEBUG: Request method is POST.")
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        paige_form = PaigesCinemaForm(request.POST, instance=paige_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)

        # Filter queryset for picture_formset
        picture_queryset = Picture.objects.filter(gallery=gallery_instance)
        if current_main_picture_object:
            picture_queryset = picture_queryset.exclude(pk=current_main_picture_object.pk)

        picture_formset = PictureFormSet(
            request.POST,
            request.FILES,
            queryset=picture_queryset,
            prefix='pictures',
            initial=[{'image_type': 'gallery'}]  # Corrected from 'gallery_image' to 'gallery' if that's your type
        )
        print(f"DEBUG: Initial picture_formset queryset count: {picture_queryset.count()}")

        main_picture_form = PictureForm(request.POST, request.FILES, instance=current_main_picture_object,
                                        prefix='main_picture_form')

        # Debugging form data manipulation for main_picture_form
        if f'{main_picture_form.prefix}-image_type' not in request.POST:
            print(f"DEBUG: Setting image_type for main_picture_form data.")
            main_picture_form.data = main_picture_form.data.copy()
            main_picture_form.data[f'{main_picture_form.prefix}-image_type'] = 'main_picture'
        else:
            print(
                f"DEBUG: image_type already in main_picture_form data: {request.POST.get(f'{main_picture_form.prefix}-image_type')}")

        if f'{main_picture_form.prefix}-gallery' not in request.POST and gallery_instance.pk:
            print(f"DEBUG: Setting gallery for main_picture_form data.")
            main_picture_form.data = main_picture_form.data.copy()
            main_picture_form.data[f'{main_picture_form.prefix}-gallery'] = gallery_instance.pk
        else:
            print(
                f"DEBUG: gallery already in main_picture_form data or gallery_instance has no PK: {request.POST.get(f'{main_picture_form.prefix}-gallery') if request.POST.get(f'{main_picture_form.prefix}-gallery') else 'Not set/No PK'}")

        print(f"DEBUG: Validating forms...")
        print(f"  block_seo_form valid: {block_seo_form.is_valid()} Errors: {block_seo_form.errors}")
        print(f"  paige_form valid: {paige_form.is_valid()} Errors: {paige_form.errors}")
        print(f"  gallery_form valid: {gallery_form.is_valid()} Errors: {gallery_form.errors}")
        print(
            f"  picture_formset valid: {picture_formset.is_valid()} Errors: {picture_formset.errors} Formset non_form_errors: {picture_formset.non_form_errors()}")
        for i, form in enumerate(picture_formset):
            print(f"    Picture form {i} valid: {form.is_valid()} Errors: {form.errors}")
        print(f"  main_picture_form valid: {main_picture_form.is_valid()} Errors: {main_picture_form.errors}")

        if (block_seo_form.is_valid() and
                paige_form.is_valid() and
                gallery_form.is_valid() and
                picture_formset.is_valid() and
                main_picture_form.is_valid()):

            print("DEBUG: All forms are valid. Saving data.")
            block_seo = block_seo_form.save()
            gallery = gallery_form.save()

            paige = paige_form.save(commit=False)
            paige.seo_block = block_seo
            paige.gallery = gallery
            paige.save()
            print(f"DEBUG: PaigesCinema saved: {paige.pk}")

            if main_picture_form.cleaned_data.get('image'):
                print("DEBUG: Main picture image provided. Saving main picture.")
                main_picture = main_picture_form.save(commit=False)
                main_picture.gallery = gallery
                main_picture.image_type = 'main_picture'  # Ensure this is always set correctly
                main_picture.save()
                print(f"DEBUG: Main picture saved: {main_picture.pk}")

                if current_main_picture_object and current_main_picture_object.pk != main_picture.pk:
                    print(f"DEBUG: Deleting old main picture: {current_main_picture_object.pk}")
                    current_main_picture_object.delete()
                    messages.info(request, "Old main picture replaced.")
            elif main_picture_form.cleaned_data.get('DELETE') and current_main_picture_object:
                print(f"DEBUG: Main picture marked for deletion. Deleting: {current_main_picture_object.pk}")
                current_main_picture_object.delete()
                messages.info(request, "Main picture deleted.")
            else:
                print("DEBUG: No main picture image provided or marked for deletion.")

            instances = picture_formset.save(commit=False)
            print(f"DEBUG: Processing {len(instances)} gallery picture instances.")
            for picture in instances:
                if not picture.pk:  # New picture
                    print(f"DEBUG: Saving new gallery picture: {picture.image.name if picture.image else 'No image'}")
                    picture.gallery = gallery
                    if not picture.image_type:
                        picture.image_type = 'gallery'  # Ensure this is 'gallery' as per your type
                    picture.save()
                else:  # Existing picture, updated
                    print(
                        f"DEBUG: Updating existing gallery picture: {picture.pk} ({picture.image.name if picture.image else 'No image'})")
                    picture.save()  # Save if it was an existing instance that was modified
            messages.success(request, f"Gallery pictures saved/updated.")

            for picture in picture_formset.deleted_objects:
                print(f"DEBUG: Deleting gallery picture: {picture.pk}")
                picture.delete()
                messages.info(request, f"Gallery picture {picture.pk} deleted.")

            messages.success(request, "Page saved successfully!")
            return redirect('paige')  # Ensure 'paige' is the correct URL name

        else:
            print("DEBUG: One or more forms are NOT valid. Re-rendering form with errors.")
            messages.error(request, "Please correct the errors in the form.")
            return render(request, 'admin/paige_list/add_paige.html', {
                'block_seo_form': block_seo_form,
                'paige_form': paige_form,
                'gallery_form': gallery_form,
                'picture_formset': picture_formset,
                'main_picture_form': main_picture_form,
                'paige': paige_instance,
                'is_edit': paige_instance is not None,
            })

    else:  # GET request
        print("DEBUG: Request method is GET.")
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        paige_form = PaigesCinemaForm(instance=paige_instance)
        gallery_form = GalleryForm(instance=gallery_instance)

        # Filter queryset for picture_formset for GET request
        picture_queryset = Picture.objects.filter(gallery=gallery_instance)
        if current_main_picture_object:
            picture_queryset = picture_queryset.exclude(pk=current_main_picture_object.pk)

        picture_formset = PictureFormSet(
            queryset=picture_queryset,
            prefix='pictures'
        )
        print(f"DEBUG: GET: Initial picture_formset queryset count: {picture_queryset.count()}")

        main_picture_form = PictureForm(
            instance=current_main_picture_object,
            prefix='main_picture_form',
            initial={'image_type': 'main_picture'}
        )
        print(
            f"DEBUG: GET: main_picture_form instance: {current_main_picture_object.pk if current_main_picture_object else 'None'}")

    print("DEBUG: Rendering template.")
    return render(request, 'admin/paige_list/add_paige.html', {
        'block_seo_form': block_seo_form,
        'paige_form': paige_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'main_picture_form': main_picture_form,
        'paige': paige_instance,
        'is_edit': paige_instance is not None,
    })

@staff_member_required
def  paige_delete(request, paige_id):
    news = get_object_or_404(PaigesCinema, pk=paige_id)
    if request.method=='POST':
        news.delete()

    return redirect('paige')