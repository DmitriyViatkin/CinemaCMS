from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from movie.models import Movies
from users.models import User,Email_campaing,Tamplate_email

from django.db.models import Prefetch

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

@staff_member_required
def email_campaign_create(request, campaign_id=None):
    campaign_instance = None
    is_edit = False
    current_task_id = None # <-- Инициализируем здесь

    if campaign_id:
        campaign_instance = get_object_or_404(Email_campaing, pk=campaign_id)
        is_edit = True

    if request.method == 'POST':
        form = EmailCampaignForm(request.POST, request.FILES, instance=campaign_instance)

        print("DEBUG POST: request.POST.get('recipient_mode'):", request.POST.get('recipient_mode'))
        print("DEBUG POST: request.POST.get('users'):", request.POST.get('users'))
        print("DEBUG POST: request.FILES.get('new_template_file'):", request.FILES.get('new_template_file'))
        print("DEBUG POST: request.POST.get('template'):", request.POST.get('template'))

        if form.is_valid():
            email_campaign = form.save(commit=False)

            # --- Логика выбора и сохранения шаблона ---
            new_template_file = form.cleaned_data.get('new_template_file')
            existing_template_obj = form.cleaned_data.get('template')

            if new_template_file:
                file_name = new_template_file.name
                try:
                    template_obj = Tamplate_email.objects.get(template_file__icontains=file_name)
                    template_obj.template_file.save(file_name, new_template_file, save=True)
                    print(f"DEBUG: Обновлен существующий шаблон с файлом: {file_name}")
                except Tamplate_email.DoesNotExist:
                    template_obj = Tamplate_email()
                    template_obj.template_file.save(file_name, new_template_file, save=True)
                    print(f"DEBUG: Создан новый шаблон с файлом: {file_name}")
                email_campaign.template = template_obj
            elif existing_template_obj:
                email_campaign.template = existing_template_obj
                print(f"DEBUG: Выбран существующий шаблон с ID: {existing_template_obj.id}")
            else:
                email_campaign.template = None
                print("DEBUG: Шаблон не выбран и новый файл не загружен.")

            email_campaign.save()

            # --- Логика выбора получателей ---
            recipient_mode = form.cleaned_data.get('recipient_mode')
            selected_user_ids = form.cleaned_data.get('users', [])

            if recipient_mode == "selected":
                if selected_user_ids:
                    print(f"DEBUG: Выбран режим 'selected'. Количество ID из формы: {len(selected_user_ids)}")
                    users_to_set = User.objects.filter(id__in=selected_user_ids)
                    email_campaign.users.set(users_to_set)
                else:
                    print("DEBUG: Режим 'selected' выбран, но ни один пользователь не выбран.")
                    email_campaign.users.clear()
            elif recipient_mode == "all":
                print("DEBUG: Выбран режим 'all'.")
                all_active_users = User.objects.filter(is_active=True)
                email_campaign.users.set(all_active_users)
                print(f"DEBUG: Количество активных пользователей: {all_active_users.count()}")

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
                print("DEBUG: Нет email-адресов для отправки. Задача Celery не запущена.")
                email_campaign.status = 'sent'
                email_campaign.save()
                # Если нет получателей, можно просто перенаправить на список или ту же страницу без task_id
                return redirect('email_campaign_list') # или redirect('email_campaign_create')


        else:  # Форма невалидна
            print(f"DEBUG: Форма невалидна. Ошибки: {form.errors}")

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
        print(f"DEBUG (GET request): Form fields available: {list(form.fields.keys())}")

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
            else:
                print("ОШИБКА КОНФИГУРАЦИИ: Поле 'template' не найдено в EmailCampaignForm. Проверьте admins/forms.py.")


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
    today = timezone.now().date()
    date_from = today - timezone.timedelta(days=30)
    ticket_sales = (Tickets.objects.filter(session__date__gte=date_from,session__date__lte=today).
                    values('session__date').annotate(count=Count('id')).order_by('session__date' ))
    chart_labels = [item['session__date'].strftime('%Y-%m-%d') for item in ticket_sales]
    chart_data = [item['count'] for item in ticket_sales]
    knob_data = {
        'category1': 5,
        'category2': 10,
        'category3': 20,
    }

    context = {
        'user_count': user_count,
        'ticket_count': ticket_count,
        'movie_count' : movie_count,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'knob_data': knob_data,
    }

    return render(request,'admin/index.html', context)



@staff_member_required
def new_contacts(request):
    print(f"--- new_contacts view called, Request method: {request.method} ---")

    seo_instance = None
    try:
        seo_instance = Block_SEO.objects.get(id=1)
        print(f"DEBUG: Found existing Block_SEO instance with ID: {seo_instance.id}")
    except Block_SEO.DoesNotExist:
        print("DEBUG: Block_SEO instance with id=1 does not exist. A new one will be created if form is valid.")
        seo_instance = None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while retrieving Block_SEO: {e}")

    if request.method=='POST':
        print("DEBUG: Handling POST request.")
        formset = ContactFormSet(request.POST, request.FILES, queryset=Contact.objects.all())
        block_seo_form = BlockSEOForm(request.POST, instance=seo_instance)

        print(f"DEBUG: Data from POST request (first 200 chars): {str(request.POST)[:200]}...")
        if request.FILES:
            print(f"DEBUG: Files from POST request: {request.FILES.keys()}")
        else:
            print("DEBUG: No files in POST request.")

        if formset.is_valid() and block_seo_form.is_valid():
            print("DEBUG: Both ContactFormSet and BlockSEOForm are valid. Proceeding to save.")


            try:

                contacts = formset.save()
                print(f"DEBUG: Formset saved {len(contacts)} contacts.")

                for obj in formset.deleted_objects:
                    print(f"DEBUG: Deleting contact: {obj.title} (ID: {obj.id})")
                    if obj.gallery:
                        obj.gallery.delete()
                        print(f"DEBUG: Deleted gallery for contact {obj.title}")
                    obj.delete()

            except Exception as e:
                print(f"ERROR: An error occurred during formset save: {e}")

                raise e
            block_seo_form.save()
            print(f"DEBUG: BlockSEOForm saved. New/updated title_seo: {block_seo_form.instance.title_seo}")

            print("DEBUG: Redirecting to 'con' (contacts list page).")
            return redirect('con')
        else:
            print("WARNING: One or more forms are NOT valid. Displaying errors.")
            if not formset.is_valid():
                print("ERROR: ContactFormSet is INVALID.")
                for i, form in enumerate(formset):
                    if form.errors:
                        print(f"  Form {i} errors: {form.errors}")
                    if form.non_field_errors():
                        print(f"  Form {i} non-field errors: {form.non_field_errors()}")
            else:
                print("DEBUG: ContactFormSet is VALID.")

            if not block_seo_form.is_valid():
                print("ERROR: BlockSEOForm is INVALID.")
                print(f"  BlockSEOForm errors: {block_seo_form.errors}")
                print(f"  BlockSEOForm non_field_errors: {block_seo_form.non_field_errors()}")
            else:
                print("DEBUG: BlockSEOForm is VALID.")

    else:  # GET request
        print("DEBUG: Handling GET request.")
        formset = ContactFormSet(queryset=Contact.objects.all())
        block_seo_form = BlockSEOForm(instance=seo_instance)

    print("DEBUG: Rendering new_contacts.html template.")
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

            print("Ошибка валидации форм")
            print("block_seo_form.errors:", block_seo_form.errors)
            print("movie_form.errors:", movie_form.errors)
            print("gallery_form.errors:", gallery_form.errors)
            print("picture_formset.errors:", picture_formset.errors)
            print("main_picture_form.errors:", main_picture_form.errors)

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
            queryset=Picture.objects.filter(gallery=gallery_instance).exclude(pk=current_main_picture_object.pk) if current_main_picture_object else Picture.objects.filter(gallery=gallery_instance),
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
    cinemas_list = Cinemas.objects.select_related('gallery').prefetch_related(
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


    if request.method=='POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        cinema_form = CinemaForm(request.POST, instance=cinema_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)

        banner_form = PictureForm(request.POST, request.FILES, instance=current_main_picture_object,
                                                                                 prefix='banner_form')
        logo_form = PictureForm(request.POST, request.FILES, instance=current_logo_picture_object,
                                                                                prefix='logo_form')


        picture_queryset_for_formset = Picture.objects.none()
        if gallery_instance:
            picture_queryset_for_formset = gallery_instance.pictures.filter(image_type='gallery_image').order_by('pk')

        picture_formset = PictureFormSet(request.POST,  request.FILES,   queryset=picture_queryset_for_formset,
                                                                                prefix='pictures'   )


        if (block_seo_form.is_valid() and
                cinema_form.is_valid() and
                gallery_form.is_valid() and
                picture_formset.is_valid() and
                banner_form.is_valid() and
                logo_form.is_valid()):


            block_seo = block_seo_form.save()
            gallery = gallery_form.save()


            cinema = cinema_form.save(commit=False)
            cinema.seo_block = block_seo
            cinema.gallery = gallery
            cinema.save()

            if banner_form.cleaned_data.get('image'):
                banner_picture = banner_form.save(commit=False)
                banner_picture.gallery = gallery
                banner_picture.image_type = 'main_picture'
                banner_picture.save()

                if current_main_picture_object and current_main_picture_object.pk!=banner_picture.pk:
                    current_main_picture_object.delete()
            elif banner_form.cleaned_data.get('DELETE') and current_main_picture_object:
                current_main_picture_object.delete()


            if logo_form.cleaned_data.get('image'):
                logo_picture = logo_form.save(commit=False)
                logo_picture.gallery = gallery
                logo_picture.image_type = 'logo'
                logo_picture.save()

                if current_logo_picture_object and current_logo_picture_object.pk!=logo_picture.pk:
                    current_logo_picture_object.delete()
            elif logo_form.cleaned_data.get('DELETE') and current_logo_picture_object:
                current_logo_picture_object.delete()


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
            print("Ошибка валидации форм")
            print("block_seo_form.errors:", block_seo_form.errors)
            print("cinema_form.errors:", cinema_form.errors)
            print("gallery_form.errors:", gallery_form.errors)
            print("picture_formset.errors:", picture_formset.errors)
            print("banner_form.errors:", banner_form.errors)
            print("logo_form.errors:", logo_form.errors)

            return render(request, 'admin/paige_list/add_cinema.html', {
                'block_seo_form': block_seo_form,
                'cinema_form': cinema_form,
                'gallery_form': gallery_form,
                'picture_formset': picture_formset,
                'banner_form': banner_form,
                'logo_form': logo_form,
                'cinema': cinema_instance,
                'halls_list': halls_list,
                'is_edit': cinema_instance is not None,
            })


    else:
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        cinema_form = CinemaForm(instance=cinema_instance)
        gallery_form = GalleryForm(instance=gallery_instance)


        picture_queryset_for_formset = Picture.objects.none()
        if gallery_instance:
            picture_queryset_for_formset = gallery_instance.pictures.filter(image_type='gallery_image').order_by('pk')

        picture_formset = PictureFormSet( queryset=picture_queryset_for_formset, prefix='pictures'     )

        banner_form = PictureForm( instance=current_main_picture_object, prefix='banner_form',
                                                        initial={'image_type': 'main_picture'}     )

        logo_form = PictureForm(instance=current_logo_picture_object,     prefix='logo_form',
                                                                      initial={'image_type': 'logo'}        )

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

def add_halls_create(request, cinema_pk, halls_id=None): # <-- Тепер приймає halls_id як необов'язковий
    # Отримуємо об'єкт кінотеатру, до якого буде належати зал
    cinema_instance = get_object_or_404(Cinemas, pk=cinema_pk) # Використовуємо Cinema замість Cinemas, якщо це назва вашої моделі

    halls_instance = None
    block_seo_instance = None
    gallery_instance = None

    current_main_picture_object = None
    current_cheme_picture_object = None

    # --- Логіка завантаження існуючого залу для редагування ---
    if halls_id:
        # Якщо halls_id присутній, ми редагуємо існуючий зал
        halls_instance = get_object_or_404(Halls, pk=halls_id, cinema=cinema_instance) # Перевіряємо, що зал належить цьому кінотеатру
        block_seo_instance = halls_instance.seo_block
        gallery_instance = halls_instance.gallery

        # Якщо у існуючого залу немає галереї, створюємо її
        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()
            halls_instance.gallery = gallery_instance
            halls_instance.save() # Зберігаємо, щоб прив'язати галерею до залу

        # Завантажуємо існуючі зображення банера та схеми, якщо вони є
        if gallery_instance:
            current_main_picture_object = gallery_instance.pictures.filter(image_type='main_picture').first()
            current_cheme_picture_object = gallery_instance.pictures.filter(image_type='logo').first()
    # --- Кінець логіки завантаження існуючого залу ---


    if request.method == 'POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        halls_form = HallsForm(request.POST, instance=halls_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)

        banner_form = PictureForm(request.POST, request.FILES, instance=current_main_picture_object,
            prefix='banner_form')
        cheme_form = PictureForm(request.POST, request.FILES, instance=current_cheme_picture_object,
            prefix='logo_form')

        # Завантажуємо існуючі галерейні зображення для формсету
        picture_queryset_for_formset = Picture.objects.none()
        if gallery_instance: # Якщо галерея існує (якщо редагуємо або щойно створили для існуючого залу)
            picture_queryset_for_formset = gallery_instance.pictures.filter(image_type='gallery_image').order_by('pk')

        picture_formset = PictureFormSet(request.POST, request.FILES, queryset=picture_queryset_for_formset,
            prefix='pictures')

        if (block_seo_form.is_valid() and
                halls_form.is_valid() and
                gallery_form.is_valid() and
                picture_formset.is_valid() and
                banner_form.is_valid() and
                cheme_form.is_valid()):

            block_seo = block_seo_form.save()
            gallery = gallery_form.save()

            halls = halls_form.save(commit=False)
            halls.seo_block = block_seo
            halls.gallery = gallery
            halls.cinema = cinema_instance # Завжди прив'язуємо зал до поточного кінотеатру
            halls.save()

            # --- Логіка збереження картинок та формсетів залишається незмінною ---
            if banner_form.cleaned_data.get('image'):
                banner_picture = banner_form.save(commit=False)
                banner_picture.gallery = gallery
                banner_picture.image_type = 'main_picture'
                banner_picture.save()

                if current_main_picture_object and current_main_picture_object.pk != banner_picture.pk:
                    current_main_picture_object.delete()
            elif banner_form.cleaned_data.get('DELETE') and current_main_picture_object:
                current_main_picture_object.delete()

            if cheme_form.cleaned_data.get('image'):
                cheme_picture = cheme_form.save(commit=False)
                cheme_picture.gallery = gallery
                cheme_picture.image_type = 'logo'
                cheme_picture.save()

                if current_cheme_picture_object and current_cheme_picture_object.pk != cheme_picture.pk:
                    current_cheme_picture_object.delete()
            elif cheme_form.cleaned_data.get('DELETE') and current_cheme_picture_object:
                current_cheme_picture_object.delete()

            instances_gallery = picture_formset.save(commit=False)
            for pic_instance in instances_gallery:
                if not pic_instance.pk: # Це нове зображення
                    pic_instance.gallery = gallery
                    if not pic_instance.image_type:
                        pic_instance.image_type = 'gallery_image'
                pic_instance.save()

            for picture_to_delete in picture_formset.deleted_objects:
                picture_to_delete.delete()
            # --- Кінець логіки збереження картинок та формсетів ---

            # Перенаправлення після успішного збереження/редагування
            # Перенаправляємо на сторінку редагування кінотеатру,
            # яка покаже оновлений список залів.
            return redirect('add_cinema_edit', cinema_id=cinema_pk)

        else: # Якщо форми невалідні (POST-запит)
            print("Ошибка валидации форм")
            print("block_seo_form.errors:", block_seo_form.errors)
            print("halls_form.errors:", halls_form.errors)
            print("gallery_form.errors:", gallery_form.errors)
            print("picture_formset.errors:", picture_formset.errors)
            print("banner_form.errors:", banner_form.errors)
            print("logo_form.errors:", cheme_form.errors)

            return render(request, 'admin/halls/add_halls.html', {
                'block_seo_form': block_seo_form,
                'halls_form': halls_form,
                'gallery_form': gallery_form,
                'picture_formset': picture_formset,
                'banner_form': banner_form,
                'cheme_form': cheme_form,
                'halls': halls_instance, # Передаємо halls_instance (може бути None або об'єкт)
                'cinema': cinema_instance,
                'is_edit': halls_instance is not None, # is_edit тепер залежить від halls_instance
            })

    else: # GET-запит (відображення форми)
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        halls_form = HallsForm(instance=halls_instance)
        gallery_form = GalleryForm(instance=gallery_instance)

        picture_queryset_for_formset = Picture.objects.none()
        if gallery_instance: # Завантажуємо існуючі зображення для формсету
            picture_queryset_for_formset = gallery_instance.pictures.filter(image_type='gallery_image').order_by('pk')

        picture_formset = PictureFormSet(queryset=picture_queryset_for_formset, prefix='pictures')

        banner_form = PictureForm(instance=current_main_picture_object, prefix='banner_form',
            initial={'image_type': 'main_picture'})
        cheme_form = PictureForm(instance=current_cheme_picture_object, prefix='logo_form',
            initial={'image_type': 'logo'})

    return render(request, 'admin/halls/add_halls.html', {
        'block_seo_form': block_seo_form,
        'halls_form': halls_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'banner_form': banner_form,
        'cheme_form': cheme_form,
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

@staff_member_required
def session_list(request):
    session_list = Sessions.objects.all()

    paginator = Paginator(session_list, 10)
    page = request.GET.get('page')
    try:
        sessions = paginator.page(page)
    except PageNotAnInteger:
        sessions = paginator.page(1)
    except EmptyPage:
        sessions = paginator.page(paginator.num_pages)

    context = {'sessions': sessions}
    return render(request, 'admin/session/sessions_list.html', context)

@staff_member_required
def add_edit_session(request, session_id=None):
    if request.method == 'POST':
        formset = SessionFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('sessions_list')
    else:

        formset = SessionFormSet(queryset=Sessions.objects.none())

    return render(request, 'admin/session/add_sessions.html', {
        'session_formset': formset,
        'session': None
    })

@staff_member_required
def delete_sessions(request, pk):
        sessions = get_object_or_404(Sessions, pk=pk)

        sessions.delete()

        return redirect('sessions_list')

@staff_member_required
def seats_list(request: HttpRequest) :
    seats_list = Seats.objects.select_related('halls').order_by('number_row', 'seat')
    paginator = Paginator(seats_list, 10)
    page_number = request.GET.get('page')

    try:
        seats = paginator.page(page_number)
    except PageNotAnInteger:
        seats = paginator.page(1)
    except EmptyPage:
        seats = paginator.page(paginator.num_pages)

    context = {'seats': seats}

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('admin/seats_list/seats_table_partial.html', context, request=request)
        return HttpResponse(html)
    else:
        return render(request, 'admin/seats_list/seats_list.html', context)

@staff_member_required
def add_edit_seat(request):
    seat_id = request.GET.get('seat_id') or request.POST.get('seat_id')
    if seat_id:
        seat_instance = get_object_or_404(Seats, id=seat_id)
        form = SeatForm(request.POST or None, instance=seat_instance)
    else:
        form = SeatForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('seats_list')

    seats = Seats.objects.all().order_by('number_row', 'seat')
    return render(request, 'admin/seats_list/add_seats.html', {
        'form': form,
        'seats': seats,
    })

@staff_member_required
def delete_seats(request, pk):
        seat = get_object_or_404(Seats, pk=pk)

        seat.delete()

        return redirect('seats_list')

@staff_member_required
def tickets_list(request):

    tickets_list = Tickets.objects.all()


    paginator = Paginator(tickets_list, 10)
    page = request.GET.get('page')
    try:
        tickets = paginator.page(page)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)

    context = {
        'tickets': tickets,
    }
    return render(request, 'admin/tickets/tickets_list.html', context)

@staff_member_required
def add_edit_ticket(request, session_id=None):
    session_instance = None
    ticket_instance = None

    if session_id:
        session_instance = get_object_or_404(Sessions, id=session_id)
        try:
            ticket_instance = Tickets.objects.get(session=session_instance)
        except Tickets.DoesNotExist:
            ticket_instance = Tickets(session=session_instance)

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket_instance)
        if form.is_valid():
            saved_ticket = form.save()

            seat_to_update = saved_ticket.seat
            if seat_to_update:
                seat_to_update.status = 'S'
                seat_to_update.save()

            return redirect('tickets_lists')
    else:
        form = TicketForm(instance=ticket_instance)

    context = {
        'form': form,
        'session': session_instance,
    }
    return render(request, 'admin/tickets/add_tickets.html', context)

@staff_member_required
def delete_tickets (request, pk):
        tickets = get_object_or_404(Tickets, pk=pk)
        if request.method == 'POST':
            tickets.delete()
            return redirect('tickets_lists')
        tickets.delete()
        return redirect('tickets_lists')


@staff_member_required
def add_banners(request):
    banner_formset = BannersFormSet(request.POST or None, request.FILES or None, queryset=Banners.objects.all(), prefix='top_banners')
    cross_banner_instance = Cross_Banner.objects.first()
    cross_banner_form = CrossBannerForm(request.POST or None, request.FILES or None, instance=cross_banner_instance, prefix='cross_banner')
    news_formset = NewsFormSet(request.POST or None, request.FILES or None, queryset=News.objects.all(), prefix='news')


    if request.method=='POST':

        if "which_form_is_it" in request.POST:
            which_form_is_submiting = request.POST["which_form_is_it"]

            if str(which_form_is_submiting) == "this_is_form_banner":

                if banner_formset.is_valid():

                    banner_formset.save()

                    for form in banner_formset.forms:
                        if not form.cleaned_data:
                            continue
                        banner = form.instance

                        # Перевіряємо, чи передано новий файл
                        main_picture_file = form.cleaned_data.get('main_picture')

                        # Якщо новина не має галереї — створюємо її
                        if banner and not banner.gallery:
                            banner.gallery = Gallery.objects.create()
                            banner.save()

                        # Якщо є галерея — отримуємо або створюємо Picture з типом main_picture
                        if banner.gallery:
                            picture = banner.gallery.pictures.filter(image_type='main_picture').first()
                            if not picture:
                                picture = Picture(gallery=banner.gallery, image_type='main_picture')

                            # Оновлюємо зображення, тільки якщо новий файл передано
                            if main_picture_file:
                                picture.image = main_picture_file

                            picture.save()

                    banner_formset.save()

                    return redirect('add_banners')
                else:
                    pass


            elif str(which_form_is_submiting) == "this_is_form_cross_banner":

                if cross_banner_form.is_valid():
                    cross_banner = cross_banner_form.save()
                    image_file = request.FILES.get('cross_banner-image')

                    if cross_banner:
                        if not cross_banner.gallery_id:
                            cross_banner.gallery = Gallery.objects.create()
                            cross_banner.save()

                        if cross_banner.gallery:
                            picture = cross_banner.gallery.pictures.first()

                            if not picture:
                                picture = Picture(gallery=cross_banner.gallery)

                            if image_file:
                                picture.image = image_file
                                picture.save()
                            else:
                                pass
                    return redirect('add_banners')

                else:
                    pass
            elif str(which_form_is_submiting)=="this_is_form_news":

                if news_formset.is_valid():

                    news_formset.save()
                    for form in news_formset.forms:
                        if not form.cleaned_data:
                            continue
                        news = form.instance

                        # Перевіряємо, чи передано новий файл
                        main_picture_file = form.cleaned_data.get('main_picture')

                        # Якщо новина не має галереї — створюємо її
                        if news and not news.gallery:
                            news.gallery = Gallery.objects.create()
                            news.save()

                        # Якщо є галерея — отримуємо або створюємо Picture з типом main_picture
                        if news.gallery:
                            picture = news.gallery.pictures.filter(image_type='main_picture').first()
                            if not picture:
                                picture = Picture(gallery=news.gallery, image_type='main_picture')

                            # Оновлюємо зображення, тільки якщо новий файл передано
                            if main_picture_file:
                                picture.image = main_picture_file

                            picture.save()

                    return redirect('add_banners')
                else:
                    pass
        else:
                pass

    form_data = []
    for form in banner_formset.forms:
        image_url = None
        if form.instance.gallery:
            picture = form.instance.gallery.pictures.filter(image_type='main_picture').first()
            if picture and picture.image:
                image_url = picture.image.url
        form_data.append({'form': form, 'image_url': image_url})

    news_form_data = []
    for form in news_formset.forms:
        image_url = None
        if form.instance.gallery:
            picture = form.instance.gallery.pictures.filter(image_type='main_picture').first()
            if picture and picture.image:
                image_url = picture.image.url
        news_form_data.append({'form': form, 'image_url': image_url})

    return render(request, 'admin/banner/add_banner.html', {
        'formset': banner_formset,
        'form_data': form_data,
        'cross_banner_form': cross_banner_form,
        'news_formset': news_formset,
        'news_form_data': news_form_data,
    })

@staff_member_required
def banners_list(request):
    banners_list = Banners.objects.select_related('gallery').all().order_by('id')

    paginator = Paginator(banners_list, 10)
    page = request.GET.get('page')
    try:
        banners = paginator.page(page)
    except PageNotAnInteger:
        banners = paginator.page(1)
    except EmptyPage:
        banners = paginator.page(paginator.num_pages)

    context = {'banners': banners}

    return render(request, 'admin/banner/banner.html', context)

@staff_member_required
def delete_banners(request, banners_id):
     banner = get_object_or_404(Banners, pk=banners_id)
     if request.method == 'POST':
         banner.delete()

     return redirect('banners')

@staff_member_required
def user_list(request):

    user_list_all = User.objects.all()
    paginator = Paginator(user_list_all, 10)
    page_number = request.GET.get('page')

    try:
        users_page = paginator.page(page_number)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)
    context = {'users': users_page}
    return render(request, 'admin/user/user_lists.html', context)

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

    if request.method == 'POST': # <<< Видалення відбувається тільки тут
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

            print("Ошибка валидации форм")
            print("block_seo_form.errors:", block_seo_form.errors)
            print("news_form.errors:", news_form.errors)
            print("gallery_form.errors:", gallery_form.errors)
            print("picture_formset.errors:", picture_formset.errors)
            print("main_picture_form.errors:", main_picture_form.errors)

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
def  promotion_paige_add(request, promotion_id=None):
    promotion_instance = None
    block_seo_instance = None
    gallery_instance = None

    current_main_picture_object = None

    if promotion_id:
        promotion_instance = get_object_or_404(PaigesNews, pk=promotion_id)
        block_seo_instance = promotion_instance.seo_block
        gallery_instance = promotion_instance.gallery

        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()
            promotion_instance.gallery = gallery_instance
            promotion_instance.save()


        current_main_picture_object = gallery_instance.pictures.filter(image_type='main_picture').first()


    if gallery_instance is None:
        gallery_instance = Gallery.objects.create()  # Создаем новую галерею


    if request.method=='POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        promotion_form = PromotionForm(request.POST, instance=promotion_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)


        picture_formset = PictureFormSet(
            request.POST,
            request.FILES,
            queryset=Picture.objects.filter(gallery=gallery_instance).exclude(pk=current_main_picture_object.pk)
            if current_main_picture_object else Picture.objects.filter(gallery=gallery_instance),
            prefix='pictures', initial=[{'image_type': 'gallery_image'}]
        )

        main_picture_form = PictureForm(request.POST, request.FILES, instance=current_main_picture_object,
                                        prefix='main_picture_form')


        if f'{main_picture_form.prefix}-image_type' not in request.POST:
            main_picture_form.data = main_picture_form.data.copy()
            main_picture_form.data[f'{main_picture_form.prefix}-image_type'] = 'main_picture'

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

            return redirect('promotion')

        else:

            print("Ошибка валидации форм")
            print("block_seo_form.errors:", block_seo_form.errors)
            print("Promotion_form.errors:", promotion_form.errors)
            print("gallery_form.errors:", gallery_form.errors)
            print("picture_formset.errors:", picture_formset.errors)
            print("main_picture_form.errors:", main_picture_form.errors)

            return render(request, 'admin/promotion/add_promotion.html', {
                'block_seo_form': block_seo_form,
                'promotion_form': promotion_form,
                'gallery_form': gallery_form,
                'picture_formset': picture_formset,
                'main_picture_form': main_picture_form,
                'promotion': promotion_instance,
                'is_edit': promotion_instance is not None,
            })


    else:
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        promotion_form = PromotionForm(instance=promotion_instance)
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
            print("Ошибка валидации форм")
            print("block_seo_form.errors:", block_seo_form.errors)
            print("paige_form.errors:", paige_form.errors)

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
    paige_instance = None
    block_seo_instance = None
    gallery_instance = None

    current_main_picture_object = None

    if paige_id:
        paige_instance = get_object_or_404(PaigesCinema, pk=paige_id)
        block_seo_instance = paige_instance.seo_block
        gallery_instance = paige_instance.gallery

        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()
            paige_instance.gallery = gallery_instance
            paige_instance.save()

        current_main_picture_object = gallery_instance.pictures.filter(image_type='main_picture').first()

    if gallery_instance is None:
        gallery_instance = Gallery.objects.create()  # Создаем новую галерею

    if request.method=='POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        paige_form = PaigesCinemaForm(request.POST, instance=paige_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)

        picture_formset = PictureFormSet(
            request.POST,
            request.FILES,
            queryset=Picture.objects.filter(gallery=gallery_instance).exclude(pk=current_main_picture_object.pk) if
            current_main_picture_object else Picture.objects.filter(gallery=gallery_instance),
            prefix='pictures', initial=[{'image_type': 'gallery_image'}]
        )

        main_picture_form = PictureForm(request.POST, request.FILES, instance=current_main_picture_object,
                                        prefix='main_picture_form')

        if f'{main_picture_form.prefix}-image_type' not in request.POST:
            main_picture_form.data = main_picture_form.data.copy()
            main_picture_form.data[f'{main_picture_form.prefix}-image_type'] = 'main_picture'

        if f'{main_picture_form.prefix}-gallery' not in request.POST and gallery_instance.pk:
            main_picture_form.data = main_picture_form.data.copy()
            main_picture_form.data[f'{main_picture_form.prefix}-gallery'] = gallery_instance.pk

        if (block_seo_form.is_valid() and
                paige_form.is_valid() and
                gallery_form.is_valid() and
                picture_formset.is_valid() and  #
                main_picture_form.is_valid()):

            block_seo = block_seo_form.save()
            gallery = gallery_form.save()

            paige = paige_form.save(commit=False)
            paige.seo_block = block_seo
            paige.gallery = gallery
            paige.save()

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

            return redirect('paige')

        else:

            print("Ошибка валидации форм")
            print("block_seo_form.errors:", block_seo_form.errors)
            print("paige_form.errors:", paige_form.errors)
            print("gallery_form.errors:", gallery_form.errors)
            print("picture_formset.errors:", picture_formset.errors)
            print("main_picture_form.errors:", main_picture_form.errors)

            return render(request, 'admin/paige_list/add_paige.html', {
                'block_seo_form': block_seo_form,
                'paige_form': paige_form,
                'gallery_form': gallery_form,
                'picture_formset': picture_formset,
                'main_picture_form': main_picture_form,
                'paige': paige_instance,
                'is_edit': paige_instance is not None,
            })


    else:
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        paige_form = PaigesCinemaForm(instance=paige_instance)
        gallery_form = GalleryForm(instance=gallery_instance)

        picture_formset = PictureFormSet(
            queryset=Picture.objects.filter(gallery=gallery_instance).exclude(pk=current_main_picture_object.pk) if
            current_main_picture_object else Picture.objects.filter(gallery=gallery_instance),
            prefix='pictures'
        )

        main_picture_form = PictureForm(
            instance=current_main_picture_object,
            prefix='main_picture_form',
            initial={'image_type': 'main_picture'}
        )

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
def  paige_delete(request, news_id):
    news = get_object_or_404(PaigesNews, pk=news_id)
    if request.method=='POST':
        news.delete()

    return redirect('news')