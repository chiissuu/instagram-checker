===============================================================
 INSTAGRAM CHECKER - USER GUIDE
===============================================================

This program compares your Instagram "followers" and "following"
and generates a file listing the people you follow who don't
follow you back.

To make it work you need 3 things:
  1. Have Python installed on your computer.
  2. Download your Instagram information (the export).
  3. Run the checker.py script.

Each step is explained below.


---------------------------------------------------------------
1. HOW TO DOWNLOAD YOUR INSTAGRAM INFORMATION
---------------------------------------------------------------

Instagram lets you download all of your account's information
(followers, following, messages, photos, etc.) from the
"Accounts Center". The process is the same whether you do it
from your phone (app) or your computer (web browser).

  1. Open Instagram (app or instagram.com) and go to your
     profile.
  2. Go to "Settings and privacy".
  3. Go to "Accounts Center".
  4. Tap "Your information and permissions".
  5. Tap "Download your information".
  6. Select your Instagram account and tap "Create export
     file".

  When creating the export file you'll need to choose several
  options. It's recommended to set them like this:

    - Information to include: select ONLY "Followers and
      following". You don't need to check the rest of the
      categories, the script only uses this one.

    - Date range: whichever you prefer, but to get the best
      result (so nobody is missing from the list) it's
      recommended to choose "All time".

    - Format: MUST be "JSON" (not "HTML"), since the script can
      only read JSON files.

    - Media quality: "Low". No photos or videos get exported
      anyway, so this option doesn't affect the result, and it
      keeps the file smaller.

    - Destination: you can choose to download it straight to
      your device, or transfer it to an external service like
      Google Drive, Dropbox, etc. (the exact options can vary a
      bit between the app and the website). Pick whichever is
      more convenient for you. Either way, Instagram will
      notify you by notification or email once the file is
      ready to download; that notice arrives regardless of the
      destination you choose, it isn't a destination option in
      itself.

  7. Confirm the request. Instagram will take anywhere from a
     few minutes to several hours to prepare the file.
  8. Once you get the notification, go back into "Download your
     information" (or the external service you chose) and
     download the .zip file.

Note: if Instagram delivers the file through Google Drive, it
sometimes splits it into several parts (for example
"...-1-001.zip", "...-1-002.zip"). If that happens, unzip all
the parts and copy the contents of all of them into a folder
next to the checker.py script (see next step).


---------------------------------------------------------------
2. WHAT TO DO WITH THE DOWNLOADED FILE
---------------------------------------------------------------

  1. Unzip the .zip file(s) Instagram gave you.
  2. You'll see a folder with subfolders inside
     (followers_and_following, personal_information, etc.).
  3. Copy ALL of the unzipped contents into ANY folder next to
     the checker.py script. That folder's name doesn't matter
     (you can name it whatever you want, or keep the name
     Instagram gave it).

The final structure should look roughly like this:

  instagram-checker/
    checker.py
    followers_and_following/     <- the name doesn't matter
      followers_1.json
      following.json
      personal_information/
        ...

You DON'T need to modify anything inside the checker.py script,
nor create a folder with a specific name: the script recursively
searches EVERY folder and subfolder next to checker.py (going
through every level, no matter how many there are) until it
finds followers_1.json and following.json, wherever they are and
whatever the containing folder is called. Just unzip the file
and copy its contents somewhere inside the project folder.


---------------------------------------------------------------
3. HOW TO INSTALL PYTHON
---------------------------------------------------------------

The script is written in Python, so you need to have it
installed to run it.

--- Windows ---

  1. Go to https://www.python.org/downloads/ and download the
     latest version of Python for Windows.
  2. Run the downloaded installer.
  3. IMPORTANT: check the "Add Python to PATH" box before
     clicking "Install Now".
  4. Once installed, open a terminal (cmd or PowerShell) and
     type:
         python --version
     If it shows a version number, it's installed correctly.

--- macOS ---

  Option A (recommended, with Homebrew):
    1. Install Homebrew if you don't have it (https://brew.sh).
    2. Open Terminal and run:
         brew install python3
    3. Check the installation with:
         python3 --version

  Option B (official installer):
    1. Go to https://www.python.org/downloads/ and download the
       installer for macOS.
    2. Open it and follow the setup steps.
    3. Check the installation by opening Terminal and typing:
         python3 --version

--- Linux ---

  Most distributions already come with Python installed. To
  check, open a terminal and type:
      python3 --version

  If you don't have it, use your distribution's package
  manager:

    Ubuntu / Debian:
        sudo apt update
        sudo apt install python3

    Fedora:
        sudo dnf install python3

    Arch Linux:
        sudo pacman -S python

Optional: if you want to use the online verification (point 6),
also install Playwright (same on Windows, macOS and Linux):

    pip install -r requirements-optional.txt
    playwright install chromium

Not needed if you're not going to use that optional feature.


---------------------------------------------------------------
4. HOW TO RUN THE SCRIPT
---------------------------------------------------------------

  1. Open a terminal (cmd, PowerShell, macOS/Linux Terminal)
     inside the project folder (instagram-checker).
  2. Run the script with:

       Windows:      python checker.py
       macOS/Linux:  python3 checker.py

  3. If the script can't detect your username automatically
     (this happens if you didn't include the "Personal
     information" category in your download), it will ask you
     for it. Just type it and press Enter.
  4. It will ask whether you want to enable the optional online
     verification (see point 6 below). You can answer no
     without any issue, it's optional.
  5. When it's done, a file will be generated named:

       personas_que_no_te_siguen_de_vuelta_instagram_<your_username>.txt

     That file contains, one per line, the profile link of each
     person you follow who doesn't follow you back.

  Options to avoid answering questions by keyboard (useful if
  you want to automate the run): when running the script you
  can add, after "checker.py", any of these options:

    --verify              Enables online verification without
                           asking.
    --no-verify            Disables online verification without
                           asking.
    --format txt|csv|json  Output file format (default: txt).
                           csv or json are useful if you want to
                           open the result in a spreadsheet or
                           process it with another program.

  Example (generates the result as CSV without asking anything):

       python checker.py --no-verify --format csv


---------------------------------------------------------------
5. ACCOUNTS WHOSE LINK DOESN'T WORK
---------------------------------------------------------------

It's normal for some links in the generated list to lead to a
"Sorry, this page isn't available." That's not a bug in the
script: those users are still saved in your export because
Instagram doesn't clean up that relationship from your data even
if the account:

  - was deleted or deactivated,
  - was suspended/banned by Instagram, or
  - blocked you (in that case the profile only looks
    nonexistent to your account).

There's no way to tell these cases apart from the link alone,
and regardless of the reason, the action to take is the same:
unfollow that account (see the tip in the next point).

To unfollow these accounts, use your profile > Following,
instead of Instagram's search bar. Deleted, suspended, or
blocking accounts don't show up in search results, but they're
still visible (and can be unfollowed) in your Following list.
The generated .txt file itself includes this same reminder at
the end.


---------------------------------------------------------------
6. OPTIONAL ONLINE VERIFICATION (accounts that no longer exist)
---------------------------------------------------------------

When the analysis is done, the script asks whether you want it
to check, account by account, which of the profiles that don't
follow you back no longer exist (deleted, suspended, or blocking
you). It's entirely optional (OFF by default) and only runs if
you answer yes that time, or if you run the script with
--verify (see point 4).

How it works:

  - Opens each profile in a real browser (Chromium, via the
    Playwright library), exactly like you would by hand; it
    doesn't call any internal API. It was first tried making
    direct requests to Instagram's internal API, but that route
    blocks any automated client almost instantly (even with the
    right header and valid cookies); actually loading the
    profile page, on the other hand, works normally.

  - Checks TWO different signals to decide whether a profile no
    longer exists: the browser tab's title and a piece of text
    from the page's own content. That way, if Instagram changes
    the wording of one of the two, the other acts as a backup
    and the script doesn't go "blind" all at once.

  - NEVER uses your login. The browser signs in to no account at
    all. If something goes wrong, the worst case is that
    viewing logged-out profiles gets temporarily blocked, never
    your own account.

  - Requires Playwright installed (see point 3; you'll also need
    to run "pip install -r requirements-optional.txt" and
    "playwright install chromium"). If you don't have it, the
    script tells you the exact command and marks those accounts
    as "unverified" in the result, instead of failing.

  - Checks for an internet connection first. If there isn't one,
    it doesn't even try: it marks all accounts as "unverified
    (no connection)", as requested.

  - Goes slowly on purpose, with a random pause of a few seconds
    between each profile visited. With many accounts this can
    take several minutes (the script gives you an estimate
    before starting).

  - Stops itself if Instagram starts pushing back (several
    checks in a row with no clear result, e.g. if you get
    redirected to the login screen). In that case it leaves the
    rest as "unverified" instead of insisting.

  - You can interrupt it with Ctrl+C at any point without losing
    progress: every result is saved as it happens (see
    "Remembers what's already been checked" below), so there's
    no need to wait for it to finish if it's taking too long.

  - The final result splits the file into three groups: accounts
    still active (they really don't follow you back), accounts
    confirmed inaccessible, and unverified accounts (with the
    reason why).

  REMEMBERS WHAT'S ALREADY BEEN CHECKED BETWEEN RUNS

  Every result from this verification is saved in a file called
  "verificacion_cache.json", next to checker.py. Thanks to this:

    - Accounts already confirmed as active or nonexistent in a
      previous run are NOT checked again the next time.
    - Accounts that were left as "unverified" (due to blocking,
      an interruption, etc.) are automatically retried first,
      before new accounts, the next time you enable
      verification.

  In practice this means only the first run, with many accounts,
  really takes a while; later runs get progressively faster. If
  you ever want everything checked again from scratch, just
  delete that file.

Why there's no faster, lighter, or "guaranteed" option:
Instagram doesn't offer any public API to check whether someone
else's account exists. The only reliable method found is loading
the actual profile page in a real browser, which means installing
Playwright (a considerably heavier dependency than the rest of
the script) and running a Chromium instance in the background.
It isn't official or 100% reliable long-term: it can stop working
if Instagram changes its website. That's normal, and doesn't
indicate any problem with your data.


---------------------------------------------------------------
TROUBLESHOOTING
---------------------------------------------------------------

An empty file named "python" (or similar) gets created when
running the script.

  The script doesn't create any file with that name. If you see
  it, it's almost always because the command you ran included an
  accidental output redirection, for example:

      python checker.py > python

  instead of:

      python checker.py

  Check the command for a stray ">" (it can sneak in when
  pasting the command or reusing a line from your terminal
  history with the up arrow) and remove it if present; it
  doesn't affect how the script works.


---------------------------------------------------------------
FINAL NOTES
---------------------------------------------------------------

- By default, this script doesn't connect to the internet or
  send your data anywhere: all of the analysis happens locally,
  reading the JSON files you already downloaded, and saving its
  results (including the verification cache) in the same project
  folder. The only exception is the optional online verification
  (point 6): if you explicitly enable it, the script asks
  Instagram, anonymously and without your login, for the
  username of each account that doesn't follow you back.
- You can run the script again whenever you want, as long as you
  update the contents of the data folder (whichever one it is)
  with a more recent download.
