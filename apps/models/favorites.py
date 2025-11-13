from django.db import models
from django.db.models import ForeignKey, Model


class Favorite(Model):
    user = models.ForeignKey('apps.UserProfile',on_delete=models.CASCADE,related_name='favorites',verbose_name="Foydalanuvchi")
    exercise = ForeignKey('apps.Exercise',on_delete=models.CASCADE,related_name='favorites')
    notes = models.TextField(blank=True, verbose_name="Eslatmalar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan sana")

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'exercise')
        verbose_name = "Sevimli"
        verbose_name_plural = "Sevimlilar"

    def __str__(self):
        return f"{self.user.name}"

class FavoriteCollection(models.Model):
    user = models.ForeignKey('apps.UserProfile',
        on_delete=models.CASCADE,
        related_name='favorite_collections',
        verbose_name="Foydalanuvchi"
    )
    name = models.CharField(max_length=100, verbose_name="Nomi")
    icon = models.CharField(max_length=10, default="⭐", verbose_name="Icon")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'name')
        verbose_name = "Sevimlilar to'plami"
        verbose_name_plural = "Sevimlilar to'plamlari"

    def __str__(self):
        return f"{self.user.name} - {self.name}"

    @property
    def items_count(self):
        return Favorite.objects.filter(user=self.user).count()
