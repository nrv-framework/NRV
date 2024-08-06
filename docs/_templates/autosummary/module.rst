{{ fullname | escape | underline }}

Description
-----------
.. automodule:: {{ fullname }}
.. currentmodule:: {{ fullname }}


{% if modules %}
Subpackages
-----------
.. autosummary::
    :toctree: {{ fullname }}/_subpackages
    {% for module in modules %}
    {{ module }}
    {% endfor %}
{% endif %}



{% if classes %}
Classes
-------
.. autosummary::
    :toctree: {{ fullname }}/_classes
    {% for class in classes %}
    {{ class }}
    {% endfor %}
{% endif %}

{% if functions %}
Functions
---------

.. autosummary:: 
    :toctree: {{ fullname }}/_functions
    {% for function in functions %}
    {{ function }}
    {% endfor %}
{% endif %}
