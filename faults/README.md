# Benchmark of Multi-language S/W Faults

## Applying Faults

```shell
git apply faults/[fault_id].diff
```

## Faults Info
| Bug ID | Faulty File & Method              | Type       |
|--------|-----------------------------------|------------|
| p1     | misaka/api.py                     | [real](https://github.com/FSX/misaka/issues/66)       |
|        | SaferHtmlRenderer$link            |            |
| p2     | misaka/api.py                     | artificial |
|        | smartypants                       |            |
| p3     | misaka/callbacks.py               | artificial |
|        | _misaka_listitem                  |            |
| p4     | misaka/callbacks.py               | artificial |
|        | _misaka_image                     |            |
| p5     | misaka/api.py                     | artificial |
|        | SaferHtmlRenderer$autolink        |            |
| p6     | misaka/api.py                     | artificial |
|        | SaferHtmlRenderer$rewrite_url     |            |
| p7     | misaka/api.py                     | artificial |
|        | SaferHtmlRenderer$link            |            |
| p8     | misaka/api.py                     | artificial |
|        | Markdown$\_\_call\_\_                 |            |
| p9     | misaka/callbacks.py               | artificial |
|        | _misaka_autolink                  |            |
| p10    | misaka/callbacks.py               | artificial |
|        | _misaka_autolink                  |            |
| c1     | misaka/hoedown/html_blocks.c      | artificial |
|        | hoedown_find_block_tag            |            |
| c2     | misaka/hoedown/escape.c           | artificial |
|        | hoedown_escape_html               |            |
| c3     | misaka/hoedown/escape.c           | artificial |
|        | hoedown_escape_html               |            |
| c4     | misaka/hoedown/document.c         | artificial |
|        | replace_spacing                   |            |
| c5     | misaka/hoedown/html.c             | artificial |
|        | rndr_paragraph                    |            |
| c6     | misaka/hoedown/html_smartypants.c | artificial |
|        | hoedown_html_smartypants          |            |
| c7     | misaka/hoedown/document.c         | artificial |
|        | char_emphasis                     |            |
| c8     | misaka/hoedown/document.c         | artificial |
|        | is_hrule                          |            |
| c9     | misaka/hoedown/escape.c           | artificial |
|        | hoedown_escape_href               |            |
| c10    | misaka/hoedown/html_smartypants.c | artificial |
|        | smartypants_squote                |            |
