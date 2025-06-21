document.addEventListener('DOMContentLoaded', function() {
    // Теперь нам нужен только GLOBAL_CURRENT_SEAT_STATUS_DATA
    const currentSeatStatusData = window.GLOBAL_CURRENT_SEAT_STATUS_DATA;

    console.log("Данные о текущем статусе мест из Django (hallScheme.js):", currentSeatStatusData);

    const hallSchemeContainer = document.getElementById('hall-scheme-container');
    const selectedSeatsInput = document.getElementById('selected-seats-input');
    const selectedSeatsCountSpan = document.getElementById('selected-seats-count');
    const totalPriceSpan = document.getElementById('total-price');
    const purchaseButton = document.getElementById('purchase-button');

    let selectedSeats = [];
    let totalPrice = 0;

    // --- Core Functions for Hall Scheme Rendering and Interaction ---

    // Функция mergeSchemeAndStatus больше не нужна, так как мы не объединяем файлы

    /**
     * Renders the hall scheme using SVG based on provided seat data.
     * @param {Array} schemeData - The seat data directly from Django (already merged with status).
     * @param {string} containerId - The ID of the HTML element where the SVG should be rendered.
     */
    function renderHallScheme(schemeData, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = ''; // Очищаем контейнер

        if (!schemeData || schemeData.length === 0) {
            container.innerHTML = '<p>Нет данных о рядах и местах для отображения схемы зала.</p>';
            return;
        }

        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("width", "100%");
        svg.style.height = "auto";
        svg.style.border = "1px solid #ccc";
        svg.style.backgroundColor = "#f9f9f9";

        const seatSize = 40;
        const seatSpacing = 15;
        const rowSpacing = 60;
        const startX = 70;
        const startY = 50;

        let currentY = startY;
        let maxX = 0;

        // Ensure rows are sorted by row_number (это уже должно быть сделано в views.py)
        schemeData.sort((a, b) => a.row_number - b.row_number);

        schemeData.forEach(rowData => {
            const rowNumber = rowData.row_number;
            const seats = rowData.seats;

            // Ensure seats within a row are sorted by seat_number (это уже должно быть сделано в views.py)
            seats.sort((a, b) => a.seat_number - b.seat_number);

            let currentX = startX;

            // Метка ряда
            const rowLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
            rowLabel.setAttribute("x", startX - 10);
            rowLabel.setAttribute("y", currentY + seatSize / 2);
            rowLabel.setAttribute("dominant-baseline", "middle");
            rowLabel.setAttribute("text-anchor", "end");
            rowLabel.style.fontSize = "16px";
            rowLabel.style.fontWeight = "bold";
            rowLabel.textContent = `Ряд ${rowNumber}`;
            svg.appendChild(rowLabel);

            seats.forEach(seatData => {
                const seatId = seatData.id;
                const seatNumber = seatData.seat_number;
                const status = seatData.status; // 'F', 'S', 'N'
                const isVip = seatData.is_vip;
                const price = seatData.price;

                const seatElement = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                seatElement.setAttribute("x", currentX);
                seatElement.setAttribute("y", currentY);
                seatElement.setAttribute("width", seatSize);
                seatElement.setAttribute("height", seatSize);
                seatElement.setAttribute("rx", 5);

                seatElement.classList.add('seat', 'svg-seat');

                // Apply status and VIP classes
                if (status === 'F') { // Free
                    seatElement.classList.add('free');
                } else if (status === 'S') { // Sold/Occupied
                    seatElement.classList.add('occupied');
                } else { // 'N' - Not available (e.g., gangway)
                    seatElement.classList.add('unavailable');
                }
                if (isVip) {
                    seatElement.classList.add('vip');
                }

                // Add data attributes for JS logic
                if (seatId) { // Only if the seat has an actual DB ID
                    seatElement.dataset.seatId = seatId;
                    seatElement.dataset.row = rowNumber;
                    seatElement.dataset.seat = seatNumber;
                    seatElement.dataset.price = price;
                    seatElement.dataset.status = status; // Базовый статус
                } else {
                    // For "placeholder" seats (gangways, etc.) that don't have a DB ID
                    seatElement.dataset.status = 'N'; // Always unavailable
                }


                const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
                title.textContent = `Ряд: ${rowNumber}, Место: ${seatNumber}\nСтатус: ${
                    status === 'F' ? 'Свободно' : (status === 'S' ? 'Занято' : 'Недоступно')
                }\nЦена: ${price !== undefined ? price + ' грн' : 'N/A'}`; // Добавил проверку на undefined для price
                seatElement.appendChild(title);

                seatElement.addEventListener('click', () => {
                    // Можно выбрать только свободные места, у которых есть ID в БД
                    if (seatId && status === 'F') {
                        const currentSeatId = seatElement.dataset.seatId;
                        const currentSeatPrice = parseFloat(seatElement.dataset.price);

                        if (seatElement.classList.contains('selected')) {
                            // Отмена выбора
                            seatElement.classList.remove('selected');
                            selectedSeats = selectedSeats.filter(id => id.toString() !== currentSeatId);
                            totalPrice -= currentSeatPrice;
                        } else {
                            // Выбор
                            seatElement.classList.add('selected');
                            selectedSeats.push(currentSeatId);
                            totalPrice += currentSeatPrice;
                        }
                        updateSelectionDisplay();
                    } else if (!seatId) {
                        alert('Это место не определено в системе (нет ID в БД) и не может быть выбрано.');
                    } else {
                        alert(`Место Ряд ${rowNumber}, Место ${seatNumber} уже занято или недоступно.`);
                    }
                });

                svg.appendChild(seatElement);

                // Номер места
                const seatText = document.createElementNS("http://www.w3.org/2000/svg", "text");
                seatText.setAttribute("x", currentX + seatSize / 2);
                seatText.setAttribute("y", currentY + seatSize / 2);
                seatText.setAttribute("text-anchor", "middle");
                seatText.setAttribute("dominant-baseline", "middle");
                seatText.style.fontSize = "12px";
                seatText.style.fill = "#fff";
                seatText.style.pointerEvents = "none"; // Чтобы клики проходили через текст
                seatText.textContent = seatNumber;
                svg.appendChild(seatText);

                currentX += seatSize + seatSpacing;
            });

            // Обновляем максимальную ширину SVG
            if (currentX > maxX) {
                maxX = currentX;
            }

            currentY += seatSize + rowSpacing;
        });

        container.appendChild(svg);

        // Динамически устанавливаем viewBox, чтобы вместить все элементы
        const finalWidth = maxX + startX; // Отступ справа
        const finalHeight = currentY + startY; // Отступ снизу
        svg.setAttribute("viewBox", `0 0 ${finalWidth} ${finalHeight}`);
        svg.setAttribute("width", finalWidth); // Устанавливаем фактическую ширину
        svg.setAttribute("height", finalHeight); // Устанавливаем фактическую высоту
        svg.style.width = "100%"; // Но отображаем на всю ширину контейнера
    }

    // --- Функции для управления выбором и отображением формы ---
    function updateSelectionDisplay() {
        selectedSeatsCountSpan.textContent = selectedSeats.length;
        totalPriceSpan.textContent = totalPrice.toFixed(2);
        selectedSeatsInput.value = JSON.stringify(selectedSeats);

        // Включаем/отключаем кнопку покупки
        purchaseButton.disabled = selectedSeats.length === 0;

        // Обновляем визуальный статус выбранных мест в SVG
        document.querySelectorAll('.seat.svg-seat').forEach(seatElement => {
            const seatId = seatElement.dataset.seatId;
            if (seatId && selectedSeats.includes(seatId.toString())) { // Преобразуем id в строку для сравнения
                seatElement.classList.add('selected');
            } else if (seatElement.classList.contains('selected') && !selectedSeats.includes(seatId.toString())) {
                seatElement.classList.remove('selected');
            }
        });
    }

    // --- Логика Инициализации ---
    // Это точка входа для отрисовки схемы зала. Теперь вызываем renderHallScheme напрямую.
    if (currentSeatStatusData && currentSeatStatusData.length > 0) {
        renderHallScheme(currentSeatStatusData, 'hall-scheme-container');
    } else {
        hallSchemeContainer.innerHTML = '<p>Нет данных о местах для отображения схемы зала.</p>';
    }
});