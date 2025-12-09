from apps.models.base import CreatedBaseModel
from django.db.models import CASCADE, SET_NULL, CharField, ForeignKey, ManyToManyField, TextField
from django.utils.translation import gettext_lazy as _


class FavoriteCollection(CreatedBaseModel):
    user = ForeignKey('apps.UserProfile', CASCADE, related_name='favorite_collections')
    name = CharField(max_length=100, verbose_name="Collection Name")
    description = TextField(blank=True, null=True)
    exercises = ManyToManyField('apps.Exercise', related_name='in_collections', blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Favorite Collection"
        verbose_name_plural = "Favorite Collections"
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.user.name} - {self.name}"

    @property
    def exercise_count(self):
        return int(self.exercises.count())


class Favorite(CreatedBaseModel):
    user = ForeignKey('apps.UserProfile', CASCADE, related_name='favorites')
    exercise = ForeignKey('apps.Exercise', CASCADE, related_name='favorites')
    collection = ForeignKey('apps.FavoriteCollection', SET_NULL, null=True, blank=True, related_name='favorites')
    notes = TextField(_("Notes"), null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'exercise')
        verbose_name = _("Sevimli")
        verbose_name_plural = _("Sevimlilar")

    def __str__(self):
        return f"{self.user.name}"
