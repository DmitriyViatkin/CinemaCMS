document.addEventListener('DOMContentLoaded', function() {
    const addPictureFormBtn = document.getElementById('add-picture-form');
    const galleryFormsetContainer = document.getElementById('gallery-formset');
    const emptyFormTemplate = document.getElementById('empty-picture-form');
    const totalForms = document.getElementById('id_form-TOTAL_FORMS');

    function addPictureForm() {
        const newForm = emptyFormTemplate.content.cloneNode(true);
        const formRegex = RegExp(`__prefix__`, 'g');
        const formIndex = parseInt(totalForms.value);

        newForm.querySelectorAll('label').forEach(label => {
            const forAttr = label.getAttribute('for');
            if (forAttr) {
                label.setAttribute('for', forAttr.replace(formRegex, `form-${formIndex}`));
            }
        });

        newForm.querySelectorAll('input, select, textarea').forEach(input => {
            const nameAttr = input.getAttribute('name');
            if (nameAttr) {
                input.setAttribute('name', nameAttr.replace(formRegex, `form-${formIndex}`));
                const idAttr = input.getAttribute('id');
                if (idAttr) {
                    input.setAttribute('id', idAttr.replace(formRegex, `id_form-${formIndex}`));
                }
            }
        });

        galleryFormsetContainer.appendChild(newForm);
        totalForms.value = formIndex + 1;
    }

    addPictureFormBtn.addEventListener('click', addPictureForm);
});