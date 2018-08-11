Shared Secret Fragments for $label
==================================
Created: $timestamp
This directory contains shared secret fragments for distribution. The fragments can be safely shared - they cannot be used individually to rebuild the original secret.
Sharing distributed secrets is a good way to safeguard important data. Re-assembling distributed secret shares allows the originator to recover the original secret.

Storing these files in one place is a security vulnerability.

To securely delete them in a Linux environment:

```
# Move into the directory
cd /path/to/shares

# Securely shred:
find . -type f -exec shred -vfzu {} +
```
