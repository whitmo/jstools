import pkg_resources
DIST = pkg_resources.get_distribution(__name__)
REQ = pkg_resources.Requirement.parse(__name__)
