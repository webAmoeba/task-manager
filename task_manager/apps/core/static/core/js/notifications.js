(function () {
  const config = window.notificationsConfig;
  if (!config || !config.currentUserId) {
    return;
  }

  const container = document.querySelector('[data-notification-area]');
  if (!container) {
    return;
  }

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

  function renderNotification(notification) {
    const element = document.createElement('div');
    element.className = 'toast align-items-center text-bg-primary border-0 show mb-2';
    element.setAttribute('role', 'alert');
    element.setAttribute('aria-live', 'assertive');
    element.setAttribute('aria-atomic', 'true');
    element.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          <strong class="d-block">${escapeHtml(notification.title)}</strong>
          ${escapeHtml(notification.message)}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>`;
    container.appendChild(element);
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

  connect();
})();
