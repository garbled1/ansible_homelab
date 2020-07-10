# -*- coding: utf-8 -*-

# Copyright: (c) 2019. Chris Mills <chris@discreet-its.co.uk>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
nb_lookup_lag.py

A lookup function designed to return lag data from the Netbox application
"""

from __future__ import absolute_import, division, print_function

from pprint import pformat

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.parsing.splitter import parse_kv, split_args
from ansible.utils.display import Display

import pynetbox

__metaclass__ = type

DOCUMENTATION = """
    lookup: nb_lookup_lag
    author: Tim Rightnour (@garbled1)
    version_added: "2.9"
    short_description: Queries and returns lag elements from Netbox
    description:
        - Queries Netbox via its API to return lag devices in a format
          that network modules expect
        - Result can be handed directly as config parameter to many
          modules, such as cisco.ios.ios_lag_interfaces
    options:
        _terms:
            description:
                - The name of a device in netbox
                - only operates on one term
            required: True
        lagname:
            description:
                - Find only lags whose name contain this string
                - Default is to return all lag devices
            required: False
        mode:
            description:
                - Set the mode string to a specific value
            required: False
            default: "active"
        api_endpoint:
            description:
                - The URL to the Netbox instance to query
            required: True
        token:
            description:
                - The API token created through Netbox
                - This may not be required depending on the Netbox setup.
            required: False
        validate_certs:
            description:
                - Whether or not to validate SSL of the NetBox instance
            required: False
            default: True
    requirements:
        - pynetbox
"""

EXAMPLES = """
tasks:
  # Set a fact
  - name: Gather the lags from a device
    set_fact:
      lagdata: '{{ query("nb_lookup_lag", "switchname", api_endpoint='http://localhost/', token='<redacted>') }}'
"""

RETURN = """
  _list:
    description:
      - list of composed dictionaries with key and value
    type: list
"""


def get_endpoint(netbox, term):
    """
    get_endpoint(netbox, term)
        netbox: a predefined pynetbox.api() pointing to a valid instance
                of Netbox
        term: the term passed to the lookup function upon which the api
              call will be identified
    """

    netbox_endpoint_map = {
        "interfaces": {"endpoint": netbox.dcim.interfaces},
    }

    return netbox_endpoint_map[term]["endpoint"]


class LookupModule(LookupBase):
    """
    LookupModule(LookupBase) is defined by Ansible
    """

    def run(self, terms, variables=None, **kwargs):

        netbox_api_token = kwargs.get("token")
        netbox_api_endpoint = kwargs.get("api_endpoint")
        netbox_ssl_verify = kwargs.get("validate_certs")
        netbox_private_key_file = kwargs.get("key_file")
        netbox_lagname_match = kwargs.get("lagname")
        netbox_lag_mode = kwargs.get("mode")

        if netbox_lag_mode is None:
            netbox_lag_mode = "active"

        if not isinstance(terms, list):
            terms = [terms]
        terms = terms[0]

        try:
            netbox = pynetbox.api(
                netbox_api_endpoint,
                token=netbox_api_token if netbox_api_token else None,
                ssl_verify=netbox_ssl_verify,
                private_key_file=netbox_private_key_file,
            )
        except FileNotFoundError:
            raise AnsibleError(
                "%s cannot be found. Please make sure file exists."
                % netbox_private_key_file
            )

        results = []

        endpoint = get_endpoint(netbox, "interfaces")

        Display().vvvv(
            u"Netbox lag lookup for %s to %s using token %s"
            % (terms, netbox_api_endpoint, netbox_api_token)
        )

        filter = {"device": terms}

        Display().vvvv("filter is %s" % filter)

        iface_results = {}
        for res in endpoint.filter(**filter):

            Display().vvvvv(pformat(dict(res)))

            key = dict(res)["id"]
            iface_results[key] = dict(res)

        Display().vvvvv(pformat(dict(iface_results)))

        laglist = {}
        for id in iface_results.keys():
            if iface_results[id]["lag"]:
                lagname = iface_results[id]["lag"]["name"]
                # check if we are filtering
                if (netbox_lagname_match is not None and
                        netbox_lagname_match not in lagname):
                    continue

                if lagname not in laglist:
                    laglist[lagname] = dict()
                laglist[lagname]["name"] = lagname
                if "members" not in laglist[lagname]:
                    laglist[lagname]["members"] = []
                laglist[lagname]["members"].append(
                    {
                        "member": iface_results[id]["name"],
                        "mode": netbox_lag_mode
                    }
                )
        Display().vvvv(pformat(dict(laglist)))

        for lag in laglist:
            results.append(laglist[lag])

        return results
