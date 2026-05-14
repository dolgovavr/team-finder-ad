// Project-specific JS (complete project action + toggle participate)
(function(){
  document.addEventListener("DOMContentLoaded", function() {
    const completeBtn = document.getElementById("complete-project-btn");
    if (completeBtn) {
      completeBtn.addEventListener("click", function(e) {
        e.preventDefault();
        const projectId = completeBtn.dataset.id;
        if (!projectId) return;

        fetch(`/projects/${projectId}/complete/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": window.getCookie ? window.getCookie("csrftoken") : "",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === "ok") {
            const statusEl = document.querySelector(".project-status-black");
            if (statusEl) statusEl.textContent = "Закрыт";
            completeBtn.remove();
            if (window.toast) window.toast("Проект завершён", { type: 'info' });
          } else {
            if (window.toast) window.toast("Ошибка при завершении проекта", { type: 'error' });
            else alert("Ошибка при завершении проекта");
          }
        })
        .catch(err => {
          console.error("Ошибка запроса:", err);
          if (window.toast) window.toast("Ошибка сети", { type: 'error' });
        });
      });
    }

    const participateBtn = document.getElementById("participate-btn");
    const participantsList = document.getElementById("participants-list");
    const participantsCount = document.getElementById("participants-count");
    if (participateBtn && participantsList && participantsCount) {
      const userId = participateBtn.dataset.userId || null;
      const projectId = participateBtn.dataset.project;
      const userName = participateBtn.dataset.userName || "";
      const userAvatar = participateBtn.dataset.userAvatar || "";

      /** Счётчик = число карточек участников в списке (как на сервере после перезагрузки). */
      function syncParticipantCountFromList() {
        const n = participantsList.querySelectorAll('a[id^="participant-"]').length;
        participantsCount.textContent = String(Math.max(0, n));
        const noEl = document.getElementById("no-participants");
        if (n === 0) {
          if (!noEl) {
            const p = document.createElement("p");
            p.id = "no-participants";
            p.textContent = "Пока нет участников";
            participantsList.appendChild(p);
          }
        } else if (noEl) {
          noEl.remove();
        }
      }

      let participateBusy = false;

      participateBtn.addEventListener("click", function(e) {
        e.preventDefault();
        if (!projectId || participateBusy) return;
        participateBusy = true;

        fetch(`/projects/${projectId}/toggle-participate/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": window.getCookie ? window.getCookie("csrftoken") : "",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({})
        })
        .then(resp => resp.json())
        .then(data => {
          if (data.status !== "ok") {
            if (window.toast) window.toast("Ошибка при изменении участия", { type: 'error' });
            else alert("Ошибка при изменении участия");
            return;
          }

          const joined =
            data.is_participant === true ||
            data.is_participant === "true" ||
            data.is_participant === 1;

          if (joined) {
            participateBtn.textContent = "Отказаться от участия";

            if (userId && !document.getElementById(`participant-${userId}`)) {
              const a = document.createElement("a");
              a.href = `/users/${userId}`;
              a.id = `participant-${userId}`;
              a.innerHTML = `
              <div class="participant-item">
                <img src="${userAvatar}" alt="Аватар" class="participant-avatar">
                <div class="participant-info">
                  <span class="participant-name">${userName}</span>
                  <span class="participant-role">Участник</span>
                </div>
              </div>
            `;
              participantsList.appendChild(a);
            }
          } else {
            participateBtn.textContent = "Участвовать";
            const el = userId ? document.getElementById(`participant-${userId}`) : null;
            if (el) el.remove();
          }

          syncParticipantCountFromList();
        })
        .catch(err => {
          console.error("Ошибка запроса:", err);
          if (window.toast) window.toast("Ошибка сети", { type: 'error' });
        })
        .finally(() => {
          participateBusy = false;
        });
      });
    }
  });
})();
