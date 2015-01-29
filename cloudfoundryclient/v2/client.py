# Copyright (c) 2015 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import requests

from cloudfoundryclient.common import exceptions


class Client(object):
    """Client to interface with Cloudfoundry.

        usage:
            from cloudfoundryclient.v2 import client
            cf_client = client.Client(username="foo@bar.com",
                                      password="BAAAAH")
            cf_client.login()
    """

    # user-agent
    USER_AGENT = "python-cloudfoundryclient"

    # urls
    info_url = '/v2/info'
    auth_token_url = '/oauth/token'
    organizations_url = '/v2/organizations'
    organization_space_url = '/v2/organizations/%s/spaces'
    organization_summary_url = '/v2/organizations/%s/summary'
    organization_services_url = '/v2/organizations/%s/services'
    organization_space_quota_definitions_url = (
        '/v2/organizations/%s/space_quota_definitions')
    apps_space_url = '/v2/spaces/%s/apps'

    def __init__(self, username="", password="",
                 base_url="https://api.run.pivotal.io/"):
        self._base_url = base_url
        self._username = username
        self._password = password
        self._server_api_info = self.get_info()
        self._auth_data = None

    def _get_headers(self):
        return {"Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": self.USER_AGENT}

    def get_info(self):
        r = requests.get(self._base_url + self.info_url)
        return r.json()

    def login(self):
        headers = self._get_headers()
        # A login request requires these special header values.
        headers["Authorization"] = "Basic Y2Y6"
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = (("grant_type=password&password=%(password)s"
                   "&scope=&username=%(username)s") %
                   {'password': self._password, 'username': self._username})
        url = self._server_api_info['token_endpoint'] + self.auth_token_url
        r = requests.post(url, data=payload, headers=headers)
        if r.status_code != requests.codes.ok:
            raise exceptions.LoginError(r.text)
        else:
            # stash response for other api calls.
            self._auth_data = r.json()
        return r.json()

    def logout(self):
        self._auth_data = None

    def _check_logged_in(self):
        if not self._auth_data:
            raise exceptions.NotLoggedIn

    def _generic_request_headers(self):
        self._check_logged_in()
        headers = self._get_headers()
        headers["Authorization"] = ("%s %s" %
                                    (self._auth_data['token_type'],
                                     self._auth_data['access_token']))
        return headers

    def get_organizations(self):
        """Return oranizations that a user is part of.

        An org consists of users grouped together for management purposes.
        All members of an org share a resource quota plan, services
        availability, and custom domains.
        """
        headers = self._generic_request_headers()
        url = self._base_url + self.organizations_url
        r = requests.get(url, headers=headers)
        return r.json()

    def get_organization_summary(self, guid):
        headers = self._generic_request_headers()
        url = self._base_url + (self.organization_summary_url % guid)
        r = requests.get(url, headers=headers)
        return r.json()

    def get_organization_spaces(self, guid):
        """Return list of all spaces for an organization

        param - guid: the guid of the organization.

        Every application and service is scoped to a space. Each org
        contains at least one space. A space provides a set of users
        access to a shared location for application development,
        deployment, and maintenance. Each space role applies only to
        a particular space.
        """

        headers = self._generic_request_headers()
        url = self._base_url + (self.organization_space_url % guid)
        r = requests.get(url, headers=headers)
        return r.json()

    def get_organization_services(self, guid):
        """Return list of all services for an organization

        param - guid: the guid of the organization.
        """
        headers = self._generic_request_headers()
        url = self._base_url + (self.organization_services_url % guid)
        r = requests.get(url, headers=headers)
        return r.json()

    def get_organization_space_quota_definitions(self, guid):
        """Return list of all space quota definiations

        param - guid: the guid of the organization.
        """
        headers = self._generic_request_headers()
        url = self._base_url + (
            self.organization_space_quota_definitions_url % guid)
        r = requests.get(url, headers=headers)
        return r.json()

    def get_apps_in_space(self, guid):
        """Return list of all space quota definiations

        param - guid: the guid of the organization.
        """
        headers = self._generic_request_headers()
        url = self._base_url + (
            self.apps_space_url % guid)
        r = requests.get(url, headers=headers)
        return r.json()
