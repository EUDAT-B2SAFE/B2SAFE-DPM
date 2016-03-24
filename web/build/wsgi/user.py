'''Module for user accounts'''
import sqlite3
import itsdangerous
import passlib.apps

s_key = "key for the data policy manager"

def verify_password(user, password, config):
    '''Verify the password'''
    verified = False
    conn = sqlite3.connect(config.get("DATABASE", "profile_name"))
    cursor = conn.cursor()
    cursor.execute("select pword from user where name = ?", (user,))
    results = cursor.fetchall()
    if len(results) == 1:
        pword_hash = results[0][0]
        verified = passlib.apps.custom_app_context.verify(password, pword_hash)
    return verified

def generate_auth_token(user, expiry):
    '''Create an authentication token'''
    ser = itsdangerous.TimedJSONWebSignatureSerializer(s_key, expires_in=expiry)
    return ser.dumps({"id": user})

def verify_auth_token(token, config):
    '''Verify the authentication token'''
    user = None
    data = None
    ser = itsdangerous.TimedJSONWebSignatureSerializer(s_key)
    try:
        data = ser.loads(token)
    except itsdangerous.SignatureExpired:
        return user    # valid token, but expired
    except itsdangerous.BadSignature:
        return user # invalid token

    conn = sqlite3.connect(config.get("DATABASE", "profile_name"))
    cursor = conn.cursor()
    cursor.execute("select name, user_id from user where name = ?", (data["id"],))
    results = cursor.fetchall()
    if len(results) == 1:
        user = {}
        user["name"] = results[0][0]
        user_id = results[0][1]
        cursor.execute('''select community.name from community, user_community
                          where user_community.user_id = ?
                          and user_community.community_id = community.community_id''',
                       (user_id,))
        res = cursor.fetchall()
        if len(res) > 0:
            communities = []
            for a_result in res:
                communities.append(a_result[0])
            user["communities"] = communities
        else:
            user["communities"] = communities
    return user
