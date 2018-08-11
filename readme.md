Share Secrets
=============
A Python 3 wrapper for the [debian ssss package][1] implementation of [Shamir's Secret Sharing Scheme][2].

To split a secret, run `./split.py`. This runs an interactive terminal session that configures and runs `ssss`.

The output shares are stored as individual files, each with a suitable descriptive introduction. This eases the process of creating and distributing your secret shares.

You will be provided with an option to securely delete the share files as part of the splitting process - you should copy and distribute the files separately before shredding. Secure deletion uses the GNU `shred` utility. If you want to shred the share files at a later stage, use the command:

```
shred -vfzu filename.txt

# Alternatively, shred all files in a directory:
# MAKE SURE YOU'RE IN THE RIGHT DIRECTORY!
cd /path/to/shares
find . -type f -exec shred -vfzu {} +
```
If you're in a Tails session, you can use the "Wipe" utility in the Nautilus (GUI) file manager.

## Configuration
Save `sample-config.json` as `config.json` and enter your personal details.

Each share file will contain your name and an email address as specified in the config - this may make it easier to recover secret shares. The file also contains instructions for the share holder.

## Rebuild
To rebuild, just run `ssss-combine` on the command line. Pass the required threshold number of the generated shares (in any order) to:
```
# For example, if the threshold is 3
ssss-combine -t 3
```

Useful Resources
----------------
Generate printable password:

```sh
# Generate a pseudo random 44 printable character password
# Note that a 32 byte input resolves to 44 base64 encoded characters
head -c 32 /dev/random | base64

# Generate printable password, alnum + punctuation
tr -dc '[:alnum:][:punct:]' < /dev/urandom | head -c 32 ; echo
```

## References
>Shamir's Secret Sharing is defined with Lagrange's polynomials, precisely: there is a unique polynomial of degree at most t-1 which goes through t given points, and it is rebuilt as a linear combinations of Lagrange's polynomials. When the secret is shared, a random polynomial P of degree at most t-1 is generated, such that P(0) is the secret. Then user i receives share P(i). Any t shares are enough to rebuild P and recompute P(0)
>
> [Tom Leek in SO comment][12]

* [ssss][1] - C implementation, present by default in standard Tails installation
* [Shamir's Secret Sharing][2] - an overview, with sample Python code
* [Shred][3] - securely delete shares on a *nix system
* [Python gfshare package][4]
* [Description of python-gfshare][5]
* [libgfshare source package in Ubuntu][6] - C implementation
* [libgfshare man page][8]
* [Blockstack secret sharing][7] - python implementation
* [Interesting fork of libgfshare][9]
* [Secret Sharing Made Short][10](Hugo Krawczyk, 2001)
* [Issues with SSSS Package][11]

[1]: http://point-at-infinity.org/ssss/
[2]: https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing
[3]: https://manpages.debian.org/jessie/coreutils/shred.1.en.html
[4]: https://lamby.github.io/python-gfshare/
[5]: https://chris-lamb.co.uk/projects/python-gfshare
[6]: https://launchpad.net/ubuntu/+source/libgfshare/1.0.5-3
[7]: https://github.com/blockstack/secret-sharing
[8]: http://manpages.ubuntu.com/manpages/xenial/en/man7/gfshare.7.html
[9]: https://github.com/jcushman/libgfshare
[10]: https://link.springer.com/chapter/10.1007%2F3-540-48329-2_12
[11]: https://security.stackexchange.com/a/83924/58780
[12]: https://security.stackexchange.com/a/49311/58780
