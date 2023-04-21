# Jinja2
Jinja2 is modeled after Django's templates that allows for the use of Python parameters, for-loops, etc in HTML using `{{ double_brackets }}`

### Filters
https://jinja.palletsprojects.com/en/3.1.x/templates/#list-of-builtin-filters

- Uppercase:    {{ variable|upper }}
- Lowercase:    {{ variable|lower }}
- Capitalize:   {{ variable|capitalize }}
- Title:        {{ variable|title }}
- Trim:         {{ variable|trim }}         # remove trailing spaces
- Strip Tags:   {{ variable|striptags }}    # strips html tags
- Safe:         {{ variable| safe }}        # allows html to be passed as variable

### If-Then and For Loops
- {% if %}
- {% endif %}

- {% for x in array %}
-     {{ x }}
- {% endfor %}
