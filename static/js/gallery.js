// static/js/gallery.js (или add_movie.js, если вы его еще не переименовали)

// Объявление DEFAULT_IMAGE_URL должно быть в вашем HTML-шаблоне ОДИН РАЗ,
// перед подключением этого файла.

document.addEventListener('DOMContentLoaded', function() {

    // --- ФУНКЦИИ-ПОМОЩНИКИ ---

    function previewImage(input, previewContainer, maxWidth, maxHeight) {
        const imgElement = previewContainer.querySelector('img');
        // ИСПРАВЛЕНО: ищем remove-item-cross
        const removeCrossBtn = previewContainer.querySelector('.remove-item-cross');

        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imgElement.src = e.target.result;
                imgElement.style.maxWidth = maxWidth + 'px';
                imgElement.style.maxHeight = maxHeight + 'px';
                if (removeCrossBtn) {
                    removeCrossBtn.style.display = 'block';
                }
            };
            reader.readAsDataURL(input.files[0]);
        } else {
            if (imgElement.src !== DEFAULT_IMAGE_URL) {
                imgElement.src = DEFAULT_IMAGE_URL;
            }
            if (removeCrossBtn) {
                removeCrossBtn.style.display = 'none';
            }
        }
    }

    function updateFormIndices(formElement, newIndex) {
        formElement.querySelectorAll('input, select, textarea, label').forEach(node => {
            let id = node.getAttribute('id');
            let name = node.getAttribute('name');
            let htmlFor = node.getAttribute('for');

            const regex = /(\w+)-(\d+|__prefix__)-(\w+)/;

            if (id && regex.test(id)) {
                node.setAttribute('id', id.replace(regex, `$1-${newIndex}-$3`));
            }
            if (name && regex.test(name)) {
                node.setAttribute('name', name.replace(regex, `$1-${newIndex}-$3`));
            }
            if (htmlFor && regex.test(htmlFor)) {
                node.setAttribute('for', htmlFor.replace(regex, `$1-${newIndex}-$3`));
            }
        });
    }

    function hideGalleryFormFields(form) {
        const fieldsToHide = ['id', 'image_type', 'gallery'];
        fieldsToHide.forEach(fieldName => {
            const field = form.querySelector(`[id$="-${fieldName}"]`);
            if (field) {
                const formGroup = field.closest('.form-group');
                if (formGroup) {
                    formGroup.style.display = 'none';
                } else {
                    field.style.display = 'none';
                }
            }
            const label = form.querySelector(`label[for$="-${fieldName}"]`);
            if (label) {
                label.style.display = 'none';
            }
        });
    }

    function initializeImageForm(containerSelector, formPrefix) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        const fileInput = container.querySelector('input[type="file"]');
        // ИСПРАВЛЕНО: ищем image-preview-container
        const previewContainer = container.querySelector('.image-preview-container');
        const customFileButton = container.querySelector('.custom-file-button');
        // ИСПРАВЛЕНО: ищем remove-item-cross
        const removeCrossBtn = previewContainer ? previewContainer.querySelector('.remove-item-cross') : null;
        const deleteCheckbox = container.querySelector(`input[type="checkbox"][name$="${formPrefix}-DELETE"]`);

        const updatePreviewAndCrossVisibility = (file) => {
            if (!previewContainer) return; // Добавлена проверка на всякий случай

            const imgElement = previewContainer.querySelector('img');
            if (!imgElement) return; // Добавлена проверка

            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    imgElement.src = e.target.result;
                    if (removeCrossBtn) removeCrossBtn.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                imgElement.src = DEFAULT_IMAGE_URL;
                if (removeCrossBtn) removeCrossBtn.style.display = 'none';
            }
        };

        if (previewContainer && previewContainer.querySelector('img')) { // Убедимся, что img существует
            const currentImgSrc = previewContainer.querySelector('img').src;
            if (currentImgSrc && !currentImgSrc.includes(DEFAULT_IMAGE_URL)) {
                if (removeCrossBtn) removeCrossBtn.style.display = 'block';
            } else {
                if (removeCrossBtn) removeCrossBtn.style.display = 'none';
            }
        }


        if (fileInput) {
            fileInput.addEventListener('change', function() {
                updatePreviewAndCrossVisibility(this.files[0]);
                if (deleteCheckbox) deleteCheckbox.checked = false;
            });
        }

        if (customFileButton) {
            customFileButton.addEventListener('click', function() {
                fileInput.click();
            });
        }

        if (removeCrossBtn) {
            removeCrossBtn.addEventListener('click', function(event) {
                event.preventDefault();
                if (fileInput) fileInput.value = '';
                updatePreviewAndCrossVisibility(null);
                if (deleteCheckbox) deleteCheckbox.checked = true;
            });
        }

        hideGalleryFormFields(container);
    }


    // --- ОСНОВНАЯ ЛОГИКА DOMContentLoaded ---

    initializeImageForm('.main-picture-form', 'main_picture_form');
    initializeImageForm('.banner-form-container', 'banner_form');
    initializeImageForm('.hall-scheme-container', 'logo_form');


    const addPictureFormButton = document.getElementById('add-picture-form');
    const picturesFormsetContainer = document.getElementById('pictures-formset');

    const emptyFormTemplateWrapper = document.getElementById('empty-form');
    let emptyFormTemplate = null;
    if (emptyFormTemplateWrapper) {
        emptyFormTemplate = emptyFormTemplateWrapper.querySelector('.gallery-image-form');
    }

    if (!emptyFormTemplate) {
        console.error("Empty form template for gallery not found! Check #empty-form structure.");
    }

    const totalForms = document.querySelector('#id_pictures-TOTAL_FORMS');
    let formCount = 0;

    const updateActualFormCount = () => {
        formCount = picturesFormsetContainer.querySelectorAll('.gallery-image-form:not([style*="display: none"])').length;
        if (totalForms) totalForms.value = formCount;
    };


    const initializeGalleryForm = (form) => {
        const fileInput = form.querySelector('input[type="file"]');
        // ИСПРАВЛЕНО: ищем image-preview-container
        const previewContainer = form.querySelector('.image-preview-container');
        const customFileButton = form.querySelector('.custom-file-button');
        // ИСПРАВЛЕНО: ищем remove-item-cross
        const removeCrossBtn = previewContainer ? previewContainer.querySelector('.remove-item-cross') : null;
        const removeFullBtn = form.querySelector('.remove-gallery-btn');

        if (previewContainer && previewContainer.querySelector('img')) { // Убедимся, что img существует
            const currentImgSrc = previewContainer.querySelector('img').src;
            if (currentImgSrc && !currentImgSrc.includes(DEFAULT_IMAGE_URL)) {
                if (removeCrossBtn) {
                    removeCrossBtn.style.display = 'block';
                }
            } else {
                if (removeCrossBtn) {
                    removeCrossBtn.style.display = 'none';
                }
            }
        }


        if (fileInput && previewContainer) {
            fileInput.addEventListener('change', function() {
                previewImage(this, previewContainer, 100, 100);
                const deleteCheckbox = form.querySelector('input[type="checkbox"][name$="-DELETE"]');
                if (deleteCheckbox) deleteCheckbox.checked = false;
            });

            if (customFileButton) {
                customFileButton.addEventListener('click', function() {
                    fileInput.click();
                });
            }
        }

        if (removeCrossBtn) {
            removeCrossBtn.addEventListener('click', function(event) {
                event.preventDefault();
                handleGalleryRemoval(form);
            });
        }

        if (removeFullBtn) {
            removeFullBtn.addEventListener('click', function(event) {
                event.preventDefault();
                handleGalleryRemoval(form);
            });
        }

        hideGalleryFormFields(form);
    };

    const handleGalleryRemoval = (formToDelete) => {
        const deleteCheckbox = formToDelete.querySelector('input[type="checkbox"][name$="-DELETE"]');
        // ИСПРАВЛЕНО: ищем image-preview-container, затем img
        const imagePreviewImg = formToDelete.querySelector('.image-preview-container img');
        const fileInputToClear = formToDelete.querySelector('input[type="file"]');
        // ИСПРАВЛЕНО: ищем remove-item-cross
        const removeCrossBtn = formToDelete.querySelector('.remove-item-cross');

        if (deleteCheckbox) {
            deleteCheckbox.checked = true;
        }
        if (fileInputToClear) {
            fileInputToClear.value = '';
        }
        if (imagePreviewImg) {
            imagePreviewImg.src = DEFAULT_IMAGE_URL;
        }
        if (removeCrossBtn) {
            removeCrossBtn.style.display = 'none';
        }

        formToDelete.style.display = 'none';

        updateActualFormCount();
        picturesFormsetContainer.querySelectorAll('.gallery-image-form:not([style*="display: none"])').forEach((form, index) => {
            updateFormIndices(form, index);
            hideGalleryFormFields(form);
        });
    };


    if (picturesFormsetContainer) {
        picturesFormsetContainer.querySelectorAll('.gallery-image-form').forEach(form => {
            initializeGalleryForm(form);
            const deleteCheckbox = form.querySelector('input[type="checkbox"][name$="-DELETE"]');
            if (deleteCheckbox && deleteCheckbox.checked) {
                form.style.display = 'none';
            }
        });
        updateActualFormCount();
    }

    if (addPictureFormButton) {
        addPictureFormButton.addEventListener('click', function() {
            if (!emptyFormTemplate) {
                console.error("Empty form template is missing. Cannot add new form.");
                return;
            }

            const newForm = emptyFormTemplate.cloneNode(true);
            newForm.style.display = '';
            newForm.dataset.exists = "false";

            updateFormIndices(newForm, formCount);

            newForm.querySelectorAll('input:not([type="hidden"]):not([type="checkbox"]), select, textarea').forEach(input => {
                if (input.tagName === 'SELECT') {
                    input.selectedIndex = 0;
                } else {
                    input.value = '';
                }
            });

            const newDeleteCheckbox = newForm.querySelector('input[type="checkbox"][name$="-DELETE"]');
            if (newDeleteCheckbox) {
                newDeleteCheckbox.checked = false;
            }

            // ИСПРАВЛЕНО: ищем image-preview-container, затем img
            const newFormPreviewImg = newForm.querySelector('.image-preview-container img');
            // ИСПРАВЛЕНО: ищем remove-item-cross
            const newFormRemoveCrossBtn = newForm.querySelector('.image-preview-container .remove-item-cross');
            if (newFormPreviewImg) {
                newFormPreviewImg.src = DEFAULT_IMAGE_URL;
            }
            if (newFormRemoveCrossBtn) {
                newFormRemoveCrossBtn.style.display = 'none';
            }

            if (picturesFormsetContainer) {
                picturesFormsetContainer.appendChild(newForm);
                initializeGalleryForm(newForm);
            }

            updateActualFormCount();
        });
    }

    if (emptyFormTemplate) {
        hideGalleryFormFields(emptyFormTemplate);
    }

    // --- ИНИЦИАЛИЗАЦИЯ JQUERY ПЛАГИНОВ (если они должны быть внутри DOMContentLoaded) ---
    $(function () {
      $('#reservationdatetime').datetimepicker({ icons: { time: 'far fa-clock' } });
      $('#reservation').daterangepicker({ singleDatePicker: true, showDropdowns: true, locale: { format: 'MM/DD/YYYY' } });
      $('#timepicker').datetimepicker({ format: 'LT' });
      $('input[data-bootstrap-switch]').each(function(){
          $(this).bootstrapSwitch('state', $(this).prop('checked'));
      });
    });
});