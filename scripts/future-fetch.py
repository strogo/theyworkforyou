#!/usr/bin/python

import os
import sys
package_dir = os.path.abspath(os.path.split(__file__)[0])

paths = (
    os.path.normpath(package_dir + "/../commonlib/pylib"),
    )

for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from mysociety import config
config.set_file(os.path.abspath(package_dir + "/../conf/general"))

from lxml import objectify
import MySQLdb

CALENDAR_URL = 'http://services.parliament.uk/calendar/all.rss'

class Entry(object):                                                                                                                                                          
    id = None
    created = None
    deleted = 0
    link_calendar = None
    link_external = None
    body = 'uk'
    chamber = None
    event_date = None
    time_start = None
    time_end = None
    committee_name = ''
    debate_type = ''
    title = ''
    witnesses = ''
    location = ''

    def __init__(self, entry):
        self.id = entry.event.attrib['id']
        self.link_calendar = entry.guid
        self.link_external = entry.link
        self.chamber = '%s: %s' % (entry.event.house.text.strip(), entry.event.chamber.text.strip())
        self.event_date = entry.event.date
        self.time_start = getattr(entry.event, 'startTime', None)
        self.time_end = getattr(entry.event, 'endTime', None)

        committee_text = entry.event.comittee.text
        if committee_text:
            committee_text = committee_text.strip()
            if committee_text == 'Select Committee':
                self.committee_name = committee_text
            else:
                self.debate_type = committee_text

        title_text = entry.event.inquiry.text
        if title_text:
            # TODO Check for person's name at end of this string, strip and match to ID if present
            self.title = title_text.strip()

        witness_text = entry.event.witnesses.text
        if witness_text == 'This is a private meeting.':
            self.title = witness_text
        elif witness_text:
            self.witnesses = witness_text.strip()

        location_text = entry.event.location.text
        if location_text: self.location = location_text.strip()

    def add(self):
        # TODO This function needs to insert into Xapian as well, or store to insert in one go at the end
        db_cursor.execute("""INSERT INTO future (
            id, created, deleted, 
            link_calendar, link_external, 
            body, chamber, 
            event_date, time_start, time_end, 
            committee_name, debate_type, 
            title, witnesses, location
        ) VALUES (
            %s, now(), %s, 
            %s, %s, 
            %s, %s, 
            %s, %s, %s, 
            %s, %s, 
            %s, %s, %s
        )""", (
            self.id, 0,
            self.link_calendar, self.link_external,
            self.body, self.chamber,
            self.event_date, self.time_start, self.time_end,
            self.committee_name, self.debate_type,
            self.title.encode('iso-8859-1', 'xmlcharrefreplace'),
            self.witnesses.encode('iso-8859-1', 'xmlcharrefreplace'),
            self.location.encode('iso-8859-1', 'xmlcharrefreplace'),
        ) )

db_connection = MySQLdb.connect(
    host=config.get('TWFY_DB_HOST'),
    db=config.get('TWFY_DB_NAME'),
    user=config.get('TWFY_DB_USER'),
    passwd=config.get('TWFY_DB_PASS'),
    )

db_cursor = db_connection.cursor()


parsed = objectify.parse(CALENDAR_URL)
root = parsed.getroot()

entries = root.channel.findall('item')
for entry in entries:
    id = entry.event.attrib['id']
    row_count = db_cursor.execute('select * from future where id=%s', id)

    if row_count:
        # We have seen this event before. TODO Compare with current entry,
        # update db and Xapian if so
        pass
    else:
        Entry(entry).add()

# TODO HERE: Remove entries that are no longer present in the feed.
