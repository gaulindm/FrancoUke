from cube.models import CubeState
from ..base import StepView, CubeStateLoader


class WhiteCrossView(StepView):

    template_name = "francontcube/methods/cubienewbie/white-cross.html"
    method_name = "CubieNewbie"
    step_name = "Croix Blanche"
    step_number = 1
    step_icon = "plus-circle"

    next_step = "francontcube:beginner_bottom_corners"
    prev_step = None

    cube_state_slugs = {
        'goal_state': 'white-cross-goal',
        'before_state': 'white-cross-before',
        'after_state': 'white-cross-after',
    }

def get_context_data(self):
    context = super().get_context_data()

    # Load progress states (0-4 edges placed)
    progress_slugs = {f'progress_{i}': f'white-cross-progress-{i}' for i in range(5)}
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


white_cross = WhiteCrossView.as_view()
