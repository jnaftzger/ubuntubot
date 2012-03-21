# script:
#	- iterates through each table described by a file in the directory at "psTableDirectory" and
#	- exports each table via DDE
#	- processes each file to remove special characters and convert dates to ISO format saving converted file in same directory
#	- reads each converted file a line at a time, splits the data, converts it to a SQL string, and loads data into mySQL
#	- 
#
# scottdawson72

# this code requires at config file
# specify the path here
config_file_path = r'/home/orwig/Dropbox/lincoln_ubuntubot/ubuntubot.cfg'

import ConfigParser
import datetime
import erc
#import follett
import gmailer
import logging
import MySQLdb
import os
import powerschool
import ps1000
import re
import string
import sys
import time
import unittest

config = ConfigParser.ConfigParser()
config.read([config_file_path])

gmail_user = config.get('gmail', 'user')
gmail_pwd = config.get('gmail', 'password')
email_body = ''
email_attention_flag = ''
prowl_address = config.get('prowl', 'email')
log_file = config.get('logging','path')

logging.basicConfig(filename=log_file)

multiple_building = 0
powerschool_table_directory = config.get('vlad', 'table_directory')
browser_download_directory = config.get('vlad', 'download_directory')
logging.info('Download directory:{0}'.format(browser_download_directory))
today = datetime.date.today()
date_stamp = today.strftime("%A, %B %d %Y")
powerschool_term_id = 'label=11-12 2011-2012'
field_delimeter = '^'
record_delimiter = '|'
sql_statement_counter = 0

prowl_body = ''


full_path_to_host_file = config.get('ps1000', 'path_to_host_file')

whitelist = string.letters + string.digits + ' ' + '/' + '?' + '\\' + '\t' + '.' + '!' + '@' + '#' + '$' + '%' + '&' + '*' + '(' + ')' + '_' + '-' + '=' + '+' + ':' + ';' + '|' + '[' + ']' + '{' + '}' + '<' + '>' + '~' + '^' + '`'
date_finder = re.compile('([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})')

def characters_from_whitelist_only(dirty_string):
   clean_string = ''
   for shady_character in dirty_string:
      if shady_character in whitelist:
         clean_string += shady_character
   return clean_string

## PROCEDURAL CODE STARTS HERE

# db_host = 'localhost'
# db_user = config.get('powerschoolmirror', 'user')
# db_password = config.get('powerschoolmirror', 'password')
# db_name = config.get('powerschoolmirror', 'database')
# conn = MySQLdb.connect (host = db_host,
#                         user = db_user,
#                         passwd = db_password,
#                         db = db_name)
# cursor = conn.cursor ()
# cursor.execute ("SELECT VERSION()")
# row = cursor.fetchone ()
# logging.info('Connected to mySQL - server version: {0}'.format(row[0]))
# cursor.close ()
# conn.close ()

#prowl_body = prowl_body + '\n' + powerschool.update_students()
prowl_body = prowl_body + '\n' + powerschool.update_teachers()
prowl_body = prowl_body + '\n' + powerschool.update_graduation_requirements()
prowl_body = prowl_body + '\n' + powerschool.update_graduation_requirements_sets()

ps1000.write_host_file()
erc.write_erc_update_file()


prowl_subject = 'vlad has run'
prowl_body = prowl_body + '\nvlad completed a run at {0}'.format(date_stamp)
gmailer.mail(prowl_address, prowl_subject, prowl_body, gmail_user, gmail_pwd)
