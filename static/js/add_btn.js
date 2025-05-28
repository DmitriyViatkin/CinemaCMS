document.addEventListener('DOMContentLoaded', function () {
    const addButton = document.getElementById('add-picture-form');
    if (!addButton) return;  // ← Запобігає помилці, якщо кнопка відсутня

    const formsetContainer = document.getElementById('gallery-formset');
    const emptyFormTemplate = document.getElementById('empty-picture-form').innerHTML;
    const totalForms = document.querySelector('#id_pictures-TOTAL_FORMS');

    addButton.addEventListener('click', function () {
        const formCount = parseInt(totalForms.value);
        const newFormHtml = emptyFormTemplate.replace(/__prefix__/g, formCount);
        formsetContainer.insertAdjacentHTML('beforeend', newFormHtml);
        totalForms.value = formCount + 1;
    });

    formsetContainer.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-form')) {
            const formBlock = e.target.closest('.gallery-image-form');
            formBlock.remove();
            totalForms.value = document.querySelectorAll('.gallery-image-form').length;
        }
    });
});
