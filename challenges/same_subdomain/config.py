CONTENT_HOST = "content.warcgames.test:8089"
short_message = "Use top-level cookies to log out the current user."
message = """
    <p>In this challenge, the archive server is configured to serve captured web archive content at a subdomain
    of the user dashboard. This means that captured pages can overwrite session cookies with new top-level cookies.</p>

    <p>Your mission is to edit {challenge_path}/challenge.html so that, when 
    <a href="{challenge_url}challenge.html">{challenge_url}challenge.html</a> is captured or played back,
    the current user is logged out.</p>
    
    <p><b>Bonus:</b> With a bit more effort, you can log in the user as a different user -- for example, any visitor
    could be logged into an account controlled by the attacker.</p>
"""