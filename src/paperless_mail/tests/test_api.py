from django.contrib.auth.models import User
from documents.models import Correspondent
from documents.models import DocumentType
from documents.models import Tag
from documents.tests.utils import DirectoriesMixin
from paperless_mail.models import MailAccount
from paperless_mail.models import MailRule
from rest_framework.test import APITestCase


class TestAPIMailAccounts(DirectoriesMixin, APITestCase):
    ENDPOINT = "/api/mail_accounts/"

    def setUp(self):
        super().setUp()

        self.user = User.objects.create_superuser(username="temp_admin")
        self.client.force_authenticate(user=self.user)

    def test_get_mail_accounts(self):
        """
        GIVEN:
            - Configured mail accounts
        WHEN:
            - API call is made to get mail accounts
        THEN:
            - Configured mail accounts are provided
        """

        account1 = MailAccount.objects.create(
            name="Email1",
            username="username1",
            password="password1",
            imap_server="server.example.com",
            imap_port=443,
            imap_security=MailAccount.ImapSecurity.SSL,
            character_set="UTF-8",
        )

        response = self.client.get(self.ENDPOINT)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        returned_account1 = response.data["results"][0]

        self.assertEqual(returned_account1["name"], account1.name)
        self.assertEqual(returned_account1["username"], account1.username)
        self.assertEqual(
            returned_account1["password"],
            "*" * len(account1.password),
        )
        self.assertEqual(returned_account1["imap_server"], account1.imap_server)
        self.assertEqual(returned_account1["imap_port"], account1.imap_port)
        self.assertEqual(returned_account1["imap_security"], account1.imap_security)
        self.assertEqual(returned_account1["character_set"], account1.character_set)

    def test_create_mail_account(self):
        """
        WHEN:
            - API request is made to add a mail account
        THEN:
            - A new mail account is created
        """

        account1 = {
            "name": "Email1",
            "username": "username1",
            "password": "password1",
            "imap_server": "server.example.com",
            "imap_port": 443,
            "imap_security": MailAccount.ImapSecurity.SSL,
            "character_set": "UTF-8",
        }

        response = self.client.post(
            self.ENDPOINT,
            data=account1,
        )

        self.assertEqual(response.status_code, 201)

        returned_account1 = MailAccount.objects.get(name="Email1")

        self.assertEqual(returned_account1.name, account1["name"])
        self.assertEqual(returned_account1.username, account1["username"])
        self.assertEqual(returned_account1.password, account1["password"])
        self.assertEqual(returned_account1.imap_server, account1["imap_server"])
        self.assertEqual(returned_account1.imap_port, account1["imap_port"])
        self.assertEqual(returned_account1.imap_security, account1["imap_security"])
        self.assertEqual(returned_account1.character_set, account1["character_set"])

    def test_delete_mail_account(self):
        """
        GIVEN:
            - Existing mail account
        WHEN:
            - API request is made to delete a mail account
        THEN:
            - Account is deleted
        """

        account1 = MailAccount.objects.create(
            name="Email1",
            username="username1",
            password="password1",
            imap_server="server.example.com",
            imap_port=443,
            imap_security=MailAccount.ImapSecurity.SSL,
            character_set="UTF-8",
        )

        response = self.client.delete(
            f"{self.ENDPOINT}{account1.pk}/",
        )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(len(MailAccount.objects.all()), 0)

    def test_update_mail_account(self):
        """
        GIVEN:
            - Existing mail accounts
        WHEN:
            - API request is made to update mail account
        THEN:
            - The mail account is updated, password only updated if not '****'
        """

        account1 = MailAccount.objects.create(
            name="Email1",
            username="username1",
            password="password1",
            imap_server="server.example.com",
            imap_port=443,
            imap_security=MailAccount.ImapSecurity.SSL,
            character_set="UTF-8",
        )

        response = self.client.patch(
            f"{self.ENDPOINT}{account1.pk}/",
            data={
                "name": "Updated Name 1",
                "password": "******",
            },
        )

        self.assertEqual(response.status_code, 200)

        returned_account1 = MailAccount.objects.get(pk=account1.pk)
        self.assertEqual(returned_account1.name, "Updated Name 1")
        self.assertEqual(returned_account1.password, account1.password)

        response = self.client.patch(
            f"{self.ENDPOINT}{account1.pk}/",
            data={
                "name": "Updated Name 2",
                "password": "123xyz",
            },
        )

        self.assertEqual(response.status_code, 200)

        returned_account2 = MailAccount.objects.get(pk=account1.pk)
        self.assertEqual(returned_account2.name, "Updated Name 2")
        self.assertEqual(returned_account2.password, "123xyz")


class TestAPIMailRules(DirectoriesMixin, APITestCase):
    ENDPOINT = "/api/mail_rules/"

    def setUp(self):
        super().setUp()

        self.user = User.objects.create_superuser(username="temp_admin")
        self.client.force_authenticate(user=self.user)

    def test_get_mail_rules(self):
        """
        GIVEN:
            - Configured mail accounts and rules
        WHEN:
            - API call is made to get mail rules
        THEN:
            - Configured mail rules are provided
        """

        account1 = MailAccount.objects.create(
            name="Email1",
            username="username1",
            password="password1",
            imap_server="server.example.com",
            imap_port=443,
            imap_security=MailAccount.ImapSecurity.SSL,
            character_set="UTF-8",
        )

        rule1 = MailRule.objects.create(
            name="Rule1",
            account=account1,
            folder="INBOX",
            filter_from="from@example.com",
            filter_subject="subject",
            filter_body="body",
            filter_attachment_filename="file.pdf",
            maximum_age=30,
            action=MailRule.MailAction.MARK_READ,
            assign_title_from=MailRule.TitleSource.FROM_SUBJECT,
            assign_correspondent_from=MailRule.CorrespondentSource.FROM_NOTHING,
            order=0,
            attachment_type=MailRule.AttachmentProcessing.ATTACHMENTS_ONLY,
        )

        response = self.client.get(self.ENDPOINT)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        returned_rule1 = response.data["results"][0]

        self.assertEqual(returned_rule1["name"], rule1.name)
        self.assertEqual(returned_rule1["account"], account1.pk)
        self.assertEqual(returned_rule1["folder"], rule1.folder)
        self.assertEqual(returned_rule1["filter_from"], rule1.filter_from)
        self.assertEqual(returned_rule1["filter_subject"], rule1.filter_subject)
        self.assertEqual(returned_rule1["filter_body"], rule1.filter_body)
        self.assertEqual(
            returned_rule1["filter_attachment_filename"],
            rule1.filter_attachment_filename,
        )
        self.assertEqual(returned_rule1["maximum_age"], rule1.maximum_age)
        self.assertEqual(returned_rule1["action"], rule1.action)
        self.assertEqual(returned_rule1["assign_title_from"], rule1.assign_title_from)
        self.assertEqual(
            returned_rule1["assign_correspondent_from"],
            rule1.assign_correspondent_from,
        )
        self.assertEqual(returned_rule1["order"], rule1.order)
        self.assertEqual(returned_rule1["attachment_type"], rule1.attachment_type)

    def test_create_mail_rule(self):
        """
        GIVEN:
            - Configured mail account exists
        WHEN:
            - API request is made to add a mail rule
        THEN:
            - A new mail rule is created
        """

        account1 = MailAccount.objects.create(
            name="Email1",
            username="username1",
            password="password1",
            imap_server="server.example.com",
            imap_port=443,
            imap_security=MailAccount.ImapSecurity.SSL,
            character_set="UTF-8",
        )

        tag = Tag.objects.create(
            name="t",
        )

        correspondent = Correspondent.objects.create(
            name="c",
        )

        document_type = DocumentType.objects.create(
            name="dt",
        )

        rule1 = {
            "name": "Rule1",
            "account": account1.pk,
            "folder": "INBOX",
            "filter_from": "from@example.com",
            "filter_subject": "subject",
            "filter_body": "body",
            "filter_attachment_filename": "file.pdf",
            "maximum_age": 30,
            "action": MailRule.MailAction.MARK_READ,
            "assign_title_from": MailRule.TitleSource.FROM_SUBJECT,
            "assign_correspondent_from": MailRule.CorrespondentSource.FROM_NOTHING,
            "order": 0,
            "attachment_type": MailRule.AttachmentProcessing.ATTACHMENTS_ONLY,
            "action_parameter": "parameter",
            "assign_tags": [tag.pk],
            "assign_correspondent": correspondent.pk,
            "assign_document_type": document_type.pk,
        }

        response = self.client.post(
            self.ENDPOINT,
            data=rule1,
        )

        self.assertEqual(response.status_code, 201)

        response = self.client.get(self.ENDPOINT)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        returned_rule1 = response.data["results"][0]

        self.assertEqual(returned_rule1["name"], rule1["name"])
        self.assertEqual(returned_rule1["account"], account1.pk)
        self.assertEqual(returned_rule1["folder"], rule1["folder"])
        self.assertEqual(returned_rule1["filter_from"], rule1["filter_from"])
        self.assertEqual(returned_rule1["filter_subject"], rule1["filter_subject"])
        self.assertEqual(returned_rule1["filter_body"], rule1["filter_body"])
        self.assertEqual(
            returned_rule1["filter_attachment_filename"],
            rule1["filter_attachment_filename"],
        )
        self.assertEqual(returned_rule1["maximum_age"], rule1["maximum_age"])
        self.assertEqual(returned_rule1["action"], rule1["action"])
        self.assertEqual(
            returned_rule1["assign_title_from"],
            rule1["assign_title_from"],
        )
        self.assertEqual(
            returned_rule1["assign_correspondent_from"],
            rule1["assign_correspondent_from"],
        )
        self.assertEqual(returned_rule1["order"], rule1["order"])
        self.assertEqual(returned_rule1["attachment_type"], rule1["attachment_type"])
        self.assertEqual(returned_rule1["action_parameter"], rule1["action_parameter"])
        self.assertEqual(
            returned_rule1["assign_correspondent"],
            rule1["assign_correspondent"],
        )
        self.assertEqual(
            returned_rule1["assign_document_type"],
            rule1["assign_document_type"],
        )
        self.assertEqual(returned_rule1["assign_tags"], rule1["assign_tags"])

    def test_delete_mail_rule(self):
        """
        GIVEN:
            - Existing mail rule
        WHEN:
            - API request is made to delete a mail rule
        THEN:
            - Rule is deleted
        """

        account1 = MailAccount.objects.create(
            name="Email1",
            username="username1",
            password="password1",
            imap_server="server.example.com",
            imap_port=443,
            imap_security=MailAccount.ImapSecurity.SSL,
            character_set="UTF-8",
        )

        rule1 = MailRule.objects.create(
            name="Rule1",
            account=account1,
            folder="INBOX",
            filter_from="from@example.com",
            filter_subject="subject",
            filter_body="body",
            filter_attachment_filename="file.pdf",
            maximum_age=30,
            action=MailRule.MailAction.MARK_READ,
            assign_title_from=MailRule.TitleSource.FROM_SUBJECT,
            assign_correspondent_from=MailRule.CorrespondentSource.FROM_NOTHING,
            order=0,
            attachment_type=MailRule.AttachmentProcessing.ATTACHMENTS_ONLY,
        )

        response = self.client.delete(
            f"{self.ENDPOINT}{rule1.pk}/",
        )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(len(MailRule.objects.all()), 0)

    def test_update_mail_rule(self):
        """
        GIVEN:
            - Existing mail rule
        WHEN:
            - API request is made to update mail rule
        THEN:
            - The mail rule is updated
        """

        account1 = MailAccount.objects.create(
            name="Email1",
            username="username1",
            password="password1",
            imap_server="server.example.com",
            imap_port=443,
            imap_security=MailAccount.ImapSecurity.SSL,
            character_set="UTF-8",
        )

        rule1 = MailRule.objects.create(
            name="Rule1",
            account=account1,
            folder="INBOX",
            filter_from="from@example.com",
            filter_subject="subject",
            filter_body="body",
            filter_attachment_filename="file.pdf",
            maximum_age=30,
            action=MailRule.MailAction.MARK_READ,
            assign_title_from=MailRule.TitleSource.FROM_SUBJECT,
            assign_correspondent_from=MailRule.CorrespondentSource.FROM_NOTHING,
            order=0,
            attachment_type=MailRule.AttachmentProcessing.ATTACHMENTS_ONLY,
        )

        response = self.client.patch(
            f"{self.ENDPOINT}{rule1.pk}/",
            data={
                "name": "Updated Name 1",
                "action": MailRule.MailAction.DELETE,
            },
        )

        self.assertEqual(response.status_code, 200)

        returned_rule1 = MailRule.objects.get(pk=rule1.pk)
        self.assertEqual(returned_rule1.name, "Updated Name 1")
        self.assertEqual(returned_rule1.action, MailRule.MailAction.DELETE)
