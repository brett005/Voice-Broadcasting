from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db.models.signals import post_save
from countries.models import Country
from dialer_cdr.models import Callrequest
from dialer_gateway.models import Gateway
from user_profile.models import UserProfile
from datetime import datetime, timedelta
from common.intermediate_model_base_class import Model


CONTACT_STATUS = (
    (1, u'ACTIVE'),
    (0, u'INACTIVE'),
)

CAMPAIGN_SUBSCRIBER_STATUS = (
    (1, u'PENDING'),
    (2, u'PAUSE'),
    (3, u'ABORT'),
    (4, u'FAIL'),
    (5, u'COMPLETE'),
    (6, u'IN PROCESS'),
    (7, u'NOT AUTHORIZED'),
)

CAMPAIGN_STATUS = (
    (1, u'START'),
    (2, u'PAUSE'),
    (3, u'ABORT'),
    (4, u'END'),
)

DAY_STATUS = (
    (1, u'YES'),
    (0, u'NO'),
)


class Phonebook(Model):
    """This defines the Phonebook

    **Attributes**:

        * ``name`` - phonebook name.
        * ``description`` - description about phonebook.

    Relationships:

        * ``user`` - Foreign key relationship to the User model.
                     Each phonebook assigned to User

    **Name of DB table**: dialer_phonebook
    """
    name = models.CharField(unique=True, max_length=90)
    description = models.TextField(null=True, blank=True,
                  help_text=_("Short description about the Phonebook"))
    user = models.ForeignKey('auth.User', related_name='Phonebook owner')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'dialer_phonebook'
        verbose_name = _("Phonebook")
        verbose_name_plural = _("Phonebooks")

    def __unicode__(self):
            return u"%s" % self.name

    def phonebook_contacts(self):
        """This will return count of contacts in the phonebook"""
        return Contact.objects.filter(phonebook=self.id).count()
    phonebook_contacts.allow_tags = True
    phonebook_contacts.short_description = _('Contacts')


class Contact(Model):
    """This defines the Contact

    **Attributes**:

        * ``contact`` - Contact no
        * ``last_name`` - Contact's last name
        * ``first_name`` - Contact's first name
        * ``email`` - Contact's e-mail address
        * ``city`` - city name
        * ``description`` - description about Contact
        * ``status`` - contact status
        * ``additional_vars`` - Additional variables

    Relationships:

        * ``phonebook`` - Foreign key relationship to the Phonebook model.
                          Each contact mapped with phonebook
        * ``country`` - Foreign key relationship to the Country model.
                        Each contact mapped with country

    **Name of DB table**: dialer_contact
    """
    phonebook = models.ForeignKey(Phonebook,
                                help_text=_("Select Phonebook"))
    contact = models.CharField(max_length=90)
    last_name = models.CharField(max_length=120, blank=True, null=True)
    first_name = models.CharField(max_length=120, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    description = models.TextField(null=True, blank=True,
                  help_text=_("Additional information about the contact"))
    status = models.IntegerField(choices=CONTACT_STATUS, default='1',
                verbose_name="Status", blank=True, null=True)
    additional_vars = models.CharField(max_length=100, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'dialer_contact'
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
        unique_together = ['contact', 'phonebook']

    def __unicode__(self):
            return u"%s (%s)" % (self.contact, self.last_name)

    def contact_name(self):
        """Return Contact Name"""
        return u"%s %s" % (self.first_name, self.last_name)
    contact_name.allow_tags = True
    contact_name.short_description = _('Name')


class CampaignManager(models.Manager):
    """Campaign Manager"""

    def get_running_campaign(self):
        """Return all the active campaign which will be running based on
        the expiring date, the daily start/stop time, days of the week"""
        kwargs = {}
        kwargs['status'] = 1
        tday = datetime.now()
        kwargs['startingdate__lte'] = datetime(tday.year, tday.month,
            tday.day, tday.hour, tday.minute, tday.second, tday.microsecond)
        kwargs['expirationdate__gte'] = datetime(tday.year, tday.month,
            tday.day, tday.hour, tday.minute, tday.second, tday.microsecond)

        s_time = str(tday.hour) + ":" + str(tday.minute) + ":"\
                 + str(tday.second)
        kwargs['daily_start_time__lte'] = datetime.strptime(s_time, '%H:%M:%S')
        kwargs['daily_stop_time__gte'] = datetime.strptime(s_time, '%H:%M:%S')

        # weekday status 1 - YES
        # self.model._meta.get_field(tday.strftime("%A").lower()).value()
        kwargs[tday.strftime("%A").lower()] = 1

        return Campaign.objects.filter(**kwargs)


class Campaign(Model):
    """This defines the Campaign

    **Attributes**:

        * ``name`` - Campaign name.
        * ``description`` - Description about Campaign.
        * ``status`` - Campaign status.
        * ``startingdate`` - Starting date of Campaign
        * ``expirationdate`` - Expiration date of Campaign
        * ``daily_start_time`` - Start time of day
        * ``daily_stop_time`` - End time of day
        * ``week_day_setting`` (monday, tuesday, wednesday, thursday, friday,
                                saturday, sunday)
        * ``frequency`` - Frequency, speed of the campaign. number of calls/min
        * ``callmaxduration`` - Max retry allowed per user
        * ``maxretry`` - Max retry allowed per user
        * ``intervalretry`` - Time to wait between retries in seconds
        * ``calltimeout`` - Amount of second to timeout on calls
        * ``aleg_gateway`` - Gateway to use to reach the contact
        * ``answer_url`` - Url that will provide the application in RestXML
        * ``extra_data`` - Additional data to pass to the application

    Relationships:

        * ``phonebook`` - ManyToMany relationship to the Phonebook model.

        * ``user`` - Foreign key relationship to the User model.
                     Each campaign assigned to User

    **Name of DB table**: dialer_campaign
    """
    name = models.CharField(unique=True, max_length=150)
    description = models.TextField(verbose_name='Description', blank=True,
                  null=True, help_text=_("Short description of the Campaign"))
    user = models.ForeignKey('auth.User', related_name='Campaign owner')
    status = models.IntegerField(choices=CAMPAIGN_STATUS, default='1',
                verbose_name="Status", blank=True, null=True)
    #General Starting & Stopping date
    startingdate = models.DateTimeField(default=datetime.now(),
                   verbose_name='Starting')
    expirationdate = \
            models.DateTimeField(default=datetime.now() + timedelta(days=7),
            verbose_name='Expiring')
    #Per Day Starting & Stopping Time
    daily_start_time = models.TimeField(default='00:00:00')
    daily_stop_time = models.TimeField(default='23:59:59')
    monday = models.IntegerField(choices=DAY_STATUS, default='1')
    tuesday = models.IntegerField(choices=DAY_STATUS, default='1')
    wednesday = models.IntegerField(choices=DAY_STATUS, default='1')
    thursday = models.IntegerField(choices=DAY_STATUS, default='1')
    friday = models.IntegerField(choices=DAY_STATUS, default='1')
    saturday = models.IntegerField(choices=DAY_STATUS, default='1')
    sunday = models.IntegerField(choices=DAY_STATUS, default='1')

    #Campaign Settings
    frequency = models.IntegerField(default='10', blank=True, null=True,
                help_text=_("Define the frequency, speed of the campaign. \
                This is the number of calls per minute."))
    callmaxduration = models.IntegerField(default='1800', blank=True,
                      null=True, verbose_name='Call Max Duration',
                      help_text=_("Define the \
                      call's duration maximum. (Value in seconds 1800 = \
                      30 minutes)"))
    maxretry = models.IntegerField(default='3', blank=True, null=True,
               verbose_name='Max Retries', help_text=_("Define the max retry \
               allowed per user."))
    intervalretry = models.IntegerField(default='3', blank=True, null=True,
                    verbose_name='Time between Retries', help_text=_("Define \
                    the time to wait between retries in seconds"))
    calltimeout = models.IntegerField(default='45', blank=True, null=True,
                  verbose_name='Timeout on Call', help_text=_("Define the \
                  amount of second to timeout on calls"))
    #Gateways
    aleg_gateway = models.ForeignKey(Gateway, verbose_name="A-Leg Gateway",
                related_name="A-Leg Gateway",
                help_text=_("Select Gateway to use to reach the contact"))
    answer_url = models.CharField(max_length=250, blank=True,
                verbose_name="Answer URL", help_text=_("Define the \
                Answer URL that will power the VoIP application"))
    extra_data = models.CharField(max_length=120, blank=True,
                verbose_name="Extra Data", help_text=_("Define the \
                additional data to pass to the application"))

    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    phonebook = models.ManyToManyField(Phonebook, blank=True, null=True)

    objects = CampaignManager()

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        db_table = u'dialer_campaign'
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

    def update_campaign_status(self):
        """Update campaign's status

        For example,
        If campaign is active, you can change status to 'Pause' or 'Stop'
        """
        # active - 1 | pause - 2 | stop - 4
        if self.status == 1:
            return "<a href='%s'>Pause</a> | <a href='%s'>Stop</a>" % \
            (reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 2]),
             reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 4]))

        if self.status == 2:
            return "<a href='%s'>Active</a> | <a href='%s'>Stop</a>" % \
            (reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 1]),
             reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 4]))

        if self.status == 4:
            return "<a href='%s'>Active</a> | <a href='%s'>Pause</a>" % \
            (reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 1]),
             reverse('dialer_campaign.views.update_campaign_status_admin',
             args=[self.pk, 2]))
    update_campaign_status.allow_tags = True
    update_campaign_status.short_description = _('Action')

    def count_contact_of_phonebook(self, status=None):
        """Count no of Contacts from phonebook"""
        if status and status == 1:
            count_contact = \
            Contact.objects.filter(status=1,
                                   phonebook__campaign=self.id).count()
        else:
            count_contact = \
            Contact.objects.filter(phonebook__campaign=self.id).count()
        if not count_contact:
            return "Phonebook Empty"

        return count_contact
    count_contact_of_phonebook.allow_tags = True
    count_contact_of_phonebook.short_description = _('Contact')

    def is_authorized_contact(self, str_contact):
        """Check if a contact is authorized
        For this we will check the dialer settings : whitelist and blacklist
        """
        try:
            obj_userprofile = UserProfile.objects.get(user=self.user_id)
        except UserProfile.DoesNotExist:
            #"UserProfile.DoesNotExist"
            return True

        whitelist = obj_userprofile.dialersetting.whitelist
        blacklist = obj_userprofile.dialersetting.blacklist

        import re

        if whitelist and len(whitelist) > 0:
            result = re.search(whitelist, str_contact)
            if result:
                return True

        if blacklist and len(blacklist) > 0:
            result = re.search(blacklist, str_contact)
            if result:
                return False

        #TODO Tool to test this function from the UI
        return True

    def get_active_max_frequency(self):
        """Get the active max frequency"""
        try:
            obj_userprofile = UserProfile.objects.get(user=self.user_id)
        except UserProfile.DoesNotExist:
            return self.frequency

        max_frequency = obj_userprofile.dialersetting.max_frequency
        if max_frequency < self.frequency:
            return max_frequency

        return self.frequency

    def get_active_callmaxduration(self):
        """Get the active call max duration"""
        try:
            obj_userprofile = UserProfile.objects.get(user=self.user_id)
        except UserProfile.DoesNotExist:
            return self.frequency

        callmaxduration = obj_userprofile.dialersetting.callmaxduration
        if callmaxduration < self.callmaxduration:
            return callmaxduration

        return self.callmaxduration

    def get_active_contact(self):
        """Get all the active Contact from the phonebook"""
        list_contact =\
        Contact.objects.filter(phonebook__campaign=self.id, status=1).all()
        if not list_contact:
            return False
        return list_contact

    def get_active_contact_no_subscriber(self):
        """List of active contacts that doesn't exist in CampaignSubscriber"""
        # The list of active contacts that doesn't
        # exist in CampaignSubscriber
        query = \
        'SELECT dc.id, dc.phonebook_id, dc.contact, dc.name, dc.description, \
        dc.status, dc.additional_vars, dc.created_date, dc.updated_date \
        FROM dialer_contact as dc \
        INNER JOIN dialer_phonebook ON \
        (dc.phonebook_id = dialer_phonebook.id) \
        INNER JOIN dialer_campaign_phonebook ON \
        (dialer_phonebook.id = dialer_campaign_phonebook.phonebook_id) \
        WHERE dialer_campaign_phonebook.campaign_id = %s \
        AND dc.status = 1 \
        AND dc.id NOT IN \
        (SELECT  dialer_campaign_subscriber.contact_id \
        FROM dialer_campaign_subscriber \
        WHERE dialer_campaign_subscriber.campaign_id = %s)' % \
        (str(self.id), str(self.id),)

        rawcontact_list = Contact.objects.raw(query)
        return rawcontact_list

    def progress_bar(self):
        """Progress bar generated based on no of contacts"""
        # Cache campaignsubscriber_count
        count_contact = \
        Contact.objects.filter(phonebook__campaign=self.id).count()

        # Cache need to be set per campaign
        # campaignsubscriber_count_key_campaign_id_1
        campaignsubscriber_count = \
        cache.get('campaignsubscriber_count_key_campaign_id_' + str(self.id))
        #campaignsubscriber_count = None
        if campaignsubscriber_count is None:
            list_contact = \
            Contact.objects.filter(phonebook__campaign=self.id).all()
            campaignsubscriber_count = 0
            for a in list_contact:
                campaignsubscriber_count += CampaignSubscriber.objects\
                .filter(contact=a.id, campaign=self.id, status=5).count()

            cache.set("campaignsubscriber_count_key_campaign_id_" \
            + str(self.id), campaignsubscriber_count, 5)

        campaignsubscriber_count = int(campaignsubscriber_count)
        count_contact = int(count_contact)

        if count_contact > 0:
            percentage_pixel = \
            (float(campaignsubscriber_count) / count_contact) * 100
            percentage_pixel = int(percentage_pixel)
        else:
            percentage_pixel = 0
        campaignsubscriber_count_string = \
        "campaign-subscribers (" + str(campaignsubscriber_count) + ")"
        return "<div title='%s' style='width: 100px; border: 1px solid #ccc;'>\
                <div style='height: 4px; width: %dpx; background: #555; '>\
                </div></div>" % \
                (campaignsubscriber_count_string, percentage_pixel)
    progress_bar.allow_tags = True
    progress_bar.short_description = _('Progress')

    def campaignsubscriber_detail(self):
        """This will link to campaignsubscribers which are associated with
        campaign"""
        model_name = CampaignSubscriber._meta.object_name.lower()
        app_label = self._meta.app_label
        link = '/admin/%s/%s/' % (app_label, model_name)
        link += '?campaign__id=%d' % self.id # &status__exact=5
        display_link = "<a href='%s'>" % link + _("Details") + "</a>"
        return display_link
    campaignsubscriber_detail.allow_tags = True
    campaignsubscriber_detail.short_description = _('Campaign Subscriber')

    def get_pending_subscriber(self, limit=1000):
        """Get all the pending subscriber from the campaign"""
        list_subscriber = \
        CampaignSubscriber.objects.filter(campaign=self.id, status=1)\
        .all()[:limit]
        if not list_subscriber:
            return False
        return list_subscriber


class CampaignSubscriber(Model):
    """This defines the Contact imported to a Campaign

    **Attributes**:

        * ``last_attempt`` -
        * ``count_attempt`` -
        * ``duplicate_contact`` -
        * ``status`` -

    Relationships:

        * ``contact`` - Foreign key relationship to the Contact model.
        * ``campaign`` - Foreign key relationship to the Campaign model.
        * ``callrequest`` - Foreign key relationship to the Callrequest model.

    **Name of DB table**: dialer_campaign_subscriber
    """
    contact = models.ForeignKey(Contact, null=True, blank=True,
                                help_text=_("Select Contact"))
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                                help_text=_("Select Campaign"))
    callrequest = models.ForeignKey(Callrequest, null=True, blank=True,
                                help_text=_("Select Callrequest"))
    last_attempt = models.DateTimeField(null=True, blank=True)
    count_attempt = models.IntegerField(null=True, blank=True, default='0')

    #We duplicate contact to create a unique constraint
    duplicate_contact = models.CharField(max_length=90,
                        verbose_name=_("Contact"))
    status = models.IntegerField(choices=CAMPAIGN_SUBSCRIBER_STATUS,
             default='1', verbose_name=_("Status"), blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'dialer_campaign_subscriber'
        verbose_name = _("Campaign Subscriber")
        verbose_name_plural = _("Campaign Subscribers")
        unique_together = ['contact', 'campaign']

    def __unicode__(self):
            return u"%s" % str(self.id)

    def contact_name(self):
        return self.contact.name


def post_save_add_contact(sender, **kwargs):
    """This post_save method will be called by Contact instance whenever it is
    going to save."""
    obj = kwargs['instance']
    active_campaign_list = \
    Campaign.objects.filter(phonebook__contact__id=obj.id, status=1)
    # created instance = True + active contact + active_campaign
    if kwargs['created'] and obj.status == 1 \
       and active_campaign_list.count() >= 1:
        for elem_campaign in active_campaign_list:
            try:
                CampaignSubscriber.objects.create(
                                     contact=obj,
                                     duplicate_contact=obj.contact,
                                     status=1, # START
                                     campaign=elem_campaign)
            except:
                pass

post_save.connect(post_save_add_contact, sender=Contact)