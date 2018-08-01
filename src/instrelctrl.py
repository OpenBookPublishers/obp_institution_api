import web
from api import *
from errors import *
from models import InstRelation

logger = logging.getLogger(__name__)

class InstRelationsController(object):
    """Handles Institution Relation queries"""

    @json_response
    @api_response
    def GET(self, name):
        """ Gets relationship between two uuids."""
        logger.debug("Query: %s" % (web.input()))

        institution_uuid_a   = web.input().get('institution_uuid_a')
        institution_uuid_b   = web.input().get('institution_uuid_b')
        if institution_uuid_a and institution_uuid_b:
            if institution_uuid_a == institution_uuid_b:
                raise Error(SAMEINST)
            results = InstRelation.get_from_uuids(institution_uuid_a,institution_uuid_b)
        else:
            results = InstRelation.get_all()

        if not results:
            raise Error(NORESULT)
        data = results_to_relations(results)
        return data

    @json_response
    @api_response
    def POST(self, name):
        """Inserts new relation."""
        data = json.loads(web.data())
        parent_inst_uuid = data.get('parent_inst_uuid')
        child_inst_uuid = data.get('child_inst_uuid')
        try:
            assert parent_inst_uuid and child_inst_uuid
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        relation = InstRelation(parent_inst_uuid,child_inst_uuid)
        relation.save()
        return [relation.__dict__]

    @json_response
    @api_response
    def PUT(self, name):
        raise Error(NOTALLOWED,msg="Try deleting or inserting instead.")

    @json_response
    @api_response
    def DELETE(self, name):
        """Deletes relation using both uuids."""
        parent_inst_uuid = web.input().get('parent_inst_uuid')
        child_inst_uuid = web.input().get('child_inst_uuid')
        try:
            assert parent_inst_uuid and child_inst_uuid
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        try:
            relation = InstRelation(parent_inst_uuid,child_inst_uuid)
            relation.delete()
        except:
            raise Error(NOTFOUND,msg="The relation does not exist.")
        return [relation.__dict__]
