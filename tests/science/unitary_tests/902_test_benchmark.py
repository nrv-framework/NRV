import numpy as np
import nrv


# define functions to benchmark
def matmul_numpy(a, b):
    """Multiply two matrices with NumPy."""
    return np.matmul(a, b)

def matmul_naive(a, b):
    """Multiply two matrices with a naive approach
    even if a and b are stored in numpy array (2D), there is a double loop
    to feed the result matrix
    """
    if a.shape[1] != b.shape[0]:
        raise ValueError("Matrices cannot be multiplied")

    n_rows = a.shape[0]
    n_cols = b.shape[1]
    n_inner = a.shape[1]

    result = np.zeros((n_rows, n_cols), dtype=a.dtype)

    for i in range(n_rows):
        for j in range(n_cols):
            value = 0
            for k in range(n_inner):
                value = value + a[i, k] * b[k, j]
            result[i, j] = value

    return result

# define input builders
def numpy_case_builder(case):
    """Build deterministic NumPy input matrices from a benchmark case."""
    rng = np.random.default_rng(case.get("seed", 0))
    m, k, n = case["shape"]
    a = rng.random((m, k), dtype=np.float32)
    b = rng.random((k, n), dtype=np.float32)
    return a, b

def naive_case_builder(case):
    """Build MLX matrices from the NumPy-generated benchmark inputs."""
    a, b = numpy_case_builder(case)
    return a, b

# define benchmark cases
cases = [
    {"shape": (16, 16, 16), "seed": 0},
    {"shape": (32, 32, 32), "seed": 1},
    {"shape": (64, 64, 64), "seed": 2},
]

# declare snippets
snippet_np = nrv.Snippet(
    matmul_numpy,
    name="numpy.matmul",
    input_builder=numpy_case_builder,
)
snippet_naive = nrv.Snippet(
    matmul_naive,
    name="naive.matmul",
    input_builder=naive_case_builder,
)

# declare benchmark
test_benchmark = nrv.Benchmark(
    label="Matrix multiplication",
    cases=cases,
    repeat=5,
    number=5,
    warmup=1,
)
# add code snippets to it
test_benchmark.add_snippet(snippet_np, snippet_naive)
test_benchmark.run()
test_benchmark.get_stats()
test_benchmark.display_stats(fname='./unitary_tests/figures/902_A.png',show=False)