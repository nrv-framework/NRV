{{ objname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}


{% block attributes %}
{% if attributes %}
Attributes
----------
.. autosummary::
    :toctree: {{ name }}
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
    :toctree: {{ name }}
    
{% for item in methods %}
    {{ name }}.{{ item }}
{% endfor %}
{% endif %}
{% endblock %}
