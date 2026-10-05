export default function MatchList({ matches, onDelete }) {
  if (matches.length === 0) {
    return (
      <p className="empty">
        Nothing recorded yet. Results appear here as you add them, newest first.
      </p>
    );
  }

  return (
    <ul className="results">
      {matches.map((m) => (
        <li key={m.id}>
          <span className="fixture">
            {m.home_team}
            <span className="score">{m.home_goals}</span>
            &ndash;
            <span className="score">{m.away_goals}</span>
            {m.away_team}
          </span>
          <button
            type="button"
            className="remove"
            onClick={() => onDelete(m.id)}
            aria-label={`Remove ${m.home_team} against ${m.away_team}`}
          >
            Remove
          </button>
        </li>
      ))}
    </ul>
  );
}
