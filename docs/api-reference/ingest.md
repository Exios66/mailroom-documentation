---
description: "Submit documents and read the queue."
icon: inbox
---

# Ingest

Submit documents to the inbox and read the live queue. The watcher claims uploads and mints the `doc_id`. Narrative: [API](../pipeline-reference-llm-mailroom/api.md).

{% openapi src="https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml" path="/v1/upload" method="post" %}
https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml
{% endopenapi %}

{% openapi src="https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml" path="/v1/queue" method="get" %}
https://raw.githubusercontent.com/Exios66/mailroom-documentation/main/docs/api-reference/mailroom-openapi.yaml
{% endopenapi %}
