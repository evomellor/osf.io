import pytest
from nose.tools import *  # flake8: noqa
import json

import jwt
import jwe

from modularodm import Q

from tests.base import ApiTestCase
from tests.base import capture_signals
from osf_tests.factories import InstitutionFactory, UserFactory

from api.base import settings
from api.base.settings.defaults import API_BASE
from framework.auth import signals
from website.models import User


class TestInstitutionAuth(ApiTestCase):
    def setUp(self):
        super(TestInstitutionAuth, self).setUp()
        self.institution = InstitutionFactory()
        self.institution.save()
        self.url = '/{0}institutions/auth/'.format(API_BASE)

    def build_payload(self, username):
        data = {
            'provider': {
                'id': self.institution._id,
                'user': {
                    'middleNames': '',
                    'familyName': '',
                    'givenName': '',
                    'fullname': 'Fake User',
                    'suffix': '',
                    'username': username
                }
            }
        }
        return jwe.encrypt(jwt.encode({
            'sub': username,
            'data': json.dumps(data)
        }, settings.JWT_SECRET, algorithm='HS256'), settings.JWE_SECRET)

    def test_creates_user(self):
        username = 'hmoco@circle.edu'
        assert_equal(User.find(Q('username', 'eq', username)).count(), 0)

        with capture_signals() as mock_signals:
            res = self.app.post(self.url, self.build_payload(username))

        assert_equal(res.status_code, 204)
        assert_equal(mock_signals.signals_sent(), set([signals.user_confirmed]))

        user = User.find_one(Q('username', 'eq', username))

        assert_true(user)
        assert_in(self.institution, user.affiliated_institutions.all())

    def test_adds_institution(self):
        username = 'hmoco@circle.edu'

        user = UserFactory(username=username, fullname='Mr Moco')
        user.save()

        with capture_signals() as mock_signals:
            res = self.app.post(self.url, self.build_payload(username))

        assert_equal(res.status_code, 204)
        assert_equal(mock_signals.signals_sent(), set())

        user.reload()
        assert_in(self.institution, user.affiliated_institutions.all())

    def test_finds_user(self):
        username = 'hmoco@circle.edu'

        user = UserFactory(username=username, fullname='Mr Moco')
        user.affiliated_institutions.add(self.institution)
        user.save()

        res = self.app.post(self.url, self.build_payload(username))
        assert_equal(res.status_code, 204)

        user.reload()
        assert_equal(user.affiliated_institutions.count(), 1)

    def test_bad_token(self):
        res = self.app.post(self.url, 'al;kjasdfljadf', expect_errors=True)
        assert_equal(res.status_code, 403)
