# Netune on winget

`winget install DataAsh.Netune` is the route with no Windows notice and
nothing to install first. winget is Microsoft's own package manager, on every
Windows 11 and installable on Windows 10; it downloads Netune's Setup.exe,
**checks the SHA-256 itself** — which is why SmartScreen has nothing to say —
and runs it. `winget uninstall DataAsh.Netune` takes it away again through
the same uninstaller Settings › Apps uses.

## The three files here are generated, not written

`package.py --site C:\Projects\dataash` writes them from the same manifest
that produced the build, so the checksum in `DataAsh.Netune.installer.yaml`
is the checksum of the file that was actually uploaded. Copying a hash by
hand is how a submission gets rejected, so nobody copies one by hand.

Regenerate after every release. Never edit them.

## Checking them before submitting

```powershell
winget validate --manifest C:\Projects\dataash\winget
```

That is the same validator Microsoft's bot runs. To go further and install
from these files locally, an administrator has to switch local manifests on
once:

```powershell
winget settings --enable LocalManifestFiles     # in an elevated PowerShell
winget install --manifest C:\Projects\dataash\winget
```

## Submitting a version

winget's index is a public repository, so publishing is a pull request.

1. Fork <https://github.com/microsoft/winget-pkgs>.
2. Copy the three `.yaml` files here into your fork at
   `manifests/d/DataAsh/Netune/<version>/` — the path is case-sensitive and
   must match `PackageIdentifier`.
3. Commit on a branch named for the version, push, and open a pull request
   against `microsoft/winget-pkgs`.
4. A bot validates the manifest, downloads the installer, checks the hash and
   scans it. If it is happy and a moderator agrees, it merges, and
   `winget install DataAsh.Netune` works for everyone within a few hours.

The first submission is the slow one, because a human looks at a publisher
nobody has seen before. Later versions are usually automatic.

`wingetcreate submit` can do steps 1–3 for you if you would rather not touch
a fork by hand:

```powershell
winget install Microsoft.WingetCreate
wingetcreate submit --token <a GitHub token with public_repo> C:\Projects\dataash\winget
```

## Do not put the command on the website until it is merged

`winget install DataAsh.Netune` fails with "No package found" until the pull
request lands. Add it to `netune-free-beta.html` after, not before.

## What each file is for

| File | What it carries |
|---|---|
| `DataAsh.Netune.yaml` | the version, and which locale is the default |
| `DataAsh.Netune.installer.yaml` | the download URL, its SHA-256, the installer type and the ProductCode `winget uninstall` matches on |
| `DataAsh.Netune.locale.en-US.yaml` | the name, publisher, description and tags people search |

`ProductCode` must stay equal to the `AppId` in `package.py`'s Inno script
with `_is1` on the end — that is the key Inno writes into Add/Remove
Programs, and how winget recognises an installed copy. Change one and change
the other.
