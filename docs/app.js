(function () {
  "use strict";

  const BOOKMAKER_LABELS = { sportsbet: "Sportsbet", tab: "TAB", unibet: "Unibet" };
  const SPORT_LABELS = {
    americanfootball: "American Football",
    basketball: "Basketball",
    baseball: "Baseball",
    icehockey: "Ice Hockey",
    soccer: "Soccer",
  };

  const state = {
    data: null,
    competitionsByKey: {},
    sort: { key: "edge", dir: "desc" },
    filters: { sport: "", competition: "", bookmaker: "", minEdge: null },
  };

  const els = {
    statusBar: document.getElementById("status-bar"),
    lastUpdated: document.getElementById("last-updated"),
    sportSelect: document.getElementById("filter-sport"),
    competitionSelect: document.getElementById("filter-competition"),
    bookmakerSelect: document.getElementById("filter-bookmaker"),
    minEdgeInput: document.getElementById("filter-min-edge"),
    tbody: document.getElementById("edges-tbody"),
    rowCount: document.getElementById("row-count"),
    marketInfoBody: document.getElementById("market-info-body"),
    unmatchedSection: document.getElementById("unmatched-info"),
    unmatchedList: document.getElementById("unmatched-list"),
    table: document.getElementById("edges-table"),
  };

  function sportLabel(competitionKey) {
    const prefix = competitionKey.split("_")[0];
    return SPORT_LABELS[prefix] || prefix;
  }

  function fmtPct(x, digits) {
    if (x === null || x === undefined) return "–";
    return (x * 100).toFixed(digits === undefined ? 1 : digits) + "%";
  }

  function fmtSignedPct(x) {
    if (x === null || x === undefined) return "–";
    const pct = x * 100;
    const sign = pct > 0 ? "+" : "";
    return sign + pct.toFixed(1) + "%";
  }

  function fmtPrice(x) {
    return x === null || x === undefined ? "–" : x.toFixed(2);
  }

  function fmtMelbourne(isoString, opts) {
    if (!isoString) return "unknown";
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return "unknown";
    return new Intl.DateTimeFormat("en-AU", Object.assign({
      timeZone: "Australia/Melbourne",
      dateStyle: "medium",
      timeStyle: "short",
    }, opts || {})).format(d);
  }

  function loadData() {
    fetch("data.json", { cache: "no-store" })
      .then((r) => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then((data) => {
        state.data = data;
        state.competitionsByKey = {};
        data.competitions.forEach((c) => { state.competitionsByKey[c.key] = c; });
        init();
      })
      .catch((err) => {
        els.lastUpdated.textContent = "Couldn't load data.json (" + err.message + "). The daily update may not have run yet.";
        els.tbody.innerHTML = '<tr><td colspan="10" class="empty-state">No data available yet.</td></tr>';
      });
  }

  function init() {
    const data = state.data;

    els.lastUpdated.innerHTML =
      "Last updated " + escapeHtml(fmtMelbourne(data.generated_at)) + " (Melbourne time). Analysis only &mdash; not betting advice.";

    populateSportOptions();
    populateCompetitionOptions();
    renderMarketInfo();
    renderUnmatched();

    els.sportSelect.addEventListener("change", () => {
      state.filters.sport = els.sportSelect.value;
      populateCompetitionOptions();
      render();
    });
    els.competitionSelect.addEventListener("change", () => {
      state.filters.competition = els.competitionSelect.value;
      render();
    });
    els.bookmakerSelect.addEventListener("change", () => {
      state.filters.bookmaker = els.bookmakerSelect.value;
      render();
    });
    els.minEdgeInput.addEventListener("input", () => {
      const v = parseFloat(els.minEdgeInput.value);
      state.filters.minEdge = isNaN(v) ? null : v;
      render();
    });
    els.table.querySelectorAll("th.sortable").forEach((th) => {
      th.addEventListener("click", () => {
        const key = th.getAttribute("data-sort");
        if (state.sort.key === key) {
          state.sort.dir = state.sort.dir === "desc" ? "asc" : "desc";
        } else {
          state.sort.key = key;
          state.sort.dir = "desc";
        }
        updateSortIndicators();
        render();
      });
    });

    render();
  }

  function populateSportOptions() {
    const sports = new Set(state.data.competitions.map((c) => sportLabel(c.key)));
    const current = els.sportSelect.value;
    els.sportSelect.innerHTML = '<option value="">All sports</option>';
    Array.from(sports).sort().forEach((s) => {
      const opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      els.sportSelect.appendChild(opt);
    });
    els.sportSelect.value = current;
  }

  function populateCompetitionOptions() {
    const sport = state.filters.sport;
    const comps = state.data.competitions.filter((c) => !sport || sportLabel(c.key) === sport);
    const current = els.competitionSelect.value;
    els.competitionSelect.innerHTML = '<option value="">All competitions</option>';
    comps.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c.key;
      opt.textContent = c.name;
      els.competitionSelect.appendChild(opt);
    });
    const stillValid = comps.some((c) => c.key === current);
    els.competitionSelect.value = stillValid ? current : "";
    state.filters.competition = els.competitionSelect.value;
  }

  function updateSortIndicators() {
    els.table.querySelectorAll("th.sortable").forEach((th) => {
      th.classList.remove("sort-asc", "sort-desc");
      if (th.getAttribute("data-sort") === state.sort.key) {
        th.classList.add(state.sort.dir === "asc" ? "sort-asc" : "sort-desc");
      }
    });
  }

  function buildRows() {
    const { sport, competition, bookmaker, minEdge } = state.filters;
    const rows = [];

    state.data.teams.forEach((t) => {
      if (competition && t.competition_key !== competition) return;
      if (sport && sportLabel(t.competition_key) !== sport) return;

      let displayPrice, displayBookmaker, edge, annualisedEdge;
      if (bookmaker) {
        const price = t.prices[bookmaker];
        if (price === null || price === undefined) return;
        displayPrice = price;
        displayBookmaker = bookmaker;
        edge = t.model_probability * price - 1;
        const meta = state.competitionsByKey[t.competition_key];
        const days = meta ? meta.days_to_event : null;
        annualisedEdge = days ? Math.pow(1 + edge, 365 / days) - 1 : null;
      } else {
        displayPrice = t.best_price;
        displayBookmaker = t.best_bookmaker;
        edge = t.edge;
        annualisedEdge = t.annualised_edge;
      }

      if (minEdge !== null && edge * 100 < minEdge) return;

      rows.push(Object.assign({}, t, {
        display_price: displayPrice,
        display_bookmaker: displayBookmaker,
        edge,
        annualised_edge: annualisedEdge,
      }));
    });

    rows.sort((a, b) => {
      const key = state.sort.key;
      let av = a[key], bv = b[key];
      if (av === null || av === undefined) av = -Infinity;
      if (bv === null || bv === undefined) bv = -Infinity;
      const cmp = av < bv ? -1 : av > bv ? 1 : 0;
      return state.sort.dir === "asc" ? cmp : -cmp;
    });

    return rows;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  function priceCell(price, isUsed) {
    const cls = isUsed ? ' class="price-used"' : "";
    return "<td" + cls + ">" + fmtPrice(price) + "</td>";
  }

  function render() {
    const rows = buildRows();
    els.rowCount.textContent = rows.length + " team" + (rows.length === 1 ? "" : "s") + " shown";

    if (rows.length === 0) {
      els.tbody.innerHTML = '<tr><td colspan="10" class="empty-state">No teams match these filters.</td></tr>';
      return;
    }

    const html = rows.map((r) => {
      const edgeCls = r.edge > 0 ? "edge-positive" : r.edge < 0 ? "edge-negative" : "";
      const usedTag = state.filters.bookmaker
        ? ""
        : '<span class="bookmaker-tag">' + (BOOKMAKER_LABELS[r.display_bookmaker] || r.display_bookmaker) + "</span>";

      return (
        "<tr>" +
        '<td class="edge-cell ' + edgeCls + '">' + fmtSignedPct(r.edge) + "</td>" +
        "<td>" + escapeHtml(r.competition_name) + "</td>" +
        "<td>" + escapeHtml(r.team) + "</td>" +
        "<td>" + fmtPct(r.model_probability, 2) + "</td>" +
        "<td>" + fmtPrice(r.fair_odds) + "</td>" +
        priceCell(r.prices.sportsbet, r.display_bookmaker === "sportsbet") +
        priceCell(r.prices.tab, r.display_bookmaker === "tab") +
        priceCell(r.prices.unibet, r.display_bookmaker === "unibet") +
        "<td>" + fmtPrice(r.display_price) + usedTag + "</td>" +
        "<td>" + fmtSignedPct(r.annualised_edge) + "</td>" +
        "</tr>"
      );
    }).join("");

    els.tbody.innerHTML = html;
  }

  function renderMarketInfo() {
    const html = state.data.competitions.map((c) => {
      const overroundParts = Object.keys(BOOKMAKER_LABELS).map((bm) => {
        const v = c.bookmaker_overround ? c.bookmaker_overround[bm] : null;
        return BOOKMAKER_LABELS[bm] + ": " + (v ? fmtPct(v, 0) : "–");
      }).join(" &middot; ");

      const updateParts = Object.keys(BOOKMAKER_LABELS).map((bm) => {
        const v = c.bookmaker_last_update ? c.bookmaker_last_update[bm] : null;
        return BOOKMAKER_LABELS[bm] + " " + (v ? fmtMelbourne(v, { dateStyle: undefined, timeStyle: "short" }) : "n/a");
      }).join(" &middot; ");

      const probSum = c.probability_sum !== null && c.probability_sum !== undefined
        ? " &middot; model probabilities sum to " + fmtPct(c.probability_sum, 1)
        : "";

      return (
        '<div class="market-card">' +
        '<span class="market-name">' + escapeHtml(c.name) + "</span>" +
        '<span class="market-meta">Overround: ' + overroundParts + probSum + "</span>" +
        '<span class="market-meta">Bookmaker odds last updated: ' + updateParts + "</span>" +
        "</div>"
      );
    }).join("");

    els.marketInfoBody.innerHTML = html || "<p>No competitions available.</p>";
  }

  function renderUnmatched() {
    const unmatched = state.data.unmatched || [];
    if (unmatched.length === 0) {
      els.unmatchedSection.hidden = true;
      return;
    }
    els.unmatchedSection.hidden = false;
    els.unmatchedList.innerHTML = unmatched.map((u) => {
      const compName = (state.competitionsByKey[u.competition_key] || {}).name || u.competition_key;
      const reason = u.reason === "no_mapping" ? "no name mapping yet" : "no bookmaker price today";
      return "<li>" + escapeHtml(compName) + ": " + escapeHtml(u.team) + " (" + reason + ")</li>";
    }).join("");
  }

  loadData();
})();
