document.addEventListener('DOMContentLoaded', function() {
    // Форматирование для регистрации
    const phoneInput = document.querySelector('.phone-input');
    if (phoneInput) {
        new Cleave(phoneInput, {
            phone: true,
            phoneRegionCode: 'RU',
            prefix: '+7',
            delimiter: ' ',
            blocks: [2, 3, 3, 2, 2],
            numericOnly: true,
            onValueChanged: function(e) {
                const raw = e.target.rawValue;
                if (raw.startsWith('8')) {
                    this.setRawValue('7' + raw.slice(1));
                } else if (raw.startsWith('9')) {
                    this.setRawValue('7' + raw);
                }
            }
        });
    }
});