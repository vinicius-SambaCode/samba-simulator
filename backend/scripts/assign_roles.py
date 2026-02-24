from app.core.db import SessionLocal
from app.models.base_models import User, Role

def run():
    db = SessionLocal()

    teacher_role = db.query(Role).filter(Role.name == "TEACHER").first()

    users = db.query(User).all()

    for user in users:
        if teacher_role not in user.roles:
            user.roles.append(teacher_role)

    db.commit()
    db.close()

    print("✔ Papéis atribuídos aos usuários!")

if __name__ == "__main__":
    run()