import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

class QuestonModelTest(TestCase):

    def test_was_published_recently_with_future_question(self):
        """ was_published_recently() retorna False para las
            preguntas cuya fecha de publicación es en el 
            futuro """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """ was_published_recently() retorna True para las 
            preguntas cuya fecha de publicación esta dentro 
            del ultimo dia """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_was_published_recently_with_old_question(self):
        """ was_published_recently() retorna False para las
            preguntas cuya fecha de publicación is mas
            antigua que 1 dia """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

def create_question(question_text, days):
    """ Crea una pregunta con la question_text dada y 
        publicada con el numero dado en days compensado
        ahora (negativo para preguntas publicadas en el
        pasado, positivo para preguntas que aun no se
        han publicado)"""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """ si no existen preguntas, un mensaje apropiado
        es mostrado """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
        
    def test_past_question(self):
        """ Preguntas con una fecha de publicacion en el
            pasado son mostradas en la pagina index. """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_future_question(self):
        """ Preguntas con una fecha de publicacion en el 
            futuro no son mostradas en la pagina index. """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """ incluso si ambas preguntas existieran, solo 
            preguntas del pasado son mostradas. """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_two_past_questions(self):
        """ La pagina index puede mostrar multiples preguntas. """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question 2.>', '<Question: Past question 1.>'])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """ La vista de detalles de una pregunta con una fecha
            de publicacion en el futuro retorna un 404 no encontrado. """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        La vista de detalles de una pregunta con una fecha de
        publicacion en el pasado muestra el texto de la pregunta.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)