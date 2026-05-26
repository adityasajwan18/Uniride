// =====================================================
// UniRide — Frontend Logic
// =====================================================

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initFindRide();
  initAddRide();
  initDashboard();
});

/* ---------------- Tabs ---------------- */
function initTabs() {
  const tabs = document.querySelectorAll(".tab");
  if (!tabs.length) return;

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      document.querySelectorAll(".tab-content").forEach(tc => tc.classList.add("hidden"));
      document.getElementById(`tab-${tab.dataset.tab}`).classList.remove("hidden");
    });
  });
}

/* ---------------- Find Ride ---------------- */
function initFindRide() {
  const btn = document.getElementById("btn-find");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    const source = document.getElementById("find-source").value;
    const destination = document.getElementById("find-destination").value;
    const resultsEl = document.getElementById("find-results");

    if (!source) {
      resultsEl.innerHTML = `<div class="empty-state">Please select a pickup location.</div>`;
      return;
    }

    resultsEl.innerHTML = `<div class="empty-state">Searching optimized rides…</div>`;

    try {
      const res = await fetch("/find-rides", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source, destination }),
      });
      const data = await res.json();
      renderRides(data, resultsEl);
    } catch (err) {
      resultsEl.innerHTML = `<div class="empty-state">Something went wrong. Try again.</div>`;
    }
  });
}

function renderRides(data, container) {
  if (!data.success) {
    container.innerHTML = `<div class="empty-state">${data.message || "No rides found."}</div>`;
    return;
  }
  if (!data.rides || data.rides.length === 0) {
    container.innerHTML = `<div class="empty-state">No matching rides available right now.</div>`;
    return;
  }

  let html = "";

  if (data.route && data.route.path && data.route.path.length) {
    html += `
      <div class="route-summary">
        <div><strong>Optimized route:</strong> ${data.route.path.join(" → ")}</div>
        <div class="muted" style="margin-top:4px;">Distance: <strong style="color:var(--text)">${data.route.distance} km</strong> · via Dijkstra</div>
        <div class="algo-tags">
          ${(data.algorithms_used || []).map(a => `<span class="algo-tag">${a}</span>`).join("")}
        </div>
      </div>
    `;
  }

  data.rides.forEach(ride => {
    html += `
      <div class="ride-card">
        <div>
          <div class="driver">${ride.driver_name}</div>
          <div class="route-line">${ride.source} → ${ride.destination}${ride.path ? ` &nbsp;·&nbsp; ${ride.path.join(" → ")}` : ""}</div>
          <div class="meta">
            <span>⏱ <strong>${ride.time}</strong></span>
            <span>👥 <strong>${ride.seats}</strong> seats</span>
            <span>📍 <strong>${ride.distance} km</strong></span>
          </div>
        </div>
        <span class="badge">Ride #${ride.id}</span>
      </div>
    `;
  });

  container.innerHTML = html;
}

/* ---------------- Add Ride ---------------- */
function initAddRide() {
  const btn = document.getElementById("btn-add");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    const payload = {
      driver_name: document.getElementById("add-driver").value.trim(),
      source: document.getElementById("add-source").value,
      destination: document.getElementById("add-destination").value,
      time: document.getElementById("add-time").value,
      seats: document.getElementById("add-seats").value,
    };
    const feedback = document.getElementById("add-feedback");

    if (!payload.driver_name || !payload.source || !payload.time) {
      feedback.className = "feedback error";
      feedback.textContent = "Please fill driver name, source, and time.";
      return;
    }

    feedback.className = "feedback muted";
    feedback.textContent = "Publishing ride…";

    try {
      const res = await fetch("/add-ride", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.success) {
        feedback.className = "feedback success";
        feedback.textContent = `Ride published successfully · Distance ${data.distance} km`;
        document.getElementById("add-driver").value = "";
        document.getElementById("add-time").value = "";
      } else {
        feedback.className = "feedback error";
        feedback.textContent = data.message || "Failed to add ride.";
      }
    } catch (err) {
      feedback.className = "feedback error";
      feedback.textContent = "Network error. Try again.";
    }
  });
}

/* ---------------- Dashboard ---------------- */
async function initDashboard() {
  const grid = document.getElementById("stat-grid");
  if (!grid) return;

  try {
    const res = await fetch("/stats");
    const data = await res.json();
    if (!data.success) return;

    document.getElementById("stat-total").textContent = data.total_rides;
    document.getElementById("stat-routes").textContent = data.active_routes;
    document.getElementById("stat-algos").textContent = data.algorithms_used;

    const tbody = document.querySelector("#recent-table tbody");
    if (!data.recent_rides.length) {
      tbody.innerHTML = `<tr><td colspan="6" class="muted">No rides yet.</td></tr>`;
      return;
    }
    tbody.innerHTML = data.recent_rides.map(r => `
      <tr>
        <td>${r.driver_name}</td>
        <td>${r.source}</td>
        <td>${r.destination}</td>
        <td>${r.time}</td>
        <td>${r.seats}</td>
        <td>${r.distance}</td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Dashboard load failed", err);
  }
}
