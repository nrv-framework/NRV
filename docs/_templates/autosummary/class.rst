{{ objname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

{% block attributes %}
{% if attributes %}
Attributes
----------
.. autosummary::
    :toctree: {{ fullname }}/_attributes
{% for item in attributes %}
    {{ name }}.{{ item }}
{% endfor %}
{% endif %}
{% endblock %}

{% block methods %}
{% if methods %}
Methods
-------
.. autosummary::
    :toctree: {{ fullname }}/_methods
    
{% for item in methods %}
    {{ name }}.{{ item }}
{% endfor %}
{% endif %}
{% endblock %}
