from django.db import models

#Модель для таблицы БД с нуными полями
class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя',
    )
    username = models.TextField(
        verbose_name='Логин пользователя',
    )
    name = models.TextField(
        verbose_name='Имя пользователя',
    )
    phoneNumber = models.TextField(
        verbose_name='Номер телефона пользователя',
    )
    answers = models.TextField(
        verbose_name='Ответы пользователя',
    )

    def __str__(self):
        return f'#{self.external_id} {self.username} {self.name} {self.phoneNumber} {self.answers}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

