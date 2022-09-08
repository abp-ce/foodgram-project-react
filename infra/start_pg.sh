docker run --name psql -v pg-data:/var/lib/postgresql/data/ \
    -e POSTGRES_PASSWORD=1234 -p 5432:5432 -d postgres:alpine
