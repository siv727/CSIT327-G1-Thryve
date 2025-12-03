from django import template
from thryve_app.models import Listing

register = template.Library()

@register.simple_tag
def get_category_display(category_value):
    """Get the display name for a category"""
    choices_dict = dict(Listing.CATEGORY_CHOICES)
    return choices_dict.get(category_value, category_value)

@register.simple_tag
def get_subcategory_display(category, subcategory_value):
    """Get the display name for a subcategory"""
    subcategories = Listing.SUBCATEGORY_CHOICES.get(category, [])
    for sub in subcategories:
        if sub[0] == subcategory_value:
            return sub[1]
    return subcategory_value