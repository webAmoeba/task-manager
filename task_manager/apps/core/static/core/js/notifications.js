(function () {
  const config = window.notificationsConfig;
  if (!config || !config.currentUserId) {
    return;
  }

  const container = document.querySelector('[data-notification-area]');
  if (!container) {
    return;
  }

  const displayedIds = new Set();

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return decodeURIComponent(parts.pop().split(';').shift());
    }
    return null;
  }

  const csrfToken = getCookie('csrftoken');

  function escapeHtml(value) {
    if (value === null || value === undefined) {
      return '';
    }
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function markRead(id) {
    if (!id) {
      return;
    }
    fetch(`${config.apiMarkReadBase || '/api/notifications/'}${id}/mark-read/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken || '',
      },
      credentials: 'same-origin',
    }).catch(() => {
      /* swallow errors */
    });
  }

  function renderNotification(notification) {
    if (!notification || displayedIds.has(notification.id)) {
      return;
    }
    displayedIds.add(notification.id);
    const element = document.createElement('div');
    element.className = 'toast align-items-center text-bg-primary border-0 show mb-2';
    element.setAttribute('role', 'alert');
    element.setAttribute('aria-live', 'assertive');
    element.setAttribute('aria-atomic', 'true');
    element.setAttribute('data-bs-autohide', 'false');
    element.dataset.notificationId = notification.id;
    element.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          <strong class="d-block">${escapeHtml(notification.title)}</strong>
          ${escapeHtml(notification.message)}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>`;
    element.querySelector('.btn-close').addEventListener('click', () => {
      markRead(notification.id);
    });
    container.appendChild(element);
  }

  function loadInitialNotifications() {
    const listUrl = config.apiListUrl || '/api/notifications/?unread=1';
    fetch(listUrl, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to load notifications');
        }
        return response.json();
      })
      .then((data) => {
        const results = Array.isArray(data) ? data : data.results || [];
        results.forEach(renderNotification);
      })
      .catch(() => {
        /* ignore */
      });
  }

  function connect() {
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socketUrl = `${scheme}://${window.location.host}${config.websocketPath || '/ws/notifications/'}`;
    const socket = new WebSocket(socketUrl);

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data && data.title) {
          renderNotification(data);
        }
      } catch (error) {
        console.error('Failed to parse notification message', error);
      }
    };

    socket.onclose = () => {
      setTimeout(connect, 3000);
    };

    socket.onerror = () => {
      socket.close();
    };
  }

  loadInitialNotifications();
  connect();
})();
