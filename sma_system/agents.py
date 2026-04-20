from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from mesa import Agent


@dataclass
class Product:
    product_id: str
    category: str
    price: float
    stock: int
    margin: float
    promo_boost: float = 0.0


@dataclass
class UserState:
    user_id: str
    interests: Dict[str, float]
    price_sensitivity: float


class BaseSMAAgent(Agent):
    """Base class for 3-phase agent behavior: perceive -> decide -> act."""

    def __init__(self, model, name: str):
        super().__init__(model)
        self.name = name
        self.local_view = {}
        self.intent = {}

    def perceive(self) -> None:
        raise NotImplementedError

    def decide(self) -> None:
        raise NotImplementedError

    def act(self) -> None:
        raise NotImplementedError


class AgentProfiling(BaseSMAAgent):
    def __init__(self, model):
        super().__init__(model, "profiling")

    def perceive(self) -> None:
        self.local_view = {
            "interactions": list(self.model.interactions_last_tick),
            "learning_signals": self.model.fetch_messages("profiling", "learning_signal"),
        }

    def decide(self) -> None:
        profile_updates: Dict[str, Dict[str, float]] = {}

        for event in self.local_view["interactions"]:
            user_id = event["user_id"]
            product = self.model.products[event["product_id"]]
            profile_updates.setdefault(user_id, {})
            delta = 0.08 if event["event_type"] == "click" else 0.15
            profile_updates[user_id][product.category] = profile_updates[user_id].get(product.category, 0.0) + delta

        for signal in self.local_view["learning_signals"]:
            user_id = signal["payload"]["user_id"]
            success = signal["payload"]["success"]
            profile_updates.setdefault(user_id, {})
            if not success:
                for category in list(profile_updates[user_id].keys()):
                    profile_updates[user_id][category] *= 0.9

        self.intent = {"profile_updates": profile_updates}

    def act(self) -> None:
        for user_id, category_changes in self.intent["profile_updates"].items():
            profile = self.model.user_profiles[user_id]
            for category, delta in category_changes.items():
                profile[category] = max(0.01, profile.get(category, 0.1) + delta)

            total = sum(profile.values())
            if total > 0:
                for category in profile:
                    profile[category] /= total

            self.model.send_message(
                "recommendation",
                "profile_updated",
                {"user_id": user_id, "profile": dict(profile)},
            )


class AgentRecommendation(BaseSMAAgent):
    def __init__(self, model, top_k: int = 5):
        super().__init__(model, "recommendation")
        self.top_k = top_k

    def perceive(self) -> None:
        self.local_view = {
            "profiles": {uid: dict(profile) for uid, profile in self.model.user_profiles.items()},
            "catalog": [p for p in self.model.products.values() if p.stock > 0],
            "signals": self.model.fetch_messages("recommendation", "learning_signal"),
        }

    def decide(self) -> None:
        recommendations: Dict[str, List[Tuple[str, float]]] = {}

        for user_id, profile in self.local_view["profiles"].items():
            user = self.model.users[user_id]
            scored: List[Tuple[str, float]] = []
            for product in self.local_view["catalog"]:
                pref = profile.get(product.category, 0.01)
                price_penalty = user.price_sensitivity * (product.price / 150.0)
                noise = self.model.random.uniform(-0.02, 0.02)
                score = pref + product.promo_boost * 0.2 - price_penalty + noise
                scored.append((product.product_id, score))

            scored.sort(key=lambda x: x[1], reverse=True)
            recommendations[user_id] = scored[: self.top_k]

        for signal in self.local_view["signals"]:
            if signal["payload"]["success"]:
                continue
            user_id = signal["payload"]["user_id"]
            if user_id in recommendations and recommendations[user_id]:
                recommendations[user_id] = recommendations[user_id][1:] + recommendations[user_id][:1]

        self.intent = {"recommendations": recommendations}

    def act(self) -> None:
        self.model.candidate_recommendations = self.intent["recommendations"]
        self.model.send_message(
            "marketing",
            "new_recommendations",
            {"recommendations": self.model.candidate_recommendations},
        )


class AgentMarketing(BaseSMAAgent):
    def __init__(self, model):
        super().__init__(model, "marketing")

    def perceive(self) -> None:
        self.local_view = {
            "recommendations": dict(self.model.candidate_recommendations),
            "promotions": dict(self.model.promotions),
        }

    def decide(self) -> None:
        ranked: Dict[str, List[str]] = {}
        conflicts = []

        for user_id, recs in self.local_view["recommendations"].items():
            rescored = []
            for product_id, rec_score in recs:
                product = self.model.products[product_id]
                business_score = (
                    self.local_view["promotions"].get(product_id, 0.0)
                    + product.margin * 0.15
                    + (1.0 if product.stock > 3 else -0.3)
                )
                final_score = 0.45 * rec_score + 0.55 * business_score
                rescored.append((product_id, final_score, rec_score, business_score))

            rescored.sort(key=lambda x: x[1], reverse=True)
            ranked[user_id] = [p[0] for p in rescored]

            if rescored:
                avg_rec = sum(p[2] for p in rescored) / len(rescored)
                avg_business = sum(p[3] for p in rescored) / len(rescored)
                conflicts.append(abs(avg_business - avg_rec))

        conflict_level = sum(conflicts) / max(1, len(conflicts))
        self.intent = {"marketing_rankings": ranked, "conflict_level": conflict_level}

    def act(self) -> None:
        self.model.marketing_rankings = self.intent["marketing_rankings"]
        self.model.send_message(
            "arbitre",
            "conflict_report",
            {
                "conflict_level": self.intent["conflict_level"],
                "marketing_rankings": self.model.marketing_rankings,
            },
        )


class AgentArbitre(BaseSMAAgent):
    def __init__(self, model):
        super().__init__(model, "arbitre")

    def perceive(self) -> None:
        reports = self.model.fetch_messages("arbitre", "conflict_report")
        conflict_level = reports[-1]["payload"]["conflict_level"] if reports else 0.0

        self.local_view = {
            "conflict_level": conflict_level,
            "recommendations": dict(self.model.candidate_recommendations),
            "marketing_rankings": dict(self.model.marketing_rankings),
            "avg_satisfaction": self.model.last_metrics.get("avg_satisfaction", 0.5),
        }

    def decide(self) -> None:
        final_rankings: Dict[str, List[str]] = {}

        for user_id, recs in self.local_view["recommendations"].items():
            rec_order = [pid for pid, _ in recs]
            market_order = self.local_view["marketing_rankings"].get(user_id, rec_order)

            # If conflict is high and user satisfaction is falling, favor recommendation quality.
            if self.local_view["conflict_level"] > 0.45 and self.local_view["avg_satisfaction"] < 0.55:
                weight_rec = 0.7
            else:
                weight_rec = 0.5

            scores = {}
            for idx, pid in enumerate(rec_order):
                scores[pid] = scores.get(pid, 0.0) + weight_rec * (len(rec_order) - idx)
            for idx, pid in enumerate(market_order):
                scores[pid] = scores.get(pid, 0.0) + (1 - weight_rec) * (len(market_order) - idx)

            merged = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            final_rankings[user_id] = [pid for pid, _ in merged]

        self.intent = {"final_rankings": final_rankings}

    def act(self) -> None:
        self.model.final_rankings = self.intent["final_rankings"]


class AgentFeedback(BaseSMAAgent):
    def __init__(self, model):
        super().__init__(model, "feedback")

    def perceive(self) -> None:
        self.local_view = {
            "interactions": list(self.model.interactions_last_tick),
            "shown_rankings": dict(self.model.final_rankings),
        }

    def decide(self) -> None:
        clicks = [e for e in self.local_view["interactions"] if e["event_type"] == "click"]
        purchases = [e for e in self.local_view["interactions"] if e["event_type"] == "purchase"]
        shown_count = sum(len(v) for v in self.local_view["shown_rankings"].values())

        ctr = len(clicks) / shown_count if shown_count else 0.0
        conversion = len(purchases) / max(1, len(clicks))

        user_satisfaction = {}
        for user_id, ranking in self.local_view["shown_rankings"].items():
            if not ranking:
                user_satisfaction[user_id] = 0.0
                continue
            top_categories = [self.model.products[pid].category for pid in ranking[:3]]
            profile = self.model.user_profiles[user_id]
            satisfaction = sum(profile.get(cat, 0.0) for cat in top_categories) / 3
            user_satisfaction[user_id] = satisfaction

        diversity_scores = []
        for ranking in self.local_view["shown_rankings"].values():
            cats = [self.model.products[pid].category for pid in ranking[:5]]
            diversity_scores.append(len(set(cats)) / max(1, len(cats)))

        avg_satisfaction = sum(user_satisfaction.values()) / max(1, len(user_satisfaction))
        diversity = sum(diversity_scores) / max(1, len(diversity_scores))

        learning_signals = []
        for user_id, satisfaction in user_satisfaction.items():
            learning_signals.append(
                {
                    "user_id": user_id,
                    "success": satisfaction >= 0.45,
                }
            )

        self.intent = {
            "metrics": {
                "ctr": ctr,
                "conversion": conversion,
                "avg_satisfaction": avg_satisfaction,
                "diversity": diversity,
            },
            "learning_signals": learning_signals,
        }

    def act(self) -> None:
        self.model.last_metrics = self.intent["metrics"]
        self.model.metrics_history.append(dict(self.intent["metrics"]))

        for signal in self.intent["learning_signals"]:
            self.model.send_message("profiling", "learning_signal", signal)
            self.model.send_message("recommendation", "learning_signal", signal)
