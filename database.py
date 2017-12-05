from models import User
from models import Session


session = Session()
# user = User(name='name', password='password')
# session.add(user)
# session.commit()
a = session.query(User).all()
print(type(a[0].created_at))
