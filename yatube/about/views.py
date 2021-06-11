from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Привет.\nМеня зовут Павел и \
            вы зашли на мой учебный проект'
        context['text'] = 'Я автор этого франкенштейна.\nОн еще на начальной стадии сборки, \
            поэтому переодичеси заходите сюда, что бы увидеть прогресс.'
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Технологии использованные в проекте:'
        context['text'] = 'Python 3.7.10\nDjango 2.2.9\nBootstrap'
        return context
