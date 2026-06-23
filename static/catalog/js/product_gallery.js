document.addEventListener("DOMContentLoaded", function() {
    const container = document.getElementById('image-formset-container');
    const totalFormsInput = document.getElementById('id_images-TOTAL_FORMS');

    if (!container || !totalFormsInput) return;

    // --- 1. ОБРАБОТКА ВЫБОРА ФАЙЛА (FileReader + Генерация нового слота) ---
    container.addEventListener('change', function(e) {
        if (e.target.matches('input[type="file"]')) {
            const input = e.target;
            const file = input.files[0]; // Важно: берем первый файл из массива [0]
            const block = input.closest('.image-upload-block');
            
            if (file && block) {
                // --- ВАЛИДАЦИЯ ФАЙЛА НА КЛИЕНТЕ ---
                const validExtensions = ['jpg', 'jpeg', 'png'];
                const fileExt = file.name.split('.').pop().toLowerCase();
                const maxSize = 5 * 1024 * 1024; // 5 Мегабайт

                // Проверяем расширение
                if (!validExtensions.includes(fileExt)) {
                    showJsError(`Файл "${file.name}" имеет недопустимый формат. Разрешены только JPG, JPEG, PNG.`);
                    input.value = ""; // Полностью очищаем этот инпут (минусуем плохой файл)
                    return; // Прерываем выполнение: превью не строится, новый чекбокс НЕ создается
                }

                // Проверяем размер
                if (file.size > maxSize) {
                    showJsError(`Размер файла "${file.name}" превышает 5 МБ. Пожалуйста, выберите другое изображение.`);
                    input.value = ""; // Полностью очищаем этот инпут (минусуем плохой файл)
                    return; // Прерываем выполнение: превью не строится, новый чекбокс НЕ создается
                }

                // Если всё отлично, скрываем старое сообщение об ошибке
                hideJsError();
                // --- КОНЕЦ ВАЛИДАЦИИ ---

                const reader = new FileReader();
                
                reader.onload = function(event) {
                    const defaultInfo = block.querySelector('.preview-default-info');
                    const imgPreview = block.querySelector('.img-preview');
                    const clearBtn = block.querySelector('.btn-new-clear');
                    const labelBtn = block.querySelector('label');
                    
                    if (imgPreview && defaultInfo && clearBtn && labelBtn) {
                        imgPreview.src = event.target.result;
                        defaultInfo.classList.add('d-none');
                        imgPreview.classList.remove('d-none');
                        clearBtn.classList.remove('d-none');
                        
                        labelBtn.classList.remove('btn-outline-secondary');
                        labelBtn.classList.add('btn-outline-success');

                        // Проверяем, является ли эта строка последней среди ВСЕХ строк формсета
                        const allRows = container.querySelectorAll('.formset-row');
                        const currentRow = input.closest('.formset-row');
                        const lastRow = allRows[allRows.length - 1];
                        
                        if (currentRow === lastRow) {
                            createNextUploadSlot();
                        }
                    }
                };
                reader.readAsDataURL(file);
            }
        }
    });

    // Вспомогательная функция генерации нового слота
    function createNextUploadSlot() {
        const currentFormCount = parseInt(totalFormsInput.value);
        const templateHtml = document.getElementById('empty-form-template').innerHTML;

        // Заменяем технический префикс Django на текущий ID
        const newFormHtml = templateHtml.replace(/__prefix__/g, currentFormCount);

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = newFormHtml;
        const newRow = tempDiv.firstElementChild;
        
        container.appendChild(newRow);
        totalFormsInput.value = currentFormCount + 1;
    }

    // --- 2. ЕДИНЫЙ ОБРАБОТЧИК КЛИКОВ (Делегирование событий) ---
    container.addEventListener('click', function(e) {
        const clearBtn = e.target.closest('.btn-new-clear');
        const savedClearBtn = e.target.closest('.btn-saved-clear');

        // А. Клик по крестику у НОВЫХ (еще не сохраненных) файлов
        if (clearBtn) {
            e.preventDefault();
            e.stopPropagation(); // Останавливаем всплытие
            
            const currentCardRow = clearBtn.closest('.formset-row');
            const block = clearBtn.closest('.image-upload-block');
            const input = block.querySelector('input[type="file"]');
            const defaultInfo = block.querySelector('.preview-default-info');
            const imgPreview = block.querySelector('.img-preview');
            const labelBtn = block.querySelector('label');

            if (input && imgPreview && defaultInfo && labelBtn) {
                // Считаем только пустые слоты, у которых еще нет выбранного файла
                const allRows = Array.from(container.querySelectorAll('.formset-row'));
                // Фильтр: строки без картинок (новые пустые слоты)
                const newEmptyRows = allRows.filter(row => row.querySelector('.image-upload-block') && !row.querySelector('.img-saved-wrapper'));

                if (newEmptyRows.length > 1) {
                    // Удаляем строку физически
                    currentCardRow.remove();
                    // КРИТИЧЕСКИ ВАЖНО: Пересчитываем индексы всех оставшихся строк, чтобы Django не потерял данные
                    reindexFormset();
                } else {
                    // Если слот последний оставшийся пустой — просто очищаем форму до дефолта
                    input.value = ""; 
                    imgPreview.src = "";
                    imgPreview.classList.add('d-none');
                    defaultInfo.classList.remove('d-none');
                    clearBtn.classList.add('d-none');
                    
                    labelBtn.classList.remove('btn-outline-success');
                    labelBtn.classList.add('btn-outline-secondary');
                }
            }
        }

        // Б. Клик по крестику у УЖЕ СОХРАНЕННЫХ в БД фотографий (Мягкое удаление/Восстановление)
        if (savedClearBtn) {
            e.preventDefault();
            
            const checkboxId = savedClearBtn.getAttribute('data-checkbox-id');
            const nativeCheckbox = document.getElementById(checkboxId);
            const cardContainer = savedClearBtn.closest('.card');
            const imgWrapper = cardContainer.querySelector('.img-saved-wrapper');

            if (nativeCheckbox && cardContainer && imgWrapper) {
                nativeCheckbox.checked = !nativeCheckbox.checked;

                if (nativeCheckbox.checked) {
                    imgWrapper.style.opacity = '0.2';
                    cardContainer.classList.remove('bg-light');
                    cardContainer.style.backgroundColor = '#fde8e8';
                    cardContainer.style.borderColor = '#f8b4b4';
                    savedClearBtn.innerHTML = '<i class="bi bi-arrow-counterclockwise fs-6"></i>';
                    savedClearBtn.classList.remove('btn-danger');
                    savedClearBtn.classList.add('btn-secondary');
                    savedClearBtn.title = "Восстановить фото";
                } else {
                    imgWrapper.style.opacity = '1';
                    cardContainer.style.backgroundColor = '';
                    cardContainer.style.borderColor = '';
                    cardContainer.classList.add('bg-light');
                    savedClearBtn.innerHTML = '<i class="bi bi-x fs-6"></i>';
                    savedClearBtn.classList.remove('btn-secondary');
                    savedClearBtn.classList.add('btn-danger');
                    savedClearBtn.title = "Удалить фото";
                }
            }
        }
    });

    // --- 3. ФУНКЦИЯ ДЛЯ ПЕРЕСЧЕТА ИНДЕКСОВ ДЛЯ DJANGO ---
    function reindexFormset() {
        const rows = container.querySelectorAll('.formset-row');
        totalFormsInput.value = rows.length; // Обновляем TOTAL_FORMS точным числом оставшихся строк

        rows.forEach((row, index) => {
            // Ищем все элементы управления внутри строки, у которых есть атрибуты name, id или for
            const elements = row.querySelectorAll('input, label, select, textarea');
            
            elements.forEach(el => {
                // Регулярное выражение ищет паттерн вида -знак-цифра-знак, например "-0-", "-1-"
                if (el.hasAttribute('name')) {
                    el.setAttribute('name', el.getAttribute('name').replace(/-\d+-/, `-${index}-`));
                }
                if (el.hasAttribute('id')) {
                    el.setAttribute('id', el.getAttribute('id').replace(/-\d+-/, `-${index}-`));
                }
                if (el.hasAttribute('for')) {
                    el.setAttribute('for', el.getAttribute('for').replace(/-\d+-/, `-${index}-`));
                }
            });

            // Также обновляем атрибут data-checkbox-id у кнопок, если они есть в этой строке
            const savedBtn = row.querySelector('.btn-saved-clear');
            if (savedBtn && savedBtn.hasAttribute('data-checkbox-id')) {
                savedBtn.setAttribute('data-checkbox-id', savedBtn.getAttribute('data-checkbox-id').replace(/-\d+-/, `-${index}-`));
            }
        });
    }
});

// Функции для управления блоком ошибок на странице
    function showJsError(message) {
        const errorAlert = document.getElementById('js-gallery-error');
        const errorText = document.getElementById('js-error-text');
        if (errorAlert && errorText) {
            errorText.innerText = message;
            errorAlert.classList.remove('d-none');
        }
    }

    function hideJsError() {
        const errorAlert = document.getElementById('js-gallery-error');
        if (errorAlert) {
            errorAlert.classList.add('d-none');
        }
    }
