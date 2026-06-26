document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form[enctype="multipart/form-data"]');
    const container = document.getElementById('image-formset-container');
    const errorBlock = document.getElementById('js-gallery-error');
    const errorText = document.getElementById('js-error-text');

    if (!form || !container) {
        console.error("❌ Проверка галереи: Форма или контейнер '#image-formset-container' не найдены!");
        return;
    }


    // Универсальная функция проверки всех полей галереи
    window.validateGallery = function() {
        const inputs = document.querySelectorAll('#image-formset-container input[type="file"]');
        const validExtensions = ['.jpg', '.jpeg', '.png'];
        const maxSize = 5 * 1024 * 1024; // 5 МБ
        let hasError = false;
        let errorMessage = '';

        for (let i = 0; i < inputs.length; i++) {
            const input = inputs[i];

            // Проверяем, выбран ли файл в текущем инпуте
            if (input.files && input.files.length > 0) {
                // СТРОГО ИСПРАВЛЕНО: Берём первый файл из списка через индекс [0]
                const currentFile = input.files[0];
                const fileName = currentFile.name.toLowerCase();

                // Валидация расширения файла
                const matchesExt = validExtensions.some(ext => fileName.endsWith(ext));
                if (!matchesExt) {
                    hasError = true;
                    errorMessage = "Файл " + currentFile.name + " имеет недопустимый формат. Разрешены только JPG, JPEG, PNG.";
                    input.value = ''; // Очищаем поле выбора
                    resetPreviewBlock(input);
                    break;
                }

                // Валидация веса файла
                if (currentFile.size > maxSize) {
                    hasError = true;
                    errorMessage = "Размер файла " + currentFile.name + " превышает 5 МБ. Пожалуйста, сожмите изображение.";
                    input.value = ''; // Очищаем поле выбора
                    resetPreviewBlock(input);
                    break;
                }
            }
        }

        if (hasError) {
            // Гарантированно выводим стандартное окно браузера, если HTML-блоки для ошибок отсутствуют
            const errorBlock = document.getElementById('js-gallery-error');
            const errorText = document.getElementById('js-error-text');

            if (errorBlock && errorText) {
                errorText.innerHTML = errorMessage;
                errorBlock.classList.remove('d-none');
                errorBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                alert(errorMessage);
            }
            return false;
        }

        const errorBlock = document.getElementById('js-gallery-error');
        if (errorBlock) errorBlock.classList.add('d-none');
        return true;
    };

    // Функция безопасного сброса инпута и превью
    function clearInput(input) {
        input.value = ''; // Очищаем выбранный файл

        // Корректный сброс для старых IE/Edge, если необходимо
        if (input.value) {
            input.type = 'text';
            input.type = 'file';
        }

        resetPreviewBlock(input);
    }

    // Вспомогательная функция сброса превью
    function resetPreviewBlock(input) {
        const block = input.closest('.image-upload-block');
        if (block) {
            const previewImg = block.querySelector('.img-preview');
            const defaultInfo = block.querySelector('.preview-default-info');
            const clearBtn = block.querySelector('.btn-new-clear');
            if (previewImg) previewImg.classList.add('d-none');
            if (defaultInfo) defaultInfo.classList.remove('d-none');
            if (clearBtn) clearBtn.classList.add('d-none');
        }
    }

    // Код перехватчика
    // Самый надежный перехват галереи
    const galleryContainer = document.getElementById('image-formset-container');

    if (galleryContainer) {
        // Используем capture-фазу (true), чтобы наш скрипт выполнился ГАРАНТИРОВАННО первым на странице
        galleryContainer.addEventListener('change', function (e) {
            if (e.target && e.target.tagName === 'INPUT' && e.target.type === 'file') {
                const input = e.target;

                // ПРОВЕРКА ПО ПУТИ ФАЙЛА (Самый надежный способ в Windows)
                let currentPath = input.value || "";


                // Если в пути есть .pdf или вообще нет расширений картинок
                if (currentPath) {
                    const lowerPath = currentPath.toLowerCase();
                    const isImage = lowerPath.endsWith('.jpg') || lowerPath.endsWith('.jpeg') || lowerPath.endsWith('.png');

                    if (!isImage) {
                        console.error("❌ Обнаружен запрещенный файл в пути:", currentPath);
                        alert("Ошибка! Вы выбрали недопустимый формат файла.\n\nРазрешены только изображения (JPG, JPEG, PNG).\nФайлы PDF, документы и программы загружать ЗАПРЕЩЕНО.");

                        input.value = ""; // Очищаем поле сами
                        e.stopImmediatePropagation(); // Полностью блокируем превью и другие скрипты
                        e.preventDefault();
                        return false;
                    }
                }

                // Дополнительная проверка, если браузер передал файлы в массив
                if (input.files && input.files.length > 0) {
                    const file = input.files[0];
                    const maxSize = 5 * 1024 * 1024; // 5 МБ

                    if (file.size > maxSize) {
                        alert("Ошибка! Размер файла \"" + file.name + "\" превышает 5 МБ. Пожалуйста, сожмите изображение.");
                        input.value = "";
                        e.stopImmediatePropagation();
                        e.preventDefault();
                        return false;
                    }
                } else if (!currentPath) {
                    // Если сработал change, но всё абсолютно пусто — значит браузер молча стер PDF
                    alert("Ошибка! Выбран недопустимый формат файла (например, PDF).\nПожалуйста, выбирайте только картинки в формате JPG или PNG.");
                    e.stopImmediatePropagation();
                    e.preventDefault();
                    return false;
                }

                // Если это легитимная картинка, пускаем к основной валидации
                window.validateGallery();
            }
        }, true); // Значение true заставляет этот обработчик сработать раньше всех остальных на странице
    }


    // Предохранитель перед отправкой формы в Django
    form.addEventListener('submit', function (e) {
        if (!window.validateGallery()) {
            e.preventDefault();
        }
    });
});
