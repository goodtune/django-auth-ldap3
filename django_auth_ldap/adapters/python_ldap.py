# Copyright (c) 2009, Peter Sagerson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
python-ldap adapter for django-auth-ldap.

This module provides a thin wrapper around the python-ldap library, implementing
the BaseLDAPAdapter interface. This is essentially a pass-through to preserve
exact backward compatibility with the existing behavior.
"""

import ldap
import ldap.dn
import ldap.filter
from ldap import cidict as ldap_cidict

from .base import BaseLDAPAdapter


class Adapter(BaseLDAPAdapter):
    """
    python-ldap based LDAP adapter.

    This adapter wraps the python-ldap library, providing backward compatibility
    with the existing django-auth-ldap implementation.
    """

    # LDAP search scope constants - directly from python-ldap
    SCOPE_BASE = ldap.SCOPE_BASE
    SCOPE_ONELEVEL = ldap.SCOPE_ONELEVEL
    SCOPE_SUBTREE = ldap.SCOPE_SUBTREE

    # LDAP option constants - directly from python-ldap
    OPT_REFERRALS = ldap.OPT_REFERRALS
    OPT_X_TLS_REQUIRE_CERT = ldap.OPT_X_TLS_REQUIRE_CERT
    OPT_X_TLS_CACERTFILE = ldap.OPT_X_TLS_CACERTFILE
    OPT_X_TLS_NEWCTX = ldap.OPT_X_TLS_NEWCTX

    # LDAP result type constants
    RES_SEARCH_ENTRY = ldap.RES_SEARCH_ENTRY
    RES_SEARCH_RESULT = ldap.RES_SEARCH_RESULT

    # Exceptions - directly from python-ldap
    LDAPError = ldap.LDAPError
    INVALID_CREDENTIALS = ldap.INVALID_CREDENTIALS
    NO_SUCH_OBJECT = ldap.NO_SUCH_OBJECT
    NO_SUCH_ATTRIBUTE = ldap.NO_SUCH_ATTRIBUTE
    UNDEFINED_TYPE = ldap.UNDEFINED_TYPE

    def __init__(self):
        """Initialize the adapter with DN, filter, and cidict modules."""
        self.dn = _DNModule()
        self.filter = _FilterModule()
        self.cidict = _CIDictModule()

    def initialize(self, uri, bytes_mode=False):
        """
        Initialize a connection to an LDAP server.

        Args:
            uri: The LDAP URI (e.g., 'ldap://localhost')
            bytes_mode: Whether to use bytes mode (should be False)

        Returns:
            A python-ldap LDAPObject wrapped for consistent interface
        """
        return ldap.initialize(uri, bytes_mode=bytes_mode)

    def set_option(self, option, value):
        """
        Set a global LDAP option.

        Args:
            option: The option constant
            value: The value to set
        """
        ldap.set_option(option, value)


class _DNModule:
    """DN manipulation utilities using python-ldap."""

    @staticmethod
    def escape_dn_chars(s):
        """
        Escape special characters for use in a DN.

        Args:
            s: The string to escape

        Returns:
            The escaped string
        """
        return ldap.dn.escape_dn_chars(s)


class _FilterModule:
    """LDAP filter utilities using python-ldap."""

    @staticmethod
    def escape_filter_chars(s, escape_mode=0):
        """
        Escape special characters for use in an LDAP filter.

        Args:
            s: The string to escape
            escape_mode: Mode for escaping (0 = standard)

        Returns:
            The escaped string
        """
        return ldap.filter.escape_filter_chars(s, escape_mode)


class _CIDictModule:
    """Case-insensitive dictionary utilities using python-ldap."""

    @staticmethod
    def cidict():
        """
        Create a new case-insensitive dictionary.

        Returns:
            A python-ldap cidict instance
        """
        return ldap_cidict.cidict()
