from cube.models import CubeState
from ..base import StepView, CubeStateLoader


class BottomCrossView(StepView):

    template_name = "francontcube/methods/cubienewbie/bottom-cross.html"
    method_name = "CubieNewbie"
    step_name = "Croix du bas(Jaune)"
    step_number = 1
    step_icon = "plus-circle"

    next_step = "francontcube:beginner_bottom_corners"
    prev_step = None

    cube_state_slugs = {
        'goal_state': 'bottom-cross-goal',
        'before_state': 'bottom-cross-before',
        'after_state': 'bottom-cross-after',
    }

def get_context_data(self):
    context = super().get_context_data()

    # Load progress states (0-4 edges placed)
    progress_slugs = {f'progress_{i}': f'bottom-cross-progress-{i}' for i in range(5)}
    progress_states, progress_missing = CubeStateLoader.get_multiple(progress_slugs)

    context['progress_states'] = [progress_states[f'progress_{i}'] for i in range(5)]
    context['missing_slugs'].extend(progress_missing)

    # ── Roofpig config (NEW) ───────────────────────────────
    goal_state_obj = context.get("goal_state")
    if goal_state_obj and isinstance(goal_state_obj, CubeState):
        context["roofpig_config"] = goal_state_obj.get_roofpig_config()
    else:
        context["roofpig_config"] = None

    return context


bottom_cross = BottomCrossView.as_view()
