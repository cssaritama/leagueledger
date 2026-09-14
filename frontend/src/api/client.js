// Every call to the backend goes through this module.
// No component talks to the network directly, so the transport can change
// without touching the UI.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // response had no JSON body; keep the status line
    }
    throw new Error(detail);
  }

  return response.status === 204 ? null : response.json();
}

export const api = {
  listTeams: () => request("/teams"),

  createTeam: (name) =>
    request("/teams", { method: "POST", body: JSON.stringify({ name }) }),

  listMatches: () => request("/matches"),

  recordMatch: (match) =>
    request("/matches", { method: "POST", body: JSON.stringify(match) }),

  deleteMatch: (id) => request(`/matches/${id}`, { method: "DELETE" }),

  // The table is computed server-side from the recorded matches.
  // There is no local copy to keep in sync.
  getStandings: () => request("/standings"),
};
