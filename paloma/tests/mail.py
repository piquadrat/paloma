from paloma import Mail
from django.core import mail
from django.test.utils import override_settings
from .testcase import TestCase


@override_settings(DEFAULT_FROM_EMAIL='default@example.com',
                   DEFAULT_FROM_NAME='Default sender')
class MailTestCase(TestCase):
    """Test case for :class:`Mail`.
    """

    def assertSimple(self, sent, **kwargs):
        self.assertEqual(sent.subject,
                         kwargs.pop('subject', 'Subject of the e-mail'))
        self.assertEqual(sent.body, kwargs.pop('body', 'Body of the e-mail'))
        from_email = kwargs.pop('from_email', 'default@example.com')
        from_name = kwargs.pop('from_name', 'Default sender')
        if from_name:
            self.assertEqual(sent.from_email, '%s <%s>' % (from_name,
                                                           from_email))
        else:
            self.assertEqual(sent.from_email, from_email)
        self.assertEqual(len(sent.to), 1)
        self.assertEqual(sent.to[0], kwargs.pop('to', 'test@example.com'))

        html_alternatives = filter(lambda a: a[1] == 'text/html',
                                   sent.alternatives)
        self.assertEqual(any(html_alternatives), 'html_body' in kwargs)

        if 'html_body' in kwargs:
            html_body = kwargs.pop('html_body')
            actual_html_body, mime_type = html_alternatives[0]
            self.assertEqual(html_body, actual_html_body)

    def test_init__defaults_to_setting_for_from_email_and_from_name(self):
        """Mail().__init__(from_name=None, from_email=None) uses defaults
        """

        class TestMail(Mail):
            subject = 'Subject of the e-mail'

        # Test with global.
        with override_settings(DEFAULT_FROM_EMAIL='someone@example.com',
                               DEFAULT_FROM_NAME='Someone'):
            m = TestMail()
            self.assertEqual(m.from_email, 'someone@example.com')
            self.assertEqual(m.from_name, 'Someone')

            with self.assertMailsSent(1):
                m.send('test@example.com', 'Body of the e-mail')
            self.assertSimple(mail.outbox[-1],
                              from_email='someone@example.com',
                              from_name='Someone')

    def test_send__respects_from_email_ivar_from_sent(self):
        """Mail().send(..) respects from_email instance variable
        """

        class TestMail(Mail):
            subject = 'Subject of the e-mail'
            from_email = 'from@example.com'

        # Test without global.
        with override_settings(DEFAULT_FROM_EMAIL=None):
            with self.assertMailsSent(1):
                TestMail().send('test@example.com', 'Body of the e-mail')
            self.assertSimple(mail.outbox[-1], from_email='from@example.com')

        # Test with global.
        with self.assertMailsSent(1):
            TestMail().send('test@example.com', 'Body of the e-mail')
        self.assertSimple(mail.outbox[-1], from_email='from@example.com')

    def test_send__respects_from_name_ivar_from_sent(self):
        """Mail().send(..) respects from_name instance variable
        """

        class TestMail(Mail):
            subject = 'Subject of the e-mail'
            from_name = 'Overridden'

        # Test without global.
        with override_settings(DEFAULT_FROM_NAME=None):
            with self.assertMailsSent(1):
                TestMail().send('test@example.com', 'Body of the e-mail')
            self.assertSimple(mail.outbox[-1], from_name='Overridden')

        # Test with global.
        with self.assertMailsSent(1):
            TestMail().send('test@example.com', 'Body of the e-mail')
        self.assertSimple(mail.outbox[-1], from_name='Overridden')

    def test_send__respects_subject(self):
        """Mail().send(..) respects subject argument
        """

        class TestMail(Mail):
            subject = 'Not this subject of the e-mail'

        with self.assertMailsSent(1):
            TestMail().send('test@example.com',
                            'Body of the e-mail',
                            subject='This is the subject')
        self.assertSimple(mail.outbox[-1], subject='This is the subject')

    def test_send__with_html_body(self):
        """Mail().send(..) with HTML body sends both plain text and HTML body
        """

        class TestMail(Mail):
            subject = 'Subject of the e-mail'

        html_body = '<h1>HTML body of the e-mail</h1>'
        with self.assertMailsSent(1):
            TestMail().send('test@example.com',
                            'Body of the e-mail',
                            html_body)
        self.assertSimple(mail.outbox[-1], html_body=html_body)


__all__ = (
    'MailTestCase',
)