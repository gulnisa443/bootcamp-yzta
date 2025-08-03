// Migren Günlüğü - Ana JavaScript Dosyası
console.log('Migren Günlüğü uygulaması başlatıldı.');

// Global değişkenler
const USER_KEY = 'migrenUser';

// Kullanıcı yönetimi
class UserManager {
  static getCurrentUser() {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null');
  }

  static setCurrentUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  static logout() {
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem('access_token');
    window.location.href = 'index.html';
  }

  static isLoggedIn() {
    return this.getCurrentUser() !== null && !!localStorage.getItem('access_token');
  }
}

// Backend API ile veri yönetimi
class DataManager {
  static async getEntries() {
    const token = localStorage.getItem('access_token');
    const res = await fetch('http://localhost:8000/entries/', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    return await res.json();
  }

  static async saveEntry(entry) {
    const token = localStorage.getItem('access_token');
    const res = await fetch('http://localhost:8000/entries/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify(entry)
    });
    return await res.json();
  }

  static async deleteEntry(entryId) {
    const token = localStorage.getItem('access_token');
    const res = await fetch(`http://localhost:8000/entries/${entryId}`, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + token }
    });
    return await res.json();
  }
  static async predictRisk(entry) {
  const token = localStorage.getItem('access_token');
  const res = await fetch("http://localhost:8000/entries/predict-ml-risk", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify(entry)
  });

  return await res.json();
}

  static async getRecentEntries(days = 30) {
    const token = localStorage.getItem('access_token');
    const res = await fetch(`http://localhost:8000/entries/recent/?days=${days}`, {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    return await res.json();
  }
}

// Analiz fonksiyonları (opsiyonel: backend'den summary endpointi ile alınabilir)
class AnalysisManager {
  static async getSummary(days = 30) {
    const token = localStorage.getItem('access_token');
    const res = await fetch(`http://localhost:8000/analysis/summary/?days=${days}`, {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    return await res.json();
  }
}


// UI yardımcı fonksiyonları
class UIHelper {
  static showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 16px 24px;
      border-radius: 8px;
      color: white;
      font-weight: 500;
      z-index: 1000;
      animation: slideIn 0.3s ease;
    `;

    if (type === 'success') {
      notification.style.backgroundColor = '#10b981';
    } else if (type === 'error') {
      notification.style.backgroundColor = '#ef4444';
    } else {
      notification.style.backgroundColor = '#3b82f6';
    }

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, 3000);
  }

  static formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  static formatNumber(number, decimals = 1) {
    return parseFloat(number).toFixed(decimals);
  }

  static createChart(ctx, data, options = {}) {
    // Basit chart oluşturma (Chart.js kullanılabilir)
    const canvas = document.createElement('canvas');
    canvas.width = options.width || 400;
    canvas.height = options.height || 200;
    
    const context = canvas.getContext('2d');
    // Chart çizim kodları buraya eklenebilir
    
    return canvas;
  }
}

// Form validasyonu
class FormValidator {
  static validateMigrenForm(formData) {
    const errors = [];

    if (!formData.uyku || formData.uyku < 0 || formData.uyku > 24) {
      errors.push('Uyku süresi 0-24 saat arasında olmalıdır');
    }

    if (!formData.stres || formData.stres < 1 || formData.stres > 10) {
      errors.push('Stres seviyesi 1-10 arasında olmalıdır');
    }

    if (!formData.su || formData.su < 0 || formData.su > 10) {
      errors.push('Su tüketimi 0-10 litre arasında olmalıdır');
    }

    if (!formData.ekran || formData.ekran < 0 || formData.ekran > 24) {
      errors.push('Ekran süresi 0-24 saat arasında olmalıdır');
    }

    if (!formData.ruhHali) {
      errors.push('Ruh hali seçilmelidir');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

// Sayfa yüklendiğinde çalışacak genel fonksiyonlar
document.addEventListener('DOMContentLoaded', function() {
  // Kullanıcı giriş kontrolü (sadece belirli sayfalarda)
  const protectedPages = ['dashboard.html', 'panel.html', 'gecmis.html', 'grafikler.html', 'ayarlar.html', 'profile.html'];
  const currentPage = window.location.pathname.split('/').pop();
  
  // Eğer korumalı bir sayfadaysa ve giriş yapmamışsa login'e yönlendir
  if (protectedPages.includes(currentPage) && !UserManager.isLoggedIn()) {
    // Sadece login ve signup sayfalarında değilse yönlendir
    if (currentPage !== 'login.html' && currentPage !== 'signup.html') {
      window.location.href = 'login.html';
      return;
    }
  }

  // Navigation aktif sayfa işaretleme
  highlightCurrentPage();
});

function highlightCurrentPage() {
  const currentPage = window.location.pathname.split('/').pop();
  const navLinks = document.querySelectorAll('.nav-links a');
  
  navLinks.forEach(link => {
    if (link.getAttribute('href') === currentPage) {
      link.style.color = '#a855f7';
      link.style.fontWeight = '700';
    }
  });
}

// Global fonksiyonlar (HTML'den çağrılabilir)
window.MigrenApp = {
  UserManager,
  DataManager,
  AnalysisManager,
  UIHelper,
  FormValidator
}; 