from django.contrib import admin
from .models import *


# Text to put at the end of each page's <title>.
admin.site.site_title = "Sharing is Caring | Admin"

# Text to put in each page's <h1> (and above login form).
admin.site.site_header = "Sharing is Caring Administration"

# Text to put at the top of the admin index page.
admin.site.index_title = "Home"


admin.site.register(CustomUser)
admin.site.register(Customer)
admin.site.register(UserToken)