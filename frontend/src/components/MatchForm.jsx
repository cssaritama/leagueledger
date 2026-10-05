import { useState } from "react";

const EMPTY = { home_team_id: "", away_team_id: "", home_goals: 0, away_goals: 0 };

export default function MatchForm({ teams, onSubmit }) {
  const [form, setForm] = useState(EMPTY);

  if (teams.length < 2) {
    return (
      <p className="empty">
        Two teams are needed before a result can be recorded.
      </p>
    );
  }

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  const sameTeam =
    form.home_team_id !== "" && form.home_team_id === form.away_team_id;
  const incomplete = !form.home_team_id || !form.away_team_id;

  function submit(event) {
    event.preventDefault();
    if (incomplete || sameTeam) return;

    onSubmit({
      home_team_id: Number(form.home_team_id),
      away_team_id: Number(form.away_team_id),
      home_goals: Number(form.home_goals),
      away_goals: Number(form.away_goals),
    });
    setForm(EMPTY);
  }

  return (
    <form onSubmit={submit} className="record-result">
      <div className="field-row">
        <select
          value={form.home_team_id}
          onChange={(e) => update("home_team_id", e.target.value)}
          aria-label="Home team"
        >
          <option value="">Home team</option>
          {teams.map((t) => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
        <input
          type="number"
          min="0"
          max="99"
          value={form.home_goals}
          onChange={(e) => update("home_goals", e.target.value)}
          aria-label="Home goals"
        />
      </div>

      <div className="field-row">
        <select
          value={form.away_team_id}
          onChange={(e) => update("away_team_id", e.target.value)}
          aria-label="Away team"
        >
          <option value="">Away team</option>
          {teams.map((t) => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
        <input
          type="number"
          min="0"
          max="99"
          value={form.away_goals}
          onChange={(e) => update("away_goals", e.target.value)}
          aria-label="Away goals"
        />
      </div>

      {sameTeam && <p className="note">Pick two different teams.</p>}

      <button type="submit" disabled={incomplete || sameTeam}>
        Record result
      </button>
    </form>
  );
}
