from flask_security.utils import get_hmac, _pwd_context, _security

def verify_password(password, password_hash):
    """Returns ``True`` if the password matches the supplied hash.
    :param password: A plaintext password to verify
    :param password_hash: The expected hash value of the password (usually form your database)
    """
    if _security.password_hash != 'plaintext':
        password = get_hmac(password)

    return _pwd_context.verify(password, password_hash)

def allowed_file(filename, allowed):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed