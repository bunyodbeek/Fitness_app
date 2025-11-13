from django.db import models
from django.conf import settings  # 🔹 bu importni qo‘sh
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 🔹 shu joy o‘zgardi
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="Foydalanuvchi"
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Tur"
    )
    object_id = models.PositiveIntegerField(verbose_name="Obyekt ID")
    content_object = GenericForeignKey('content_type', 'object_id')

    collection = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="To'plam"
    )

    notes = models.TextField(blank=True, verbose_name="Eslatmalar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan sana")

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = "Sevimli"
        verbose_name_plural = "Sevimlilar"
        indexes = [
            models.Index(fields=['user', 'content_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.content_object}"

    @property
    def content_type_name(self):
        return self.content_type.model


class FavoriteCollection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 🔹 bu joy ham o‘zgardi
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
        return f"{self.user.username} - {self.name}"

    @property
    def items_count(self):
        return Favorite.objects.filter(
            user=self.user,
            collection=self.name
        ).count()
