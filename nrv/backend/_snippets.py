import inspect


class Snippet:
    """
    Wrap a callable and describe how to generate valid benchmark inputs.

    A ``Snippet`` is the smallest executable unit of the benchmarking system.
    It stores a callable, introspects its signature, converts a benchmark case
    into positional and keyword arguments, then optionally post-processes the
    output.

    Parameters
    ----------
    fun : callable, optional
        Function or callable object to benchmark.
    name : str, optional
        Explicit snippet name. If omitted, the callable name is used.
    input_builder : callable, optional
        Callable receiving one benchmark case and returning either positional
        arguments, keyword arguments, or an ``(args, kwargs)`` pair.
    result_handler : callable, optional
        Callable applied to the function result after execution. This is
        especially useful for libraries using asynchronous execution.

    Attributes
    ----------
    fun : callable or None
        Wrapped callable.
    name : str or None
        Human-readable snippet name.
    parameters : list of inspect.Parameter
        Signature parameters extracted from the callable.
    input_builder : callable or None
        Helper used to transform benchmark cases into call arguments.
    result_handler : callable or None
        Optional result post-processing hook.

    Notes
    -----
    The class is intentionally generic: it does not assume anything about the
    snippet content. This keeps it reusable across NRV specific benchmarks or
    pureliy computational benchmarks to adapt the code to the machine.
    """

    def __init__(self, fun=None, name=None, input_builder=None, result_handler=None):
        self.fun = None
        self.name = name
        self.parameters = []
        self.input_builder = input_builder
        self.result_handler = result_handler

        if fun is not None:
            self.set_function(fun)

    def set_function(self, fun):
        """
        Register the callable and cache its signature metadata.

        Parameters
        ----------
        fun : callable
            Function or callable object to benchmark.

        Raises
        ------
        TypeError
            If ``fun`` is not callable.
        """
        if not callable(fun):
            raise TypeError("Snippet expects a callable object.")

        self.fun = fun
        if self.name is None:
            self.name = getattr(fun, "__name__", fun.__class__.__name__)
        self._find_arguments()

    def _find_arguments(self):
        """
        Extract the callable signature as ``inspect.Parameter`` objects.

        Notes
        -----
        The method stores the raw ``inspect`` parameter objects. See
        ``inspect`` library documentation for
        """
        if self.fun is None:
            self.parameters = []
        else:
            signature = inspect.signature(self.fun)
            self.parameters = list(signature.parameters.values())

    def expected_arguments(self):
        """
        Return a compact description of the callable signature.

        Returns
        -------
        list of dict
            One dictionary per parameter containing the parameter name, kind,
            annotation, and default information.

        Notes
        -----
        This representation is deliberately serializable and display-friendly.
        It is easier to print or export than raw ``inspect.Parameter`` objects.
        """
        return [
            {
                "name": parameter.name,
                "kind": parameter.kind.name,
                "annotation": (
                    None
                    if parameter.annotation is inspect._empty
                    else parameter.annotation
                ),
                "has_default": parameter.default is not inspect._empty,
                "default": (
                    None if parameter.default is inspect._empty else parameter.default
                ),
            }
            for parameter in self.parameters
        ]

    def build_call(self, case):
        """
        Convert a benchmark case into ``(*args, **kwargs)``.

        Parameters
        ----------
        case : object
            User-defined benchmark case descriptor.

        Returns
        -------
        tuple
            A two-element tuple ``(args, kwargs)`` ready to be passed to the
            wrapped callable.

        Notes
        -----
        Supported builder return formats are:

        - ``None`` for a no-argument call.
        - ``dict`` for keyword-only invocation.
        - ``list`` or ``tuple`` for positional arguments.
        - ``(args, kwargs)`` for full explicit control.

        """
        # if there is a builder, appy it
        if self.input_builder is not None:
            built = self.input_builder(case)
        else:
            built = case

        # construct case by case the *args, **kwargs
        if built is None:
            return (), {}

        if isinstance(built, tuple) and len(built) == 2 and isinstance(built[1], dict):
            args, kwargs = built
            return tuple(args), dict(kwargs)

        if isinstance(built, dict):
            return (), dict(built)

        if isinstance(built, (list, tuple)):
            return tuple(built), {}

        return (built,), {}

    def run(self, case):
        """
        Execute the snippet on one benchmark case.

        Parameters
        ----------
        case : object
            Benchmark case descriptor passed to ``input_builder``.

        Returns
        -------
        object
            Return value of the wrapped callable.

        Notes
        -----
        The optional ``result_handler`` runs after the function call. This is
        where backend-specific synchronization can be injected without leaking
        these details into the generic benchmark orchestration layer.
        """
        args, kwargs = self.build_call(case)
        result = self.fun(*args, **kwargs)
        if self.result_handler is not None:
            self.result_handler(result)
        return result

    def __call__(self, *args, **kwargs):
        """
        Forward a direct call to the wrapped callable.

        Parameters
        ----------
        *args
            Positional arguments forwarded to ``self.fun``.
        **kwargs
            Keyword arguments forwarded to ``self.fun``.

        Returns
        -------
        object
            Return value of the wrapped callable.
        """
        return self.fun(*args, **kwargs)

    def __repr__(self):
        """
        Return a compact debugging representation.

        Returns
        -------
        str
            Textual representation of the snippet instance.
        """
        return f"Snippet(name={self.name!r}, parameters={len(self.parameters)})"
