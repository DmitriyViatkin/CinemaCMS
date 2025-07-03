document.addEventListener('DOMContentLoaded', function () {
    const totalForms = document.getElementById('id_pictures-TOTAL_FORMS');
    const picturesFormsetContainer = document.getElementById('pictures-formset');
    const addPictureFormButton = document.getElementById('add-picture-form');
    const emptyPictureTemplate = document.getElementById('empty-picture-template').innerHTML;

    if (!totalForms || !picturesFormsetContainer || !addPictureFormButton || !emptyPictureTemplate) {
        console.error('Один або кілька елементів для formset не знайдено.');
        return;
    }

    let formNum = parseInt(totalForms.value);

    addPictureFormButton.addEventListener('click', function () {
        const newFormHTML = emptyPictureTemplate.replace(/__prefix__/g, formNum);
        const newFormElement = document.createElement('div');
        newFormElement.innerHTML = newFormHTML;
        const formItem = newFormElement.firstElementChild;

        const imageInput = formItem.querySelector('input[type="file"]');
        const previewBox = formItem.querySelector('div[style*="border: 1px dashed"]');

        if (imageInput) {
            imageInput.addEventListener('change', function (e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function (ev) {
                        const img = document.createElement('img');
                        img.src = ev.target.result;
                        img.style.maxWidth = '100%';
                        img.style.maxHeight = '80px';
                        previewBox.innerHTML = '';
                        previewBox.appendChild(img);
                    };
                    reader.readAsDataURL(file);
                }
            });
        }

        picturesFormsetContainer.appendChild(formItem);
        formNum++;
        totalForms.value = formNum;
    });

    picturesFormsetContainer.addEventListener('click', function (event) {
        if (event.target.classList.contains('form-check-input') && event.target.name.endsWith('-DELETE')) {
            const formToDelete = event.target.closest('.gallery-image-item');
            if (formToDelete) {
                formToDelete.style.display = 'none';
                event.target.checked = true;
            }
        }
    });

    picturesFormsetContainer.querySelectorAll('input[type="file"]').forEach(function (input) {
        const container = input.closest('.gallery-image-item');
        const previewBox = container.querySelector('img') || container.querySelector('div[style*="border: 1px dashed"]');

        input.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (ev) {
                    const img = document.createElement('img');
                    img.src = ev.target.result;
                    img.style.maxWidth = '100%';
                    img.style.maxHeight = '80px';
                    if (previewBox.tagName === 'IMG') {
                        previewBox.src = ev.target.result;
                    } else {
                        previewBox.innerHTML = '';
                        previewBox.appendChild(img);
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });

 // Logo image preview
    const logoInput = document.getElementById('logo-image-input');
    const logoPreviewContainer = document.getElementById('logo-preview');

    if (logoInput && logoPreviewContainer) {
        logoInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (ev) {
                    // Видаляємо все у контейнері та додаємо img
                    logoPreviewContainer.innerHTML = '';
                    const img = document.createElement('img');
                    img.src = ev.target.result;
                    img.style.maxWidth = '100%';
                    img.style.maxHeight = '100%';
                    img.style.objectFit = 'contain';
                    logoPreviewContainer.appendChild(img);
                };
                reader.readAsDataURL(file);
            }
        });
    }
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
    // Banner image preview

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
});