{% macro pii_check(model) %}
  select *
  from {{ model }}
  where 1=0 -- placeholder: example macro for policy checks
{% endmacro %}


