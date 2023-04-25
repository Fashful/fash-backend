import json
import requests
from dotenv import load_dotenv
from requests.exceptions import ConnectTimeout, ReadTimeout, ConnectionError
from sqlalchemy import or_
from sqlalchemy import text
from datetime import datetime

load_dotenv()

def success(text=None, data=None, pages=None, total=None):
    return_obj = {
        'success': True,
        'data': data,
        'text': text
    }
    if pages is not None:
        return_obj['pages'] = pages
    if total is not None:
        return_obj['total'] = total
    return json.dumps(return_obj, default=str)


def failure(text=None, data=None):
    return_obj = {
        'success': False,
        'text': text,
        'data': data
    }
    return json.dumps(return_obj, default=str)

def build_query(db, args, model, joined_model=None):
    if joined_model is not None:
        query = db.session.query(model, joined_model).join(joined_model)
    else:
        query = db.session.query(model)
    for attr, value in args.items():
        if attr.startswith('date__'):
            # date format date__lte__created_at, date__gte__created_at
            attr = attr.split('__')
            modelAttr = getattr(model, attr[2], None)
            if modelAttr is None:
                modelAttr = getattr(joined_model, attr[2], None)
            if modelAttr is not None:
                if attr[1] == 'gte':
                    query = query.filter(modelAttr >= value)
                elif attr[1] == 'lte':
                    query = query.filter(modelAttr <= value)
        elif '__' in attr:
            attr = attr.split('__')
            query = query.filter(
                text(f"{attr[0]}->>'{attr[1]}' ILIKE '%{value}%'"))

        else:
            modelAttr = getattr(model, attr, None)
            if modelAttr is None:
                modelAttr = getattr(joined_model, attr, None)
            if modelAttr is not None:
                if str(modelAttr.type) == "BOOLEAN":
                    query = query.filter(
                        modelAttr == (value == "true"))
                elif str(modelAttr.type) == "DATE":
                    query = query.filter(modelAttr == value)
                else:
                    if ',' in value:
                        values = value.split(',')
                        query = query.filter(
                            or_(modelAttr == v for v in values))
                    else:
                        query = query.filter(
                            modelAttr.ilike(f"%{value}%"))
    return query