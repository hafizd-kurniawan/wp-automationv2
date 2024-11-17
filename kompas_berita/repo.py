
from datetime import datetime

from database.model import *

# Data Dummy untuk Article
article = Article(
    title="Dummy Article about AI and Python",
    source_url="https://example.com/dummy-article1",
    category="teknologi",
    tags="hardware Komputer",
    scraping_date=datetime.now(),
    created_at=datetime.now(),
    updated_at=datetime.now(),
)
session.add(article)
session.commit()


# Menambahkan Excerpt
excerpt = Excerpt(
    article_id=article.id,
    content="ini adalah sebuah sumper komputer",
)
session.add(excerpt)

# Menambahkan kategori
category = Category(
    name="Technology",
)
session.add(category)

# Menambahkan tag
tag = Tag(
    name="hardware Komputer",
)
session.add(tag)

# Menambahkan content
# kontent perlu dependensi ke artikel
content = Content(
    article_id=article.id,
    content="/home/hafizd/rumahkita/file.json",
)
session.add(content)
session.commit()
