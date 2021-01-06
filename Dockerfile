FROM python3.9.1

WORKDIR /app

ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND noninteractive
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime


RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y \
  git \
  make \
  cmake \
  curl \
  xz-utils \
  file \
  sudo \
  build-essential \
  antiword \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip install textract langdetect
COPY extract.py /app
# /app/workspace is mounted to ./workspace

CMD ["python3", "extract.py", "/app/workspace/docs/", "/app/workspace/texts/"]