# Detadantic

## Note: As both Deta and Pydantic v1 has changed a lot since the creation of this project, this is deprecated. See [SpaceModel](https://github.com/Jay184/spacemodel) instead.

A wrapper providing Active-Record style access to Deta Bases using Pydantic.

```py
from typing import Optional
from datetime import datetime

from detadantic import DetaModel

# The following is not required when ran inside a Deta Micro
DetaModel.set_project_key('...')
# Or simply: os.environ['DETA_PROJECT_KEY'] = '...'

class Simple(DetaModel):
	__base_name__ = 'simple_db'
	name: str
	age: int

simple1 = Simple(name='alex', age=77)
simple1.save()

# Create to save it directly
simple2 = Simple.create({'name': 'alex', 'age': 77, 'key': 'one'})

# Expiring items
# Expire item in 300 seconds
simple3 = Simple(name='alex', age=77, key='alex23')
simple3.save(expire_in=300)

# Expire item at date
expire_at = datetime.fromisoformat('2023-01-01T00:00:00')
simple4 = Simple.create({'name': 'max', 'age': 28, 'key': 'max28'}, expire_at=expire_at)
```

refer to the [Deta docs](https://docs.deta.sh/docs/base/sdk/) for more information.
