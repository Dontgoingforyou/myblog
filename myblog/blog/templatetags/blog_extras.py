from django import template

register = template.Library()


@register.filter
def russian_pluralize(number, forms):
    """Возвращает одну из трёх форм слова по русским правилам склонения."""
    one, few, many = (form.strip() for form in forms.split(','))
    number = abs(int(number))
    last_two = number % 100
    last_one = number % 10

    if last_one == 1 and last_two != 11:
        return one
    if 2 <= last_one <= 4 and last_two not in {12, 13, 14}:
        return few
    return many
