




# ─────────────────────────────────────────────────────────────
# library/seed.py — run once: python manage.py shell < library/seed.py
# ─────────────────────────────────────────────────────────────
MANGA_SEED = [
    dict(mangadex_id='f9c33607-9180-4ba6-b85c-e4b5faae7132', title='Solo Leveling',  description="A weak hunter becomes the world's strongest.",           cover_color='#1a1a2e', unlock_key='chapter_1',   order=1),
    dict(mangadex_id='32d76d19-8a05-4db0-9fc2-e0b0648fe9d0', title='Mushishi',       description='Quiet, beautiful stories about mysterious life forms.',   cover_color='#1d7a5a', unlock_key='chapter_2',   order=2),
    dict(mangadex_id='c52b2ce3-7f95-469c-96b0-479524fb7a1a', title='Dungeon Meshi',  description='Adventurers cook dungeon monsters. Hilarious and cosy.',  cover_color='#9a6800', unlock_key='chapter_3',   order=3),
    dict(mangadex_id='4f3ebb17-2f1e-4e8e-a53b-a46e7a5d6ec9', title='Blue Period',   description='A teen discovers art and himself. Raw and emotional.',     cover_color='#1a5fa8', unlock_key='second_book', order=4),
    dict(mangadex_id='b9797c5b-642e-44d9-ac40-8b31b9ae110a', title='Vinland Saga',  description='A Viking saga that becomes a search for peace.',           cover_color='#3d2b23', unlock_key='full_library',order=5),
]

BOOK_SEED = [
    dict(gutenberg_id=84,   title='Frankenstein',              author='Mary Shelley',      description="The original monster story — about loneliness and being misunderstood.", cover_color='#1a1a2e', unlock_key='chapter_1',   order=1),
    dict(gutenberg_id=345,  title='Dracula',                   author='Bram Stoker',       description='Suspenseful, gothic, and surprisingly modern.',                           cover_color='#4a0a0a', unlock_key='chapter_2',   order=2),
    dict(gutenberg_id=43,   title='Jekyll and Hyde',           author='R.L. Stevenson',    description='A gripping thriller about identity and hidden selves.',                   cover_color='#2a1a4a', unlock_key='chapter_3',   order=3),
    dict(gutenberg_id=1184, title='The Count of Monte Cristo', author='Alexandre Dumas',   description='The ultimate revenge story. Betrayal and one epic comeback.',             cover_color='#0a3a2a', unlock_key='second_book', order=4),
    dict(gutenberg_id=5200, title='Metamorphosis',             author='Franz Kafka',       description='Waking up changed and alienated. Gen Z gets this.',                       cover_color='#1a3a1a', unlock_key='full_library',order=5),
    dict(gutenberg_id=174,  title='The Picture of Dorian Gray',author='Oscar Wilde',       description='Beauty, obsession, and a portrait that holds all your sins.',             cover_color='#3a1a4a', unlock_key='full_library',order=6),
    dict(gutenberg_id=43,   title='Jekyll and Hyde',           author='R.L. Stevenson',    description='Identity, duality, and the self you hide.',                               cover_color='#2a1a4a', unlock_key='full_library',order=7),
]
