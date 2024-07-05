# build
FROM python:3.12-slim as build

RUN apt-get update

RUN apt-get install -y --no-install-recommends build-essential gcc

WORKDIR /usr/app

RUN python -m venv /usr/app/venv

ENV PATH="/usr/app/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install -r requirements.txt


# run
FROM python:3.12-slim

WORKDIR /usr/app

COPY --from=build /usr/app/venv ./venv

COPY . .

ENV PATH="/usr/app/venv/bin:$PATH"

# python3 -m uvicorn main:app --reload
CMD [ "python3", "-m", "uvicorn", "main:app", "--reload" ]