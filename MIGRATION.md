# Migration Guide

This document describes how to migrate from previous versions of django-auth-ldap
to the new pluggable backend architecture.

## Overview

Starting with this release, django-auth-ldap supports multiple LDAP libraries
through a pluggable adapter architecture:

- **ldap3**: A pure Python LDAP library (no compilation required)
- **python-ldap**: The traditional C extension (requires OpenLDAP libraries)

## Breaking Changes

**Dependencies**: The package no longer requires `python-ldap` by default. You
must explicitly install the LDAP library you want to use.

## Migration Steps

### 1. Update Your Installation

If you're currently using `python-ldap` and want to continue using it:

```bash
pip install django-auth-ldap[openldap]
```

If you want to switch to `ldap3` (pure Python):

```bash
pip install django-auth-ldap[ldap3]
```

To install both for testing:

```bash
pip install django-auth-ldap[all]
```

### 2. Configure the Backend (Optional)

By default, django-auth-ldap uses `python-ldap` for backward compatibility. If
you want to use `ldap3` or want to be explicit about your choice, add the
following to your Django settings:

```python
# Use ldap3 (pure Python, recommended for Docker/containers)
AUTH_LDAP_BACKEND = 'django_auth_ldap.adapters.ldap3'

# Or use python-ldap (traditional, requires C extension)
AUTH_LDAP_BACKEND = 'django_auth_ldap.adapters.python_ldap'
```

### 3. Update Direct LDAP Imports (If Any)

If your code directly imports from `ldap`, you may need to update it to use
the adapter interface. However, most users who only use the django-auth-ldap
configuration settings will not need any changes.

**Before** (if you had custom code using ldap directly):
```python
import ldap

# Using ldap constants
scope = ldap.SCOPE_SUBTREE
```

**After** (using the adapter):
```python
from django_auth_ldap.config import _LDAPConfig

ldap_adapter = _LDAPConfig.get_ldap()
scope = ldap_adapter.SCOPE_SUBTREE
```

## Configuration Examples

### Short Form (Recommended)

```python
# Use ldap3
AUTH_LDAP_BACKEND = 'django_auth_ldap.adapters.ldap3'

# Use python-ldap
AUTH_LDAP_BACKEND = 'django_auth_ldap.adapters.python_ldap'
```

### Full Form

```python
# Use ldap3
AUTH_LDAP_BACKEND = 'django_auth_ldap.adapters.ldap3.Adapter'

# Use python-ldap
AUTH_LDAP_BACKEND = 'django_auth_ldap.adapters.python_ldap.Adapter'
```

### Custom Adapter

```python
# Use a custom adapter (must implement BaseLDAPAdapter)
AUTH_LDAP_BACKEND = 'myapp.ldap_adapter.MyCustomAdapter'
```

## Creating Custom Adapters

If you need to create a custom LDAP adapter (e.g., for a different LDAP library
or for testing), you can implement the `BaseLDAPAdapter` interface:

```python
from django_auth_ldap.adapters.base import BaseLDAPAdapter

class MyCustomAdapter(BaseLDAPAdapter):
    # Implement required methods and attributes
    # See adapters/base.py for the full interface
    pass
```

## Silencing the Configuration Warning

If you haven't explicitly set `AUTH_LDAP_BACKEND`, Django's system checks will
issue a warning (django_auth_ldap.W001). To silence this warning, either:

1. Explicitly set `AUTH_LDAP_BACKEND` in your settings:
   ```python
   AUTH_LDAP_BACKEND = 'django_auth_ldap.adapters.python_ldap'
   ```

2. Or add the check ID to `SILENCED_SYSTEM_CHECKS`:
   ```python
   SILENCED_SYSTEM_CHECKS = ['django_auth_ldap.W001']
   ```

## Compatibility Notes

### ldap3 vs python-ldap Differences

Both adapters provide the same interface, but there may be subtle differences
in behavior:

1. **Connection handling**: ldap3 uses different connection management than
   python-ldap. Most users won't notice any difference.

2. **TLS/SSL**: Both libraries support TLS, but configuration options may
   differ slightly.

3. **Error messages**: Exception messages may vary between libraries.

### Testing Both Adapters

If you want to ensure your configuration works with both adapters, you can
run your tests with each:

```python
from django.test import TestCase, override_settings

class MyLDAPTest(TestCase):
    @override_settings(AUTH_LDAP_BACKEND='django_auth_ldap.adapters.python_ldap')
    def test_with_python_ldap(self):
        # Your test code
        pass

    @override_settings(AUTH_LDAP_BACKEND='django_auth_ldap.adapters.ldap3')
    def test_with_ldap3(self):
        # Your test code
        pass
```

## Troubleshooting

### ImportError: Cannot import LDAP adapter

Make sure you've installed the required LDAP library:

```bash
# For python-ldap
pip install python-ldap

# For ldap3
pip install ldap3
```

### AttributeError: 'X' does not have attribute 'Y'

If you're using a custom adapter, ensure it implements all required methods
and attributes from `BaseLDAPAdapter`.

### Tests fail with one adapter but not the other

The adapters have been designed to provide identical behavior, but edge cases
may exist. Please report any inconsistencies as bugs.
