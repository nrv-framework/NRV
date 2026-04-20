from __future__ import annotations

import pytest


@pytest.mark.fenics
@pytest.mark.slow
def test_eit_2d_pipeline_runs_and_produces_results(
    nrv_module, fenics_available, legacy_sources_dir, tmp_path
) -> None:
    eit = pytest.importorskip("nrv.eit", reason="EIT submodule must be available")

    nerve_path = legacy_sources_dir / "400_1uax_nerve.json"
    problem = eit.EIT2DProblem(
        str(nerve_path),
        res_dname=str(tmp_path),
        label="pytest_eit",
        x_rec=3000,
        dt_fem=0.5,
        n_proc_global=1,
        l_elec=200,
        l_fem=500,
        i_drive=30,
    )

    nerve_results = problem.simulate_nerve(t_start=0, sim_param={"t_sim": 1.0})
    problem._setup_problem()
    problem.build_mesh()
    fem_results = problem.simulate_eit()

    assert nerve_results is not None
    assert fem_results.has_fem_res
    assert fem_results.n_t > 0
    assert fem_results.n_e > 0
