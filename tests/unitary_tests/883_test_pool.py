import os
import multiprocessing as mp
# import dolfinx  # noqa: F401
# Hard-set (not setdefault)
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OMP_DYNAMIC"] = "FALSE"

# Apple Accelerate / vecLib threading cap
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

# Also harmless to set these (covers OpenBLAS/MKL if present)
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# PETSc can take options from env var too
# (forces PETSc OpenMP thread count if PETSc was built with OpenMP)
os.environ["PETSC_OPTIONS"] = os.environ.get("PETSC_OPTIONS", "") + " -omp_num_threads 1"

from mpi4py import MPI
import dolfinx


def _run_iteration(i_n_loop):
    # Apply limits first (initializer already ran), then import heavy libs


    i, n_loop = i_n_loop
    print(f"{i}/{n_loop}")
    for k in range(100_000_000):
        a = 1 + 5/3*k

if __name__ == "__main__":
    n_loop = 100
    n_proc = 2

    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=n_proc) as pool:
        pool.map(_run_iteration, [(i, n_loop) for i in range(n_loop)])
