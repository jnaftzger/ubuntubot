import configmanager
import datetime
import logging
import MySQLdb
import os
import string
import time
import xml.etree.ElementTree as element_tree

configuration_values = configmanager.readconfig()

current_time = datetime.datetime.now()
datetime_stamp = current_time.strftime('%Y%m%d_%H%M%S')
request_file_name = ''.join(['uic_request_', datetime_stamp,'.xml'])
request_file_path = os.path.join(configuration_values['etl_directory'],request_file_name)
print 'UIC request file to be written at:{0}'.format(request_file_path)

db_host = 'localhost'
db_user = configuration_values['db_user']
db_password = configuration_values['db_passwd']
db_name = configuration_values['db_db']
conn = MySQLdb.connect (host = db_host,
                    user = db_user,
                    passwd = db_password,
                    db = db_name)

sql_query = """SELECT last_name, first_name, dob, gender, schoolid, student_number, grade_level, Mailing_Street, Mailing_City, Mailing_State, Mailing_Zip, Ethnicity, ExitCode FROM students"""

def write_uic_request_file():
	cursor = conn.cursor()
	cursor.execute(sql_query)

	building_lookup = {'4':'05235','004':'05235', '100':'05235','200':'07190','300':'02186','400':'05166','500':'02187','600':'00308','700':'09148', '800':'00405', '900':'00052', '999999':'999999', '1100':'00052'}
	attribute_dictionary = {'SchemaVersionMinor': '2', 'SubmittingSystemVersion': '1.0', 'CollectionName': 'RequestforUIC', 'SubmittingSystemVendor': 'ScottOrwig', 'CollectionId': '102', 'SchemaVersionMajor': 'Collection', 'SubmittingSystemName': 'Ubuntubot', 'xsi:noNamespaceSchemaLocation': 'http://cepi.state.mi.us/msdsxml/RequestforUICCollection2.xsd', 'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
    
	root = element_tree.Element('RequestforUICGroup', attribute_dictionary)

	result = cursor.fetchall()
   	record_count = len(result)
   	log_string = '{0} records SELECTed from the database'.format(record_count)
   	print log_string

   	for student in result:
      	 if student[4] != '999999':
     		request = element_tree.SubElement(root,'RequestforUIC')

     		entity = element_tree.SubElement(request, 'SubmittingEntity')
     		type_code = element_tree.SubElement(entity,'SubmittingEntityTypeCode')
     		type_code.text = 'D'
     		entity_code = element_tree.SubElement(entity, 'SubmittingEntityCode')
     		entity_code.text = '81070'

     		personal_core = element_tree.SubElement(request, 'PersonalCore')
     		last_name = element_tree.SubElement(personal_core, 'LastName')
     		last_name.text = student[0]
                first_name = element_tree.SubElement(personal_core, 'FirstName')
                first_name.text = student[1]
                date_of_birth = element_tree.SubElement(personal_core,'DateOfBirth')
                try:
                    date_of_birth.text = student[2].strftime('%Y-%m-%d')
                except:
                    date_of_birth.text = '2000-01-01'
                gender = element_tree.SubElement(personal_core,"Gender")
                gender.text = student[3]

                school_demographics = element_tree.SubElement(request, 'SchoolDemographics')
                operating_isd_number = element_tree.SubElement(school_demographics,'OperatingISDESANumber')
                operating_isd_number.text = '81'
                operating_district_number = element_tree.SubElement(school_demographics,'OperatingDistrictNumber')
                operating_district_number.text = '81070'
                school_facility_number = element_tree.SubElement(school_demographics, 'SchoolFacilityNumber')
                try:
                    school_facility_number.text = building_lookup[student[4]]
                except:
                    school_facility_number.text = '02187'

                student_id_number = element_tree.SubElement(school_demographics, 'StudentIdNumber')
                student_id_number.text = student[5]
                grade_or_setting = element_tree.SubElement(school_demographics, 'GradeOrSetting')
                if student[6] == '-2':
                    grade_or_setting.text = '00'
                else:
                    grade_or_setting.text = student[6].zfill(2)




   	file_writer = open(request_file_path, 'w')
   	element_tree.ElementTree(root).write(file_writer)


write_uic_request_file()



    
