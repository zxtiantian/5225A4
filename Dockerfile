FROM public.ecr.aws/lambda/python:3.9

# 1) give Python a place to write matplotlib cache
ENV MPLCONFIGDIR=/tmp/.matplotlib

# 2) install tar + xz + libsndfile
RUN yum install -y tar xz libsndfile libsndfile-devel \
 && yum install -y ffmpeg libsndfile libsndfile-devel sox sox-devel \
 && yum clean all


# 3) unpack static ffmpeg & symlink into /usr/bin
ADD https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz /tmp/
RUN tar xJf /tmp/ffmpeg-release-amd64-static.tar.xz \
 && cp ffmpeg-*/ffmpeg ffmpeg-*/ffprobe /usr/bin/ \
 && chmod +x /usr/bin/{ffmpeg,ffprobe} \
 && rm -rf /tmp/ffmpeg-*

# 4) install only the Python deps
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# 5) copy code + model
COPY lambda.py ${LAMBDA_TASK_ROOT}/
COPY model     ${LAMBDA_TASK_ROOT}/model/

# 6) point CMD at the real handler name
CMD ["lambda.lambda_handler"]