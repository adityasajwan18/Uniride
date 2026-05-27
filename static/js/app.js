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

/* ---------------- Skeleton Loader ---------------- */
function showSkeleton(container, count = 3) {
  container.innerHTML = Array.from({ length: count }).map(() => `
    <div class="skeleton">
      <div class="skeleton-line w-40"></div>
      <div class="skeleton-line w-80"></div>
      <div class="skeleton-line w-60"></div>
      <div class="skeleton-line w-30"></div>
    </div>
  `).join("");
}

/* ---------------- Helpers ---------------- */
function formatTime(raw) {
  if (!raw) return raw;
  const [h, m] = raw.split(":").map(Number);
  const ampm = h >= 12 ? "PM" : "AM";
  const hour = h % 12 || 12;
  return `${hour}:${String(m).padStart(2, "0")} ${ampm}`;
}

function seatsClass(seats) {
  if (seats >= 3) return "seats-high";
  if (seats === 2) return "seats-medium";
  return "seats-low";
}

/* ---------------- Autocomplete (Rabin-Karp via /suggest-locations) ---------------- */
function initAutocomplete(inputId, suggestionsId, onSelect) {
  const input = document.getElementById(inputId);
  const list  = document.getElementById(suggestionsId);
  if (!input || !list) return;

  let debounceTimer;

  input.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    const q = input.value.trim();

    if (!q) { list.innerHTML = ""; list.classList.remove("open"); return; }

    debounceTimer = setTimeout(async () => {
      try {
        const res  = await fetch(`/suggest-locations?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        renderSuggestions(data.suggestions || [], list, input, onSelect);
      } catch (_) { list.innerHTML = ""; list.classList.remove("open"); }
    }, 180);
  });

  // Close suggestions when clicking elsewhere
  document.addEventListener("click", e => {
    if (!input.contains(e.target) && !list.contains(e.target)) {
      list.innerHTML = ""; list.classList.remove("open");
    }
  });
}

function renderSuggestions(items, list, input, onSelect) {
  if (!items.length) { list.innerHTML = ""; list.classList.remove("open"); return; }
  list.innerHTML = items.map(item => `<li data-value="${item}">${item}</li>`).join("");
  list.classList.add("open");

  list.querySelectorAll("li").forEach(li => {
    li.addEventListener("click", () => {
      input.value = li.dataset.value;
      list.innerHTML = ""; list.classList.remove("open");
      if (onSelect) onSelect(li.dataset.value);
    });
  });
}

/* ---------------- Find Ride ---------------- */
function initFindRide() {
  const btn = document.getElementById("btn-find");
  if (!btn) return;

  // Wire autocomplete for the free-text source input
  initAutocomplete("find-source", "find-source-suggestions", null);

  btn.addEventListener("click", async () => {
    const source      = document.getElementById("find-source").value.trim();
    const destination = document.getElementById("find-destination").value;
    const resultsEl   = document.getElementById("find-results");

    if (!source) {
      resultsEl.innerHTML = `<div class="empty-state">Please enter your pickup location.</div>`;
      return;
    }

    // Show skeleton while fetching
    showSkeleton(resultsEl, 3);
    btn.disabled = true;

    try {
      const res  = await fetch("/find-rides", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source, destination }),
      });
      const data = await res.json();
      renderRides(data, resultsEl);
    } catch (_) {
      resultsEl.innerHTML = `<div class="empty-state">Something went wrong. Try again.</div>`;
    } finally {
      btn.disabled = false;
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
        <div><strong>Your optimized route:</strong> ${data.route.path.join(" → ")}</div>
        <div class="muted" style="margin-top:4px;">Distance: <strong style="color:var(--text)">${data.route.distance} km</strong> · via Dijkstra</div>
        <div class="algo-tags">
          ${(data.algorithms_used || []).map(a => `<span class="algo-tag">${a}</span>`).join("")}
        </div>
      </div>
    `;
  }

  data.rides.forEach(ride => {
    const isPathMatch = ride.match_type === "path";
    const pickupLabel = isPathMatch
      ? `<span class="pickup-badge">📍 Picks you up at <strong>${ride.pickup_point}</strong> (passes through your area)</span>`
      : `<span class="pickup-badge source-match">📍 Starts near <strong>${ride.pickup_point}</strong></span>`;

    const pathDisplay = ride.path && ride.path.length
      ? `<div class="path-line">${ride.path.join(" → ")}</div>`
      : "";

    html += `
      <div class="ride-card ${isPathMatch ? "ride-path-match" : ""}">
        <div>
          <div class="driver">${ride.driver_name}</div>
          <div class="route-line">${ride.source} → ${ride.destination}</div>
          ${pathDisplay}
          ${pickupLabel}
          <div class="meta">
           <span>⏱ <strong>${formatTime(ride.time)}</strong>${ride.time_score === 0 ? ' <span style="color:#b91c1c;font-size:.75rem">(departed)</span>' : ride.time_score >= 3 ? ' <span style="color:#047857;font-size:.75rem">(leaving soon)</span>' : ''}</span>

            <span>👥 <strong class="${seatsClass(ride.seats)}">${ride.seats} seats</strong></span>
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
      source:      document.getElementById("add-source").value,
      destination: document.getElementById("add-destination").value,
      time:        document.getElementById("add-time").value,
      seats:       document.getElementById("add-seats").value,
    };
    const feedback = document.getElementById("add-feedback");

    if (!payload.driver_name || !payload.source || !payload.time) {
      feedback.className = "feedback error";
      feedback.textContent = "Please fill driver name, source, and time.";
      return;
    }

    feedback.className = "feedback muted";
    feedback.textContent = "Publishing ride…";
    btn.disabled = true;

    try {
      const res  = await fetch("/add-ride", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.success) {
        feedback.className = "feedback success";
        feedback.textContent = `Ride published successfully · Distance ${data.distance} km`;
        document.getElementById("add-driver").value = "";
        document.getElementById("add-time").value   = "";
      } else {
        feedback.className = "feedback error";
        feedback.textContent = data.message || "Failed to add ride.";
      }
    } catch (_) {
      feedback.className = "feedback error";
      feedback.textContent = "Network error. Try again.";
    } finally {
      btn.disabled = false;
    }
  });
}

/* ---------------- Dashboard ---------------- */
async function initDashboard() {
  const grid = document.getElementById("stat-grid");
  if (!grid) return;

  try {
    const res  = await fetch("/stats");
    const data = await res.json();
    if (!data.success) return;

    document.getElementById("stat-total").textContent  = data.total_rides;
    document.getElementById("stat-routes").textContent = data.active_routes;
    document.getElementById("stat-algos").textContent  = data.algorithms_used;

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
        <td>${formatTime(r.time)}</td>
        <td class="${seatsClass(r.seats)}">${r.seats}</td>
        <td>${r.distance} km</td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Dashboard load failed", err);
  }
}