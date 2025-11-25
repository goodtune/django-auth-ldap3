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
Base adapter interface for LDAP backends.

This module defines the abstract interface that all LDAP backend adapters must
implement. The adapter provides a common API that wraps different LDAP libraries
(python-ldap, ldap3, etc.) to provide a unified interface for the django-auth-ldap
authentication backend.
"""

from abc import ABC, abstractmethod


class LDAPConnection(ABC):
    """
    Abstract base class for LDAP connection objects.

    This wraps an LDAP connection and provides a unified interface for
    common LDAP operations like bind, search, compare, etc.
    """

    @abstractmethod
    def simple_bind_s(self, who, cred):
        """
        Synchronous simple bind to the LDAP server.

        Args:
            who: The distinguished name (DN) to bind as
            cred: The password/credentials

        Raises:
            INVALID_CREDENTIALS: If the credentials are incorrect
            LDAPError: For other LDAP errors
        """
        pass

    @abstractmethod
    def search_s(self, base, scope, filterstr="(objectClass=*)", attrlist=None):
        """
        Synchronous search operation.

        Args:
            base: The base DN for the search
            scope: The search scope (SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE)
            filterstr: The LDAP filter string
            attrlist: List of attributes to retrieve (None = all)

        Returns:
            A list of (dn, attrs) tuples
        """
        pass

    @abstractmethod
    def search(self, base, scope, filterstr="(objectClass=*)", attrlist=None):
        """
        Asynchronous search operation.

        Args:
            base: The base DN for the search
            scope: The search scope
            filterstr: The LDAP filter string
            attrlist: List of attributes to retrieve

        Returns:
            A message ID to be used with result()
        """
        pass

    @abstractmethod
    def result(self, msgid, all=1, timeout=None):
        """
        Get the result of an asynchronous operation.

        Args:
            msgid: The message ID from the async operation
            all: Whether to return all results
            timeout: Optional timeout

        Returns:
            A tuple of (result_type, result_data)
        """
        pass

    @abstractmethod
    def compare_s(self, dn, attr, value):
        """
        Synchronous compare operation.

        Args:
            dn: The DN of the entry to compare
            attr: The attribute to compare
            value: The value to compare against

        Returns:
            True if the values match, False otherwise
        """
        pass

    @abstractmethod
    def set_option(self, option, value):
        """
        Set an LDAP connection option.

        Args:
            option: The option constant
            value: The value to set
        """
        pass

    @abstractmethod
    def get_option(self, option):
        """
        Get an LDAP connection option value.

        Args:
            option: The option constant

        Returns:
            The option value
        """
        pass

    @abstractmethod
    def start_tls_s(self):
        """
        Start TLS on the connection (STARTTLS).
        """
        pass

    @abstractmethod
    def unbind_s(self):
        """
        Unbind from the LDAP server and close the connection.
        """
        pass


class DNModule(ABC):
    """
    Abstract interface for DN manipulation utilities.
    """

    @staticmethod
    @abstractmethod
    def escape_dn_chars(s):
        """
        Escape special characters for use in a DN.

        Args:
            s: The string to escape

        Returns:
            The escaped string
        """
        pass


class FilterModule(ABC):
    """
    Abstract interface for LDAP filter utilities.
    """

    @staticmethod
    @abstractmethod
    def escape_filter_chars(s, escape_mode=0):
        """
        Escape special characters for use in an LDAP filter.

        Args:
            s: The string to escape
            escape_mode: Mode for escaping (0 = standard)

        Returns:
            The escaped string
        """
        pass


class CIDictModule(ABC):
    """
    Abstract interface for case-insensitive dictionary.
    """

    @staticmethod
    @abstractmethod
    def cidict():
        """
        Create a new case-insensitive dictionary.

        Returns:
            A case-insensitive dict instance
        """
        pass


class BaseLDAPAdapter(ABC):
    """
    Abstract base class for LDAP backend adapters.

    Implementations of this class wrap different LDAP libraries and provide
    a unified interface for django-auth-ldap.
    """

    # LDAP search scope constants
    SCOPE_BASE = 0
    SCOPE_ONELEVEL = 1
    SCOPE_SUBTREE = 2

    # LDAP option constants
    OPT_REFERRALS = 8
    OPT_X_TLS_REQUIRE_CERT = 24582
    OPT_X_TLS_CACERTFILE = 24578
    OPT_X_TLS_NEWCTX = 24591

    # LDAP result type constants
    RES_SEARCH_ENTRY = 100
    RES_SEARCH_RESULT = 101

    # DN utilities
    dn = None  # type: DNModule

    # Filter utilities
    filter = None  # type: FilterModule

    # Case-insensitive dict utilities
    cidict = None  # type: CIDictModule

    # Exceptions
    LDAPError = Exception

    # Specific exceptions subclassed from LDAPError
    INVALID_CREDENTIALS = Exception
    NO_SUCH_OBJECT = Exception
    NO_SUCH_ATTRIBUTE = Exception
    UNDEFINED_TYPE = Exception

    @abstractmethod
    def initialize(self, uri, bytes_mode=False):
        """
        Initialize a connection to an LDAP server.

        Args:
            uri: The LDAP URI (e.g., 'ldap://localhost')
            bytes_mode: Whether to use bytes mode (should be False)

        Returns:
            An LDAPConnection instance
        """
        pass

    def set_option(self, option, value):
        """
        Set a global LDAP option.

        Args:
            option: The option constant
            value: The value to set
        """
        pass
