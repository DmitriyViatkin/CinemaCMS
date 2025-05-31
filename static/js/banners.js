(function($) {
    $(function() {
        // Змінні для попереднього перегляду окремого зображення
        const imageInput = document.getElementById('image-input');
        const previewImg = document.getElementById('preview-img');
        const previewPlaceholder = document.getElementById('preview-placeholder');

        if (imageInput) {
            imageInput.addEventListener('change', function () {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        if (previewImg) {
                            previewImg.src = e.target.result;
                        } else if (previewPlaceholder) {
                            const img = document.createElement('img');
                            img.id = 'preview-img';
                            img.src = e.target.result;
                            img.style.width = '120px';
                            img.style.border = '1px solid #ccc';
                            previewPlaceholder.replaceWith(img);
                        }
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
// Обробник для завантаження зображення крос-банера
        // Обробник для завантаження зображення крос-банера
        $('#id_cross_banner-image').on('change', function() {
            const file = this.files[0];
            const previewImage = $('#preview-img'); // Знаходимо існуючий елемент preview-img
            const previewPlaceholder = $('#preview-placeholder');

            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImage.attr('src', e.target.result); // Оновлюємо src існуючого елемента
                    if (previewPlaceholder.length) {
                        previewPlaceholder.hide(); // Приховуємо заглушку, якщо є
                    }
                }
                reader.readAsDataURL(file);
            } else {
                previewImage.attr('src', '#'); // Очищаємо src, якщо файл не вибрано
                if (previewPlaceholder.length) {
                    previewPlaceholder.show(); // Показуємо заглушку, якщо файл видалено
                }
            }
        });
        function updateImagePreview(input) {
            const file = input.files[0];
            if (file) {
                const reader = new FileReader();
                const preview = $(input).closest('.banner-unit').find('.preview');
                reader.onload = e => {
                    preview.attr('src', e.target.result).show();
                };
                reader.readAsDataURL(file);
            } else {
                $(input).closest('.banner-unit').find('.preview').attr('src', '#').hide();
            }
        }

        $(document).on('change', '[id$="-main_picture"]', function() {
            updateImagePreview(this);
        });

        $('#add-banner-form').on('click', function () {
            console.log('Кнопку "Додати банер" натиснуто!'); // Код відладки

            const template = $('#empty-form-template').html();
            const container = $('#banner-container');
            const totalForms = $('#id_top_banners-TOTAL_FORMS');

            if (!totalForms.length) {
                console.error('TOTAL_FORMS для верхніх банерів не знайдено!');
                return;
            }

            const formCount = parseInt(totalForms.val(), 10);
            const newFormHtml = template.replace(/__prefix__/g, formCount);

            const $newForm = $(newFormHtml).removeAttr('style');

            $newForm.find(':input').each(function() {
                const name = $(this).attr('name')?.replace('__prefix__', formCount);
                const id = $(this).attr('id')?.replace('__prefix__', formCount);
                if (name) $(this).attr('name', name);
                if (id) $(this).attr('id', id);
                if (this.type !== 'checkbox') $(this).val('');
                if (this.type === 'file') $(this).val(null);
                $(this).closest('.banner-unit').find('.preview').attr('src', '#').hide();
            });

            $newForm.find('label').each(function() {
                const newFor = $(this).attr('for')?.replace('__prefix__', formCount);
                if (newFor) $(this).attr('for', newFor);
            });

            container.append($newForm);
            totalForms.val(formCount + 1);

            updateGlobalControls();
        });

       $('#add-banner-form-news').on('click', function () {
    console.log('Кнопку "Додати новину" натиснуто!'); // Код відладки

    const template = $('#empty-form-template-news').html(); // витяг HTML з <template>
    const container = $('#banner-container-news');
    const totalForms = container.closest('form').find('input[name="news-TOTAL_FORMS"]');

    if (!totalForms.length) {
        console.error('TOTAL_FORMS для новин не знайдено!');
        return;
    }

    const formCount = parseInt(totalForms.val(), 10);
    const newFormHtml = template.replace(/__prefix__/g, formCount); // заміна __prefix__

    const $newForm = $(newFormHtml).removeAttr('style');

    $newForm.find(':input').each(function() {
        const name = $(this).attr('name')?.replace('__prefix__', formCount);
        const id = $(this).attr('id')?.replace('__prefix__', formCount);
        if (name) $(this).attr('name', name);
        if (id) $(this).attr('id', id);
        if (this.type !== 'checkbox') $(this).val('');
        if (this.type === 'file') $(this).val(null);
    });

    $newForm.find('label').each(function() {
        const newFor = $(this).attr('for')?.replace('__prefix__', formCount);
        if (newFor) $(this).attr('for', newFor);
    });

    container.append($newForm);
    totalForms.val(formCount + 1);

    updateGlobalNewsControls();
});


        $(document).on('click', '.remove-banner-btn', function() {
            const form = $(this).closest('.banner-unit');
            const deleteInput = form.find('[name$="-DELETE"]');
            const idInput = form.find('[name$="-id"]');

            if (idInput.val()) {
                deleteInput.prop('checked', true);
                form.hide();
            } else {
                form.remove();
            }
        });

        // Глобальне керування станом "Показувати" для банерів
        $('#global-is-active').on('change', function() {
            const globalIsActive = $(this).prop('checked');
            $('[id$="-is_active"]').prop('checked', globalIsActive);
        });

        // Глобальне оновлення швидкості прокрутки для банерів
        $('#global-scroll-speed').on('change', function() {
            const globalSpeed = $(this).val();
            $('[id$="-scroll_speed"]').val(globalSpeed);
        });

        // Автосинхронізація стану чекбоксів для банерів
        function updateGlobalControls() {
            const total = $('[id^="id_top_banners-"][id$="-is_active"]').length;
            const checked = $('[id^="id_top_banners-"][id$="-is_active"]:checked').length;
            const allActive = total > 0 && total === checked;
            $('#global-is-active').prop('checked', allActive);

            const firstSpeed =  $('[id^="id_top_banners-"][id$="-scroll_speed"]').first().val();
            const allSame = $('[id^="id_top_banners-"][id$="-scroll_speed"]').toArray().every(input => $(input).val() === firstSpeed);
            if (allSame) {
                $('#global-scroll-speed').val(firstSpeed);
            }
        }

        // Глобальне керування станом "Показувати" для новин
        $('#global-is-active-news').on('change', function() {
            const globalIsActiveNews = $(this).prop('checked');
            $('[id^="id_news-"][id$="-is_active"]').prop('checked', globalIsActiveNews);
        });

        // Глобальне оновлення швидкості прокрутки для новин
        $('#global-scroll-speed-news').on('change', function() {
            const globalSpeedNews = $(this).val();
            $('[id^="id_news-"][id$="-scroll_speed"]').val(globalSpeedNews);
        });

        // Автосинхронізація стану чекбоксів для новин
        function updateGlobalNewsControls() {
            const totalNews = $('[id^="id_news-"][id$="-is_active"]').length;
            const checkedNews = $('[id^="id_news-"][id$="-is_active"]:checked').length;
            const allActiveNews = totalNews > 0 && totalNews === checkedNews;
            $('#global-is-active-news').prop('checked', allActiveNews);

            const firstSpeedNews = $('[id^="id_news-"][id$="-scroll_speed"]').first().val();
            const allSameNews = $('[id^="id_news-"][id$="-scroll_speed"]').toArray().every(input => $(input).val() === firstSpeedNews);
            if (allSameNews) {
                $('#global-scroll-speed-news').val(firstSpeedNews);
            }
        }

        // Відображення існуючих зображень при завантаженні
        $('.banner-unit').each(function() {
            const preview = $(this).find('.preview');
            const imageUrl = preview.attr('src');
            if (imageUrl && imageUrl !== '#') {
                preview.show();
            }
        });

        // ініціалізація при завантаженні
        updateGlobalControls();
        updateGlobalNewsControls();
    });
})(jQuery);