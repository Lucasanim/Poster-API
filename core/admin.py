from django.contrib import admin

from core import models

admin.site.register(models.User)
admin.site.register(models.Followers)
admin.site.register(models.Follows)
admin.site.register(models.Post)
admin.site.register(models.Thread)
admin.site.register(models.Message)
