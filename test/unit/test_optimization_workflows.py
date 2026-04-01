from __future__ import annotations

import numpy as np


def test_problem_and_scipy_optimizer_minimize_sphere(nrv_module) -> None:
    problem = nrv_module.Problem()
    problem.costfunction = nrv_module.sphere()
    problem.optimizer = nrv_module.scipy_optimizer(
        method="Powell",
        x0=np.array([2.0, -1.5]),
        maxiter=20,
    )

    results = problem()

    assert results["status"] != "Error"
    assert results["best_cost"] < 1e-4
    assert np.linalg.norm(results["best_position"]) < 1e-2


def test_biphasic_stimulus_cost_function_can_be_configured(
    nrv_module, legacy_sources_dir
) -> None:
    static_context = str(legacy_sources_dir / "200_myelinated_axon.json")
    context_modifier = nrv_module.biphasic_stimulus_CM(
        start=1.0,
        s_cathod="0",
        t_cathod="1",
        s_anod=0,
    )
    cost_evaluation = nrv_module.recrutement_count_CE(reverse=True) + 0.01 * nrv_module.stim_energy_CE()

    cost_function = nrv_module.cost_function(
        static_context=static_context,
        context_modifier=context_modifier,
        cost_evaluation=cost_evaluation,
        t_sim=2.0,
    )

    assert cost_function.static_context is not None
    assert cost_function.context_modifier is context_modifier
    assert cost_function.cost_evaluation is cost_evaluation
