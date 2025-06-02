from flask import Blueprint

# We don't define a main blueprint here, as each route file will have its own.
# This file serves to import all blueprints so they are discoverable.
# The actual registration happens in ezpark/__init__.py