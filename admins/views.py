from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from movie.models import Movies
from main.models import Gallery
from core.models import Cinemas, Halls, Sessions
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import BlockSEOForm, MovieForm, PictureFormSet, GalleryForm, CinemaForm, HallsForm, SessionsForm


def index(request):

    return render(request,'admin/index.html')

def movie_list(request):
    movies_list = Movies.objects.all()
    paginator = Paginator(movies_list, 10)
    page = request.GET.get('page')
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)

    context = {'movies': movies}
    return render(request, 'admin/movies_lists/movies_lists.html', context)

def add_movie(request,movie_id=None):
    movie_instance = None
    block_seo_instance = None
    gallery_instance = None


    if movie_id is not None:
        movie_instance = get_object_or_404(Movies, pk=movie_id)
        block_seo_instance = movie_instance.seo_block  # Отримуємо пов'язаний Block_SEO
        gallery_instance = movie_instance.gallery  # Отримуємо пов'язану Gallery


        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()


    if request.method == 'POST':

        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        movie_form = MovieForm(request.POST, instance=movie_instance)
        gallery_form = GalleryForm(request.POST,
                                   instance=gallery_instance)
        picture_formset = PictureFormSet(request.POST, request.FILES, instance=gallery_instance)


        if block_seo_form.is_valid() and movie_form.is_valid() and gallery_form.is_valid() and picture_formset.is_valid():


            block_seo_instance = block_seo_form.save()
            gallery_instance = gallery_form.save()


            movie_instance = movie_form.save(commit=False)


            movie_instance.seo_block = block_seo_instance
            movie_instance.gallery = gallery_instance
            if movie_id is None and not movie_instance.date:
                movie_instance.date = timezone.now().date()

            movie_instance.save()

            # Зберігаємо картинки після збереження галереї
            picture_formset.instance = gallery_instance
            picture_formset.save()


            if movie_id is None:  # Якщо створювали

                return redirect('movie_list')
            else:
                return redirect('movie_list')
        else:

            pass
    else:

        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        movie_form = MovieForm(instance=movie_instance)
        gallery_form = GalleryForm(instance=gallery_instance)
        picture_formset = PictureFormSet(instance=gallery_instance)  # Якщо gallery_instance None, формсет буде порожнім


    return render(request, 'admin/movies_lists/add_movies.html', {  # Переконайтеся, що шлях до шаблону правильний
        'block_seo_form': block_seo_form,
        'movie_form': movie_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'movie': movie_instance,  # Можливо, вам знадобиться об'єкт movie у шаблоні (наприклад, для заголовка сторінки)
    })

def delete_movie(request, pk):
    movie = get_object_or_404(Movies, pk=pk)

    movie.delete()


    return redirect('movie_list')

def cinema_list(request):
    cinemas_list = Cinemas.objects.all()

    paginator = Paginator(cinemas_list, 10)
    page = request.GET.get('page')
    try:
        cinemas = paginator.page(page)
    except PageNotAnInteger:
        cinemas = paginator.page(1)
    except EmptyPage:
        cinemas = paginator.page(paginator.num_pages)

    context = {'cinemas': cinemas}
    return render(request, 'admin/cinema/cinema_list.html', context)

def add_cinema_create(request, cinema_id=None):


    cinema_instance = None
    block_seo_instance = None
    gallery_instance = None

    if cinema_id is not None:
        cinema_instance = get_object_or_404(Cinemas, pk=cinema_id)
        block_seo_instance = cinema_instance.seo_block
        gallery_instance = cinema_instance.gallery

        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()

    if request.method == 'POST':
        # Ініціалізуємо форми з даними POST
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        cinema_form = CinemaForm(request.POST, instance=cinema_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)
        picture_formset = PictureFormSet(request.POST, request.FILES, instance=gallery_instance)

        print("POST DATA:", request.POST)
        print("block_seo_form errors:", block_seo_form.errors)
        print("cinema_form errors:", cinema_form.errors)
        print("gallery_form errors:", gallery_form.errors)
        print("picture_formset errors:", picture_formset.errors)

        if block_seo_form.is_valid() and cinema_form.is_valid() and gallery_form.is_valid() and picture_formset.is_valid():
            block_seo_instance = block_seo_form.save()
            gallery_instance = gallery_form.save()

            cinema_instance = cinema_form.save(commit=False)
            cinema_instance.seo_block = block_seo_instance
            cinema_instance.gallery = gallery_instance

            if cinema_id is None and not cinema_instance.date:
                cinema_instance.date = timezone.now().date()

            cinema_instance.save()

            picture_formset.instance = gallery_instance
            picture_formset.save()

            return redirect('cinema_lists')
    else:
        # Ініціалізуємо форми без даних POST
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        cinema_form = CinemaForm(instance=cinema_instance)
        gallery_form = GalleryForm(instance=gallery_instance)
        picture_formset = PictureFormSet(instance=gallery_instance)

    return render(request, 'admin/cinema/add_cinema.html', {
        'block_seo_form': block_seo_form,
        'cinema_form': cinema_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'cinema': cinema_instance,
        'form': cinema_form,  # Якщо потрібно для заголовка сторінки
    })
def delete_cinema(request, pk):
    cinema = get_object_or_404(Cinemas, pk=pk)

    cinema.delete()


    return redirect('cinema_list')

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

def add_halls_create(request, halls_id=None):
    halls_instance = None
    block_seo_instance = None
    gallery_instance = None

    if halls_id is not None:
        halls_instance = get_object_or_404(Halls, pk=halls_id)
        block_seo_instance = halls_instance.seo_block
        gallery_instance = halls_instance.gallery

        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()

    if request.method == 'POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        halls_form = HallsForm(request.POST, instance=halls_instance)  # Тут використовуємо HallsForm
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)
        picture_formset = PictureFormSet(request.POST, request.FILES, instance=gallery_instance)

        print("POST DATA:", request.POST)
        print("block_seo_form errors:", block_seo_form.errors)
        print("halls_form errors:", halls_form.errors)
        print("gallery_form errors:", gallery_form.errors)
        print("picture_formset errors:", picture_formset.errors)

        if block_seo_form.is_valid() and halls_form.is_valid() and gallery_form.is_valid() and picture_formset.is_valid():
            block_seo_instance = block_seo_form.save()
            gallery_instance = gallery_form.save()

            halls_instance = halls_form.save(commit=False)
            halls_instance.seo_block = block_seo_instance
            halls_instance.gallery = gallery_instance

            if halls_id is None and not halls_instance.date:
                halls_instance.date = timezone.now().date()

            halls_instance.save()

            picture_formset.instance = gallery_instance
            picture_formset.save()

            return redirect('halls_lists')
    else:
        # Ініціалізуємо форми без даних POST
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        halls_form = HallsForm(instance=halls_instance)  # Тепер правильна форма
        gallery_form = GalleryForm(instance=gallery_instance)
        picture_formset = PictureFormSet(instance=gallery_instance)

    return render(request, 'admin/halls/add_halls.html', {
        'block_seo_form': block_seo_form,
        'halls_form': halls_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'halls': halls_instance,
        'form': halls_form,  # Якщо потрібно для заголовка сторінки
    })

def delete_halls(request, pk):
    halls = get_object_or_404(Halls, pk=pk)

    halls.delete()


    return redirect('halls_list')

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

def add_edit_session(request, session_id=None): # Змінено ім'я функції для ясності
    session_instance = None
    if session_id is not None:
        session_instance = get_object_or_404(Sessions, pk=session_id)

    if request.method == 'POST':
        form = SessionsForm(request.POST, instance=session_instance) # Передаємо коректний інстанс або None
        if form.is_valid():
            form.save()
            return redirect('sessions_list') # Перенаправлення після успішного збереження
    else: # GET запит
        form = SessionsForm(instance=session_instance) # Передаємо коректний інстанс або None

    return render(request, 'admin/session/add_sessions.html', {'form': form, 'session': session_instance})


def delete_sessions(request, pk):
        sessions = get_object_or_404(Sessions, pk=pk)

        sessions.delete()

        return redirect('sessions_list')