Shared Secret Fragment for $label
==================================
Created: $timestamp
Originator: $contactName
Email: $contactEmail
This shared secret fragment can be safely shared - it cannot be used on it's own to rebuild the original secret.
Sharing distributed secrets is a good way to safeguard important data. Re-assembling distributed secret shares
allows the originator to recover the original secret.

If requested, please return this file to the sender or their legal representative.

## Rebuild Instructions
Creation of shares by means of `ssss-split`: $report

To reconstruct the secret, pass n of the generated shares (in any order) to:
~~~
ssss-combine -t n
~~~
You can achieve this conveniently by running a Tails session in an offline computer -
the ssss package is installed in Tails by default.

Tails: (https://tails.boum.org/)[https://tails.boum.org/]

## Fragment
---
$fragment
---
