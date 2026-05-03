import csv
from pathlib import Path
import statistics
import timeit

import matplotlib.pyplot as plt


class Benchmark:
    """
    Benchmark multiple snippets on a shared collection of input cases.

    This class centralizes the orchestration of the benchmark:
    registration of snippets, definition of benchmark cases, timed execution,
    aggregation of summary statistics, CSV export, and plotting.

    Parameters
    ----------
    label : str, optional
        Human-readable benchmark name used in console output and figure titles.
    cases : list, optional
        Collection of benchmark cases. Each case is forwarded to the snippet
        through :meth:`snippet.Snippet.run`.
    repeat : int, optional
        Number of independent timing repetitions collected by ``timeit`` for
        each snippet and each case.
    number : int, optional
        Number of executions performed inside one ``timeit`` repetition.
        Reported statistics are normalized to a per-call duration.
    warmup : int, optional
        Number of untimed calls executed before starting the measurements.

    Attributes
    ----------
    label : str
        Human-readable benchmark label.
    snippets : list
        Registered snippet objects.
    cases : list
        Benchmark case definitions.
    repeat : int
        Number of ``timeit`` repetitions.
    number : int
        Number of executions per repetition.
    warmup : int
        Number of warmup executions before timing.
    results : list of dict
        Raw aggregated timing records produced by :meth:`run`.
    """

    def __init__(self, label="", cases=None, repeat=6, number=10, warmup=1):
        self.label = label
        self.snippets = []
        self.cases = list(cases) if cases is not None else []
        self.repeat = repeat
        self.number = number
        self.warmup = warmup
        self.results = []

    def add_snippet(self, *snippets):
        """
        Register one or more snippets in the benchmark.

        Parameters
        ----------
        *snippets : Snippet
            Snippet instances to benchmark on all configured cases.
        """
        for snippet in snippets:
            self.snippets.append(snippet)

    def add_case(self, case):
        """
        Append a new benchmark case.

        Parameters
        ----------
        case : object
            User-defined case descriptor passed later to each snippet.

        Notes
        -----
        A case is intentionally left untyped here. It can be a dictionary,
        a dataclass, or any custom object, as long as the snippet knows how to
        interpret it through its input builder.
        """
        self.cases.append(case)

    def _case_to_text(self, case):
        """
        Convert a benchmark case into a compact display label.

        Parameters
        ----------
        case : object
            Benchmark case descriptor.

        Returns
        -------
        str
            String representation suitable for console output, CSV export, or
            plotting axis labels.
        """
        if isinstance(case, dict) and "shape" in case:
            shape = case["shape"]
            if isinstance(shape, tuple):
                return "x".join(str(dim) for dim in shape)
            return str(shape)
        return str(case)

    def _time_one(self, snippet, case):
        """
        Time one snippet on one case and aggregate summary statistics.

        Parameters
        ----------
        snippet : Snippet
            Snippet to execute.
        case : object
            Benchmark case passed to the snippet.

        Returns
        -------
        dict
            Dictionary containing the case, snippet name, raw timing samples,
            and summary statistics in seconds per call.

        Notes
        -----
        The use of ``timeit.Timer`` isolates the hot execution path and avoids
        common timing pitfalls such as clock handling boilerplate in the main
        benchmark loop. Warmup runs are excluded from the reported timings.
        """
        for _ in range(self.warmup):
            snippet.run(case)

        timer = timeit.Timer(lambda: snippet.run(case))
        samples = timer.repeat(repeat=self.repeat, number=self.number)
        per_call = [sample / self.number for sample in samples]
        return {
            "snippet": snippet.name,
            "case": case,
            "mean": statistics.mean(per_call),
            "min": min(per_call),
            "max": max(per_call),
            "stdev": statistics.stdev(per_call) if len(per_call) > 1 else 0.0,
            "samples": per_call,
        }

    def run(self):
        """
        Execute the benchmark for all snippets and all cases.

        Returns
        -------
        list of dict
            Timing results for every ``(snippet, case)`` pair.

        Raises
        ------
        ValueError
            If no snippets or no cases have been configured.

        Notes
        -----
        Calling this method resets ``self.results`` and recomputes all timing
        records from scratch.
        """
        if not self.snippets:
            raise ValueError("Benchmark has no snippets to execute.")
        if not self.cases:
            raise ValueError("Benchmark has no input cases to execute.")

        self.results = []
        for case in self.cases:
            for snippet in self.snippets:
                self.results.append(self._time_one(snippet, case))
        return self.results

    def get_stats(self, fname=None):
        """
        Print benchmark summary statistics and optionally export them to CSV.

        Parameters
        ----------
        fname : str or pathlib.Path, optional
            Output CSV filename. When provided, one row is written for each
            benchmark result.

        Returns
        -------
        list of dict
            The current benchmark results.
        """
        if not self.results:
            print("No benchmark results available.")
            return []

        header = (
            f"{'snippet':<20} {'shape':<18} {'mean (s)':>12} "
            f"{'min (s)':>12} {'max (s)':>12} {'stdev (s)':>12}"
        )
        print(header)
        print("-" * len(header))
        for result in self.results:
            case_text = self._case_to_text(result["case"])
            print(
                f"{result['snippet']:<20} {case_text:<18} "
                f"{result['mean']:>12.6e} {result['min']:>12.6e} "
                f"{result['max']:>12.6e} {result['stdev']:>12.6e}"
            )

        if fname is not None:
            output_path = Path(fname)
            with output_path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=[
                        "snippet",
                        "case",
                        "mean_s",
                        "min_s",
                        "max_s",
                        "stdev_s",
                        "samples_s",
                    ],
                )
                writer.writeheader()
                for result in self.results:
                    writer.writerow(
                        {
                            "snippet": result["snippet"],
                            "case": self._case_to_text(result["case"]),
                            "mean_s": result["mean"],
                            "min_s": result["min"],
                            "max_s": result["max"],
                            "stdev_s": result["stdev"],
                            "samples_s": ",".join(
                                f"{sample:.12e}" for sample in result["samples"]
                            ),
                        }
                    )

        return self.results

    def display_stats(self, fname=None, show=True):
        """
        Plot mean execution times with error bars using ``matplotlib``.

        Parameters
        ----------
        fname : str or pathlib.Path, optional
            Output image filename. When provided, the figure is saved before
            being optionally displayed.
        show : bool, optional
            If ``True``, display the figure with ``matplotlib.pyplot.show``.

        Returns
        -------
        tuple
            The ``(figure, axis)`` pair created by matplotlib.

        Raises
        ------
        ValueError
            If no benchmark results are available.

        Notes
        -----
        The plot groups results by snippet and uses the case labels on the
        x-axis. Error bars represent one standard deviation across repeated
        ``timeit`` samples, which provides a compact first estimate of timing
        variability without introducing more advanced statistical tooling yet.
        """
        if not self.results:
            raise ValueError("No benchmark results available. Run the benchmark first.")

        snippet_names = []
        for result in self.results:
            if result["snippet"] not in snippet_names:
                snippet_names.append(result["snippet"])

        case_labels = []
        for case in self.cases:
            label = self._case_to_text(case)
            if label not in case_labels:
                case_labels.append(label)

        figure, axis = plt.subplots(figsize=(10, 5))
        for snippet_name in snippet_names:
            snippet_results = [
                result for result in self.results if result["snippet"] == snippet_name
            ]
            means = [result["mean"] for result in snippet_results]
            stdevs = [result["stdev"] for result in snippet_results]
            labels = [self._case_to_text(result["case"]) for result in snippet_results]
            axis.errorbar(
                labels,
                means,
                yerr=stdevs,
                marker="o",
                capsize=4,
                linewidth=1.5,
                label=snippet_name,
            )

        axis.set_title(self.label or "Benchmark results")
        axis.set_xlabel("Case")
        axis.set_ylabel("Mean execution time (s)")
        axis.grid(True, linestyle="--", alpha=0.4)
        axis.legend()
        figure.tight_layout()

        if fname is not None:
            figure.savefig(fname, dpi=200, bbox_inches="tight")

        if show:
            plt.show()

        return figure, axis
