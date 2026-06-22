document.addEventListener('DOMContentLoaded', function () {
    // Находим форму, в которой лежит кнопка сохранения
    const form = document.querySelector('form[enctype="multipart/form-data"]');

    if (!form) return;

    // Делаем функцию глобальной, чтобы ее видел второй скрипт
    window.validateGallery = function() {
        const inputs = form.querySelectorAll('input[type="file"]');
        const validExtensions = ['.jpg', '.jpeg', '.png'];
        const maxSize = 5 * 1024 * 1024; // 5 МБ

        let hasError = false;
        let errorMessage = '';

        inputs.forEach(input => {
            if (input.files && input.files[0]) {
                const file = input.files[0];
                const fileName = file.name.toLowerCase();

                // Проверка расширения
                const matchesExt = validExtensions.some(ext => fileName.endsWith(ext));
                if (!matchesExt) {
                    hasError = true;
                    errorMessage = `Файл "${file.name}" имеет неверный формат. Разрешены только JPG, JPEG и PNG.`;
                    input.value = ''; // Мгновенно очищаем инпут
                }

                // Проверка размера
                if (file.size > maxSize) {
                    hasError = true;
                    errorMessage = `Файл "${file.name}" слишком большой. Максимальный размер — 5 МБ.`;
                    input.value = ''; // Мгновенно очищаем инпут
                }
            }
        });

        if (hasError) {
            alert(errorMessage);
            return false;
        }
        return true;
    };

    // Проверяем файлы сразу при их выборе
    form.addEventListener('change', function (e) {
        if (e.target && e.target.type === 'file') {
            window.validateGallery();
        }
    });

    // Жесткий предохранитель на кнопку "Сохранить"
    form.addEventListener('submit', function (e) {
        if (!window.validateGallery()) {
            e.preventDefault(); // Запрещаем Django перезагружать страницу
        }
    });
});
