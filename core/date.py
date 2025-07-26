from datetime import datetime

cinema_data_list = [
    {
        "title": "Кинотеатр Планета Кино",
        "title_ru": "Кинотеатр Планета Кино",
        "title_uk": "Кинотеатр Планета Кино",
        "description": "дуже великий екран;\r\nсистема кругової поляризації REAL3D;\r\nзвук DOLBY DIGITAL SURROUND-EX;\r\nкомфортна відстань між рядами крісел;\r\nсистема обігріву і кондиціонування повітря;\r\nсучасні ергономічні крісла;\r\nможливість оплати квитків онлайн;\r\nрепертуар світових прем’єр.",
        "description_ru": "дуже великий екран;\r\nсистема кругової поляризации REAL3D;\r\nзвук DOLBY DIGITAL SURROUND-EX;\r\nкомфортна відстань між рядами крісел;\r\nсистема обігріву і кондиціонування повітря;\r\nсучасні ергономічні крісла;\r\nможливість оплати квитків онлайн;\r\nрепертуар світових прем’єр.",
        "description_uk": "очень большой экран; система круговой поляризации REAL3D; звук DOLBY DIGITAL SURROUND-EX; комфортное расстояние между рядами кресел; система обогрева и кондиционирования воздуха; современные эргономические кресла; онлайн возможность оплаты; премьер.",
        "conditions": "дуже великий екран;\r\nсистема кругової поляризації REAL3D;\r\nзвук DOLBY DIGITAL SURROUND-EX;\r\nкомфортна відстань між рядами крісел;\r\nсистема обігріву і кондиціонування повітря;\r\nсучасні ергономічні крісла;\r\nможливість оплати квитків онлайн;\r\nрепертуар світових прем’єр.",
        "conditions_ru": "очень большой экран; система круговой поляризации REAL3D; звук DOLBY DIGITAL SURROUND-EX; комфортное расстояние между рядами кресел; система обогрева и кондиционирования воздуха; современные эргономические кресла; онлайн возможность оплаты; премьер.",
        "conditions_uk": "дуже великий екран;\r\nсистема кругової поляризации REAL3D;\r\nзвук DOLBY DIGITAL SURROUND-EX;\r\nкомфортна відстань між рядами крісел;\r\nсистема обігріву і кондиціонування повітря;\r\nсучасні ергономічні крісла;\r\nможливість оплати квитків онлайн;\r\nрепертуар світових прем’єр.",
        "city": "Запорожье",
        "city_ru": "Запорожье",
        "city_uk": "",
        "date": "2025-05-11"
    },
    {
        "title": "Кинотеатр Мультиплекс",
        "title_ru": "Кинотеатр Мультиплекс",
        "title_uk": "Кінотеатр Мультиплекс",
        "description": "Сучасні кінозали;\r\nЗручні сидіння;\r\nШирокий вибір фільмів;\r\nПриємна атмосфера;\r\nМожливість замовлення їжі та напоїв.",
        "description_ru": "Современные кинозалы;\r\nУдобные сиденья;\r\nШирокий выбор фильмов;\r\nПриятная атмосфера;\r\nВозможность заказа еды и напитков.",
        "description_uk": "Сучасні кінозали;\r\nЗручні сидіння;\r\nШирокий вибір фільмів;\r\nПриємна атмосфера;\r\nМожливість замовлення їжі та напоїв.",
        "conditions": "Сучасні кінозали;\r\nЗручні сидіння;\r\nШирокий вибір фільмів;\r\nПриємна атмосфера;\r\nМожливість замовлення їжі та напоїв.",
        "conditions_ru": "Современные кинозалы;\r\nУдобные сиденья;\r\nШирокий выбор фильмов;\r\nПриятная атмосфера;\r\nВозможность заказа еды и напитков.",
        "conditions_uk": "Сучасні кінозали;\r\nЗручні сидіння;\r\nШирокий вибір фільмів;\r\nПриємна атмосфера;\r\nМожливість замовлення їжі та напоїв.",
        "city": "Запорожье",
        "city_ru": "Запорожье",
        "city_uk": "Запоріжжя",
        "date": "2025-05-11"
    },
    {
        "title": "Кинотеатр Довженко",
        "title_ru": "Кинотеатр Довженко",
        "title_uk": "Кінотеатр Довженка",
        "description": "Затишні зали;\r\nЗручне розташування в центрі міста;\r\nРізноманітний репертуар;\r\nДоступні ціни;\r\nІсторична будівля.",
        "description_ru": "Уютные залы;\r\nУдобное расположение в центре города;\r\nРазнообразный репертуар;\r\nДоступные цены;\r\nИсторическое здание.",
        "description_uk": "Затишні зали;\r\nЗручне розташування в центрі міста;\r\nРізноманітний репертуар;\r\nДоступні ціни;\r\nІсторична будівля.",
        "conditions": "Затишні зали;\r\nЗручне розташування в центрі міста;\r\nРізноманітний репертуар;\r\nДоступні ціни;\r\nІсторична будівля.",
        "conditions_ru": "Уютные залы;\r\nУдобное расположение в центре города;\r\nРазнообразный репертуар;\r\nДоступные цены;\r\nИсторическое здание.",
        "conditions_uk": "Затишні зали;\r\nЗручне розташування в центрі міста;\r\nРізноманітний репертуар;\r\nДоступні ціни;\r\nІсторична будівля.",
        "city": "Запорожье",
        "city_ru": "Запорожье",
        "city_uk": "Запоріжжя",
        "date": "2025-05-11"
    }
]

seo_block_cinema_data_list = [
    {
        "title_seo": "Кинотеатр Планета Кино",
        "seo_url": "Cinema_Planeta_Kino",
        "seo_keywords": "Cinema Planeta Kino",
        "seo_description": "Cinema Planeta Kino"
    },
    {
        "title_seo": "Кинотеатр Мультиплекс",
        "seo_url": "Cinema_Multipleks",
        "seo_keywords": "Cinema Multipleks",
        "seo_description": "Cinema Multipleks"
    },
    {
        "title_seo": "Кинотеатр Довженко",
        "seo_url": "Cinema_Dovzhenko",
        "seo_keywords": "Cinema Dovzhenko",
        "seo_description": "Cinema Dovzhenko"
    }
]



picture_data_movies_list = {
    "Барби": [
        {"image_path": "movies/barbie_poster.jpeg", "image_type": "main_picture"},
        {"image_path": "movies/barbie_promo1.jpeg", "image_type": "gallery"},
        {"image_path": "movies/barbie_promo2.jpeg", "image_type": "gallery"},
    ],
    "Оппенгеймер": [
        {"image_path": "movies/oppenheimer_poster.jpeg", "image_type": "main_picture"},
        {"image_path": "movies/oppenheimer_scene1.jpeg", "image_type": "gallery"},
        {"image_path": "movies/oppenheimer_scene2.jpeg", "image_type": "gallery"},
    ],
    "Дюна: Часть вторая": [
        {"image_path": "movies/dune2_poster.jpeg", "image_type": "main_picture"},
        {"image_path": "movies/dune2_scene1.jpeg", "image_type": "gallery"},
        {"image_path": "movies/dune2_scene2.jpeg", "image_type": "gallery"},
    ],
}


seo_block_movies_data_list = [
    {"title_seo": "Фильм Барби SEO", "seo_url": "barbie-movie-seo", "seo_keywords": "барби, фильм", "seo_description": "SEO описание фильма Барби."},
    {"title_seo": "Фильм Оппенгеймер SEO", "seo_url": "oppenheimer-movie-seo", "seo_keywords": "оппенгеймер, драма", "seo_description": "SEO описание фильма Оппенгеймер."},
    {"title_seo": "Фильм Дюна: Часть вторая SEO", "seo_url": "dune-part-two-seo", "seo_keywords": "дюна, фантастика", "seo_description": "SEO описание фильма Дюна 2."},
]

# Данные для самих фильмов
movies_data_list = [
    {
        "title": "Барби",
        "title_ru": "Барби",
        "title_uk": "Барбі",
        "seo_block_title_seo": "Фильм Барби SEO",
        "genre": "COM",
        "url_trailer": "https://www.youtube.com/watch?v=some_barbie_trailer_id",
        "description": "Когда Барби и Кен попадают в реальный мир, они обнаруживают сложности жизни.",
        "description_ru": "Когда Барби и Кен попадают в реальный мир, они обнаруживают сложности жизни.",
        "description_uk": "Коли Барбі та Кен потрапляють у реальний світ, вони виявляють складнощі життя.",
        "relise_date": "2023-07-20",
        "age_limit": 6,
        "is_2d": True,
        "is_3d": False,
        "is_imax": False,
    },
    {
        "title": "Оппенгеймер",
        "title_ru": "Оппенгеймер",
        "title_uk": "Оппенгеймер",
        "seo_block_title_seo": "Фильм Оппенгеймер SEO",
        "genre": "DR",
        "url_trailer": "https://www.youtube.com/watch?v=some_oppenheimer_trailer_id",
        "description": "История жизни физика Дж. Роберта Оппенгеймера, руководителя Манхэттенского проекта.",
        "description_ru": "История жизни физика Дж. Роберта Оппенгеймера, руководителя Манхэттенского проекта.",
        "description_uk": "Історія життя фізика Дж. Роберта Оппенгеймера, керівника Манхеттенського проекту.",
        "relise_date": "2023-07-20",
        "age_limit": 16,
        "is_2d": True,
        "is_3d": False,
        "is_imax": True,
    },
    {
        "title": "Дюна: Часть вторая",
        "title_ru": "Дюна: Часть вторая",
        "title_uk": "Дюна: Частина друга",
        "seo_block_title_seo": "Фильм Дюна: Часть вторая SEO",
        "genre": "Sci",
        "url_trailer": "https://www.youtube.com/watch?v=some_dune_trailer_id",
        "description": "Пол Атрейдес объединяется с Чани и фременами, чтобы отомстить за свою семью.",
        "description_ru": "Пол Атрейдес объединяется с Чани и фременами, чтобы отомстить за свою семью.",
        "description_uk": "Пол Атрейдес об'єднується з Чані та фременами, щоб помститися за свою родину.",
        "relise_date": "2024-03-01",
        "age_limit": 12,
        "is_2d": True,
        "is_3d": True,
        "is_imax": True,
    },
]

picture_data_cinema_list = {
    "Кинотеатр Планета Кино": [
        {"image_path": "images/cinema_planetakino_main.jpeg", "image_type": "main_picture"},
        {"image_path": "images/cinema_planetakino_hall1.jpeg", "image_type": "logo"},
        {"image_path": "images/cinema_planetakino_lobby.jpeg", "image_type": "gallery"},
    ],
    "Кинотеатр Довженко": [
        {"image_path": "images/dovzhenko_cinema_main.jpeg", "image_type": "main_picture"},
        {"image_path": "images/dovzhenko_cinema_hall1.jpeg", "image_type": "logo"},
        {"image_path": "images/dovzhenko_cinema_lobby.jpeg", "image_type": "gallery"},
    ],
    "Кинотеатр Мультиплекс": [
        {"image_path": "images/cinema_multiplex_main.jpeg", "image_type": "main_picture"},
        {"image_path": "images/cinema_multiplex1.jpeg", "image_type": "logo"},
        {"image_path": "images/cinema_multiplex.jpeg", "image_type": "gallery"},
    ]
}

seo_block_pages_data_list = [
    {"title_seo": "Страница О нас SEO", "seo_url": "about-us-seo", "seo_keywords": "о нас, история, кинотеатр", "seo_description": "Информация о кинотеатре."},
    {"title_seo": "Страница Кафе SEO", "seo_url": "cafe-seo", "seo_keywords": "кафе, еда, напитки", "seo_description": "SEO описание кафе в кинотеатре."},
    {"title_seo": "Страница Реклама в кинотеатре SEO", "seo_url": "advertisement-seo", "seo_keywords": "реклама, кинотеатр, баннер", "seo_description": "Информация о рекламе в кинотеатре."},
    {"title_seo": "Страница Детская комната SEO", "seo_url": "kids-room-seo", "seo_keywords": "детская комната, кино, развлечения", "seo_description": "SEO описание детской комнаты."},
    {"title_seo": "Страница VIP-зал кинотеатра SEO", "seo_url": "vip-hall-seo", "seo_keywords": "vip зал, комфорт, премиум", "seo_description": "SEO описание VIP-зала."},

]

# Данные для модели PaigesCinema (включая "Реклама", "Детская комната", "VIP-зал", "Кафе", "О нас", "Контакты")
paiges_cinema_data_list = [
    {
        "title": "О нас",
        "title_ru": "О нас",
        "title_uk": "Про нас",
        "seo_block_title_seo": "Страница О нас SEO",
        "description": "Кинотеатр CineWave - это современное пространство для любителей кино, предлагающее широкий выбор фильмов и комфортные условия просмотра.",
        "description_ru": "Кинотеатр CineWave - это современное пространство для любителей кино, предлагающее широкий выбор фильмов и комфортные условия просмотра.",
        "description_uk": "Кінотеатр CineWave - це сучасний простір для любителів кіно, що пропонує широкий вибір фільмів та комфортні умови перегляду.",
        "date": "2025-06-25",
        "is_active": True,
    },
    {
        "title": "Кафе",
        "title_ru": "Кафе",
        "title_uk": "Кафе",
        "seo_block_title_seo": "kafe-bar",
        "description": "Наше уютное кафе предлагает широкий ассортимент закусок, напитков и десертов, чтобы ваш кинопросмотр был еще приятнее.",
        "description_ru": "Наше уютное кафе предлагает широкий ассортимент закусок, напитков и десертов, чтобы ваш кинопросмотр был еще приятнее.",
        "description_uk": "Наше затишне кафе пропонує широкий асортимент закусок, напоїв та десертів, щоб ваш кіноперегляд був ще приємнішим.",
        "date": "2025-06-29",
        "is_active": True,
    },
    {
        "title": "Реклама",
        "title_ru": "Реклама",
        "title_uk": "Реклама",
        "seo_block_title_seo": "promotion_22",
        "description": "Мы предлагаем различные варианты размещения рекламы в наших кинотеатрах. От баннеров до видеороликов перед сеансами.",
        "description_ru": "Мы предлагаем различные варианты размещения рекламы в наших кинотеатрах. От баннеров до видеороликов перед сеансами.",
        "description_uk": "Ми пропонуємо різні варіанти розміщення реклами у наших кінотеатрах. Від банерів до відеороликів перед сеансами.",
        "date": "2025-06-25",
        "is_active": True,
    },
    {
        "title": "Детская комната",
        "title_ru": "Детская комната",
        "title_uk": "Дитяча кімната",
        "seo_block_title_seo": "chaild_room",
        "description": "Ваши дети могут весело провести время в нашей современной детской комнате под присмотром опытных аниматоров, пока вы наслаждаетесь фильмом.",
        "description_ru": "Ваши дети могут весело провести время в нашей современной детской комнате под присмотром опытных аниматоров, пока вы наслаждаетесь фильмом.",
        "description_uk": "Ваші діти можуть весело провести час у нашій сучасній дитячій кімнаті під наглядом досвідчених аніматорів, поки ви насолоджуєтеся фільмом.",
        "date": "2025-06-25",
        "is_active": True,
    },
    {
        "title": "VIP-зал",
        "title_ru": "VIP-зал",
        "title_uk": "VIP-зал",
        "seo_block_title_seo": "VIP",
        "description": "Погрузитесь в мир кино с максимальным комфортом в нашем VIP-зале. Удобные кресла, индивидуальное обслуживание и эксклюзивное меню.",
        "description_ru": "Погрузитесь в мир кино с максимальным комфортом в нашем VIP-зале. Удобные кресла, индивидуальное обслуживание и эксклюзивное меню.",
        "description_uk": "Пориньте у світ кіно з максимальним комфортом у нашому VIP-залі. Зручні крісла, індивідуальне обслуговування та ексклюзивне меню.",
        "date": "2025-06-25",
        "is_active": True,
    },
    {
        "title": "Контакты",
        "title_ru": "Контакты",
        "title_uk": "Контакти",
        "seo_block_title_seo": "contact_paige",
        "description": "Свяжитесь с нами по телефону, электронной почте или посетите наш кинотеатр по адресу: [Ваш адрес].",
        "description_ru": "Свяжитесь с нами по телефону, электронной почте или посетите наш кинотеатр по адресу: [Ваш адрес].",
        "description_uk": "Зв'яжіться з нами за телефоном, електронною поштою або відвідайте наш кінотеатр за адресою: [Ваша адреса].",
        "date": "2025-06-25",
        "is_active": True,
    },
]

picture_data_pages_list = {
    "О нас": [
        {"image_path": "pages/about_us_main.jpeg", "image_type": "main_picture"},
        {"image_path": "pages/about_us_interior.jpeg", "image_type": "gallery"},
    ],
    "Кафе": [
        {"image_path": "pages/cafe_main.jpeg", "image_type": "main_picture"},
        {"image_path": "pages/cafe_interior.jpeg", "image_type": "gallery"},
    ],
    "Реклама": [
        {"image_path": "pages/advertisement_main.jpeg", "image_type": "main_picture"},
        {"image_path": "pages/advertisement_banner1.jpeg", "image_type": "gallery"},
    ],
    "Детская комната": [
        {"image_path": "pages/kids_room_main.jpeg", "image_type": "main_picture"},
        {"image_path": "pages/kids_room_play_area.jpeg", "image_type": "gallery"},
    ],
    "VIP-зал": [
        {"image_path": "pages/vip_hall_main.jpeg", "image_type": "main_picture"},
        {"image_path": "pages/vip_hall_interior.jpeg", "image_type": "gallery"},
        {"image_path": "pages/vip_hall_chair.jpeg", "image_type": "gallery"},
    ],
}

seo_block_contact_data_list = [
    {"title_seo": "Страница Контакты SEO", # Виправлено: додано "SEO" для відповідності
     "seo_url": "contacts-seo",
     "seo_keywords": "контакты кинотеатр, адрес кинотеатра, телефоны кинотеатра, кинотеатры в Украине",
     "seo_description": "Контактная информация, адреса и телефоны всех кинотеатров нашей сети в Украине."
    }
]

contact_data_list = [
    {
        "seo_block": "Страница Контакты SEO", # Виправлено для відповідності title_seo
        "title": "Кинотеатр Планета Кино",
        "address": "ул. Европейская, 10, Днепр",
        "latitude": 48.4647,
        "longitude": 35.0462,
        "phone_number": "+380000000001"
    },
    {
        "seo_block": "Страница Контакты SEO", # Виправлено для відповідності title_seo
        "title": "Кинотеатр Мультиплекс",
        "address": "пр. Степана Бандеры, 34В, Запорожье ",
        "latitude": 47.823162274049835,
        "longitude": 35.16817462440918,
        "phone_number": "+38000000002"
    },
    {
        "seo_block": "Страница Контакты SEO", # Виправлено для відповідності title_seo
        "title": "Кинотеатр Оскар",
        "address": "пр. Соборный, 145, Киев",
        "latitude": 50.439626,
        "longitude": 30.522204,
        "phone_number": "+380000000003"
    },
]

picture_data_contact_list = {
    'Кинотеатр Планета Кино': [
        {
            'image_path': 'contact/kontakt1_logo.png',
            'image_type': 'main_picture',
        },
        {
            'image_path': 'contact/kontakt1_logo.png',
            'image_type': 'logo',
        },
    ],
    'Кинотеатр Мультиплекс': [
        {
            'image_path': 'contact/kontakt2_logo.png',
            'image_type': 'main_picture',
        },
        {
            'image_path': 'contact/kontakt2_logo.png',
            'image_type': 'logo',
        },
    ],
    "Кинотеатр Оскар": [
        {
            'image_path': 'contact/kontakt3_logo.png',
            'image_type': 'main_picture',
        },
        {
            'image_path': 'contact/kontakt3_logo.png',
            'image_type': 'logo',
        },
    ],
}

banner_data_list = [
    {

        "url": "https://youtu.be/_fLRWSxlO3I?si=7VBpMQG-RKyTkIxd",
        "text": "Літні прем’єри вже в кінотеатрах CineWave!",
        "scroll_speed": 50,
        "is_active": True
    },
    {

        "url": "https://youtu.be/_fLRWSxlO3I?si=7VBpMQG-RKyTkIxd",
        "text": "Купуйте квитки онлайн без черг",
        "scroll_speed": 30,
        "is_active": True
    },
    {

        "url": "https://youtu.be/_fLRWSxlO3I?si=7VBpMQG-RKyTkIxd",
        "text": "Знижки для студентів та пенсіонерів – дізнайтесь більше!",
        "scroll_speed": 40,
        "is_active": True
    },
    {

        "url": "",
        "text": "CineWave – простір сучасного кіно",
        "scroll_speed": 60,
        "is_active": False
    }
]
picture_data_banners_list = {
    "Галерея для нових банерів": [
        {
            "image_path": "banners/banner.png",
            "image_type": "main_picture"
        },
        {
            "image_path": "banners/banner2.png",
            "image_type": "main_picture"
        },
        {
            "image_path": "banners/banner3.png",
            "image_type": "gallery"
        },

    ]
}
banner_news_list = [
    {

        "url": "https://youtu.be/_fLRWSxlO3I?si=7VBpMQG-RKyTkIxd",

        "scroll_speed": 50,
        "is_active": True
    },
    {

        "url": "https://youtu.be/_fLRWSxlO3I?si=7VBpMQG-RKyTkIxd",

        "scroll_speed": 30,
        "is_active": True
    },
    {

        "url": "https://youtu.be/_fLRWSxlO3I?si=7VBpMQG-RKyTkIxd",

        "scroll_speed": 40,
        "is_active": True
    },
    {

        "url": "https://youtu.be/_fLRWSxlO3I?si=7VBpMQG-RKyTkIxd",

        "scroll_speed": 60,
        "is_active": False
    }
]
picture_data_news_list = {
    "Галерея для нових банерів": [
        {
            "image_path": "banners/banner.png",  #
            "image_type": "main_picture"
        },
        {
            "image_path": "/banners/banner2.png",
            "image_type": "main_picture"
        },
        {
            "image_path": "banners/banner3.png",
            "image_type": "main_picture"
        },
        # Додай більше за потребою...
    ]
}
cross_banner_list = [
    {"type": "photo_background"}
]
picture_data_ross_banner_list = {
    "Галерея для нових банерів": [
        {
            "image_path": "banners/banner.png",  #
            "image_type": "main_picture"
        },
    ]}
