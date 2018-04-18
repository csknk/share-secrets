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
## Configuration
Save `sample-config.json` as `config.json` and enter your personal details.

Each share file will contain your name and an email address as specified in the config - this may make it easier to recover secret shares. The file also contains instructions for the share holder.

## References
* [ssss][1]
* [Shamir's Secret Sharing][2]
* [Shred][3]

[1]: http://point-at-infinity.org/ssss/
[2]: https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing
[3]: https://manpages.debian.org/jessie/coreutils/shred.1.en.html
