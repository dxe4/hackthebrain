from django.db import models


class WaveData(models.Model):
    alpha = models.FloatField()
    beta = models.FloatField()
    beta_theta_ratio = models.FloatField()  # b / t
    beta_alpha_theta_ratio = models.FloatField()  #  b / a + th
