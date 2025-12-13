from django.db.models import CASCADE, SET_NULL, CharField, ForeignKey, TextField
from django.utils.translation import gettext_lazy as _

from apps.models.base import CreatedBaseModel


class FavoriteCollection(CreatedBaseModel):
    user = ForeignKey('apps.UserProfile', CASCADE, related_name='favorite_collections')
    name = CharField(max_length=100, verbose_name="Collection Name")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Favorite Collection"
        verbose_name_plural = "Favorite Collections"
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.user.name} - {self.name}"

    @property
    def exercise_count(self):
        return self.favorites.count()


class Favorite(CreatedBaseModel):
    user = ForeignKey('apps.UserProfile', CASCADE, related_name='favorites')
    exercise = ForeignKey('apps.Exercise', CASCADE, related_name='favorites')
    collection = ForeignKey('apps.FavoriteCollection', SET_NULL, null=True, blank=True, related_name='favorites')

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'exercise')
        verbose_name = _("Favorite")
        verbose_name_plural = _("Favorites")

    def __str__(self):
        return f"{self.user.name}"
