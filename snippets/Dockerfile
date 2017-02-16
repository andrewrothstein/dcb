FROM {{fq_upstream_image}}
MAINTAINER "Andrew Rothstein" andrew.rothstein@gmail.com

RUN mkdir -p /freshen
WORKDIR /freshen
COPY requirements.yml requirements.yml
COPY playbook.yml playbook.yml
RUN ansible-galaxy install -r requirements.yml
RUN ansible-playbook playbook.yml

RUN mkdir -p /role-to-test
ONBUILD ADD . /role-to-test
ONBUILD WORKDIR /role-to-test
ONBUILD RUN if [ -f requirements.yml ]; then ansible-galaxy install -r requirements.yml; fi
ONBUILD RUN if [ -f test-requirements.yml ]; then ansible-galaxy install -r test-requirements.yml; fi
ONBUILD RUN if [ -f test-inventory.ini ]; then ansible-playbook -i test-inventory.ini test.yml; else ansible-playbook test.yml; fi
