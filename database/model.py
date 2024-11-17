from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


def migrate(databaseUrl: str):
    global Base
    engine = create_engine(databaseUrl, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False, index=True)
    Excerpt = Column(Text, nullable=True)
    source_url = Column(Text, nullable=False, index=True, unique=True)
    category = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)
    contents = Column(Text, nullable=True)
    scraping_date = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    excerpt = relationship("Excerpt", back_populates="articles")
    content = relationship("Content", back_populates="articles")
    # tags = relationship("Tag", back_populates="articles")
    # internal_links = relationship(
    #     "InternalLink", back_populates="articles", cascade="all, delete-orphan"
    # )
    # cross_site_links = relationship("CrossSiteLink", back_populates="articles")
    # featured_image = relationship(
    #     "FeaturedImage", back_populates="articles", uselist=False
    # )
    # images = relationship("Image", back_populates="articles")


class Excerpt(Base):
    __tablename__ = "excerpts"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    content = Column(Text, nullable=False)

    articles = relationship("Article", back_populates="excerpt")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)


class Content(Base):
    __tablename__ = "contents"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    content = Column(Text, nullable=False)

    articles = relationship("Article", back_populates="content")


# class InternalLink(Base):
#     __tablename__ = "internal_links"

#     id = Column(Integer, primary_key=True)
#     article_id = Column(Integer, ForeignKey("articles.id"))

#     # Relasi ke artikel utama
#     articles = relationship("Article", back_populates="internal_links")


# class CrossSiteLink(Base):
#     __tablename__ = "cross_site_links"

#     id = Column(Integer, primary_key=True)
#     article_id = Column(Integer, ForeignKey("articles.id"))
#     target_url = Column(String(255), nullable=False)
#     anchor_text = Column(String(255), nullable=False)

#     articles = relationship("Article", back_populates="cross_site_links")


# class FeaturedImage(Base):
#     __tablename__ = "featured_images"

#     id = Column(Integer, primary_key=True)
#     article_id = Column(Integer, ForeignKey("articles.id"))
#     image = Column(String(255), nullable=False)
#     alt = Column(String(255), nullable=False)
#     caption = Column(String(255), nullable=True)

#     articles = relationship("Article", back_populates="featured_image")


# class Image(Base):
#     __tablename__ = "images"

#     id = Column(Integer, primary_key=True)
#     article_id = Column(Integer, ForeignKey("articles.id"))
#     image = Column(String(255), nullable=False)
#     alt = Column(String(255), nullable=False)
#     caption = Column(String(255), nullable=True)

#     articles = relationship("Article", back_populates="images")
