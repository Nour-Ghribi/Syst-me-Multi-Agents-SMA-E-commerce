from __future__ import annotations

import time
from typing import Dict, List

import matplotlib.pyplot as plt
import solara

from sma_system.model import EcommerceSMAModel


# Shared reactive state for the dashboard session.
model_state = solara.reactive(EcommerceSMAModel(seed=7))
running_state = solara.reactive(False)
tick_state = solara.reactive(0)
interval_ms_state = solara.reactive(700)
history_state = solara.reactive(
    {
        "ticks": [],
        "ctr": [],
        "satisfaction": [],
        "diversity": [],
        "conversion": [],
    }
)
rankings_state = solara.reactive({})


def _snapshot(model: EcommerceSMAModel) -> None:
    metrics = model.last_metrics

    next_history = {key: list(values) for key, values in history_state.value.items()}
    next_history["ticks"].append(model.tick)
    next_history["ctr"].append(metrics["ctr"])
    next_history["satisfaction"].append(metrics["avg_satisfaction"])
    next_history["diversity"].append(metrics["diversity"])
    next_history["conversion"].append(metrics["conversion"])

    history_state.value = next_history
    rankings_state.value = {uid: list(ranking) for uid, ranking in model.final_rankings.items()}
    tick_state.value = model.tick


def _step_once() -> None:
    model = model_state.value
    model.step()
    _snapshot(model)


def _reset_model() -> None:
    running_state.value = False
    model_state.value = EcommerceSMAModel(seed=7)
    tick_state.value = 0
    history_state.value = {
        "ticks": [],
        "ctr": [],
        "satisfaction": [],
        "diversity": [],
        "conversion": [],
    }
    rankings_state.value = {}


def _make_line_chart(title: str, x: List[int], y: List[float], y_label: str):
    fig, ax = plt.subplots(figsize=(5.5, 2.8))
    ax.plot(x, y, marker="o", linewidth=2)
    ax.set_title(title)
    ax.set_xlabel("Tick")
    ax.set_ylabel(y_label)
    ax.grid(alpha=0.3)
    return fig


@solara.component
def Dashboard() -> None:
    model = model_state.value
    metrics = model.last_metrics

    def _auto_runner(stop_event):
        if not running_state.value:
            return

        while running_state.value and not stop_event.is_set():
            _step_once()
            time.sleep(interval_ms_state.value / 1000.0)

    solara.use_thread(_auto_runner, dependencies=[running_state.value, interval_ms_state.value])

    with solara.Column(gap="16px"):
        solara.Markdown("## Dashboard SMA E-commerce")
        solara.Markdown(
            "Simulation multi-agents en temps reel (Perception -> Decision -> Action)."
        )

        with solara.Card("Controles de simulation"):
            with solara.Row(gap="12px"):
                solara.Button("Next Step", on_click=_step_once, color="primary")
                solara.Button(
                    "Run" if not running_state.value else "Pause",
                    on_click=lambda: setattr(running_state, "value", not running_state.value),
                    color="success" if not running_state.value else "warning",
                )
                solara.Button("Reset", on_click=_reset_model, color="error", outlined=True)
            solara.SliderInt(
                "Intervalle auto-run (ms)",
                value=interval_ms_state,
                min=200,
                max=2000,
                step=100,
            )
            solara.Markdown(f"Tick actuel: **{tick_state.value}**")

        with solara.Card("Metriques en temps reel"):
            with solara.Columns([1, 1, 1, 1]):
                solara.Markdown(f"**CTR**: {metrics['ctr']:.3f}")
                solara.Markdown(f"**Conversion**: {metrics['conversion']:.3f}")
                solara.Markdown(f"**Satisfaction**: {metrics['avg_satisfaction']:.3f}")
                solara.Markdown(f"**Diversite**: {metrics['diversity']:.3f}")

        x_ticks = history_state.value["ticks"]
        with solara.Card("Graphiques dynamiques"):
            with solara.Columns([1, 1, 1]):
                ctr_fig = _make_line_chart(
                    "Evolution CTR",
                    x_ticks,
                    history_state.value["ctr"],
                    "CTR",
                )
                solara.FigureMatplotlib(ctr_fig)

                sat_fig = _make_line_chart(
                    "Evolution Satisfaction",
                    x_ticks,
                    history_state.value["satisfaction"],
                    "Satisfaction",
                )
                solara.FigureMatplotlib(sat_fig)

                div_fig = _make_line_chart(
                    "Evolution Diversite",
                    x_ticks,
                    history_state.value["diversity"],
                    "Diversite",
                )
                solara.FigureMatplotlib(div_fig)

        with solara.Card("Recommandations par utilisateur"):
            if not rankings_state.value:
                solara.Markdown("Aucune recommandation pour le moment. Lancez au moins un tick.")
            else:
                for user_id, ranking in rankings_state.value.items():
                    top_items = ", ".join(ranking[:5])
                    solara.Markdown(f"- **{user_id}**: {top_items}")

@solara.component
def Page() -> None:
    Dashboard()


page = Page
