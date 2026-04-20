from __future__ import annotations

from sma_system.model import EcommerceSMAModel


def run_demo(ticks: int = 8, seed: int = 7) -> None:
    model = EcommerceSMAModel(seed=seed)

    print("=== SMA E-commerce Recommendation (Mesa) ===")
    print("Agents: Profiling, Recommendation, Marketing, Arbitre, Feedback")
    print("Cycle: Perception -> Decision -> Action (parallel phases)")
    print()

    for _ in range(ticks):
        model.step()
        print(model.get_tick_log())

    print("\n=== Final rankings (last tick) ===")
    for user_id, ranking in model.final_rankings.items():
        print(f"{user_id}: {ranking}")

    if model.metrics_history:
        avg_ctr = sum(m["ctr"] for m in model.metrics_history) / len(model.metrics_history)
        avg_sat = sum(m["avg_satisfaction"] for m in model.metrics_history) / len(model.metrics_history)
        avg_div = sum(m["diversity"] for m in model.metrics_history) / len(model.metrics_history)
        print("\n=== Average metrics ===")
        print(f"CTR={avg_ctr:.3f}  Satisfaction={avg_sat:.3f}  Diversity={avg_div:.3f}")


if __name__ == "__main__":
    run_demo()
