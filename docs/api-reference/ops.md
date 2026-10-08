---
description: "System metrics and maintenance actions."
icon: gauge-high
---

# Operations

Error rates, stuck documents, sweeps, and resume. Narrative: [API](../pipeline-reference-llm-mailroom/api.md).

{% openapi src="https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml" path="/v1/ops/status" method="get" %}
https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml
{% endopenapi %}

{% openapi src="https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml" path="/v1/ops/sweep" method="post" %}
https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml
{% endopenapi %}

{% openapi src="https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml" path="/v1/ops/resume" method="post" %}
https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml
{% endopenapi %}
