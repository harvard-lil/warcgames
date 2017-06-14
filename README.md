WARCgames
=========

Building secure web archival tools is hard, because web archives have to ingest and play back so much attacker-submitted
content. WARCgames challenges you to attack deliberately-insecure, simplified web archive services running on your local
computer, and thereby learn to create secure ones.

![WARCgames browser screenshot](docs/screenshot.png)

Install and Run
---------------

1) [Install Docker](https://docs.docker.com/installation/)

2) `git clone https://github.com/jcushman/warcgames`

3) `cd warcgames`

4) `cat support_files/hosts | sudo tee -a /etc/hosts` 

    (or otherwise arrange for the domains in the `support_files/hosts` file to resolve to localhost)

4) `python warcgames.py` to see a list of challenges.

5) `python warcgames.py same_domain` to start the first challenge.

Challenges
----------

WARCgames currently offers the following challenges:

<!-- The following is automatically populated --> 
<!-- CHALLENGES -->
* csrf: Use cross-site request forgery to control an archive user's account.
* port_scan: Discover services running on the archive server.
* same_domain: Use cross-site scripting (XSS) to control an archive user's account.
* same_subdomain: Use top-level cookies to log out the current user.
<!-- END CHALLENGES-->

(This is the output of `python warcgames.py`)

Contributing Challenges
-----------------------

Please file an issue if you would like WARCgames to support a new challenge.

Even better, send a pull request!

Each challenge is a subdirectory under `challenges/`. Files:

* `config.py`: Python file that defines:
    * `short_message`: short text description of the challenge.
    * `message`: HTML description of the challenge to embed at https://warcgames.test:8089/
    * `CONTENT_HOST` (optional, default `warcgames-content.test:8089`): host to serve captured content.
    * `include_wombat` (optional, default false): if true, wombat.js will be included in the header of captured pages.
      This should be included only for challenges that require sub-assets to load correctly.
* `challenge.html`: file for user to edit when attempting challenge.
* `sample_answer.html`: sample version of `challenge.html` that correctly completes the challenge.
* `wsgi.py` (optional): custom wsgi file, used to monkeypatch app server.

Security Reporting
------------------

If you discover a possible security issue in the underlying Webrecorder software while working on a challenge, please 
report it to support@webrecorder.io rather than filing an issue on this project.