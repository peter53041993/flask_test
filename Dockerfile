FROM python:3.7
WORKDIR	/opt/oracle
RUN apt-get update && apt-get install -y libaio1 wget unzip \
&& wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip \
&& unzip instantclient-basiclite-linuxx64.zip \
&& rm -f instantclient-basiclite-linuxx64.zip \
&& cd /opt/oracle/instantclient* \
&& rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci \
&& echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf \
&& ldconfig
WORKDIR /jupyter_test
COPY requirements.txt /jupyter_test
COPY . /jupyter_test
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple
ENTRYPOINT ["python","/jupyter_test/flask_test.py"]

