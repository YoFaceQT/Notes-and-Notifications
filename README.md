npm start

uvicorn src.main:app --reload

docker exec -it pg-container bash
psql -U postgres


\l
SELECT * FROM notes;