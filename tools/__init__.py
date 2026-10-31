#########################################################################################
# Filename    : __init__.py
# description : Registry of the available sections, in the order they appear in the menu
#########################################################################################

from tools import audit, compute, container_engine, identity, monitoring, waf

SECTIONS = [identity, container_engine, compute, waf, monitoring, audit]
