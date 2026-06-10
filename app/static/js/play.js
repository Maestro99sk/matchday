/* Matchday pick-a-5: cycle formations, fill slots from the day's pool,
   enforce budget + max-per-team, submit lineup with subs bench. */
(function () {
  const cfgEl = document.getElementById("cfg");
  if (!cfgEl) return;
  const cfg = JSON.parse(cfgEl.textContent);

  const ROLE_COLOR = { GK: "#ffb300", DEF: "#39c0ff", MID: "#00e676", FWD: "#ff5a8a" };
  const FORMATION_NAMES = {
    "1-2-1": "The Diamond", "2-1-1": "The Anchor", "1-1-2": "The Spearhead",
    "2-2": "The Box", "3-1": "The Wall", "1-3": "The Blitz"
  };
  const COORDS = {
    "1-2-1": [[50,88],[50,66],[24,44],[76,44],[50,20]],
    "2-1-1": [[50,88],[30,66],[70,66],[50,44],[50,20]],
    "1-1-2": [[50,88],[50,66],[50,44],[30,20],[70,20]],
    "2-2":   [[50,88],[30,62],[70,62],[30,28],[70,28]],
    "3-1":   [[50,88],[22,62],[50,64],[78,62],[50,26]],
    "1-3":   [[50,88],[50,64],[22,30],[50,24],[78,30]],
  };
  const BENCH_POS_ORDER = ["GK", "DEF", "MID", "FWD"];
  function benchSlots() {
    const shp = shape();
    return BENCH_POS_ORDER
      .filter(pos => shp.includes(pos))
      .map((role, i) => ({slot: 5 + i, role}));
  }
  const FLAGS = {
    "Czech Republic":"🇨🇿","Mexico":"🇲🇽","South Africa":"🇿🇦","South Korea":"🇰🇷",
    "Canada":"🇨🇦","Bosnia and Herzegovina":"🇧🇦","United States":"🇺🇸","Paraguay":"🇵🇾",
    "Qatar":"🇶🇦","Switzerland":"🇨🇭","Brazil":"🇧🇷","Morocco":"🇲🇦","Haiti":"🇭🇹",
    "Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","Australia":"🇦🇺","Turkey":"🇹🇷","Germany":"🇩🇪",
    "Curacao":"🇨🇼","Spain":"🇪🇸","Egypt":"🇪🇬","Argentina":"🇦🇷","Algeria":"🇩🇿",
    "Portugal":"🇵🇹","Senegal":"🇸🇳","Belgium":"🇧🇪","Ivory Coast":"🇨🇮",
    "Netherlands":"🇳🇱","Japan":"🇯🇵","Croatia":"🇭🇷","Ghana":"🇬🇭","Uruguay":"🇺🇾",
    "Panama":"🇵🇦","Colombia":"🇨🇴","Uzbekistan":"🇺🇿","England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Iran":"🇮🇷","Ecuador":"🇪🇨","Norway":"🇳🇴","Austria":"🇦🇹","Saudi Arabia":"🇸🇦",
    "France":"🇫🇷","Italy":"🇮🇹","Denmark":"🇩🇰","Serbia":"🇷🇸","Poland":"🇵🇱",
    "Ukraine":"🇺🇦","Wales":"🏴󠁧󠁢󠁷󠁬󠁳󠁿","Cameroon":"🇨🇲","Tunisia":"🇹🇳",
    "Nigeria":"🇳🇬","New Zealand":"🇳🇿","Chile":"🇨🇱","Peru":"🇵🇪",
    "Venezuela":"🇻🇪","Honduras":"🇭🇳","Costa Rica":"🇨🇷","Jamaica":"🇯🇲",
  };
  function flag(team) { return FLAGS[team] || team.slice(0,3).toUpperCase(); }

  const fIds = Object.keys(cfg.formations);
  const byId = {}; cfg.pool.forEach(p => byId[p.id] = p);

  let idx = 0;
  let lineup = {};      // slotIndex (0-4) -> player
  let subsLineup = {};  // slotIndex (5-8) -> player
  let activeSlot = null;

  const pitch = document.getElementById("pitch");
  const fName = document.getElementById("fName");
  const fSub  = document.getElementById("fSub");
  const fDots = document.getElementById("fDots");
  const remaining = document.getElementById("remaining");
  const tray = document.getElementById("tray");
  const bench = document.getElementById("bench");
  const progress = document.getElementById("progress");
  const confirmBtn = document.getElementById("confirmBtn");

  // restore existing lineup
  if (cfg.existing && cfg.existing.formation) {
    const fi = fIds.indexOf(cfg.existing.formation);
    if (fi >= 0) {
      idx = fi;
      cfg.existing.picks.forEach(pk => {
        const pl = byId[pk.player_id];
        if (!pl) return;
        if (pk.slot < 5) lineup[pk.slot] = pl;
        else subsLineup[pk.slot] = pl;
      });
    }
  }

  // formation dots
  fIds.forEach((id, i) => {
    const b = document.createElement("button");
    b.className = "fdot" + (i === idx ? " on" : "");
    b.setAttribute("aria-label", id);
    b.onclick = () => { idx = i; lineup = {}; subsLineup = {}; activeSlot = null; render(); };
    fDots.appendChild(b);
  });

  function shape() { return cfg.formations[fIds[idx]]; }

  function cycle(d) {
    idx = (idx + d + fIds.length) % fIds.length;
    lineup = {}; subsLineup = {}; activeSlot = null; render();
  }
  document.getElementById("fPrev").onclick = () => cycle(-1);
  document.getElementById("fNext").onclick = () => cycle(1);
  window.addEventListener("keydown", e => {
    if (e.key === "ArrowLeft") cycle(-1);
    if (e.key === "ArrowRight") cycle(1);
  });

  function totalSpent() {
    return Object.values(lineup).reduce((s, p) => s + p.value, 0)
         + Object.values(subsLineup).reduce((s, p) => s + p.value, 0);
  }

  function starterTeamCounts() {
    const c = {};
    Object.values(lineup).forEach(p => { c[p.team] = (c[p.team] || 0) + 1; });
    return c;
  }

  // Nations that have a starter in a given role — sub must come from one of these
  function starterNationsForRole(role) {
    const nations = new Set();
    const shp = shape();
    shp.forEach((r, i) => { if (r === role && lineup[i]) nations.add(lineup[i].team); });
    return nations;
  }

  function activePlayerValue() {
    if (activeSlot === null) return 0;
    const p = activeSlot < 5 ? lineup[activeSlot] : subsLineup[activeSlot];
    return p ? p.value : 0;
  }

  function render() {
    const fid = fIds[idx];
    fName.textContent = fid;
    fSub.textContent = FORMATION_NAMES[fid] || "";
    Array.from(fDots.children).forEach((d, i) => d.className = "fdot" + (i === idx ? " on" : ""));

    pitch.querySelectorAll(".slot").forEach(n => n.remove());

    const shp = shape();
    const coords = COORDS[fid];
    shp.forEach((role, i) => {
      const [x, y] = coords[i];
      const player = lineup[i];
      const color = ROLE_COLOR[role];
      const active = activeSlot === i;

      const btn = document.createElement("button");
      btn.className = "slot";
      btn.style.left = x + "%"; btn.style.top = y + "%";
      btn.style.animation = `slotIn .3s cubic-bezier(.2,.8,.2,1) ${i * 0.04}s both`;

      const tok = document.createElement("span");
      tok.className = "token" + (player ? " filled" : "");
      tok.style.borderColor = color;
      tok.style.boxShadow = active
        ? `0 0 0 3px ${color},0 8px 22px rgba(0,0,0,.5)` : `0 6px 16px rgba(0,0,0,.45)`;

      if (player) {
        tok.innerHTML =
          `<span class="tok-flag">${flag(player.team)}</span>` +
          `<span class="tok-val" style="color:${color}">${player.value}</span>`;
        const nameLabel = document.createElement("span");
        nameLabel.className = "slot-name";
        nameLabel.textContent = shortName(player.name);
        btn.appendChild(tok);
        btn.appendChild(nameLabel);
        const xBtn = document.createElement("span");
        xBtn.className = "tok-remove"; xBtn.textContent = "×";
        xBtn.onclick = (e) => { e.stopPropagation(); delete lineup[i]; if (activeSlot===i) activeSlot=null; render(); };
        btn.appendChild(xBtn);
      } else {
        tok.innerHTML = `<span class="tok-role" style="color:${color}">${role}</span>`;
        btn.appendChild(tok);
      }
      btn.onclick = () => { activeSlot = active ? null : i; render(); };
      pitch.appendChild(btn);
    });

    const rem = cfg.budget - totalSpent();
    remaining.textContent = rem;
    remaining.className = "num" + (rem < 0 ? " over" : "");

    const filled = Object.keys(lineup).length;
    const bs = benchSlots();
    progress.textContent = `${filled}/${shp.length} starters · ${Object.keys(subsLineup).length}/${bs.length} subs`;
    const ok = filled === shp.length && rem >= 0;
    confirmBtn.style.opacity = ok ? 1 : .4;
    confirmBtn.style.pointerEvents = ok ? "auto" : "none";
    confirmBtn.textContent = ok ? "Confirm lineup" : (rem < 0 ? "Over budget" : "Tap a slot to fill");

    renderBench();
    renderTray();
  }

  function renderBench() {
    let html = `<div class="bench-wrap">
      <div class="bench-label">SUBS BENCH</div>
      <div class="bench-slots">`;
    benchSlots().forEach(({slot, role}) => {
      const player = subsLineup[slot];
      const color = ROLE_COLOR[role];
      const active = activeSlot === slot;
      const shadow = active ? `box-shadow:0 0 0 3px ${color},0 8px 22px rgba(0,0,0,.5);` : "";
      if (player) {
        html += `<div class="bench-slot-wrap">
          <button class="bench-slot filled${active ? " active" : ""}" data-slot="${slot}"
            style="border-color:${color};${shadow}">
            <span class="tok-flag">${flag(player.team)}</span>
            <span class="tok-val" style="color:${color}">${player.value}</span>
            <span class="bench-remove" data-slot="${slot}">×</span>
          </button>
          <span class="bench-name">${escapeHtml(shortName(player.name))}</span>
        </div>`;
      } else {
        html += `<div class="bench-slot-wrap">
          <button class="bench-slot${active ? " active" : ""}" data-slot="${slot}"
            style="border-color:${color};${shadow}">
            <span class="tok-role" style="color:${color}">${role}</span>
          </button>
          <span class="bench-name"></span>
        </div>`;
      }
    });
    html += `</div></div>`;
    bench.innerHTML = html;

    bench.querySelectorAll(".bench-slot").forEach(btn => {
      const sl = parseInt(btn.getAttribute("data-slot"), 10);
      btn.onclick = () => { activeSlot = activeSlot === sl ? null : sl; render(); };
    });
    bench.querySelectorAll(".bench-remove").forEach(x => {
      x.onclick = (e) => {
        e.stopPropagation();
        const sl = parseInt(x.getAttribute("data-slot"), 10);
        delete subsLineup[sl];
        if (activeSlot === sl) activeSlot = null;
        render();
      };
    });
  }

  function renderTray() {
    if (activeSlot === null) { tray.innerHTML = ""; return; }
    const isSub = activeSlot >= 5;
    const role = isSub
      ? benchSlots().find(b => b.slot === activeSlot).role
      : shape()[activeSlot];
    const color = ROLE_COLOR[role];
    const usedIds = new Set([
      ...Object.values(lineup).map(p => p.id),
      ...Object.values(subsLineup).map(p => p.id),
    ]);
    const currentPlayer = isSub ? subsLineup[activeSlot] : lineup[activeSlot];
    const rem = cfg.budget - totalSpent() + (currentPlayer ? currentPlayer.value : 0);

    const allEligible = cfg.pool.filter(p => p.pos === role);

    // For sub slots: only show players from nations that have a starter in this role
    const starterNations = isSub ? starterNationsForRole(role) : null;
    const noStarterYet = isSub && starterNations.size === 0;
    const eligible = isSub ? allEligible.filter(p => starterNations.has(p.team)) : allEligible;

    const counts = isSub ? {} : starterTeamCounts();
    const maxForSlot = cfg.maxStartersPerTeam;
    const cards = eligible.map(p => {
      const currentlyHere = currentPlayer && currentPlayer.id === p.id;
      const usedElsewhere = usedIds.has(p.id) && !currentlyHere;
      const teamFull = !isSub && (counts[p.team] || 0) >= maxForSlot &&
                       !(currentPlayer && currentPlayer.team === p.team);
      const tooDear = p.value > rem;
      const disabled = usedElsewhere || teamFull || tooDear;
      let why = "";
      if (usedElsewhere) why = "in XI";
      else if (teamFull) why = "team full";
      else if (tooDear) why = "too dear";
      const teamDisplay = (disabled && why) ? why : flag(p.team);
      return `<button class="tray-card" data-pid="${p.id}" ${disabled ? "disabled" : ""}>
        <span class="tpos" style="color:${color}">${p.pos}</span>
        <span class="tname">${escapeHtml(p.name)}</span>
        <span class="tval">${p.value}</span>
        <span class="tteam">${teamDisplay}</span>
      </button>`;
    }).join("");

    const label = isSub ? `<b style="color:${color}">${role}</b> sub` : `<b style="color:${color}">${role}</b>`;
    let listHtml;
    if (noStarterYet) {
      listHtml = `<p class="muted center">Pick your ${role} starter first — your sub must be from the same nation.</p>`;
    } else if (eligible.length === 0) {
      listHtml = `<p class="muted center">No ${role} available from your starter's nation.</p>`;
    } else {
      listHtml = `<div class="tray-list">${cards}</div>`;
    }
    tray.innerHTML = `
      <div class="tray">
        <div class="tray-head"><span>Pick a ${label}</span>
          <button class="btn ghost sm" id="trayCancel">Cancel</button></div>
        ${listHtml}
      </div>`;
    document.getElementById("trayCancel").onclick = () => { activeSlot = null; render(); };
    tray.querySelectorAll(".tray-card").forEach(btn => {
      if (btn.disabled) return;
      btn.onclick = () => {
        const pid = parseInt(btn.getAttribute("data-pid"), 10);
        if (isSub) {
          Object.keys(subsLineup).forEach(k => { if (subsLineup[k].id === pid) delete subsLineup[k]; });
          subsLineup[activeSlot] = byId[pid];
        } else {
          Object.keys(lineup).forEach(k => { if (lineup[k].id === pid) delete lineup[k]; });
          lineup[activeSlot] = byId[pid];
        }
        activeSlot = null;
        render();
      };
    });
  }

  confirmBtn.onclick = async () => {
    const shp = shape();
    const starterPicks = Object.keys(lineup).map(slot => ({
      slot: parseInt(slot, 10), role: shp[slot], player_id: lineup[slot].id,
    }));
    const subPicks = Object.keys(subsLineup).map(slot => ({
      slot: parseInt(slot, 10),
      role: benchSlots().find(b => b.slot === parseInt(slot, 10)).role,
      player_id: subsLineup[slot].id,
    }));
    if (starterPicks.length !== shp.length) return;
    confirmBtn.disabled = true; confirmBtn.textContent = "Saving…";
    try {
      const res = await fetch(cfg.submitUrl, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ formation: fIds[idx], picks: [...starterPicks, ...subPicks] }),
      });
      const data = await res.json();
      if (data.ok) {
        location.href = data.redirect || location.pathname;
      } else {
        alert(data.msg || "Something went wrong.");
        confirmBtn.disabled = false; render();
      }
    } catch (e) {
      alert("Network error. Try again.");
      confirmBtn.disabled = false; render();
    }
  };

  function shortName(n) { return n.length > 10 ? n.split(" ").slice(-1)[0] : n; }
  function escapeHtml(s) {
    return s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }

  render();
})();
