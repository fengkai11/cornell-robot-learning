"""Unit tests for the independent Lecture 03 GridWorld MDP lab."""

from __future__ import annotations

import unittest

import numpy as np

from gridworld_mdp import (
    Action,
    GridWorldMDP,
    discounted_return,
    evaluate_policy,
    greedy_goal_policy,
)


class GridWorldMDPTest(unittest.TestCase):
    def test_transition_probabilities_sum_to_one(self) -> None:
        mdp = GridWorldMDP(slip_probability=0.2)
        for state in mdp.states:
            for action in mdp.actions:
                total = sum(
                    item.probability
                    for item in mdp.transition_distribution(state, action)
                )
                self.assertTrue(np.isclose(total, 1.0))

    def test_terminal_state_is_absorbing(self) -> None:
        mdp = GridWorldMDP()
        for action in mdp.actions:
            distribution = mdp.transition_distribution(mdp.goal, action)
            self.assertEqual(len(distribution), 1)
            transition = distribution[0]
            self.assertEqual(transition.next_state, mdp.goal)
            self.assertEqual(transition.reward, 0.0)
            self.assertTrue(transition.terminated)
            self.assertEqual(transition.probability, 1.0)

    def test_invalid_move_stays_in_place(self) -> None:
        mdp = GridWorldMDP(slip_probability=0.0)
        distribution = mdp.transition_distribution((0, 0), Action.UP)
        self.assertEqual(len(distribution), 1)
        self.assertEqual(distribution[0].next_state, (0, 0))

    def test_transition_model_is_history_independent(self) -> None:
        mdp = GridWorldMDP(slip_probability=0.3)
        first = mdp.transition_distribution((4, 0), Action.RIGHT)
        second = mdp.transition_distribution((4, 0), Action.RIGHT)
        self.assertEqual(first, second)

    def test_discounted_return(self) -> None:
        value = discounted_return([1.0, 2.0, 3.0], gamma=0.5)
        self.assertAlmostEqual(value, 1.0 + 0.5 * 2.0 + 0.25 * 3.0)

    def test_seeded_rollout_is_reproducible(self) -> None:
        mdp = GridWorldMDP()
        policy = greedy_goal_policy(mdp.goal)
        first = mdp.rollout(policy, seed=42)
        second = mdp.rollout(policy, seed=42)
        self.assertEqual(first, second)

    def test_policy_evaluation_returns_valid_metrics(self) -> None:
        mdp = GridWorldMDP()
        metrics = evaluate_policy(
            mdp,
            greedy_goal_policy(mdp.goal),
            episodes=20,
            seed=3,
        )
        self.assertGreaterEqual(metrics["success_rate"], 0.0)
        self.assertLessEqual(metrics["success_rate"], 1.0)
        self.assertGreater(metrics["mean_length"], 0.0)


if __name__ == "__main__":
    unittest.main()
