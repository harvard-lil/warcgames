try:
    from support_files.challenge_wsgi import application
except ImportError as e:
    if 'challenge_wsgi' in str(e.msg):
        from webrecorder.main import application
    else:
        raise