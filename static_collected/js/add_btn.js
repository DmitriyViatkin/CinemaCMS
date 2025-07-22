document.addEventListener('DOMContentLoaded', function () {
    const addButton = document.getElementById('add-picture-form');
    const formsetContainer = document.getElementById('gallery-formset');
    const emptyFormTemplate = document.getElementById('empty-picture-form').innerHTML;
    const totalForms = document.querySelector('#id_pictures-TOTAL_FORMS');

    if (addButton && formsetContainer && emptyFormTemplate && totalForms) {
        addButton.addEventListener('click', function () {
            const formCount = parseInt(totalForms.value);
            const newFormHtml = emptyFormTemplate.replace(/__prefix__/g, formCount);
            formsetContainer.insertAdjacentHTML('beforeend', newFormHtml);
            totalForms.value = formCount + 1;
            initializeImagePreview(formsetContainer.lastElementChild);
        });

        formsetContainer.addEventListener('click', function (e) {
            if (e.target.classList.contains('remove-form')) {
                const formBlock = e.target.closest('.gallery-image-form');
                formBlock.remove();
                totalForms.value = document.querySelectorAll('.gallery-image-form').length;
            }
        });
    }

    function initializeImagePreview(formElement) {
        const imageInput = formElement.querySelector('input[type="file"]');
        const imagePreview = formElement.querySelector('.image-preview');

        if (imageInput && imagePreview) {
            imageInput.addEventListener('change', function () {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        imagePreview.innerHTML = `<img src="${e.target.result}" style="max-width: 100%; max-height: 100%;">`;
                    };
                    reader.readAsDataURL(file);
                } else {
                    imagePreview.innerHTML = '';
                }
            });
        }
    }

    // Ініціалізація для існуючих форм галереї
    document.querySelectorAll('.gallery-image-form').forEach(initializeImagePreview);

    // Ініціалізація банера
    const bannerImageInput = document.querySelector('.banner-form input[type="file"]');
    const bannerImagePreview = document.querySelector('.banner-form .image-preview');
    if (bannerImageInput && bannerImagePreview) {
        bannerImageInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    bannerImagePreview.innerHTML = `<img src="${e.target.result}" style="max-width: 100%; max-height: 100%;">`;
                };
                reader.readAsDataURL(file);
            } else {
                bannerImagePreview.innerHTML = '';
            }
        });
    }

    // Ініціалізація логотипа
    const logoImageInput = document.querySelector('.main-picture-form input[type="file"]');
    const logoImagePreview = document.querySelector('.main-picture-form .image-preview');
    if (logoImageInput && logoImagePreview) {
        logoImageInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    logoImagePreview.innerHTML = `<img src="${e.target.result}" style="max-width: 100%; max-height: 100%;">`;
                };
                reader.readAsDataURL(file);
            } else {
                logoImagePreview.innerHTML = '';
            }
        });
    }
});