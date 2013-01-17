---
layout: default
title: Home
---

Recent News
-----------

{% for entry in site.posts %}
[{{entry.title}}]({{entry.url}})
{% endfor %}
