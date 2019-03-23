from app.utils.env import env

MONGO_URI = env('MONGODB_URI')

IF_MATCH = False
PAGINATION_LIMIT = 5000
PAGINATION_DEFAULT = 5000

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST']  # DELETE

# Enable reads (GET), edits (PATCH) and deletes of individual items (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']  # PUT

# Client cache directives for all resources exposed
CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20

# Cross-Origin Resource Sharing (CORS) => '*'
X_DOMAINS = '*'
X_HEADERS = ['Authorization', 'Content-type']
X_ALLOW_CREDENTIALS = True

github_commits = {
    'schema': {
        'repository': {
            'type': 'string'
        },
        'commit_date': {
            'type': 'string',
        },
        'actor': {
            'type': 'string',
        },
        'sha': {
            'type': 'string',
        },
        'message': {
            'type': 'string',
        },
        'html_url': {
            'type': 'string',
        },
    }
}

github_events = {
    'schema': {

        'id': {
            'type': 'string',
        },
        'actor': {
            'type': 'string',
        },
        'type': {
            'actor': 'string',
        },
        'created_at': {
            'type': 'string',
        },
        'repo': {
            'type': 'string',
        },
        'repo_url': {
            'type': 'string',
        },
        'commits': {
            'type': 'string',
        },
        'commits_url': {
            'type': 'string',
        },
    }
}

github_repositories = {
    'schema': {

        'id': {
            'type': 'string',
        },
        'actor': {
            'actor': 'string',
        },
        'name': {
            'actor': 'string',
        },
        'display_name': {
            'type': 'string',
        },
        'private': {
            'type': 'string',
        },
        'owner': {
            'type': 'string',
        },
        'repo_url': {
            'type': 'string',
        },
        'commits': {
            'type': 'string',
        },
        'commits_url': {
            'type': 'string',
        },
        'labels_url': {
            'type': 'string',
        },
        'created_at': {
            'type': 'string',
        },
        'updated_at': {
            'type': 'string',
        },
    }
}

# Our API will expose two resources (MongoDB collections): 'people' and
# 'works'. In order to allow for proper data validation, we define beaviour
# and structure.
people = {
    # 'title' tag used in item links.
    'item_title': 'person',

    # by default the standard item entry point is defined as
    # '/people/<ObjectId>/'. We leave it untouched, and we also enable an
    # additional read-only entry point. This way consumers can also perform GET
    # requests at '/people/<lastname>/'.
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'lastname'
    },

    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/pyeve/cerberus) for details.
    'schema': {
        'firstname': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 10,
        },
        'lastname': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 15,
            'required': True,
            # talk about hard constraints! For the purpose of the demo
            # 'lastname' is an API entry-point, so we need it to be unique.
            'unique': True,
        },
        'middlename': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 15,
            'required': False,
            # talk about hard constraints! For the purpose of the demo
            # 'lastname' is an API entry-point, so we need it to be unique.
            'unique': False,
        },
        # 'role' is a list, and can only contain values from 'allowed'.
        'role': {
            'type': 'list',
            'allowed': ["author", "contributor", "copy"],
        },
        # An embedded 'strongly-typed' dictionary.
        'location': {
            'type': 'dict',
            'schema': {
                'address': {'type': 'string'},
                'city': {'type': 'string'}
            },
        },
        'born': {
            'type': 'datetime',
        },
    }
}

works = {
    # if 'item_title' is not provided Eve will just strip the final
    # 's' from resource name, and use it as the item_title.
    # 'item_title': 'work',

    # We choose to override global cache-control directives for this resource.
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,

    'schema': {
        'title': {
            'type': 'string',
            'required': True,
        },
        'description': {
            'type': 'string',
        },
        'owner': {
            'type': 'objectid',
            'required': True,
            # referential integrity constraint: value must exist in the
            # 'people' collection. Since we aren't declaring a 'field' key,
            # will default to `people._id` (or, more precisely, to whatever
            # ID_FIELD value is).
            'data_relation': {
                'resource': 'people',
                # make the owner embeddable with ?embedded={"owner":1}
                'embeddable': True
            },
        },
    }
}

# The DOMAIN dict explains which resources will be available and how they will
# be accessible to the API consumer.
DOMAIN = {
    'github_commits': github_commits,
    'github_events': github_events,
    'github_repositories': github_repositories
}
