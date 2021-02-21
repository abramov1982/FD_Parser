FROM python:3.8
ENV PORT 8081
COPY ./requirements.txt /fd_parser/requirements.txt
COPY ./config.yml /fd_parser/config.yml
WORKDIR /fd_parser
RUN pip install -r requirements.txt
COPY ./fd_parser /fd_parser
ENTRYPOINT ["python"]
CMD ["timer.py"]