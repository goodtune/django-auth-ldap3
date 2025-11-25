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
Django system checks for django-auth-ldap configuration.
"""

from django.conf import settings
from django.core.checks import Tags, Warning, register


@register(Tags.compatibility)
def check_ldap_backend_configured(app_configs, **kwargs):
    """
    Check if AUTH_LDAP_BACKEND is explicitly configured.

    This check warns users who haven't explicitly configured AUTH_LDAP_BACKEND,
    informing them about the available adapter options.
    """
    warnings = []

    if not hasattr(settings, "AUTH_LDAP_BACKEND"):
        warnings.append(
            Warning(
                "AUTH_LDAP_BACKEND is not configured",
                hint=(
                    "The LDAP backend will default to ldap3 (pure Python). "
                    "Set AUTH_LDAP_BACKEND explicitly to silence this warning. "
                    'For ldap3 (default): "django_auth_ldap.adapters.ldap3" '
                    'For python-ldap: "django_auth_ldap.adapters.python_ldap"'
                ),
                id="django_auth_ldap.W001",
            )
        )

    return warnings
