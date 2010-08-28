"""module with all helper functions of django-help app"""

def unslugify(slug):
    return slug.replace('-', ' ').capitalize()

def get_help_slug_from_url(url, app_label=""):
    return 