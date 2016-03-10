import json
import sqlite3

def check_schema(config, log_document):
    '''Check the log document schema'''
    schema_ok = True
    schema_keys = []

    for item in config.items("LOG_SCHEMA"):
        schema_keys.append(item[0])

    for key, value in log_document.items():
        if key not in schema_keys:
            schema_ok = False
            break
    if schema_ok:
        for key in schema_keys:
            if key == "last_index":
                continue
            if key not in log_document and key != "comment":
                schema_ok = False
                break
            if (key != "comment" and
                    isinstance(log_document[key], list) and
                    len(log_document[key]) != 1):
                schema_ok = False
                break
            if (key == "comment" and "comment" in log_document and
                    isinstance(log_document[key], list) and
                    len(log_document[key]) != 1):
                schema_ok = False
                break
    return schema_ok

def get_identifier_index(cur, iden):
    '''Get the database index for the corresponding identifier'''
    index = -1
    cur.execute('''select key from policies where key like 'policy_id_%' and
                   value = ?''', (iden,))
    results = cur.fetchall()
    if len(results) == 1:
        index = results[0][0].split("_")[-1]
    return index

def get_last_log_index(cur, cfg, idx):
    '''Return the index of the last log entry for this index'''
    last_log = -1
    last_index = "%s_%s" % (cfg.get("LOG_SCHEMA", "last_index"), idx)
    cur.execute("select value from policies where key = ?",
                (last_index,))
    results = cur.fetchall()
    if len(results) == 1:
        last_log = results[0][0]
    elif len(results) == 0:
        last_log = 0
    return last_log

def store_last_index(cur, cfg, idx, log_idx):
    '''Store the last log index'''
    last_log_index = int(log_idx) + 1
    db_key = "%s_%s" % (cfg.get("LOG_SCHEMA", "last_index"), idx)
    cur.execute("select key from policies where key = ?",
                (db_key,))
    results = cur.fetchall()
    if len(results) == 1:
        cur.execute("update policies set ? = ?",
                    (db_key, last_log_index))
    else:
        cur.execute("insert into policies(key,value) values(?,?)",
                    (db_key, last_log_index))

def load_db(config, log_document):
    '''Load the log document into the database'''

    conn = sqlite3.connect(config.get("DATABASE", "name"))
    cursor = conn.cursor()

    index = get_identifier_index(cursor, log_document["identifier"])
    last_log_index = get_last_log_index(cursor, config, index)

    for key, db_key in config.items("LOG_SCHEMA"):
        db_key = "%s_%s_%s" % (db_key, last_log_index, index)
        if key in log_document:
            cursor.execute("insert into policies(key, value) values (?,?)",
                           (db_key, log_document[key]))
    store_last_index(cursor, config, index, last_log_index)
    conn.commit()
    stored_log_doc = fetch_log_document(config, log_document, index,
                                        last_log_index)
    return stored_log_doc

def fetch_log_document(cfg, log_doc, idx, log_idx):
    '''Get the log document from the database'''
    out_doc = {}
    conn = sqlite3.connect(cfg.get("DATABASE", "name"))
    cursor = conn.cursor()
    for key, db_key in cfg.items("LOG_SCHEMA"):
        if key in log_doc:
            db_key = "%s_%s_%s" % (db_key, log_idx, idx)
            cursor.execute("select value from policies where key = ?",
                           (db_key,))
            results = cursor.fetchall()
            if len(results) == 1:
                out_doc[key] = results[0][0]
    return out_doc

def pack_response(data, msg, return_code):
    '''Pack the response for returning to the server'''
    response = {}
    if msg is not None:
        json_msg = json.dumps(msg)
    response["data"] = data
    response["message"] = json_msg
    response["return_code"] = return_code
    return response

def upload(cfg, log_documents):
    '''Upload the log document to the database'''

    # Need to loop over each document if we have a list or just the one doc
    # and then
    response = None
    return_code = 200
    data = []
    message = {}

    if type(log_documents) == str:
        log_documents = [log_documents]

    for log_document in log_documents:
        is_valid = check_schema(cfg, log_document)
        if not is_valid:
            data = []
            message["error"] = "JSON does not conform to schema"
            return_code = 400
            break
        else:
            data.append(load_db(cfg, log_document))
    response = pack_response(data, message, return_code)
    return response
