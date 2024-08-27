{{ fullname | escape | underline }}

Description
-----------
.. automodule:: {{ fullname }}
.. currentmodule:: {{ fullname }}


{% if modules %}
Subpackages
-----------
.. autosummary::
    :toctree: {{ name }}
    :recursive:
    {% for module in modules %}
    {{ module }}
    {% endfor %}
{% endif %}



{% if classes %}
Classes
-------
.. autosummary::
    :toctree: {{ name }}
    {% for class in classes %}
    {{ class }}
    {% endfor %}
{% endif %}

{% if functions %}
Functions
---------

.. autosummary:: 
    :toctree: {{ name }}
    {% for function in functions %}
    {{ function }}
    {% endfor %}
{% endif %}
