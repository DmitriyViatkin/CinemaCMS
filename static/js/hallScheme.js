document.addEventListener('DOMContentLoaded', function() {
    // These variables will be defined in the HTML template's inline script
    // before this external script runs.
    const schemeFileUrl = window.GLOBAL_SCHEME_FILE_URL; // From template
    const currentSeatStatusData = window.GLOBAL_CURRENT_SEAT_STATUS_DATA; // From template

    console.log("[DEBUG] DOMContentLoaded - Script started.");
    console.log("[DEBUG] URL файла схемы зала (JSON) from external JS:", schemeFileUrl);
    console.log("[DEBUG] Данные о текущем статусе мест из Django from external JS:", currentSeatStatusData);

    const hallSchemeContainer = document.getElementById('hall-scheme-container');
    const selectedSeatsInput = document.getElementById('selected-seats-input');
    const selectedSeatsCountSpan = document.getElementById('selected-seats-count');
    const totalPriceSpan = document.getElementById('total-price');
    const purchaseButton = document.getElementById('purchase-button');

    let selectedSeats = [];
    let totalPrice = 0;

    // --- Core Functions for Hall Scheme Rendering and Interaction ---

    /**
     * Merges a base hall scheme (from JSON file) with current seat status data (from Django DB).
     * @param {Object} baseScheme - The scheme data loaded from the JSON file.
     * @param {Array} currentStatus - An array of seat rows with current status from Django.
     * @returns {Array} An array of merged seat rows, ready for rendering.
     */
    function mergeSchemeAndStatus(baseScheme, currentStatus) {
        console.log("[DEBUG] mergeSchemeAndStatus - Merging base scheme with current status.");
        const mergedRows = [];
        const currentStatusMap = new Map();

        // Create a Map for quick access to current statuses by seat ID
        currentStatus.forEach(row => {
            row.seats.forEach(seat => {
                if (seat.id) {
                    currentStatusMap.set(seat.id.toString(), seat);
                } else {
                    console.warn(`[DEBUG] mergeSchemeAndStatus - Seat without ID found in currentStatus: Row ${row.row_number}, Seat ${seat.seat_number}`);
                }
            });
        });
        console.log("[DEBUG] currentStatusMap created:", currentStatusMap);


        if (baseScheme.rows) {
            baseScheme.rows.forEach(baseRow => {
                const newSeats = baseRow.seats.map(baseSeat => {
                    const currentSeat = currentStatusMap.get(baseSeat.id ? baseSeat.id.toString() : null);
                    if (currentSeat) {
                        // console.log(`[DEBUG] Merging seat ID ${baseSeat.id}: Base ${baseSeat.status}, Current ${currentSeat.status}`);
                        return {
                            ...baseSeat, // Copy static data from base scheme
                            status: currentSeat.status, // Override with dynamic status
                            is_vip: currentSeat.is_vip, // Override
                            price: currentSeat.price // Override
                        };
                    }
                    // If a seat from the base scheme isn't found in currentStatus (e.g., deleted from DB),
                    // default its status to unavailable.
                    console.warn(`[DEBUG] Seat ID ${baseSeat.id} from base scheme not found in current status. Defaulting to unavailable.`);
                    return {
                        ...baseSeat,
                        status: baseSeat.status || 'N', // Use base status or 'N'
                        price: baseSeat.price || 0.0,
                        is_vip: baseSeat.is_vip || false
                    };
                });
                mergedRows.push({
                    row_number: baseRow.row_number,
                    seats: newSeats
                });
            });
        } else {
            console.warn("[DEBUG] Base scheme JSON did not contain a 'rows' array. Falling back to only current status data.");
            // If base scheme JSON is malformed or empty, just use current status data.
            return currentStatus;
        }
        console.log("[DEBUG] Merged scheme data:", mergedRows);
        return mergedRows;
    }

    /**
     * Loads the base hall scheme from a URL, merges it with current status, and renders it.
     * @param {string} url - The URL to the JSON file containing the base hall scheme.
     * @param {Array} currentStatusData - The real-time seat status data from Django.
     */
    function loadAndRenderHallScheme(url, currentStatusData) {
        console.log("[DEBUG] loadAndRenderHallScheme - Attempting to load scheme from URL:", url);
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    console.error(`[DEBUG] HTTP error! status: ${response.status} for URL: ${url}`);
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                console.log("[DEBUG] Hall scheme JSON fetched successfully.");
                return response.json();
            })
            .then(schemeData => {
                console.log("[DEBUG] Базовая схема зала загружена из JSON:", schemeData);
                const mergedData = mergeSchemeAndStatus(schemeData, currentStatusData);
                renderHallScheme(mergedData, 'hall-scheme-container');
            })
            .catch(error => {
                console.error("[DEBUG] Ошибка при загрузке или парсинге схемы зала из JSON:", error);
                hallSchemeContainer.innerHTML =
                    '<p style="color: red;">Не удалось загрузить базовую схему зала из JSON. Попробуем отрисовать только по актуальным данным.</p>';
                // Fallback: if base scheme fails to load, render using only current status data
                if (currentStatusData && currentStatusData.length > 0) {
                    console.log("[DEBUG] Falling back to render using only currentStatusData.");
                    renderHallScheme(currentStatusData, 'hall-scheme-container');
                } else {
                    console.log("[DEBUG] No currentStatusData available for fallback rendering.");
                    hallSchemeContainer.innerHTML = '<p>Нет данных для отображения схемы зала.</p>';
                }
            });
    }

    /**
     * Renders the hall scheme using SVG based on provided seat data.
     * @param {Array} schemeData - The merged seat data (base scheme + current status).
     * @param {string} containerId - The ID of the HTML element where the SVG should be rendered.
     */
    function renderHallScheme(schemeData, containerId) {
        console.log("[DEBUG] renderHallScheme - Starting rendering with data:", schemeData);
        const container = document.getElementById(containerId);
        container.innerHTML = ''; // Clear previous content

        if (!schemeData || schemeData.length === 0) {
            container.innerHTML = '<p>Нет данных о рядах и местах в схеме зала.</p>';
            console.warn("[DEBUG] No schemeData provided to renderHallScheme.");
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

        // Ensure rows are sorted by row_number
        schemeData.sort((a, b) => a.row_number - b.row_number);
        console.log("[DEBUG] Scheme data rows sorted:", schemeData.map(row => row.row_number));

        schemeData.forEach(rowData => {
            const rowNumber = rowData.row_number;
            const seats = rowData.seats;

            // Ensure seats within a row are sorted by seat_number
            seats.sort((a, b) => a.seat_number - b.seat_number);
            // console.log(`[DEBUG] Row ${rowNumber} seats sorted:`, seats.map(s => s.seat_number));


            let currentX = startX;

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
                const seatId = seatData.id ? seatData.id.toString() : null; // Ensure ID is string for consistency
                const seatNumber = seatData.seat_number;
                const status = seatData.status; // 'F', 'S', 'N'
                const isVip = seatData.is_vip;
                const price = parseFloat(seatData.price || 0); // Ensure price is a number

                const seatElement = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                seatElement.setAttribute("x", currentX);
                seatElement.setAttribute("y", currentY);
                seatElement.setAttribute("width", seatSize);
                seatElement.setAttribute("height", seatSize);
                seatElement.setAttribute("rx", 5);

                seatElement.classList.add('seat', 'svg-seat');

                // Apply status and VIP classes
                if (status === 'F') {
                    seatElement.classList.add('free');
                } else if (status === 'S') {
                    seatElement.classList.add('occupied');
                } else { // 'N'
                    seatElement.classList.add('unavailable');
                }
                if (isVip) {
                    seatElement.classList.add('vip');
                }

                // Add data attributes for JS logic
                if (seatId) {
                    seatElement.dataset.seatId = seatId;
                    seatElement.dataset.row = rowNumber;
                    seatElement.dataset.seat = seatNumber;
                    seatElement.dataset.price = price.toFixed(2); // Store price as a fixed string
                    seatElement.dataset.status = status;
                } else {
                    seatElement.dataset.status = 'N'; // Seat without DB ID
                    console.warn(`[DEBUG] Seat (Row: ${rowNumber}, Seat: ${seatNumber}) missing ID in merged data. Setting status to 'N'.`);
                }

                const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
                title.textContent = `Ряд: ${rowNumber}, Место: ${seatNumber}\nСтатус: ${
                    status === 'F' ? 'Свободно' : (status === 'S' ? 'Занято' : 'Недоступно')
                }\nЦена: ${price.toFixed(2)} грн`;
                seatElement.appendChild(title);

                seatElement.addEventListener('click', () => {
                    console.log(`[DEBUG] Clicked seat: ID ${seatId}, Row ${rowNumber}, Seat ${seatNumber}, Status ${status}`);
                    if (seatId && status === 'F') { // Only interact with free seats that have an ID
                        const currentSeatId = seatElement.dataset.seatId;
                        const currentSeatPrice = parseFloat(seatElement.dataset.price);

                        if (seatElement.classList.contains('selected')) {
                            console.log(`[DEBUG] Deselecting seat: ${currentSeatId}`);
                            seatElement.classList.remove('selected');
                            selectedSeats = selectedSeats.filter(id => id !== currentSeatId);
                            totalPrice -= currentSeatPrice;
                        } else {
                            console.log(`[DEBUG] Selecting seat: ${currentSeatId}`);
                            seatElement.classList.add('selected');
                            selectedSeats.push(currentSeatId);
                            totalPrice += currentSeatPrice;
                        }
                        updateSelectionDisplay();
                    } else if (!seatId) {
                        alert('Это место не определено в системе (нет ID).');
                        console.warn(`[DEBUG] Clicked an undefined seat: Row ${rowNumber}, Seat ${seatNumber}`);
                    } else {
                        alert(`Место Ряд ${rowNumber}, Место ${seatNumber} уже занято или недоступно.`);
                        console.log(`[DEBUG] Clicked an unavailable/occupied seat: ID ${seatId}, Status ${status}`);
                    }
                });

                svg.appendChild(seatElement);

                const seatText = document.createElementNS("http://www.w3.org/2000/svg", "text");
                seatText.setAttribute("x", currentX + seatSize / 2);
                seatText.setAttribute("y", currentY + seatSize / 2);
                seatText.setAttribute("text-anchor", "middle");
                seatText.setAttribute("dominant-baseline", "middle");
                seatText.style.fontSize = "12px";
                seatText.style.fill = "#fff";
                seatText.style.pointerEvents = "none";
                seatText.textContent = seatNumber;
                svg.appendChild(seatText);

                currentX += seatSize + seatSpacing;
            });

            if (currentX > maxX) {
                maxX = currentX;
            }

            currentY += seatSize + rowSpacing;
        });

        container.appendChild(svg);

        // Adjust viewBox and SVG dimensions to fit content
        const finalWidth = maxX + startX;
        const finalHeight = currentY + startY;
        svg.setAttribute("viewBox", `0 0 ${finalWidth} ${finalHeight}`);
        svg.setAttribute("width", finalWidth);
        svg.setAttribute("height", finalHeight);
        svg.style.width = "100%"; // Make it responsive
        console.log(`[DEBUG] SVG rendered with final dimensions: ${finalWidth}x${finalHeight}`);
        // Initial update to reflect any pre-selected seats (if applicable, though usually not on load)
        updateSelectionDisplay();
    }

    /**
     * Updates the UI elements showing selected seat count, total price, and enables/disables the purchase button.
     */
    function updateSelectionDisplay() {
        console.log("[DEBUG] updateSelectionDisplay - Updating UI for selected seats.");
        console.log("[DEBUG] Current selectedSeats array:", selectedSeats);
        console.log("[DEBUG] Current totalPrice:", totalPrice);

        selectedSeatsCountSpan.textContent = selectedSeats.length;
        totalPriceSpan.textContent = totalPrice.toFixed(2);
        selectedSeatsInput.value = JSON.stringify(selectedSeats); // For form submission

        purchaseButton.disabled = selectedSeats.length === 0;

        // Visual feedback: ensure 'selected' class is correct on all seats
        document.querySelectorAll('.seat.svg-seat').forEach(seatElement => {
            const seatId = seatElement.dataset.seatId;
            if (selectedSeats.includes(seatId)) {
                if (!seatElement.classList.contains('selected')) {
                    seatElement.classList.add('selected');
                    console.log(`[DEBUG] Added 'selected' class to seat ID: ${seatId}`);
                }
            } else {
                if (seatElement.classList.contains('selected')) {
                    seatElement.classList.remove('selected');
                    console.log(`[DEBUG] Removed 'selected' class from seat ID: ${seatId}`);
                }
            }
        });
    }

    // --- Initialization Logic ---
    // This is the starting point for rendering the hall scheme
    console.log("[DEBUG] Initialization Logic - Starting hall scheme rendering process.");
    if (schemeFileUrl) {
        loadAndRenderHallScheme(schemeFileUrl, currentSeatStatusData);
    } else {
        hallSchemeContainer.innerHTML = '<p style="color: orange;">URL для базовой схемы зала не указан. Отрисовка по данным из базы.</p>';
        console.warn("[DEBUG] schemeFileUrl is missing. Attempting to render directly from currentSeatStatusData.");
        if (currentSeatStatusData && currentSeatStatusData.length > 0) {
            renderHallScheme(currentSeatStatusData, 'hall-scheme-container');
        } else {
            hallSchemeContainer.innerHTML = '<p>Нет данных для отображения схемы зала.</p>';
            console.error("[DEBUG] No schemeFileUrl and no currentSeatStatusData available to render the hall scheme.");
        }
    }

    // Add a simple legend for seat statuses
    const legendDiv = document.createElement('div');
    legendDiv.style.marginTop = '20px';
    legendDiv.style.padding = '10px';
    legendDiv.style.border = '1px solid #eee';
    legendDiv.style.backgroundColor = '#f0f0f0';
    legendDiv.innerHTML = `
        <p><strong>Условные обозначения:</strong></p>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 20px; background-color: #28a745; border-radius: 3px; margin-right: 10px;"></div>
            <span>Свободно (F)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 20px; background-color: #dc3545; border-radius: 3px; margin-right: 10px;"></div>
            <span>Занято (S)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 20px; background-color: #6c757d; border-radius: 3px; margin-right: 10px;"></div>
            <span>Недоступно (N)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 20px; background-color: #007bff; border-radius: 3px; margin-right: 10px;"></div>
            <span>Выбрано</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 20px; background-color: #ffc107; border-radius: 3px; margin-right: 10px;"></div>
            <span>VIP место</span>
        </div>
    `;
    hallSchemeContainer.parentNode.insertBefore(legendDiv, hallSchemeContainer.nextSibling);

    // Basic CSS for visualization of seat states (if not already defined)
    const style = document.createElement('style');
    style.innerHTML = `
        .svg-seat {
            cursor: pointer;
            transition: all 0.2s ease-in-out;
        }
        .svg-seat.free {
            fill: #28a745; /* Green */
        }
        .svg-seat.occupied {
            fill: #dc3545; /* Red */
            cursor: not-allowed;
        }
        .svg-seat.unavailable {
            fill: #6c757d; /* Gray */
            cursor: not-allowed;
        }
        .svg-seat.selected {
            fill: #007bff; /* Blue */
            stroke: #0056b3;
            stroke-width: 2px;
            transform: scale(1.05);
        }
        .svg-seat.vip {
            stroke: #ffc107; /* Yellow border for VIP */
            stroke-width: 2px;
        }
        .svg-seat.occupied.vip {
             stroke: #dc3545; /* Keep red for occupied VIP */
        }
        .svg-seat.unavailable.vip {
            stroke: #6c757d; /* Keep gray for unavailable VIP */
        }
    `;
    document.head.appendChild(style);

});