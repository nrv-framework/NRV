from __future__ import annotations

import numpy as np


def test_population_can_be_created_from_explicit_data(nrv_module) -> None:
    population = nrv_module.axon_population()
    population.set_geometry(center=(0.0, 0.0), radius=40.0)

    axon_types = np.array([0, 1, 0], dtype=int)
    diameters = np.array([1.2, 8.0, 2.4])
    y_positions = np.array([0.0, 8.0, -10.0])
    z_positions = np.array([0.0, -6.0, 5.0])

    population.create_population_from_data(
        (axon_types, diameters, y_positions, z_positions)
    )

    assert population.n_ax == 3
    assert {"types", "diameters", "y", "z"}.issubset(population.axon_pop.columns)
    assert np.allclose(population.axon_pop["diameters"], diameters)
    assert np.allclose(population.axon_pop["y"], y_positions)
    assert np.allclose(population.axon_pop["z"], z_positions)


def test_population_generate_places_axons_inside_geometry(nrv_module) -> None:
    np.random.seed(0)
    population = nrv_module.axon_population()

    population.generate(
        center=(0.0, 0.0),
        radius=25.0,
        n_ax=6,
        percent_unmyel=0.5,
        delta=1.0,
        n_iter=50,
    )

    placed = population.axon_pop[population.axon_pop["is_placed"]]

    assert population.n_ax == 6
    assert {"y", "z", "is_placed"}.issubset(population.axon_pop.columns)
    assert len(placed) > 0
    assert np.all(np.hypot(placed["y"], placed["z"]) <= 25.0)
