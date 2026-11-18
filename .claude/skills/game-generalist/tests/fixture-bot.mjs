// Closed-loop module bot for fixture-game.html: reads state() and holds ArrowRight until the goal.
export function act(state, elapsedMs) {
  if (state.status !== "playing") return [];
  return state.progress < 100 ? ["ArrowRight"] : [];
}
