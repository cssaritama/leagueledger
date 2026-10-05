import { useEffect, useState } from "react";
import { api } from "./api/client";
import StandingsTable from "./components/StandingsTable";
import MatchForm from "./components/MatchForm";
import MatchList from "./components/MatchList";
import TeamForm from "./components/TeamForm";
import "./App.css";

export default function App() {
  const [teams, setTeams] = useState([]);
  const [matches, setMatches] = useState([]);
  const [standings, setStandings] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // One refresh path for everything. After any write the table is re-read from
  // the server rather than patched locally, which is the whole reason for
  // deriving standings instead of storing them.
  async function refresh() {
    try {
      const [nextTeams, nextMatches, nextStandings] = await Promise.all([
        api.listTeams(),
        api.listMatches(),
        api.getStandings(),
      ]);
      setTeams(nextTeams);
      setMatches(nextMatches);
      setStandings(nextStandings);
      setError(null);
    } catch (err) {
      setError(err.message || "The backend is not responding on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  // Loading the league on mount is exactly the case an effect is for:
  // synchronising with an external system. The lint rule cannot tell that
  // refresh() is an async network read rather than derived state.
  // oxlint-disable-next-line react/set-state-in-effect
  useEffect(() => {
    refresh();
  }, []);

  async function handle(action) {
    try {
      await action();
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <p className="loading">Loading the league</p>;

  return (
    <div className="app">
      <header className="masthead">
        <h1>LeagueLedger</h1>
        <p>
          Results are recorded as facts. The table is recalculated from them
          every time it loads, so it can never drift away from the results
          behind it.
        </p>
      </header>

      {error && <p className="error">{error}</p>}

      <StandingsTable standings={standings} />

      <div className="columns section">
        <section>
          <h2>Teams</h2>
          <TeamForm onSubmit={(name) => handle(() => api.createTeam(name))} />
          <p className="count">
            {teams.length === 0
              ? "None registered"
              : `${teams.length} registered`}
          </p>
        </section>

        <section>
          <h2>Record a result</h2>
          <MatchForm
            teams={teams}
            onSubmit={(match) => handle(() => api.recordMatch(match))}
          />
        </section>
      </div>

      <section className="section">
        <h2>Results</h2>
        <MatchList
          matches={matches}
          onDelete={(id) => handle(() => api.deleteMatch(id))}
        />
      </section>
    </div>
  );
}
