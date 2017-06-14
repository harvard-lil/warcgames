short_message = "Discover services running on the archive server."
message = """
    <p>In this challenge, the archive server is configured to allow the capture proxy to reach local IPs.
    This means captured pages can scan and interact with services running on the archive server.</p>

    <p>Your mission is to edit {challenge_path}/challenge.html so that, when 
    <a href="{challenge_url}">{challenge_url}</a> is captured and played back,
    the captured page includes the contents of http://127.0.0.1:8000 through http://127.0.0.1:8100
    as seen by the capture proxy.</p>
    
    <p><b>Bonus:</b></p>
    <ul>
        <li>Can you scan for other reachable IP addresses on the same network?</li>
        <li>Can you take advantage of a service you discover between port 8000 and 8100?</li>
    </p>
    
    <p><b>Learn more:</b></p>
    <ul>
        <li><a href="https://security.stackexchange.com/questions/145336/how-can-a-webpage-scan-my-local-internal-network-from-the-internet">Stack Overflow</a></li>
        <li><a href="https://github.com/beefproject/beef/wiki/Network-Discovery">Network Discovery - beefproject/beef Wiki</a></li>
        <li><a href="https://defuse.ca/in-browser-port-scanning.htm">Port Scanning Local Network From a Web Browser - Defuse Security</a></li>
    </ul>
"""
include_wombat = True  # loading http://127.0.0.1 requires manual rewriting to get a correct answer otherwise, which is annoying