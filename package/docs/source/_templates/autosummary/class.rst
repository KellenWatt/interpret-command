..
  class.rst

{{ fullname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
    :members:
    :show-inheritance:
    :inherited-members:

    {% block methods %}
        {% if methods %}
            .. rubric:: {{ _('Methods') }}

            .. autosummary::
                :nosignatures:
                {% for item in methods %}
                {%- if item not in inherited_members %}
                    ~{{ name }}.{{ item }}
                {%- endif %}
                {%- endfor %}
        {% endif %}
    {% endblock %}