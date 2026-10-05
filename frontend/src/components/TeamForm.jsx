import { useState } from "react";

export default function TeamForm({ onSubmit }) {
  const [name, setName] = useState("");

  function submit(event) {
    event.preventDefault();
    const value = name.trim();
    if (!value) return;
    onSubmit(value);
    setName("");
  }

  return (
    <form onSubmit={submit}>
      <div className="field-row">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Team name"
          maxLength={60}
          aria-label="Team name"
        />
        <button type="submit">Register</button>
      </div>
    </form>
  );
}
