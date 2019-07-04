last_items_kwargs = {'KeyConditionExpression': '#id = :ballots',
                     'Limit': 1,
                     'ScanIndexForward': False,
                     'ExpressionAttributeNames': {'#id': 'id'},
                     'ExpressionAttributeValues': {':ballots': 'ballots'}}

put_item_kwargs = {'Item': {'id': 'ballots', 'sortkey': 'test', 'prop': 'prop'}}
