FROM lambci/lambda:build-python3.6

WORKDIR /var/task
ENV WORKDIR /var/task

#RUN mkdir -p packages/ && \
#    pip install uuid -t packages/
COPY chatless "$WORKDIR/chatless"
COPY chatbot_example.py "$WORKDIR/chatbot_example.py"

# RUN zip -r9 $WORKDIR/lambda.zip packages/ lambda_function.py

# CMD ["/bin/bash"]