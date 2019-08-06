import os
from datetime import date
from typing import Optional, Tuple, Dict
import logging
import functools
import boto3

log = logging.getLogger()
log.setLevel(logging.DEBUG)

# there is assumption of schema
# id -> string / metacontainer
# sortkey -> string / sort string for container
# it should cover 90% usecases

def _dict_to_expression(expr_dict: Dict[str, str]) -> Tuple[str, Dict[str, str], Dict[str, str]]:
    # fold this to big tuple?
    expressions = (f"#{key_name} = :{val_name}" for key_name, val_name in expr_dict.items())
    expression = " AND ".join(expressions)
    attributes = {f":{v}": v for _, v in expr_dict.items()}
    keys = {f"#{k}": k for k, _ in expr_dict.items()}
    return expression, keys, attributes

# it is nicer abstraction than partial monkeypatching
# and provides some immutibility and comp

class DynamoTableControl(object):
    def __init__(self, table):
        self._table = table

    @property
    def table(self):
        return self._table

    def last_items(self, pkey: Tuple[str, str], sortkey: Optional[Tuple[str, str]] = None,
                   reverse: bool = False, limit: int = 1) -> list:
        pkeys = filter(None, (pkey, sortkey))  # f mypy
        expr_dict = {k: v for k, v in pkeys}  # noqa T484
        key_expression, keys, attributes = _dict_to_expression(expr_dict)
        elements = self.table.query(KeyConditionExpression=key_expression,
                                    Limit=limit, ScanIndexForward=reverse,
                                    ExpressionAttributeNames=keys,
                                    ExpressionAttributeValues=attributes)
        return elements.get('Items', [])

    # put item should be easier to use if whole item is replaced
    # TODO: redesign update to provide atomicity in operations
    # perhaps obtaining document should create a class and track modifications
    # to make them atomic
    # def update_item(self, pkey: Tuple[str, str], sortkey: Tuple[str, str],
    #                 update_dict: dict) -> dict:
    #     log.debug("Updating ballot %s with {%s: %s}",)
    #     pkeys = filter(lambda x: x, (pkey, sortkey))
    #     expression, keys, attributes = _dict_to_expression(update_dict)
    #     update_expression = f"SET {expression}"
    #     update_cmd = self.table.update_item(Key={key: val for key, val in pkeys},
    #                                         UpdateExpression=update_expression,
    #                                         ExpressionAttributeNames=keys,
    #                                         ExpressionAttributeValues=attributes,
    #                                         ReturnValues="ALL_NEW")
    #     return update_cmd.get('Attributes', {})

    # not the heaviest method
    def put_item(self, item: dict) -> bool:
        assert item.get('id') and item.get('sortkey')
        response = self.table.put_item(Item=item).get('ResponseMetadata', {})
        success = response.get('HTTPStatusCode') == 200
        return success

class DynamoSubsetTableControl(DynamoTableControl):
    def __init__(self, table, pkey):
        self._table = table
        self._pkey = pkey

    @property
    def table(self):
        return self._table

    @property
    def pkey(self):
        return self._pkey

    def last_items(self, *args, **kwargs) -> list:
        print(**kwargs)
        print(*args)
        return super().last_items(pkey=self._pkey, *args, **kwargs)  # type: ignore # fuck mypy issue 4335

    # def update_item(self, *args, **kwargs) -> dict:
    #     return super().update_item(pkey=self._pkey, *args, **kwargs)  # type: ignore # fuck mypy issue 4335

    def put_item(self, item: dict) -> bool:
        key, val = self._pkey
        assert item.get(key) == val
        return super().put_item(item=item)
