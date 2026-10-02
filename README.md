🇬🇧 English (you're here) · 🇪🇸 [Español](READMEs/README.es.md)

# Instagram Checker

[![Tests](https://github.com/chiissuu/instagram-checker/actions/workflows/tests.yml/badge.svg)](https://github.com/chiissuu/instagram-checker/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Python script that compares your Instagram **followers** and **following** using the official export of your data, and generates a list of the people you follow who don't follow you back.

The core analysis runs **entirely locally**: the script only reads the JSON files you download from Instagram yourself. It can optionally connect to Instagram to check which of those accounts no longer exist (see [Optional online verification](#optional-online-verification-accounts-that-no-longer-exist)), but only if you explicitly ask for it each time.

Want to see it working without using your own data? Check the [`demo` branch](https://github.com/chiissuu/instagram-checker/tree/demo) — same tool, run against a synthetic (fake) export with no real accounts involved.

## What it generates

A file with the result, in whichever format you choose (`.txt` by default):

```
personas_que_no_te_siguen_de_vuelta_instagram_<your_username>.txt
```

with one profile link per line, one for each person you follow who doesn't follow you back. You can also get the same result as `.csv` or `.json` (see [Command-line options](#command-line-options)) if you want to open it in a spreadsheet or process it with another script.

## Requirements

- Python 3 installed.
- Your Instagram data export in **JSON** format.
- Optional, only if you're going to use [online verification](#optional-online-verification-accounts-that-no-longer-exist): [Playwright](https://playwright.dev/python/), installable with:

```bash
pip install -r requirements-optional.txt
playwright install chromium
```

## 1. Download your Instagram data

The process is the same whether you do it from your phone or your computer, since Instagram manages it all through the **Accounts Center**.

1. Open Instagram (app or [instagram.com](https://instagram.com)) and go to your profile.
2. Go to **Settings and privacy**.
3. Go to **Accounts Center**.
4. Tap **Your information and permissions**.
5. Tap **Download your information**.
6. Select your Instagram account → **Create export file**.

### What to choose when creating the export file

| Option | What to choose | Why |
|---|---|---|
| Information to include | Only **Followers and following** | It's the only thing the script uses; no need to download the rest |
| Date range | Whichever you prefer (recommended: **all time**) | To make sure nobody is missing from the result |
| Format | **JSON** (never HTML) | The script can only read JSON |
| Media quality | **Low** | No photos or videos get exported anyway, so this doesn't affect the result, and it keeps the file smaller |
| Destination | To your device, or transferred to a service like **Google Drive** | Whichever is more convenient for you |

About the destination: Instagram lets you choose between downloading it straight to your device or transferring it to a cloud service (Google Drive, Dropbox, Google Photos...); the exact options can vary slightly between the app and the website. Either way, you'll get a notification or email once the file is ready to download — that notice arrives regardless of the destination you picked, it isn't a destination option in itself.

Confirm the request and wait for the notification (it can take anywhere from a few minutes to a few hours).

> **Note:** if Instagram delivers the file through Google Drive, it sometimes splits it into several parts (`...-1-001.zip`, `...-1-002.zip`, etc.). If that happens, unzip all the parts and copy the contents of all of them next to `checker.py` (see next step).

## 2. Place the data in the project

1. Unzip the `.zip` file(s) Instagram sends you.
2. Copy all of its contents into **any folder next to `checker.py`**. For example:

```
instagram-checker/
├── checker.py
└── followers_and_following/      ← this folder's name doesn't matter
    ├── followers_1.json
    └── following.json
```

There's no need to touch anything in the script or to use a specific folder name: the script recursively searches **every folder and subfolder next to `checker.py`** until it finds `followers_1.json` and `following.json`, whatever the name or depth of the folders the `.zip` brings (Instagram has used different structures depending on the download method, e.g. with or without an intermediate `connections/` folder). Just unzip and copy — no renaming needed.

## 3. Install Python

<details>
<summary>Windows</summary>

1. Download the installer from [python.org/downloads](https://www.python.org/downloads/).
2. Run it and check the **Add Python to PATH** box before installing.
3. Verify with:

```bash
python --version
```
</details>

<details>
<summary>macOS</summary>

With Homebrew (recommended):

```bash
brew install python3
python3 --version
```

Or by downloading the official installer from [python.org/downloads](https://www.python.org/downloads/).
</details>

<details>
<summary>Linux</summary>

Usually comes preinstalled. Check with:

```bash
python3 --version
```

If you don't have it:

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install python3

# Fedora
sudo dnf install python3

# Arch
sudo pacman -S python
```
</details>

## 4. Run the script

```bash
python checker.py       # Windows
python3 checker.py      # macOS / Linux
```

If your export doesn't include the "Personal information" category, the script won't be able to detect your username automatically and will ask you for it.

When it's done, you'll see a summary in the terminal and the result file will be created in the project folder.

### Command-line options

All optional; without any of them, the script asks by keyboard whatever it needs.

| Option | What it does |
|---|---|
| `--verify` | Enables online verification without asking |
| `--no-verify` | Disables online verification without asking |
| `--format {txt,csv,json}` | Output file format (default: `txt`) |

Example, to generate the result as CSV without any prompts:

```bash
python checker.py --no-verify --format csv
```

## Accounts whose link doesn't work

It's normal for some links in the generated list to lead to a "Sorry, this page isn't available." That's not a bug in the script: those users are still saved in your export because Instagram doesn't clean up that relationship from your data even if the account:

- was **deleted** or **deactivated**,
- was **suspended/banned** by Instagram, or
- **blocked you** (in that case the profile only looks nonexistent to your account).

There's no way to tell these cases apart from the link alone, and regardless of the reason, the action to take is the same: unfollow that account (see the tip below).

### How to unfollow these accounts

Use your profile → **Following**, instead of Instagram's search bar. Deleted, suspended, or blocking accounts don't show up in search results, but they're still visible (and can be unfollowed) in your Following list. The generated file itself includes this same reminder at the end (in the `.txt` format).

## Optional online verification (accounts that no longer exist)

When the analysis is done, the script asks whether you want it to check, account by account, which of the profiles that don't follow you back no longer exist (deleted, suspended, or blocking you). It's entirely optional (off by default) and only runs if you answer yes that time, or if you use `--verify`.

How it works:

- **Opens each profile in a real browser (Chromium, via Playwright)**, exactly like you would by hand — it doesn't call any internal API. It was first tried with direct requests to Instagram's internal API, but that route blocks any automated client almost instantly (even with the right header and valid cookies); actually loading the profile page, on the other hand, works normally.
- **Checks two independent signals** to decide whether a profile no longer exists: the browser tab's title and a piece of text from the page's own content. If Instagram changes the wording of one of the two, the other acts as a fallback — the script doesn't depend on a single point of failure.
- **Never uses your login.** The browser signs in to no account at all. So if something goes wrong, the worst case is that Instagram stops showing logged-out profiles for a while — never that your account gets flagged for automated behavior.
- **Requires Playwright installed** (see [Requirements](#requirements)). If you don't have it, the script tells you the exact command to run and marks those accounts as "unverified" in the result, instead of failing.
- **Checks for an internet connection first.** If there isn't one, it doesn't even try: it marks all accounts as "unverified (no connection)".
- **Goes slowly on purpose**, with a random pause of a few seconds between each profile visited. With many accounts this can take several minutes (the script gives you an estimate before starting).
- **Stops itself if Instagram starts pushing back** (several checks in a row with no clear result, e.g. if you get redirected to the login screen). In that case it leaves the rest of the accounts as "unverified" instead of insisting.
- **You can interrupt it with Ctrl+C at any point without losing progress**: every result is saved as it happens (see next section), so there's no need to wait for it to finish if it's taking too long.
- The final result splits accounts into three groups: accounts still active (they really don't follow you back), accounts confirmed inaccessible, and unverified accounts (with the reason why).

### Cache between runs

Every result from the online verification is saved in `verificacion_cache.json`, next to `checker.py`. This has two effects:

- Accounts already confirmed as **active** or **nonexistent** in a previous run are **not checked again** on later runs — the script reuses the cached result directly.
- Accounts that were left as **"unverified"** (due to blocking, an interruption, or any other reason) are **automatically retried first**, before new accounts, the next time you enable verification.

In practice, this means only the first run with many accounts is really slow: later ones get progressively faster, and over time end up resolving accounts that were left unverified at the time. The file contains account names, so it's not pushed to the repository if you use git (it's already in `.gitignore`); if you want to force everything to be checked again from scratch, just delete it.

> **Why there's no faster, lighter, or "guaranteed" option:** Instagram doesn't offer any public API to check whether someone else's account exists. The only reliable method found is loading the actual profile page in a real browser, which means installing Playwright (a considerably heavier dependency than the rest of the script) and running a Chromium instance in the background. It isn't official or 100% reliable long-term: it can stop working if Instagram changes its website. That's normal, and doesn't indicate any problem with your data.

## Troubleshooting

**An empty file named `python` (or similar) gets created when running the script.**
The script doesn't create any file with that name. If you see it, it's almost always because the command you ran included an accidental output redirection, for example `python checker.py > python` instead of `python checker.py`. Check the command for a stray `>` (it can sneak in when pasting the command or reusing a line from your terminal history with the ↑ arrow) and remove it if present; it doesn't affect how the script works.

## Privacy

By default, no data leaves your computer: the script only reads the `.json` files you downloaded from your own Instagram account, and saves its results (including the verification cache) in the same project folder. The only exception is [optional online verification](#optional-online-verification-accounts-that-no-longer-exist): if you explicitly enable it, the script asks Instagram (anonymously, without your login) for the username of each account that doesn't follow you back, to find out whether it still exists.

## License

[MIT](LICENSE) — you're free to use, copy, and modify this project.
