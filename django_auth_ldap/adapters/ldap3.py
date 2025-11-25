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
ldap3 adapter for django-auth-ldap.

This module provides an implementation of the BaseLDAPAdapter interface using
the ldap3 library (pure Python). This allows django-auth-ldap to work without
requiring the python-ldap C extension and OpenLDAP binaries.
"""

from urllib.parse import urlparse

import ldap3
from ldap3.core.exceptions import (
    LDAPException,
    LDAPInvalidCredentialsResult,
    LDAPNoSuchAttributeResult,
    LDAPNoSuchObjectResult,
    LDAPUndefinedAttributeTypeResult,
)
from ldap3.utils.dn import escape_rdn as _escape_rdn

from .base import BaseLDAPAdapter, LDAPConnection


class LDAPError(LDAPException):
    """Base exception for LDAP errors, compatible with python-ldap."""

    pass


class INVALID_CREDENTIALS(LDAPError):
    """Exception raised when credentials are invalid."""

    pass


class NO_SUCH_OBJECT(LDAPError):
    """Exception raised when the requested object doesn't exist."""

    pass


class NO_SUCH_ATTRIBUTE(LDAPError):
    """Exception raised when the requested attribute doesn't exist."""

    pass


class UNDEFINED_TYPE(LDAPError):
    """Exception raised when an attribute type is undefined in schema."""

    pass


class _LDAP3Connection(LDAPConnection):
    """
    LDAPConnection implementation using ldap3.

    This wraps an ldap3 Connection object and provides the interface expected
    by django-auth-ldap.
    """

    def __init__(self, server, conn):
        """
        Initialize the connection wrapper.

        Args:
            server: The ldap3 Server object
            conn: The ldap3 Connection object
        """
        self._server = server
        self._conn = conn
        self._options = {}
        self._async_results = {}
        self._async_counter = 0

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
        try:
            self._conn.rebind(user=who, password=cred)
            if not self._conn.bound:
                result = self._conn.result
                if result and result.get("description") == "invalidCredentials":
                    raise INVALID_CREDENTIALS({"desc": "Invalid credentials"})
                raise LDAPError({"desc": "Bind failed"})
        except LDAPInvalidCredentialsResult as e:
            raise INVALID_CREDENTIALS({"desc": str(e)}) from e
        except LDAPException as e:
            raise LDAPError({"desc": str(e)}) from e

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
        ldap3_scope = _convert_scope(scope)
        attrs = attrlist if attrlist else ldap3.ALL_ATTRIBUTES

        try:
            self._conn.search(
                search_base=base,
                search_filter=filterstr,
                search_scope=ldap3_scope,
                attributes=attrs,
            )
        except LDAPNoSuchObjectResult as e:
            raise NO_SUCH_OBJECT({"desc": str(e)}) from e
        except LDAPException as e:
            raise LDAPError({"desc": str(e)}) from e

        return _convert_entries(self._conn.entries)

    def search(self, base, scope, filterstr="(objectClass=*)", attrlist=None):
        """
        Asynchronous search operation.

        Note: ldap3 doesn't have true async, so we simulate it by storing
        results and returning a message ID.

        Args:
            base: The base DN for the search
            scope: The search scope
            filterstr: The LDAP filter string
            attrlist: List of attributes to retrieve

        Returns:
            A message ID to be used with result()
        """
        self._async_counter += 1
        msgid = self._async_counter

        try:
            results = self.search_s(base, scope, filterstr, attrlist)
            self._async_results[msgid] = (Adapter.RES_SEARCH_RESULT, results)
        except LDAPError as e:
            self._async_results[msgid] = (None, e)

        return msgid

    def result(self, msgid, all=1, timeout=None):
        """
        Get the result of an asynchronous operation.

        Args:
            msgid: The message ID from the async operation
            all: Whether to return all results
            timeout: Optional timeout (ignored in ldap3)

        Returns:
            A tuple of (result_type, result_data)
        """
        if msgid not in self._async_results:
            raise LDAPError({"desc": "Unknown message ID"})

        result_type, data = self._async_results.pop(msgid)
        if result_type is None:
            raise data  # Re-raise the stored exception
        return (result_type, data)

    def compare_s(self, dn, attr, value):
        """
        Synchronous compare operation.

        Args:
            dn: The DN of the entry to compare
            attr: The attribute to compare
            value: The value to compare against (bytes or str)

        Returns:
            True if the values match, False otherwise
        """
        if isinstance(value, bytes):
            value = value.decode("utf-8")

        try:
            result = self._conn.compare(dn, attr, value)
            return result
        except LDAPNoSuchObjectResult:
            return False
        except LDAPNoSuchAttributeResult:
            return False
        except LDAPUndefinedAttributeTypeResult:
            return False
        except LDAPException as e:
            raise LDAPError({"desc": str(e)}) from e

    def set_option(self, option, value):
        """
        Set an LDAP connection option.

        Args:
            option: The option constant
            value: The value to set
        """
        self._options[option] = value

    def get_option(self, option):
        """
        Get an LDAP connection option value.

        Args:
            option: The option constant

        Returns:
            The option value
        """
        return self._options.get(option)

    def start_tls_s(self):
        """
        Start TLS on the connection (STARTTLS).
        """
        try:
            self._conn.start_tls()
        except LDAPException as e:
            raise LDAPError({"desc": str(e)}) from e

    def unbind_s(self):
        """
        Unbind from the LDAP server and close the connection.
        """
        self._conn.unbind()


class Adapter(BaseLDAPAdapter):
    """
    ldap3-based LDAP adapter (pure Python).

    This adapter wraps the ldap3 library, providing a python-ldap compatible
    interface for django-auth-ldap.
    """

    # LDAP search scope constants
    SCOPE_BASE = ldap3.BASE
    SCOPE_ONELEVEL = ldap3.LEVEL
    SCOPE_SUBTREE = ldap3.SUBTREE

    # LDAP option constants - using same values as python-ldap for compatibility
    OPT_REFERRALS = 8
    OPT_X_TLS_REQUIRE_CERT = 24582
    OPT_X_TLS_CACERTFILE = 24578
    OPT_X_TLS_NEWCTX = 24591

    # LDAP result type constants
    RES_SEARCH_ENTRY = 100
    RES_SEARCH_RESULT = 101

    # Exceptions
    LDAPError = LDAPError
    INVALID_CREDENTIALS = INVALID_CREDENTIALS
    NO_SUCH_OBJECT = NO_SUCH_OBJECT
    NO_SUCH_ATTRIBUTE = NO_SUCH_ATTRIBUTE
    UNDEFINED_TYPE = UNDEFINED_TYPE

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
            bytes_mode: Whether to use bytes mode (ignored, always False in ldap3)

        Returns:
            An _LDAP3Connection instance
        """
        parsed = urlparse(uri)
        use_ssl = parsed.scheme == "ldaps"
        host = parsed.hostname
        port = parsed.port

        if port is None:
            port = 636 if use_ssl else 389

        server = ldap3.Server(host, port=port, use_ssl=use_ssl, get_info=ldap3.NONE)
        conn = ldap3.Connection(server, auto_bind=False, raise_exceptions=True)
        conn.bind()

        return _LDAP3Connection(server, conn)

    def set_option(self, option, value):
        """
        Set a global LDAP option.

        Note: ldap3 doesn't have global options in the same way as python-ldap.
        This is a no-op for compatibility.

        Args:
            option: The option constant
            value: The value to set
        """
        pass


def _convert_scope(scope):
    """
    Convert a scope constant to ldap3 scope.

    Args:
        scope: The scope constant (SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE)

    Returns:
        The ldap3 scope constant
    """
    if scope == Adapter.SCOPE_BASE or scope == ldap3.BASE:
        return ldap3.BASE
    elif scope == Adapter.SCOPE_ONELEVEL or scope == ldap3.LEVEL:
        return ldap3.LEVEL
    else:
        return ldap3.SUBTREE


def _convert_entries(entries):
    """
    Convert ldap3 Entry objects to python-ldap style tuples.

    Args:
        entries: A list of ldap3 Entry objects

    Returns:
        A list of (dn, attrs_dict) tuples
    """
    results = []
    for entry in entries:
        dn = entry.entry_dn
        attrs = {}
        for attr_name in entry.entry_attributes:
            attr_value = entry[attr_name]
            if hasattr(attr_value, "values"):
                attrs[attr_name] = list(attr_value.values)
            elif hasattr(attr_value, "value"):
                attrs[attr_name] = [attr_value.value] if attr_value.value else []
            else:
                attrs[attr_name] = []
        results.append((dn, attrs))
    return results


class _DNModule:
    """DN manipulation utilities for ldap3."""

    @staticmethod
    def escape_dn_chars(s):
        """
        Escape special characters for use in a DN.

        Args:
            s: The string to escape

        Returns:
            The escaped string
        """
        # ldap3's escape_rdn escapes for RDN values
        return _escape_rdn(s)


class _FilterModule:
    """LDAP filter utilities for ldap3."""

    @staticmethod
    def escape_filter_chars(s, escape_mode=0):
        """
        Escape special characters for use in an LDAP filter.

        According to RFC 4515, the following characters need to be escaped:
        * (0x2a) -> \\2a
        ( (0x28) -> \\28
        ) (0x29) -> \\29
        \\ (0x5c) -> \\5c
        NUL (0x00) -> \\00

        Args:
            s: The string to escape
            escape_mode: Mode for escaping (0 = standard)

        Returns:
            The escaped string
        """
        # Handle bytes input
        if isinstance(s, bytes):
            s = s.decode("utf-8")

        # Escape according to RFC 4515
        s = s.replace("\\", "\\5c")
        s = s.replace("*", "\\2a")
        s = s.replace("(", "\\28")
        s = s.replace(")", "\\29")
        s = s.replace("\x00", "\\00")

        return s


class CIDict(dict):
    """
    Case-insensitive dictionary for LDAP attribute names.

    LDAP attribute names are case-insensitive, so this dictionary
    normalizes keys to lowercase.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __delitem__(self, key):
        super().__delitem__(key.lower())

    def __contains__(self, key):
        return super().__contains__(key.lower())

    def get(self, key, default=None):
        return super().get(key.lower(), default)

    def pop(self, key, *args):
        return super().pop(key.lower(), *args)

    def setdefault(self, key, default=None):
        return super().setdefault(key.lower(), default)

    def update(self, *args, **kwargs):
        if args:
            other = args[0]
            if isinstance(other, dict):
                for key, value in other.items():
                    self[key] = value
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value


class _CIDictModule:
    """Case-insensitive dictionary utilities for ldap3."""

    @staticmethod
    def cidict():
        """
        Create a new case-insensitive dictionary.

        Returns:
            A CIDict instance
        """
        return CIDict()
