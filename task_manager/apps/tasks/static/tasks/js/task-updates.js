(function () {
  const config = window.taskUpdatesConfig;
  const tableBody = document.querySelector("[data-task-table-body]");

  if (!config || !tableBody) {
    return;
  }

  const alertsContainer = document.querySelector("[data-task-alerts]");
  const currentUserId = config.currentUserId;
  const messages = {
    edit: (config.messages && config.messages.edit) || "Edit",
    delete: (config.messages && config.messages.delete) || "Delete",
    pending: (config.messages && config.messages.pending) || "Pending",
    created: (config.messages && config.messages.created) || "New task created",
    updated: (config.messages && config.messages.updated) || "Task updated",
    deleted: (config.messages && config.messages.deleted) || "Task deleted",
  };

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return decodeURIComponent(parts.pop().split(";").shift());
    }
    return null;
  }

  const csrfToken = getCookie("csrftoken") || "";

  function escapeHtml(value) {
    if (value === null || value === undefined) {
      return "";
    }
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function formatDate(value) {
    if (!value) {
      return "—";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return "—";
    }
    const pad = (num) => num.toString().padStart(2, "0");
    return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
  }

  function renderPerson(fullName, username) {
    if (fullName) {
      return `${escapeHtml(fullName)}<br>(${escapeHtml(username)})`;
    }
    if (username) {
      return escapeHtml(username);
    }
    return "—";
  }

  function showAlert(message, level = "info") {
    if (!alertsContainer) {
      return;
    }
    const wrapper = document.createElement("div");
    wrapper.className = `alert alert-${level} alert-dismissible fade show`;
    wrapper.setAttribute("role", "alert");
    wrapper.innerHTML = `${escapeHtml(message)}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
    alertsContainer.appendChild(wrapper);
  }

  function buildActions(task) {
    const isAuthor = task.author === currentUserId;
    const isExecutor = task.executor === currentUserId;
    const actions = [];

    actions.push(
      `<a href="${task.update_url}">${escapeHtml(messages.edit)}</a>`
    );

    if (isAuthor) {
      actions.push(
        `<br /><a href="${task.delete_url}">${escapeHtml(messages.delete)}</a>`
      );
    } else {
      actions.push(
        `<br /><a style="opacity: 0.4; cursor: default" href="${task.delete_url}">${escapeHtml(messages.delete)}</a>`
      );
    }

    return actions.join("");
  }

  function renderTaskRow(task) {
    const row = document.createElement("tr");
    row.dataset.taskId = task.id;
    const isOverdue = Boolean(task.is_overdue) && !task.is_completed;
    row.innerHTML = `
      <td>${task.id}</td>
      <td><a href="${task.detail_url}">${escapeHtml(task.name)}</a></td>
      <td>${escapeHtml(task.status_name || "")}</td>
      <td>${renderPerson(task.author_full_name, task.author_username)}</td>
      <td>${task.executor
        ? renderPerson(task.executor_full_name, task.executor_username)
        : ""
      }</td>
      <td class="${isOverdue ? "text-danger" : ""}">${
        task.due_at ? `${formatDate(task.due_at)} UTC` : "—"
      }</td>
      <td>${
        task.completed_at
          ? `${formatDate(task.completed_at)} UTC`
          : escapeHtml(messages.pending)
      }</td>
      <td>${task.created_at ? `${formatDate(task.created_at)} UTC` : ""}</td>
      <td>${buildActions(task)}</td>
    `;
    return row;
  }

  function upsertRow(task, eventType) {
    const existing = tableBody.querySelector(`[data-task-id="${task.id}"]`);
    const newRow = renderTaskRow(task);
    if (existing) {
      existing.replaceWith(newRow);
    } else {
      tableBody.prepend(newRow);
    }
    if (eventType === "created") {
      showAlert(messages.created, "success");
    } else {
      showAlert(messages.updated, "info");
    }
  }

  function deleteRow(task) {
    const existing = tableBody.querySelector(`[data-task-id="${task.id}"]`);
    if (existing) {
      existing.remove();
    }
    showAlert(messages.deleted, "warning");
  }

  function connect() {
    const scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socketUrl = `${scheme}://${window.location.host}${config.websocketPath || "/ws/tasks/"}`;
    const socket = new WebSocket(socketUrl);

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.event === "deleted") {
          deleteRow(data.task);
        } else if (data.task) {
          upsertRow(data.task, data.event);
        }
      } catch (error) {
        console.error("Failed to process websocket message", error);
      }
    };

    socket.onclose = () => {
      setTimeout(connect, 2000);
    };

    socket.onerror = () => {
      socket.close();
    };
  }

  connect();
})();
