CONTENT_HOST = "warcgames.test:8089"
short_message = "Use cross-site scripting (XSS) to control an archive user's account."
message = """
    <p>In this challenge, the archive server is configured to serve the user interface and captured web archive content
    on the same domain. This means captured web content can use cross-site scripting (XSS) to control user accounts on the
    archive server.</p>

    <p>Your mission is to edit {challenge_path}/challenge.html so that, when 
    <a href="{challenge_url}challenge.html">{challenge_url}challenge.html</a> is captured or played back,
    the current user's account is deleted.</p>
"""