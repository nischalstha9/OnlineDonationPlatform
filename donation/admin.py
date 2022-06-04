from django.contrib import admin
from .models import Category, Donation,MetaImage
from rangefilter.filters import DateRangeFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter


# Register your models here.
admin.site.register(Category)
admin.site.register(MetaImage)
class DonationAdmin(admin.ModelAdmin):
    list_filter = [
        ('category', RelatedDropdownFilter),
        ('created_at', DateRangeFilter),
        ('updated_at', DateRangeFilter),
        'active',
        ]
    list_display = ['id','title', 'user','active','created_at','updated_at']
    list_display_links = ['title']
    ordering = ['created_at','updated_at']
    sortable_by = ['created_at','updated_at','title']
    search_fields = ['title','id',]
    search_help_text = "Search helps by title and ID"
    show_full_result_count = True
    save_as= True
admin.site.register(Donation, DonationAdmin)

# admin.site.register(DonationLikes)

