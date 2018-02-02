from django.db import models

from siem.choices import *

# Create your models here.

def validate_modifier_range(value):
    if not 0 < value <= 10:
        raise ValidationError('%s not in 0.1-10 range' % value)

class LogEventParser(models.Model):
    name = models.CharField(max_length=32, unique=True)
    desc = models.CharField(max_length=200, null=True, blank=True)
    match_regex = models.CharField(max_length=1024)
    backup_match_regex = models.CharField(max_length=1024,
            null=True, blank=True)
    fields = models.CharField(max_length=512)
    backup_fields = models.CharField(max_length=512,
            null=True, blank=True)

class LogEvent(models.Model):
    parsed_at = models.DateTimeField(6)
    time_zone = models.CharField(max_length=32,
            null=True, blank=True)
    eol_date_local = models.DateField()
    eol_date_backup = models.DateField()
    event_type = models.CharField(max_length=24, default='default')
    raw_text = models.CharField(max_length=1280)
    date_stamp = models.CharField(max_length=32,
            null=True, blank=True)
    facility = models.IntegerField(choices=facility_choices,
            null=True, blank=True)
    severity = models.IntegerField(choices=severity_choices,
            null=True, blank=True)
    source_host = models.CharField(max_length=32, default='')
    source_port = models.CharField(max_length=8, default='')
    dest_host = models.CharField(max_length=32, default='')
    dest_port = models.CharField(max_length=8, default='')
    source_process = models.CharField(max_length=24, default='')
    source_pid = models.IntegerField(
            null=True, blank=True)
    protocol = models.CharField(max_length=12, default='')
    message = models.CharField(max_length=1024, default='')
    extended = models.CharField(max_length=1024, default='')
    ext_user = models.CharField(max_length=32, default='')
    ext_ip = models.CharField(max_length=32, default='')
    ext_session = models.CharField(max_length=24, default='')
    parsed_on = models.CharField(max_length=32)
    source_path = models.CharField(max_length=200,)
    class Meta:
        permissions = (('view_logevent', 'Can view log events'),)


class LimitRule(models.Model):
    name = models.CharField(max_length=32)
    desc = models.CharField(max_length=200,
            null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    rule_events = models.BooleanField(default=False)
    rule_category = models.CharField(max_length=24, default='default')
    local_lifespan_days = models.IntegerField()
    backup_lifespan_days = models.IntegerField()
    event_type = models.CharField(max_length=24, default='default')
    severity = models.IntegerField(choices=severity_choices)
    overkill_modifier = models.DecimalField(
            validators=[validate_modifier_range],
            decimal_places=1, max_digits=3, default=1)
    severity_modifier = models.DecimalField(
            validators=[validate_modifier_range],
            decimal_places=1, max_digits=3, default=1)
    time_int = models.IntegerField()
    event_limit = models.IntegerField()
    message_filter_regex = models.CharField(max_length=1024,
            null=True, blank=True)
    raw_text_filter_regex = models.CharField(max_length=1024,
            null=True, blank=True)
    source_host_filter = models.CharField(max_length=32,
            null=True, blank=True)
    process_filter = models.CharField(max_length=32,
            null=True, blank=True)
    rulename_filter = models.CharField(max_length=32,
            null=True, blank=True)
    magnitude_filter = models.IntegerField(null=True, blank=True)
    message = models.CharField(max_length=1024)
    def __str__(self):
        return self.name
    class Meta:
        permissions = (('view_limitrule', 'Can view limit rules'),)


class RuleEvent(models.Model):
    date_stamp = models.DateTimeField()
    time_zone = models.CharField(max_length=32)
    eol_date_local = models.DateField()
    eol_date_backup = models.DateField()
    rule_category = models.CharField(max_length=24, default='default')
    event_type = models.CharField(max_length=24, default='default')
    source_rule = models.ForeignKey(LimitRule,
            related_name='triggered_events',
            on_delete=models.PROTECT)
    severity = models.IntegerField(choices=severity_choices)
    event_limit = models.IntegerField()
    event_count = models.IntegerField()
    magnitude = models.IntegerField()
    time_int = models.IntegerField()
    message = models.CharField(max_length=1024)
    source_ids_log = models.ManyToManyField(LogEvent,
            related_name='rules_triggered',
            blank=True)
    source_ids_rule = models.ManyToManyField('self',
            related_name='rules_triggered',
            blank=True, symmetrical=False)
    class Meta:
        permissions = (('view_ruleevent', 'Can view rule events'),)
