  // static/js/tabs.js
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');

    // Перевіряємо, чи є кнопки та панелі
    if (tabButtons.length === 0 || tabPanes.length === 0) {
        console.warn("Вкладки не знайдені. Перевірте HTML-структуру.");
        return; // Якщо немає вкладок, виходимо
    }

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTabId = button.dataset.tabTarget;
            const targetPane = document.querySelector(targetTabId);

            // Якщо цільова панель не знайдена, виходимо
            if (!targetPane) {
                console.error(`Панель з ID ${targetTabId} не знайдена.`);
                return;
            }

            // Видаляємо 'active' клас з усіх кнопок та панелей
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));


            button.classList.add('active');

            // Показуємо відповідну панель вмісту
            targetPane.classList.add('active');
        });
    });


});