from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from mesa import Model

from .agents import (
    AgentArbitre,
    AgentFeedback,
    AgentMarketing,
    AgentProfiling,
    AgentRecommendation,
    Product,
    UserState,
)


class EcommerceSMAModel(Model):
    """Mesa model for a recommendation system implemented as a true SMA."""

    def __init__(self, seed: int | None = 42):
        super().__init__(seed=seed)

        self.tick = 0
        self.message_bus: Dict[str, List[dict]] = defaultdict(list)

        self.users: Dict[str, UserState] = self._build_users()
        self.products: Dict[str, Product] = self._build_products()
        self.promotions: Dict[str, float] = self._build_promotions()

        self.user_profiles: Dict[str, Dict[str, float]] = {
            uid: dict(user.interests) for uid, user in self.users.items()
        }

        self.candidate_recommendations: Dict[str, List[tuple[str, float]]] = {}
        self.marketing_rankings: Dict[str, List[str]] = {}
        self.final_rankings: Dict[str, List[str]] = {}

        self.interactions_last_tick: List[dict] = []

        self.last_metrics = {
            "ctr": 0.0,
            "conversion": 0.0,
            "avg_satisfaction": 0.5,
            "diversity": 0.0,
        }
        self.metrics_history: List[dict] = []

        self.sma_agents = [
            AgentProfiling(self),
            AgentRecommendation(self),
            AgentMarketing(self),
            AgentArbitre(self),
            AgentFeedback(self),
        ]

    def _build_users(self) -> Dict[str, UserState]:
        return {
            "u1": UserState("u1", {"tech": 0.6, "fashion": 0.25, "home": 0.15}, 0.3),
            "u2": UserState("u2", {"tech": 0.2, "fashion": 0.65, "home": 0.15}, 0.55),
            "u3": UserState("u3", {"tech": 0.2, "fashion": 0.2, "home": 0.6}, 0.4),
        }

    def _build_products(self) -> Dict[str, Product]:
        products = [
            Product("p1", "tech", 120, stock=8, margin=0.28),
            Product("p2", "tech", 80, stock=5, margin=0.18),
            Product("p3", "fashion", 45, stock=10, margin=0.35),
            Product("p4", "fashion", 95, stock=3, margin=0.42),
            Product("p5", "home", 60, stock=7, margin=0.25),
            Product("p6", "home", 135, stock=4, margin=0.30),
            Product("p7", "tech", 40, stock=12, margin=0.12),
            Product("p8", "fashion", 70, stock=9, margin=0.22),
            Product("p9", "home", 30, stock=11, margin=0.16),
        ]
        return {p.product_id: p for p in products}

    def _build_promotions(self) -> Dict[str, float]:
        return {
            "p3": 0.9,
            "p6": 0.6,
            "p2": 0.4,
        }

    def send_message(self, recipient: str, message_type: str, payload: dict) -> None:
        self.message_bus[recipient].append(
            {
                "type": message_type,
                "payload": payload,
                "tick": self.tick,
            }
        )

    def fetch_messages(self, recipient: str, message_type: str | None = None) -> List[dict]:
        messages = self.message_bus.get(recipient, [])
        if message_type is None:
            selected = list(messages)
        else:
            selected = [m for m in messages if m["type"] == message_type]
        self.message_bus[recipient] = []
        return selected

    def _phase_activate(self, phase_name: str) -> None:
        phase_order = list(self.sma_agents)
        self.random.shuffle(phase_order)
        for agent in phase_order:
            getattr(agent, phase_name)()

    def _simulate_user_interactions(self) -> List[dict]:
        interactions: List[dict] = []

        for user_id, ranking in self.final_rankings.items():
            user = self.users[user_id]
            for rank, product_id in enumerate(ranking[:5], start=1):
                product = self.products[product_id]

                # User response is stochastic and local to what the user sees in ranking.
                relevance = self.user_profiles[user_id].get(product.category, 0.01)
                promo = self.promotions.get(product_id, 0.0)
                exposure_bias = 1.0 / rank
                click_prob = min(0.95, 0.55 * relevance + 0.25 * promo + 0.2 * exposure_bias)

                if self.random.random() < click_prob:
                    interactions.append(
                        {
                            "tick": self.tick,
                            "user_id": user_id,
                            "product_id": product_id,
                            "event_type": "click",
                        }
                    )

                    purchase_prob = max(
                        0.02,
                        0.25 * relevance + 0.2 * promo - user.price_sensitivity * (product.price / 200),
                    )
                    if product.stock > 0 and self.random.random() < purchase_prob:
                        interactions.append(
                            {
                                "tick": self.tick,
                                "user_id": user_id,
                                "product_id": product_id,
                                "event_type": "purchase",
                            }
                        )
                        product.stock -= 1

        return interactions

    def step(self) -> None:
        """
        True SMA tick:
        1) all agents perceive
        2) all agents decide
        3) all agents act
        Activation order is randomized on each phase.
        """

        self._phase_activate("perceive")
        self._phase_activate("decide")
        self._phase_activate("act")

        self.interactions_last_tick = self._simulate_user_interactions()
        self.tick += 1

    def get_tick_log(self) -> str:
        return (
            f"tick={self.tick:02d} "
            f"ctr={self.last_metrics['ctr']:.3f} "
            f"conv={self.last_metrics['conversion']:.3f} "
            f"sat={self.last_metrics['avg_satisfaction']:.3f} "
            f"div={self.last_metrics['diversity']:.3f} "
            f"events={len(self.interactions_last_tick)}"
        )
