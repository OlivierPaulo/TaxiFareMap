### FROM the base image we want to build
FROM python:3.8.6-buster

### COPY file needed for the Docker images
COPY . .

### RUN the directives to install the dependancies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN make install

### CMD apply the command that the container should run once it has started
CMD streamlit run app.py 