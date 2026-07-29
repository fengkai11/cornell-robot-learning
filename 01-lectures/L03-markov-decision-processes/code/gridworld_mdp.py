"""A small, independent MDP lab for Cornell Robot Learning Lecture 03.

This module deliberately focuses on *formulating* and *sampling* an MDP.
It does not implement the official course assignment and does not introduce
value iteration or Q-learning, which belong to later lectures.

Run:
    python gridworld_mdp.py

Test:
    python -m unittest test_gridworld_mdp.py
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Iterable, Mapping, Sequence

import numpy as np


State = tuple[int, int]
Policy = Callable[[State, int], "Action"]


class Action(IntEnum):
    """Discrete actions for the 2-D grid world."""

    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


_ACTION_DELTAS: Mapping[Action, State] = {
    Action.UP: (-1, 0),
    Action.RIGHT: (0, 1),
    Action.DOWN: (1, 0),
    Action.LEFT: (0, -1),
}


@dataclass(frozen=True)
class Transition:
    """One possible transition outcome."""

    probability: float
    next_state: State
    reward: float
    terminated: bool


@dataclass(frozen=True)
class StepRecord:
    """A single realized interaction tuple."""

    t: int
    state: State
    action: Action
    reward: float
    next_state: State
    terminated: bool


@dataclass(frozen=True)
class Episode:
    """A sampled trajectory and its discounted return."""

    records: tuple[StepRecord, ...]
    discounted_return: float

    @property
    def final_state(self) -> State:
        if not self.records:
            raise ValueError("An empty episode has no final state.")
        return self.records[-1].next_state

    @property
    def terminated(self) -> bool:
        return bool(self.records and self.records[-1].terminated)


@dataclass
class GridWorldMDP:
    """Finite grid-world MDP with stochastic lateral action slip.

    State:
        Robot cell `(row, column)`.
    Action:
        Move up, right, down, or left.
    Transition:
        The intended action succeeds with probability `1 - slip_probability`.
        With equal probability, the robot instead executes one of the two
        perpendicular actions. Invalid moves leave the robot in place.
    Reward:
        `goal_reward` on first entry into the goal, otherwise `step_reward`.
    Terminal state:
        The goal is absorbing and ends the episode.
    """

    height: int = 5
    width: int = 6
    start: State = (4, 0)
    goal: State = (0, 5)
    obstacles: frozenset[State] = frozenset({(1, 1), (1, 2), (2, 2), (3, 4)})
    slip_probability: float = 0.2
    step_reward: float = -1.0
    goal_reward: float = 20.0

    def __post_init__(self) -> None:
        if self.height <= 0 or self.width <= 0:
            raise ValueError("height and width must be positive")
        if not 0.0 <= self.slip_probability <= 1.0:
            raise ValueError("slip_probability must lie in [0, 1]")
        for name, state in (("start", self.start), ("goal", self.goal)):
            if not self.in_bounds(state):
                raise ValueError(f"{name} state {state} is out of bounds")
            if state in self.obstacles:
                raise ValueError(f"{name} state {state} cannot be an obstacle")
        for obstacle in self.obstacles:
            if not self.in_bounds(obstacle):
                raise ValueError(f"obstacle {obstacle} is out of bounds")

    @property
    def states(self) -> tuple[State, ...]:
        """All valid states, including the terminal goal state."""

        return tuple(
            (row, col)
            for row in range(self.height)
            for col in range(self.width)
            if (row, col) not in self.obstacles
        )

    @property
    def actions(self) -> tuple[Action, ...]:
        return tuple(Action)

    def in_bounds(self, state: State) -> bool:
        row, col = state
        return 0 <= row < self.height and 0 <= col < self.width

    def is_terminal(self, state: State) -> bool:
        return state == self.goal

    def _apply_action(self, state: State, action: Action) -> State:
        if self.is_terminal(state):
            return state
        delta_row, delta_col = _ACTION_DELTAS[action]
        candidate = (state[0] + delta_row, state[1] + delta_col)
        if not self.in_bounds(candidate) or candidate in self.obstacles:
            return state
        return candidate

    @staticmethod
    def _perpendicular_actions(action: Action) -> tuple[Action, Action]:
        if action in (Action.UP, Action.DOWN):
            return Action.LEFT, Action.RIGHT
        return Action.UP, Action.DOWN

    def transition_distribution(
        self, state: State, action: Action
    ) -> tuple[Transition, ...]:
        """Return P(s' | s, a) with outcomes merged by next state.

        The method depends only on `(state, action)`, which makes the modeled
        process Markov. A real robot may violate this assumption when hidden
        variables such as velocity, contact mode, actuator temperature, or
        object motion are omitted from the state.
        """

        if state not in self.states:
            raise ValueError(f"invalid state: {state}")
        action = Action(action)

        if self.is_terminal(state):
            return (
                Transition(
                    probability=1.0,
                    next_state=state,
                    reward=0.0,
                    terminated=True,
                ),
            )

        side_a, side_b = self._perpendicular_actions(action)
        outcomes = (
            (1.0 - self.slip_probability, action),
            (self.slip_probability / 2.0, side_a),
            (self.slip_probability / 2.0, side_b),
        )

        merged: dict[State, float] = {}
        for probability, executed_action in outcomes:
            if probability <= 0.0:
                continue
            next_state = self._apply_action(state, executed_action)
            merged[next_state] = merged.get(next_state, 0.0) + probability

        transitions: list[Transition] = []
        for next_state, probability in sorted(merged.items()):
            terminated = self.is_terminal(next_state)
            reward = self.goal_reward if terminated else self.step_reward
            transitions.append(
                Transition(
                    probability=probability,
                    next_state=next_state,
                    reward=reward,
                    terminated=terminated,
                )
            )

        total_probability = sum(item.probability for item in transitions)
        if not np.isclose(total_probability, 1.0):
            raise RuntimeError(
                f"transition probabilities sum to {total_probability}, not 1"
            )
        return tuple(transitions)

    def sample_transition(
        self,
        state: State,
        action: Action,
        rng: np.random.Generator,
    ) -> Transition:
        distribution = self.transition_distribution(state, action)
        probabilities = np.asarray(
            [transition.probability for transition in distribution], dtype=float
        )
        index = int(rng.choice(len(distribution), p=probabilities))
        return distribution[index]

    def rollout(
        self,
        policy: Policy,
        *,
        horizon: int = 30,
        gamma: float = 0.95,
        seed: int | None = None,
        initial_state: State | None = None,
    ) -> Episode:
        """Sample one finite-horizon trajectory under a policy."""

        if horizon <= 0:
            raise ValueError("horizon must be positive")
        if not 0.0 <= gamma <= 1.0:
            raise ValueError("gamma must lie in [0, 1]")

        state = self.start if initial_state is None else initial_state
        if state not in self.states:
            raise ValueError(f"invalid initial_state: {state}")

        rng = np.random.default_rng(seed)
        records: list[StepRecord] = []
        discounted_return = 0.0

        for t in range(horizon):
            if self.is_terminal(state):
                break
            action = Action(policy(state, t))
            transition = self.sample_transition(state, action, rng)
            records.append(
                StepRecord(
                    t=t,
                    state=state,
                    action=action,
                    reward=transition.reward,
                    next_state=transition.next_state,
                    terminated=transition.terminated,
                )
            )
            discounted_return += (gamma**t) * transition.reward
            state = transition.next_state
            if transition.terminated:
                break

        return Episode(
            records=tuple(records), discounted_return=float(discounted_return)
        )

    def render(self, state: State | None = None) -> str:
        """Return a compact text rendering suitable for a terminal or Markdown."""

        state = self.start if state is None else state
        rows: list[str] = []
        for row in range(self.height):
            cells: list[str] = []
            for col in range(self.width):
                cell = (row, col)
                if cell == state:
                    token = "R"
                elif cell == self.goal:
                    token = "G"
                elif cell == self.start:
                    token = "S"
                elif cell in self.obstacles:
                    token = "#"
                else:
                    token = "."
                cells.append(token)
            rows.append(" ".join(cells))
        return "\n".join(rows)


def discounted_return(rewards: Iterable[float], gamma: float) -> float:
    """Compute sum_t gamma^t r_t."""

    if not 0.0 <= gamma <= 1.0:
        raise ValueError("gamma must lie in [0, 1]")
    return float(sum((gamma**t) * reward for t, reward in enumerate(rewards)))


def greedy_goal_policy(goal: State) -> Policy:
    """A myopic policy that reduces Manhattan distance when possible.

    This policy ignores obstacles and action uncertainty. It is intentionally
    simple so failures can be attributed to the policy/state formulation rather
    than hidden optimization machinery.
    """

    def policy(state: State, _: int) -> Action:
        row_error = goal[0] - state[0]
        col_error = goal[1] - state[1]
        if abs(col_error) >= abs(row_error) and col_error != 0:
            return Action.RIGHT if col_error > 0 else Action.LEFT
        if row_error != 0:
            return Action.DOWN if row_error > 0 else Action.UP
        return Action.RIGHT

    return policy


def waypoint_policy(waypoints: Sequence[State]) -> Policy:
    """Create a finite-memory policy by augmenting decision state with time.

    The policy chooses the waypoint indexed by time. It illustrates that a
    finite-horizon policy may depend on `t`, and that hidden internal memory must
    be represented explicitly if it affects future action selection.
    """

    if not waypoints:
        raise ValueError("waypoints must not be empty")

    def policy(state: State, t: int) -> Action:
        target = waypoints[min(t, len(waypoints) - 1)]
        row_error = target[0] - state[0]
        col_error = target[1] - state[1]
        if col_error != 0:
            return Action.RIGHT if col_error > 0 else Action.LEFT
        if row_error != 0:
            return Action.DOWN if row_error > 0 else Action.UP
        return Action.RIGHT

    return policy


def evaluate_policy(
    mdp: GridWorldMDP,
    policy: Policy,
    *,
    episodes: int = 500,
    horizon: int = 30,
    gamma: float = 0.95,
    seed: int = 0,
) -> dict[str, float]:
    """Estimate return and success statistics by Monte Carlo rollouts."""

    if episodes <= 0:
        raise ValueError("episodes must be positive")
    seed_sequence = np.random.SeedSequence(seed)
    child_seeds = seed_sequence.spawn(episodes)

    returns: list[float] = []
    successes = 0
    lengths: list[int] = []
    for child_seed in child_seeds:
        episode_seed = int(child_seed.generate_state(1, dtype=np.uint32)[0])
        episode = mdp.rollout(
            policy,
            horizon=horizon,
            gamma=gamma,
            seed=episode_seed,
        )
        returns.append(episode.discounted_return)
        lengths.append(len(episode.records))
        successes += int(episode.terminated)

    return {
        "mean_return": float(np.mean(returns)),
        "return_std": float(np.std(returns)),
        "success_rate": successes / episodes,
        "mean_length": float(np.mean(lengths)),
    }


def format_episode(episode: Episode) -> str:
    if not episode.records:
        return "<empty episode>"
    lines = ["t  state   action  reward  next    done"]
    for item in episode.records:
        lines.append(
            f"{item.t:<2} {str(item.state):<7} {item.action.name:<6} "
            f"{item.reward:>6.1f}  {str(item.next_state):<7} {item.terminated}"
        )
    lines.append(f"discounted_return={episode.discounted_return:.3f}")
    return "\n".join(lines)


def main() -> None:
    mdp = GridWorldMDP()
    policy = greedy_goal_policy(mdp.goal)

    print("GridWorld MDP")
    print(mdp.render())
    print()
    print("One sampled trajectory")
    episode = mdp.rollout(policy, horizon=30, gamma=0.95, seed=7)
    print(format_episode(episode))
    print()
    print("Monte Carlo policy evaluation")
    metrics = evaluate_policy(mdp, policy, episodes=500, seed=7)
    for name, value in metrics.items():
        print(f"{name}: {value:.3f}")


if __name__ == "__main__":
    main()
