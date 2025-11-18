from django.db.models import CASCADE, CharField, ForeignKey, TextField
from django.utils.translation import gettext_lazy as _

from apps.models.base import CreatedBaseModel


class Favorite(CreatedBaseModel):
    user = ForeignKey('apps.UserProfile', CASCADE, related_name='favorites', verbose_name="Users")
    exercise = ForeignKey('apps.Exercise', CASCADE, related_name='favorites')
    notes = TextField(_("Notes"), blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'exercise')
        verbose_name = _("Sevimli")
        verbose_name_plural = _("Sevimlilar")

    def __str__(self):
        return f"{self.user.name}"


class FavoriteCollection(CreatedBaseModel):
    user = ForeignKey('apps.UserProfile', CASCADE, related_name='favorite_collections', verbose_name="Users")
    name = CharField(_("Name"), max_length=100)
    icon = CharField(_("Icon"), max_length=10, default="⭐")
    description = TextField(_("Description"), blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'name')
        verbose_name = _("Favorite Collection")
        verbose_name_plural = _("Favorite Collections")

    def __str__(self):
        return f"{self.user.name} - {self.name}"

    @property
    def items_count(self):
        return Favorite.objects.filter(user=self.user).count()
