short_message = "Use cross-site request forgery to control an archive user's account."
message = """
    <p>In this challenge, the archive server is configured to disable cross-site request forgery protection.
    This means captured web content can submit web forms on behalf of a logged in user.</p>

    <p>Your mission is to edit {challenge_path}/challenge.html so that, when 
    <a href="{challenge_url}">{challenge_url}</a> is captured or played back,
    the current user's account is deleted.</p>
"""