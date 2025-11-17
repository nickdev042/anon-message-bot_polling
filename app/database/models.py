from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3", echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # id в TG
    link_code: Mapped[str] = mapped_column(
        unique=True
    )  # Cсылка для отправки сообщений этому пользователю
    vip: Mapped[bool] = mapped_column(default=False)  # Параметр раскрытия никнейма


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
