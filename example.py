from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker


engine = create_engine("sqlite:///database5.sqlite", echo=True)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))

    def __repr__(self):
        return f"Post(id={self.id}, title={self.title})"


Base.metadata.create_all(engine)


with Session() as session:
    post = Post(title="Hello World")
    session.add(post)
    session.commit()
