export default function StandingsTable({ standings }) {
  if (standings.length === 0) {
    return (
      <p className="empty">
        No teams yet. Register one below and the table starts here.
      </p>
    );
  }

  // A team only leads if it has actually played and sits alone on top.
  const top = standings[0];
  const leads =
    top.played > 0 && (standings.length === 1 || standings[1].points < top.points);

  return (
    <table className="standings">
      <thead>
        <tr>
          <th className="pos" scope="col">
            <span className="sr-only">Position</span>
          </th>
          <th className="team" scope="col">Team</th>
          <th scope="col" title="Played">Pl</th>
          <th scope="col" title="Won">W</th>
          <th scope="col" title="Drawn">D</th>
          <th scope="col" title="Lost">L</th>
          <th className="drop" scope="col" title="Goals for">GF</th>
          <th className="drop" scope="col" title="Goals against">GA</th>
          <th scope="col" title="Goal difference">GD</th>
          <th className="pts" scope="col" title="Points">Pts</th>
        </tr>
      </thead>
      <tbody>
        {standings.map((s, index) => (
          <tr key={s.team} className={index === 0 && leads ? "leader" : undefined}>
            <td className="pos">{s.position}</td>
            <td className="team">{s.team}</td>
            <td>{s.played}</td>
            <td>{s.won}</td>
            <td>{s.drawn}</td>
            <td>{s.lost}</td>
            <td className="drop">{s.goals_for}</td>
            <td className="drop">{s.goals_against}</td>
            <td
              className={
                "gd " +
                (s.goal_difference > 0
                  ? "positive"
                  : s.goal_difference < 0
                    ? "negative"
                    : "")
              }
            >
              {s.goal_difference > 0 ? `+${s.goal_difference}` : s.goal_difference}
            </td>
            <td className="pts">{s.points}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
