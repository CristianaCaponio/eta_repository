from mongoengine import Document, DictField

class JsonCollectionTest(Document):
    response_data = DictField(required=True)
    meta = {'collection': 'json_collection_test'} 

# class RouteSummary(EmbeddedDocument):
#     lengthInMeters = fields.IntField(required=True)
#     travelTimeInSeconds = fields.IntField(required=True)
#     trafficDelayInSeconds = fields.IntField(required=True)
#     trafficLengthInMeters = fields.IntField(required=True)
#     startAddress = fields.StringField(required=True)
#     endAddress = fields.StringField(required=True)
#     departureTime = fields.DateTimeField(required=True)
#     arrivalTime = fields.DateTimeField(required=True)

# class LegSummary(EmbeddedDocument):
#     lengthInMeters = fields.IntField(required=True)
#     travelTimeInSeconds = fields.IntField(required=True)
#     trafficDelayInSeconds = fields.IntField(required=True)
#     trafficLengthInMeters = fields.IntField(required=True)
#     departureAddress = fields.StringField(required=True)
#     arrivalAddress = fields.StringField(required=True)
#     departureTime = fields.DateTimeField(required=True)
#     arrivalTime = fields.DateTimeField(required=True)

# class Leg(EmbeddedDocument):
#     summary = fields.EmbeddedDocumentField(LegSummary)

# class Section(EmbeddedDocument):
#     startPointIndex = fields.IntField(required=True)
#     endPointIndex = fields.IntField(required=True)
#     sectionType = fields.StringField(required=True)
#     travelMode = fields.StringField(required=True)

# class Route(EmbeddedDocument):
#     summary = fields.EmbeddedDocumentField(RouteSummary)
#     legs = fields.ListField(fields.EmbeddedDocumentField(Leg))
#     sections = fields.ListField(fields.EmbeddedDocumentField(Section))

# class TomTomResponse(Document):
#     formatVersion = fields.StringField(required=True)
#     routes = fields.ListField(fields.EmbeddedDocumentField(Route))
# from mongoengine import Document, EmbeddedDocument, StringField, IntField, ListField, EmbeddedDocumentField

# # Define the structure for RouteSummary
# class RouteSummary(EmbeddedDocument):
#     lengthInMeters = IntField()
#     travelTimeInSeconds = IntField()
#     trafficDelayInSeconds = IntField()
#     trafficLengthInMeters = IntField()
#     startAddress = StringField()
#     endAddress = StringField()
#     departureTime = StringField()
#     arrivalTime = StringField()

# # Define the structure for LegSummary
# class LegSummary(EmbeddedDocument):
#     lengthInMeters = IntField()
#     travelTimeInSeconds = IntField()
#     trafficDelayInSeconds = IntField()
#     trafficLengthInMeters = IntField()
#     departureAddress = StringField()
#     arrivalAddress = StringField()
#     departureTime = StringField()
#     arrivalTime = StringField()

# # Define the structure for Leg
# class Leg(EmbeddedDocument):
#     summary = EmbeddedDocumentField(LegSummary)

# # Define the structure for Section
# class Section(EmbeddedDocument):
#     startPointIndex = IntField()
#     endPointIndex = IntField()
#     sectionType = StringField()
#     travelMode = StringField()

# # Define the structure for Route
# class Route(EmbeddedDocument):
#     summary = EmbeddedDocumentField(RouteSummary)
#     legs = ListField(EmbeddedDocumentField(Leg))
#     sections = ListField(EmbeddedDocumentField(Section))

# # Define the main TomTomResponse structure
# class TomTomResponse(Document):
#     formatVersion = StringField()
#     routes = ListField(EmbeddedDocumentField(Route))
       
#     meta = {
#         'collection': 'json_collection_test'  
#     }
