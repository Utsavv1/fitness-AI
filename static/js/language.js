function changeLanguage(lang) {
    // Get all elements that need translation
    const title = document.querySelector('.header-title');
    const subtitle = document.querySelector('.header-subtitle');
    const welcome = document.querySelector('.welcome-message h2');
    const description = document.querySelector('.welcome-message p');
    const startButton = document.querySelector('.start-button');

    // Update text content with translations
    title.innerHTML = `<img src="/static/images/icon1.png" style="height: 2.2em; vertical-align: middle; margin-right: 0.5em;" alt="Logo">${translations[lang].title}`;
    subtitle.textContent = translations[lang].subtitle;
    welcome.textContent = translations[lang].welcome;
    description.textContent = translations[lang].description;
    startButton.textContent = translations[lang].startButton;

    // Save selected language to localStorage
    localStorage.setItem('selectedLanguage', lang);
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedLanguage = localStorage.getItem('selectedLanguage') || 'en';
    changeLanguage(savedLanguage);
}); 