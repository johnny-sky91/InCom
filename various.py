# create x ic in database

# user_id, timestamp, order_number, product_type,
# model, cause, detection_area, description, complaint_status

from app.models import User, InCom, DetectionAreas, Models, Types, Causes
from app import db
from datetime import datetime
import random
from random import randint
import string

date = datetime.utcnow()

model_query = Models.query.with_entities(Models.product_model).all()
models = [item for t in model_query for item in t]

type_query = Types.query.with_entities(Types.product_type).all()
types = [item for t in type_query for item in t]

cause_query = Causes.query.with_entities(Causes.cause_type).all()
causes = [item for t in cause_query for item in t]

letters = string.ascii_letters


def create_ic(choose_models, choose_types, choose_causes, choose_letters):
    description = (''.join(random.choice(choose_letters) for i in range(10)))
    new_ic = InCom(
        user_id=1,
        timestamp=date,
        order_number=str(randint(10000, 99999)),
        product_type=random.choice(choose_types),
        model=random.choice(choose_models),
        cause=random.choice(choose_causes),
        detection_area='PIŁA',
        description=description,
    )
    db.session.add(new_ic)
    db.session.commit()
