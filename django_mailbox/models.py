#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Models declaration for application ``django_mailbox``.
"""

from email.encoders import encode_base64
from email.message import Message as EmailMessage
from email.utils import formatdate, parseaddr
from quopri import encode as encode_quopri
import base64
import email
import logging
import mimetypes
import os.path
import sys
import uuid

import six
from six.moves.urllib.parse import parse_qs, unquote, urlparse

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail.message import make_msgid
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .utils import convert_header_to_unicode, get_body_from_message
from django_mailbox.signals import message_received
from django_mailbox.transports import Pop3Transport, ImapTransport, \
    MaildirTransport, MboxTransport, BabylTransport, MHTransport, \
    MMDFTransport, GmailImapTransport

logger = logging.getLogger(__name__)


STRIP_UNALLOWED_MIMETYPES = getattr(
    settings,
    'DJANGO_MAILBOX_STRIP_UNALLOWED_MIMETYPES',
    False
)

ALLOWED_MIMETYPES = getattr(
    settings,
    'DJANGO_MAILBOX_ALLOWED_MIMETYPES',
    [
        'text/plain',
        'text/html'
    ]
)

TEXT_STORED_MIMETYPES = getattr(
    settings,
    'DJANGO_MAILBOX_TEXT_STORED_MIMETYPES',
    [
        'text/plain',
        'text/html'
    ]
)

ALTERED_MESSAGE_HEADER = getattr(
    settings,
    'DJANGO_MAILBOX_ALTERED_MESSAGE_HEADER',
    'X-Django-Mailbox-Altered-Message'
)

ATTACHMENT_INTERPOLATION_HEADER = getattr(
    settings,
    'DJANGO_MAILBOX_ATTACHMENT_INTERPOLATION_HEADER',
    'X-Django-Mailbox-Interpolate-Attachment'
)

ATTACHMENT_UPLOAD_TO = getattr(
    settings,
    'DJANGO_MAILBOX_ATTACHMENT_UPLOAD_TO',
    'mailbox_attachments/%Y/%m/%d/'
)

STORE_ORIGINAL_MESSAGE = getattr(
    settings,
    'DJANGO_MAILBOX_STORE_ORIGINAL_MESSAGE',
    False
)


class ActiveMailboxManager(models.Manager):
    def get_queryset(self):
        return super(ActiveMailboxManager, self).get_queryset().filter(
            active=True,
        )


class Mailbox(models.Model):
    name = models.CharField(
        _(u'Name'),
        max_length=255,
    )

    uri = models.CharField(
        _(u'URI'),
        max_length=255,
        help_text=(_(
            "Example: imap+ssl://myusername:mypassword@someserver <br />"
            "<br />"
            "Internet transports include 'imap' and 'pop3'; "
            "common local file transports include 'maildir', 'mbox', "
            "and less commonly 'babyl', 'mh', and 'mmdf'. <br />"
            "<br />"
            "Be sure to urlencode your username and password should they "
            "contain illegal characters (like @, :, etc)."
        )),
        blank=True,
        null=True,
        default=None,
    )

    from_email = models.CharField(
        _(u'From email'),
        max_length=255,
        help_text=(_(
            "Example: MailBot &lt;mailbot@yourdomain.com&gt;<br />"
            "'From' header to set for outgoing email.<br />"
            "<br />"
            "If you do not use this e-mail inbox for outgoing mail, this "
            "setting is unnecessary.<br />"
            "If you send e-mail without setting this, your 'From' header will'"
            "be set to match the setting `DEFAULT_FROM_EMAIL`."
        )),
        blank=True,
        null=True,
        default=None,
    )

    active = models.BooleanField(
        _(u'Active'),
        help_text=(_(
            "Check this e-mail inbox for new e-mail messages during polling "
            "cycles.  This checkbox does not have an effect upon whether "
            "mail is collected here when this mailbox receives mail from a "
            "pipe, and does not affect whether e-mail messages can be "
            "dispatched from this mailbox. "
        )),
        blank=True,
        default=True,
    )

    objects = models.Manager()
    active_mailboxes = ActiveMailboxManager()

    @property
    def _protocol_info(self):
        return urlparse(self.uri)

    @property
    def _query_string(self):
        return parse_qs(self._protocol_info.query)

    @property
    def _domain(self):
        return self._protocol_info.hostname

    @property
    def port(self):
        """Returns the port to use for fetching messages."""
        return self._protocol_info.port

    @property
    def username(self):
        """Returns the username to use for fetching messages."""
        return unquote(self._protocol_info.username)

    @property
    def password(self):
        """Returns the password to use for fetching messages."""
        return unquote(self._protocol_info.password)

    @property
    def location(self):
        """Returns the location (domain and path) of messages."""
        return self._domain if self._domain else '' + self._protocol_info.path

    @property
    def type(self):
        """Returns the 'transport' name for this mailbox."""
        scheme = self._protocol_info.scheme.lower()
        if '+' in scheme:
            return scheme.split('+')[0]
        return scheme

    @property
    def use_ssl(self):
        """Returns whether or not this mailbox's connection uses SSL."""
        return '+ssl' in self._protocol_info.scheme.lower()

    @property
    def archive(self):
        """Returns (if specified) the folder to archive messages to."""
        archive_folder = self._query_string.get('archive', None)
        if not archive_folder:
            return None
        return archive_folder[0]

    @property
    def folder(self):
        """Returns (if specified) the folder to fetch mail from."""
        folder = self._query_string.get('folder', None)
        if not folder:
            return None
        return folder[0]

    def get_connection(self):
        """Returns the transport instance for this mailbox.

        These will always be instances of
        `django_mailbox.transports.base.EmailTransport`.

        """
        if not self.uri:
            return None
        elif self.type == 'imap':
            conn = ImapTransport(
                self.location,
                port=self.port if self.port else None,
                ssl=self.use_ssl,
                archive=self.archive,
                folder=self.folder
            )
            conn.connect(self.username, self.password)
        elif self.type == 'gmail':
            conn = GmailImapTransport(
                self.location,
                port=self.port if self.port else None,
                ssl=True,
                archive=self.archive
            )
            conn.connect(self.username, self.password)
        elif self.type == 'pop3':
            conn = Pop3Transport(
                self.location,
                port=self.port if self.port else None,
                ssl=self.use_ssl
            )
            conn.connect(self.username, self.password)
        elif self.type == 'maildir':
            conn = MaildirTransport(self.location)
        elif self.type == 'mbox':
            conn = MboxTransport(self.location)
        elif self.type == 'babyl':
            conn = BabylTransport(self.location)
        elif self.type == 'mh':
            conn = MHTransport(self.location)
        elif self.type == 'mmdf':
            conn = MMDFTransport(self.location)
        return conn

    def process_incoming_message(self, message):
        """Process a message incoming to this mailbox."""
        msg = self._process_message(message)
        msg.outgoing = False
        msg.save()

        message_received.send(sender=self, message=msg)

        return msg

    def record_outgoing_message(self, message):
        """Record an outgoing message associated with this mailbox."""
        msg = self._process_message(message)
        msg.outgoing = True
        msg.save()
        return msg

    def _get_dehydrated_message(self, msg, record):
        new = EmailMessage()
        if msg.is_multipart():
            for header, value in msg.items():
                new[header] = value
            for part in msg.get_payload():
                new.attach(
                    self._get_dehydrated_message(part, record)
                )
        elif (
            STRIP_UNALLOWED_MIMETYPES
            and not msg.get_content_type() in ALLOWED_MIMETYPES
        ):
            for header, value in msg.items():
                new[header] = value
            # Delete header, otherwise when attempting to  deserialize the
            # payload, it will be expecting a body for this.
            del new['Content-Transfer-Encoding']
            new[ALTERED_MESSAGE_HEADER] = (
                'Stripped; Content type %s not allowed' % (
                    msg.get_content_type()
                )
            )
            new.set_payload('')
        elif (
            (msg.get_content_type() not in TEXT_STORED_MIMETYPES) or
            ('attachment' in msg.get('Content-Disposition', ''))
        ):
            filename = msg.get_filename()
            if not filename:
                extension = mimetypes.guess_extension(msg.get_content_type())
            else:
                _, extension = os.path.splitext(filename)
            if not extension:
                extension = '.bin'

            attachment = MessageAttachment()

            attachment.document.save(
                uuid.uuid4().hex + extension,
                ContentFile(
                    six.BytesIO(
                        msg.get_payload(decode=True)
                    ).getvalue()
                )
            )
            attachment.message = record
            for key, value in msg.items():
                attachment[key] = value
            attachment.save()

            placeholder = EmailMessage()
            placeholder[ATTACHMENT_INTERPOLATION_HEADER] = str(attachment.pk)
            new = placeholder
        else:
            content_charset = msg.get_content_charset()
            if not content_charset:
                content_charset = 'ascii'
            try:
                # Make sure that the payload can be properly decoded in the
                # defined charset, if it can't, let's mash some things
                # inside the payload :-\
                msg.get_payload(decode=True).decode(content_charset)
            except LookupError:
                logger.warning(
                    "Unknown encoding %s; interpreting as ASCII!",
                    content_charset
                )
                msg.set_payload(
                    msg.get_payload(decode=True).decode(
                        'ascii',
                        'ignore'
                    )
                )
            except ValueError:
                logger.warning(
                    "Decoding error encountered; interpreting as ASCII!",
                    content_charset
                )
                msg.set_payload(
                    msg.get_payload(decode=True).decode(
                        content_charset,
                        'ignore'
                    )
                )
            new = msg
        return new

    def _process_message(self, message):
        msg = Message()
        if STORE_ORIGINAL_MESSAGE:
            msg.eml.save('%s.eml' % uuid.uuid4(), ContentFile(message), save=False)
        msg.mailbox = self
        if 'subject' in message:
            msg.subject = convert_header_to_unicode(message['subject'])[0:255]
        if 'message-id' in message:
            msg.message_id = message['message-id'][0:255].strip()
        if 'from' in message:
            msg.from_header = convert_header_to_unicode(message['from'])
        if 'to' in message:
            msg.to_header = convert_header_to_unicode(message['to'])
        elif 'Delivered-To' in message:
            msg.to_header = convert_header_to_unicode(message['Delivered-To'])
        msg.save()
        message = self._get_dehydrated_message(message, msg)
        msg.set_body(message.as_string())
        if message['in-reply-to']:
            try:
                msg.in_reply_to = Message.objects.filter(
                    message_id=message['in-reply-to'].strip()
                )[0]
            except IndexError:
                pass
        msg.save()
        return msg

    def get_new_mail(self, condition=None):
        """Connect to this transport and fetch new messages."""
        new_mail = []
        connection = self.get_connection()
        if not connection:
            return new_mail
        for message in connection.get_message(condition):
            msg = self.process_incoming_message(message)
            new_mail.append(msg)
        return new_mail

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Mailboxes"


class IncomingMessageManager(models.Manager):
    def get_queryset(self):
        return super(IncomingMessageManager, self).get_queryset().filter(
            outgoing=False,
        )


class OutgoingMessageManager(models.Manager):
    def get_queryset(self):
        return super(OutgoingMessageManager, self).get_queryset().filter(
            outgoing=True,
        )


class UnreadMessageManager(models.Manager):
    def get_queryset(self):
        return super(UnreadMessageManager, self).get_queryset().filter(
            read=None
        )


class Message(models.Model):
    mailbox = models.ForeignKey(
        Mailbox,
        related_name='messages',
        verbose_name=_(u'Mailbox'),
    )

    subject = models.CharField(
        _(u'Subject'),
        max_length=255
    )

    message_id = models.CharField(
        _(u'Message ID'),
        max_length=255
    )

    in_reply_to = models.ForeignKey(
        'django_mailbox.Message',
        related_name='replies',
        blank=True,
        null=True,
        verbose_name=_(u'In reply to'),
    )

    from_header = models.CharField(
        _('From header'),
        max_length=255,
    )

    to_header = models.TextField(
        _(u'To header'),
    )

    outgoing = models.BooleanField(
        _(u'Outgoing'),
        default=False,
        blank=True,
    )

    body = models.TextField(
        _(u'Body'),
    )

    encoded = models.BooleanField(
        _(u'Encoded'),
        default=False,
        help_text=_('True if the e-mail body is Base64 encoded'),
    )

    processed = models.DateTimeField(
        _('Processed'),
        auto_now_add=True
    )

    read = models.DateTimeField(
        _(u'Read'),
        default=None,
        blank=True,
        null=True,
    )

    eml = models.FileField(
        _(u'Raw message contents'),
        null=True,
        upload_to="messages",
        help_text=_(u'Original full content of message')
    )
    objects = models.Manager()
    unread_messages = UnreadMessageManager()
    incoming_messages = IncomingMessageManager()
    outgoing_messages = OutgoingMessageManager()

    @property
    def address(self):
        """Property allowing one to get the relevant address(es).

        In earlier versions of this library, the model had an `address` field
        storing the e-mail address from which a message was received.  During
        later refactorings, it became clear that perhaps storing sent messages
        would also be useful, so the address field was replaced with two
        separate fields.

        """
        addresses = []
        addresses = self.to_addresses + self.from_address
        return addresses

    @property
    def from_address(self):
        """Returns the address (as a list) from which this message was received

        .. note::

           This was once (and probably should be) a string rather than a list,
           but in a pull request received long, long ago it was changed;
           presumably to make the interface identical to that of
           `to_addresses`.

        """
        if self.from_header:
            return [parseaddr(self.from_header)[1].lower()]
        else:
            return []

    @property
    def to_addresses(self):
        """Returns a list of addresses to which this message was sent."""
        addresses = []
        for address in self.to_header.split(','):
            if address:
                addresses.append(
                    parseaddr(
                        address
                    )[1].lower()
                )
        return addresses

    def reply(self, message):
        """Sends a message as a reply to this message instance.

        Although Django's e-mail processing will set both Message-ID
        and Date upon generating the e-mail message, we will not be able
        to retrieve that information through normal channels, so we must
        pre-set it.

        """
        if not message.from_email:
            if self.mailbox.from_email:
                message.from_email = self.mailbox.from_email
            else:
                message.from_email = settings.DEFAULT_FROM_EMAIL
        message.extra_headers['Message-ID'] = make_msgid()
        message.extra_headers['Date'] = formatdate()
        message.extra_headers['In-Reply-To'] = self.message_id.strip()
        message.send()
        return self.mailbox.record_outgoing_message(
            email.message_from_string(
                message.message().as_string()
            )
        )

    @property
    def text(self):
        """
        Returns the message body matching content type 'text/plain'.
        """
        return get_body_from_message(
            self.get_email_object(), 'text', 'plain'
        ).replace('=\n', '').strip()

    @property
    def html(self):
        """
        Returns the message body matching content type 'text/html'.
        """
        return get_body_from_message(
            self.get_email_object(), 'text', 'html'
        ).replace('\n', '').strip()

    def _rehydrate(self, msg):
        new = EmailMessage()
        if msg.is_multipart():
            for header, value in msg.items():
                new[header] = value
            for part in msg.get_payload():
                new.attach(
                    self._rehydrate(part)
                )
        elif ATTACHMENT_INTERPOLATION_HEADER in msg.keys():
            try:
                attachment = MessageAttachment.objects.get(
                    pk=msg[ATTACHMENT_INTERPOLATION_HEADER]
                )
                for header, value in attachment.items():
                    new[header] = value
                encoding = new['Content-Transfer-Encoding']
                if encoding and encoding.lower() == 'quoted-printable':
                    # Cannot use `email.encoders.encode_quopri due to
                    # bug 14360: http://bugs.python.org/issue14360
                    output = six.BytesIO()
                    encode_quopri(
                        six.BytesIO(
                            attachment.document.read()
                        ),
                        output,
                        quotetabs=True,
                        header=False,
                    )
                    new.set_payload(
                        output.getvalue().decode().replace(' ', '=20')
                    )
                    del new['Content-Transfer-Encoding']
                    new['Content-Transfer-Encoding'] = 'quoted-printable'
                else:
                    new.set_payload(
                        attachment.document.read()
                    )
                    del new['Content-Transfer-Encoding']
                    encode_base64(new)
            except MessageAttachment.DoesNotExist:
                new[ALTERED_MESSAGE_HEADER] = (
                    'Missing; Attachment %s not found' % (
                        msg[ATTACHMENT_INTERPOLATION_HEADER]
                    )
                )
                new.set_payload('')
        else:
            for header, value in msg.items():
                new[header] = value
            new.set_payload(
                msg.get_payload()
            )
        return new

    def get_body(self):
        """Returns the `body` field of this record.

        This will automatically base64-decode the message contents
        if they are encoded as such.

        """
        if self.encoded:
            return base64.b64decode(self.body.encode('ascii'))
        return self.body.encode('utf-8')

    def set_body(self, body):
        """Set the `body` field of this record.

        This will automatically base64-encode the message contents to
        circumvent a limitation in earlier versions of Django in which
        no fields existed for storing arbitrary bytes.

        """
        if six.PY3:
            body = body.encode('utf-8')
        self.encoded = True
        self.body = base64.b64encode(body).decode('ascii')

    def get_email_object(self):
        """Returns an `email.message.Message` instance representing the
        contents of this message and all attachments.

        See [email.Message.Message]_ for more information as to what methods
        and properties are available on `email.message.Message` instances.

        .. note::

           Depending upon the storage methods in use (specifically --
           whether ``DJANGO_MAILBOX_STORE_ORIGINAL_MESSAGE`` is set
           to ``True``, this may either create a "rehydrated" message
           using stored attachments, or read the message contents stored
           on-disk.

        .. [email.Message.Message]: Python's `email.message.Message` docs
           (https://docs.python.org/2/library/email.message.html)

        """
        if self.eml:
            self.eml.open()
            body = self.eml.file.read()
        else:
            body = self.get_body()
        if six.PY3:
            flat = email.message_from_bytes(body)
        else:
            flat = email.message_from_string(body)
        return self._rehydrate(flat)

    def delete(self, *args, **kwargs):
        """Delete this message and all stored attachments."""
        for attachment in self.attachments.all():
            # This attachment is attached only to this message.
            attachment.delete()
        return super(Message, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.subject


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        Message,
        related_name='attachments',
        null=True,
        blank=True,
        verbose_name=_('Message'),
    )

    headers = models.TextField(
        _(u'Headers'),
        null=True,
        blank=True,
    )

    document = models.FileField(
        _(u'Document'),
        upload_to=ATTACHMENT_UPLOAD_TO,
    )

    def delete(self, *args, **kwargs):
        """Deletes the attachment."""
        self.document.delete()
        return super(MessageAttachment, self).delete(*args, **kwargs)

    def _get_rehydrated_headers(self):
        headers = self.headers
        if headers is None:
            return EmailMessage()
        if sys.version_info < (3, 0):
            try:
                headers = headers.encode('utf-8')
            except UnicodeDecodeError:
                headers = unicode(headers, 'utf-8').encode('utf-8')
        return email.message_from_string(headers)

    def _set_dehydrated_headers(self, email_object):
        self.headers = email_object.as_string()

    def __delitem__(self, name):
        rehydrated = self._get_rehydrated_headers()
        del rehydrated[name]
        self._set_dehydrated_headers(rehydrated)

    def __setitem__(self, name, value):
        rehydrated = self._get_rehydrated_headers()
        rehydrated[name] = value
        self._set_dehydrated_headers(rehydrated)

    def get_filename(self):
        """Returns the original filename of this attachment."""
        file_name = self._get_rehydrated_headers().get_filename()
        if isinstance(file_name, six.text_type):
            return file_name
        elif file_name:
            return convert_header_to_unicode(file_name)
        else:
            return None

    def items(self):
        return self._get_rehydrated_headers().items()

    def __getitem__(self, name):
        value = self._get_rehydrated_headers()[name]
        if value is None:
            raise KeyError('Header %s does not exist' % name)
        return value

    def __unicode__(self):
        return self.document.url