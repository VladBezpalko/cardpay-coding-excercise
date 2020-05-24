"""
URL Configuration for cardpay project.

The `urlpatterns` list routes URLs to views.
"""
from django.urls import path

from payments.views import TokenizeView, SaleView

urlpatterns = [
    path('tokenise', TokenizeView.as_view()),
    path('sale', SaleView.as_view()),
]
