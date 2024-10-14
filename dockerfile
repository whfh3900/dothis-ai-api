
FROM --platform=linux/amd64 python:3.8-slim
WORKDIR /app

RUN apt-get update -y && apt-get install -y curl wget gzip gcc g++ make automake libtool build-essential libmecab2 nano procps

RUN wget https://bitbucket.org/eunjeon/mecab-ko/downloads/mecab-0.996-ko-0.9.2.tar.gz \
    && tar -xf mecab-0.996-ko-0.9.2.tar.gz \
    && cd mecab-0.996-ko-0.9.2 \
    && ./configure \
    && make \
    && make check \
    && make install \
    && cd .. \
    && rm -rf mecab-0.996-ko-0.9.2.tar.gz

RUN wget https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/mecab-ko-dic-2.1.1-20180720.tar.gz \
    && tar -xf mecab-ko-dic-2.1.1-20180720.tar.gz \
    && cd mecab-ko-dic-2.1.1-20180720 \
    && ./configure \
    && ./autogen.sh \
    && make \
    && make install \
    && cd .. \
    && rm -rf mecab-ko-dic-2.1.1-20180720.tar.gz

COPY . .

RUN pip install --upgrade pip setuptools \
    && pip install -r requirements.txt

EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
