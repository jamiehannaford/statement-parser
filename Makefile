default: test

DB_PASS := $(shell kubectl get secret expensifier --template={{.data.MYSQL_ROOT_PASSWORD}} | base64 -D)

.PHONY: test
test:
	python ./compare_output.py

.PHONY: test
rebuild:
	docker build -t jamiehannaford/expensifier . && docker push jamiehannaford/expensifier

.PHONY: flushall
flushall:
	kubectl exec -it redis-master redis-cli flushall

.PHONY: stopall
stopall: flushall
	kubectl delete jobs -l app=worker
	echo "" > .workers 
	kubectl delete -f config/k8s/jobs/populate-expenses.yaml
	kubectl delete -f config/k8s/jobs/populate-meta.yaml

.PHONY: test
run-worker:
	scripts/run_workers.sh

.PHONY: test
run-expenses: run-worker
	 kubectl create -f config/k8s/jobs/populate-expenses.yaml

.PHONY: attach-mysql
attach-mysql:
	kubectl exec -it $(shell kubectl get pod -l app=mysql -o name) -- mysql -u root -p$(DB_PASS) -h mysql -D expensifier

.PHONY: tail
tail:
	kubectl logs -f $(shell kubectl get job -l app=worker -o name | head -n 1) -c worker