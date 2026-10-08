---
description: "Find, read, and resolve held documents."
icon: clipboard-check
---

# Review desk

The REVIEW sequence: list, find, read the source, decide. Narrative: [API](../pipeline-reference-llm-mailroom/api.md).

{% openapi src="https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml" path="/v1/lookup" method="get" %}
https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml
{% endopenapi %}

{% openapi src="https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml" path="/v1/review/queue" method="get" %}
https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml
{% endopenapi %}

{% openapi src="https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml" path="/v1/review/{doc_id}/resolve" method="post" %}
https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml
{% endopenapi %}

{% openapi src="https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml" path="/v1/documents/{doc_id}/source" method="get" %}
https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml
{% endopenapi %}
