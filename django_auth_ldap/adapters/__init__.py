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
LDAP adapter implementations for django-auth-ldap.

This package provides pluggable LDAP backend adapters that allow django-auth-ldap
to work with different LDAP libraries.

Available adapters:
    - django_auth_ldap.adapters.ldap3: Pure Python ldap3 library (default)
    - django_auth_ldap.adapters.python_ldap: Traditional python-ldap C extension

Configuration:
    Set AUTH_LDAP_BACKEND in your Django settings to choose an adapter:

    # Use ldap3 (pure Python, default)
    AUTH_LDAP_BACKEND = 'django_auth_ldap.adapters.ldap3'

    # Use python-ldap (requires C extension)
    AUTH_LDAP_BACKEND = 'django_auth_ldap.adapters.python_ldap'

Custom adapters must implement BaseLDAPAdapter and be named 'Adapter' in their
module, or use the full path: 'myapp.adapters.MyCustomAdapter'
"""

from .base import BaseLDAPAdapter, LDAPConnection

__all__ = ["BaseLDAPAdapter", "LDAPConnection"]
