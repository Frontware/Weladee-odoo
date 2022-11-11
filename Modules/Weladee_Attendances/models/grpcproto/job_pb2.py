# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: job.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import weladee_pb2 as weladee__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tjob.proto\x12\x10grpc.weladee.com\x1a\rweladee.proto\"w\n\x08\x41pplyJob\x12\x12\n\x04\x41\x64ID\x18\x01 \x01(\x03R\x04\x61\x64id\x12\x39\n\tCandidate\x18\x02 \x01(\x0b\x32\x1b.grpc.weladee.com.CandidateR\tcandidate\x12\x1c\n\tCompanyID\x18\x03 \x01(\x03R\tcompanyid\"\xfd\x01\n\tCandidate\x12\x0e\n\x02ID\x18\x01 \x01(\x03R\x02id\x12\x1b\n\x08LastName\x18\x02 \x01(\tR\tlast_name\x12\x1d\n\tFirstName\x18\x03 \x01(\tR\nfirst_name\x12\x14\n\x05\x45mail\x18\x04 \x01(\tR\x05\x65mail\x12\x14\n\x05Phone\x18\x05 \x01(\tR\x05phone\x12\x14\n\x08Language\x18\x06 \x01(\tR\x02lg\x12\x30\n\x06Gender\x18\x07 \x01(\x0e\x32\x18.grpc.weladee.com.GenderR\x06gender\x12\x30\n\x12LinkedInProfileURL\x18\n \x01(\tR\x14linkedin_profile_url\"\xdf\x03\n\x0eJobApplication\x12\x0e\n\x02ID\x18\x01 \x01(\x03R\x02id\x12 \n\x0b\x43\x61ndidateID\x18\x0c \x01(\x03R\x0b\x63\x61ndidateid\x12\x18\n\x07JobAdID\x18\r \x01(\x03R\x07jobadid\x12\x1b\n\x08LastName\x18\x02 \x01(\tR\tlast_name\x12\x1d\n\tFirstName\x18\x03 \x01(\tR\nfirst_name\x12\x14\n\x05\x45mail\x18\x04 \x01(\tR\x05\x65mail\x12\x14\n\x05Phone\x18\x05 \x01(\tR\x05phone\x12\x14\n\x08Language\x18\x06 \x01(\tR\x02lg\x12\x30\n\x06Gender\x18\x07 \x01(\x0e\x32\x18.grpc.weladee.com.GenderR\x06gender\x12;\n\x06Status\x18\t \x01(\x0e\x32#.grpc.weladee.com.ApplicationStatusR\x06status\x12\x1c\n\tTimestamp\x18\x0f \x01(\x03R\ttimestamp\x12\x12\n\x04Note\x18\x10 \x01(\tR\x04note\x12\x1a\n\x08Position\x18\x14 \x01(\tR\x08position\x12\x14\n\x05Title\x18\x15 \x01(\tR\x05title\x12\x30\n\x12LinkedInProfileURL\x18\n \x01(\tR\x14linkedin_profile_url\"N\n\x0eSiteMapRequest\x12\x16\n\x06Offset\x18\t \x01(\x03R\x06offset\x12\x14\n\x05Limit\x18\n \x01(\x03R\x05limit\x12\x0e\n\x02Lg\x18\x0b \x01(\tR\x02lg\"Q\n\nURLSitemap\x12\x19\n\x07URLName\x18\x01 \x01(\tR\x08url_name\x12\x0e\n\x02lg\x18\x02 \x01(\tR\x02lg\x12\x18\n\x07\x43\x61ption\x18\x03 \x01(\tR\x07\x63\x61ption\"T\n\nRelatedJob\x12\x0e\n\x02ID\x18\x01 \x01(\x03R\x02id\x12\x1a\n\x08Position\x18\x14 \x01(\tR\x08position\x12\x1a\n\x07URLName\x18\x82\x01 \x01(\tR\x08url_name\"\xbf\x0c\n\x05JobAd\x12\x0e\n\x02ID\x18\x01 \x01(\x03R\x02id\x12\x17\n\x06\x41geMin\x18\x02 \x01(\x05R\x07min_age\x12\x17\n\x06\x41geMax\x18\x03 \x01(\x05R\x07max_age\x12\x37\n\tMinDegree\x18\x04 \x01(\x0e\x32\x18.grpc.weladee.com.DegreeR\nmin_degree\x12\x14\n\x05Title\x18\x05 \x01(\tR\x05title\x12\x43\n\x0c\x43ontractType\x18\x06 \x01(\x0e\x32\x1e.grpc.weladee.com.ContractTypeR\rcontract_type\x12\x30\n\x06Gender\x18\x07 \x01(\x0e\x32\x18.grpc.weladee.com.GenderR\x06gender\x12\x1e\n\nExperience\x18\x08 \x01(\tR\nexperience\x12 \n\x0b\x44\x65scription\x18\n \x01(\tR\x0b\x64\x65scription\x12\x15\n\x06Skills\x18\x0b \x01(\tR\x05skill\x12\x19\n\x08\x42\x65nefits\x18\x0c \x01(\tR\x07\x62\x65nefit\x12\x16\n\x06Salary\x18\r \x01(\tR\x06salary\x12(\n\x10Responsabilities\x18\x0e \x01(\tR\x0eresponsability\x12\x12\n\x04Note\x18\x0f \x01(\tR\x04note\x12\x1c\n\tPublished\x18\x10 \x01(\x08R\tpublished\x12\x0e\n\x02lg\x18\x11 \x01(\tR\x02lg\x12\x1a\n\x08Position\x18\x14 \x01(\tR\x08position\x12\x1a\n\x08Location\x18\x15 \x01(\tR\x08location\x12\x1c\n\tDocuments\x18\x16 \x01(\tR\tdocuments\x12\x1b\n\x08\x46ormsURL\x18\x19 \x01(\tR\tforms_url\x12!\n\x0bPublishDate\x18\x1e \x01(\x03R\x0cpublish_date\x12\x1f\n\nExpireDate\x18\x1f \x01(\x03R\x0b\x65xpire_date\x12!\n\x0b\x43ompanyName\x18\x64 \x01(\tR\x0c\x63ompany_name\x12!\n\x0b\x43ompanyLogo\x18\x65 \x01(\tR\x0c\x63ompany_logo\x12#\n\x0c\x43ompanyAbout\x18\x66 \x01(\tR\rcompany_about\x12\'\n\x0e\x43ompanyAddress\x18g \x01(\tR\x0f\x63ompany_address\x12*\n\x0f\x43ompanyPostcode\x18h \x01(\tR\x11\x63ompany_post_code\x12!\n\x0b\x43ompanyCity\x18i \x01(\tR\x0c\x63ompany_city\x12)\n\x0f\x43ompanyLatitude\x18\x17 \x01(\x01R\x10\x63ompany_latitude\x12+\n\x10\x43ompanyLongitude\x18\x18 \x01(\x01R\x11\x63ompany_longitude\x12#\n\x0c\x43ompanyEmail\x18j \x01(\tR\rcompany_email\x12#\n\x0c\x43ompanyPhone\x18k \x01(\tR\rcompany_phone\x12#\n\nCompanyURL\x18l \x01(\tR\x0f\x63ompany_website\x12\'\n\x0e\x43ompanyCountry\x18m \x01(\tR\x0f\x63ompany_country\x12)\n\x0f\x43ompanyTelegram\x18w \x01(\tR\x10\x63ompany_telegram\x12\'\n\x0e\x43ompanyTwitter\x18x \x01(\tR\x0f\x63ompany_twitter\x12)\n\x0f\x43ompanyFacebook\x18y \x01(\tR\x10\x63ompany_facebook\x12!\n\x0b\x43ompanyLine\x18z \x01(\tR\x0c\x63ompany_line\x12)\n\x0f\x43ompanyLinkedin\x18{ \x01(\tR\x10\x63ompany_linkedin\x12\x1c\n\tCompanyID\x18| \x01(\x03R\tcompanyid\x12\x1a\n\x07URLName\x18\x82\x01 \x01(\tR\x08url_name\x12$\n\x0c\x45xternalName\x18\x86\x01 \x01(\tR\rexternal_name\x12\"\n\x0b\x45xternalURL\x18\x87\x01 \x01(\tR\x0c\x65xternal_url\x12\x19\n\x07TweetID\x18\x96\x01 \x01(\tR\x07tweetid\x12@\n\x0bRelatedJobs\x18\xc8\x01 \x03(\x0b\x32\x1c.grpc.weladee.com.RelatedJobR\x0crelated_jobs\"\xd1\x03\n\nJobRequest\x12\x0e\n\x02ID\x18\x01 \x01(\x03R\x02id\x12\x1a\n\x08\x46reeText\x18\x02 \x01(\tR\x08\x66reetext\x12\x37\n\tPublished\x18\x03 \x01(\x0e\x32\x19.grpc.weladee.com.TrinaryR\tpublished\x12\x19\n\x07URLName\x18\x1e \x01(\tR\x08url_name\x12\x38\n\tOnlineNow\x18\x1f \x01(\x0e\x32\x19.grpc.weladee.com.TrinaryR\nonline_now\x12!\n\x0b\x43ompanyName\x18\x15 \x01(\tR\x0c\x63ompany_name\x12\x1a\n\x08Position\x18\x04 \x01(\tR\x08position\x12\x1c\n\tCompanyID\x18\x05 \x01(\x03R\tcompanyid\x12\x12\n\x04\x43ity\x18\x06 \x01(\tR\x04\x63ity\x12\x1b\n\x08PostCode\x18\x07 \x01(\tR\tpost_code\x12\x1f\n\nSimilarJob\x18\x08 \x01(\x03R\x0bsimilar_job\x12\x16\n\x06Offset\x18\t \x01(\x03R\x06offset\x12\x14\n\x05Limit\x18\n \x01(\x03R\x05limit\x12\x1a\n\x08Language\x18\x0b \x01(\tR\x08language\x12\x10\n\x03XLS\x18\x0c \x01(\x08R\x03xls\"\xbd\x03\n\x0bJobSettings\x12\x14\n\x05\x41\x62out\x18\x01 \x01(\tR\x05\x61\x62out\x12\x14\n\x05Phone\x18\x02 \x01(\tR\x05phone\x12\x14\n\x05\x45mail\x18\x03 \x01(\tR\x05\x65mail\x12\x18\n\x07\x41\x64\x64ress\x18\x04 \x01(\tR\x07\x61\x64\x64ress\x12\x18\n\x07\x43ountry\x18\x06 \x01(\tR\x07\x63ountry\x12\x12\n\x04\x43ity\x18\x07 \x01(\tR\x04\x63ity\x12\x1b\n\x08PostCode\x18\x08 \x01(\tR\tpost_code\x12\x14\n\x03URL\x18\x05 \x01(\tR\x07website\x12\x1a\n\x08Telegram\x18\t \x01(\tR\x08telegram\x12\x12\n\x04Line\x18\n \x01(\tR\x04line\x12\x1a\n\x08\x46\x61\x63\x65\x62ook\x18\x0b \x01(\tR\x08\x66\x61\x63\x65\x62ook\x12\x18\n\x07Twitter\x18\x0c \x01(\tR\x07twitter\x12\x1a\n\x08Linkedin\x18\r \x01(\tR\x08linkedin\x12\x14\n\x05\x46orms\x18\x0e \x01(\x08R\x05\x66orms\x12\x1f\n\nShowOnline\x18\x0f \x01(\x08R\x0bshow_online\x12\x1a\n\x08latitude\x18\x17 \x01(\x01R\x08latitude\x12\x1c\n\tlongitude\x18\x18 \x01(\x01R\tlongitude\"\xb3\x02\n\x15JobApplicationRequest\x12\x30\n\x06Gender\x18\x01 \x01(\x0e\x32\x18.grpc.weladee.com.GenderR\x06gender\x12\x0e\n\x02ID\x18\x02 \x01(\x03R\x02id\x12\x10\n\x03XLS\x18\x0c \x01(\x08R\x03xls\x12\x12\n\x04\x41\x64ID\x18\r \x01(\x03R\x04\x61\x64id\x12 \n\x0b\x43\x61ndidateID\x18\x0e \x01(\x03R\x0b\x63\x61ndidateid\x12\x1a\n\x08Position\x18\x14 \x01(\tR\x08position\x12\x37\n\tConfirmed\x18\x05 \x01(\x0e\x32\x19.grpc.weladee.com.TrinaryR\tconfirmed\x12;\n\x06Status\x18\x07 \x01(\x0e\x32#.grpc.weladee.com.ApplicationStatusR\x06status*\x8f\x01\n\x11\x41pplicationStatus\x12\x12\n\x0e\x41pplicationNew\x10\x00\x12!\n\x1d\x41pplicationInterviewScheduled\x10\x01\x12\x16\n\x12\x41pplicationRefused\x10\x02\x12\x14\n\x10\x41pplicationHired\x10\x03\x12\x15\n\x11\x41pplicationOnHold\x10\x04*d\n\x0c\x43ontractType\x12\x0c\n\x08\x46ullTime\x10\x00\x12\x0c\n\x08PartTime\x10\x01\x12\r\n\tFreelance\x10\x02\x12\x0e\n\nInternship\x10\x03\x12\n\n\x06Remote\x10\x04\x12\r\n\tFixedTerm\x10\x05*H\n\x06\x44\x65gree\x12\x0c\n\x08NoDegree\x10\x00\x12\x0e\n\nVocational\x10\x01\x12\x0c\n\x08\x42\x61\x63helor\x10\x02\x12\n\n\x06Master\x10\x03\x12\x06\n\x02\x44r\x10\x04\x32\xd9\x01\n\x03Job\x12\x44\n\tGetJobAds\x12\x1c.grpc.weladee.com.JobRequest\x1a\x17.grpc.weladee.com.JobAd0\x01\x12N\n\nGetSiteMap\x12 .grpc.weladee.com.SiteMapRequest\x1a\x1c.grpc.weladee.com.URLSitemap0\x01\x12<\n\x05\x41pply\x12\x1a.grpc.weladee.com.ApplyJob\x1a\x17.grpc.weladee.com.EmptyB\x02H\x03\x62\x06proto3')

_APPLICATIONSTATUS = DESCRIPTOR.enum_types_by_name['ApplicationStatus']
ApplicationStatus = enum_type_wrapper.EnumTypeWrapper(_APPLICATIONSTATUS)
_CONTRACTTYPE = DESCRIPTOR.enum_types_by_name['ContractType']
ContractType = enum_type_wrapper.EnumTypeWrapper(_CONTRACTTYPE)
_DEGREE = DESCRIPTOR.enum_types_by_name['Degree']
Degree = enum_type_wrapper.EnumTypeWrapper(_DEGREE)
ApplicationNew = 0
ApplicationInterviewScheduled = 1
ApplicationRefused = 2
ApplicationHired = 3
ApplicationOnHold = 4
FullTime = 0
PartTime = 1
Freelance = 2
Internship = 3
Remote = 4
FixedTerm = 5
NoDegree = 0
Vocational = 1
Bachelor = 2
Master = 3
Dr = 4


_APPLYJOB = DESCRIPTOR.message_types_by_name['ApplyJob']
_CANDIDATE = DESCRIPTOR.message_types_by_name['Candidate']
_JOBAPPLICATION = DESCRIPTOR.message_types_by_name['JobApplication']
_SITEMAPREQUEST = DESCRIPTOR.message_types_by_name['SiteMapRequest']
_URLSITEMAP = DESCRIPTOR.message_types_by_name['URLSitemap']
_RELATEDJOB = DESCRIPTOR.message_types_by_name['RelatedJob']
_JOBAD = DESCRIPTOR.message_types_by_name['JobAd']
_JOBREQUEST = DESCRIPTOR.message_types_by_name['JobRequest']
_JOBSETTINGS = DESCRIPTOR.message_types_by_name['JobSettings']
_JOBAPPLICATIONREQUEST = DESCRIPTOR.message_types_by_name['JobApplicationRequest']
ApplyJob = _reflection.GeneratedProtocolMessageType('ApplyJob', (_message.Message,), {
  'DESCRIPTOR' : _APPLYJOB,
  '__module__' : 'job_pb2'
  # @@protoc_insertion_point(class_scope:grpc.weladee.com.ApplyJob)
  })
_sym_db.RegisterMessage(ApplyJob)

Candidate = _reflection.GeneratedProtocolMessageType('Candidate', (_message.Message,), {
  'DESCRIPTOR' : _CANDIDATE,
  '__module__' : 'job_pb2'
  # @@protoc_insertion_point(class_scope:grpc.weladee.com.Candidate)
  })
_sym_db.RegisterMessage(Candidate)

JobApplication = _reflection.GeneratedProtocolMessageType('JobApplication', (_message.Message,), {
  'DESCRIPTOR' : _JOBAPPLICATION,
  '__module__' : 'job_pb2'
  # @@protoc_insertion_point(class_scope:grpc.weladee.com.JobApplication)
  })
_sym_db.RegisterMessage(JobApplication)

SiteMapRequest = _reflection.GeneratedProtocolMessageType('SiteMapRequest', (_message.Message,), {
  'DESCRIPTOR' : _SITEMAPREQUEST,
  '__module__' : 'job_pb2'
  # @@protoc_insertion_point(class_scope:grpc.weladee.com.SiteMapRequest)
  })
_sym_db.RegisterMessage(SiteMapRequest)

URLSitemap = _reflection.GeneratedProtocolMessageType('URLSitemap', (_message.Message,), {
  'DESCRIPTOR' : _URLSITEMAP,
  '__module__' : 'job_pb2'
  # @@protoc_insertion_point(class_scope:grpc.weladee.com.URLSitemap)
  })
_sym_db.RegisterMessage(URLSitemap)

RelatedJob = _reflection.GeneratedProtocolMessageType('RelatedJob', (_message.Message,), {
  'DESCRIPTOR' : _RELATEDJOB,
  '__module__' : 'job_pb2'
  # @@protoc_insertion_point(class_scope:grpc.weladee.com.RelatedJob)
  })
_sym_db.RegisterMessage(RelatedJob)

JobAd = _reflection.GeneratedProtocolMessageType('JobAd', (_message.Message,), {
  'DESCRIPTOR' : _JOBAD,
  '__module__' : 'job_pb2'
  # @@protoc_insertion_point(class_scope:grpc.weladee.com.JobAd)
  })
_sym_db.RegisterMessage(JobAd)

JobRequest = _reflection.GeneratedProtocolMessageType('JobRequest', (_message.Message,), {
  'DESCRIPTOR' : _JOBREQUEST,
  '__module__' : 'job_pb2'
  # @@protoc_insertion_point(class_scope:grpc.weladee.com.JobRequest)
  })
_sym_db.RegisterMessage(JobRequest)

JobSettings = _reflection.GeneratedProtocolMessageType('JobSettings', (_message.Message,), {
  'DESCRIPTOR' : _JOBSETTINGS,
  '__module__' : 'job_pb2'
  # @@protoc_insertion_point(class_scope:grpc.weladee.com.JobSettings)
  })
_sym_db.RegisterMessage(JobSettings)

JobApplicationRequest = _reflection.GeneratedProtocolMessageType('JobApplicationRequest', (_message.Message,), {
  'DESCRIPTOR' : _JOBAPPLICATIONREQUEST,
  '__module__' : 'job_pb2'
  # @@protoc_insertion_point(class_scope:grpc.weladee.com.JobApplicationRequest)
  })
_sym_db.RegisterMessage(JobApplicationRequest)

_JOB = DESCRIPTOR.services_by_name['Job']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'H\003'
  _APPLICATIONSTATUS._serialized_start=3983
  _APPLICATIONSTATUS._serialized_end=4126
  _CONTRACTTYPE._serialized_start=4128
  _CONTRACTTYPE._serialized_end=4228
  _DEGREE._serialized_start=4230
  _DEGREE._serialized_end=4302
  _APPLYJOB._serialized_start=46
  _APPLYJOB._serialized_end=165
  _CANDIDATE._serialized_start=168
  _CANDIDATE._serialized_end=421
  _JOBAPPLICATION._serialized_start=424
  _JOBAPPLICATION._serialized_end=903
  _SITEMAPREQUEST._serialized_start=905
  _SITEMAPREQUEST._serialized_end=983
  _URLSITEMAP._serialized_start=985
  _URLSITEMAP._serialized_end=1066
  _RELATEDJOB._serialized_start=1068
  _RELATEDJOB._serialized_end=1152
  _JOBAD._serialized_start=1155
  _JOBAD._serialized_end=2754
  _JOBREQUEST._serialized_start=2757
  _JOBREQUEST._serialized_end=3222
  _JOBSETTINGS._serialized_start=3225
  _JOBSETTINGS._serialized_end=3670
  _JOBAPPLICATIONREQUEST._serialized_start=3673
  _JOBAPPLICATIONREQUEST._serialized_end=3980
  _JOB._serialized_start=4305
  _JOB._serialized_end=4522
# @@protoc_insertion_point(module_scope)
