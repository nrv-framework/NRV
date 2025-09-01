import numpy as np
from nrv.eit.utils._misc import split_job_from_arrays

def test_split_job_from_arrays_default_even_split():
    len_arrays = 10
    n_split = 2
    result = split_job_from_arrays(len_arrays, n_split)

    # Should split into two groups of 5
    assert len(result) == n_split
    assert all(isinstance(r, list) for r in result)
    assert sorted(sum(result, [])) == list(range(len_arrays))
    assert all(len(r) == 5 for r in result)

def test_split_job_from_arrays_default_uneven_split():
    len_arrays = 11
    n_split = 3
    result = split_job_from_arrays(len_arrays, n_split)
    # Should split into three groups, two of 4 and one of 3
    assert len(result) == n_split
    assert sorted(sum(result, [])) == list(range(len_arrays))
    lengths = [len(r) for r in result]
    assert sorted(lengths) == [3, 4, 4]

def test_split_job_from_arrays_comb():
    len_arrays = 6
    n_split = 3
    result = split_job_from_arrays(len_arrays, n_split, stype="comb")
    # Each group should contain indices where i % n_split == group index
    expected = [
        [0, 3],
        [1, 4],
        [2, 5]
    ]
    assert result == expected

def test_split_job_from_arrays_comb_large():
    len_arrays = 10
    n_split = 4
    result = split_job_from_arrays(len_arrays, n_split, stype="comb")
    # Each group should contain indices where i % n_split == group index
    expected = [
        [0, 4, 8],
        [1, 5, 9],
        [2, 6],
        [3, 7]
    ]
    assert result == expected

def test_split_job_from_arrays_single_split():
    len_arrays = 5
    n_split = 1
    result = split_job_from_arrays(len_arrays, n_split)
    assert len(result) == 1
    assert result[0] == list(range(len_arrays))

def test_split_job_from_arrays_empty():
    len_arrays = 0
    n_split = 3
    result = split_job_from_arrays(len_arrays, n_split)
    assert len(result) == n_split
    assert all(r == [] for r in result)


if __name__== "__main__":
    test_split_job_from_arrays_default_even_split()
    test_split_job_from_arrays_default_uneven_split()
    test_split_job_from_arrays_comb()
    test_split_job_from_arrays_comb_large()
    test_split_job_from_arrays_single_split()
    test_split_job_from_arrays_empty()