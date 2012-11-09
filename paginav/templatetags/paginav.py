import re
import ttag
from django import template, http
from django.http import QueryDict

RE_URL = re.compile('(.*)1(.*)')
register = template.Library()


def page_separator(current, count, adjacent, caps):
    if current < adjacent + 1:
        adjacent += adjacent - current + 1
    elif count - current < adjacent:
        adjacent += adjacent - (count - current)
    bits = []
    if current > (1 + adjacent + caps):
        if caps:
            bits.append(range(1, caps + 1))
        start = current - adjacent
    else:
        start = 1
    if current + adjacent < count - caps:
        end = current + adjacent
    else:
        end = count
    bits.append(range(start, end + 1))
    if end != count:
        if caps:
            bits.append(range(count - caps + 1, count + 1))
    return bits


class Paginav(ttag.Tag):
    """
    Generate Digg-like pagination navigation.

    For example, if 200 entries were paginated 10 per page:

    ``{% paginav page %}`` (on page 1)
        On page 1, outputs: ``1 2 3 4 ... 20``

        On page 7, outputs: ``1 ... 4 5 6 7 8 9 10 ... 20``

    ``{% paginav page adjacent=1 %}`` (on page 7)
        On page 1, outputs: ``1 2 ... 20``

        On page 7, outputs: ``1 ... 6 7 8 ... 20``

    ``{% paginav page caps=2 %}`` (on page 7)
        On page 1, outputs: ``1 2 3 4 ... 19 20``

        On page 7, outputs: ``1 2 3 4 5 6 7 8 9 10 ... 19 20``

    If ``url`` is provided and contains a `1` then it will be used as the page
    number when building page URLs rather than the standard behaviour of adding
    ``?page=x`` as a querystring.

    ``first_url`` can be used to specify an alternate url for the first page.
    For example, you may want to have a url pattern which doesn't contain the
    page number for the initial page::

        {% url browse-entries page=1 as page_url %}
        {% url browse-entries as first_page_url %}
        {% paginav page url=page_url first_url=first_page_url caps=3 %}
    """
    page = ttag.Arg()
    template = ttag.Arg(default='paginav.html')
    adjacent = ttag.IntegerArg(keyword=True, default=3)
    caps = ttag.IntegerArg(keyword=True, default=1)
    url = ttag.Arg(keyword=True, required=False)
    first_url = ttag.Arg(keyword=True, required=False)
    page_var = ttag.StringArg(keyword=True, default='page')

    def output(self, data):
        if not data.get('page'):
            return ''
        return template.loader.render_to_string(
            data['template'],
            self.get_context(data)
        )

    def resolve(self, context):
        data = super(Paginav, self).resolve(context)
        request = context.get('request')
        if isinstance(request, http.HttpRequest):
            data['request'] = request
        return data

    def get_context(self, data):
        page = data['page']
        num_pages = page.paginator.num_pages
        c = {'num_pages': num_pages}
        if num_pages < 2:
            return c
        current = page.number
        pages = []
        for page_group in page_separator(current, num_pages,
                adjacent=data['adjacent'], caps=data['caps']):
            group = []
            for number in page_group:
                url = self.build_url(number, data)
                if not url:
                    return {}
                group.append({'url': url, 'number': number,
                              'current': current == number})
            pages.append(group)
        c['pages'] = pages
        if current > 1:
            c['previous_url'] = self.build_url(current - 1, data)
        if current < num_pages:
            c['next_url'] = self.build_url(current + 1, data)
        return c

    def build_url(self, number, data):
        if number == 1 and data.get('first_page_url'):
            return data['first_page_url']
        url = data.get('url')
        match = url and RE_URL.match(url)
        if match:
            start, end = match.groups()
            return '%s%s%s' % (start, number, end)
        # Add the page as a querystring.
        if 'request' in data:
            querydict = data['request'].GET
        else:
            querydict = QueryDict('')
        qs = querydict.copy()
        if number == 1:
            qs.pop(data['page_var'], None)
        else:
            qs[data['page_var']] = number
        qs = qs.urlencode()
        if qs:
            qs = '?%s' % qs
        if not url and not qs:
            return '.'
        return '%s%s' % (url or '', qs)


register.tag(Paginav)
